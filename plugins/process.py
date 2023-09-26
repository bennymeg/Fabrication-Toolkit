# For better annotation.
from __future__ import annotations

# System base libraries
import os
import csv
import math
import shutil
from collections import defaultdict
import re

# Interaction with KiCad.
import pcbnew  # type: ignore

# Application definitions.
from .config import *


class ProcessManager:
    def __init__(self):
        self.board = pcbnew.GetBoard()
        self.bom = []
        self.components = []
        self.__rotation_db = self.__read_rotation_db()

    @staticmethod
    def normalize_filename(filename):
        return re.sub(r'[^\w\s\.\-]', '', filename)

    @staticmethod
    def __read_rotation_db(filename: str = os.path.join(os.path.dirname(__file__), 'rotations.cf')) -> dict[str, float]:
        '''Read the rotations.cf config file so we know what rotations
        to apply later.
        '''
        db = {}

        with open(filename, 'r') as fh:
            for line in fh:
                line = line.rstrip()
                line = re.sub('#.*$', '', line)         # remove anything after a comment
                line = re.sub('\s*$', '', line)         # remove all trailing space

                if (line == ""):
                    continue

                match = re.match('^([^\s]+)\s+(\d+)$', line)

                if match:
                    db.update({ match.group(1): int(match.group(2)) })

        return db

    def _get_rotation_from_db(self, footprint: str) -> float:
        '''Get the rotation to be added from the database file.'''
        # Look for regular expression math of the footprint name and not its root library.
        fpshort = footprint.split(':')[-1]

        for expression, delta in self.db.items():
            fp = fpshort

            if (re.search(':', expression)):
                fp = footprint
                
            if(re.search(expression, fp)):
                return delta

        return 0.0

    def update_zone_fills(self):
        '''Verify all zones have up-to-date fills.'''
        filler = pcbnew.ZONE_FILLER(self.board)
        zones = self.board.Zones()

        # Fill returns true/false if a refill was made
        # We cant use aCheck = True as that would require a rollback on the commit object if
        # user decided to not perform the zone fill and the commit object is not exposed to python API
        filler.Fill(zones, False)

        # Finally rebuild the connectivity db
        self.board.BuildConnectivity()

    def generate_gerber(self, temp_dir):
        '''Generate the Gerber files.'''
        settings = self.board.GetDesignSettings()
        settings.m_SolderMaskMargin = 50000
        settings.m_SolderMaskToCopperClearance = 5000
        settings.m_SolderMaskMinWidth = 0

        plot_controller = pcbnew.PLOT_CONTROLLER(self.board)

        plot_options = plot_controller.GetPlotOptions()
        plot_options.SetOutputDirectory(temp_dir)
        plot_options.SetPlotFrameRef(False)
        plot_options.SetSketchPadLineWidth(pcbnew.FromMM(0.1))
        plot_options.SetAutoScale(False)
        plot_options.SetScale(1)
        plot_options.SetMirror(False)
        plot_options.SetUseGerberAttributes(True)
        plot_options.SetUseGerberProtelExtensions(False)
        plot_options.SetUseAuxOrigin(True)
        plot_options.SetSubtractMaskFromSilk(True)
        plot_options.SetDrillMarksType(0)  # NO_DRILL_SHAPE
        
        if hasattr(plot_options, "SetExcludeEdgeLayer"):
            plot_options.SetExcludeEdgeLayer(True)

        for layer_info in plotPlan:
            if self.board.IsLayerEnabled(layer_info[1]):
                plot_controller.SetLayer(layer_info[1])
                plot_controller.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
                
                if layer_info[1] == pcbnew.Edge_Cuts and hasattr(plot_controller, 'plotLayers'):
                    # includes User_1 layer with Edge_Cuts layer to allow V Cuts to be defined as User_1 layer
                    # available for KiCad 7.0.1+
                    seq = pcbnew.LSEQ()
                    seq.push_back(layer_info[1])
                    seq.push_back(pcbnew.User_1)
                    plot_controller.PlotLayers(seq)
                else:
                    plot_controller.PlotLayer()

        plot_controller.ClosePlot()

    def generate_drills(self, temp_dir):
        '''Generate the drill file.'''
        drill_writer = pcbnew.EXCELLON_WRITER(self.board)

        drill_writer.SetOptions(
            False,
            True,
            self.board.GetDesignSettings().GetAuxOrigin(),
            False)
        drill_writer.SetFormat(False)
        drill_writer.CreateDrillandMapFilesSet(temp_dir, True, False)

    def generate_netlist(self, temp_dir):
        '''Generate the connection netlist.'''
        netlist_writer = pcbnew.IPC356D_WRITER(self.board)
        netlist_writer.Write(os.path.join(temp_dir, netlistFileName))

    def generate_tables(self, temp_dir, exclude_dnp):
        '''Generate the data tables.'''
        if hasattr(self.board, 'GetModules'):
            footprints = list(self.board.GetModules())
        else:
            footprints = list(self.board.GetFootprints())

        # sort footprint after designator
        footprints.sort(key=lambda x: x.GetReference())

        # unique designator dictionary
        footprint_designators = defaultdict(int)
        for i, footprint in enumerate(footprints):
            # count unique designators
            footprint_designators[footprint.GetReference()] += 1
        bom_designators = footprint_designators.copy()

        if len(footprint_designators.items()) > 0:
            with open((os.path.join(temp_dir, designatorsFileName)), 'w', encoding='utf-8-sig') as f:
                for key, value in footprint_designators.items():
                    f.write('%s:%s\n' % (key, value))

        for i, footprint in enumerate(footprints):
            try:
                footprint_name = str(footprint.GetFPID().GetFootprintName())
            except AttributeError:
                footprint_name = str(footprint.GetFPID().GetLibItemName())

            layer = {
                pcbnew.F_Cu: 'top',
                pcbnew.B_Cu: 'bottom',
            }.get(footprint.GetLayer())

            # mount_type = {
            #     0: 'smt',
            #     1: 'tht',
            #     2: 'smt'
            # }.get(footprint.GetAttributes())

            skip_footprint = exclude_dnp and (footprint.HasProperty('dnp') or footprint.GetValue().upper() == 'DNP')

            if not (footprint.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_POS_FILES) and not skip_footprint:
                # append unique ID if duplicate footprint designator
                unique_id = ""
                if footprint_designators[footprint.GetReference()] > 1:
                    unique_id = str(footprint_designators[footprint.GetReference()])
                    footprint_designators[footprint.GetReference()] -= 1

                designator = "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id)
                mid_x = (footprint.GetPosition()[0] - self.board.GetDesignSettings().GetAuxOrigin()[0]) / 1000000.0
                mid_y = (footprint.GetPosition()[1] - self.board.GetDesignSettings().GetAuxOrigin()[1]) * -1.0 / 1000000.0
                rotation = footprint.GetOrientation().AsDegrees() if hasattr(footprint.GetOrientation(), 'AsDegrees') else footprint.GetOrientation() / 10.0
                # Get the rotation offset to be added to the actual rotation prioritizing the explicated by the
                # designer at the standards symbol fields. If not specified use the internal database.
                rotation_offset = self._get_rotation_offset_from_footprint(footprint) #or self._get_rotation_from_db(footprint)
                rotation = (rotation + rotation_offset) % 360.0

                # position offset needs to take rotation into account
                pos_offset = self._get_position_offset_from_footprint(footprint)
                rsin = math.sin(rotation / 180 * math.pi)
                rcos = math.cos(rotation / 180 * math.pi)
                pos_offset = ( pos_offset[0] * rcos - pos_offset[1] * rsin, pos_offset[0] * rsin + pos_offset[1] * rcos )
                mid_x, mid_y = tuple(map(sum,zip((mid_x, mid_y), pos_offset)))

                # JLC expect 'Rotation' to be 'as viewed from above component', so bottom needs inverting, and ends up 180 degrees out as well
                if layer == 'bottom':
                    rotation = (540.0 - rotation) % 360.0
                                
                self.components.append({
                    'Designator': designator,
                    'Mid X': mid_x,
                    'Mid Y': mid_y,
                    'Rotation': rotation,
                    'Layer': layer,
                })

            if not (footprint.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM) and not skip_footprint:
                # append unique ID if we are dealing with duplicate bom designator
                unique_id = ""
                if bom_designators[footprint.GetReference()] > 1:
                    unique_id = str(bom_designators[footprint.GetReference()])
                    bom_designators[footprint.GetReference()] -= 1

                # merge similar parts into single entry
                insert = True
                for component in self.bom:
                    same_footprint = component['Footprint'] == self._normalize_footprint_name(footprint_name)
                    same_value = component['Value'].upper() == footprint.GetValue().upper()
                    same_lcsc = component['LCSC Part #'] == self._get_mpn_from_footprint(footprint)

                    if same_footprint and same_value and same_lcsc:
                        component['Designator'] += ", " + "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id)
                        component['Quantity'] += 1
                        insert = False
                        # break ? 

                # add component to BOM
                if insert:
                    self.bom.append({
                        'Designator': "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id),
                        'Footprint': self._normalize_footprint_name(footprint_name),
                        'Quantity': 1,
                        'Value': footprint.GetValue(),
                        # 'Mount': mount_type,
                        'LCSC Part #': self._get_mpn_from_footprint(footprint),
                    })

    def generate_positions(self, temp_dir):
        '''Generate the position file.'''
        if len(self.components) > 0:
            with open((os.path.join(temp_dir, placementFileName)), 'w', newline='', encoding='utf-8-sig') as outfile:
                csv_writer = csv.writer(outfile)
                # writing headers of CSV file
                csv_writer.writerow(self.components[0].keys())

                for component in self.components:
                    # writing data of CSV file
                    if ('**' not in component['Designator']):
                        csv_writer.writerow(component.values())

    def generate_bom(self, temp_dir):
        '''Generate the bom file.'''
        if len(self.bom) > 0:
            with open((os.path.join(temp_dir, bomFileName)), 'w', newline='', encoding='utf-8-sig') as outfile:
                csv_writer = csv.writer(outfile)
                # writing headers of CSV file
                csv_writer.writerow(self.bom[0].keys())

                # Output all of the component information
                for component in self.bom:
                    # writing data of CSV file
                    if ('**' not in component['Designator']):
                        csv_writer.writerow(component.values())

    def generate_archive(self, temp_dir, temp_file):
        '''Generate the archive file.'''
        temp_file = shutil.make_archive(temp_file, 'zip', temp_dir)
        temp_file = shutil.move(temp_file, temp_dir)

        # remove non essential files
        for item in os.listdir(temp_dir):
            if not item.endswith(".zip") and not item.endswith(".csv") and not item.endswith(".ipc"):
                os.remove(os.path.join(temp_dir, item))

        return temp_file

    def _get_mpn_from_footprint(self, footprint):
        ''''Get the MPN/LCSC stock code from standard symbol fields.'''
        keys = ['LCSC Part #', 'JLCPCB Part #']
        fallback_keys = ['LCSC Part', 'JLC Part', 'LCSC', 'JLC', 'MPN', 'Mpn', 'mpn']

        if footprint.HasProperty('dnp'):
            return 'DNP'

        for key in keys + fallback_keys:
            if footprint.HasProperty(key):
                return footprint.GetProperty(key)

    def _get_rotation_offset_from_footprint(self, footprint) -> float:
        '''Get the rotation from standard symbol fields.'''
        keys = ['JLCPCB Rotation Offset']
        fallback_keys = ['JlcRotOffset', 'JLCRotOffset']

        offset = None

        for key in keys + fallback_keys:
            if footprint.HasProperty(key):
                offset = footprint.GetProperty(key)
                break

        if offset is None or offset == "":
            return 0
        else:
            try:
                return float(offset)
            except ValueError:
                raise RuntimeError("Rotation offset of {} is not a valid number".format(footprint.GetReference()))

    def _get_position_offset_from_footprint(self, footprint):
        keys = ['JLCPCB Position Offset']
        fallback_keys = ['JlcPosOffset', 'JLCPosOffset']

        offset = None

        for key in keys + fallback_keys:
            if footprint.HasProperty(key):
                offset = footprint.GetProperty(key)
                break

        if offset is None or offset == "":
            return (0, 0)
        else:
            try:
                return ( float(offset.split(",")[0]), float(offset.split(",")[1]) )
            except ValueError:
                raise RuntimeError("Position offset of {} is not a valid pair of numbers".format(footprint.GetReference()))

    def _normalize_footprint_name(self, footprint):
        # replace footprint names of resistors, capacitors, inductors, diodes, LEDs, fuses etc, with the footprint size only
        pattern = re.compile(r'^(\w*_SMD:)?\w{1,4}_(\d+)_\d+Metric.*$')

        return pattern.sub(r'\2', footprint)

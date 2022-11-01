import os
import csv
import shutil
import pcbnew
from collections import defaultdict
from .config import *


class ProcessManager:
    def __init__(self):
        self.board = pcbnew.GetBoard()
        self.bom = []
        self.components = []

    def generate_gerber(self, temp_dir):
        settings = self.board.GetDesignSettings()
        settings.m_SolderMaskMargin = 0
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
        plot_options.SetSubtractMaskFromSilk(False)
        plot_options.SetDrillMarksType(0)  # NO_DRILL_SHAPE
        
        if hasattr(plot_options, "SetExcludeEdgeLayer"):
            plot_options.SetExcludeEdgeLayer(True)

        for layer_info in plotPlan:
            if self.board.IsLayerEnabled(layer_info[1]):
                plot_controller.SetLayer(layer_info[1])
                plot_controller.OpenPlotfile(
                    layer_info[0],
                    pcbnew.PLOT_FORMAT_GERBER,
                    layer_info[2])
                plot_controller.PlotLayer()

        plot_controller.ClosePlot()

    def generate_drills(self, temp_dir):
        drill_writer = pcbnew.EXCELLON_WRITER(self.board)

        drill_writer.SetOptions(
            False,
            True,
            self.board.GetDesignSettings().GetAuxOrigin(),
            False)
        drill_writer.SetFormat(False)
        drill_writer.CreateDrillandMapFilesSet(temp_dir, True, False)

    def generate_netlist(self, temp_dir):
        netlist_writer = pcbnew.IPC356D_WRITER(self.board)
        netlist_writer.Write(os.path.join(temp_dir, netlistFileName))

    def generate_positions(self, temp_dir):
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
            with open((os.path.join(temp_dir, designatorsFileName)), 'w', encoding='utf-8') as f:
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

            if not footprint.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_POS_FILES:
                # append unique ID if duplicate footprint designator
                unique_id = ""
                if footprint_designators[footprint.GetReference()] > 1:
                    unique_id = str(footprint_designators[footprint.GetReference()])
                    footprint_designators[footprint.GetReference()] -= 1

                designator = "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id)
                mid_x = (footprint.GetPosition()[0] - self.board.GetDesignSettings().GetAuxOrigin()[0]) / 1000000.0
                mid_y = (footprint.GetPosition()[1] - self.board.GetDesignSettings().GetAuxOrigin()[1]) * -1.0 / 1000000.0
                mid_x, mid_y = tuple(map(sum,zip((mid_x, mid_y), self._getPosOffsetFromFootprint(footprint))))
                rotation = footprint.GetOrientation().AsDegrees() if hasattr(footprint.GetOrientation(), 'AsDegrees') else footprint.GetOrientation() / 10.0
                rotation = (rotation + self._getRotOffsetFromFootprint(footprint)) % 360.0

                self.components.append({
                    'Designator': designator,
                    'Mid X': mid_x,
                    'Mid Y': mid_y,
                    'Rotation': rotation,
                    'Layer': layer,
                })

            if not footprint.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM:
                # append unique ID if we are dealing with duplicate bom designator
                unique_id = ""
                if bom_designators[footprint.GetReference()] > 1:
                    unique_id = str(bom_designators[footprint.GetReference()])
                    bom_designators[footprint.GetReference()] -= 1

                # merge similar parts into single entry
                insert = True
                for component in self.bom:
                    if component['Footprint'].upper() == footprint_name.upper() and component['Value'].upper() == footprint.GetValue().upper():
                        component['Designator'] += ", " + "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id)
                        component['Quantity'] += 1
                        insert = False

                # add component to BOM
                if insert:
                    self.bom.append({
                        'Designator': "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id),
                        'Footprint': footprint_name,
                        'Quantity': 1,
                        'Value': footprint.GetValue(),
                        # 'Mount': mount_type,
                        'LCSC Part #': self._getMpnFromFootprint(footprint),
                    })

        if len(self.components) > 0:
            with open((os.path.join(temp_dir, placementFileName)), 'w', newline='', encoding='utf-8') as outfile:
                csv_writer = csv.writer(outfile)
                # writing headers of CSV file
                csv_writer.writerow(self.components[0].keys())

                for component in self.components:
                    # writing data of CSV file
                    if ('**' not in component['Designator']):
                        csv_writer.writerow(component.values())

    def generate_bom(self, temp_dir):
        if len(self.bom) > 0:
            with open((os.path.join(temp_dir, bomFileName)), 'w', newline='', encoding='utf-8') as outfile:
                csv_writer = csv.writer(outfile)
                # writing headers of CSV file
                csv_writer.writerow(self.bom[0].keys())

                # Output all of the component information
                for component in self.bom:
                    # writing data of CSV file
                    if ('**' not in component['Designator']):
                        csv_writer.writerow(component.values())

    def generate_archive(self, temp_dir, temp_file):
        temp_file = shutil.make_archive(temp_file, 'zip', temp_dir)
        temp_file = shutil.move(temp_file, temp_dir)

        # remove non essential files
        for item in os.listdir(temp_dir):
            if not item.endswith(".zip") and not item.endswith(".csv") and not item.endswith(".ipc"):
                os.remove(os.path.join(temp_dir, item))

        return temp_file

    def _getMpnFromFootprint(self, footprint):
        keys = ['LCSC Part #', 'JLCPCB Part #']
        fallback_keys = ['LCSC', 'JLC', 'MPN', 'Mpn', 'mpn']

        for key in keys:
            if footprint.HasProperty(key):
                return footprint.GetProperty(key)

        for key in fallback_keys:
            if footprint.HasProperty(key):
                return footprint.GetProperty(key)

    def _getRotOffsetFromFootprint(self, footprint):
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

    def _getPosOffsetFromFootprint(self, footprint):
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

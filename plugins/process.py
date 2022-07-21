# from urllib import response
# import json
# import requests
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
        plot_options.SetExcludeEdgeLayer(True)
        plot_options.SetUseGerberProtelExtensions(False)
        plot_options.SetUseAuxOrigin(True)
        plot_options.SetSubtractMaskFromSilk(False)
        plot_options.SetDrillMarksType(0)  # NO_DRILL_SHAPE

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

        # unique designator dictionary
        footprint_designators = defaultdict(int)
        for i, footprint in enumerate(footprints):
            # count unique designators
            footprint_designators[footprint.GetReference()] += 1
        bom_designators = footprint_designators.copy()

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

                self.components.append({
                    'Designator': "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id),
                    'Mid X': (footprint.GetPosition()[0] - self.board.GetDesignSettings().GetAuxOrigin()[0]) / 1000000.0,
                    'Mid Y': (footprint.GetPosition()[1] - self.board.GetDesignSettings().GetAuxOrigin()[1]) * -1.0 / 1000000.0,
                    'Rotation': footprint.GetOrientation() / 10.0,
                    'Layer': layer,
                })

            if not footprint.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM:
                # append unique ID if we are dealing with duplicate bom designator
                unique_id = ""
                if bom_designators[footprint.GetReference()] > 1:
                    unique_id = str(bom_designators[footprint.GetReference()])
                    bom_designators[footprint.GetReference()] -= 1

                # todo: merge similar parts into single entry

                self.bom.append({
                    'Designator': "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id),
                    'Footprint': footprint_name,
                    'Quantity': 1,
                    'Value': footprint.GetValue(),
                    # 'Mount': mount_type,
                    'LCSC Part #': self._getMpnFromFootprint(footprint),
                })

        with open((os.path.join(temp_dir, placementFileName)), 'w', newline='', encoding='utf-8') as outfile:
            header = True
            csv_writer = csv.writer(outfile)

            for component in self.components:
                if header:
                    # writing headers of CSV file
                    csv_writer.writerow(component.keys())
                    header = False

                # writing data of CSV file
                if ('**' not in component['Designator']):
                    csv_writer.writerow(component.values())

    def generate_bom(self, temp_dir):

        with open((os.path.join(temp_dir, bomFileName)), 'w', newline='', encoding='utf-8') as outfile:
            header = True
            csv_writer = csv.writer(outfile)

            for component in self.bom:
                if header:
                    # writing headers of CSV file
                    csv_writer.writerow(component.keys())
                    header = False

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

    def upload_archive(self, temp_file):
        boardWidth = pcbnew.Iu2Millimeter(self.board.GetBoardEdgesBoundingBox().GetWidth())
        boardHeight = pcbnew.Iu2Millimeter(self.board.GetBoardEdgesBoundingBox().GetHeight())
        boardLayer = self.board.GetCopperLayerCount()

        files = { 'upload[file]': open(temp_file, 'rb') }
        upload_url = baseUrl + '/Common/KiCadUpFile/'

        # response = requests.post(
        #     upload_url, files=files, data={ 'boardWidth': boardWidth, 'boardHeight': boardHeight, 'boardLayer': boardLayer })
        # urls = json.loads(response.content)

    def _getMpnFromFootprint(self, footprint):
        keys = ['mpn', 'Mpn', 'MPN', 'JLC_MPN', 'LCSC_MPN', 'LCSC Part #', 'JLC', 'LCSC']
        for key in keys:
            if footprint.HasProperty(key):
                return footprint.GetProperty(key)

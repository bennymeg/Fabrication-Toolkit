# original copyright Aisler and licensed under the MIT license.
# https://opensource.org/licenses/MIT

# from urllib import response
# import json
# import requests
import os
import wx
import csv
import shutil
import tempfile
import webbrowser
from collections import defaultdict
from threading import Thread
from .result_event import *
from .config import *


class ProcessThread(Thread):
    def __init__(self, wxObject):
        Thread.__init__(self)
        self.wxObject = wxObject
        self.start()

    def run(self):

        temp_dir = tempfile.mkdtemp()
        _, temp_file = tempfile.mkstemp()
        board = pcbnew.GetBoard()
        title_block = board.GetTitleBlock()

        # configure gerber
        self.report(5)

        settings = board.GetDesignSettings()
        settings.m_SolderMaskMargin = 0
        settings.m_SolderMaskMinWidth = 0

        pctl = pcbnew.PLOT_CONTROLLER(board)

        popt = pctl.GetPlotOptions()
        popt.SetOutputDirectory(temp_dir)
        popt.SetPlotFrameRef(False)
        popt.SetSketchPadLineWidth(pcbnew.FromMM(0.1))
        popt.SetAutoScale(False)
        popt.SetScale(1)
        popt.SetMirror(False)
        popt.SetUseGerberAttributes(True)
        popt.SetExcludeEdgeLayer(True)
        popt.SetUseGerberProtelExtensions(False)
        popt.SetUseAuxOrigin(True)
        popt.SetSubtractMaskFromSilk(False)
        popt.SetDrillMarksType(0)  # NO_DRILL_SHAPE

        # generate gerber
        self.report(10)
        for layer_info in plotPlan:
            if board.IsLayerEnabled(layer_info[1]):
                pctl.SetLayer(layer_info[1])
                pctl.OpenPlotfile(
                    layer_info[0],
                    pcbnew.PLOT_FORMAT_GERBER,
                    layer_info[2])
                pctl.PlotLayer()

        pctl.ClosePlot()

        # generate drill file
        self.report(15)
        drlwriter = pcbnew.EXCELLON_WRITER(board)

        drlwriter.SetOptions(
            False,
            True,
            board.GetDesignSettings().GetAuxOrigin(),
            False)
        drlwriter.SetFormat(False)
        drlwriter.CreateDrillandMapFilesSet(pctl.GetPlotDirName(), True, False)

        # generate netlist
        self.report(25)
        netlist_writer = pcbnew.IPC356D_WRITER(board)
        netlist_writer.Write(os.path.join(temp_dir, netlistFileName))

        # generate pick and place file
        self.report(40)
        components = []
        bom = []
        if hasattr(board, 'GetModules'):
            footprints = list(board.GetModules())
        else:
            footprints = list(board.GetFootprints())

        # unique designator dictionary
        footprint_designators = defaultdict(int)
        for i, footprint in enumerate(footprints):
            # count unique designators
            footprint_designators[footprint.GetReference()] += 1
        bom_designators = footprint_designators.copy()

        with open((os.path.join(temp_dir, designatorsFileName)), 'w') as f:
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

                components.append({
                    'Designator': "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id),
                    'Mid X': (footprint.GetPosition()[0] - board.GetDesignSettings().GetAuxOrigin()[0]) / 1000000.0,
                    'Mid Y': (footprint.GetPosition()[1] - board.GetDesignSettings().GetAuxOrigin()[1]) * -1.0 / 1000000.0,
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

                bom.append({
                    'Designator': "{}{}{}".format(footprint.GetReference(), "" if unique_id == "" else "_", unique_id),
                    'Footprint': footprint_name,
                    'Quantity': 1,
                    'Value': footprint.GetValue(),
                    # 'Mount': mount_type,
                    'LCSC Part #': self.getMpnFromFootprint(footprint),
                })

        with open((os.path.join(temp_dir, placementFileName)), 'w', newline='') as outfile:
            header = True
            csv_writer = csv.writer(outfile)

            for component in components:
                if header:
                    # writing headers of CSV file
                    csv_writer.writerow(component.keys())
                    header = False

                # writing data of CSV file
                if ('**' not in component['Designator']):
                    csv_writer.writerow(component.values())

        # generate BOM file
        self.report(60)
        with open((os.path.join(temp_dir, bomFileName)), 'w', newline='') as outfile:
            header = True
            csv_writer = csv.writer(outfile)

            for component in bom:
                if header:
                    # writing headers of CSV file
                    csv_writer.writerow(component.keys())
                    header = False

                # writing data of CSV file
                if ('**' not in component['Designator']):
                    csv_writer.writerow(component.values())

        # generate production archive
        self.report(75)
        temp_file = shutil.make_archive(temp_file, 'zip', temp_dir)
        temp_file = shutil.move(temp_file, temp_dir)

        # remove non essential files
        for item in os.listdir(temp_dir):
            if not item.endswith(".zip") and not item.endswith(".csv") and not item.endswith(".ipc"):
                os.remove(os.path.join(temp_dir, item))

        # upload files
        self.report(87.5)
        boardWidth = pcbnew.Iu2Millimeter(board.GetBoardEdgesBoundingBox().GetWidth())
        boardHeight = pcbnew.Iu2Millimeter(board.GetBoardEdgesBoundingBox().GetHeight())
        boardLayer = board.GetCopperLayerCount()

        # files = {'upload[file]': open(temp_file, 'rb')}
        # upload_url = baseUrl + '/Common/KiCadUpFile/'

        # response = requests.post(
        #     upload_url, files=files, data={'boardWidth':boardWidth,'boardHeight':boardHeight,'boardLayer':boardLayer})

        # urls = json.loads(response.content)

        readsofar = 0
        totalsize = os.path.getsize(temp_file)
        with open(temp_file, 'rb') as file:
            while True:
                data = file.read(10)
                if not data:
                    break
                readsofar += len(data)
                percent = readsofar * 1e2 / totalsize
                self.report(75 + percent / 8)

        os.rename(temp_file, os.path.join(temp_dir, gerberArchiveName))

        webbrowser.open("file://%s" % (temp_dir))
        # webbrowser.open(urls['redirect'])
        self.report(-1)

    def report(self, status):
        wx.PostEvent(self.wxObject, ResultEvent(status))

    def getMpnFromFootprint(self, footprint):
        keys = ['mpn', 'Mpn', 'MPN', 'JLC_MPN', 'LCSC_MPN', 'LCSC Part #', 'JLC', 'LCSC']
        for key in keys:
            if footprint.HasProperty(key):
                return footprint.GetProperty(key)

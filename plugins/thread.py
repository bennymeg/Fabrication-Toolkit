import os
import wx
import shutil
import tempfile
import webbrowser
from threading import Thread
from .events import StatusEvent
from .process import ProcessManager
from .config import *


class ProcessThread(Thread):
    def __init__(self, wx):
        Thread.__init__(self)

        self.process_manager = ProcessManager()
        self.wx = wx
        self.start()

    def run(self):
        # initializing
        self.report(0)

        temp_dir = tempfile.mkdtemp()
        _, temp_file = tempfile.mkstemp()
        project_directory = os.path.dirname(self.process_manager.board.GetFileName())
        output_path = os.path.join(project_directory, outputFolder)

        try:
            # configure and generate gerber
            self.report(5)
            self.process_manager.generate_gerber(temp_dir)

            # generate drill file
            self.report(15)
            self.process_manager.generate_drills(temp_dir)

            # generate netlist
            self.report(25)
            self.process_manager.generate_netlist(temp_dir)

            # generate pick and place file
            self.report(40)
            self.process_manager.generate_positions(temp_dir)

            # generate BOM file
            self.report(60)
            self.process_manager.generate_bom(temp_dir)

            # generate production archive
            self.report(75)
            temp_file = self.process_manager.generate_archive(temp_dir, temp_file)
        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            self.report(-1)
            return

        # progress bar done animation
        read_so_far = 0
        total_size = os.path.getsize(temp_file)
        with open(temp_file, 'rb') as file:
            while True:
                data = file.read(10)
                if not data:
                    break
                read_so_far += len(data)
                percent = read_so_far * 1e2 / total_size
                self.report(75 + percent / 8)

        os.rename(temp_file, os.path.join(temp_dir, gerberArchiveName))

        try:
            if os.path.exists(output_path):
                shutil.rmtree(output_path)

            shutil.copytree(temp_dir, output_path)
            webbrowser.open("file://%s" % (output_path))
        except Exception as e: 
            webbrowser.open("file://%s" % (temp_dir))

        self.report(-1)

    def report(self, status):
        wx.PostEvent(self.wx, StatusEvent(status))

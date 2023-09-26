import os
import wx
import pcbnew  # type: ignore
import shutil
import tempfile
import webbrowser
import datetime
from threading import Thread
from .events import StatusEvent
from .process import ProcessManager
from .config import *
from .options import *


class ProcessThread(Thread):
    def __init__(self, wx, options):
        Thread.__init__(self)

        self.process_manager = ProcessManager()
        self.wx = wx
        self.options = options
        self.start()

    def run(self):
        # initializing
        self.progress(0)

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

        temp_dir = tempfile.mkdtemp() + timestamp
        os.makedirs(temp_dir)
        os.makedirs(temp_dir + "_g")

        _, temp_file = tempfile.mkstemp()
        project_directory = os.path.dirname(self.process_manager.board.GetFileName())

        try:
            # Verify all zones are up-to-date
            self.progress(10)
            self.process_manager.update_zone_fills()

            # generate gerber
            self.progress(20)
            self.process_manager.generate_gerber(temp_dir + "_g")

            # generate drill file
            self.progress(30)
            self.process_manager.generate_drills(temp_dir + "_g")

            # generate netlist
            self.progress(40)
            self.process_manager.generate_netlist(temp_dir)

            # generate data tables
            self.progress(50)
            self.process_manager.generate_tables(temp_dir, self.options[EXCLUDE_DNP_OPT])

            # generate pick and place file
            self.progress(60)
            self.process_manager.generate_positions(temp_dir)

            # generate BOM file
            self.progress(70)
            self.process_manager.generate_bom(temp_dir)

            # generate production archive
            self.progress(85)
            temp_file = self.process_manager.generate_archive(temp_dir + "_g", temp_file)
            shutil.move(temp_file, temp_dir)
            shutil.rmtree(temp_dir + "_g")
            temp_file = os.path.join(temp_dir, os.path.basename(temp_file))
        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            self.progress(-1)
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
                self.progress(85 + percent / 8)

        # generate gerber name
        title_block = self.process_manager.board.GetTitleBlock()
        title = title_block.GetTitle()
        revision = title_block.GetRevision()
        company = title_block.GetCompany()
        file_date = title_block.GetDate()

        if (hasattr(self.process_manager.board, "GetProject") and hasattr(pcbnew, "ExpandTextVars")):
            project = self.process_manager.board.GetProject()
            title = pcbnew.ExpandTextVars(title, project)
            revision = pcbnew.ExpandTextVars(revision, project)
            company = pcbnew.ExpandTextVars(company, project)
            file_date = pcbnew.ExpandTextVars(file_date, project)

        # make output dir
        filename = os.path.splitext(os.path.basename(self.process_manager.board.GetFileName()))[0]
        name = ProcessManager.normalize_filename("_".join(("{} {} {}".format(title or filename, revision or '', timestamp).strip()).split()))
        output_path = os.path.join(project_directory, outputFolder, name)
        os.makedirs(output_path)

        # rename gerber archive
        gerberArchiveName = ProcessManager.normalize_filename("_".join(("{} {}".format(title or filename, revision or '').strip() + '.zip').split()))
        os.rename(temp_file, os.path.join(temp_dir, gerberArchiveName))

        # copy to & open output dir
        try:
            if os.path.exists(output_path):
                shutil.rmtree(output_path)

            shutil.copytree(temp_dir, output_path)
            webbrowser.open("file://%s" % (output_path))
            shutil.rmtree(temp_dir)
        except Exception as e: 
            webbrowser.open("file://%s" % (temp_dir))

        self.progress(-1)

    def progress(self, percent):
        wx.PostEvent(self.wx, StatusEvent(percent))

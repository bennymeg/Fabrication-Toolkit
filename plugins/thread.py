import os
import wx
import pcbnew  # type: ignore
import shutil
import tempfile
import webbrowser
import datetime
import logging
from threading import Thread
from .events import StatusEvent
from .process import ProcessManager
from .config import *
from .options import *


class ProcessThread(Thread):
    def __init__(self, wx, options, cli = None, openBrowser = True):
        Thread.__init__(self)

        # prevent use of cli and grapgical mode at the same time
        if (wx is None and cli is None) or (wx is not None and cli is not None):
            logging.error("Specify either graphical or cli use!")
            return
        
        if cli is not None:
            try:
                self.board = pcbnew.LoadBoard(cli)
            except Exception as e:
                logging.error("Fabrication Toolkit - Error" + str(e))
                return
        else:
            self.board = None
            
        self.process_manager = ProcessManager(self.board)
        self.wx = wx
        self.cli = cli
        self.options = options
        self.openBrowser = openBrowser
        self.start()

    def run(self):
        # initializing
        self.progress(0)

        temp_dir = tempfile.mkdtemp()
        temp_dir_gerber = temp_dir + "_g"
        os.makedirs(temp_dir_gerber)

        _, temp_file = tempfile.mkstemp()
        project_directory = os.path.dirname(self.process_manager.board.GetFileName())

        try:
            # Verify all zones are up-to-date
            self.progress(10)
            if (self.options[AUTO_FILL_OPT]):
                self.process_manager.update_zone_fills()

            # generate gerber
            self.progress(20)
            self.process_manager.generate_gerber(temp_dir_gerber, self.options[EXTRA_LAYERS], self.options[EXTEND_EDGE_CUT_OPT], self.options[ALTERNATIVE_EDGE_CUT_OPT])

            # generate drill file
            self.progress(30)
            self.process_manager.generate_drills(temp_dir_gerber)

            # generate netlist
            self.progress(40)
            self.process_manager.generate_netlist(temp_dir)

            # generate data tables
            self.progress(50)
            self.process_manager.generate_tables(temp_dir, self.options[AUTO_TRANSLATE_OPT], self.options[EXCLUDE_DNP_OPT])

            # generate pick and place file
            self.progress(60)
            self.process_manager.generate_positions(temp_dir)

            # generate BOM file
            self.progress(70)
            self.process_manager.generate_bom(temp_dir)

            # generate production archive
            self.progress(85)
            temp_file = self.process_manager.generate_archive(temp_dir_gerber, temp_file)
            shutil.move(temp_file, temp_dir)
            shutil.rmtree(temp_dir_gerber)
            temp_file = os.path.join(temp_dir, os.path.basename(temp_file))
        except Exception as e:
            if self.wx is None:
                logging.error("Fabrication Toolkit - Error" + str(e))
            else:
                wx.MessageBox(str(e), "Fabrication Toolkit - Error", wx.OK | wx.ICON_ERROR)
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
        output_path = os.path.join(project_directory, outputFolder)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # rename gerber archive
        gerberArchiveName = ProcessManager.normalize_filename("_".join(("{} {}".format(title or filename, revision or '').strip() + '.zip').split()))
        os.rename(temp_file, os.path.join(temp_dir, gerberArchiveName))

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        backup_name = ProcessManager.normalize_filename("_".join(("{} {} {}".format(title or filename, revision or '', timestamp).strip()).split()))
        shutil.make_archive(os.path.join(output_path, 'backups', backup_name), 'zip', temp_dir)


        # copy to & open output dir
        try:
            shutil.copytree(temp_dir, output_path, dirs_exist_ok=True)
            if self.openBrowser:
                webbrowser.open("file://%s" % (output_path))
            shutil.rmtree(temp_dir)
        except Exception as e:
            if self.openBrowser:
                webbrowser.open("file://%s" % (temp_dir))

        if self.wx is None: 
            self.progress(100)
        else:
            self.progress(-1)

    def progress(self, percent):
        def cliBar(percent, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
            """
            Call in a loop to create terminal progress bar
            @params:
                percent     - Required  : current percentage (Int)
                prefix      - Optional  : prefix string (Str)
                suffix      - Optional  : suffix string (Str)
                decimals    - Optional  : positive number of decimals in percent complete (Int)
                length      - Optional  : character length of bar (Int)
                fill        - Optional  : bar fill character (Str)
                printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
            """
            if percent == -1:
                percent = 0
            filledLength = int(length * (percent / 100 ))
            bar = fill * filledLength + '-' * (length - filledLength)
            percent2dec = "%.2f" % percent
            print(f'\r{prefix} |{bar}| {percent2dec}% {suffix}', end = printEnd)
            # Print New Line on Complete
            if percent == 100: 
                print()
        

        if self.wx is None:
            cliBar(percent, prefix = 'Progress:', suffix = 'Complete', length = 50)
        else:
            wx.PostEvent(self.wx, StatusEvent(percent))

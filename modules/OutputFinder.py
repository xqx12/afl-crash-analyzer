#!/usr/bin/env python2.7
'''
    AFL crash analyzer, crash triage for the American Fuzzy Lop fuzzer
    Copyright (C) 2015  floyd

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Created on Apr 13, 2015
@author: floyd, http://floyd.ch, @floyd_ch
'''
from utilities.Logger import Logger
from utilities.Executer import Executer
import os

class OutputFinder:
    def __init__(self, config, search_dir=None, output_dir=None):
        self.config = config
        self.search_dir = search_dir
        if self.search_dir is None:
            self.search_dir = self.config.original_crashes_directory
        #output directory will be just the same place where the input file is if output_dir is None
        self.output_dir = output_dir
        #it's going to be: fileName-binaryName-outputPrefix-gdbPrefix-config.runExtension
        #For example: crash15-ffmpeg-
        self.output_prefix_plain = "-plain"
        self.output_prefix_instrumented = "-instrumented"
        self.output_prefix_asan = "-asan"
        self.gdb_prefix = "-gdb"
    
    def instrumented_combined_stdout_stderr(self, gdb_run=False):
        self._combined_stdout_stderr(self.config.target_binary_instrumented, gdb_run, self.output_prefix_instrumented)
    
    def plain_combined_stdout_stderr(self, gdb_run=False):
        if not self.config.target_binary_plain:
            Logger.warning("You didn't configure a plain binary (recommended: with symbols), therefore skipping run with plain binary.")
        else:
            self._combined_stdout_stderr(self.config.target_binary_plain, gdb_run, self.output_prefix_plain)

    def asan_combined_stdout_stderr(self, gdb_run=False):
        if not self.config.target_binary_asan:
            Logger.warning("You didn't configure an ASAN enabled binary (recommended: with symbols), therefore skipping run with ASAN binary.")
        else:
            self._combined_stdout_stderr(self.config.target_binary_asan, gdb_run, self.output_prefix_asan)
    
    
    def _combined_stdout_stderr(self, binary, gdb_run, hint):
        executer = Executer(self.config)
        for path, _, files in os.walk(self.search_dir):
            for filename in files:
                if filename.endswith(self.config.run_extension):
                    continue
                filepath = os.path.join(path, filename )
                if gdb_run:
                    command = self.config.get_gdb_command_line(binary, filepath)
                    new_filename = filename+"-"+os.path.basename(binary)+hint+"-gdb"
                else:
                    command = self.config.get_command_line(binary, filepath)
                    new_filename = filename+"-"+os.path.basename(binary)+hint
                Logger.debug("Looking for stdout/stderr output:", command, debug_level=3)
                if self.output_dir:
                    output_file_name = self.get_new_output_file_name(self.output_dir, new_filename, self.config.run_extension)
                    new_filepath = os.path.join(self.output_dir, output_file_name)
                else:
                    output_file_name = self.get_new_output_file_name(path, new_filename, self.config.run_extension)
                    new_filepath = os.path.join(path, output_file_name)
                fp = file(new_filepath, "w")
                executer.get_output_for_run(command, fp, env=self.config.env)
                fp.close()
        
    def get_new_output_file_name(self, path, filename, extension):
        new_filename = filename
        i = 1
        while os.path.exists(os.path.join(path, new_filename+extension)) and i < 10**self.config.max_digets:
            formatstr = "%0"+str(self.config.max_digets)+"d"
            new_number = formatstr % i
            new_filename = filename + new_number
            i += 1
        return new_filename + extension
        
        

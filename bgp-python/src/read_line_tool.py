import readline
import logging
import os
from termcolor import colored
from printer import Printer
from file_tool import File_Tool

class Read_Line_Tool( object ):
    LOG_FILENAME = '../log/completer.log'
    HISTORY_FILENAME = '../log/completer.hist'

    program_name = ""
    P = None
    FT = None
    path_to_history = ""
    current_length = None

    def __init__( self, program_name = None, P = None ):
        if P is not None:
            self.P = P
        else:
            self.P = Printer()
            self.P.write( "[WARNING] Read_Line_Tool : __init__ : P is None", color = 'yellow', attrs = ['bold'] )

        self.P.write( "Read_Line_Tool: Loading...", color = 'cyan', attrs=['bold'] )

        self.FT = File_Tool( program_name = "Read_Line_Tool", base_path = "log/", P = self.P )

        self.matches = []

        if program_name is not None:
            self.program_name = program_name
            self.LOG_FILENAME = '../log/' + str(program_name) + '_completer.log'
            self.HISTORY_FILENAME = '../log/' + str(program_name) + '_completer.hist'

        logging.basicConfig(filename=self.LOG_FILENAME,
                        level=logging.DEBUG,
                        )
        try:
            readline.read_history_file(self.HISTORY_FILENAME)
        except ( IOError ):
            self.P.write( "[Read_Line_Tool: __init__ : HISTORY_FILENAME does not exists...", color = 'cyan', attrs = ['bold'] )
            
        self.current_length = readline.get_current_history_length()
        readline.parse_and_bind('set editing-mode vi')

        self.path_to_history = self.FT.get_file_path( file_name = str(self.program_name) + '_completer.hist' )
        self.P.write( "\tRead_Line_Tool: Using console history file " + str(self.path_to_history), attrs=['bold'] )
        return

    def filter( self ):
        file_name = str(self.program_name) + '_completer.hist'
        file_data = self.FT.load_text_file( file_name = file_name )
        lines = file_data.split("\n")

        lines = lines[self.current_length:]

        data_text = ""
        for x in range(0, len(lines) ):
            data_text = data_text + lines[x] + '\n'

        data_text = data_text.replace('\n\n','\n')

        self.current_length = readline.get_current_history_length() - self.current_length 
        self.FT.save_text_file( data_text = data_text, file_name = file_name )

        readline.clear_history()
        readline.read_history_file(self.HISTORY_FILENAME)

    def get_history_items( self ):
        return self.FT.load_text_file( file_name = str(self.program_name) + '_completer.hist')

    def read_line( self ):
        if os.path.exists(self.HISTORY_FILENAME):
            readline.read_history_file(self.HISTORY_FILENAME)

        if self.P.get_last_was_rewrite() is True:
            print ""
            self.P.reset_last_was_rewrite()

        if self.P.get_last_was_rewrite() is True:
            print ""
            self.P.reset_last_was_rewrite()

        line = raw_input( self.P.get_time_stamp() + colored( 'Enter Command: ', color = 'green', attrs=['bold'] ))

        readline.write_history_file( self.HISTORY_FILENAME )
        self.filter()

        return line

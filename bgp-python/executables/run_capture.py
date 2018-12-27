import os, sys

sys.path.append( str(os.getcwd()) + "/../src" )

import time, hashlib
from printer import Printer
from file_tool import File_Tool
from ask_tool import Ask_Tool
from time import sleep

class Capture():
	P = None 
	FT = None
	AT = Ask_Tool()
	file_name = None

	def __init__( self ):
		self.__clear_terminal()
		self.P = Printer()
		self.FT = File_Tool( base_path = "output/", program_name = "Capture", P = self.P )
	
	def run( self ):
		file_names = self.FT.get_file_list()
		found_file_names = list()
		for file_name in file_names:
			if ".output" in file_name:
				file_name = file_name.split('.output')[0]
				found_file_names.append( file_name )

		entered_correct_file_name = False
		while entered_correct_file_name is False:
			if len( found_file_names ) > 0:
				self.P.write( "Capture: Found the following .output files...", color = 'green')
				for file_name in found_file_names:
					self.P.write( " * " + str(file_name) )
			else:
				self.P.write_error( "Capture: No .output files found..." )
				return

			self.file_name = self.AT.ask( question = "Enter file name:" )

			if str(self.file_name) in found_file_names:
				entered_correct_file_name = True
			else:
				self.P.write_error( "Capture: Wrong file name provided " )

			if "." not in self.file_name:
				self.file_name = self.file_name + ".output"

		while True:
			sleep(0.1)
			lines = self.FT.load_CSV_file( file_name = self.file_name, seperator = "\n", simple_mode = True )

			while lines is None:
				sleep(1)
				self.__clear_terminal()
				lines = self.FT.load_CSV_file( file_name = self.file_name, seperator = "\n", simple_mode = True )

			self.__clear_terminal()

			for x in range(0, 100):
				print ""

			for line in lines:
				if len(line) > 0:
					print line

			self.__print_header()

	def __print_header( self ):
		result = "| CAPTURE | file_name = " + str(self.file_name) + " | time = " + self.P.get_time_stamp() + "|" 
		length = len(result)

		filler = "|"
		for x in range( 0, length - 11 ):
			filler = filler + "-"
		filler = filler + "|"

		print "\n"
		print filler
		print result
		print filler

	def __clear_terminal( self ):
		os.system('cls' if os.name == 'nt' else 'clear')

C = Capture()
C.run()
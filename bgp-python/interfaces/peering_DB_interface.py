import json, requests, os, sys, wget
from time import sleep
from random import randint

sys.path.append( str(os.getcwd()) + "/../src" )

from printer import Printer
from file_tool import File_Tool
from ask_tool import Ask_Tool
from string_tool import String_Tool
from AS_rank_interface import AS_Rank_Interface

class Peering_DB_Interface():
	IXs_dict = None

	base_url = None
	FT = None
	AT = None
	save_counter = None
	save_data_bool = None

	RANDOM_STRING = None

	def __init__( self, P = None, ASRI = None, save_data = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] Peering_DB_Interface: __init__ : P is None", color = 'yellow' )

		self.RANDOM_STRING = "_" + str(randint(0, 1000000000))

		self.P.write( "Peering_DB_Interface: Loading... (RANDOM_STRING = " + self.RANDOM_STRING + ")", color = 'cyan' )
		self.ST = String_Tool()
		self.AT = Ask_Tool( P = self.P )

		if save_data is not None:
			self.save_data_bool = save_data
		else:
			self.P.write( "[WARNING] Peering_DB_Interface: __init__ : save_data is None", color = 'yellow' )
			self.save_data_bool = False
		
		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write( "[WARNING] Peering_DB_Interface : __init__ : ASRI is None", color = 'yellow' )
			self.ASRI = AS_Rank_Interface( P = self.P )

		self.P.write( "Peering_DB_Interface: __init__ : save_data = " + str(self.save_data_bool) )

		self.FT = File_Tool( P = self.P, base_path = "/data/", program_name = "Peering_DB_Interface" )

		self.IXs_dict = dict()

		self.base_url = "https://peeringdb.com/net?asn="
		self.save_counter = 0
		self.__load_data()

	def __load_data( self ):
		if self.FT.check_checksum( file_name = "Peering_DB_Interface_AS_to_IXs.json" ):
			self.IXs_dict = self.FT.load_JSON_file( file_name = "Peering_DB_Interface_AS_to_IXs.json", print_status = False  )
			self.P.write( "\tLoaded IXs_dict (" + str(len(self.IXs_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded IXs_dict", color = 'red' )

	def save_data( self ):
		self.save_counter = 1001
		self.__save_data()

	def auto_download( self ):
		if "N" in self.AT.ask( "Peering_DB_Interface: auto_download: this function requires a fully cached AS Rank, continue? (Y/N)", expect_list = [ "Y", "N" ] ):
			return

		self.P.write( "Peering_DB_Interface: auto_download: start", color = 'green' )
		
		AS_numbers = self.ASRI.get_all_saved_ASes()

		counter = 0
		for AS_number in AS_numbers:
			counter += 1
			percentage = int( float(counter) / float(len(AS_numbers)) * 100 )
			percentage_str = "(" + str(percentage) + "%)"

			self.P.rewrite( "\tAS" + str(AS_number) + " - " + str(counter) + " of " + str(len(AS_numbers)) + " " + percentage_str + "           " )

			self.get_IXs( AS_number = AS_number )

	def __save_data( self ):
		if self.save_data_bool is False:
			return

		self.save_counter += 1

		if self.save_counter > 99:
			self.P.rewrite( "\tAS_Rank_Interface: __save_data: Start... -*-*-*- DO NOT TERMINATE PROGRAM -*-*-*-         ", color = 'yellow', force_new_line = True )

			self.FT.save_JSON_file( file_name = "Peering_DB_Interface_AS_to_IXs.json", data_JSON = self.IXs_dict )
			self.FT.create_checksum( file_name = "Peering_DB_Interface_AS_to_IXs.json" )
			self.save_counter = 0

			self.P.rewrite( "AS_Rank_Interface: __save_data: done!                                                      ", color = 'green', keep_this_line = True )

	def __get_data( self, url = None, file_name = None ):
		relative_folder_path = "../tmp"
		file_name = file_name + self.RANDOM_STRING + ".html"
		file_path = self.FT.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		#Remove Old Temp Files
		if self.FT.check_file_exists( relative_folder_path = relative_folder_path, file_name = file_name ) is True:
			os.remove( self.FT.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name ) )

		wget.download( url = url, out=file_path, bar = None )
		return self.FT.load_CSV_file( relative_folder_path = relative_folder_path, file_name = file_name, seperator = "\n", simple_mode = True )

	def get_IXs( self, AS_number = None ):
		if str(AS_number) in self.IXs_dict:
			return self.IXs_dict[str(AS_number)]

		url = self.base_url + str(AS_number)
		data_text_list = self.__get_data( url = url, file_name = "temp" )

		IXs = list()
		for line in data_text_list:
			words = self.ST.get_words_after_substring( full_text=line, sub_text_before_words = "Network - Exchange link: ", numberOfWords = 1 )

			if len(words) == 0:
				continue

			IXs.append( words[0] )

		self.IXs_dict[str(AS_number)] = list(set(IXs))
		self.__save_data()

		return self.IXs_dict[str(AS_number)]






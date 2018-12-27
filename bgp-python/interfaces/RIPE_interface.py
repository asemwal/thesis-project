import json, wget, os, sys

sys.path.append( str(os.getcwd()) + "/../src" )

from string_tool import String_Tool
from file_tool import File_Tool

class RIPE_Interface():
	P = None
	ST = None
	FT = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "RIPE_Interface : __init__ : P is None" )

		self.P.write( "RIPE_Interface: Loading...", color = 'cyan' )

		self.ST = String_Tool()
		self.FT = File_Tool( P = self.P, base_path = "tmp/", program_name = "RIPE_Interface" )

	def get_all_RRC_peer_AS_numbers( self ):
		RRC_number_list = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21 ]
		AS_list = list()

		for RRC_number in RRC_number_list:
			self.P.rewrite( "Loading ASes of RRC" + str(RRC_number).zfill(2) )
			AS_list.extend( self.get_RRC_peer_AS_numbers( RRC_number = RRC_number ) )

		return list(sorted(set(AS_list)))

	def get_RRC_peer_AS_numbers( self, RRC_number ):
		RRC_number = str(RRC_number).zfill(2)
		local_AS_list = list()

		file_name_html = "rrc" + RRC_number + ".html"
		file_name_shtml = "rrc" + RRC_number + ".shtml"

		file_path = self.FT.get_file_path( file_name = file_name_html )
		url = "http://www.ris.ripe.net/peerlist/" + str(file_name_shtml)
		wget.download( url = url, out=file_path, bar = None )
		data_text_list = self.FT.load_CSV_file( file_name = file_name_html, seperator = "\n", simple_mode = True )

		for line in data_text_list:
			words = self.ST.get_words_after_substring( full_text=line, sub_text_before_words = "https://stat.ripe.net/AS", numberOfWords = 1 )

			if len(words) == 0:
				continue

			local_AS_list.append( int(words[0]) )

		return list( sorted( set( local_AS_list ) ) )


		
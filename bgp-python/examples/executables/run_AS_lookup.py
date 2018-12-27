import sys, os, json, time

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from clear_screen_tool import Clear_Screen_Tool
from geo_interface import Geo_Interface
from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface

class AS_Lookup():
	P = None
	GI = None
	RSI = None
	ASRI = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer( write_to_file = True, printer_id = "Test" )

		self.GI = Geo_Interface( P = self.P )
		self.RSI = RIPE_Stat_Interface( P = self.P )
		self.ASRI = AS_Rank_Interface( P = self.P )

	def auto_download( self ):
		self.P.write( "AS_Lookup: run: auto_download", color = 'green' )

		self.ASRI.auto_download()
		self.RSI.bulk_download( AS_numbers = self.ASRI.get_all_saved_ASes() )

	def get_AS_number( self, IP4_address = None ):
		AS_number = self.GI.get_AS_number( IP4_address = IP4_address )
		self.P.write( AS_number )
		IP4_prefix = None

	def run( self ):
		self.P.write( "AS_Lookup: run: start", color = 'green' )
		# Load Data From RIPE_Stat_Interface and AS_Rank_Interface in local file cache
		#self.auto_download()
		
		# Geo_Interface.py
		# IP4 ONLY, using port 4000 on Mars
		# Using IP4 Address
		AS_number = self.GI.get_AS_number( IP4_address = "100.100.100.100" )
		self.P.write( AS_number )

		# Using IP4 Prefix
		AS_number = self.GI.get_AS_number( IP4_prefix = "171.21.80.0/22" )
		self.P.write( AS_number )

		# RIPE_Stat_Interface.py
		# IP4 and IP6 prefixes (ONLY DIRECT MATCH)
		AS_numbers = self.RSI.get_AS_numbers( prefix = "171.21.80.0/22" )
		self.P.write( AS_numbers )

		# IP4 
		AS_numbers = self.RSI.get_AS_numbers( IP4_address = "171.21.80.0" )
		self.P.write( AS_numbers )

		AS_numbers = self.RSI.get_AS_numbers( IP6_address = "2001:67c:1514::" )
		self.P.write( AS_numbers )

		# Save RSI cache to disk
		self.RSI.save_data()

AS_Lookup().run()
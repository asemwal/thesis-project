import sys, os, json, time

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from clear_screen_tool import Clear_Screen_Tool
from are_you_sure_tool import Are_You_Sure_Tool
from printer import Printer
from time_tool import Time_Tool

from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from geo_interface import Geo_Interface
from simulator_interface import Simulator_Interface
from MRT_interface import ES_Interface
from MRT_interface import MRT_Interface
from gao import Gao

class Gao_Demo():
	P = None
	ARST = None

	ASRI = None
	RSI = None
	GI = None
	SI = None
	GAO = None

	TT = None
	ESI = None
	MRTI = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer()
		self.ARST = Are_You_Sure_Tool( P = self.P, program_name = "Simulator_ES_Relations_Tool" )
		self.TT = Time_Tool( P = self.P )
		self.ESI = ES_Interface( P = self.P )
		self.MRTI = MRT_Interface( P = self.P, ESI = self.ESI )


		self.ASRI = AS_Rank_Interface( P = self.P )
		self.RSI = RIPE_Stat_Interface( P = self.P )
		self.GI = Geo_Interface( P = self.P )
		self.SI = Simulator_Interface( P = self.P, ASRI = self.ASRI, RSI = self.RSI, GI = self.GI )

		self.GAO = Gao( P = self.P, SI = self.SI )

	def save_paths( self ):
		#Get time interval
		time_interval = self.TT.get_time_interval( time_start_str = "2017-01-01", time_end_str = "2017-01-01 00:00:05" )

		# Retrieve download pahts of MRT files from ElasticSearch index bgp-links
		# Only RIBs
		download_paths = self.MRTI.get_download_paths( RRC_number = 7, time_interval = time_interval, only_ribs = True )

		if len( download_paths ) == 0:
			self.P.write_error( "Process_Routes: save_paths: len( download_paths ) == 0" )
			return

		#Download MRT records
		records = self.MRTI.download_MRT_records( download_path = download_paths[0] )

		#Capture BGP paths
		counter = 0
		for record in records:
			if self.MRTI.is_RIB_record( record = record ) is True:
				routes = self.MRTI.get_RIB_routes( record = record )
				
				for route in routes:
					self.GAO.add_path( path = route['path'] )
					counter += 1

					if counter % 1000 == 0:
						self.P.rewrite( "Gao_Demo: save_paths: " + str(counter/1000) + "k routes processed")

			#if counter > 100000:
			#	break

		self.GAO.save_paths( file_name = "gao_demo" )

	def run( self ):
		self.P.write("Gao: run: do you want to save paths to the file 'gao_demo.paths'?", color = 'red' )
		if self.ARST.ask_are_you_sure() is True:
			self.save_paths()
		
		self.GAO.load_paths( file_name = "gao_demo" )
		self.GAO.run( print_debug = True )
		self.ESI.kill_thread()

Gao_Demo().run()
import sys, os

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from clear_screen_tool import Clear_Screen_Tool
from are_you_sure_tool import Are_You_Sure_Tool
from printer import Printer
from ask_tool import Ask_Tool
from time_tool import Time_Tool
from MRT_interface import MRT_Interface
from ES_interface import ES_Interface

class Download_MRT_Files():
	P = None
	CST = None
	ARST = None
	MRTI = None
	ESI = None

	def __init__( self ):
		self.CST = Clear_Screen_Tool()
		self.CST.clear_screen()

		#Tool to print output
		self.P = Printer()

		#Tool to ask Yes or No
		self.ARST = Are_You_Sure_Tool( P = self.P )

		#Tool to get user input
		self.AT = Ask_Tool( P = self.P )

		#Tool to measure time / get intervals / get time_epoch
		self.TT = Time_Tool( P = self.P )

		#Interface to ElasticSearch : download / upload routes, withdrawns, stats and state change messages
		self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False )

		#Interface to RouteViews, RIPE and ElasticSearch : index, delete, download and modify MRT files from RouteViews and RIPE RRCs
		self.MRTI = MRT_Interface( P = self.P, ESI = self.ESI )

	def run( self ):
		self.P.write("------------------------------------------------------------")
		RRC_number = self.AT.ask( question = "RRC_number:", expect_int = True )
		self.P.write( "RRC_number is " + str(RRC_number) )

		#Get time interval
		time_interval = self.TT.get_time_interval( time_start_str = "2018-01-01", time_end_str = "2018-01-01 08:00:00" )
		self.P.write( "time_interval is " + str(time_interval) )

		#Retrieve download pahts of MRT files from ElasticSearch index bgp-links
		download_paths = self.MRTI.get_download_paths( RRC_number = RRC_number, time_interval = time_interval )
		
		if len( download_paths ) == 0:
			self.P.write( "Download_And_Print: run: len( download_paths ) == 0", color = 'red' )
			return

		self.P.write( "found following download_paths:" )
		for download_path in download_paths:
			self.P.write( "\t" + download_path )
			
		#Select first download path in list
		download_path = download_paths[0]
		self.P.write( "download link " + str(download_path) )

		#Download MRT records
		records = self.MRTI.download_MRT_records( download_path = download_path )

		#Print MRT records
		for record in records:
			self.P.write( "Show next record?" )
			if self.ARST.ask_are_you_sure() is False:
				break

			data_JSON = self.MRTI.get_data_JSON( record = record )
			self.P.write( "Raw Data", color = 'green' )
			self.P.write_JSON( data_JSON = data_JSON )

			if self.MRTI.is_update_record( record = record ):
				routes = self.MRTI.get_update_routes( record = record )
				
				self.P.write( "Processed Data", color = 'green' )
				for route in routes:
					self.P.write_JSON( data_JSON = route )

			elif self.MRTI.is_RIB_record( record = record ) is True:
				routes = self.MRTI.get_RIB_routes( record = record )
				
				self.P.write( "Processed Data", color = 'green' )
				for route in routes:
					self.P.write_JSON( data_JSON = route )

Download_MRT_Files().run()













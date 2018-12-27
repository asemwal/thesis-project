import sys, os, json, time

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from ask_tool import Ask_Tool

from clear_screen_tool import Clear_Screen_Tool
from time_tool import Time_Tool
from ES_interface import ES_Interface
from MRT_interface import MRT_Interface

class Process_Routes():
	P = None
	TT = None
	AT = None
	ESI = None
	MRTI = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer()
		self.TT = Time_Tool( P = self.P )
		self.AT = Ask_Tool( P = self.P )
		self.ESI = ES_Interface( P = self.P )
		self.MRTI = MRT_Interface( P = self.P, ESI = self.ESI )

	def single_download_path_demo( self ):
		#Get time interval
		time_interval = self.TT.get_time_interval( time_start_str = "2017-01-01", time_end_str = "2017-01-01 08:00:00" )

		# Retrieve download pahts of MRT files from ElasticSearch index bgp-links
		# Only Updates
		RRC_number = 7
		download_paths = self.MRTI.get_download_paths( RRC_number = RRC_number, time_interval = time_interval, only_updates = True )

		if len( download_paths ) == 0:
			self.P.write_error( "Process_Routes: run: en( download_paths ) == 0" )
			return

		download_path = download_paths[1]

		# Set processed for download path
		self.MRTI.set_processed( download_path = download_path )

		# Reset processed for download path
		self.MRTI.reset_processed( download_path = download_path )

		#Download MRT records
		records = self.MRTI.download_MRT_records( download_path = download_path )

		#Processing MRT records
		counter = 0
		for record in records:
			counter += 1
			self.P.rewrite( "\tProcess_Routes: single_download_path_demo: processed " + str(counter) + " records...        " )

			if self.MRTI.is_update_record( record = record ):
				routes = self.MRTI.get_update_routes( record = record )
				
				for route in routes:
					self.ESI.put_route( route = route, RRC_number = RRC_number )

		self.P.rewrite( "\tProcess_Routes: single_download_path_demo: processed " + str(counter) + " records... DONE!        " )

		# Flush ES_Interface buffers
		self.ESI.flush()

		# Process bgp-withdraw items
		self.ESI.process_withdraws( RRC_number = RRC_number )

		# Kill ES_Route_Buffer
		self.ESI.kill_thread()

	def single_route_demo( self ):
		RRC_number = 0

		route_up = dict()
		route_up['next_hop'] = '10.0.0.0'
		route_up['dest_AS'] = 1
		route_up['source_AS'] = 3
		route_up['path'] = [ 3, 2, 1 ]
		route_up['mode'] = 'up'
		route_up['time'] = 1
		route_up['RRC_number'] = RRC_number
		route_up['start_IP'] = "192.168.1.0"
		route_up['end_IP'] = "192.168.1.255"

		route_down = dict()
		route_down['next_hop'] = '10.0.0.0'
		route_down['dest_AS'] = 1
		route_down['source_AS'] = 3
		route_down['path'] = [ 3, 2, 1 ]
		route_down['mode'] = 'down'
		route_down['time'] = 10
		route_down['RRC_number'] = RRC_number
		route_down['start_IP'] = "192.168.1.0"
		route_down['end_IP'] = "192.168.1.255"

		route_withdraw = dict()
		route_withdraw['next_hop'] = '10.0.0.0'
		route_withdraw['dest_AS'] = 1
		route_withdraw['mode'] = 'withdraw'
		route_withdraw['time'] = 7
		route_withdraw['RRC_number'] = RRC_number
		route_withdraw['start_IP'] = "192.168.1.0"
		route_withdraw['end_IP'] = "192.168.1.255"

		[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = route_up['time'] )

		# Add route_up to ES
		route_id = self.ESI.put_route( route = route_up, RRC_number = RRC_number )
		self.P.write( "Added route_up with _id = " + str(route_id) ) 

		# Flush ES_Interface buffers
		self.ESI.flush()

		# Get Route from ES
		self.ESI.get_id( index = "bgp-routes" + str(interval_str), id = route_id, print_server_response = True )

		# Delete Route from ES
		self.ESI.delete_id( index = "bgp-routes" + str(interval_str), id = route_id, print_server_response = True )

		# Reset Route_Buffer cache
		self.ESI.reset_route_buffer_cache()

		# Add route_up, route_down and route_withdraw to ES
		route_id = self.ESI.put_route( route = route_up, RRC_number = RRC_number )
		self.P.write( "Added route_up with _id = " + str(route_id) ) 

		route_id = self.ESI.put_route( route = route_down, RRC_number = RRC_number )
		self.P.write( "Added route_down with _id = " + str(route_id) ) 

		withdraw_id = self.ESI.put_route( route = route_withdraw, RRC_number = RRC_number )
		self.P.write( "Added route_withdraw with _id = " + str(withdraw_id) ) 

		# Flush ES_Interface buffers
		self.ESI.flush()

		# Get Route from ES
		self.ESI.get_id( index = "bgp-routes" + str(interval_str), id = route_id, print_server_response = True )

		# Get withdraw from ES
		self.ESI.get_id( index = "bgp-withdraws", id = withdraw_id, print_server_response = True )

		# Wait for ES to process
		time.sleep(1)

		# Process bgp-withdraw items
		self.ESI.process_withdraws( RRC_number = RRC_number )

		# Get Route from ES
		self.ESI.get_id( index = "bgp-routes" + str(interval_str), id = route_id, print_server_response = True )

		# Kill ES_Route_Buffer
		self.ESI.kill_thread()

	def run( self ):
		Clear_Screen_Tool().clear_screen()
		mode = self.AT.ask( "Select demo: single_download_path_demo, single_route_demo (1/2)?", expect_list = [ 1, 2 ] )

		if "1" in mode:
			self.single_download_path_demo()
		elif "2" in mode:
			self.single_route_demo()

Process_Routes().run()
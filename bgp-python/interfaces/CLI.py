import sys, os, datetime, time, urllib2, urllib, requests, json, shutil, glob, gzip, struct, base64, wget, calendar, copy
from time import sleep
from random import randint

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer

from ES_interface import ES_Interface
from AS_rank_interface import AS_Rank_Interface
from BGP_view_interface import BGP_View_Interface
from peering_DB_interface import Peering_DB_Interface
from simulator_interface import Simulator_Interface

from MRT_interface import MRT_Interface

from time_tool import Time_Tool
from ask_tool import Ask_Tool
from file_tool import File_Tool
from params_tool import Params_Tool
from string_tool import String_Tool
from read_line_tool import Read_Line_Tool
from CLI_input_handler import CLI_Input_Handler
from are_you_sure_tool import Are_You_Sure_Tool

class CLI():
	AT = None
	IH = None

	ESI = None
	ASRI = None
	BGVPI = None
	MRTI = None
	PDBI = None
	CI = None

	TT = None
	PT = None
	P = None
	SI = None
	FT = None
	RLT = None
	ARST = None

	processed_downloads_list = None

	ROUTES = None
	LINKS = None
	STATE_CHANGE = None

	RANDOM_STRING = None
	printer_id = None

	def __init__( self, stand_alone = True, P = None, printer_id = "temp", ESI = None, MRTI = None, ASRI = None, BGPVI = None, PDBI = None ):
		self.printer_id = printer_id

		if P is not None:
			self.P = P
		else:
			self.P = Printer( write_to_file = True, printer_id = printer_id )
			self.P.write( "[WARNING] CLI : __init__ : P is None", color = 'yellow' )

		self.RANDOM_STRING = "_" + str(randint(0, 1000000000))

		self.P.write( "CLI: Loading... (stand_alone = " + str(stand_alone) + ", RANDOM_STRING = " + self.RANDOM_STRING + ")", color = 'cyan' )

		self.ROUTES = "bgp-routes"
		self.LINKS = "bgp-links"

		self.FT = File_Tool( P = self.P, program_name = "CLI.py" )
		self.P.write( "CLI : __init__ : Clearing tmp folder..." )
		self.FT.clear_folder( relative_folder_path = "tmp/" )

		self.AT = Ask_Tool( P = self.P )

		if ESI is None:
			self.ESI = ES_Interface( P = self.P )
		else:
			self.ESI = ESI

		if MRTI is None:
			self.MRTI = MRT_Interface( P = self.P, ESI = self.ESI )
		else:
			self.MRTI = MRTI

		if ASRI is None:
			self.ASRI = self.ASRI = AS_Rank_Interface( P = self.P )
		else:
			self.ASRI = ASRI

		if BGPVI is None:
			self.BGPVI = BGP_View_Interface( P = self.P )
		else:
			self.BGPVI = BGPVI

		if PDBI is None:
			self.PDBI = Peering_DB_Interface( P = self.P, ASRI = self.ASRI )
		else:
			self.PDBI = PDBI

		self.SI = Simulator_Interface( P = self.P, ASRI = self.ASRI )

		self.TT = Time_Tool( P = self.P )
		self.PT = Params_Tool( P = self.P )

		self.ST = String_Tool()

		self.IH = CLI_Input_Handler( P = self.P )

		self.ARST = Are_You_Sure_Tool( P = self.P )

		self.processed_downloads_list = list()
		
		if self.ESI.exists_index( index = self.LINKS ) is False:
			self.__create_links_index()
			self.P.write( "CLI: __init__: first run command --update-links", color = 'red' )

		if stand_alone is True:
			self.RLT = Read_Line_Tool( program_name = "cli", P = self.P )
			self.P.write()
			self.P.write("\t-*-*-*- READY -*-*-*-", color = 'green' )

			self.IH.print_help()
			while True:
				keywords = self.wait_for_input()
				self.pick_function( keywords = keywords )

	def download_routes( self, RRC_number = None, RRC_range = None, time_interval = None ):
		if RRC_number is not None:
			RRC_range = [ RRC_number, RRC_number ]

		if RRC_range is None and RRC_number is None:
			self.P.write_error( "CLI: download_routes: RRC_range is None and RRC_number is None" )
			return None

		if time_interval is None:
			self.P.write_error( "CLI: download_routes: time_interval is None" )
			return None

		for RRC_number in range( RRC_range[0], RRC_range[1] + 1 ):
			self.P.write( "CLI: download: RRC_number = " + str(RRC_number) )
			processed_list = self.MRTI.get_download_paths( RRC_number = RRC_number, time_interval = time_interval, include_processed = True, include_not_processed = False )
			not_processed_list = self.MRTI.get_download_paths( RRC_number = RRC_number, time_interval = time_interval, include_processed = False, include_not_processed = True )

			self.P.write( "Found " + str( len(not_processed_list) ) + " items to process...")
			self.P.write( "Found " + str( len(processed_list) ) + " items already processed...")

			counter = 0
			done = len(processed_list)
			todo = len(not_processed_list)
			self.ESI.update_stats( RRC_number = RRC_number, done = done, todo = todo )
			for download_path in not_processed_list:
				counter = counter + 1
				self.ESI.update_stats( RRC_number = RRC_number, done = done, todo = todo )
				self.__download( download_path = download_path, counter = counter, size = len(not_processed_list), RRC_number = RRC_number, done = done, todo = todo )
				done += 1
				todo -= 1

			self.flush()

	def burst_prefix( self, prefix = None, time_interval = None, RRC_range = None, AS_numbers = None ):
		return

	def draw_prefix( self, prefix = None, epoch_time = None, RRC_range = None, AS_numbers = None ):
		answer = self.AT.ask( question = "CLI: draw_prefix: draw labels (Y/N)?", expect_list = [ "Y", "N" ] )
		if "Y" in answer:
			draw_labels = True
		elif "N" in answer:
			draw_labels = False

		prefix = prefix[0]

		AS_graph = self.SI.init_AS_graph( use_AS_rank = True, print_debug = False )
		AS_graph = self.SI.add_ES_routes( AS_graph = AS_graph, RRC_range = RRC_range, prefix = prefix, good_ASes = AS_numbers, time_str = epoch_time )
		AS_graph = self.SI.remove_unused_ASes( AS_graph = AS_graph )

		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
		routing_state = self.SI.generate_routing_state( routing_table = routing_table, calculate_passing_ASes = True )

		self.SI.write_routing_table_statistics( routing_table = routing_table )
		self.SI.write_routing_state_statistics( routing_state = routing_state )

		self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, draw_unused_links = True, draw_labels = draw_labels, file_name = "CLI_" + str(prefix).replace(".","_").replace("/","_") + "_" + str(epoch_time) )

	def flush( self ):
		self.P.write( "CLI: download : flushing send buffers")
		self.ESI.flush()
		self.process_downloaded_list()

	def __download( self, download_path = None, counter = None, size = None, RRC_number = None, done = None, todo = None ):
		process_downloads_list = False
		if len(self.processed_downloads_list) > 10:
			process_downloads_list = True
		elif "view." in str(download_path):
			process_downloads_list = True
		elif "rib." in str(download_path):
			process_downloads_list = True

		if process_downloads_list is True:
			self.flush()

		percentage_float = float(counter) / float(size) * 100.0
		percentage_string = "(" + str(float("{0:.2f}".format(percentage_float))) + "%)"

		records = self.MRTI.download_MRT_records( download_path = download_path, RRC_number = RRC_number )
		error_counter = [ 0, 0, 0, 0 ]

		temp_TT = Time_Tool( P = self.P, no_output = True )
		record = 0
		counter = 0
		temp_counter = 0
		for record in records:
			#self.MRTI.print_record( record = record )

			if type(record) is int:
				error_counter[ record ] += 1
				continue

			delta = self.__process_record( record = record, RRC_number = RRC_number )

			counter += delta
			temp_counter += delta

			if temp_counter>3000 and counter != 0:
				temp_counter = 0
				time_float = temp_TT.get_elapsed_time_S_float()

				avg_float = float(time_float) / float(counter)
				amount_float = round(1.0 / avg_float,0)

				avg = str( format(avg_float * 1000.0, '.2f') ) + "ms"
				amount = str( int(amount_float) ) + " per second"
				temp_string = "[ " + str(error_counter[0]) + ", " + str(error_counter[1]) + ", " + str(error_counter[2]) + ", " + str(error_counter[3]) + " ]"
				self.P.rewrite( "\t" + str(avg) + " - "  + str(amount) + " - " + str(counter) + " - " + str(temp_string) + "                                                        ")                                                     

				if "view" in download_path:
					self.ESI.update_stats( RRC_number = RRC_number, mode = "view", count = counter, ms = avg_float * 1000.0, ps = amount_float, done = done, todo = todo )
				elif "update" in download_path:
					self.ESI.update_stats( RRC_number = RRC_number, mode = "update", count = counter, ms = avg_float * 1000.0, ps = amount_float, done = done, todo = todo )

		self.processed_downloads_list.append( str(download_path) )

		process_downloads_list = False
		if len(self.processed_downloads_list) > 10:
			process_downloads_list = True
		elif "view." in str(download_path):
			process_downloads_list = True
		elif "rib." in str(download_path):
			process_downloads_list = True

		if process_downloads_list is True:
			self.flush()
					
	def process_downloaded_list( self ):
		self.P.write( "CLI: process_downloaded_list")
		for download_path in self.processed_downloads_list:
			self.MRTI.set_processed( download_path = download_path, print_server_response = False )

		self.processed_downloads_list = list()

	def __process_state_change( self, record ):
		new_state = self.MRTI.get_new_state( record = record )
		time_stamp = self.MRTI.get_time_stamp( record = record )
		peer_AS = self.MRTI.get_peer_AS( record = record )

		self.ESI.put_state_change( peer_AS = peer_AS, time_stamp = time_stamp, new_state = new_state )

	def __process_record( self, record, print_debug = False, RRC_number = None ):
		if self.MRTI.is_state_change_record( record = record ) is True:

			new_state = self.MRTI.get_new_state( record = record )
			peer_AS = self.MRTI.get_peer_AS( record = record )

			#self.P.write( str(new_state) + " : " + str(peer_AS) )

			self.__process_state_change( record = record )

			return 1

		elif self.MRTI.is_update_record( record = record ):
			routes = self.MRTI.get_update_routes( record = record )
			for route in routes:

				if route is None:
					continue
					
				if len( route ) == 0:
					continue

				self.ESI.put_route( route = route, RRC_number = RRC_number )

			return len(routes)

		elif self.MRTI.is_RIB_record( record = record ) is True:
			routes = self.MRTI.get_RIB_routes( record = record )
			for route in routes:

				if route is None:
					continue

				if len( route ) == 0:
					continue

				self.ESI.put_route( route = route, RRC_number = RRC_number )

			return len(routes)

		return 0
	
	def custom_loop( self, RRC_range = None ):
		if RRC_range is None:
			self.P.write_error( "CLI: custom_loop: RRC_range is None" )
			return None

		for RRC_number in range( RRC_range[0], RRC_range[1] + 1 ):
			self.ESI.update_stats( RRC_number = RRC_range[0], mode = "loaded" )

			time_interval = self.TT.get_time_interval( time_start_str = "2016-09-07", time_end_str = "2016-09-07 09:00:00" )

			from_time = datetime.datetime.utcfromtimestamp( time_interval[0] ).strftime('%Y-%m-%d %H:%M:%S UTC')
			to_time = datetime.datetime.utcfromtimestamp( time_interval[1] ).strftime('%Y-%m-%d %H:%M:%S UTC')
			self.P.write( "\tINTERVAL: " + str(from_time) + " (" + str(time_interval[0]) + ") to " + str(to_time) + " (" + str(time_interval[1]) + ") | (default)" )

			self.download_routes( time_interval = time_interval, RRC_number = RRC_number )
			self.ESI.update_stats( RRC_number = RRC_range[0], mode = "closed" )
		
		self.quit()

	def pick_function( self, keywords ):
		if len(keywords) == 0:
			return
		elif keywords[0] == "exit" or keywords[0] == "quit":
			self.P.write( "Stopping CLI...", color = 'cyan' )
			self.quit()
		elif keywords[0] == "CLI":
			params = self.PT.get_params( index = 1, keywords = keywords )
			
			function = self.IH.get_function( params = params )
			prefix = self.IH.get_prefix( function = function, params = params )
			RRC_range = self.IH.get_RRC_range( function = function, params = params )
			time_interval = self.IH.get_time_interval( function = function, params = params )
			epoch_time = self.IH.get_epoch_time( function = function, params = params )
			AS_numbers = self.IH.get_AS_numbers( function = function, params = params )

			if function is None:
				return

			#GENERAL
			elif "clear-temp-folder" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.FT.clear_folder( relative_folder_path = "tmp/" )
			elif "clear-output-folder" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.FT.clear_folder( relative_folder_path = "output/" )
			elif "reset-input-history" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.FT.clear_folder( relative_folder_path = "log/" )
					self.P.write( "CLI: restart required" )
			elif "custom-loop" in function and RRC_range is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.custom_loop( RRC_range = RRC_range )
			elif "calculate-rrc-coverage" in function and time_interval is not None and RRC_range:
				if self.ARST.ask_are_you_sure() is True:
					self.calculate_rrc_coverage( time_interval = time_interval, RRC_range = RRC_range )
			elif "burst-prefix" in function and prefix is not None and time_interval is not None and RRC_range is not None and AS_numbers is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.burst_prefix( prefix = prefix, time_interval = time_interval, RRC_range = RRC_range, AS_numbers = AS_numbers )
			elif "draw-prefix" in function and prefix is not None and epoch_time is not None and RRC_range is not None and AS_numbers is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.draw_prefix( prefix = prefix, epoch_time = epoch_time, RRC_range = RRC_range, AS_numbers = AS_numbers )

			#MRT_INDEXER		
			elif "reset-processed" in function and RRC_range is not None and time_interval is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.MRTI.reset_processed( RRC_range = RRC_range, time_interval = time_interval )
			elif "reset-links" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.MRTI.delete_links_index()
					self.MRTI.create_links_index()
			elif "create-links" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.MRTI.create_links_index()
			elif "delete-links" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.MRTI.delete_links_index()

			elif "update-links" in function and RRC_range is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.MRTI.setup_links_index()

					seconds_in_a_month = 2678400
					time_interval = [ time.time() - seconds_in_a_month, 2147483647 ] 

					self.MRTI.index( RRC_range = RRC_range, time_interval = time_interval )

			elif "load-links" in function and time_interval is not None and RRC_range is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.MRTI.setup_links_index()
					self.MRTI.index( RRC_range = RRC_range, time_interval = time_interval )

			#ES_ROUTES
			elif "reset-routes" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.ESI.reset_routes_index()
			elif "download-routes" in function and RRC_range is not None and time_interval is not None:
				if self.ARST.ask_are_you_sure() is True:
					self.download_routes( RRC_range = RRC_range, time_interval = time_interval )

			#ES_STATS_TOOL
			elif "reset-stats" in function:
				if self.ARST.ask_are_you_sure() is True:
					self.ESI.reset_stats_index()
			
			#ES_WITHDRAW_TOOL
			elif "reset-withdraws" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.delete_withdraws_index()
					self.ESI.create_withdraws_index()
			elif "delete-withdraws" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.delete_withdraws_index()
			elif "create-withdraws" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.create_withdraws_index()

			elif "process-withdraws" in function:
				if self.ARST.ask_are_you_sure() is True and RRC_range is not None and time_interval is not None:
					self.ESI.process_withdraws( RRC_number = None, RRC_range = RRC_range, time_interval = time_interval )

			#ES_STATE_CHANGE
			elif "reset-state-change" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.delete_state_change_index()
					self.ESI.create_state_change_index()
			elif "create-state-change" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.create_state_change_index()
			elif "delete-state-change" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.delete_state_change_index()

			#SIMULATOR_RELATIONS_TOOL
			elif "reset-relations" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.delete_relations_index()
					self.SI.create_relations_index()
			elif "delete-relations" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.delete_relations_index()
			elif "create-relations" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.create_relations_index()
			elif "flush-AS-rank-relations" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.flush_AS_rank_relations()

			#SIMULATOR_TRACE_ROUTES_TOOL
			elif "reset-trace-routes" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.delete_trace_routes_index()
					self.SI.create_trace_routes_index()
			elif "delete-trace-routes" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.delete_trace_routes_index()
			elif "create-trace-routes" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.create_trace_routes_index()
			elif "flush-trace-routes-from-CSV" in function:
				if self.ARST.ask_are_you_sure():
					self.SI.flush_ES_trace_routes_from_CSV( print_server_response = False )

			#ES_COVERAGE_BUFFER
			elif "reset-coverage" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.delete_coverage_index()
					self.ESI.create_coverage_index()
			elif "create-coverage" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.create_coverage_index()
			elif "delete-coverage" in function:
				if self.ARST.ask_are_you_sure():
					self.ESI.delete_coverage_index()
			elif "load-RRC-coverage" in function and RRC_range is not None and time_interval is not None:
				if self.ARST.ask_are_you_sure():
					self.CI.load_RRC_coverage( RRC_number = None, RRC_range = RRC_range, time_interval = time_interval )
			elif "load-AS-rank-coverage" in function:
				if self.ARST.ask_are_you_sure():
					self.CI.load_AS_rank_coverage()
			elif "load-BGP-view-coverage" in function:
				if self.ARST.ask_are_you_sure():
					self.CI.load_BGP_view_coverage()
			elif "load-IX-coverage" in function:
				if self.ARST.ask_are_you_sure():
					self.CI.load_IX_coverage()
			elif "cache-AS-rank" in function:
				if self.ARST.ask_are_you_sure():
					self.ASRI.bulk_download()
			elif "cache-peering-DB" in function:
				if self.ARST.ask_are_you_sure():
					self.PDBI.auto_download()
		else:
			if len( keywords[0] ) != 0:
				self.P.write( "\tInput Error: command '" + str(keywords[0]) + "' not known, expects, 'exit', 'quit' or other commands", color = 'red' )
				self.P.write( "\tInput Error: no parameter given, use --help", color = 'red' )	

	def quit( self ):
		self.P.write( "CLI : quit" )
		self.ESI.kill_thread()
		exit()

	def wait_for_input( self ):
		var = self.RLT.read_line()

		temp_vars = var.split(" ")

		final_vars = list()
		for var in temp_vars:
			if len(var) != 0:
				final_vars.append(var)

		if len( final_vars ) > 0 and  "--" in final_vars[0]:
			final_vars.insert( 0, "CLI" )

		return final_vars		


		
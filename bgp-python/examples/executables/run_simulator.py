import sys, os, json, time, copy, random

from netaddr import *

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from geo_interface import Geo_Interface

from printer import Printer
from time_tool import Time_Tool
from file_tool import File_Tool
from clear_screen_tool import Clear_Screen_Tool
from simulator_interface import Simulator_Interface
from are_you_sure_tool import Are_You_Sure_Tool
from ask_tool import Ask_Tool

class Simulator():
	P = None
	ARST = None
	TT = None
	FT = None
	AT = None

	ASRI = None
	BGPVI = None
	GI = None
	SI = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer()
		self.ARST = Are_You_Sure_Tool( P = self.P )
		self.TT = Time_Tool( P = self.P )
		self.FT = File_Tool( P = self.P, base_path = "tmp", program_name = "Simulator" )
		self.AT = Ask_Tool( P = self.P )

		self.ASRI = AS_Rank_Interface( P = self.P )
		self.RSI = RIPE_Stat_Interface( P = self.P )
		self.GI = Geo_Interface( P = self.P )
		self.SI = Simulator_Interface( P = self.P, ASRI = self.ASRI, RSI = self.RSI, GI = self.GI )
		
	def ES_links_demo( self ):
		self.P.write( "ES_links_demo: start", color = 'green' )

		# Use AS Rank data to initialise the AS_graph
		AS_graph = self.SI.init_AS_graph( use_AS_rank = True, print_debug = False )

		# Add Sibling relations from Christian
		AS_graph = self.SI.add_possible_siblings( AS_graph = AS_graph, print_debug = False )

		# Add found links in routes to AS_graph 
		time_interval = self.TT.get_time_interval( time_start_str = "2016-09-07", time_end_str = "2016-09-07 07:50:00" )
		AS_graph = self.SI.add_ES_links( AS_graph = AS_graph, RRC_number = 6, time_interval = time_interval, print_debug = False, print_server_response = False )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_links_demo_stage_1", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_1", print_status = True )

		# Create and Add BAD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "82.118.233.0/24", AS_number = 201133, good = True )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_links_demo_stage_2", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_2", print_status = True )

		# Create and Add BAD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "82.118.233.0/24", AS_number = 203959, good = False )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )		

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_links_demo_stage_3", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_3", print_status = True )

		# Calculate and Print Routing Table
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )

		# save and load routing_table to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_table)
		self.SI.save_routing_table( file_name = "ES_links_demo", routing_table = routing_table, print_status = True )
		routing_table = self.SI.load_routing_table( file_name = "ES_links_demo", print_status = True )

		# Calculate and Print routing_state
		routing_state = self.SI.generate_routing_state( routing_table = routing_table, calculate_passing_ASes = False )

		# save and load routing_state to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_state)
		self.SI.save_routing_state( file_name = "ES_links_demo", routing_state = routing_state, print_status = True )
		routing_state = self.SI.load_routing_state( file_name = "ES_links_demo", print_status = True )

		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_3", print_status = True )
		routing_table = self.SI.load_routing_table( file_name = "ES_links_demo", print_status = True )
		routing_state = self.SI.load_routing_state( file_name = "ES_links_demo", print_status = True )

		# Print routing_table statistics
		self.SI.write_routing_table_statistics( routing_table = routing_table )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

	def ES_routes_demo( self ):
		self.P.write( "ES_routes_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph( use_AS_rank = True, print_debug = False )

		# Add Sibling relations from Christian
		AS_graph = self.SI.add_possible_siblings( AS_graph = AS_graph, print_debug = False )

		# Add found links in routes to AS_graph 
		time_interval = self.TT.get_time_interval( time_start_str = "2016-09-07", time_end_str = "2016-09-07 07:50:00" )
		AS_graph = self.SI.add_ES_links( AS_graph = AS_graph, RRC_number = 6, time_interval = time_interval, print_debug = False, print_server_response = False )

		# Load ES routes into AS_graph that are alive at 2016-09-07 00:05:00 which encapsulates 82.118.233.0/24
		AS_graph = self.SI.add_ES_routes( AS_graph = AS_graph, RRC_range = [0,21], prefix = "82.118.233.0/24", good_ASes = [ 201133 ], ignore_ASes = [ 23456 ], time_str = "2016-09-07 07:50:00" )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_routes_demo", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_routes_demo", print_status = True )

		# Calculate and Print routing_state
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )

		# save and load routing_state to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_state)
		self.SI.save_routing_table( file_name = "ES_routes_demo", routing_table = routing_table, print_status = True )
		self.SI.load_routing_table( file_name = "ES_routes_demo", print_status = True )

		# Generate Routing Statue
		routing_state = self.SI.generate_routing_state( routing_table = routing_table, calculate_passing_ASes = False )
		
		# save and load routing_state to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_state)
		self.SI.save_routing_state( file_name = "ES_routes_demo", routing_state = routing_state, print_status = True )
		self.SI.load_routing_state( file_name = "ES_routes_demo", print_status = True )
	
		# Draw Routing State
		self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state )

		# Print routing_table statistics
		self.SI.write_routing_table_statistics( routing_table = routing_table )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

	def insert_announcements_demo( self ):
		self.P.write( "insert_announcements_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 1, customer = 2 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 2, customer = 3 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 3, customer = 4 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 4, customer = 5 )

		AS_graph = self.SI.add_provider( AS_graph = AS_graph, AS_number = 3, provider = 11 )
		AS_graph = self.SI.add_provider( AS_graph = AS_graph, AS_number = 11, provider = 12 )

		AS_graph = self.SI.add_peer( AS_graph = AS_graph, AS_number = 44, peer = 55 )

		# Add forwarding rule
		#AS_graph = self.SI.add_forwarding_rule( AS_graph = AS_graph, AS_number = 1, from_type = self.SI.get_P2P_type(), to_type = self.SI.get_C2P_type(), allow = True )

		# Set LOCAL_PREFERENCE
		AS_graph = self.SI.set_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = 3, to_AS = 11, LOCAL_PREFERENCE = 999 )

		# Save / Load AS Graph
		self.SI.save_AS_graph( AS_graph = AS_graph, file_name = "insert_announcements_demo", print_status = True )
		AS_Graph = self.SI.load_AS_graph( file_name = "insert_announcements_demo", print_status = True )

		# Create and Add GOOD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 1, good = True )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# Create and Add BAD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 12, good = False )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# Print AS_graph
		self.P.write_JSON( AS_graph )

		# Calculate and Print unique path found
		unique_paths = self.SI.get_unique_paths( AS_graph = AS_graph )
		self.P.write( "Simulator: custom_demo: unique paths:")
		self.P.write_JSON( unique_paths )

		# Calculate and Print Routing Table
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
		self.P.write( "Simulator: custom_demo: routing table:")
		self.P.write_JSON( routing_table )

		# Save / Load Routing Table
		self.SI.save_routing_table( routing_table = routing_table, file_name = "insert_announcements_demo", print_status = True )
		routing_table = self.SI.load_routing_table( file_name = "insert_announcements_demo", print_status = True )

		# Calculate and Print routing_state
		routing_state = self.SI.generate_routing_state( routing_table = routing_table )
		
		# Save / Load Routing State
		self.SI.save_routing_state( file_name = "insert_announcements_demo", routing_state = routing_state, print_status = True )
		routing_state = self.SI.load_routing_state( file_name = "insert_announcements_demo", print_status = True )


		self.P.write( "Simulator: custom_demo: routing_state:")
		self.P.write_JSON( routing_state )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

		# Draw AS_graph State
		self.SI.draw_AS_graph( AS_graph = AS_graph, file_name = "insert_announcements_demo" )

		# Draw Routing State
		self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, draw_unused_links = True, file_name = "insert_announcements_demo" )

		self.SI.compare_routing_states( routing_state_1 = routing_state, routing_state_2 = routing_state )

	def insert_routes_demo( self ):
		self.P.write( "insert_routes_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 1, customer = 2 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 2, customer = 3 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 3, customer = 4 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 4, customer = 5 )

		# create route
		route = dict()
		route['prefix'] = "192.168.2.0/24"
		route['path'] = [ 2, 3, 3, 3, 4, 4, 5 ]
		route['source_AS'] = 2

		# insert route
		AS_graph = self.SI.insert_route( AS_graph = AS_graph, route = route, good = True )

		# create route
		route2 = dict()
		route2['prefix'] = "192.168.2.0/20"
		route2['path'] = [ 1, 2, 3, 4, 4, 5 ]
		route2['source_AS'] = 1

		# insert route
		AS_graph = self.SI.insert_route( AS_graph = AS_graph, route = route2, good = False )

		# Print AS Graph
		self.P.write( "Simulator: insert_routes_demo: AS Graph:")
		self.P.write_JSON( AS_graph )

		# Calculate and Print unique path found
		unique_paths = self.SI.get_unique_paths( AS_graph = AS_graph )
		self.P.write( "Simulator: insert_routes_demo: unique paths:")
		self.P.write_JSON( unique_paths )

		# Calculate and Print Routing Table
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
		self.P.write( "Simulator: insert_routes_demo: routing_table:")
		self.P.write_JSON( routing_table )

		# Calculate and Print routing_state
		routing_state = self.SI.generate_routing_state( routing_table = routing_table )
		self.P.write( "Simulator: insert_routes_demo: routing_state:")
		self.P.write_JSON( routing_state )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

		# Draw AS_graph State
		self.SI.draw_AS_graph( AS_graph = AS_graph, file_name = "AS_graph" )

		# Draw Routing State
		self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, draw_unused_links = True )

	def type_prediction_demo( self ):
		self.P.write( "type_prediction_demo: start", color = 'green' )

		#TODO
		return

	def graph_validation_connectivity_demo( self ):
		self.P.write( "graph_validation_connectivity_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 1, customer = 2 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 2, customer = 3 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 3, customer = 4 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 4, customer = 5 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 12, customer = 11 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 11, customer = 3 )

		self.SI.validate_connectivity( AS_graph = AS_graph, AS_number = 1, print_debug = True )

		return

	def graph_create_legend_demo( self ):
		self.P.write( "graph_create_legend_demo: start", color = 'green' )
		self.SI.create_legend()
		return

	def load_save_relations_demo( self ):
		self.P.write( "load_save_relations_demo: start", color = 'green' )

		# -----
		# Simulator_ES_Relations_Tool serves as an interface between YOU and ElasticSeach index bgp-relations.
		# With flush() you send your local changes to ElasticSeach index bgp-relations
		# flush() is called internally every X updates. 
		# See simulation_interface.py: You can use the following arguments:
		#	print_server_response - print ES server response
		#	print_debug			  - print Simulator_ES_Relations_Tool debug information
		#	overwrite			  - overwrite existing entries (default = False)
		#	create 				  - add a new relation when True and relation does not yet exists (default = True)
		# An relation consists of:
		# 	from_AS
		# 	to_AS
		# 	source 				- where was the link found
		# 	type 					- [P2P, C2P, P2C, S2S, UNKOWN] = [0, 1, 2, 3, -1]
		# 	p2p 					- when the type switch to p2p 	
		# 	p2c					- when the type switch to p2c 
		# 	c2p 					- when the type switch to c2p 
		# 	s2s 					- when the type switch to s2s 
		# 	trace_route_ids 		- list of trace_route_ids asociated with it
		# -----

		# Reset ElasticSeach index bgp-relations 
		self.SI.delete_relations_index()
		self.SI.create_relations_index()

		# Add AS Rank data
		self.SI.add_AS_rank_relations( overwrite = True )

		# sync ElasticSeach index bgp-relations locally for faster processing 
		self.SI.sync_ES_relations()								# For all ASes

		# save and load LOCAL data
		self.SI.save_ES_relations( file_name = "test" )
		self.SI.load_ES_relations( file_name = "test" )

		# Add relation [USING dict()]
		relation = dict()
		relation['from_AS'] = 999
		relation['to_AS'] = 1000
		relation['type'] = self.SI.get_P2P_type()
		relation['source'] = 0 
		relation_id = self.SI.add_ES_relation( relation = relation, print_debug = True )

		# Add relation [USING arguments]
		relation_id = self.SI.add_ES_relation( from_AS = 999, to_AS = 1000, type = self.SI.get_P2P_type(), source = 1, overwrite = True, print_debug = True )

		# Retrieve relation [USING from_AS, to_AS]
		#relation = self.SI.get_ES_relation( from_AS = 286, to_AS = 1136, print_debug = True )
		#self.P.write_JSON( relation )

		# Retrieve relation [USING relation_id]
		relation = self.SI.get_ES_relation( relation_id = relation_id, print_debug = True )
		self.P.write_JSON( relation )

		# Send changed data to ES
		self.SI.flush_ES_relations()

	def load_save_trace_routes_demo( self ):
		self.P.write( "load_save_relations_demo: start", color = 'green' )

		# -----
		# Simulator_ES_Trace_Routes_Tool serves as an interface between YOU and ElasticSeach index bgp-trace-routes.
		# With flush() you send your local changes to ElasticSeach index bgp-trace-routes
		# flush() is called internally every X updates. 
		# See simulation_interface.py: You can use the following arguments:
		#	print_server_response - print ES server response
		#	print_debug			  - print Simulator_ES_Trace_Routes_Tool debug information
		# An traceroute consists of:
		# 	source_IP 		- for example: 192.168.2.1
		# 	dest_IP 		- for example: 133.168.2.1
		# 	path 			- for example: [AS1, AS2, ..., ASX ]
		# 	epoch time 		- when the traceroute was performed
		# 	relation_ids  	- list of relation_ids asociated with it
		# -----

		# Reset ElasticSeach index bgp-trace-routes 
		self.SI.delete_trace_routes_index()
		self.SI.create_trace_routes_index()

		# sync ElasticSeach index bgp-relations locally for faster processing 
		self.SI.sync_ES_trace_routes()							

		# save and load LOCAL data
		self.SI.save_ES_trace_routes( file_name = "test" )
		self.SI.load_ES_trace_routes( file_name = "test" )

		# Add traceroute METHOD 1
		trace_route = dict()
		trace_route['source_IP'] = "192.168.2.1"
		trace_route['dest_IP'] = "133.168.2.1"
		trace_route['path'] = [ 2, 4, 6, 8 ]
		trace_route['epoch_time'] = 3423423423
		trace_route_id = self.SI.add_ES_trace_route( trace_route = trace_route, print_debug = True )

		# Add traceroute METHOD 2
		trace_route_id = self.SI.add_ES_trace_route( source_IP = "127.127.127.0", dest_IP = "133.168.2.1", path = [ 2, 4, 6, 8 ], epoch_time = 3423423423, print_debug = True )
		
		# Get and Print trace_route
		trace_route = self.SI.get_ES_trace_route( trace_route_id = trace_route_id )
		self.P.write_JSON( trace_route )

		# Flush
		self.SI.flush_ES_trace_routes()

	def improver_missing_relatations_demo( self ):
		# Download ElasticSearch index bgp-relations locally
		#self.SI.sync_ES_relations( overwrite = True )

		#Save all relations in Simulator_ES_Relations_Tool to a file - FILE EXTENSION ARE ADDED AUTOMATICALLY (.relations)
		#self.SI.save_ES_relations( file_name = "demo")

		#Load known relations from file to Simulator_Relation_Type_Improver_Tool - FILE EXTENSION ARE ADDED AUTOMATICALLY (.relations)
		self.SI.load_improver_relations( file_name = "demo" )

		mode = None

		if mode == 1:			# Compute missing relations using locally stored trace routes
			trace_route = self.SI.create_trace_route( path = [99, 100, 101, 102], source_IP = "0.0.0.0", dest_IP = "1.1.1.1", epoch_time = 2222 )
			self.SI.add_improver_trace_route( trace_route = trace_route, print_debug = True )
			self.SI.compute_missing_relations( mode = "local", print_debug = True )
		elif mode == 2:			# Compute missing relations using relations found in ElasticSearch index bgp-trouce-route
			self.SI.compute_missing_relations( mode = "ES", print_debug = False )
		elif mode == 3:			# Compute missing relations using relations found in an external CSV File
			self.SI.compute_missing_relations( mode = "CSV", file_name = "traceroutes_asn.csv", print_debug = False )
		else:					# Choose for menu
			self.SI.compute_missing_relations()
		
		#Save all missing relations in Simulator_Relation_Type_Improver_Tool to a file - FILE EXTENSION ARE ADDED AUTOMATICALLY (.missing_relation)
		self.SI.save_improver_missing_relations( file_name = "demo" )

	def improver_predicting_relatations_demo( self ):
		self.SI.load_improver_relations( file_name = "demo" )
		self.SI.load_improver_missing_relations( file_name = "demo" )

		self.SI.predict_missing_relations( print_debug = False )

	def improver_rectify_relatations_demo( self ):
		#self.SI.add_AS_rank_relations()
		#self.SI.save_ES_relations( file_name = "AS_Rank" )
		self.SI.load_improver_relations( file_name = "AS_Rank" )
		self.SI.compute_wrong_relations( print_debug = False, print_server_response = False )

	def thesis( self ):
		self.SI.load_improver_relations( file_name = "AS_Rank" )
		missing_relations = self.SI.compute_missing_relations( print_debug = False, print_server_response = False )
		wrong_relations = self.SI.compute_wrong_relations( print_debug = False, print_server_response = False )

	def random_AS_graph_demo( self ):
		AS_graph = self.SI.generate_random_AS_graph( start_size = 2, AS_multiplier = 2, number_of_tiers = 3, second_provider_probability = [0,0.5,0.5], peer_probability = [1,0.5,0.1] )

		relations = self.SI.get_AS_graph_relations( AS_graph = AS_graph )
		trace_routes = self.SI.generate_random_trace_routes( AS_graph = AS_graph )
	
		self.P.write("Print AS relations?")
		if self.ARST.ask_are_you_sure() is True:
			for relation in relations:
				self.P.write_JSON( relations )

		self.P.write("Print trace routes?")
		if self.ARST.ask_are_you_sure() is True:
			for trace_route in trace_routes:
				self.P.write_JSON( trace_route )

		self.SI.draw_AS_graph( AS_graph = AS_graph, draw_labels = False )
		return

	def todo( self ):
		AS_graph = self.SI.generate_random_AS_graph( start_size = 2, AS_multiplier = 4, max_depth = 3, second_provider_probability = [0,1,0], peer_probability = [1,1,0] )
		
		self.SI.draw_AS_graph( AS_graph = AS_graph, draw_labels = False )
		return

		complete_relations = self.SI.get_AS_graph_relations( AS_graph = AS_graph )
		trace_routes = self.SI.generate_random_trace_routes( AS_graph = AS_graph )
		

		temp_relations = dict()
		for relation in complete_relations:
			relation_id = self.SI.get_relation_id( relation = relation )
			temp_relations[relation_id] = relation

		relation_ids = random.sample(temp_relations, 5)
		for relation_id in relation_ids:
			if relation_id not in temp_relations:
				continue

			relation = temp_relations[relation_id]
			from_AS = relation['from_AS']
			to_AS = relation['to_AS']

			reverse_relation_id = self.SI.get_relation_id( from_AS = to_AS, to_AS = from_AS )

			del temp_relations[relation_id]
			del temp_relations[reverse_relation_id]

		partial_relations = list()
		for relation_id in temp_relations:
			partial_relations.append( temp_relations[relation_id] )

		trace_routes = self.SI.generate_random_trace_routes( AS_graph = AS_graph )

		self.SI.reset_trace_routes_index()
		self.SI.add_ES_trace_routes( trace_routes = trace_routes )
		self.SI.flush_ES_trace_routes()

		self.SI.add_improver_relations( relations = partial_relations )
		#self.SI.add_improver_trace_routes( trace_routes = trace_routes )
		self.SI.compute_missing_relations( print_debug = False )
		self.SI.predict_missing_relations( print_debug = False )

		#self.SI.compute_missing_relations()
		#self.SI.rectify_relations()

		self.SI.draw_AS_graph( AS_graph = AS_graph )
		return

	def temp( self ):		
		self.P.write( "insert_announcements_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 1, customer = 2 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 2, customer = 3 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 3, customer = 4 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 4, customer = 5 )

		AS_graph = self.SI.add_provider( AS_graph = AS_graph, AS_number = 3, provider = 11 )
		AS_graph = self.SI.add_provider( AS_graph = AS_graph, AS_number = 11, provider = 12 )

		AS_graph = self.SI.add_peer( AS_graph = AS_graph, AS_number = 44, peer = 55 )
		AS_graph = self.SI.add_sibling( AS_graph = AS_graph, AS_number = 2, sibling = 55 )

		# Add forwarding rule
		AS_graph = self.SI.add_forwarding_rule( AS_graph = AS_graph, AS_number = 1, from_type = self.SI.get_P2P_type(), to_type = self.SI.get_C2P_type(), allow = True )

		# Create and Add GOOD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 1, good = False )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# Create and Add BAD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 44, good = False )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# Calculate and Print Routing Table
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
		routing_state = self.SI.generate_routing_state( routing_table = routing_table )

		self.P.write( "Simulator: custom_demo: routing_state:")
		self.P.write_JSON( routing_state )

		
	def run( self ):
		self.P.write( "Simulator Demos: run: has multiple modes:", color = 'green' ) 
		self.P.write( "\t(1)  - ES links" ) 
		self.P.write( "\t(2)  - ES routes" ) 
		self.P.write( "\t(3)  - announcements" ) 
		self.P.write( "\t(4)  - routes" ) 
		self.P.write( "\t(5)  - type prediction" ) 
		self.P.write( "\t(6)  - graph validation" ) 
		self.P.write( "\t(7)  - create legend" ) 
		self.P.write( "\t(8)  - load / save relations" ) 
		self.P.write( "\t(9)  - load / save trace routes" ) 
		self.P.write( "\t(10) - relation improver - missing relations" ) 
		self.P.write( "\t(11) - relation improver - predicting relations" )
		self.P.write( "\t(12) - relation improver - rectify relations" )  
		self.P.write( "\t(13) - random AS_graph" )  

		mode = self.AT.ask( question = "Select mode (1/2/3/4/5/6/7/8/9/10/11/12/13):", expect_list = range( 1, 13 + 1 ) )

		if mode == "1":
			self.ES_links_demo()
		elif mode == "2":
			self.ES_routes_demo()
		elif mode == "3":
			self.insert_announcements_demo()
		elif mode == "4":
			self.insert_routes_demo()
		elif mode == "5":
			self.type_prediction_demo()
		elif mode == "6":
			self.graph_validation_demo()
		elif mode == "7":
			self.graph_create_legend_demo()
		elif mode == "8":
			self.load_save_relations_demo()
		elif mode == "9":
			self.load_save_trace_routes_demo()
		elif mode == "10":
			self.improver_missing_relatations_demo()
		elif mode == "11":
			self.improver_predicting_relatations_demo()
		elif mode == "12":
			self.improver_rectify_relatations_demo()
		elif mode == "13":
			self.random_AS_graph_demo()

Simulator().run()






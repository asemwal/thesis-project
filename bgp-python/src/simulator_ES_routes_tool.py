import json, requests, os, sys, hashlib, copy, time

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from alive_tool import Alive_Tool
from time_tool import Time_Tool
from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from ES_interface import ES_Interface

from simulator_link_types import Simulator_Link_Types

class Simulator_ES_Routes_Tool():
	P = None
	AT = None
	TT = None
	ESI = None
	ASRI = None
	RSI = None
	SASGT = None
	SRPT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	ROUTES = None

	last_mode = None
	MODE_1 = None
	MODE_2 = None

	def __init__( self, P = None, ASRI = None, RSI = None, ESI = None, SASGT = None, SASGPT = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_ES_Routes_Tool: __init__ : P is None" )

		self.P.write( "Simulator_ES_Routes_Tool: Loading...", color = 'cyan' )
		self.TT = Time_Tool( P = self.P )
		self.AT = Alive_Tool( P = self.P, no_output = True )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __init__ : ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if RSI is not None:
			self.RSI = RSI
		else:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __init__ : RSI is None" )
			self.RSI = RIPE_Stat_Interface( P = self.P )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False, include_coverage = False, include_raw = False )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

		if SASGT is not None:
			self.SASGT = SASGT
		else:
			self.P.write_error( "Simulator_ES_Routes_Tool: __init__ : SASGT is None" )
			self.SASGT = Simulator_AS_Graph_Tool( P = None, ASRI = self.ASRI, RSI = self.RSI, ESI = self.ESI, SLT = self.SLT )

		if SASGPT is not None:
			self.SASGPT = SASGPT
		else:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __init__ : SRPT is None" )
			self.SASGPT = Simulator_AS_Graph_Predictor_Tool( P = self.P, ASRI = self.ASRI, SASGT = self.SASGT, SLT = self.SLT )

		self.ROUTES = "bgp-routes"

	def __get_unique_paths( self, RRC_range = None, RRC_number = None, time_interval = None, print_debug = False, print_server_response = False ):
		self.P.write( "Simulator_ES_Routes_Tool: __get_unique_paths: start", color = 'green' )

		if time_interval is None:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __get_unique_paths: time_interval is None" )
			self.P.write_warning( "Simulator_ES_Routes_Tool: add_ES___get_unique_pathsroutes: setting time_interval = [ 0, 2147483647 ]" )
			time_interval = [ 0, 2147483647 ]

		if RRC_range is None and RRC_number is None:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __get_unique_paths: RRC_range is None and RRC_number is None" )
			self.P.write_warning( "Simulator_ES_Routes_Tool: __get_unique_paths: setting RRC_range = [ 0, 40 ] " )
			RRC_range = [ 0, 40 ] 
		elif RRC_range is None and RRC_number is not None:
			RRC_range = [ RRC_number, RRC_number ] 

		unique_paths = dict()
		size = 100000
		
		data_JSON = dict()
		data_JSON['size'] = size
		data_JSON['query'] = dict()
		data_JSON['query']['bool'] = dict()
		data_JSON['query']['bool']['must'] = list()

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['RRC_number'] = dict()
		data_JSON_2['range']['RRC_number']['gte'] = RRC_range[0]
		data_JSON_2['range']['RRC_number']['lte'] = RRC_range[1]
		
		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['interval_start'] = dict()
		data_JSON_2['range']['interval_start']['lte'] = time_interval[0]

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['interval_end'] = dict()
		data_JSON_2['range']['interval_end']['gte'] = time_interval[1]

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		self.P.write_JSON( data_JSON )

		data_ES = self.ESI.search( index = self.ROUTES + "*", source_filtering = [ "path" ], data_JSON = data_JSON, scroll = "1m", print_server_response = print_server_response )
		scroll_id = data_ES['_scroll_id']
		
		for item in data_ES['hits']['hits']:
			path = item['_source']['path']
			path = list( OrderedDict.fromkeys( path ) )

			if str(path) not in unique_paths:
				unique_paths[ str(path) ] = path

		amount_left = data_ES['hits']['total'] - size

		finished = False
		while finished is False:
			if amount_left < 0:
				amount_left = 0

			self.P.rewrite( "\tSimulator_ES_Routes_Tool: __get_unique_paths: " + str(int(amount_left/1000)) + "k routes left, found " + str( len(unique_paths) ) + " unique paths" )
			data_ES = self.ESI.scroll( index = self.ROUTES + "*", scroll = "1m", scroll_id = scroll_id, print_server_response = print_server_response )
			
			if len( data_ES['hits']['hits'] ) == 0:
				finished = True

			for item in data_ES['hits']['hits']:
				path = item['_source']['path']
				path = list( OrderedDict.fromkeys( path ) )

				if str(path) not in unique_paths:
					unique_paths[ str(path) ] = path

			amount_left -= size

		return unique_paths

	def __get_ES_routes( self, RRC_range = None, RRC_number = None, prefix = None, time_epoch = None, print_server_response = False ):
		time_interval = [ int(time_epoch) - 3600 * 8, int(time_epoch) + 3600 * 8 ]

		if RRC_range is None and RRC_number is None:
			self.P.write_warning( "Simulator_ES_Routes_Tool: __get_unique_paths: RRC_range is None and RRC_number is None" )
			self.P.write_warning( "Simulator_ES_Routes_Tool: __get_unique_paths: setting RRC_range = [ 0, 40 ] " )
			RRC_range = [ 0, 40 ] 
		elif RRC_range is None and RRC_number is not None:
			RRC_range = [ RRC_number, RRC_number ] 

		routes = list()

		data_JSON = dict()
		data_JSON['size'] = 100000
		data_JSON['query'] = dict()
		data_JSON['query']['bool'] = dict()
		data_JSON['query']['bool']['must'] = list()

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['RRC_number'] = dict()
		data_JSON_2['range']['RRC_number']['gte'] = RRC_range[0]
		data_JSON_2['range']['RRC_number']['lte'] = RRC_range[1] + 1

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['interval_start'] = dict()
		data_JSON_2['range']['interval_start']['lte'] = time_interval[0]

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['interval_end'] = dict()
		data_JSON_2['range']['interval_end']['gte'] = time_interval[1]

		ip_range = IPNetwork( prefix )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['start_IP'] = dict()
		data_JSON_2['range']['start_IP']['lte'] = str(ip_range[0])

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['end_IP'] = dict()
		data_JSON_2['range']['end_IP']['gte'] = str(ip_range[ ip_range.size - 1 ])

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_ES = self.ESI.search( index = self.ROUTES + "*", data_JSON = data_JSON, print_server_response = print_server_response )

		for item in data_ES['hits']['hits']:
			routes.append( item['_source'] )

		self.P.write( "\tSimulator_ES_Tool: __get_ES_routes: found " + str(len(routes)) + " routes" )

		alive_routes = list()
		for route in routes:
			if "0.0.0.0" in route['start_IP']:
				continue

			if "::" in route['start_IP']:
				continue

			if self.AT.check_alive( alive = route['alive'], time = time_epoch ) is True:
				alive_routes.append( route )
				#self.P.write_JSON( route )

		self.P.write( "\tSimulator_ES_Tool: __get_ES_routes: found " + str(len(alive_routes)) + " alive routes" )

		return alive_routes

	def add_ES_links( self, AS_graph = None, RRC_range = None, RRC_number = None, time_interval = None, print_debug = False, print_server_response = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_ES_Routes_Tool: add_ES_links: AS_graph is None" )
			return None

		self.P.write( "Simulator_ES_Routes_Tool: add_ES_routes: start" )

		unique_paths = self.__get_unique_paths( RRC_range = RRC_range, RRC_number = RRC_number, time_interval = time_interval, print_server_response = print_server_response )

		routes = list()
		for path_id in unique_paths:
			route = dict()
			route['path'] = unique_paths[ path_id ]
			routes.append( route )

		AS_graph = self.SASGPT.auto_fill( AS_graph = AS_graph, routes = routes, print_debug = print_debug )

		return AS_graph

	def add_ES_routes( self, AS_graph = None, RRC_range = None, RRC_number = None, prefix = None, good_ASes = None, ignore_ASes = None, time_str = None, print_debug = False, print_server_response = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_ES_Routes_Tool: add_ES_routes: AS_graph is None" )
			return None

		if prefix is None:
			self.P.write_error( "Simulator_ES_Routes_Tool: add_ES_routes: prefix is None" )
			return None

		if good_ASes is None:
			self.P.write_error( "Simulator_ES_Routes_Tool: add_ES_routes: good_ASes is None" )
			return None

		if ignore_ASes is None:
			self.P.write_warning( "Simulator_ES_Routes_Tool: add_ES_routes: ignore_ASes is None" )
			self.P.write_warning( "Simulator_ES_Routes_Tool: setting ignore_ASes to []" )
			ignore_ASes = list()

		if time_str is None:
			self.P.write_error( "Simulator_ES_Routes_Tool: add_ES_routes: time_str is None" )
			return None

		self.P.write( "Simulator_ES_Tool: add_ES_routes: start", color = 'green' )

		time_epoch = self.TT.get_time_epoch( time_str = time_str )
		routes = self.__get_ES_routes( RRC_range = RRC_range, RRC_number = RRC_number, prefix = prefix, time_epoch = time_epoch, print_server_response = print_server_response )

		AS_graph = self.SASGPT.auto_fill( AS_graph = AS_graph, routes = routes, print_debug = False )

		for route in routes:
			good = False
			adding = True

			for good_AS in good_ASes:
				if str( route['source_AS'] ) == str(good_AS):
					good = True

			for ignore_AS in ignore_ASes:
				if str( route['source_AS'] ) == str(ignore_AS):
					adding = False

			if adding is True:
				AS_graph = self.SASGT.insert_route( AS_graph = AS_graph, route = route, good = good, print_debug = True )

		return AS_graph








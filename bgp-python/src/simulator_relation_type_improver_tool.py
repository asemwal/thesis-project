import json, requests, os, sys, hashlib, copy, time, random

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool
from ask_tool import Ask_Tool

from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from ES_interface import ES_Interface

from simulator_link_types import Simulator_Link_Types
from simulator_AS_graph_tool import Simulator_AS_Graph_Tool

from simulator_ES_relations_tool import Simulator_ES_Relations_Tool
from simulator_ES_trace_routes_tool import Simulator_ES_Trace_Routes_Tool

class Simulator_Relation_Type_Improver_Tool():
	P = None
	FT = None
	AT = None
	ASRI = None
	RSI = None
	ESI = None
	SESRT_2 = None
	SESTRT = None

	SLT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	trace_routes = None
	trace_routes_search = None
	relations = None

	TRACE_ROUTES = None

	missing_relations_processed_cache = None
	wrong_relations_processed_cache = None

	not_p2p_relations = None

	def __init__( self, P = None, FT = None, ASRI = None, RSI = None, ESI = None, SESRT_2 = None, SESTRT = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : P is None" )

		self.P.write( "Simulator_Relation_Type_Improver_Tool: Loading...", color = 'cyan' )
		self.AT = Ask_Tool( P = self.P )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Relation_Type_Improver_Tool" )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if RSI is not None:
			self.RSI = RSI
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : RSI is None" )
			self.RSI = RIPE_Stat_Interface( P = self.P )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False, include_coverage = False, include_raw = False )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		if SESRT_2 is not None:
			self.SESRT_2 = SESRT_2
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : SESRT_2 is None" )
			self.SESRT_2 = Simulator_ES_Relations_Tool( P = self.P, FT = self.FT, ASRI = self.ASRI, ESI = self.ESI, SLT = self.SLT )

		if SESTRT is not None:
			self.SESTRT = SESTRT
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __init__ : SESTRT is None" )
			self.SESTRT = Simulator_ES_Trace_Routes_Tool( P = self.P, FT = self.FT, ESI = self.ESI )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

		self.trace_routes = dict()
		self.trace_routes_search = dict()

		self.relations = dict()

		self.missing_relations_processed_cache = dict()
		self.wrong_relations_processed_cache = dict()
		self.not_p2p_relations = dict()

		self.TRACE_ROUTES = "bgp-trace-routes"

	def reset_improver_relations( self, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: reset_improver_relations" )

		self.relations = dict()
		self.not_p2p_relations = dict()

	def reset_improver_trace_routes( self, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: reset_improver_trace_routes" )

		self.trace_routes = dict()
		self.trace_routes_search = dict()

	def load_improver_relations( self, file_name = None, print_debug = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: load_improver_relations: file_name is None" )
			return None
	
		self.P.write( "Simulator_Relation_Type_Improver_Tool: load_improver_relations: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".relations"
		file_path = self.FT.get_file_path( file_name = file_name )

		if self.FT.check_file_exists( file_name = file_name ) is False:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: load_improver_relations: " + str(file_path) + " not found" )
		elif self.FT.check_checksum( file_name = file_name ) is True:
			data_JSON = self.FT.load_JSON_file( file_name = file_name, print_status = True )

			counter = len( data_JSON )
			for _id in data_JSON:
				counter -= 1
				if counter % 1000 == 0:
					self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: load_improver_relations: " + str(counter/1000) + "k relations left to process          " )
				
				self.add_improver_relation( relation = data_JSON[_id], print_debug = print_debug )

		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: load_improver_relations: " + str(file_path) + ": checksum incorrect or missing" )

		self.P.write( "Simulator_Relation_Type_Improver_Tool: load_improver_relations: done" ) 

	def save_improver_relations( self, relations = None, file_name = None, print_debug = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: save_improver_relations: file_name is None" )
			return None

		self.P.write( "Simulator_Relation_Type_Improver_Tool: save_improver_relations: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".relations"

		self.FT.save_JSON_file( data_JSON = self.relations, file_name = file_name, print_status = True )
		self.FT.create_checksum( file_name = file_name, print_status = True )

		self.P.write( "Simulator_Relation_Type_Improver_Tool: save_improver_relations: done" )

	def load_improver_trace_routes( self, file_name = None, print_debug = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: load_improver_trace_routes: file_name is None" )
			return None

		self.P.write( "Simulator_Relation_Type_Improver_Tool: load_improver_trace_routes: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".missing_relations"
		file_path = self.FT.get_file_path( file_name = file_name )

		if self.FT.check_file_exists( file_name = file_name ) is False:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: load_improver_trace_routes: " + str(file_path) + " not found" )
		elif self.FT.check_checksum( file_name = file_name ) is True:
			data_JSON = self.FT.load_JSON_file( file_name = file_name, print_status = True )

			counter = len( data_JSON )
			for _id in data_JSON:
				counter -= 1
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: load_improver_trace_routes: " + str(counter) + " relations left to process          " )
				self.add_improver_trace_route( relation = data_JSON[_id], print_debug = print_debug )
		else:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: load_improver_trace_routes: " + str(file_path) + ": checksum incorrect or missing" )

		self.P.write( "Simulator_Relation_Type_Improver_Tool: load_improver_trace_routes: done" )

	def save_improver_trace_routes( self, relations = None, file_name = None, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: save_improver_trace_routes: start" )

		if file_name is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: save_improver_trace_routes: file_name is None" )
			return None

		self.P.write( "Simulator_Relation_Type_Improver_Tool: save_improver_trace_routes: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".trace_routes"

		self.FT.save_JSON_file( data_JSON = self.found_dict, file_name = file_name, print_status = True )
		self.FT.create_checksum( file_name = file_name, print_status = True )

		self.P.write( "Simulator_Relation_Type_Improver_Tool: save_improver_trace_routes: done" )

	def add_improver_relation( self, relation = None, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_relation: start" )

		_id = self.SESRT_2.get_relation_id( relation = relation )

		if _id not in self.relations:
			self.relations[_id] = relation

			if print_debug is True:
				type_str = self.SLT.get_type_str( type = relation['type'] )
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_relation: added AS" + str(relation['from_AS']) + " - AS" + str(relation['to_AS']) + ", type = " + str(type_str) + ", source = " + str(relation['source'])  )
		else:
			type_str = self.SLT.get_type_str( type = relation['type'] )
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: add_improver_relation: AS" + str(relation['from_AS']) + " - AS" + str(relation['to_AS']) + ", type = " + str(type_str) + ", source = " + str(relation['source']) + ": already added"  )

	def add_improver_relations( self, relations = None, print_debug = False ):
		if relations is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: add_improver_relations: relations is None" )
			return None 

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_relations: start" )

		counter = len(relations)
		for relation in relations:
			self.add_improver_relation( relation = relation )
			counter -= 1
			self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: add_improver_relations: " + str(counter) + " relations left to process          " )

	def remove_improver_relation( self, relation = None, from_AS = None, to_AS = None, print_debug = False ):
		if relation is None and from_AS is None and to_AS is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: remove_improver_relation: relation is None and from_AS is None and to_AS is None" )
			return None 

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: remove_improver_relation: start" )

		if relation is not None:
			relation_id = self.SESRT_2.get_relation_id( from_AS = relation['from_AS'], to_AS = relation['to_AS'] )
			reversed_relation_id = self.SESRT_2.get_relation_id( from_AS = relation['to_AS'], to_AS = relation['from_AS'] )
		elif from_AS is not None and to_AS is not None:
			relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS )
			reversed_relation_id = self.SESRT_2.get_relation_id( from_AS = to_AS, to_AS = from_AS )
		else:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: remove_improver_relation: from_AS is not None or to_AS is not None" )
			return

		if relation_id in self.relations:
			del self.relations[ relation_id ]

		if reversed_relation_id in self.relations:
			del self.relations[ reversed_relation_id ]

	def add_improver_trace_route( self, trace_route = None, print_debug = False ):
		if trace_route is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_route: trace_route is None" )
			return None 

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_route: start" )

		for x in range(len(trace_route['path']) - 1, 0, -1):
			if trace_route['path'][x] == trace_route['path'][x-1]:
				trace_route['path'].pop(x)

		for x in range(0, len(trace_route['path'])):
			for y in range(x+1, len(trace_route['path'])):
				if trace_route['path'][x] == trace_route['path'][y]:
					if print_debug is True:
						self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_route: poisened path" )
						self.P.write_debug( str( trace_route['path'] ) )

					return

		trace_route_id = self.SESTRT.get_trace_route_id( source_IP = trace_route['source_IP'], dest_IP = trace_route['dest_IP'], path = trace_route['path'], epoch_time = trace_route['epoch_time'] )
		
		if trace_route_id not in self.trace_routes:
			for x in range( 0, len(trace_route['path'] ) ):
				trace_route['path'][x] = int( trace_route['path'][x] )

			self.trace_routes[trace_route_id] = trace_route

			path = trace_route['path']

			for x in range( 0, len(path) -1 ):
				from_AS = path[x]
				to_AS = path[x+1]

				if from_AS == to_AS:
					continue

				_id = str(from_AS) + "_" + str(to_AS)

				if str(_id) not in self.trace_routes_search:
					self.trace_routes_search[ str(_id) ] = list()

				self.trace_routes_search[ str(_id) ].append( trace_route_id )

				_id = str(to_AS) + "_" + str(from_AS)

				if str(_id) not in self.trace_routes_search:
					self.trace_routes_search[ str(_id) ] = list()

				self.trace_routes_search[ str(_id) ].append( trace_route_id )

			if print_debug is True:
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_route: trace_route_id = " + str(trace_route_id) + ": added" )
				self.P.write_JSON( trace_route )
		else:
			if print_debug is True:
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_route: trace_route_id = " + str(trace_route_id) + ": already added" )
				self.P.write_JSON( trace_route )

	def add_improver_trace_routes( self, trace_routes = None, print_debug = False ):
		if trace_routes is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_routes: trace_routes is None" )
			return None 

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: add_improver_trace_routes: start" )

		for trace_route in trace_routes:
			self.add_improver_trace_route( trace_route = trace_route )

	def compute_missing_relations( self, mode = None, file_name = None, print_debug = False, print_server_response = False ):
		self.P.write( "Simulator_Relation_Type_Improver_Tool: compute_missing_relations: has " + str(len(self.relations)) + " relations and " + str(len(self.trace_routes)) + " trace routes: start", color = 'green' )

		if mode is not None and "local" in mode:
			pass
		elif mode is not None and "ES" in mode:
			pass
		elif mode is not None and "CSV" in mode:
			pass
		elif mode is not None and "csv" in mode:
			pass
		else:
			if mode is not None:
				self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: compute_missing_relations: mode = " + str(mode) + ", expects: local, ES or CSV" )

			self.P.write( "Simulator_Relation_Type_Improver_Tool: compute_missing_relations: has multiple modes:", color = 'green' ) 
			self.P.write( "\t(1) - use local trace routes" ) 
			self.P.write( "\t(2) - use ES trace routes" ) 
			self.P.write( "\t(3) - use CSV trace routes" ) 
			mode = self.AT.ask( question = "Select mode (1/2/3):", expect_list = [ 1, 2, 3 ] )

			if "1" in mode:
				mode = "local"
			elif "2" in mode:
				mode = "ES"
			elif "3" in mode:
				mode = "CSV"

		self.missing_relations_processed_cache = dict()

		if "local" in mode:
			missing_relations = self.__compute_missing_relations_local( print_debug = print_debug, print_server_response = print_server_response )
		elif "ES" in mode:
			missing_relations = self.__compute_missing_relations_ES( print_debug = print_debug, print_server_response = print_server_response )
		elif "CSV" in mode or "csv" in mode:
			missing_relations = self.__compute_missing_relations_CSV( file_name = file_name, print_debug = print_debug, print_server_response = print_server_response )
		elif mode is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: compute_missing_relations: mode is None") 

		#self.P.write( "Simulator_Relation_Type_Improver_Tool: compute_missing_relations: found " + str(len(missing_relations)) + " missing relations" )
		return missing_relations

	def __compute_missing_relation( self, path = None, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relation: start" )

		missing_relations = list()

		if str(path) in self.missing_relations_processed_cache:
			if print_debug is True:
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relation: path = " + str(path) + " already processed" )

			return missing_relations

		self.missing_relations_processed_cache[ str(path) ] = None

		for x in range( 0, len(path) - 1 ):
			from_AS = path[x]
			to_AS = path[x+1]

			if from_AS == to_AS:
				continue

			relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS ) 

			if relation_id in self.missing_relations_processed_cache:
				if print_debug is True:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relation: relation_id = " + str(relation_id) + ", from_AS = " + str(from_AS) + ", to_AS = " + str(to_AS) +": already processed" )

				continue

			if relation_id not in self.relations:
				relation = self.SESRT_2.create_relation( from_AS = from_AS, to_AS = to_AS, source = "missing" )
				relation_id = self.SESRT_2.get_relation_id( relation = relation )

				if relation_id not in self.missing_relations_processed_cache:
					self.missing_relations_processed_cache[ relation_id ] = None
					missing_relations.append( relation )

				if print_debug is True:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relation: relation_id = " + str(relation_id) + ": added" )
					self.P.write_JSON( relation )
			else:
				relation = self.relations[ relation_id ]
				if relation['type'] == -1:
					if relation_id not in self.missing_relations_processed_cache:
						self.missing_relations_processed_cache[ relation_id ] = None
						missing_relations.append( relation )

					if print_debug is True:
						self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relation: relation_id = " + str(relation_id) + ": added" )
						self.P.write_JSON( relation )

		return missing_relations

	def __compute_missing_relations_local( self, print_debug = False, print_server_response = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relations_local: start" )

		counter = len( self.trace_routes )

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relations_local: processing " + str(counter) + " trace_routes" )

		missing_relations = list()

		for trace_route_id in self.trace_routes:
			counter -= 1
			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_missing_relations_local: " + str(counter/1000) + "k trace routes left to process, found " + str(len(missing_relations)) + " missing relations ")

			path = self.trace_routes[trace_route_id]['path']
			found_missing_relations = self.__compute_missing_relation( path = path, print_debug = print_debug )
			missing_relations.extend( found_missing_relations )

		return missing_relations

	def __compute_missing_relations_ES( self, print_debug = False, print_server_response = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relations_ES: start" )

		missing_relations = list()
		size = 100000

		data_JSON = dict()
		data_JSON['size'] = size
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		data_ES = self.ESI.search( index = self.TRACE_ROUTES, data_JSON = data_JSON, scroll = "1m", source_filtering = ["path"], print_server_response = print_server_response )
		scroll_id = data_ES['_scroll_id']
		
		counter = len( data_ES['hits']['hits'] )
		for data in data_ES['hits']['hits']:
			counter -= 1
			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_missing_relations_ES: " + str(counter/1000) + "k trace routes left to process                                            " )

			trace_route = data['_source']
			found_missing_relations = self.__compute_missing_relation( path = trace_route['path'], print_debug = print_debug )
			missing_relations.extend( found_missing_relations )

		amount_left = data_ES['hits']['total'] - size

		finished = False
		while finished is False:
			if amount_left < 0:
				amount_left = 0

			self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_missing_relations_ES: " + str(int(amount_left/1000)) + "k trace routes left, found " + str(len(missing_relations)) + " missing relations ")
			
			data_ES = self.ESI.scroll( index = self.TRACE_ROUTES, scroll = "1m", scroll_id = scroll_id, print_server_response = print_server_response )
			
			if len( data_ES['hits']['hits'] ) == 0:
				finished = True

			counter = len( data_ES['hits']['hits'] )
			for data in data_ES['hits']['hits']:
				counter -= 1
				if counter % 1000 == 0:
					self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_missing_relations_ES: " + str(counter/1000) + "k trace routes left to process                                            " )

				trace_route = data['_source']
				found_missing_relations = self.__compute_missing_relation( path = trace_route['path'], print_debug = print_debug )
				missing_relations.extend( found_missing_relations )

			amount_left -= size

		self.P.write( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relations_ES: done!" )

		return missing_relations

	def __compute_missing_relations_CSV( self, file_name = None, print_debug = False, print_server_response = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relations_CSV: start" )

		if file_name is None:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __compute_missing_relations_CSV: CSV_file_name is None" )
			self.P.write( "Simulator_Relation_Type_Improver_Tool: place CSV file in " + self.FT.get_base_path() )
			self.P.write( "Simulator_Relation_Type_Improver_Tool: enter file name including extension" )

			file_name = self.AT.ask( question = "File Name: " )

		rows = self.FT.load_CSV_file( file_name = file_name, print_status = True )

		if rows is None:
			return list()

		missing_relations = list()
		counter = 0
		for row in rows:
			counter += 1

			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_missing_relations_CSV: " + str(counter/1000) + "k trace routes processed, found " + str(len(missing_relations)/1000) + "k missing relations" )

			if counter > 500000:
				return missing_relations

			length = len(row)

			if str(row).count('[') != str(row).count(']'):
				#self.P.write_error( "Simulator_ES_trace_Routes_Tool: load_ES_trace_routes_from_CSV: count('[') != count(']'), data:" )
				#self.P.write_error( str(row) )
				continue

			path = list()
			AS_number = int( row[1].replace("[","").replace("]","") )
			path.append( AS_number)

			for x in range( 2, length - 1 ):
				path.append( int( row[x] ) )

			if length > 2:
				AS_number = int( row[length-1].replace("]","") )
				path.append( AS_number )

			epoch_time = row[0]
			path = list(OrderedDict.fromkeys(path))
			found_missing_relations = self.__compute_missing_relation( path = path, print_debug = print_debug )
			missing_relations.extend( found_missing_relations )

		return missing_relations

	def compute_wrong_relations( self, mode = None, file_name = None, print_debug = False, print_server_response = False, mark_not_p2p = True, extensive_mode = False ):
		self.P.write( "Simulator_Relation_Type_Improver_Tool: compute_wrong_relations: has " + str(len(self.relations)) + " relations and " + str(len(self.trace_routes)) + " trace routes: start", color = 'green' )

		if mode is not None and "local" in mode:
			pass
		elif mode is not None and "ES" in mode:
			pass
		elif mode is not None and "CSV" in mode:
			pass
		elif mode is not None and "csv" in mode:
			pass
		else:
			if mode is not None:
				self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: compute_wrong_relations: mode = " + str(mode) + ", expects: local, ES or CSV" )

			self.P.write( "Simulator_Relation_Type_Improver_Tool: compute_wrong_relations: has multiple modes:", color = 'green' ) 
			self.P.write( "\t(1) - use local trace routes" ) 
			self.P.write( "\t(2) - use ES trace routes" ) 
			self.P.write( "\t(3) - use CSV trace routes" ) 
			mode = self.AT.ask( question = "Select mode (1/2/3):", expect_list = [ 1, 2, 3 ] )

			if "1" in mode:
				mode = "local"
			elif "2" in mode:
				mode = "ES"
			elif "3" in mode:
				mode = "CSV"

		self.wrong_relations_processed_cache = dict()

		if "local" in mode:
			wrong_relations = self.__compute_wrong_relations_local( print_debug = print_debug, print_server_response = print_server_response, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode )
		elif "ES" in mode:
			wrong_relations = self.__compute_wrong_relations_ES( print_debug = print_debug, print_server_response = print_server_response, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode )
		elif "CSV" in mode or "csv" in mode:
			wrong_relations = self.__compute_wrong_relations_CSV( file_name = file_name, print_debug = print_debug, print_server_response = print_server_response, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode )
		elif mode is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: compute_wrong_relations: mode is None") 

		#self.P.write( "Simulator_Relation_Type_Improver_Tool: compute_wrong_relations: found " + str(len(wrong_relations)) + " wrong relations" )
		return wrong_relations

	def __compute_wrong_relations_local( self, print_debug = False, print_server_response = False, mark_not_p2p = True, extensive_mode = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations_local: start (mark_not_p2p = " + str(mark_not_p2p) + ", extensive_mode = " + str(extensive_mode) + ")" )

		counter = len( self.trace_routes )

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations_local: processing " + str(counter) + " trace_routes" )

		wrong_relations = dict()

		for trace_route_id in self.trace_routes:
			counter -= 1
			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_wrong_relations_local: " + str(counter/1000) + "k trace routes left to process, found " + str(len(wrong_relations)) + " wrong relations           ")

			path = self.trace_routes[trace_route_id]['path'][::-1]
			wrong_relations = self.__compute_wrong_relations( wrong_relations = wrong_relations, path = path, print_debug = print_debug, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode  )

		return wrong_relations

	def __compute_wrong_relations_ES( self, print_debug = False, print_server_response = False, mark_not_p2p = True, extensive_mode = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations_ES: start (mark_not_p2p = " + str(mark_not_p2p) + ", extensive_mode = " + str(extensive_mode) + ")"  )

		wrong_relations = dict()
		size = 100000

		data_JSON = dict()
		data_JSON['size'] = size
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		data_ES = self.ESI.search( index = self.TRACE_ROUTES, data_JSON = data_JSON, scroll = "1m", source_filtering = ["path"], print_server_response = print_server_response )
		scroll_id = data_ES['_scroll_id']
		
		counter = len( data_ES['hits']['hits'] )
		for data in data_ES['hits']['hits']:
			counter -= 1
			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_wrong_relations_ES: " + str(counter/1000) + "k trace routes left to process, found " + str(len(wrong_relations)) + " wrong relations     ")

			trace_route = data['_source']
			wrong_relations = self.__compute_wrong_relations( wrong_relations = wrong_relations, path = trace_route['path'][::-1], print_debug = print_debug, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode  )

		amount_left = data_ES['hits']['total'] - size

		finished = False
		while finished is False:
			if amount_left < 0:
				amount_left = 0

			self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_wrong_relations_ES: " + str(int(amount_left/1000)) + "k trace routes left, found " + str(len(wrong_relations)) + " wrong relations       ")
			data_ES = self.ESI.scroll( index = self.TRACE_ROUTES, scroll = "1m", scroll_id = scroll_id, print_server_response = print_server_response )
			
			if len( data_ES['hits']['hits'] ) == 0:
				finished = True

			counter = len( data_ES['hits']['hits'] )
			for data in data_ES['hits']['hits']:
				counter -= 1
				if counter % 1000 == 0:
					self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_wrong_relations_ES: " + str(counter/1000) + "k trace routes left to process                                            " )

				trace_route = data['_source']
				wrong_relations = self.__compute_wrong_relations( wrong_relations = wrong_relations, path = trace_route['path'][::-1], print_debug = print_debug, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode  )

			amount_left -= size

		self.P.write( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations_ES: done!" )

		return wrong_relations

	def __compute_wrong_relations_CSV( self, file_name = None, print_debug = False, print_server_response = False, mark_not_p2p = True, extensive_mode = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations_CSV: start (mark_not_p2p = " + str(mark_not_p2p) + ", extensive_mode = " + str(extensive_mode) + ")" )

		if file_name is None:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations_CSV: CSV_file_name is None" )
			self.P.write( "Simulator_Relation_Type_Improver_Tool: place CSV file in  " + self.FT.get_base_path() )
			self.P.write( "Simulator_Relation_Type_Improver_Tool: enter file name including extension" )

			file_name = self.AT.ask( question = "File Name: " )

		rows = self.FT.load_CSV_file( file_name = file_name, print_status = True )

		if rows is None:
			return list()

		wrong_relations = dict()
		counter = 0
		for row in rows:
			counter += 1

			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: __compute_wrong_relations_CSV: " + str(counter/1000) + "k trace routes processed, found " + str(len(wrong_relations)) + " wrong relations" )

			#if counter > 500000:
			#	return wrong_relations

			length = len(row)

			if str(row).count('[') != str(row).count(']'):
				#self.P.write_error( "Simulator_ES_trace_Routes_Tool: load_ES_trace_routes_from_CSV: count('[') != count(']'), data:" )
				#self.P.write_error( str(row) )
				continue

			path = list()
			AS_number = int( row[1].replace("[","").replace("]","") )
			path.append( AS_number)

			for x in range( 2, length - 1 ):
				path.append( int( row[x] ) )

			if length > 2:
				AS_number = int( row[length-1].replace("]","") )
				path.append( AS_number )

			epoch_time = row[0]
			path = list(OrderedDict.fromkeys(path))
			wrong_relations = self.__compute_wrong_relations( wrong_relations = wrong_relations, path = path, print_debug = print_debug, extensive_mode = extensive_mode )

		return wrong_relations

	def __compute_wrong_relations( self, wrong_relations = None, path = None, print_debug = False, mark_not_p2p = True, extensive_mode = False  ):
		if str(path) in self.wrong_relations_processed_cache:
			if print_debug is True:
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations: path = " + str(path) + " already processed" )

			return wrong_relations

		if extensive_mode is False:
			self.wrong_relations_processed_cache[ str(path) ] = None

		types = self.__get_types( path = path )

		length = len(types)
		status = [True] * length
		types_str = self.SLT.get_types_str( types = types )
		printed_path = False

		if print_debug is True:
			old_status = copy.copy( status )

		index_C2P = -1
		for x in range( 0, length ):
			if types[x] == self.TYPE_C2P and status[x] is True:
				index_C2P = x
				break

		# P2P before C2P
		found_errors = False
		if index_C2P != -1:
			for x in range( 0, index_C2P ):
				if types[x] == self.TYPE_P2P and status[x] is True:
					status[x] = False
					found_errors = True

					if mark_not_p2p is True:
						relation_id_A = self.SESRT_2.get_relation_id( from_AS = path[x], to_AS = path[x+1] )
						relation_id_B = self.SESRT_2.get_relation_id( from_AS = path[x+1], to_AS = path[x] )
						self.not_p2p_relations[ relation_id_A ] = None
						self.not_p2p_relations[ relation_id_B ] = None

		if found_errors is True:
			if print_debug is True:
				if printed_path is False:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str( path ) + " = " + str( types_str ) )
					printed_path = True

				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: found P2P before C2P")
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str(old_status) + " -> " + str(status) )

		if print_debug is True:
			old_status = copy.copy( status )

		# P2P after P2C
		found_errors = False
		found_P2C = False
		for x in range( 0, length ):
			if types[x] == self.TYPE_P2C and status[x] is True:
				found_P2C = True

			if types[x] == self.TYPE_P2P and found_P2C is True and status[x] is True:
				status[x] = False
				found_errors = True

				if mark_not_p2p is True:
					relation_id_A = self.SESRT_2.get_relation_id( from_AS = path[x], to_AS = path[x+1] )
					relation_id_B = self.SESRT_2.get_relation_id( from_AS = path[x+1], to_AS = path[x] )
					self.not_p2p_relations[ relation_id_A ] = None
					self.not_p2p_relations[ relation_id_B ] = None

		if found_errors is True:
			if print_debug is True:
				if printed_path is False:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str( path ) + " = " + str( types_str ) )
					printed_path = True

				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: found P2P after P2C")
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str(old_status) + " -> " + str(status) )

		if print_debug is True:
			old_status = copy.copy( status )

		# Multiple P2P
		if types.count( self.TYPE_P2P ) >= 2:
			if print_debug is True:
				if printed_path is False:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations: " + str( path ) + " = " + str( types_str ) )
					printed_path = True

				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations: found multiple P2P")

			if print_debug is True:
				old_status = copy.copy( status )
			
			for x in range( 0, length ):
				if types[x] == self.TYPE_P2P:
					status[x] = False

					if mark_not_p2p is True:
						relation_id_A = self.SESRT_2.get_relation_id( from_AS = path[x], to_AS = path[x+1] )
						relation_id_B = self.SESRT_2.get_relation_id( from_AS = path[x+1], to_AS = path[x] )
						self.not_p2p_relations[ relation_id_A ] = None
						self.not_p2p_relations[ relation_id_B ] = None

					break

			if print_debug is True:
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __compute_wrong_relations: " + str(old_status) + " -> " + str(status) )

		if print_debug is True:
			old_status = copy.copy( status )

		# C2P after P2C
		found_errors = False
		found_P2C = False
		for x in range( 0, length ):
			if types[x] == self.TYPE_P2C and status[x] is True:
				found_P2C = True

			if types[x] == self.TYPE_C2P and found_P2C is True and status[x] is True:
				status[x] = False
				found_errors = True

		if found_errors is True:
			if print_debug is True:
				if printed_path is False:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str( path ) + " = " + str( types_str ) )
					printed_path = True

				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: found C2P after P2C")
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str(old_status) + " -> " + str(status) )

		if print_debug is True:
			old_status = copy.copy( status )

		# C2P after P2P
		found_errors = False
		index_P2P = -1
		for x in range( 0, length ):
			if types[x] == self.TYPE_P2P and status[x] is True:
				index_P2P = x

			if types[x] == self.TYPE_C2P and index_P2P != -1 and status[x] is True:
				status[x] = False
				found_errors = True

		if found_errors is True:
			if print_debug is True:
				if printed_path is False:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str( path ) + " = " + str( types_str ) )
					printed_path = True

				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: found C2P after P2P")
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str(old_status) + " -> " + str(status) )

		if print_debug is True:
			old_status = copy.copy( status )

		# P2C before C2P
		index_C2P = -1
		for x in range( 0, length ):
			if types[x] == self.TYPE_C2P and status[x] is True:
				index_C2P = x
				break

		found_errors = False
		if index_C2P != -1:
			for x in range( 0, index_C2P ):
				if types[x] == self.TYPE_P2C and status[x] is True:
					status[x] = False
					found_errors = True

		if found_errors is True:
			if print_debug is True:
				if printed_path is False:
					self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str( path ) + " = " + str( types_str ) )
					printed_path = True

				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: found P2C before C2P")
				self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: " + str(old_status) + " -> " + str(status) )

		if extensive_mode is True:
			for x in range( 0, len(path) - 1 ):
				from_AS = path[x]
				to_AS = path[x+1]

				relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS )
				reversed_relation_id = self.SESRT_2.get_relation_id( from_AS = to_AS, to_AS = from_AS )

				if relation_id in self.relations:
					#print status
					#print self.SLT.get_types_str( types = types )
					#print path

					if relation_id not in wrong_relations:
						wrong_relations[ relation_id ] = copy.deepcopy( self.relations[ relation_id ] )
						wrong_relations[ relation_id ]['good_counter'] = 0
						wrong_relations[ relation_id ]['bad_counter'] = 0

					if reversed_relation_id not in wrong_relations:
						wrong_relations[ reversed_relation_id ] = copy.deepcopy( self.relations[ reversed_relation_id ] )
						wrong_relations[ reversed_relation_id ]['good_counter'] = 0
						wrong_relations[ reversed_relation_id ]['bad_counter'] = 0

					if status[x] is False:
						wrong_relations[ relation_id ]['bad_counter'] += 1
						wrong_relations[ reversed_relation_id ]['bad_counter'] += 1
					else:
						wrong_relations[ relation_id ]['good_counter'] += 1
						wrong_relations[ reversed_relation_id ]['good_counter'] += 1

		elif extensive_mode is False:
			for x in range( 0, length ):
				if status[x] is False:
					from_AS = path[x]
					to_AS = path[x+1]

					if print_debug is True:
						self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __examine_types: adding wrong relation " + str(from_AS) + " -> " + str(to_AS) )

					relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS )

					if relation_id not in self.wrong_relations_processed_cache:
						self.wrong_relations_processed_cache[ relation_id ] = None

						wrong_relations[ relation_id ] = copy.deepcopy( self.relations[ relation_id ] )

		return wrong_relations

	def __get_types( self, path = None ):
		types = list()

		for x in range( 0, len(path) - 1 ):
			temp_from_AS = path[x]
			temp_to_AS = path[x+1]

			temo_relation_id = self.SESRT_2.get_relation_id( from_AS = temp_from_AS, to_AS = temp_to_AS )

			if temo_relation_id in self.relations:
				type = self.relations[temo_relation_id]['type']
				types.append( type ) 
			else:
				types.append( -1 )

		return types

	def infer_relation( self, relation = None, print_debug = False, print_server_response = False, use_ES = True, no_output = False ):
		if relation is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: infer_relation: relation is None" )
			return [ None, None ]

		from_AS = relation['from_AS']
		to_AS = relation['to_AS']
		relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS )

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: infer_relation: from_AS = " + str(from_AS) + ", to_AS = " + str(to_AS) + ": start" )
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: infer_relation: filtering trace routes that have from_AS and to_AS as a direct pair" )

		if use_ES is True:
			self.__get_ES_trace_routes_sections( from_AS = from_AS, to_AS = to_AS, print_server_response = print_server_response )

		useful_trace_route_ids = list()

		_id = str(from_AS) + "_" + str(to_AS)
		if str(_id) in self.trace_routes_search:
			useful_trace_route_ids.extend( self.trace_routes_search[ str(_id) ] )

		_id = str(to_AS) + "_" + str(from_AS)
		if str(_id) in self.trace_routes_search:
			useful_trace_route_ids.extend( self.trace_routes_search[ str(_id) ] )

		useful_trace_route_ids = list(set(useful_trace_route_ids))

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: infer_relation: found " + str(len(useful_trace_route_ids)) + " trace routes" )

		not_p2p = False	
		result = dict()
		result['p2c'] = list()
		result['c2p'] = list()
		result['p2p'] = list()
		result['s2s'] = list()

		for trace_route_id in useful_trace_route_ids:	
			[ type, local_not_p2p ] = self.__infer_type( trace_route_id = trace_route_id, from_AS = from_AS, to_AS = to_AS )

			if local_not_p2p is True:
				not_p2p = True
			
			if not_p2p is True:
				result['p2p'] = list()
				local_not_p2p = True

			if type == -1:
				if print_debug is True:
					path = self.trace_routes[ trace_route_id ]['path'][::-1]
					types = self.__get_types( path = path )

					self.P.write_debug()
					self.P.write_debug( str(from_AS) + " -> " + str(to_AS) ) 
					self.P.write_debug( "path = " + str( path ) ) 
					self.P.write_debug( "types = " + str( self.SLT.get_types_str( types = types ) ) ) 
					self.P.write_debug( "predicted type = " + self.SLT.get_type_str( type = type ) ) 
					self.P.write_debug( "not_p2p = " + str(local_not_p2p) ) 
				continue
			elif type == self.TYPE_P2C:
				result['p2c'].append( trace_route_id )
			elif type == self.TYPE_C2P:
				result['c2p'].append( trace_route_id )
			elif type == self.TYPE_P2P and not_p2p is False:
				result['p2p'].append( trace_route_id )
			elif type == self.TYPE_S2S:
				result['s2s'].append( trace_route_id )

			if print_debug is True:
				path = self.trace_routes[ trace_route_id ]['path'][::-1]
				types = self.__get_types( path = path )

				self.P.write_debug()
				self.P.write_debug( str(from_AS) + " -> " + str(to_AS) ) 
				self.P.write_debug( "path = " + str( path ) ) 
				self.P.write_debug( "types = " + str( self.SLT.get_types_str( types = types ) ) ) 
				self.P.write_debug( "predicted type = " + self.SLT.get_type_str( type = type ) ) 
				self.P.write_debug( "not_p2p = " + str(local_not_p2p) ) 
			
		result['not_p2p'] = not_p2p
		relation = self.__process_predicted_result( result = result, from_AS = from_AS, to_AS = to_AS, print_debug = print_debug )

		if relation['type'] == -1:
			if no_output is False:
				self.P.write( "Simulator_Relation_Type_Improver_Tool: infer_relation: from_AS = " + str(from_AS) + ", to_AS = " + str(to_AS) + ": not inferred" , color = 'yellow' )
			return [ None, None ]	
		else:
			if no_output is False:
				self.P.write( "Simulator_Relation_Type_Improver_Tool: infer_relation: from_AS = " + str(from_AS) + ", to_AS = " + str(to_AS) + ": inferred as " +  self.SLT.get_type_str( type = relation['type'] ) )

			#self.add_improver_relation( relation = relation )	

			type = relation['type']
			if type == self.TYPE_P2C:
				reversed_type = self.TYPE_C2P
			elif type == self.TYPE_C2P:
				reversed_type = self.TYPE_P2C
			elif type == self.TYPE_P2P:
				reversed_type = self.TYPE_P2P
			elif type == self.TYPE_S2S:
				reversed_type = self.TYPE_S2S

			reversed_relation = copy.deepcopy( relation )
			reversed_relation['type'] = reversed_type
			reversed_relation['from_AS'] = copy.deepcopy( relation['to_AS'] )
			reversed_relation['to_AS'] = copy.deepcopy( relation['from_AS'] )
			reversed_relation['c2p'] = copy.deepcopy( relation['p2c'] )
			reversed_relation['p2c'] = copy.deepcopy( relation['c2p'] )

			return [ relation, reversed_relation ]	

	def __process_predicted_result( self, result = None, from_AS = None, to_AS = None, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __process_predicted_result: from_AS = " + str(from_AS) + ", to_AS = " + str(to_AS) + ", not_p2p = " + str(result['not_p2p']) )

		relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS )

		if relation_id in self.relations:
			relation = self.relations[relation_id]
		else:
			relation = self.SESRT_2.create_relation( from_AS = from_AS, to_AS = to_AS, type = -1, source = "predicted" )	

		largest_epoch_time = -1

		if result['not_p2p'] is False:
			for trace_route_id in result['p2p']:
				relation['trace_route_ids'].append( trace_route_id )

				if relation_id not in self.trace_routes[ trace_route_id ]['relation_ids']:
					self.trace_routes[ trace_route_id ]['relation_ids'].append( relation_id )

				trace_route = self.trace_routes[ trace_route_id ]
				epoch_time = trace_route['epoch_time']
		
				relation['p2p'].append( epoch_time )

		for trace_route_id in result['s2s']:
			relation['trace_route_ids'].append( trace_route_id )

			if relation_id not in self.trace_routes[ trace_route_id ]['relation_ids']:
				self.trace_routes[ trace_route_id ]['relation_ids'].append( relation_id )

			trace_route = self.trace_routes[ trace_route_id ]
			epoch_time = trace_route['epoch_time']

			relation['s2s'].append( epoch_time )

		for trace_route_id in result['p2c']:
			relation['trace_route_ids'].append( trace_route_id )

			if relation_id not in self.trace_routes[ trace_route_id ]['relation_ids']:
				self.trace_routes[ trace_route_id ]['relation_ids'].append( relation_id )

			trace_route = self.trace_routes[ trace_route_id ]
			epoch_time = trace_route['epoch_time']

			relation['p2c'].append( epoch_time )

		for trace_route_id in result['c2p']:
			relation['trace_route_ids'].append( trace_route_id )

			if relation_id not in self.trace_routes[ trace_route_id ]['relation_ids']:
				self.trace_routes[ trace_route_id ]['relation_ids'].append( relation_id )

			trace_route = self.trace_routes[ trace_route_id ]
			epoch_time = trace_route['epoch_time']

			relation['c2p'].append( epoch_time )

		relation['trace_route_ids'] = list( set( relation['trace_route_ids'] ) )
		relation['p2p'] = list( set( relation['p2p'] ) )
		relation['s2s'] = list( set( relation['s2s'] ) )
		relation['p2c'] = list( set( relation['p2c'] ) )
		relation['c2p'] = list( set( relation['c2p'] ) )
		relation['type'] == -1

		current_max = 0

		if len( relation['p2p'] ) > current_max and result['not_p2p'] is False:
			relation['type'] = self.TYPE_P2P
			current_max = len( relation['p2p'] )

		if len( relation['s2s'] ) > current_max:
			relation['type'] = self.TYPE_S2S
			current_max = len( relation['s2s'] )

		if len( relation['c2p'] ) > current_max:
			relation['type'] = self.TYPE_C2P
			current_max = len( relation['c2p'] )

		if len( relation['p2c'] ) > current_max:
			relation['type'] = self.TYPE_P2C
			current_max = len( relation['p2c'] )

		return relation

	def __infer_type( self, trace_route_id = None, from_AS = None, to_AS = None ):
		trace_route = self.trace_routes[ trace_route_id ]
		path = trace_route['path']
		types = self.__get_types( path = path )
		length = len(types)
		type = -1
		not_p2p = False

		relation_id = self.SESRT_2.get_relation_id( from_AS = from_AS, to_AS = to_AS )
		if relation_id in self.not_p2p_relations:
			not_p2p = True

		if self.TYPE_P2P in types:
			not_p2p = True

		try:
			index = list()
			index.append( path.index( int(from_AS ) ) )
			index.append( path.index( int(to_AS) )  )
		except( ValueError ):
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: __infer_type: ValueError, from_AS = " + str(from_AS) + ", to_AS = " + str(to_AS) + ", path = " + str(path) )
			return -1

		if index[1] - index[0] == 1:
			reversed = False
			index = index[0]
		elif index[0] - index[1] == 1:
			reversed = True
			index = index[1]
		else:
			print from_AS
			print to_AS
			print path
			print types
			print index
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: __infer_type: index[0] - index[1] != 1 and index[1] - index[0] != 1" )
			return -1

		# ? -> S2S -> C2P |->| C2P 
		for x in range( index + 1, length ):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_C2P:
				type = self.TYPE_C2P
				not_p2p = True
				break
			else:
				break

		# ? -> S2S -> P2P |->| C2P 
		for x in range( index + 1, length ):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_P2P:
				type = self.TYPE_C2P
				not_p2p = True
				break
			else:
				break

		# C2P -> S2S -> ? -> S2S -> P2C |->| P2P (POSSIBILITY) 
		condition_1 = False
		condition_2 = False

		for x in range( index + 1, length ):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_P2C:
				condition_1 = True
				break
			else:
				break

		for x in range( index - 1, -1, -1):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_C2P:
				condition_2 = True
				break
			else:
				break

		if condition_1 is True and condition_2 is True:
			relation_id = self.SESRT_2.get_relation_id( from_AS = path[index], to_AS = path[index+1] )
			if relation_id in self.not_p2p_relations or not_p2p is True:
				if random.uniform(0, 1) < 0.5: 
					type = self.TYPE_P2C
				else:
					type = self.TYPE_C2P
			else:
				type = self.TYPE_P2P
			
		# ? -> S2S -> P2C |->| P2P OR P2C (POSSIBILITY) 
		for x in range( index + 1, length ):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_P2C:
				relation_id = self.SESRT_2.get_relation_id( from_AS = path[x], to_AS = path[x+1] )
				if relation_id in self.not_p2p_relations or not_p2p is True:
					if random.uniform(0, 1) < 0.5: 
						type = self.TYPE_P2C
					else:
						type = self.TYPE_C2P
				else:
					type = self.TYPE_P2P
				break
			else:
				break

		# P2P -> S2S -> ? |->| P2C 
		for x in range( index - 1, -1, -1):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_P2P:
				type = self.TYPE_P2C
				not_p2p = True
				break
			else:
				break

		# P2C -> S2S -> ? |->| P2C 
		for x in range( index - 1, -1, -1):
			if types[x] == self.TYPE_S2S:
				continue
			elif types[x] == self.TYPE_P2C:
				type = self.TYPE_P2C
				not_p2p = True
				break
			else:
				break

		if reversed is True:
			if type == self.TYPE_P2C:
				type = self.TYPE_C2P	
			elif type == self.TYPE_C2P:
				type = self.TYPE_P2C		

		return [ type, not_p2p ]

	def __get_ES_trace_routes_sections( self, from_AS = None, to_AS = None, print_debug = False, print_server_response = False ):
		data_JSON = dict()
		data_JSON['size'] = 10000
		data_JSON['query'] = dict()
		data_JSON['query']['bool'] = dict()
		data_JSON['query']['bool']['must'] = list()

		data_JSON_2 = dict()
		data_JSON_2['match'] = dict()
		data_JSON_2['match']['path'] = from_AS
		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['match'] = dict()
		data_JSON_2['match']['path'] = to_AS
		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		#Retrieve Routes From ElasticSearch
		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __get_ES_trace_routes_sections: retrieving withdraws from ES index bgp-trace-routes" )
			self.P.write_JSON(data_JSON)

		filter_path = "hits.total, hits.hits._source,hits.hits._id"
		data_ES = self.ESI.search( index = self.TRACE_ROUTES, data_JSON = data_JSON, filter_path = filter_path, print_server_response = print_server_response )

		temp_trace_routes = dict()
		if 'hits' not in data_ES:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: __get_ES_trace_routes_sections: 'hits' not in data_ES" )
			return

		if 'hits' not in data_ES['hits']:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: 'hits' not in data_ES['hits']: no trace routes found " )
			return

		if print_debug is True:
			amount = len( data_ES['hits']['hits'] )
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: __get_ES_trace_routes_sections: found " + str(amount) + " trace routes")

		for hit in data_ES['hits']['hits']:
			self.add_improver_trace_route( trace_route = hit['_source'] )

	def infer_relations( self, relations = None, print_debug = False, print_server_response = False, use_ES = True, no_output = False ):
		if relations is None:
			self.P.write_error( "Simulator_Relation_Type_Improver_Tool: infer_relations: relations is None" )
			return None 

		if print_debug is True:
			self.P.write_debug( "Simulator_Relation_Type_Improver_Tool: infer_relations: start" )

		inferred_relations = dict()
		for relation in relations:
			self.infer_relation( relation = relation, print_debug = print_debug, use_ES = use_ES, no_output = no_output )

			relation_id = self.SESRT_2.get_relation_id( relation = relation )
			inferred_relations[ relation_id ] = relation

		return inferred_relations








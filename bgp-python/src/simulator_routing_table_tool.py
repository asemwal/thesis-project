import json, requests, os, sys, copy

from netaddr import *

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool

from simulator_link_types import Simulator_Link_Types

class Simulator_Routing_Table_Tool():
	P = None
	FT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	def __init__( self, P = None, FT = None, RSI = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Routing_Table_Tool: __init__ : P is None" )

		self.P.write( "Simulator_Routing_Table_Tool: Loading...", color = 'cyan' )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_Routing_Table_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Routing_Table_Tool" )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_Routing_Table_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

	def generate_routing_table( self, AS_graph = None, prefixes_do_not_overlap = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Routing_Table_Tool: generate_routing_table: AS_graph is None" )
			return None

		self.P.write()
		self.P.write( "Simulator_Routing_Table_Tool: generate_routing_table: start (prefixes_do_not_overlap = " + str(prefixes_do_not_overlap) + ")", color = 'green' )
		routing_table = dict()

		all_prefixes = dict()
		for AS_number in AS_graph:
			for route in AS_graph[ str(AS_number) ]['RIB']['routes']:
				all_prefixes[ str(route['prefix']) ]  = None

		counter = len(AS_graph)
		for AS_number in AS_graph:
			counter -= 1
			self.P.rewrite( "\tSimulator_Routing_Table_Tool: generate_routing_table: " + str(counter) + " ASes left to process          " )

			routes = dict() 
			for prefix in all_prefixes:
				routes[str(prefix)] = list()

			for route in AS_graph[ str(AS_number) ]['RIB']['routes']:
				prefix = route['prefix']		
				routes[str(prefix)].append( route )

			for prefix in routes:
				local_routes = routes[prefix]
				non_used_routes = list()

				if prefixes_do_not_overlap is False:
					network_A = IPNetwork( prefix )
					for local_prefix in routes:
						network_B = IPNetwork( local_prefix )
						if network_A in network_B and network_A != network_B:
							local_routes.extend( routes[local_prefix] )

				if len ( local_routes ) > 1:
					[ local_routes, non_used_routes ] = self.__get_highest_LOCAL_PREFERECE_routes( routes = local_routes, non_used_routes = non_used_routes )

				if len ( local_routes ) > 1:
					[ local_routes, non_used_routes ] = self.__get_smallest_prefix_length_routes( routes = local_routes, non_used_routes = non_used_routes )

				if len ( local_routes ) > 1:
					[ local_routes, non_used_routes ] = self.__get_smallest_path_length_routes( routes = local_routes, non_used_routes = non_used_routes )

				if str(AS_number) not in routing_table:
					routing_table[str(AS_number)] = dict()

				for x in range( 0, len( local_routes ) ):
					local_routes[x]['used'] = True

				for x in range( 0, len( non_used_routes ) ):
					non_used_routes[x]['used'] = False

				routing_table[str(AS_number)][str(prefix)] = list()
				routing_table[str(AS_number)][str(prefix)].extend( local_routes )
				routing_table[str(AS_number)][str(prefix)].extend( non_used_routes )

		#routing_table = self.__check_for_black_holes( AS_graph = AS_graph, routing_table = routing_table, prefix = prefix )
		routing_table = self.__generate_routing_table_statistics( routing_table = routing_table )
		return routing_table

	def __check_for_black_holes( self, AS_graph = None, routing_table = None, prefix = None ):
		for AS_number in routing_table:
			if "data" in AS_number and "statistics" in AS_number:
				continue

			if str(prefix) not in AS_graph[ str( AS_number) ]['BLACK_HOLE']:
				continue

			if len( AS_graph[ str( AS_number) ]['BLACK_HOLE'][ str(prefix) ] ) == 0:
				continue

			for black_hole_AS in AS_graph[ str( AS_number) ]['BLACK_HOLE'][ str(prefix) ]:
				used_routes_1 = list()
				used_routes_2 = list()

				for route in routing_table[ str(AS_number) ][ str(prefix) ]:
					if route['used'] is True:
						used_routes_1.append( route )

				for route in routing_table[ str(black_hole_AS) ][ str(prefix) ]:
					if route['used'] is True:
						used_routes_2.append( route )

				print black_hole_AS

		return routing_table

	def __generate_routing_table_statistics( self, routing_table = None ):
		routing_table['data'] = dict()

		for AS_number in routing_table:
			if "data" in AS_number:
				continue

			for prefix in routing_table[ str(AS_number) ]:
				if str(prefix) not in routing_table['data']:
					routing_table['data'][ str(prefix) ] = dict()

				source_ASes = list()

				for route in routing_table[ str(AS_number) ][ str(prefix) ]:
					if route['used'] is True:
						source_AS = str( route['source_AS'] )

						if source_AS not in source_ASes:
							source_ASes.append( source_AS )

				name = ""
				source_ASes = list( sorted( source_ASes ) )
				for source_AS in source_ASes:
					name = str(name) + " + AS" + str(source_AS)

				name = name[3:]

				if len(name) == 0:
					name = "NO_ROUTING"

				if name not in routing_table['data'][ str(prefix) ]:
					routing_table['data'][ str(prefix) ][ name ] = list() 

				routing_table['data'][ str(prefix) ][ name ].append( str(AS_number) )

		routing_table['statistics'] = dict()

		for prefix in routing_table['data']:
			routing_table['statistics'][ prefix ] = dict()
			for name in routing_table['data'][ str(prefix) ]:
				routing_table['statistics'][ str(prefix) ][name] = str( len( routing_table['data'][ str(prefix) ][name]) )

		return routing_table

	def __get_highest_LOCAL_PREFERECE_routes( self, routes = None, non_used_routes = None ):
		filtered_routes = list()

		highest_LOCAL_PREFERENCE = 0
		for route in routes:
			if route['LOCAL_PREFERENCE'] > highest_LOCAL_PREFERENCE:
				highest_LOCAL_PREFERENCE = route['LOCAL_PREFERENCE']

		for route in routes:
			if route['LOCAL_PREFERENCE'] == highest_LOCAL_PREFERENCE:
				filtered_routes.append( copy.deepcopy( route ) )
			else:
				non_used_routes.append( copy.deepcopy( route ) )

		return [ filtered_routes, non_used_routes ]

	def __get_smallest_prefix_length_routes( self, routes = None, non_used_routes = None ):
		filtered_routes = list()

		smallest_prefix_length = 0
		for route in routes:
			if route['prefix_length'] > smallest_prefix_length:
				smallest_prefix_length = route['prefix_length']

		for route in routes:	
			if route['prefix_length'] == smallest_prefix_length:
				filtered_routes.append( copy.deepcopy( route ) )
			else:
				non_used_routes.append( copy.deepcopy( route ) )

		return [ filtered_routes, non_used_routes ]

	def __get_smallest_path_length_routes( self, routes = None, non_used_routes = None ):
		filtered_routes = list()

		smallest_path_length = 99
		for route in routes:
			if len( route['path'] ) + route['extra_path_length'] < smallest_path_length:
				smallest_path_length = len( route['path'] ) + route['extra_path_length']
				
		for route in routes:
			if len( route['path'] ) + route['extra_path_length'] == smallest_path_length:
				filtered_routes.append( copy.deepcopy( route ) )
			else:
				non_used_routes.append( copy.deepcopy( route ) )

		return [ filtered_routes, non_used_routes ]

	def save_routing_table( self, relative_folder_path = "", file_name = None, routing_table = None, print_status = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Routing_Table_Tool: save_routing_table: file_name is None" )
			return None

		if routing_table is None:
			self.P.write_error( "Simulator_Routing_Table_Tool: save_routing_table: routing_table is None" )
			return None

		file_name = file_name.split(".")[0] + ".routing_table"

		self.FT.save_JSON_file( relative_folder_path = relative_folder_path, file_name = file_name, data_JSON = routing_table, print_status = print_status )

	def load_routing_table( self, relative_folder_path = "", file_name = None, print_status = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Routing_Table_Tool: load_routing_table: file_name is None" )
			return None

		file_name = file_name.split(".")[0] + ".routing_table"

		return self.FT.load_JSON_file( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )

	def write_routing_table_statistics( self, routing_table = None ):
		if routing_table is None:
			self.P.write_error( "Simulator_Routing_Table_Tool: write_routing_table_statistics: routing_table is None" )
			return None

		self.P.write( "Simulator_Routing_Table_Tool: write_routing_table_statistics ", color = 'green' )
		for prefix in routing_table['statistics']:
			self.P.write( str(prefix) )
			self.P.write_JSON( routing_table['statistics'][str(prefix)] )



	




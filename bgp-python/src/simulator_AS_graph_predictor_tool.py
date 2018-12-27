import json, requests, os, sys, hashlib, copy, time

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from AS_rank_interface import AS_Rank_Interface

from simulator_link_types import Simulator_Link_Types
from simulator_AS_graph_tool import Simulator_AS_Graph_Tool

class Simulator_AS_Graph_Predictor_Tool():
	P = None
	ASRI = None

	SLT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	def __init__( self, P = None, ASRI = None, SASGT = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_AS_Graph_Predictor_Tool: __init__ : P is None" )

		self.P.write( "Simulator_AS_Graph_Predictor_Tool: Loading...", color = 'cyan' )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_AS_Graph_Predictor_Tool: __init__ : ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if SASGT is not None:
			self.SASGT = SASGT
		else:
			self.P.write_warning( "Simulator_AS_Graph_Predictor_Tool: __init__ : SASGT is None" )
			self.SASGT = Simulator_AS_Graph_Tool( P = self.P, ASRI = self.ASRI, TYPE_P2P = self.TYPE_P2P, TYPE_C2P = self.TYPE_C2P, TYPE_P2C = self.TYPE_P2C, TYPE_S2S = self.TYPE_S2S )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_AS_Graph_Predictor_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

	def __estimate_second_type( self, relations = None, first_type = None, third_type = None ):
		error = False
		warning = False
		second_type = -1

		if first_type == self.TYPE_C2P:
			if third_type == self.TYPE_C2P:
				second_type = self.TYPE_C2P
			elif third_type == self.TYPE_P2P:
				second_type = self.TYPE_C2P
			elif third_type == self.TYPE_P2C:
				second_type = self.TYPE_C2P
				warning = True 
			elif third_type == self.TYPE_S2S:
				return [ False, False, -1 ]

		elif first_type == self.TYPE_P2P:
			if third_type == self.TYPE_C2P:
				error = True
			elif third_type == self.TYPE_P2P:
				second_type = self.TYPE_S2S
				warning = True
			elif third_type == self.TYPE_P2C:
				second_type = self.TYPE_P2C
			elif third_type == self.TYPE_S2S:
				second_type = self.TYPE_S2S
				warning = True

		elif first_type == self.TYPE_P2C:
			if third_type == self.TYPE_C2P:
				error = True
			elif third_type == self.TYPE_P2P:
				error = True
			elif third_type == self.TYPE_P2C:
				second_type = self.TYPE_P2C
			elif third_type == self.TYPE_S2S:
				error = True 

		elif first_type == self.TYPE_S2S:
			if third_type == self.TYPE_C2P:
				second_type = self.TYPE_C2P
			elif third_type == self.TYPE_P2P:
				second_type = self.TYPE_C2P
			elif third_type == self.TYPE_P2C:
				if self.TYPE_P2P in relations:
					second_type = self.TYPE_C2P
				else:
					return [ False, False, -1 ]
			elif third_type == self.TYPE_S2S:
				if self.TYPE_P2P not in relations and self.TYPE_P2C not in relations:
					second_type = self.TYPE_C2P

		return [ error, warning, second_type ]

	def __add_link_to_AS_graph( self, AS_graph = None, from_AS = None, to_AS = None, type = None, database_tag = None ):
		if type == self.TYPE_C2P:
			AS_graph = self.SASGT.add_provider( AS_graph = AS_graph, AS_number = from_AS, provider = to_AS, database_tag = database_tag )
		elif type == self.TYPE_P2C:
			AS_graph = self.SASGT.add_customer( AS_graph = AS_graph, AS_number = from_AS, customer = to_AS, database_tag = database_tag )
		elif type == self.TYPE_P2P:
			AS_graph = self.SASGT.add_peer( AS_graph = AS_graph, AS_number = from_AS, peer = to_AS, database_tag = database_tag )
		elif type == self.TYPE_S2S:
			AS_graph = self.SASGT.add_sibling( AS_graph = AS_graph, AS_number = from_AS, sibling = to_AS, database_tag = database_tag )
		else:
			self.P.write_error( "Simulator_AS_Graph_Predictor_Tool: __add_link_to_AS_graph: type == -1" )

		return AS_graph

	def __error_action( self, AS_graph = None, stats = None, route = None ):
		stats[0] += 1
		relations_str = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )
		self.P.write_error( "\t" + str(relations_str) + " from path " + str( route['path'] ) )

		return [ AS_graph, stats ]

	def __warning_action( self, AS_graph = None, stats = None, route = None ):
		stats[1] += 1
		relations_str = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )
		self.P.write_warning( "\t" + str(relations_str) + " from path " + str( route['path'] ) )

		return [ AS_graph, stats ]

	def __adding_action( self, AS_graph = None, stats = None, route = None, from_index = None, to_index = None, type = None, database_tag = None ):
		relations_str_before = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )

		AS_graph = self.__add_link_to_AS_graph( AS_graph = AS_graph, from_AS = route['path'][from_index], to_AS = route['path'][to_index], type = type, database_tag = database_tag )
		stats[2] += 1
		relations_str = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )
		self.P.write( "\t[ADDING] " + str(relations_str_before) + " -> " + str(relations_str) + " from path " + str( route['path'] ), color = 'blue' )

		return [ AS_graph, stats ]

	def __complete_action( self, AS_graph = None, stats = None, route = None, print_debug = False ):
		stats[4] += 1

		#if print_debug is True:
		#	relations_str = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )
		#	self.P.write( "\t[COMPLETE] " + str(relations_str) + " from path " + str( route['path'] ), color = 'green' )

		return [ AS_graph, stats ]

	def __no_action( self, AS_graph = None, stats = None, route = None, print_debug = False ):
		stats[3] += 1
		relations_str = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )
		
		if print_debug is True:
			self.P.write( "\t[NO ACTION] " + str(relations_str) + " from path " + str( route['path'] ) )

		return [ AS_graph, stats ]

	def __auto_fill_level_1( self, AS_graph = None, stats = None, routes = None, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: __auto_fill_level_1 " )
		stats = [ 0, 0, 0, 0, 0 ]

		for route in routes:
			# find pattern
			relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )

			if -1 not in relations:
				[ AS_graph, stats ] = self.__complete_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )
				continue

			indexes = list()
			found = False
			for x in range( 0, len( relations ) - 2 ):
				if relations[x] != -1 and relations[x+1] == -1 and relations[x+2] != -1:
					found = True
					[ error, warning, type ] = self.__estimate_second_type( relations = relations, first_type = relations[x], third_type = relations[x+2] )
					relations_str = self.SLT.get_relations_str( AS_graph = AS_graph, route = route )

					if error is True:
						[ AS_graph, stats ] = self.__error_action( AS_graph = AS_graph, stats = stats, route = route )
					elif warning is True:
						[ AS_graph, stats ] = self.__warning_action( AS_graph = AS_graph, stats = stats, route = route )
						[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = type, database_tag = "P1-W" )
					elif type != -1:
						[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = type, database_tag = "P1" )
					else:
						found = False

			if found is False:
				[ AS_graph, stats ] = self.__no_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )

		self.P.write( "\t[CONFLICT, WARNING, ADDED, NO_ACTION, COMPLETE ] = " + str(stats), color = 'cyan' )

		return [ AS_graph, stats ]

	def __auto_fill_level_2( self, AS_graph = None, stats = None, routes = None, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: __auto_fill_level_2 " )
		stats = [ 0, 0, 0, 0, 0 ]

		for route in routes:
			relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )

			if -1 not in relations:
				[ AS_graph, stats ] = self.__complete_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )
				continue

			indexes = list()
			found = False
			for x in range( 0, len( relations ) - 1 ):
				if relations[x] == self.TYPE_P2C and relations[x+1] == -1:
					found = True
					[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = self.TYPE_P2C, database_tag = "P2" )
				elif relations[x] == self.TYPE_P2P and relations[x+1] == -1:
					found = True
					[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = self.TYPE_P2C, database_tag = "P2" )

			if found is False:
				[ AS_graph, stats ] = self.__no_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )

		self.P.write( "\t[CONFLICT, WARNING, ADDED, NO_ACTION, COMPLETE ] = " + str(stats), color = 'cyan' )

		return [ AS_graph, stats ]

	def __auto_fill_level_3( self, AS_graph = None, stats = None, routes = None, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: __auto_fill_level_3 " )
		stats = [ 0, 0, 0, 0, 0 ]

		for route in routes:
			relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )

			if -1 not in relations:
				[ AS_graph, stats ] = self.__complete_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )
				continue

			found = False
			if len( relations ) >= 2:
				for x in range( 0, len( relations ) - 1 ):
					if relations[x] == -1 and relations[x+1] == self.TYPE_P2P:
						found = True
						[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x, to_index = x+1, type = self.TYPE_C2P, database_tag = "P3" )
						relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )
					elif relations[x] == -1 and relations[x+1] == self.TYPE_C2P:
						found = True
						[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x, to_index = x+1, type = self.TYPE_C2P, database_tag = "P3" )
						relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )
					elif relations[x] == -1 and relations[x+1] == self.TYPE_P2C:
						found = True
						[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x, to_index = x+1, type = self.TYPE_P2C, database_tag = "P3" )
						relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )

			if found is False:
				[ AS_graph, stats ] = self.__no_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )

		self.P.write( "\t[CONFLICT, WARNING, ADDED, NO_ACTION, COMPLETE ] = " + str(stats), color = 'cyan' )

		return [ AS_graph, stats ]

	def __auto_fill_level_4( self, AS_graph = None, stats = None, routes = None, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: __auto_fill_level_4 " )
		stats = [ 0, 0, 0, 0, 0 ]

		for route in routes:
			relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )

			if -1 not in relations:
				[ AS_graph, stats ] = self.__complete_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )
				continue

			if len( relations ) == 1 and relations[0] == -1:
				number_of_customers_0 = len( self.ASRI.get_customers( route['path'][0] ) )
				number_of_customers_1 = len( self.ASRI.get_customers( route['path'][1] ) )

				if number_of_customers_0 == 0:
					number_of_customers_0 = 1

				if number_of_customers_1 == 0:
					number_of_customers_1 = 1

				if float( number_of_customers_0 ) / float( number_of_customers_1 ) >= 1.1:
					[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = 0, to_index = 1, type = self.TYPE_P2C, database_tag = "P4" )
				elif float( number_of_customers_1 ) / float( number_of_customers_0 ) >= 1.1:
					[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = 1, to_index = 0, type = self.TYPE_P2C, database_tag = "P4" )
				else:
					[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = 0, to_index = 1, type = self.TYPE_P2P, database_tag = "P4" )

			else:
				[ AS_graph, stats ] = self.__no_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )

		self.P.write( "\t[CONFLICTS, WARNING, ADDED, NO_ACTION, COMPLETE ] = " + str(stats), color = 'cyan' )

		return [ AS_graph, stats ]


	def __auto_fill_level_5( self, AS_graph = None, stats = None, routes = None, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: __auto_fill_level_5 " )
		stats = [ 0, 0, 0, 0, 0 ]

		for route in routes:
			relations = self.SLT.get_relations( AS_graph = AS_graph, route = route )

			if -1 not in relations:
				[ AS_graph, stats ] = self.__complete_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )
				continue

			if len( relations ) > 1:
				found = False
				for x in range( 0, len( relations ) -1 ):
					if relations[x] == self.TYPE_C2P and relations[x+1] == -1:
						from_AS = route['path'][x+1]
						next_AS = route['path'][x+2]

						number_of_customers_from_AS = len( self.ASRI.get_customers( AS_number = from_AS ) ) 
						number_of_customers_next_AS = len( self.ASRI.get_customers( AS_number = next_AS ) )

						if number_of_customers_from_AS > 0 and number_of_customers_next_AS == 0:
							[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = self.TYPE_P2C, database_tag = "P5" )
							found = True

						if number_of_customers_from_AS > number_of_customers_next_AS:
							[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = self.TYPE_P2C, database_tag = "P5" )
							found = True

						if number_of_customers_from_AS < number_of_customers_next_AS:
							[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = self.TYPE_C2P, database_tag = "P5" )
							found = True

						if number_of_customers_from_AS == number_of_customers_next_AS:
							[ AS_graph, stats ] = self.__adding_action( AS_graph = AS_graph, stats = stats, route = route, from_index = x+1, to_index = x+2, type = self.TYPE_P2P, database_tag = "P5" )
							found = True
				
				if found is False:
					[ AS_graph, stats ] = self.__no_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )
			else:
				[ AS_graph, stats ] = self.__no_action( AS_graph = AS_graph, stats = stats, route = route, print_debug = print_debug )

		self.P.write( "\t[CONFLICTS, WARNING, ADDED, NO_ACTION, COMPLETE ] = " + str(stats), color = 'cyan' )

		return [ AS_graph, stats ]


	def auto_fill( self, AS_graph = None, routes = None, print_debug = False ):
		for route in routes:
			route['succeeded'] = False

		run_counter = 0
		number_of_conficts_found = 0
		number_of_missing_links_found = 0
		number_of_missing_warnings_found = 0

		busy = True
		while busy is True:
			run_counter += 1

			hash_value = hashlib.sha256( str(AS_graph) ).hexdigest()	

			self.P.write()
			self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: run " + str(run_counter), color = 'green' )

			for x in range( 0, len(routes) ):
				routes[x]['path'] = list( OrderedDict.fromkeys( routes[x]['path'] ) )

			[ AS_graph, stats ] = self.__auto_fill_level_1( AS_graph = AS_graph, routes = routes, print_debug = print_debug )

			number_of_conficts_found += stats[0]
			number_of_missing_warnings_found += stats[1]
			number_of_missing_links_found += stats[2]
			

			[ AS_graph, stats ] = self.__auto_fill_level_2( AS_graph = AS_graph , routes = routes, print_debug = print_debug )

			number_of_conficts_found += stats[0]
			number_of_missing_warnings_found += stats[1]
			number_of_missing_links_found += stats[2]

			[ AS_graph, stats ] = self.__auto_fill_level_3( AS_graph = AS_graph , routes = routes, print_debug = print_debug )

			number_of_conficts_found += stats[0]
			number_of_missing_warnings_found += stats[1]
			number_of_missing_links_found += stats[2]

			[ AS_graph, stats ] = self.__auto_fill_level_4( AS_graph = AS_graph , routes = routes, print_debug = print_debug )

			number_of_conficts_found += stats[0]
			number_of_missing_warnings_found += stats[1]
			number_of_missing_links_found += stats[2]

			[ AS_graph, stats ] = self.__auto_fill_level_5( AS_graph = AS_graph , routes = routes, print_debug = print_debug )

			number_of_conficts_found += stats[0]
			number_of_missing_warnings_found += stats[1]
			number_of_missing_links_found += stats[2]

			if hashlib.sha256( str(AS_graph) ).hexdigest() == hash_value:
				busy = False

			self.P.write( "Simulator_AS_Graph_Predictor_Tool: auto_fill: done: " + str(number_of_conficts_found) + " conflicts found, " + str(number_of_missing_links_found) + " missing links added and " + str(number_of_missing_warnings_found) + " warning links added" )

		self.P.write()
		return AS_graph























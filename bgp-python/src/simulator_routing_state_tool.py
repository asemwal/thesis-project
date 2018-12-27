import json, requests, os, sys, copy, hashlib

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool
from ask_tool import Ask_Tool

from simulator_link_types import Simulator_Link_Types
from simulator_graph_draw_tool import Simulator_Graph_Draw_Tool

class Simulator_Routing_State_Tool():
	P = None
	FT = None
	AT = None

	SGDT = None
	SLT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	def __init__( self, P = None, FT = None, RSI = None, SGDT = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Routing_State_Tool: __init__ : P is None" )

		self.P.write( "Simulator_Routing_State_Tool: Loading...", color = 'cyan' )

		self.AT = Ask_Tool( P = self.P )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_Routing_State_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Routing_State_Tool" )

		if SGDT is not None:
			self.SGDT = SGDT
		else:
			self.P.write_warning( "Simulator_Routing_State_Tool: __init__ : SGDT is None" )
			self.SGDT = Simulator_Graph_Draw_Tool( P = self.P )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_Routing_State_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

	def __init_routing_state( self, routing_table = None ):
		self.P.write( "\tSimulator_Routing_State_Tool: __init_routing_state" )
		routing_state = dict()
		AS_numbers = dict()
		prefixes = dict()

		for AS_number in routing_table:
			if "data" in AS_number or "statistics" in AS_number:
				continue

			AS_numbers[ str( AS_number) ] = None

			for prefix in routing_table[ str(AS_number) ]:
				prefixes[ str( prefix) ] = None

		for prefix in prefixes:
			routing_state[ str(prefix) ] = dict()
			routing_state[ str(prefix) ]['data'] = dict()
			routing_state[ str(prefix) ]['data']['good_source_ASes'] = list()
			routing_state[ str(prefix) ]['data']['bad_source_ASes'] = list()
			routing_state[ str(prefix) ]['data']['good_ASes'] = list()
			routing_state[ str(prefix) ]['data']['bad_ASes'] = list()
			routing_state[ str(prefix) ]['data']['contested_ASes'] = list()
			routing_state[ str(prefix) ]['data']['no_routing_ASes'] = list()

			for AS_number in AS_numbers:
				routing_state[ str(prefix) ][ str(AS_number) ] = dict()
				routing_state[ str(prefix) ][ str(AS_number) ]['next_ASes'] = list()
				routing_state[ str(prefix) ][ str(AS_number) ]['from_ASes'] = list()
				routing_state[ str(prefix) ][ str(AS_number) ]['routed_to_good_source_AS'] = False
				routing_state[ str(prefix) ][ str(AS_number) ]['routed_to_bad_source_AS'] = False
				routing_state[ str(prefix) ][ str(AS_number) ]['good_source_ASes'] = list()
				routing_state[ str(prefix) ][ str(AS_number) ]['bad_source_ASes'] = list()
				routing_state[ str(prefix) ][ str(AS_number) ]['passing_ASes'] = list()
				routing_state[ str(prefix) ][ str(AS_number) ]['number_of_passing_ASes'] = 0
				routing_state[ str(prefix) ][ str(AS_number) ]['is_end_point'] = False

		return routing_state

	def generate_routing_state( self, routing_table = None, calculate_passing_ASes = True ):
		if routing_table is None:
			self.P.write_error( "Simulator_Routing_State_Tool: generate_routing_state: routing_table is None" )
			return None

		self.P.write()
		self.P.write( "Simulator_Routing_State_Tool: generate_routing_state" )

		routing_state = self.__init_routing_state( routing_table = routing_table )
		routing_state = self.__phase_1( routing_table = routing_table, routing_state = routing_state )
		
		run_counter = 0
		old_hashed_value = -1
		new_hashed_value = 0
		while old_hashed_value != new_hashed_value:
			old_hashed_value = new_hashed_value
			[ routing_state, new_hashed_value ] = self.__phase_2( routing_table = routing_table, routing_state = routing_state, run_counter = run_counter )
			run_counter += 1

		if calculate_passing_ASes is True and False:
			routing_state = self.__generate_passing_ASes( routing_table = routing_table, routing_state = routing_state )

		routing_state = self.__generate_statistics( routing_state = routing_state )

		return routing_state

	def __phase_1( self, routing_table = None, routing_state = None ):
		self.P.rewrite( force_new_line = True )

		counter = len( routing_table )
		for AS_number in routing_table:
			counter -= 1
			self.P.rewrite( "\tSimulator_Routing_State_Tool: generate_routing_state: stage 1: " + str(counter) + " ASes left to process          " )

			if "data" in AS_number or "statistics" in AS_number:
				continue

			for prefix in routing_table[ str(AS_number) ]: 
				for route in routing_table[ str(AS_number) ][ str(prefix) ]:
					if route['used'] is False:
						continue

					if len( route['path'] ) <= 1:

						if route['good'] is True:
							if str( route['source_AS'] ) not in routing_state[ str(prefix) ]['data']['good_source_ASes']:
								routing_state[ str(prefix) ]['data']['good_source_ASes'].append( str( route['source_AS'] ) )
								routing_state[ str(prefix) ][str(AS_number)]['good_source_ASes'].append( str( route['source_AS'] ) )
								routing_state[ str(prefix) ][str(AS_number)]['routed_to_good_source_AS'] = True
						elif route['good'] is False:
							if str( route['source_AS'] ) not in routing_state[ str(prefix) ]['data']['bad_source_ASes']:
								routing_state[ str(prefix) ]['data']['bad_source_ASes'].append( str( route['source_AS'] ) )
								routing_state[ str(prefix) ][str(AS_number)]['bad_source_ASes'].append( str( route['source_AS'] ) )
								routing_state[ str(prefix) ][str(AS_number)]['routed_to_bad_source_AS'] = True

						continue

					for x in range( 0, len( route['path'] ) - 1 ):
						from_AS = route['path'][x]
						to_AS = route['path'][x+1]

						if str(to_AS) not in routing_state[ str(prefix) ][ str(from_AS) ]['next_ASes']:
							routing_state[ str(prefix) ][ str(from_AS)] ['next_ASes'].append( str(to_AS) )

						if str(from_AS) not in routing_state[ str(prefix) ][ str(to_AS) ]['from_ASes']:
							routing_state[ str(prefix) ][ str(to_AS)] ['from_ASes'].append( str(from_AS) )

		return routing_state

	def __phase_2( self, routing_table = None, routing_state = None, run_counter = None ):
		self.P.rewrite( force_new_line = True )

		processed_links = dict()
		counter = len( routing_table )
		for AS_number in routing_table:
			counter -= 1
			self.P.rewrite( "\tSimulator_Routing_State_Tool: generate_routing_state: stage 2: " + str(counter) + " ASes left to process (run " +  str(run_counter)  + ")          " )

			if "data" in AS_number or "statistics" in AS_number:
				continue

			for prefix in routing_table[ str(AS_number) ]: 
				for route in routing_table[ str(AS_number) ][ str(prefix) ]:
					if route['used'] is False:
						continue

					if len( route['path'] ) == 1:
						continue

					previous_AS = str( route['path'][ len(route['path']) - 2 ] )

					bad_source_ASes	= copy.deepcopy( routing_state[ str(prefix) ][str(previous_AS)]['bad_source_ASes'] )
					good_source_ASes = copy.deepcopy( routing_state[ str(prefix) ][str(previous_AS)]['good_source_ASes'] )

					for bad_source_AS in bad_source_ASes:
						if bad_source_AS not in routing_state[ str(prefix) ][str(AS_number)]['bad_source_ASes']:
							routing_state[ str(prefix) ][str(AS_number)]['bad_source_ASes'].append( bad_source_AS )
							routing_state[ str(prefix) ][str(AS_number)]['routed_to_bad_source_AS'] = True

					for good_source_AS in good_source_ASes:
						if good_source_AS not in routing_state[ str(prefix) ][str(AS_number)]['good_source_ASes']:
							routing_state[ str(prefix) ][str(AS_number)]['good_source_ASes'].append( good_source_AS )
							routing_state[ str(prefix) ][str(AS_number)]['routed_to_good_source_AS'] = True					

		hashed_value = hashlib.md5( json.dumps( routing_state ) ).hexdigest()
		self.P.rewrite( "\tSimulator_Routing_State_Tool: generate_routing_state: stage 2: run " + str(run_counter) + ": hash: " + str(hashed_value) + "                   " )

		return [ routing_state, hashed_value ]

	def __generate_passing_ASes( self, routing_table = None, routing_state = None ):
		for prefix in routing_state: 
			end_point_ASes = list()
			for AS_number in routing_table:
				if "data" in AS_number:
					continue
				elif "statistics" in AS_number:
					continue

				if routing_state[ str(prefix) ][ str(AS_number) ]['is_end_point'] is True:
					end_point_ASes.append( str(AS_number) ) 

			for end_point_AS in end_point_ASes:
				routing_state = self.__mark_tree_passing_AS( routing_state = routing_state, prefix = prefix, AS_number = end_point_AS )

		for prefix in routing_state:
			for AS_number in routing_table:
				if "data" in AS_number:
					continue
				elif "statistics" in AS_number:
					continue

				passing_ASes = routing_state[ str(prefix) ][ str(AS_number) ]['passing_ASes']
				passing_ASes = list( set( passing_ASes ) )
				routing_state[ str(prefix) ][ str(AS_number) ]['passing_ASes'] = passing_ASes

				if str(AS_number) in passing_ASes:
					passing_ASes.remove( str(AS_number) )

				routing_state[ str(prefix) ][ str(AS_number) ]['number_of_passing_ASes'] = len( passing_ASes ) 

		return routing_state

	def __generate_statistics( self, routing_state = None ):
		for prefix in routing_state:
			for item in routing_state[ str(prefix) ]:
				try:
					AS_number = str( int( item ) )
					good = routing_state[ str(prefix) ][ str(AS_number) ]['routed_to_good_source_AS']
					bad = routing_state[ str(prefix) ][ str(AS_number) ]['routed_to_bad_source_AS']

					if good is True and bad is False:
						routing_state[ str(prefix) ]['data']['good_ASes'].append( AS_number )
					elif good is False and bad is True:
						routing_state[ str(prefix) ]['data']['bad_ASes'].append( AS_number )
					elif good is True and bad is True:	
						routing_state[ str(prefix) ]['data']['contested_ASes'].append( AS_number )
					elif good is False and bad is False:
						routing_state[ str(prefix) ]['data']['no_routing_ASes'].append( AS_number )	

				except( ValueError ):
					continue

			good_ASes = routing_state[ str(prefix) ]['data']['good_ASes'] 
			bad_ASes = routing_state[ str(prefix) ]['data']['bad_ASes'] 
			contested_ASes = routing_state[ str(prefix) ]['data']['contested_ASes'] 
			no_routing_ASes = routing_state[ str(prefix) ]['data']['no_routing_ASes'] 
			total = len( good_ASes ) + len( bad_ASes ) + len( contested_ASes ) + len( no_routing_ASes )

			perc_1 = round( float( len( good_ASes ) ) / float( total ) * 100, 2 )
			perc_2 = round( float( len( bad_ASes ) ) / float( total ) * 100, 2 )
			perc_3 = round( float( len( contested_ASes ) ) / float( total ) * 100, 2 )
			perc_4 = round( float( len( no_routing_ASes ) ) / float( total ) * 100, 2 )

			data = [ str(perc_1) + "%", str(perc_2) + "%", str(perc_3) + "%" ]

			routing_state[ str(prefix) ]['statistics'] = dict()
			routing_state[ str(prefix) ]['statistics']['percentage'] = [ perc_1, perc_2, perc_3, perc_4 ]
			routing_state[ str(prefix) ]['statistics']['amount'] = [ len( good_ASes ), len( bad_ASes ), len( contested_ASes ), len( no_routing_ASes ) ]
			routing_state[ str(prefix) ]['statistics']['keys'] = [ 'good', 'bad', 'contested', 'no_routing' ]

		return routing_state

	def __mark_tree_passing_AS( self, routing_state = None, prefix = None, AS_number = None, passing_AS_numbers = None ):
		if passing_AS_numbers is None:
			passing_AS_numbers = [ AS_number ]
		else:
			passing_AS_numbers.append( str(AS_number) )

		tree = routing_state[ str(prefix) ]
		tree[ str(AS_number) ]['passing_ASes'].extend( passing_AS_numbers )

		for from_AS in tree[ str(AS_number) ]['from_ASes']:
			routing_state = self.__mark_tree_passing_AS( routing_state = routing_state, prefix = prefix, AS_number = from_AS, passing_AS_numbers = passing_AS_numbers )

		return routing_state

	def draw_routing_state( self, AS_graph = None, routing_table = None, routing_state = None, draw_unused_links = False, draw_labels = True, file_name = None ):
		self.P.write( "Simulator_Routing_State_Tool: draw_routing_state: start", color = 'green' )

		if AS_graph is None:
			self.P.write_error( "Simulator_Routing_State_Tool: draw_routing_state: AS_graph is None" )
			return None

		if routing_table is None:
			self.P.write_error( "Simulator_Routing_State_Tool: draw_routing_state: routing_table is None" )
			return None

		if routing_state is None:
			self.P.write_error( "Simulator_Routing_State_Tool: draw_routing_state: routing_state is None" )
			return None

		prefixes = routing_state.keys()

		if len( prefixes ) == 0:
			self.P.write_warning( "len( prefixes ) == 0" )
			return 
		elif len( prefixes ) == 1:
			prefix = prefixes[0]
		else:
			self.P.write( "Simulator_Routing_State_Tool: draw_routing_state: found multiple prefixes", color = 'green' )
			counter = 0
			expect_list = list()
			for prefix in prefixes:
				expect_list.append( counter )
				self.P.write( "\t" + str(prefix) + " (" + str(counter) + ")" )
				counter += 1

			index = self.AT.ask( question = "Select prefix " + str(expect_list) + "?", expect_list = expect_list )
			prefix = prefixes[ int( index ) ]

		self.SGDT.reset()
		node_names_dict = self.__draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, prefix = prefix, node_names_dict = dict(), draw_labels = draw_labels )
			
		if draw_unused_links is True:
			node_names_dict = self.__draw_unused_links( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, prefix = prefix, node_names_dict = node_names_dict, draw_labels = draw_labels )
	
		if file_name is None:
			file_name = prefix.replace(".","_").replace("/","_")
			
		self.SGDT.draw_graph( file_name = file_name )
		return

	def __get_AS_numbers( self, routing_state = None, prefix = None ):
		AS_numbers = list()
		for AS_number in routing_state[prefix]:
			try:
				AS_numbers.append( int( AS_number ) )
			except( ValueError ):
				continue

		return AS_numbers

	def __update_node_name( self, routing_state = None, node_names_dict = None, AS_number = None, prefix = None, include_prefix = False ):
		if str( AS_number ) not in node_names_dict:
			node_names_dict[ str(AS_number) ] = "AS" + str(AS_number) 

		#if prefix is not None and "-" not in node_names_dict[ str(AS_number) ]:
		#	number_of_passing_ASes = routing_state[ str(prefix) ][ str(AS_number) ]['number_of_passing_ASes']
		#	node_names_dict[ str(AS_number) ] = "AS" + str(AS_number) + " - " + str(number_of_passing_ASes)

		if include_prefix is True:
			if prefix is not None and str(prefix) not in node_names_dict[ str(AS_number) ]:
				node_names_dict[ str(AS_number) ] = str( node_names_dict[ str(AS_number) ] ) + "\n" + str(prefix)

		return node_names_dict

	def __get_label( self, AS_graph = None, routing_table = None, from_AS = None, to_AS = None, source_AS = None, prefix = None ):
		path_length = -1

		for route in routing_table[ str(to_AS) ][ str(prefix) ]:
			if str( route['source_AS'] ) == str(source_AS):
				path_length = len( route['path'] ) + int( route['extra_path_length'] ) - 1
				prefix_length = str(route['prefix']).split("/")[1]

		LOCAL_PREFERENCE = AS_graph[str(to_AS)]['NEIGHBORS'][str(from_AS)]['LOCAL_PREFERENCE']
		data_list = [ "AS" + str(source_AS), str(LOCAL_PREFERENCE), str(path_length), "/" + str(prefix_length) ]

		return str(data_list)

	def __get_node_type( self, routing_state = None, AS_number = None, prefix = None ):
		routed_to_good_source_AS = routing_state[ prefix ][ str(AS_number) ][ 'routed_to_good_source_AS' ] 
		routed_to_bad_source_AS = routing_state[ prefix ][ str(AS_number) ][ 'routed_to_bad_source_AS' ] 

		if routed_to_good_source_AS is True and routed_to_bad_source_AS is False:
			node_type = "good"
		elif routed_to_good_source_AS is False and routed_to_bad_source_AS is True:
			node_type = "bad"
		elif routed_to_good_source_AS is True and routed_to_bad_source_AS is True:
			node_type = "contested"
		elif routed_to_good_source_AS is False and routed_to_bad_source_AS is False:
			node_type = "no_routing"

		return node_type

	def __get_edge_color( self, routing_state = None, routing_table = None, from_AS = None, to_AS = None, prefix = None, source_AS = None ):
		found = False
		for next_AS in routing_state[ prefix ][ str(from_AS) ]['next_ASes']:
			if str(next_AS) == str(to_AS):
				found = True

		if found is False:
			return "blue"

		for route in routing_table[ str(to_AS) ][ str(prefix) ]:
			if str(route['source_AS']) == str(source_AS):
				if route['used'] is True:
					if route['good'] is True:
						return "green"
					elif route['good'] is False:
						return "red"
				elif route['used'] is False:
					return "blue"

		return "not_present"

	def __get_edge_style( self, AS_graph = None, from_AS = None, to_AS = None, prefix = None ):
		relation = AS_graph[str(from_AS)]['NEIGHBORS'][str(to_AS)]['type']

		if relation == self.TYPE_P2P:
			edge_style = "solid"
		elif relation == self.TYPE_S2S:
			edge_style = "dotted"
		elif relation == self.TYPE_C2P:
			edge_style = "bold"
		elif relation == self.TYPE_P2C:
			edge_style = "dashed"
		else:
			self.P.write_error( "Simulator_Routing_State_Tool: __get_edge_style: relation == -1" )
			edge_style = "bold"

		return edge_style

	def __draw_routing_state( self, AS_graph = None, routing_table = None, routing_state = None, prefix = None, node_names_dict = None, draw_labels = True ):
		AS_numbers = self.__get_AS_numbers( routing_state = routing_state, prefix = prefix )

		for AS_number in AS_numbers:
			node_names_dict = self.__update_node_name( routing_state = routing_state, node_names_dict = node_names_dict, AS_number = AS_number, include_prefix = False )

			for route in routing_table[ str(AS_number)][ prefix ]:
				if len( route['path'] ) == 1:
					node_names_dict = self.__update_node_name( routing_state = routing_state, node_names_dict = node_names_dict, AS_number = AS_number, prefix = route['prefix'], include_prefix = True )
				else:
					node_names_dict = self.__update_node_name( routing_state = routing_state, node_names_dict = node_names_dict, AS_number = AS_number, prefix = route['prefix'], include_prefix = False )

		counter = len( AS_numbers )
		for from_AS in AS_numbers:
			counter -= 1
			self.P.rewrite( "\tSimulator_Routing_State_Tool: __draw_routing_state: " + str(counter) + " ASes left to process          " )

			from_node_name = node_names_dict[str(from_AS)]
			from_node_type = self.__get_node_type( routing_state = routing_state, AS_number = from_AS, prefix = prefix )

			for to_AS in routing_state[prefix][ str(from_AS) ]['next_ASes']:
				source_ASes = list()
				source_ASes.extend( routing_state[prefix][ str(from_AS) ]['good_source_ASes'] )
				source_ASes.extend( routing_state[prefix][ str(from_AS) ]['bad_source_ASes'] )

				for source_AS in source_ASes:
					adding = False
					for route in routing_table[ str(to_AS) ][ str(prefix) ]:
						if str(source_AS) in str( route['source_AS'] ):
							adding = True

					if adding is False:
						continue

					to_node_name = node_names_dict[ str(to_AS) ]
					to_node_type = self.__get_node_type( routing_state = routing_state, AS_number = to_AS, prefix = prefix )

					if draw_labels is True:
						label = self.__get_label( AS_graph = AS_graph, routing_table = routing_table, from_AS = from_AS, to_AS = to_AS, source_AS = source_AS, prefix = prefix )
					else:
						label = ""

					edge_style = self.__get_edge_style( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, prefix = prefix )
					edge_color = self.__get_edge_color( routing_state = routing_state, routing_table = routing_table, from_AS = from_AS, to_AS = to_AS, prefix = prefix, source_AS = source_AS )

					self.SGDT.add_edge( from_node_name = from_node_name, from_node_type = from_node_type, to_node_name = to_node_name, to_node_type = to_node_type, edge_style = edge_style, edge_color = edge_color, label = label )

		return node_names_dict

	def __draw_unused_links( self, AS_graph = None, routing_table = None, routing_state = None, prefix = None, node_names_dict = None, draw_labels = True ):
		for AS_number in self.__get_AS_numbers( routing_state = routing_state, prefix = prefix ):
			node_names_dict = self.__update_node_name( routing_state = routing_state, node_names_dict = node_names_dict, AS_number = AS_number, include_prefix = False )
			from_node_name = node_names_dict[ str(AS_number) ]
			from_node_type = self.__get_node_type( routing_state = routing_state, AS_number = str( AS_number ), prefix = prefix )
			self.SGDT.add_node( node_name = from_node_name, node_type = from_node_type )

			for route in routing_table[str(AS_number)][str(prefix)]:
				path = route['path']
				source_AS = route['source_AS']

				if len( path ) > 1:
					for x in range( 0, len(path) - 1 ):
						from_AS = str( path[x] )
						to_AS = str( path[x+1] )

						from_node_name = node_names_dict[ str(from_AS) ]
						from_node_type = self.__get_node_type( routing_state = routing_state, AS_number = from_AS, prefix = prefix )

						to_node_name = node_names_dict[ str(to_AS) ]
						to_node_type = self.__get_node_type( routing_state = routing_state, AS_number = to_AS, prefix = prefix )

						if draw_labels is True:
							label = self.__get_label( AS_graph = AS_graph, routing_table = routing_table, from_AS = from_AS, to_AS = to_AS, source_AS = source_AS, prefix = prefix )
						else:
							label = ""

						edge_style = self.__get_edge_style( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, prefix = prefix )
						edge_color = self.__get_edge_color( routing_state = routing_state, routing_table = routing_table, from_AS = from_AS, to_AS = to_AS, prefix = prefix, source_AS = source_AS )

						self.SGDT.add_edge( from_node_name = from_node_name, from_node_type = from_node_type, to_node_name = to_node_name, to_node_type = to_node_type, edge_style = edge_style, edge_color = edge_color, label = label )
			
		return node_names_dict

	def write_routing_state_statistics( self, routing_state = None ):
		if routing_state is None:
			self.P.write_error( "Simulator_Routing_State_Tool: write_routing_state_statistics: routing_state is None" )
			return None

		self.P.write( "Simulator_Routing_State_Tool: write_routing_state_statistics ", color = 'green' )

		for prefix in routing_state:
			self.P.write( str(prefix) )
			self.P.write_JSON( routing_state[str(prefix)]['statistics'] )
			self.P.write( routing_state[str(prefix)]['data']['no_routing_ASes'][:10] )

	def save_routing_state( self, relative_folder_path = "", file_name = None, routing_state = None, print_status = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Routing_State_Tool: save_routing_state: file_name is None" )
			return None

		if routing_state is None:
			self.P.write_error( "Simulator_Routing_State_Tool: save_routing_state: routing_state is None" )
			return None

		file_name = file_name.split(".")[0] + ".routing_state"

		self.FT.save_JSON_file( relative_folder_path = relative_folder_path, file_name = file_name, data_JSON = routing_state, print_status = print_status )
		
	def load_routing_state( self, relative_folder_path = "", file_name = None, print_status = False ):
		if file_name is None:
			self.P.write_error( "Simulator_Routing_State_Tool: load_routing_state: file_name is None" )
			return None

		file_name = file_name.split(".")[0] + ".routing_state"

		return self.FT.load_JSON_file( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )








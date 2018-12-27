import json, requests, os, sys, copy

from netaddr import *

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool
from ask_tool import Ask_Tool
from AS_rank_interface import AS_Rank_Interface
from geo_interface import Geo_Interface

from simulator_link_types import Simulator_Link_Types

class Simulator_Graph_Validation_Tool():
	P = None
	AT = None
	ASRI = None
	GI = None

	SGDT = None
	SLT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	def __init__( self, P = None, ASRI = None, GI = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Graph_Validation_Tool: __init__ : P is None" )

		self.P.write( "Simulator_Graph_Validation_Tool: Loading...", color = 'cyan' )

		self.AT = Ask_Tool( P = self.P )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_Graph_Validation_Tool: __init__ : ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if GI is not None:
			self.GI = GI
		else:
			self.P.write_warning( "Simulator_Graph_Validation_Tool: __init__ : GI is None" )
			self.GI = Geo_Interface( P = self.P )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_Graph_Validation_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

	def get_cross_sections( self, AS_graph = None, routing_state = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: get_cross_sections: AS_graph is None" )
			return None

		if routing_state is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: get_cross_sections: routing_state is None" )
			return None

		good_ASes = routing_state['data']['good_ASes']
		bad_ASes = routing_state['data']['bad_ASes']

		for AS_number in good_ASes:
			neighbors = AS_graph[ str(AS_number) ]['NEIGHBORS'].keys()
			

	def validate_connectivity( self, AS_graph = None, AS_number = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: validate_connectivity: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: validate_connectivity: AS_number is None" )
			return None

		AS_connectivity_status = dict()
		for temp_AS_number in AS_graph:
			AS_connectivity_status[ str(temp_AS_number) ] = False

		[ AS_numbers, AS_connectivity_status ] = self.__validate_basic_connectivity( AS_graph = AS_graph, AS_numbers = [ AS_number ], AS_connectivity_status = AS_connectivity_status )

		while len( AS_numbers ) != 0:
			[ AS_numbers, AS_connectivity_status ] = self.__validate_basic_connectivity( AS_graph = AS_graph, AS_numbers = AS_numbers, AS_connectivity_status = AS_connectivity_status )

		if print_debug is True:
			self.P.write( "Simulator_Graph_Validation_Tool: validate_connectivity: AS_connectivity_status:" )
			self.P.write_JSON( AS_connectivity_status )

			for AS_number in AS_connectivity_status:
				if AS_connectivity_status[ str(AS_number) ] is False:
					self.P.write( "AS" + str(AS_number) + " is not reachable", color = 'red' )

		return AS_connectivity_status

	def __validate_basic_connectivity( self, AS_graph = None, AS_numbers = None, AS_connectivity_status = None ):
		new_AS_numbers = list()

		for AS_number in AS_numbers:
			AS_connectivity_status[ str(AS_number) ] = True

			for neighbor in AS_graph[ str(AS_number) ]['NEIGHBORS'].keys():
				if AS_connectivity_status[ str(neighbor) ] is False:
					new_AS_numbers.append( str(neighbor) )
					AS_connectivity_status[ str(neighbor) ] = True

		new_AS_numbers = list( set( new_AS_numbers ) )
		return [ new_AS_numbers, AS_connectivity_status ]

	def compare_routing_states( self, routing_state_1 = None, routing_state_2 = None, include_no_routing_ASes = False ):
		if routing_state_1 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: compare_AS_graphs: routing_state_1 is None" )
			return None

		if routing_state_2 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: compare_AS_graphs: routing_state_2 is None" )
			return None

		results = dict()

		self.P.write( "Simulator_Graph_Validation_Tool: compare_AS_graphs: start", color = 'green' )

		for prefix in routing_state_1:
			results[ str(prefix) ] = dict()
			results[ str(prefix) ]['data'] = dict()
			results[ str(prefix) ]['data']['good'] = dict()
			results[ str(prefix) ]['data']['good']['good'] = list()
			results[ str(prefix) ]['data']['good']['bad'] = list()
			results[ str(prefix) ]['data']['good']['contested'] = list()
			results[ str(prefix) ]['data']['good']['no_routing'] = list()
			results[ str(prefix) ]['data']['bad'] = dict()
			results[ str(prefix) ]['data']['bad']['good'] = list()
			results[ str(prefix) ]['data']['bad']['bad'] = list()
			results[ str(prefix) ]['data']['bad']['contested'] = list()
			results[ str(prefix) ]['data']['bad']['no_routing'] = list()
			results[ str(prefix) ]['data']['contested'] = dict()
			results[ str(prefix) ]['data']['contested']['good'] = list()
			results[ str(prefix) ]['data']['contested']['bad'] = list()
			results[ str(prefix) ]['data']['contested']['contested'] = list()
			results[ str(prefix) ]['data']['contested']['no_routing'] = list()
			results[ str(prefix) ]['data']['no_routing'] = dict()
			results[ str(prefix) ]['data']['no_routing']['good'] = list()
			results[ str(prefix) ]['data']['no_routing']['bad'] = list()
			results[ str(prefix) ]['data']['no_routing']['contested'] = list()
			results[ str(prefix) ]['data']['no_routing']['no_routing'] = list()

			results[ str(prefix) ]['statistics'] = dict()
			results[ str(prefix) ]['statistics']['good'] = dict()
			results[ str(prefix) ]['statistics']['good']['good'] = list()
			results[ str(prefix) ]['statistics']['good']['bad'] = list()
			results[ str(prefix) ]['statistics']['good']['contested'] = list()
			results[ str(prefix) ]['statistics']['good']['no_routing'] = list()
			results[ str(prefix) ]['statistics']['bad'] = dict()
			results[ str(prefix) ]['statistics']['bad']['good'] = list()
			results[ str(prefix) ]['statistics']['bad']['bad'] = list()
			results[ str(prefix) ]['statistics']['bad']['contested'] = list()
			results[ str(prefix) ]['statistics']['bad']['no_routing'] = list()
			results[ str(prefix) ]['statistics']['contested'] = dict()
			results[ str(prefix) ]['statistics']['contested']['good'] = list()
			results[ str(prefix) ]['statistics']['contested']['bad'] = list()
			results[ str(prefix) ]['statistics']['contested']['contested'] = list()
			results[ str(prefix) ]['statistics']['contested']['no_routing'] = list()
			results[ str(prefix) ]['statistics']['no_routing'] = dict()
			results[ str(prefix) ]['statistics']['no_routing']['good'] = list()
			results[ str(prefix) ]['statistics']['no_routing']['bad'] = list()
			results[ str(prefix) ]['statistics']['no_routing']['contested'] = list()
			results[ str(prefix) ]['statistics']['no_routing']['no_routing'] = list()

			counter = len( routing_state_1[ str(prefix) ]['data']['good_ASes'] )
			for AS_number in routing_state_1[ str(prefix) ]['data']['good_ASes']:
				counter -= 1
				self.P.rewrite( "\tSimulator_Graph_Validation_Tool: compare_routing_states: " + str(counter) + " good ASes left to process          " )

				if str(AS_number) in routing_state_2[ str(prefix) ]['data']['good_ASes']:
					results[ str(prefix) ]['data']['good']['good'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['bad_ASes']:
					results[ str(prefix) ]['data']['good']['bad'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['contested_ASes']:
					results[ str(prefix) ]['data']['good']['contested'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['no_routing_ASes']:
					results[ str(prefix) ]['data']['good']['no_routing'].append( str(AS_number) )

			counter = len( routing_state_1[ str(prefix) ]['data']['bad_ASes'] )
			for AS_number in routing_state_1[ str(prefix) ]['data']['bad_ASes']:
				counter -= 1
				self.P.rewrite( "\tSimulator_Graph_Validation_Tool: compare_routing_states: " + str(counter) + " bad ASes left to process          " )

				if str(AS_number) in routing_state_2[ str(prefix) ]['data']['good_ASes']:
					results[ str(prefix) ]['data']['bad']['good'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['bad_ASes']:
					results[ str(prefix) ]['data']['bad']['bad'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['contested_ASes']:
					results[ str(prefix) ]['data']['bad']['contested'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['no_routing_ASes']:
					results[ str(prefix) ]['data']['bad']['no_routing'].append( str(AS_number) )

			counter = len( routing_state_1[ str(prefix) ]['data']['contested_ASes'] )
			for AS_number in routing_state_1[ str(prefix) ]['data']['contested_ASes']:
				counter -= 1
				self.P.rewrite( "\tSimulator_Graph_Validation_Tool: compare_routing_states: " + str(counter) + " contested ASes left to process          " )

				if str(AS_number) in routing_state_2[ str(prefix) ]['data']['good_ASes']:
					results[ str(prefix) ]['data']['contested']['good'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['bad_ASes']:
					results[ str(prefix) ]['data']['contested']['bad'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['contested_ASes']:
					results[ str(prefix) ]['data']['contested']['contested'].append( str(AS_number) )
				elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['no_routing_ASes']:
					results[ str(prefix) ]['data']['contested']['no_routing'].append( str(AS_number) )

			if include_no_routing_ASes is True:
				counter = len( routing_state_1[ str(prefix) ]['data']['no_routing_ASes'] )
				for AS_number in routing_state_1[ str(prefix) ]['data']['no_routing_ASes']:
					counter -= 1
					self.P.rewrite( "\tSimulator_Graph_Validation_Tool: compare_routing_states: " + str(counter) + " no routing ASes left to process          " )

					if str(AS_number) in routing_state_2[ str(prefix) ]['data']['good_ASes']:
						results[ str(prefix) ]['data']['no_routing']['good'].append( str(AS_number) )
					elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['bad_ASes']:
						results[ str(prefix) ]['data']['no_routing']['bad'].append( str(AS_number) )
					elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['contested_ASes']:
						results[ str(prefix) ]['data']['no_routing']['contested'].append( str(AS_number) )
					elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['no_routing_ASes']:
						results[ str(prefix) ]['data']['no_routing']['no_routing'].append( str(AS_number) )

		for prefix in routing_state_1:
			for key_1 in [ 'good', 'bad', 'contested', 'no_routing' ]:
				for key_2 in [ 'good', 'bad', 'contested', 'no_routing' ]:
					results[ str(prefix) ]['statistics'][ key_1 ][ key_2 ] = len( results[ str(prefix) ]['data'][ key_1 ][ key_2 ] )

		return results	

	def get_traces( self, routing_state_1 = None, routing_state_2 = None, source_AS = None, prefix = None ):
		if routing_state_1 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: get_trace: routing_state_1 is None" )
			return None

		if routing_state_2 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: get_trace: routing_state_2 is None" )
			return None

		if source_AS is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: get_trace: source_AS is None" )
			return None

		if prefix is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: get_trace: prefix is None" )
			return None

		traces = self.__get_traces( AS_number = source_AS, source_AS = source_AS, prefix = prefix, traces = dict(), processed_AS_numbers = dict(), routing_state_1 = routing_state_1, routing_state_2 = routing_state_2  )

		return traces

	def write_traces( self, routing_state_1 = None, routing_state_2 = None, source_AS = None, prefix = None ):
		if routing_state_1 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: write_traces: routing_state_1 is None" )
			return None

		if routing_state_2 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: write_traces: routing_state_2 is None" )
			return None

		if source_AS is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: write_traces: source_AS is None" )
			return None

		if prefix is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: write_traces: prefix is None" )
			return None

		traces = self.get_traces( routing_state_1 = routing_state_1, routing_state_2 = routing_state_2, source_AS = source_AS, prefix = prefix )

		self.P.write( "Simulator_Graph_Validation_Tool: write_traces", color = 'green' )
		lines = json.dumps( traces, sort_keys=True, indent=2, separators=(',', ': ') ) 

		for line in lines.split("\n"):
			if "B" in line and not "G" in line and not "C" in line and not "NR" in line:
				self.P.write( line, include_time_stamp = False, color = 'green' )
			elif "G" in line and not "B" in line and not "C" in line and not "NR" in line:
				self.P.write( line, include_time_stamp = False, color = 'green' )
			elif "C" in line and not "G" in line and not "B" in line and not "NR" in line:
				self.P.write( line, include_time_stamp = False, color = 'green' )
			elif "B" in line and "G" in line:
				self.P.write( line, include_time_stamp = False, color = 'red' )
			elif "B" in line and "NR" in line:
				self.P.write( line, include_time_stamp = False, color = 'red' )
			elif "G" in line and "NR" in line:
				self.P.write( line, include_time_stamp = False, color = 'red' )
			elif "B" in line and "C" in line:
				self.P.write( line, include_time_stamp = False, color = 'yellow' )
			elif "G" in line and "C" in line:
				self.P.write( line, include_time_stamp = False, color = 'yellow' )
			else:
				self.P.write( line, include_time_stamp = False )

	def __add_labels( self, AS_number = None, prefix = None, routing_state_1 = None, routing_state_2 = None ):
		AS_number_str = AS_number

		if str(AS_number) in routing_state_1[ str(prefix) ]['data']['good_ASes']:
			AS_number_str = str(AS_number_str) + " |G|"
		elif str(AS_number) in routing_state_1[ str(prefix) ]['data']['bad_ASes']:
			AS_number_str = str(AS_number_str) + " |B|"
		elif str(AS_number) in routing_state_1[ str(prefix) ]['data']['contested_ASes']:
			AS_number_str = str(AS_number_str) + " |C|"
		elif str(AS_number) in routing_state_1[ str(prefix) ]['data']['no_routing_ASes']:
			AS_number_str = str(AS_number_str) + " |NR|"

		if str(AS_number) in routing_state_2[ str(prefix) ]['data']['good_ASes']:
			AS_number_str = str(AS_number_str) + "G|"
		elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['bad_ASes']:
			AS_number_str = str(AS_number_str) + "B|"
		elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['contested_ASes']:
			AS_number_str = str(AS_number_str) + "C|"
		elif str(AS_number) in routing_state_2[ str(prefix) ]['data']['no_routing_ASes']:
			AS_number_str = str(AS_number_str) + "NR|"

		return AS_number_str

	def __get_traces( self, AS_number = None, source_AS = None, prefix = None, traces = None, processed_AS_numbers = None, routing_state_1 = None, routing_state_2 = None ):
		AS_number_str = self.__add_labels( AS_number = AS_number, prefix = prefix, routing_state_1 = routing_state_1, routing_state_2 = routing_state_2 )

		if AS_number_str in processed_AS_numbers:
			return traces
		else:
			traces[ str(AS_number_str) ] = dict()

		processed_AS_numbers[AS_number_str] = None

		for next_AS in routing_state_1[prefix][ str(AS_number) ]['next_ASes']:
			next_AS_str = self.__add_labels( AS_number = next_AS, prefix = prefix, routing_state_1 = routing_state_1, routing_state_2 = routing_state_2 )

			found = False
			if str(source_AS) in routing_state_1[prefix][ str(next_AS) ]['bad_source_ASes']:
				found = True
			elif str(source_AS) in routing_state_1[prefix][ str(next_AS) ]['good_source_ASes']:
				found = True

			if found is True:
				traces[ str(AS_number_str) ] = self.__get_traces( AS_number = next_AS, source_AS = source_AS, prefix = prefix, traces = traces[ str(AS_number_str) ], processed_AS_numbers = processed_AS_numbers, routing_state_1 = routing_state_1, routing_state_2 = routing_state_2 )

		return traces

	def analyse_trace( self, prefix = None, trace = None, AS_graph = None, routing_state_1 = None, routing_state_2 = None ):
		if prefix is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: analyse_trace: prefix is None" )
			return None

		if trace is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: analyse_trace: trace is None" )
			return None

		if AS_graph is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: analyse_trace: AS_graph is None" )
			return None

		if routing_state_1 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: analyse_trace: routing_state_1 is None" )
			return None

		if routing_state_2 is None:
			self.P.write_error( "Simulator_Graph_Validation_Tool: analyse_trace: routing_state_2 is None" )
			return None

		result = list()
		for x in range( 0, len(trace) - 1 ):
			from_AS = self.GI.get_AS_number( IP4_address = trace[x] )
			to_AS = self.GI.get_AS_number( IP4_address = trace[x+1] )

			if str(from_AS) == str(to_AS):
				continue

			from_AS_str = self.__add_labels( AS_number = from_AS, prefix = prefix, routing_state_1 = routing_state_1, routing_state_2 = routing_state_2 )
			to_AS_str = self.__add_labels( AS_number = to_AS, prefix = prefix, routing_state_1 = routing_state_1, routing_state_2 = routing_state_2 )
			label = str(from_AS_str) + " - " + str(to_AS_str)
			
			data_JSON = dict()
			data_JSON[ label ] = list()
			data_JSON[ label ].append( self.SLT.get_database_tag( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS ) )
			data_JSON[ label ].append( self.SLT.get_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS ) )
			data_JSON[ label ].append( self.SLT.get_relation_str( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS ) )
			result.append( data_JSON )

		self.P.write_JSON( result )


		

		









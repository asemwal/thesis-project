import json, requests, os, sys, hashlib, copy, time, math

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool
from time_tool import Time_Tool
from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from ES_interface import ES_Interface

from simulator_link_types import Simulator_Link_Types
from simulator_ES_relations_tool import Simulator_ES_Relations_Tool

class Simulator_AS_Graph_Tool():
	P = None
	FT = None
	TT = None
	ESI = None
	ASRI = None
	RSI = None

	SLT = None
	SESRT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None
	ROUTES = None

	S2S_DEFAULT_LOCAL_PREFERENCE = None
	P2P_DEFAULT_LOCAL_PREFERENCE = None
	P2C_DEFAULT_LOCAL_PREFERENCE = None
	C2P_DEFAULT_LOCAL_PREFERENCE = None

	last_mode = None
	MODE_1 = None
	MODE_2 = None

	def __init__( self, P = None, FT = None, ASRI = None, RSI = None, ESI = None, SGDT = None, SLT = None, SESRT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__: P is None" )

		self.P.write( "Simulator_AS_Graph_Tool: Loading...", color = 'cyan' )
		self.TT = Time_Tool( P = self.P )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_AS_Graph_Tool" )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__: ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if RSI is not None:
			self.RSI = RSI
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__: RSI is None" )
			self.RSI = RIPE_Stat_Interface( P = self.P )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__: ESI is None" )
			self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False, include_coverage = False, include_raw = False )

		if SGDT is not None:
			self.SGDT = SGDT
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__ : SGDT is Nnoe" )
			self.SGDT = Simulator_Graph_Draw_Tool( P = self.P )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__: SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		if SESRT is not None:
			self.SESRT = SESRT
		else:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __init__: SESRT is None" )
			self.SESRT = Simulator_ES_Relations_Tool( P = self.P, FT = self.FT, ASRI = self.ASRI, ESI = self.ESI, SLT = self.SLT )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

		self.S2S_DEFAULT_LOCAL_PREFERENCE = 99
		self.P2P_DEFAULT_LOCAL_PREFERENCE = 101
		self.P2C_DEFAULT_LOCAL_PREFERENCE = 200
		self.C2P_DEFAULT_LOCAL_PREFERENCE = 100

		self.ROUTES = "bgp-routes"

		self.MODE_1 = 1
		self.MODE_2 = 2
		self.last_mode = self.MODE_2

	def init_AS_graph( self, use_AS_rank = False, overwrite = True, print_debug = False  ):
		self.P.write( "Simulator_AS_Graph_Tool: init_AS_graph: start (use_AS_rank = " + str(use_AS_rank) + ", overwrite = " + str(overwrite) + ")" , color = 'green' )
		AS_graph = dict()

		if use_AS_rank is True:
			AS_graph = self.add_AS_rank_links( AS_graph = AS_graph, overwrite = overwrite, print_debug = print_debug )
		
		return AS_graph

	def add_AS( self, AS_graph = None, AS_number = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_AS: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_AS: AS_number is None" )
			return None

		if str(AS_number) not in AS_graph:
			AS_graph[ str(AS_number) ] = dict()
			AS_graph[ str(AS_number) ]['NEIGHBORS'] = dict()
			AS_graph = self.reset_forwarding_rules( AS_graph = AS_graph, AS_number = AS_number )
			AS_graph[ str(AS_number) ]['IN'] = list()
			AS_graph[ str(AS_number) ]['RIB'] = dict()
			AS_graph[ str(AS_number) ]['RIB']['routes'] = list()
			AS_graph[ str(AS_number) ]['RIB']['prefix_to_path_length'] = dict()
			AS_graph[ str(AS_number) ]['RIB']['prefix_to_LOCAL_PREFERENCE'] = dict()
			AS_graph[ str(AS_number) ]['OUT'] = list()
			AS_graph[ str(AS_number) ]['BLACK_HOLE'] = dict()

			if print_debug is True:
				self.P.write( "Simulator_AS_Graph_Tool: add_AS: created AS" + str(AS_number) )
		else:
			if print_debug is True:
				self.P.write( "Simulator_AS_Graph_Tool: add_AS: AS" + str(AS_number) + " already exists" )

		return AS_graph

	def add_link( self, AS_graph = None, from_AS = None, to_AS = None, type = None, LOCAL_PREFERENCE = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_link: AS_graph is None" )
			return None

		if from_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_link: from_AS is None" )
			return None

		if to_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_link: to_AS is None" )
			return None

		if type is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_link: type is None" )
			return None

		if LOCAL_PREFERENCE is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_link: LOCAL_PREFERENCE is None" )
			return None

		if str(from_AS) not in AS_graph:
			AS_graph[ str(from_AS) ] = dict()
			AS_graph[ str(from_AS) ]['NEIGHBORS'] = dict()
			AS_graph = self.reset_forwarding_rules( AS_graph = AS_graph, AS_number = from_AS )
			AS_graph[ str(from_AS) ]['IN'] = list()
			AS_graph[ str(from_AS) ]['RIB'] = dict()
			AS_graph[ str(from_AS) ]['RIB']['routes'] = list()
			AS_graph[ str(from_AS) ]['RIB']['prefix_to_path_length'] = dict()
			AS_graph[ str(from_AS) ]['RIB']['prefix_to_LOCAL_PREFERENCE'] = dict()
			AS_graph[ str(from_AS) ]['OUT'] = list()
			AS_graph[ str(from_AS) ]['BLACK_HOLE'] = dict()

		if database_tag is None:
			database_tag = ""

		data_JSON = dict()
		data_JSON['type'] = type
		data_JSON['LOCAL_PREFERENCE'] = LOCAL_PREFERENCE
		data_JSON['database_tag'] = database_tag

		if str(to_AS) in AS_graph[ str(from_AS) ]['NEIGHBORS'] and overwrite is True:
			if print_debug is True:
				type_str_before = self.SLT.get_type_str( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )
				type_str_after = self.SLT.get_type_str( type = type )

				LOCAL_PREFERECE_before = AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['LOCAL_PREFERENCE']
				LOCAL_PREFERECE_after = LOCAL_PREFERENCE

				if type_str_before != type_str_after or  LOCAL_PREFERECE_before != LOCAL_PREFERECE_after:
					self.P.write( "Simulator_AS_Graph_Tool: add_link: overwritten link [" + str(from_AS) + ", " + str(to_AS) + "], type = " + str( type_str_before ) + " -> " + str( type_str_after ) + ", LOCAL_PREFERENCE = " + str( LOCAL_PREFERECE_before ) + " -> " + str( LOCAL_PREFERECE_after ) )

			AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ] = data_JSON
		elif str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			if create is True:
				AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ] = data_JSON
				type_str = self.SLT.get_type_str( type = type )

				if print_debug is True:
					self.P.write( "Simulator_AS_Graph_Tool: add_link: created link [" + str(from_AS) + ", " + str(to_AS) + "], type = " + str( type_str ) + ", LOCAL_PREFERENCE = " + str(LOCAL_PREFERENCE) ) 
			else:
				if print_debug is True:
					self.P.write( "Simulator_AS_Graph_Tool: add_link: link [" + str(from_AS) + ", " + str(to_AS) + "] does not exists, create is False" ) 

		return AS_graph

	def add_peer( self, AS_graph = None, AS_number = None, peer = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_peer: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_peer: AS_number is None" )
			return None

		if peer is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_peer: peer is None" )
			return None

		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = AS_number, to_AS = peer, type = self.TYPE_P2P, LOCAL_PREFERENCE = self.P2P_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = peer, to_AS = AS_number, type = self.TYPE_P2P, LOCAL_PREFERENCE = self.P2P_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		return AS_graph

	def add_customer( self, AS_graph = None, AS_number = None, customer = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_customer: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_customer: AS_number is None" )
			return None

		if customer is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_customer: customer is None" )
			return None

		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = AS_number, to_AS = customer, type = self.TYPE_P2C, LOCAL_PREFERENCE = self.P2C_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = customer, to_AS = AS_number, type = self.TYPE_C2P, LOCAL_PREFERENCE = self.C2P_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		return AS_graph

	def add_provider( self, AS_graph = None, AS_number = None, provider = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_provider: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_provider: AS_number is None" )
			return None

		if provider is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_provider: provider is None" )
			return None

		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = AS_number, to_AS = provider, type = self.TYPE_C2P, LOCAL_PREFERENCE = self.C2P_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = provider, to_AS = AS_number, type = self.TYPE_P2C, LOCAL_PREFERENCE = self.P2C_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		return AS_graph

	def add_sibling( self, AS_graph = None, AS_number = None, sibling = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_provider: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_provider: AS_number is None" )
			return None

		if sibling is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_provider: sibling is None" )
			return None

		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = AS_number, to_AS = sibling, type = self.TYPE_S2S, LOCAL_PREFERENCE = self.S2S_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		AS_graph = self.add_link( AS_graph = AS_graph, from_AS = sibling, to_AS = AS_number, type = self.TYPE_S2S, LOCAL_PREFERENCE = self.S2S_DEFAULT_LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )
		return AS_graph

	def add_links( self, AS_graph = None, AS_number = None, peers = None, customers = None, providers = None, siblings = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_links: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_links: AS_number is None" )
			return None

		if peers is None and customers is None and providers is None and siblings is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_links: peers is None and customers is None and providers is None" )
			return None

		if peers is not None:
			for peer in peers:
				AS_graph = self.add_peer( AS_graph = AS_graph, AS_number = AS_number, peer = peer, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

		if customers is not None:
			for customer in customers:
				AS_graph = self.add_customer( AS_graph = AS_graph, AS_number = AS_number, customer = customer, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

		if providers is not None:
			for provider in providers:
				AS_graph = self.add_provider( AS_graph = AS_graph, AS_number = AS_number, provider = provider, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

		if siblings is not None:
			for sibling in siblings:
				AS_graph = self.add_sibling( AS_graph = AS_graph, AS_number = AS_number, sibling = sibling, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

		return AS_graph

	def add_AS_rank_links( self, AS_graph = None, overwrite = True, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Tool: add_AS_rank_links: start", color = 'green' )

		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_AS_rank_links: AS_graph is None" )
			return None

		ASes = self.ASRI.get_all_saved_ASes()

		counter = len( ASes )
		for AS_number in ASes:
			counter -= 1

			if counter%1000 == 0:
				self.P.rewrite( "\tSimulator_AS_Graph_Tool: add_AS_rank_links: " + str(counter/1000) + "k Ases left   ")

			peers = self.ASRI.get_peers( AS_number = AS_number )
			customers = self.ASRI.get_customers( AS_number = AS_number )
			providers = self.ASRI.get_providers( AS_number = AS_number )

			AS_graph = self.add_links( AS_graph = AS_graph, AS_number = AS_number, peers = peers, customers = customers, providers = providers, overwrite = overwrite, database_tag = "ASR", print_debug = False )

			if print_debug is True:
				if len(peers) + len(customers) + len(providers) == 0:
					self.P.write_warning( "Simulator_AS_Graph_Tool: add_AS_rank_links: AS" + str(AS_number) + ": len(peers) + len(customers) + len(providers) == 0" )

		return AS_graph

	def add_possible_siblings( self, AS_graph = None, print_debug = False ):
		self.P.write( "Simulator_AS_Graph_Tool: add_possible_siblings", color = 'green' )

		possible_siblings = self.FT.load_JSON_file( relative_folder_path = "../", file_name = "possible_siblings.json" )
		
		for siblings in possible_siblings:
			if len(siblings) < 2:
				self.P.write_error( "Simulator_AS_Graph_Tool: add_possible_siblings: len(siblings) < 2" )

			for x in range( 1, len(siblings) ):
				AS_graph = self.add_sibling( AS_graph = AS_graph, AS_number = siblings[0], sibling = siblings[x], overwrite = True, create = True, database_tag = "S2S", print_debug = print_debug )

		return AS_graph

	def remove_unused_ASes( self, AS_graph = None ):
		self.P.write( "Simulator_AS_Graph_Tool: remove_unused_ASes", color = 'green' )

		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_BGP_view_links: AS_graph is None" )
			return None

		remove_list = list()

		for AS_number in AS_graph:
			if len( AS_graph[ str(AS_number) ]['RIB']['routes'] ) == 0:
				remove_list.append( AS_number )

		for AS_number in remove_list:
			del AS_graph[ str(AS_number) ]

		return AS_graph

	def reset_forwarding_rules( self, AS_graph = None, AS_number = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: reset_forwarding_rules: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: reset_forwarding_rules: AS_number is None" )
			return None

		AS_graph[ str(AS_number) ]['RULES'] = dict()
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_S2S)] = dict()
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_S2S)][str(self.TYPE_S2S)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_S2S)][str(self.TYPE_P2C)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_S2S)][str(self.TYPE_C2P)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_S2S)][str(self.TYPE_P2P)] = True

		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2C)] = dict()
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2C)][str(self.TYPE_S2S)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2C)][str(self.TYPE_P2C)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2C)][str(self.TYPE_C2P)] = False
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2C)][str(self.TYPE_P2P)] = False

		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_C2P)] = dict()
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_C2P)][str(self.TYPE_S2S)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_C2P)][str(self.TYPE_P2C)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_C2P)][str(self.TYPE_C2P)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_C2P)][str(self.TYPE_P2P)] = True

		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2P)] = dict()
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2P)][str(self.TYPE_S2S)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2P)][str(self.TYPE_P2C)] = True
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2P)][str(self.TYPE_C2P)] = False
		AS_graph[ str(AS_number) ]['RULES'][str(self.TYPE_P2P)][str(self.TYPE_P2P)] = False

		return AS_graph

	def get_forwarding_rules( self, AS_graph = None, AS_number = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: print_forwarding_rules: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: print_forwarding_rules: AS_number is None" )
			return None

		data_JSON = dict()

		for from_type in AS_graph[ str(AS_number) ]['RULES']:
			from_type_str = self.SLT.get_type_str( type = from_type )
			data_JSON[ from_type_str ] = dict()

			for to_type in AS_graph[ str(AS_number) ]['RULES'][from_type]:
				to_type_str = self.SLT.get_type_str( type = to_type )
				allow = AS_graph[ str(AS_number) ]['RULES'][from_type][to_type]
				data_JSON[ from_type_str ][ to_type_str ] = allow

		return data_JSON

	def print_forwarding_rules( self, AS_graph = None, AS_number = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: print_forwarding_rules: AS_graph is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: print_forwarding_rules: AS_number is None" )
			return None

		forwarding_rules = self.get_forwarding_rules( AS_graph = AS_graph, AS_number = AS_number )
		self.P.write( "Simulator_AS_Graph_Tool: print_forwarding_rules:" )
		self.P.write_JSON( forwarding_rules )

	def add_forwarding_rule( self, AS_graph = None, AS_number = None, from_type = None, to_type = None, allow = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_forwarding_rule: AS_graph is None" )
			return AS_graph

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_forwarding_rule: AS_number is None" )
			return AS_graph

		if from_type is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_forwarding_rule: from_type is None" )
			return AS_graph

		if to_type is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_forwarding_rule: to_type is None" )
			return AS_graph

		if allow is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: add_forwarding_rule: allow is None" )
			return AS_graph

		AS_graph[ str(AS_number) ]['RULES'][str(from_type)][str(to_type)] = allow
		return AS_graph

	def set_type( self, AS_graph = None, from_AS = None, to_AS = None, type = None, update_LOCAL_PREFERENCE = True, update_reversed_link = True, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_type: AS_graph is None" )
			return AS_graph

		if from_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_type: from_AS is None" )
			return AS_graph

		if to_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_type: to_AS is None" )
			return AS_grap

		if type is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_type: type is None" )
			return AS_graph

		if str(from_AS) not in AS_graph:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_type: AS" + str(from_AS) + " is not in AS_graph" )
			return AS_graph

		if str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_type: AS" + str(to_AS) + " is not connected with AS" + str(from_AS) )
			return AS_graph

		AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['type'] = type

		if update_LOCAL_PREFERENCE is True:
			AS_graph = self.reset_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

		if update_reversed_link is True:
			if str(to_AS) not in AS_graph:
				self.P.write_error( "Simulator_AS_Graph_Tool: set_type: AS" + str(to_AS) + " is not in AS_graph" )
				return AS_graph

			if str(from_AS) not in AS_graph[ str(to_AS) ]['NEIGHBORS']:
				self.P.write_error( "Simulator_AS_Graph_Tool: set_type: AS" + str(from_AS) + " is not connected with AS" + str(to_AS) )
				return AS_graph

			AS_graph[ str(to_AS) ]['NEIGHBORS'][ str(from_AS) ]['type'] = type

			if update_LOCAL_PREFERENCE is True:
				AS_graph = self.reset_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = to_AS, to_AS = from_AS )

		return AS_graph

	def set_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None, LOCAL_PREFERENCE = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_LOCAL_PREFERENCE: AS_graph is None" )
			return AS_graph

		if from_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_LOCAL_PREFERENCE: from_AS is None" )
			return AS_graph

		if to_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_LOCAL_PREFERENCE: to_AS is None" )
			return AS_graph

		if LOCAL_PREFERENCE is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_LOCAL_PREFERENCE: LOCAL_PREFERENCE is None" )
			return AS_graph

		if str(from_AS) not in AS_graph:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_LOCAL_PREFERENCE: AS" + str(from_AS) + " is not in AS_graph" )
			return AS_graph

		if str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			self.P.write_error( "Simulator_AS_Graph_Tool: set_LOCAL_PREFERENCE: AS" + str(to_AS) + " is not connected with AS" + str(from_AS) )
			return AS_graph

		AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['LOCAL_PREFERENCE'] = LOCAL_PREFERENCE

		return AS_graph

	def get_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None, LOCAL_PREFERENCE = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_LOCAL_PREFERENCE: AS_graph is None" )
			return None

		if from_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_LOCAL_PREFERENCE: from_AS is None" )
			return None

		if to_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_LOCAL_PREFERENCE: to_AS is None" )
			return None

		if str(from_AS) not in AS_graph:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_LOCAL_PREFERENCE: AS" + str(from_AS) + " is not in AS_graph" )
			return None

		if str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_LOCAL_PREFERENCE: AS" + str(to_AS) + " is not connected with AS" + str(from_AS) )
			return None

		return AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['LOCAL_PREFERENCE'] 

	def reset_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: reset_LOCAL_PREFERENCE: AS_graph is None" )
			return AS_graph

		if from_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: reset_LOCAL_PREFERENCE: from_AS is None" )
			return AS_graph

		if to_AS is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: reset_LOCAL_PREFERENCE: to_AS is None" )
			return AS_graph

		type = self.SLT.get_type( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

		if type == self.TYPE_S2S:
			AS_graph = self.set_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, LOCAL_PREFERENCE = self.S2S_DEFAULT_LOCAL_PREFERENCE )
		elif type == self.TYPE_P2P:
			AS_graph = self.set_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, LOCAL_PREFERENCE = self.P2P_DEFAULT_LOCAL_PREFERENCE )
		elif type == self.TYPE_C2P:
			AS_graph = self.set_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, LOCAL_PREFERENCE = self.C2P_DEFAULT_LOCAL_PREFERENCE )
		elif type == self.TYPE_P2C:
			AS_graph = self.set_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, LOCAL_PREFERENCE = self.P2C_DEFAULT_LOCAL_PREFERENCE )
		else:
			self.P.write_error( "Simulator_AS_Graph_Tool: reset_LOCAL_PREFERENCE: to_AS is None" )
			return None

	def create_announcement( self, prefix = None, AS_number = None, good = None, print_debug = False ):
		if prefix is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: create_announcement: prefix is None" )
			return None

		if AS_number is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: create_announcement: AS_number is None" )
			return None

		if good is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: create_announcement: good is None" )
			return None

		announcement = dict()
		announcement['LOCAL_PREFERENCE'] = 9999
		announcement['prefix'] = str( prefix )
		announcement['prefix_length'] = str( IPNetwork(prefix).prefixlen )
		announcement['source_AS'] = str(AS_number)
		announcement['path'] = [ str(AS_number) ]
		announcement['good'] = good
		
		if print_debug is True:
			self.P.write_debug( "Simulator_AS_Graph_Tool: create_announcement: " )
			self.P.write_JSON( announcement )

		return announcement

	def insert_announcement( self, AS_graph = None, announcement = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_announcement: AS_graph is None" )
			return AS_graph

		if announcement is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_announcement: announcement is None" )
			return AS_graph

		if print_debug is True:
			self.P.write_debug( "Simulator_AS_Graph_Tool: insert_announcement" )
			self.P.write_JSON( announcement )

		source_AS = announcement['source_AS']

		if str(source_AS) not in AS_graph:
			self.P.write_warning( "Simulator_AS_Graph_Tool: insert_announcement: " +  str(source_AS) + " not in AS_graph local data" )
			return AS_graph

		RIB = AS_graph[str(source_AS)]['RIB']
		RIB = self.__add_to_RIB( route = announcement, RIB = RIB, send_to_IN = True )
		AS_graph[str(source_AS)]['RIB'] = RIB

		AS_graph[str(source_AS)]['OUT'].append( announcement )
		return AS_graph

	def insert_route( self, AS_graph = None, route = None, good = None, print_debug = False ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_route: AS_graph is None" )
			return AS_graph

		if route is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_route: route is None" )
			return AS_graph	

		if good is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_route: good is None" )
			return AS_graph

		if "start_IP" in route and "end_IP" in route:
			size = int( IPAddress( route['end_IP'] ) ) - int( IPAddress( route['start_IP'] ) ) 
			size = round( math.log(size)/math.log(2), 0 )

			if "." in route['start_IP']:
				prefix_length = int( 32 - size )
			elif ":" in route['start_IP']:
				prefix_length = int( 128 - size )

			route['prefix'] = route['start_IP'] + "/" + str(prefix_length)

		if "prefix" not in route:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_route: 'prefix' not in route" )
			return AS_graph

		if "source_AS" not in route:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_route: 'source_AS' not in route" )
			return AS_graph

		if "path" not in route:
			self.P.write_error( "Simulator_AS_Graph_Tool: insert_route: 'path' not in route" )
			return AS_graph

		route['good'] = good
		route['prefix_length'] = str( IPNetwork( route['prefix'] ).prefixlen )

		if print_debug is True:
			self.P.write( "Simulator_AS_Graph_Tool: insert_route: good = " + str(good) + ", prefix = " + str(route['prefix']) + ", source_AS = " + str(route['source_AS']) + ", path = " + str(route['path']) )
			#self.P.write_JSON( route )

		while len( route['path'] ) > 0:
			[ AS_graph, route ] = self.__insert_route( AS_graph = AS_graph, route = route )

		return AS_graph
			
	def __insert_route( self, AS_graph = None, route = None ):
		extra_path_length = len( route['path'] ) - len( list( OrderedDict.fromkeys( route['path'] ) ) )
		
		while len( route['path'] ) > 1 and route['path'][ len( route['path'] ) - 1 ] == route['path'][ len( route['path'] ) - 2 ]:
			route['path'].pop( len( route['path'] ) - 1 )

		temp_route = copy.deepcopy( route )
		temp_route['path'] = list(OrderedDict.fromkeys(temp_route['path']))
		temp_route = self.__add_LOCAL_PREFERENCE( AS_graph = AS_graph, route = temp_route )	

		AS_number = route['path'][ len( route['path'] ) - 1 ]
		RIB = AS_graph[str(AS_number)]['RIB']
		RIB = self.__add_to_RIB( route = temp_route, RIB = RIB, extra_path_length = extra_path_length, send_to_IN = False )
		AS_graph[str(AS_number)]['RIB'] = RIB

		route['path'].pop( len( route['path'] ) - 1 )
		return [ AS_graph, route ]

	def iterate_AS_graph( self, AS_graph = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: iterate_AS_graph: AS_graph is None" )
			return None

		self.run_counter = 0
		self.last_mode = self.MODE_2

		finished = False
		while finished is False:
			[ finished, AS_graph ] = self.__iterate( AS_graph = AS_graph )

		return AS_graph

	def __iterate( self, AS_graph = None, run_counter = None ):
		if self.last_mode == self.MODE_1:
			self.last_mode = self.MODE_2
			mode = self.MODE_2

		elif self.last_mode == self.MODE_2:
			self.last_mode = self.MODE_1
			mode = self.MODE_1

		if self.MODE_1 == mode:
			self.run_counter += 1
			self.P.write( include_time_stamp = False )
			self.P.write( "*-*-*-*-*-* START RUN " + str(self.run_counter) + " *-*-*-*-*-*")
			[ AS_graph, changed ] = self.__run_mode_1( AS_graph = AS_graph )
		if self.MODE_2 == mode:
			[ AS_graph, changed ] = self.__run_mode_2( AS_graph = AS_graph )

		if changed is True:
			return [ False, AS_graph ]
		else:
			return [ True, AS_graph ]

	def __run_mode_1( self, AS_graph = None ):
		self.P.write( "Simulator_AS_Graph_Tool: __run_mode_1: start", color = 'green' )

		number_of_outs = 0
		changed = False
		counter = len(AS_graph)
		for AS_number in AS_graph:
			counter -= 1
			if counter % 100 == 0:
				self.P.rewrite( "\tSimulator_AS_Graph_Tool: __run_mode_1: " + str(counter) + " ASes left to process          " )

			for route in AS_graph[str(AS_number)]['RIB']['routes']:
				if route['send_to_IN'] is False:
					continue

				route['send_to_IN'] = False

				if len( route['path'] ) == 1:
					for neighbor_AS in AS_graph[str(AS_number)]['NEIGHBORS']:
						AS_graph[str(neighbor_AS)]['IN'].append( route )
						changed = True
						number_of_outs += 1
				else:
					previous_AS = route['path'][ len(route['path']) - 2 ]
					from_type = AS_graph[str(previous_AS)]['NEIGHBORS'][str(AS_number)]['type']

					for neighbor_AS in AS_graph[str(AS_number)]['NEIGHBORS']:
						to_type = AS_graph[str(AS_number)]['NEIGHBORS'][str(neighbor_AS)]['type']

						types = self.SLT.get_types( AS_graph = AS_graph, route = route )

						if from_type == self.TYPE_S2S and len( types ) > 1:
							if self.TYPE_P2C in types or self.TYPE_P2P in types:
								if str( to_type ) == str( self.TYPE_P2C ) or str( to_type ) == str( self.TYPE_S2S ):
									AS_graph[str(neighbor_AS)]['IN'].append( route )
									changed = True
									number_of_outs += 1
							else:
								AS_graph[str(neighbor_AS)]['IN'].append( route )
								number_of_outs += 1

						elif AS_graph[ str(AS_number) ]["RULES"][ str(from_type) ][ str(to_type) ] is True:
							AS_graph[str(neighbor_AS)]['IN'].append( route )
							changed = True
							number_of_outs += 1

		self.P.rewrite( "\tSimulator_AS_Graph_Tool: __run_mode_1: " + str(number_of_outs) + " outs                          " )
		return [ AS_graph, changed ]

	def __process_BLACK_HOLE( self, route = None, AS_graph = None ):
		status = "no_action"

		if len( route['path'] ) < 2:
			return AS_graph 

		x1 = len( route['path'] ) - 2
		x2 = len( route['path'] ) - 1

		previous_AS = route['path'][x1]
		current_AS = route['path'][x2]

		if self.SLT.get_type( AS_graph = AS_graph, from_AS = previous_AS, to_AS = current_AS ) != self.TYPE_S2S:
			return AS_graph

		for previous_route in AS_graph[ str(previous_AS) ]['RIB']['routes']:
			if previous_route['prefix'] != route['prefix']:
				continue

			length = len( previous_route['path'] )
			if length < 2:
				continue

			if str( previous_route['path'][ length - 2 ] ) == str( current_AS ):
				AS_graph = self.__add_to_black_hole_ASes( AS_graph = AS_graph, prefix = route['prefix'], AS_number = previous_AS, black_hole_AS = current_AS )

				if str( route['source_AS'] ) == str( previous_route['source_AS'] ):
					return AS_graph

		return AS_graph

	def __process_LOCAL_PREFERENCE( self, AS_graph = None, route = None, RIB = None, OUT = None ):
		status = "no_action"

		if route['prefix'] in RIB['prefix_to_LOCAL_PREFERENCE']:
			if RIB['prefix_to_LOCAL_PREFERENCE'][ route['prefix'] ] < route['LOCAL_PREFERENCE']:
				AS_graph = self.__process_BLACK_HOLE( AS_graph = AS_graph, route = route )

				RIB = self.__add_to_RIB( route = route, RIB = RIB, send_to_IN = True )
				status = "added"

		return [ status, RIB ]

	def __process_AS_PATH( self, AS_graph = None, route = None, RIB = None, OUT = None ):
		status = "no_action"

		if route['prefix'] in RIB['prefix_to_path_length']:
			if RIB['prefix_to_path_length'][ route['prefix'] ] > len( route['path'] ):
				AS_graph = self.__process_BLACK_HOLE( AS_graph = AS_graph, route = route )

				RIB = self.__add_to_RIB( route = route, RIB = RIB, send_to_IN = True )
				status = "RIB+OUT"
			elif RIB['prefix_to_path_length'][ route['prefix'] ] == len( route['path'] ):
				AS_graph = self.__process_BLACK_HOLE( AS_graph = AS_graph, route = route )
				RIB = self.__add_to_RIB( route = route, RIB = RIB, send_to_IN = False )
				status = "RIB"
			elif RIB['prefix_to_path_length'][ route['prefix'] ] < len( route['path'] ):
				status = "deleted"

		return [ status, RIB ]

	def __process_PREFIX_LENGTH( self, AS_graph = None, route = None, RIB = None, OUT = None ):
		#NOT USED
		status = "no_action"

		for local_route in RIB['routes']:
			if IPNetwork( route['prefix'] ) in IPNetwork( local_route['prefix'] ):
				AS_graph = self.__process_BLACK_HOLE( AS_graph = AS_graph, route = route )

				RIB = self.__add_to_RIB( route = route, RIB = RIB, send_to_IN = True )
				status = "added"
				break

		return [ status, RIB ]

	def __add_to_black_hole_ASes( self, AS_graph = None, prefix = None, AS_number = None, black_hole_AS = None, print_debug = False ):
		if print_debug is True:
			self.P.write_warning( "Simulator_AS_Graph_Tool: __add_to_black_hole_ASes: AS" + str(AS_number) + " - AS" + str(black_hole_AS) )

		if str(prefix) not in AS_graph[ str( AS_number) ]['BLACK_HOLE']:
			AS_graph[ str( AS_number) ]['BLACK_HOLE'][ str(prefix) ] = list()

		if str(prefix) not in AS_graph[ str( black_hole_AS) ]['BLACK_HOLE']:
			AS_graph[ str( black_hole_AS) ]['BLACK_HOLE'][ str(prefix) ] = list()

		if str(black_hole_AS) not in AS_graph[ str( AS_number) ]['BLACK_HOLE']:
			AS_graph[ str( AS_number) ]['BLACK_HOLE'][ str(prefix) ].append( str(black_hole_AS) )

		if str(AS_number) not in AS_graph[ str( black_hole_AS) ]['BLACK_HOLE']:
			AS_graph[ str( black_hole_AS) ]['BLACK_HOLE'][ str(prefix) ].append( str(AS_number) )

		return AS_graph

	def __add_to_RIB( self, route = None, RIB = None, extra_path_length = 0, send_to_IN = None ):
		route['extra_path_length'] = extra_path_length
		
		if send_to_IN is True:
			route['send_to_IN'] = True
		elif send_to_IN is False:
			route['send_to_IN'] = False
		else:
			self.P.write_error( "Simulator_AS_Graph_Tool: __add_to_RIB: send_to_IN is None" )
			exit()

		RIB['routes'].append( route )

		if route['prefix'] in RIB['prefix_to_path_length']:
			if RIB['prefix_to_path_length'][ route['prefix'] ] > len( route['path'] ) + route['extra_path_length']:
				RIB['prefix_to_path_length'][ route['prefix'] ] = len( route['path'] ) + route['extra_path_length']
		else:
			RIB['prefix_to_path_length'][ route['prefix'] ] = len( route['path'] ) + route['extra_path_length']

		if route['prefix'] in RIB['prefix_to_LOCAL_PREFERENCE'] and 'LOCAL_PREFERENCE' in route:
			if RIB['prefix_to_LOCAL_PREFERENCE'][ route['prefix'] ] < route['LOCAL_PREFERENCE']:
				RIB['prefix_to_LOCAL_PREFERENCE'][ route['prefix'] ] = route['LOCAL_PREFERENCE']
		elif 'LOCAL_PREFERENCE' in route:
			RIB['prefix_to_LOCAL_PREFERENCE'][ route['prefix'] ] = route['LOCAL_PREFERENCE'] 

		return RIB

	def __add_LOCAL_PREFERENCE( self, AS_graph = None, route = None ):
		if len( route['path'] ) == 1:
			route['LOCAL_PREFERENCE'] = 9999
		else:
			from_AS = route['path'][ len(route['path']) - 1 ]
			to_AS = route['path'][ len(route['path']) - 2 ]

			if str(from_AS) not in AS_graph:
				self.P.write_error( "Simulator_AS_Graph_Tool: __add_LOCAL_PREFERENCE: " + str(from_AS) + " not in AS_graph" )
				return route

			if str(to_AS) not in AS_graph[str(from_AS)]['NEIGHBORS']:
				self.P.write_error( "Simulator_AS_Graph_Tool: __add_LOCAL_PREFERENCE: " + str(to_AS) + " not in AS_graph[" + str(from_AS) + "]['NEIGHBORS']" )

			route['LOCAL_PREFERENCE'] = AS_graph[str(from_AS)]['NEIGHBORS'][str(to_AS)]['LOCAL_PREFERENCE']

		return route

	def __run_mode_2( self, AS_graph = None ):
		self.P.write( "Simulator_AS_Graph_Tool: __run_mode_2: start", color = 'green' )

		counter = len(AS_graph)
		changed = False
		number_of_ins = 0
		temp_data = [ 0, 0, 0, 0, 0, 0 ]

		for AS_number in AS_graph:
			counter -= 1
			if counter % 100 == 0:
				self.P.rewrite( "\tSimulator_AS_Graph_Tool: __run_mode_2: " + str(counter) + " ASes left to process          " )

			IN = AS_graph[str(AS_number)]['IN']
			RIB = AS_graph[str(AS_number)]['RIB']

			for route in IN:
				local_route = copy.deepcopy( route )
				number_of_ins += 1

				if str(AS_number) in local_route['path']:
					temp_data[0] += 1
					local_route = None
					continue

				local_route['path'].append( AS_number )
				local_route = self.__add_LOCAL_PREFERENCE( AS_graph = AS_graph, route = local_route )

				[ status, RIB ] = self.__process_LOCAL_PREFERENCE( AS_graph = AS_graph, route = local_route, RIB = RIB )
				if "added" in status:
					changed = True
					temp_data[1] += 1
					local_route = None
					continue

				[ status, RIB ] = self.__process_AS_PATH( AS_graph = AS_graph, route = local_route, RIB = RIB )
				if "RIB+OUT" == status:
					changed = True
					temp_data[2] += 1
					local_route = None
					continue
				elif "RIB" == status:
					temp_data[3] += 1
					local_route = None
					continue
				elif "deleted" == status:
					temp_data[4] += 1
					local_route = None
					continue
	
				if "no_action" in status:
					changed = True
					temp_data[5] += 1
					AS_graph = self.__process_BLACK_HOLE( AS_graph = AS_graph, route = local_route )
					RIB = self.__add_to_RIB( route = local_route, RIB = RIB, send_to_IN = True )
					local_route = None
					continue

			AS_graph[str(AS_number)]['IN'] = list()
			AS_graph[str(AS_number)]['RIB'] = RIB

		self.P.rewrite( "\tSimulator_AS_Graph_Tool: __run_mode_2: " + str(number_of_ins) + " ins, [ LOOP, LOCAL_PREF, AS_PATH_RIB_OUT, AS_PATH_RIB, AS_PATH_DEL, OTHER ] = " + str(temp_data) + "                          " )
		return [ AS_graph, changed ]

	def get_unique_paths( self, AS_graph = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_unique_paths: AS_graph is None" )
			return None

		self.P.write( "\tSimulator_AS_Graph_Tool: get_unique_paths: start" )

		types_dict = dict()
		for AS_number in AS_graph:
			for route in AS_graph[ AS_number ]['RIB']['routes']:
				AS_list = route['path']
				types = list()
				for x in range( 0, len(AS_list) - 1 ):
					type = AS_graph[str(AS_list[x])]['NEIGHBORS'][str(AS_list[x+1])]['type']

					if type == self.TYPE_P2P:
						types.append( "p2p" )
					elif type == self.TYPE_P2C:
						types.append( "p2c" )
					elif type == self.TYPE_C2P:
						types.append( "c2p" )
					elif type == self.TYPE_S2S:
						types.append( "s2s" )
					else:
						types.append( "None" )

				if str(types) not in types_dict:
					types_dict[str(types)] = 0

				types_dict[str(types)] += 1

		return types_dict

	def write_unique_paths( self, AS_graph = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: print_unique_paths: AS_graph is None" )
			return None

		unique_paths = self.get_unique_paths( AS_graph = AS_graph )

		self.P.write( "Simulator_AS_Graph_Tool: write_unique_paths ", color = 'green' )
		self.P.write_JSON( unique_paths )

	def draw_AS_graph( self, AS_graph = None, draw_labels = True, file_name = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: draw_AS_graph: AS_graph is None" )
			return None

		if file_name is None:
			self.P.write_warning( "Simulator_AS_Graph_Tool: draw_AS_graph: file_name is None" )
			self.P.write_warning( "Simulator_AS_Graph_Tool: draw_AS_graph: setting file_name = 'AS_graph'" )
			file_name = "AS_graph"

		self.SGDT.reset()

		for AS_number in AS_graph:
			if len( AS_graph[ str(AS_number) ]['NEIGHBORS'] ) == 0:
				self.SGDT.add_node( node_name = "AS" + str(AS_number) )

			for neighbor_AS in AS_graph[ str(AS_number) ]['NEIGHBORS']:
				type = AS_graph[ str(AS_number) ]['NEIGHBORS'][ str(neighbor_AS) ]['type']
				dir = None
				label = None

				if type == self.TYPE_C2P:
					continue
					edge_style = "bold"
					if draw_labels is True:
						label = "c2p"
				elif type == self.TYPE_P2C:
					edge_style = "dashed"
					if draw_labels is True:
						label = "p2c"
				elif type == self.TYPE_P2P:
					edge_style = "solid"
					if draw_labels is True:
						label = "p2p"
					dir = "both"
				elif type == self.TYPE_S2S:
					edge_style = "dotted"
					if draw_labels is True:
						label = "s2s"
					dir = "both"

				self.SGDT.add_edge( from_node_name = "AS" + str(AS_number), to_node_name = "AS" + str(neighbor_AS), edge_style = edge_style, edge_color = "black", label = label, dir = dir )
			
		file_name = file_name.split('.')[0]
		self.SGDT.draw_graph( file_name = file_name )
		return

	def get_AS_graph_relations( self, AS_graph = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: get_AS_graph_relations: AS_graph is None" )
			return None

		relations = dict()
		for from_AS in AS_graph.keys():
			for to_AS in AS_graph[ from_AS ]['NEIGHBORS'].keys():
				type = AS_graph[ from_AS ]['NEIGHBORS'][to_AS]['type']

				relation = self.SESRT.create_relation( from_AS = from_AS, to_AS = to_AS, type = type )
				relation_id = self.SESRT.get_relation_id( relation = relation )
				relations[ relation_id ] = relation

		return relations

	def save_AS_graph( self, relative_folder_path = "", file_name = None, AS_graph = None, print_status = False ):
		if file_name is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: save_AS_graph: file_name is None" )
			return None

		if AS_graph is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: save_AS_graph: AS_graph is None" )
			return None

		file_name = file_name.split(".")[0] + ".AS_graph"

		self.FT.save_JSON_file( relative_folder_path = relative_folder_path, file_name = file_name, data_JSON = AS_graph, print_status = print_status )

	def load_AS_graph( self, relative_folder_path = "", file_name = None, print_status = False ):
		if file_name is None:
			self.P.write_error( "Simulator_AS_Graph_Tool: save_AS_graph: file_name is None" )
			return None

		file_name = file_name.split(".")[0] + ".AS_graph"

		return self.FT.load_JSON_file( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )

















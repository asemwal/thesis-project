import json, requests, os, sys

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool

from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from geo_interface import Geo_Interface
from ES_interface import ES_Interface

from simulator_link_types import Simulator_Link_Types

from simulator_AS_graph_tool import Simulator_AS_Graph_Tool
from simulator_AS_graph_predictor_tool import Simulator_AS_Graph_Predictor_Tool
from simulator_routing_table_tool import Simulator_Routing_Table_Tool
from simulator_routing_state_tool import Simulator_Routing_State_Tool

from simulator_create_legend_tool import Simulator_Create_Legend_Tool
from simulator_graph_draw_tool import Simulator_Graph_Draw_Tool
from simulator_graph_validation_tool import Simulator_Graph_Validation_Tool

from simulator_relation_type_improver_tool import Simulator_Relation_Type_Improver_Tool

from simulator_ES_routes_tool import Simulator_ES_Routes_Tool
from simulator_ES_relations_tool import Simulator_ES_Relations_Tool
from simulator_ES_trace_routes_tool import Simulator_ES_Trace_Routes_Tool
from simulator_random_AS_graph_tool import Simulator_Random_AS_Graph_Tool

class Simulator_Interface():
	P = None
	FT = None
	ASRI = None
	RSI = None
	ESI = None

	ST = None
	SIT = None
	SPT = None
	SPPT = None
	SRPT = None
	SGDT = None
	SRTPT = None
	SRTRT = None
	SESRT_1 = None
	SESRT_2 = None
	SESTRT = None
	SGVT = None
	SCLT = None

	def __init__( self, P = None, FT = None, ASRI = None, RSI = None, GI = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Interface: __init__ : P is None" )

		self.P.write( "Simulator_Interface: Loading...", color = 'cyan' )

		if FT is not None:
			self.FT = FT
		else:
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Interface" )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_Interface : __init__ : ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if RSI is not None:
			self.RSI = RSI
		else:
			self.P.write_warning( "Simulator_AS_Graph_Predictor_Tool: __init__ : ASRI is None" )
			self.RSI = RIPE_Stat_Interface( P = self.P )

		if GI is not None:
			self.GI = GI
		else:
			self.P.write_warning( "Simulator_Interface: __init__ : GI is None" )
			self.GI = Geo_Interface( P = self.P )

		self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False )

		
		self.SLT = Simulator_Link_Types( P = self.P )
		self.SGDT = Simulator_Graph_Draw_Tool( P = self.P, FT = self.FT )
		self.SESRT_2 = Simulator_ES_Relations_Tool( P = self.P, FT = self.FT, ASRI = self.ASRI, ESI = self.ESI, SLT = self.SLT )

		self.SASGT = Simulator_AS_Graph_Tool( P = self.P, FT = self.FT, ASRI = self.ASRI, RSI = self.RSI, ESI = self.ESI, SGDT = self.SGDT, SLT = self.SLT, SESRT = self.SESRT_2 )
		self.SRTT = Simulator_Routing_Table_Tool( P = self.P, FT = self.FT, SLT = self.SLT )
		self.STST = Simulator_Routing_State_Tool( P = self.P, FT = self.FT, SGDT = self.SGDT, SLT = self.SLT )
		self.SASGPT = Simulator_AS_Graph_Predictor_Tool( P = self.P, ASRI = self.ASRI, SASGT = self.SASGT, SLT = self.SLT )
		
		self.SGVT = Simulator_Graph_Validation_Tool( P = self.P, ASRI = self.ASRI, GI = self.GI, SLT = self.SLT )
		self.SCLT = Simulator_Create_Legend_Tool( P = self.P, FT = self.FT, SLT = self.SLT )

		self.SESRT_1 = Simulator_ES_Routes_Tool( P = self.P, ASRI = self.ASRI, RSI = self.RSI, ESI = self.ESI, SASGT = self.SASGT, SASGPT = self.SASGPT, SLT = self.SLT )
		self.SESTRT = Simulator_ES_Trace_Routes_Tool( P = self.P, FT = self.FT, ESI = self.ESI )

		self.SRTIT = Simulator_Relation_Type_Improver_Tool( P = self.P, FT = self.FT, ASRI = self.ASRI, RSI = self.RSI, ESI = self.ESI, SESRT_2 = self.SESRT_2, SESTRT = self.SESTRT, SLT = self.SLT )
		self.SRASGT = Simulator_Random_AS_Graph_Tool( P = self.P, FT = self.FT, SASGT = self.SASGT, SRTT = self.SRTT, SESTRT = self.SESTRT, SLT = self.SLT )

	def get_P2P_type( self ):
		return self.SLT.get_P2P_type()

	def get_C2P_type( self ):
		return self.SLT.get_C2P_type()

	def get_P2C_type( self ):
		return self.SLT.get_P2C_type()

	def get_S2S_type( self ):
		return self.SLT.get_S2S_type()

	def get_type( self, AS_graph = None, from_AS = None, to_AS = None ):
		return self.SLT.get_type( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

	def get_type_str( self, AS_graph = None, from_AS = None, to_AS = None, type = None ):
		return self.SLT.get_type_str( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, type = type )

	def get_types( self, AS_graph = None, route = None ):
		return self.SLT.get_types( AS_graph = AS_graph, route = route )

	def get_types_str( self, AS_graph = None, route = None, types = None ):
		return self.SLT.get_type_str( AS_graph = AS_graph, route = route, types = types )

	def get_database_tag( self, AS_graph = None, from_AS = None, to_AS = None ):
		return self.SLT.get_database_tag( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )
		
	def get_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None ):
		return self.SLT.get_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

	def flush( self ):
		self.flush_relations()
		self.flush_trace_routes()

	# Simulator_AS_graph_tool
	def init_AS_graph( self, use_AS_rank = False, overwrite = True, print_debug = False ):
		return self.SASGT.init_AS_graph( use_AS_rank = use_AS_rank, overwrite = overwrite, print_debug = print_debug )

	def add_AS( self, AS_graph = None, AS_number = None, print_debug = False ):
		return self.SASGT.add_AS( AS_graph = AS_graph, AS_number = AS_number, print_debug = print_debug )

	def add_link( self, AS_graph = None, from_AS = None, to_AS = None, type = None, LOCAL_PREFERENCE = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		return self.SASGT.add_link( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, type = type, LOCAL_PREFERENCE = LOCAL_PREFERENCE, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

	def add_peer( self, AS_graph = None, AS_number = None, peer = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		return self.SASGT.add_peer( AS_graph = AS_graph, AS_number = AS_number, peer = peer, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

	def add_customer( self, AS_graph = None, AS_number = None, customer = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		return self.SASGT.add_customer( AS_graph = AS_graph, AS_number = AS_number, customer = customer, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

	def add_provider( self, AS_graph = None, AS_number = None, provider = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		return self.SASGT.add_provider( AS_graph = AS_graph, AS_number = AS_number, provider = provider, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

	def add_sibling( self, AS_graph = None, AS_number = None, sibling = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		return self.SASGT.add_sibling( AS_graph = AS_graph, AS_number = AS_number, sibling = sibling, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

	def add_links( self, AS_graph = None, AS_number = None, peers = None, customers = None, providers = None, siblings = None, overwrite = True, create = True, database_tag = None, print_debug = False ):
		return self.SASGT.add_links( AS_number = AS_number, peers = peers, customers = customers, providers = providers, siblings = siblings, overwrite = overwrite, create = create, database_tag = database_tag, print_debug = print_debug )

	def add_AS_rank_links( self, AS_graph = None, overwrite = True, print_debug = False ):
		return self.SASGT.add_AS_rank_links( AS_graph = AS_graph, overwrite = overwrite, print_debug = print_debug )

	def add_possible_siblings( self, AS_graph = None, print_debug = None ):
		return self.SASGT.add_possible_siblings( AS_graph = AS_graph, print_debug = print_debug )

	def remove_unused_ASes( self, AS_graph = None ):
		return self.SASGT.remove_unused_ASes( AS_graph = AS_graph )

	def get_unique_paths( self, AS_graph = None ):
		return self.SASGT.get_unique_paths( AS_graph = AS_graph )

	def write_unique_paths( self, AS_graph = None ):
		return self.SASGT.write_unique_paths( AS_graph = AS_graph )

	def create_announcement( self, prefix = None, AS_number = None, good = None, print_debug = False ):
		return self.SASGT.create_announcement( prefix = prefix, AS_number = AS_number, good = good, print_debug = print_debug )

	def insert_announcement( self, AS_graph = None, announcement = None, print_debug = False ):
		return self.SASGT.insert_announcement( AS_graph = AS_graph, announcement = announcement, print_debug = print_debug )

	def insert_route( self, AS_graph = None, route = None, good = None, print_debug = False ):
		return self.SASGT.insert_route( AS_graph = AS_graph, route = route, good = good, print_debug = print_debug )	

	def iterate_AS_graph( self, AS_graph = None ):
		return self.SASGT.iterate_AS_graph( AS_graph = AS_graph )

	def set_type( self, AS_graph = None, from_AS = None, to_AS = None, type = None, update_LOCAL_PREFERENCE = True, update_reversed_link = True ):
		return self.SASGT.set_type( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, type = type, update_LOCAL_PREFERENCE = update_LOCAL_PREFERENCE, update_reversed_link = update_reversed_link )

	def set_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None, LOCAL_PREFERENCE = None ):
		return self.SASGT.set_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS, LOCAL_PREFERENCE = LOCAL_PREFERENCE )

	def get_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None ):
		return self.SASGT.get_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

	def reset_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None ):
		return self.SASGT.reset_LOCAL_PREFERENCE( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

	def reset_forwarding_rules( self, AS_graph = None, AS_number = None ):
		return self.SASGT.reset_forwarding_rules( AS_graph = AS_graph, AS_number = AS_number )

	def add_forwarding_rule( self, AS_graph = None, AS_number = None, from_type = None, to_type = None, allow = None ):
		return self.SASGT.add_forwarding_rule( AS_graph = AS_graph, AS_number = AS_number, from_type = from_type, to_type = to_type, allow = allow )

	def get_forwarding_rules( self, AS_graph = None, AS_number = None ):
		return self.SASGT.get_forwarding_rules( AS_graph = AS_graph, AS_number = AS_number )

	def print_forwarding_rules( self, AS_graph = None, AS_number = None ):
		return self.SASGT.print_forwarding_rules( AS_graph = AS_graph, AS_number = AS_number )
		
	def draw_AS_graph( self, AS_graph = None, draw_labels = True, file_name = None ):
		return self.SASGT.draw_AS_graph( AS_graph = AS_graph, draw_labels = draw_labels, file_name = file_name )

	def get_AS_graph_relations( self, AS_graph = None ):
		return self.SASGT.get_AS_graph_relations( AS_graph = AS_graph )

	def save_AS_graph( self, relative_folder_path = "", file_name = None, AS_graph = None, print_status = True ):
		return self.SASGT.save_AS_graph( relative_folder_path = relative_folder_path, file_name = file_name, AS_graph = AS_graph, print_status = print_status )

	def load_AS_graph( self, relative_folder_path = "", file_name = None, print_status = True ):
		return self.SASGT.load_AS_graph( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )

	# Simulator_Routing_Table_Tool
	def generate_routing_table( self, AS_graph = None, prefixes_do_not_overlap = False ):
		return self.SRTT.generate_routing_table( AS_graph = AS_graph, prefixes_do_not_overlap = prefixes_do_not_overlap )

	def save_routing_table( self, relative_folder_path = "", file_name = None, routing_table = None, print_status = False ):
		return self.SRTT.save_routing_table( relative_folder_path = relative_folder_path, file_name = file_name, routing_table = routing_table, print_status = print_status )

	def load_routing_table( self, relative_folder_path = "", file_name = None, print_status = True ):
		return self.SRTT.load_routing_table( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )

	def write_routing_table_statistics( self, routing_table = None ):
		return self.SRTT.write_routing_table_statistics( routing_table = routing_table )

	# Simulator_Routing_State_Tool
	def generate_routing_state( self, routing_table = None, calculate_passing_ASes = True ):
		return self.STST.generate_routing_state( routing_table = routing_table, calculate_passing_ASes = calculate_passing_ASes )

	def draw_routing_state( self, AS_graph = None, routing_table = None, routing_state = None, draw_unused_links = False, draw_labels = True, file_name = None ):
		return self.STST.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, draw_unused_links = draw_unused_links, draw_labels = draw_labels, file_name = file_name )

	def write_routing_state_statistics( self, routing_state = None ):
		self.STST.write_routing_state_statistics( routing_state = routing_state )

	def save_routing_state( self, relative_folder_path = "", file_name = None, routing_state = None, print_status = True ):
		return self.STST.save_routing_state( relative_folder_path = relative_folder_path, file_name = file_name, routing_state = routing_state, print_status = print_status )

	def load_routing_state( self, relative_folder_path = "", file_name = None, print_status = True ):
		return self.STST.load_routing_state( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )

	# Simulator_AS_Graph_Predictor_Tool
	def auto_fill( self, AS_graph = None, routes = None ):
		return self.SASGPT.auto_fill( AS_graph = AS_graph, routes = routes )

	# Simulator_ES_Routes_Tool
	def add_ES_links( self, AS_graph = None, RRC_range = None, RRC_number = None, time_interval = None, print_debug = False, print_server_response = False ):
		return self.SESRT_1.add_ES_links( AS_graph = AS_graph, RRC_range = RRC_range, RRC_number = RRC_number, time_interval = time_interval, print_debug = print_debug, print_server_response = print_server_response )

	def add_ES_routes( self, AS_graph = None, RRC_range = None, RRC_number = None, prefix = None, good_ASes = None, ignore_ASes = None, time_str = None, print_debug = False, print_server_response = False  ):
		return self.SESRT_1.add_ES_routes( AS_graph = AS_graph, RRC_range = RRC_range, RRC_number = RRC_number, prefix = prefix, good_ASes = good_ASes, ignore_ASes = ignore_ASes, time_str = time_str, print_debug = print_debug, print_server_response = print_server_response )

	# Simulator_ES_Trace_Routes_Tool
	def setup_trace_routes_index( self, print_server_response = False ):
		self.SESTRT.setup_trace_routes_index( print_server_response = False )

	def reset_trace_routes_index( self, print_server_response = False ):
		self.SESTRT.reset_trace_routes_index( print_server_response = False )

	def create_trace_routes_index( self, print_server_response = False ):
		self.SESTRT.create_trace_routes_index( print_server_response = False )

	def delete_trace_routes_index( self, print_server_response = False ):
		self.SESTRT.delete_trace_routes_index( print_server_response = False ) 

	def reset_ES_trace_routes_cache( self ):
		return self.reset_ES_trace_routes_cache()

	def get_trace_route_id( self, trace_route = None, source_IP = None, route = None, dest_IP = None, epoch_time = None, print_debug = False ):
		return self.SESTRT.get_trace_route_id( trace_route = None, path = path, source_IP = source_IP, dest_IP = dest_IP, epoch_time = epoch_time, print_debug = print_debug )

	def get_ES_trace_route( self, trace_route_id = None, print_debug = False, print_server_response = False ):
		return self.SESTRT.get_ES_trace_route( trace_route_id = trace_route_id, print_debug = print_debug, print_server_response = print_server_response )

	def create_trace_route( self, path = None, source_IP = None, dest_IP = None, epoch_time = None ):
		return self.SESTRT.create_trace_route( path = path, source_IP = source_IP, dest_IP = dest_IP, epoch_time = epoch_time )

	def add_ES_trace_route( self, trace_route = None, path = None, source_IP = None, dest_IP = None, epoch_time = None, overwrite = False, print_debug = False, print_server_response = False ):
		return self.SESTRT.add_ES_trace_route( trace_route = trace_route, path = path, source_IP = source_IP, dest_IP = dest_IP, epoch_time = epoch_time, print_debug = print_debug, print_server_response = print_server_response )

	def add_ES_trace_routes( self, trace_routes = None, print_debug = False ):
		return self.SESTRT.add_ES_trace_routes( trace_routes = trace_routes, print_debug = print_debug )

	def flush_ES_trace_routes( self, print_server_response = False ):
		return self.SESTRT.flush_ES_trace_routes( print_server_response = print_server_response )

	def sync_ES_trace_routes( self, print_server_response = False ):
		return self.SESTRT.sync_ES_trace_routes( print_server_response = print_server_response )

	def flush_ES_trace_routes_from_CSV( self, file_name = None, print_server_response = False, skip_counter = 0 ):
		return self.SESTRT.flush_ES_trace_routes_from_CSV( file_name = file_name, print_server_response = print_server_response, skip_counter = skip_counter )

	def load_ES_trace_routes( self, file_name = None ):
		return self.SESTRT.load_ES_trace_routes( file_name = file_name )

	def save_ES_trace_routes( self, file_name = None ):
		return self.SESTRT.save_ES_trace_routes( file_name = file_name )

	# Simulator_ES_Relations_Tool
	def setup_relations_index( self, print_server_response = False ):
		self.SESRT_2.setup_relations_index( print_server_response = False )

	def reset_relations_index( self, print_server_response = False ):
		self.SESRT_2.reset_relations_index( print_server_response = False )

	def create_relations_index( self, print_server_response = False ):
		self.SESRT_2.create_relations_index( print_server_response = False )

	def delete_relations_index( self, print_server_response = False ):
		self.SESRT_2.delete_relations_index( print_server_response = False )

	def reset_ES_relations_cache( self, print_debug = False ):
		return self.reset_ES_relations_cache( print_debug = print_debug )

	def add_AS_rank_relations( self, overwrite = True, create = True, print_server_response = False, print_debug = False ):
		return self.SESRT_2.add_AS_rank_relations( overwrite = overwrite, create = create, print_server_response = print_server_response, print_debug = print_debug )

	def get_relation_id( self, relation = None, from_AS = None, to_AS = None ):
		return self.SESRT_2.get_relation_id( relation = relation, from_AS = from_AS, to_AS = to_AS )

	def create_relation( self, from_AS = None, to_AS = None, type = None, source = None ):
		return self.SESRT_2.create_relation( from_AS = from_AS, to_AS = to_AS, type = type, source = source )

	def exist_ES_relation( self, relation_id = None, from_AS = None, to_AS = None, server_lookup = False, print_server_response = False, print_debug = False ):
		return self.SESRT_2.exist_ES_relation( relation_id = relation_id, from_AS = from_AS, to_AS = to_AS, server_lookup = server_lookup, print_server_response = print_server_response, print_debug = print_debug )

	def add_ES_relation( self, relation = None, from_AS = None, to_AS = None, type = None, source = None, overwrite = False, create = True, print_server_response = False, print_debug = False ):
		return self.SESRT_2.add_ES_relation( relation = relation, from_AS = from_AS, to_AS = to_AS, type = type, source = source, overwrite = overwrite, create = create, print_server_response = print_server_response, print_debug = print_debug )

	def add_ES_relations( self, relations = None, overwrite = False, create = True, print_debug = False, print_server_response = False):
		return self.SESRT_2.add_ES_relations( relations = relation, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response)

	def get_ES_relation( self, relation_id = None, from_AS = None, to_AS = None,  print_debug = False, print_server_response = False ):
		return self.SESRT_2.get_ES_relation( relation_id = relation_id, from_AS = from_AS, to_AS = to_AS, print_debug = print_debug, print_server_response = print_server_response ) 

	def sync_ES_relations( self, overwrite = False, print_server_response = False ):
		return self.SESRT_2.sync_ES_relations( overwrite = overwrite, print_server_response = print_server_response )

	def flush_ES_relations( self, print_server_response = False ):
		return self.SESRT_2.flush_ES_relations( print_server_response = print_server_response )

	def flush_AS_rank_relations( self, print_debug = None, print_server_response = False ):
		return self.SESRT_2.flush_AS_rank_relations( print_debug = print_debug, print_server_response = print_server_response )

	def load_ES_relations( self, file_name = None ):
		return self.SESRT_2.load_ES_relations( file_name = file_name )

	def save_ES_relations( self, file_name = None ):
		return self.SESRT_2.save_ES_relations( file_name = file_name )

	# Simulator_Relation_Type_Improver_Tool
	def reset_improver_relations( self, print_debug = False ):
		return self.SRTIT.reset_improver_relations( print_debug = print_debug )

	def reset_improver_trace_routes( self, print_debug = False ):		
		return self.SRTIT.reset_improver_trace_routes( print_debug = print_debug )

	def load_improver_relations( self, file_name = None, print_debug = False ):
		return self.SRTIT.load_improver_relations( file_name = file_name, print_debug = print_debug )

	def load_improver_missing_relations( self, file_name = None, print_debug = False ):
		return self.SRTIT.load_improver_missing_relations( file_name = file_name, print_debug = print_debug )

	def save_improver_relations( self, relations = None, file_name = None, print_debug = False ):
		return self.SRTIT.save_improver_relations( relations = relations, file_name = file_name, print_debug = print_debug )

	def save_improver_missing_relations( self, relations = None, file_name = None, print_debug = False ):
		return self.SRTIT.save_improver_missing_relations( relations = relations, file_name = file_name, print_debug = print_debug )

	def load_improver_trace_routes( self, file_name = None, print_debug = False ):
		return self.SRTIT.load_improver_trace_routes( file_name = file_name, print_debug = print_debug )

	def save_improver_trace_routes( self, file_name = None, print_debug = False ):
		return self.SRTIT.save_improver_trace_routes( file_name = file_name, print_debug = print_debug )

	def add_improver_relation( self, relation = None, print_debug = False ):
		return self.SRTIT.add_improver_relation( relation = relation, print_debug = print_debug )

	def add_improver_relations( self, relations = None, print_debug = False ):
		return self.SRTIT.add_improver_relations( relations = relations, print_debug = print_debug )

	def remove_improver_relation( self, relation = None, from_AS = None, to_AS = None, print_debug = False ):
		return self.SRTIT.remove_improver_relation( relation = relation, from_AS = from_AS, to_AS = to_AS, print_debug = print_debug )

	def add_improver_trace_route( self, trace_route = None, print_debug = False ):
		return self.SRTIT.add_improver_trace_route( trace_route = trace_route, print_debug = print_debug )

	def add_improver_trace_routes( self, trace_routes = None, print_debug = False ):
		return self.SRTIT.add_improver_trace_routes( trace_routes = trace_routes, print_debug = print_debug )

	def infer_relation( self, relation = None, print_debug = False, print_server_response = None, use_ES = True, no_output = False ):
		return self.SRTIT.infer_relation( relation = relation, print_debug = print_debug, print_server_response = print_server_response, use_ES = use_ES, no_output = no_output )

	def infer_relations( self, relations = None, print_debug = False, print_server_response = None, use_ES = True, no_output = False ):
		return self.SRTIT.infer_relations( relations = relations, print_debug = print_debug, print_server_response = print_server_response, use_ES = use_ES, no_output = no_output )

	def compute_missing_relations( self, mode = None, file_name = None, print_debug = False, print_server_response = False ):
		return self.SRTIT.compute_missing_relations( mode = mode, file_name = file_name, print_debug = print_debug, print_server_response = print_server_response )

	def compute_wrong_relations( self, mode = None, file_name = None, print_debug = False, print_server_response = False, mark_not_p2p = True, extensive_mode = False ):
		return self.SRTIT.compute_wrong_relations( mode = mode, file_name = file_name, print_debug = print_debug, print_server_response = print_server_response, mark_not_p2p = mark_not_p2p, extensive_mode = extensive_mode )

	# Simulator_Random_AS_Graph_Creator
	def generate_random_AS_graph( self, start_size = None, AS_multiplier = None, number_of_tiers = None, second_provider_probability = None, peer_probability = None ):
		return self.SRASGT.generate_random_AS_graph( start_size = start_size, AS_multiplier = AS_multiplier, number_of_tiers = number_of_tiers, second_provider_probability = second_provider_probability, peer_probability = peer_probability  )

	def generate_random_trace_routes( self, AS_graph = None ):
		return self.SRASGT.generate_random_trace_routes( AS_graph = AS_graph )

	# Simulator_Graph_Validation_Tool
	def validate_connectivity( self, AS_graph = None, AS_number = None, print_debug = False ):
		return self.SGVT.validate_connectivity( AS_graph = AS_graph, AS_number = AS_number, print_debug = print_debug )

	def compare_routing_states( self, routing_state_1 = None, routing_state_2 = None, include_no_routing_ASes = False ):
		return self.SGVT.compare_routing_states( routing_state_1 = routing_state_1, routing_state_2 = routing_state_2, include_no_routing_ASes = include_no_routing_ASes )

	def get_traces( self, routing_state_1 = None, routing_state_2 = None, source_AS = None, prefix = None ):
		return self.SGVT.get_traces( routing_state_1 = routing_state_1, routing_state_2 = routing_state_2, source_AS = source_AS, prefix = prefix )

	def write_traces( self, routing_state_1 = None, routing_state_2 = None, source_AS = None, prefix = None ):
		return self.SGVT.write_traces( routing_state_1 = routing_state_1, routing_state_2 = routing_state_2, source_AS = source_AS, prefix = prefix )
		
	def analyse_trace( self, prefix = None, trace = None, AS_graph = None, routing_state_1 = None, routing_state_2 = None ):
		return self.SGVT.analyse_trace( prefix = prefix, trace = trace, AS_graph = AS_graph, routing_state_1 = routing_state_1, routing_state_2 = routing_state_2 )

	# Simulator_Create_Legend_Tool
	def create_legend( self, relative_folder_path = "" ):
		return self.SCLT.create_legend( relative_folder_path = relative_folder_path )

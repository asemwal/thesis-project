import sys, os, datetime, time, urllib2, urllib, requests, json, hashlib, shutil, glob, gzip, bz2, struct, base64, wget, calendar, copy

sys.path.append( str(os.getcwd()) + "/../src" )

from termcolor import colored
from ES_local_interface import ES_Local_Interface
from ES_route_buffer import ES_Route_Buffer
from ES_put_buffer import ES_Put_Buffer
from ES_withdraw_tool import ES_Withdraw_Tool
from ES_state_change_tool import ES_State_Change_Tool
from ES_stats_tool import ES_Stats_Tool
from file_tool import File_Tool
from printer import Printer
from time_tool import Time_Tool
from are_you_sure_tool import Are_You_Sure_Tool
from clear_screen_tool import Clear_Screen_Tool

class ES_Interface():
	ESLI = None
	ESRB = None
	ESWT = None
	ESSTT = None
	ESST = None
	ESCB = None

	ROUTES = None

	P = None
	TT = None
	ARST = None

	interval_check_dict = None

	def __init__( self, P = None, include_state_change = True, include_withdraw = True, include_route = True, include_stats = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] ES_Interface: __init__: P is None", color = 'yellow' )

		self.P.write( "ES_Interface: Loading...", color = 'cyan' )
		self.ARST = Are_You_Sure_Tool( P = self.P )
		self.TT = Time_Tool( P = self.P )

		self.ROUTES = "bgp-routes"
		self.WITHDRAWS = "bgp-withdraws"

		self.ESLI = ES_Local_Interface( P = self.P )
		if include_stats is True:
			self.ESST = ES_Stats_Tool( P = self.P, ESLI = self.ESLI )

		if include_state_change is True:
			self.ESSTT = ES_State_Change_Tool( P = self.P, ESLI = self.ESLI )

		if include_route is True:
			self.ESRB = ES_Route_Buffer( P = self.P, ESLI = self.ESLI, index = self.ROUTES, print_run_time = False, print_debug = False )

		if include_withdraw is True:
			if include_route is False:
				self.ESRB = ES_Route_Buffer( P = self.P, ESLI = self.ESLI, index = self.ROUTES, print_run_time = False, print_debug = False )

			self.ESWT = ES_Withdraw_Tool( P = self.P, ESLI = self.ESLI, ESRB = self.ESRB, ESST = self.ESST, ROUTES = self.ROUTES, WITHDRAWS = self.WITHDRAWS )

		self.interval_check_dict = dict()
	
	#GETTERS
	def get_ES_Local_Interface( self ):
		return self.ESLI

	def get_ES_State_Change_Tool( self ):
		if self.ESSTT is not None:
			return self.ESSTT

	def get_ES_Route_Buffer( self ):
		if self.ESRB is not None:
			return self.ESRB

	def get_ES_Stats_Tool( self ):
		if self.ESST is not None:
			return self.ESST

	def get_ES_ROUTES_index_name( self ):
		return self.ROUTES

	def get_ES_WITHDRAWS_index_name( self ):
		return self.WITHDRAWS

	#GENERAL
	def __check_interval_exists( self, interval_str = None, print_server_response = False ):
		if interval_str in self.interval_check_dict:
			return

		self.interval_check_dict[interval_str] = None
		self.create_routes_index( interval_str = interval_str, print_server_response = print_server_response )

	def put_route( self, route = None, RRC_number = None ):
		[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = route['time'] )
		self.__check_interval_exists( interval_str = interval_str )

		if "withdraw" in route['mode']:
			if self.ESWT is not None:
				_id = str(route['start_IP']) + str(route['end_IP']) + str(route['dest_AS']) + str(route['time'])
				_id = hashlib.sha256( _id ).hexdigest()	

				route['RRC_number'] = RRC_number
				self.ESWT.put_route( route = route, _id = _id )
				return _id
		else:
			route['interval_start'] = interval_start
			route['interval_end'] = interval_end
			route['interval'] = interval_str
			route['RRC_number'] = RRC_number

			try:
				_id = str(route['source_AS']) + str(route['dest_AS']) + str(route['path']) + str(route['start_IP']) + str(route['end_IP']) 
				_id = str(_id) + str(route['interval_start']) + str(route['interval_end']) + str(route['RRC_number']) 
				route['_id'] = hashlib.sha256( _id ).hexdigest()	

				search_id = str(route['dest_AS']) + str(route['start_IP']) + str(route['end_IP']) + str(route['RRC_number']) 
				route['search_id'] = hashlib.sha256( search_id ).hexdigest()

				self.ESRB.put_route( route = route )
				return route['_id']
			except( TypeError ):
				self.P.write( "ES_Interface: put_route: TypeError...", color = 'red' )
				self.P.write_JSON( data_JSON = route )

		return None

	def kill_thread( self ):
		if self.ESRB is not None:
			self.ESRB.kill_thread()

	def flush( self ):
		self.P.write( "ES_Interface: flush")

		if self.ESSTT is not None:
			self.ESSTT.flush()

		if self.ESWT is not None:
			self.ESWT.flush()

		if self.ESRB is not None:
			self.ESRB.flush()

	#ES_STATS_TOOL
	def update_stats( self, RRC_number = None, mode = None, count = None, ms = None, ps = None, done = None, todo = None ):
		if self.ESST is not None:
			self.ESST.update_stats( RRC_number = RRC_number, mode = mode, count = count, ms = ms, ps = ps, done = done, todo = todo )

	def reset_stats_index( self ):
		if self.ESST is not None:
			self.ESST.reset_stats_index()

	#ES_ROUTE_BUFFER			
	def reset_routes_index( self, print_server_response = False ):
		self.P.write("ES_Interface: reset_routes_index: Do you want to delete ALL 'BGP-routes-*' ElasticSearch indexes?", color = 'red' )
		if self.ARST.ask_are_you_sure() is False:
			return

		return self.ESLI.delete_routes_index( interval_str = None, print_server_response = False ) 

	def create_routes_index( self, interval_str = None, print_server_response = False ):
		settings_JSON = dict()
		settings_JSON['number_of_shards'] = 2
		settings_JSON['number_of_replicas'] = 0
		settings_JSON['index.max_result_window'] = "100000"

		mappings_JSON = dict()
		mappings_JSON["search_id"] = dict()
		mappings_JSON["search_id"]["type"] = "keyword"
		mappings_JSON["start_IP"] = dict()
		mappings_JSON["start_IP"]["type"] = "ip"
		mappings_JSON["RRC_number"] = dict()
		mappings_JSON["RRC_number"]["type"] = "long"
		mappings_JSON["end_IP"] = dict()
		mappings_JSON["end_IP"]["type"] = "ip"
		mappings_JSON["prefix"] = dict()
		mappings_JSON["prefix"]["type"] = "text"
		mappings_JSON["source_AS"] = dict()
		mappings_JSON["source_AS"]["type"] = "integer"
		mappings_JSON["dest_AS"] = dict()
		mappings_JSON["dest_AS"]["type"] = "integer"
		mappings_JSON["interval_start"] = dict() 
		mappings_JSON["interval_start"]["type"] = "date"
		mappings_JSON["interval_start"]["format"] = "epoch_second"
		mappings_JSON["interval_end"] = dict() 
		mappings_JSON["interval_end"]["type"] = "date"
		mappings_JSON["interval_end"]["format"] = "epoch_second"
		mappings_JSON["path"] = dict()
		mappings_JSON["path"]["type"] = "keyword"
		mappings_JSON["path"]["norms"] = "false"
		mappings_JSON["alive"] = dict()
		mappings_JSON["alive"]["type"] = "keyword"
		mappings_JSON["alive"]["norms"] = "false"
		mappings_JSON["rib"] = dict()
		mappings_JSON["rib"]["type"] = "keyword"
		mappings_JSON["rib"]["norms"] = "false"

		data_ES = self.ESLI.create_index( index = self.ROUTES + interval_str, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )

		if "status" in data_ES and data_ES['status'] == 400:
			self.P.write( "ES_Interface: create_routes_index: index " + str(self.ROUTES + interval_str) + " already exists...")
		else:
			self.P.write( "ES_Interface: create_routes_index: create index " + str(self.ROUTES + interval_str) + "...")

	def delete_routes_index( self, interval_str = None, print_server_response = False ):
		if interval_str is not None:
			index = self.ROUTES + str(interval_str)
		else:
			index = self.ROUTES + "_*"

		self.P.write("ES_Interface: delete_routes_index: Do you want to delete (ALL) ElasticSearch index(es)'" + str(index) + "'?", color = 'red' )
		if self.ARST.ask_are_you_sure() is False:
			return

		if self.ESLI.exists_index( index = index ) is False:
			self.P.write("ES_Interface: delete_routes_index: ElasicSearch index '" + str(index) + "' does not exists" )

		self.P.write("ES_Interface: delete_routes_index: ElasticSearch index '" + str(index) + "' deleted" )
		return self.ESLI.delete_index( index = index, print_server_response = True ) 

	def reset_route_buffer_cache( self ):
		return self.ESRB.reset_route_buffer_cache()

	#ES_WITHDRAW_TOOL
	def setup_withdraws_index( self, print_server_response = False ):
		if self.ESWT is not None:
			self.ESWT.setup_withdraws_index( print_server_response = print_server_response )

	def create_withdraws_index( self, print_server_response = False ):
		if self.ESWT is not None:
			self.ESWT.create_withdraws_index( print_server_response = print_server_response )

	def delete_withdraws_index( self, print_server_response = False ):
		if self.ESWT is not None:
			self.ESWT.delete_withdraws_index( print_server_response = print_server_response )

	def process_withdraws( self, RRC_number = None, RRC_range = None, time_interval = None ):
		if self.ESWT is not None:
			self.ESWT.process_withdraws( RRC_number = RRC_number, RRC_range = RRC_range, time_interval = time_interval )

	#ES_STATE_CHANGE_TOOL
	def setup_state_change_index( self, print_server_response = False ):
		if self.ESSTT is not None:
			self.ESSTT.setup_state_change_index( print_server_response = print_server_response )

	def create_state_change_index( self, print_server_response = False ):
		if self.ESSTT is not None:
			self.ESSTT.create_state_change_index( print_server_response = print_server_response)

	def delete_state_change_index( self, print_server_response = False ):
		if self.ESSTT is not None:
			self.ESSTT.delete_state_change_index( print_server_response = print_server_response )

	def put_state_change( self, peer_AS = None, time_stamp = None, new_state = None ):
		if self.ESSTT is not None:
			self.ESSTT.put_state_change( peer_AS = peer_AS, time_stamp = time_stamp, new_state = new_state )

	#ES_LOCAL_INTERFACE
	def exists_index( self, index = None, print_server_response = False ):
		return self.ESLI.exists_index( index = index, print_server_response = print_server_response )

	def get_index( self, index = None, print_server_response = False ):	
		return self.ESLI.get_index( index = index, print_server_response = print_server_response )

	def msearch( self, index = None, type = None, data_list = list(), filter_path = None, print_server_response = False ):
		return self.ESLI.msearch( index = index, type = type, data_list = data_list, filter_path = filter_path, print_server_response = print_server_response )

	def msearch_thread( self, index = None, type = None, data_list = list(), max_number_of_threads = 10, filter_path = None, print_server_response = False ):
		return self.ESLI.msearch_thread( index = index, type = type, data_list = data_list, max_number_of_threads = max_number_of_threads, filter_path = filter_path, print_server_response = print_server_response )

	def mget_ids( self, index = None, type = None, ids = None, filter_path = None, source_filtering = None, print_server_response = False ):
		return self.ESLI.mget_ids( index = index, type = type, ids = ids, filter_path = filter_path, source_filtering = source_filtering, print_server_response = print_server_response )

	def mget( self, data_list = None, filter_path = None, source_filtering = None, print_server_response = False ):
		return self.ESLI.mget( data_list = data_list, filter_path = filter_path, source_filtering = source_filtering, print_server_response = print_server_response )

	def get_id( self, index = None, type = None, id = None, filter_path = None, print_server_response = False ):
		return self.ESLI.get_id( index = index, id = id, filter_path = filter_path, print_server_response = print_server_response )

	def post_bulk_thread( self, index = None, type = None, data_list = list(), max_number_of_threads = 3, print_server_response = False, print_debug = False ):
		return self.ESLI.post_bulk_thread( index = index, type = type, data_list = data_list, max_number_of_threads = max_number_of_threads, print_server_response = print_server_response )

	def post_bulk( self, index = None, type = None, data_list = list(), print_server_response = False ):
		return self.ESLI.post_bulk( index = index, type = type, data_list = data_list, print_server_response = print_server_response )

	def search( self, index = None, type = None, source_filtering = None, data_JSON = None, filter_path = None, scroll = None, print_server_response = False ):
		return self.ESLI.search( index = index, type = type, source_filtering = source_filtering, data_JSON = data_JSON, filter_path = filter_path, scroll = scroll, print_server_response = print_server_response )

	def scroll( self, index = None, scroll = None, scroll_id = None, print_server_response = False ):
		return self.ESLI.scroll( index = index, scroll = scroll, scroll_id = scroll_id, print_server_response = print_server_response )

	def update_id( self, index = None, type = None, id = None, data_JSON = None, print_server_response = False ):
		return self.ESLI.update_id( index = index, type = type, id = id, data_JSON = data_JSON, print_server_response = print_server_response )

	def put_id( self, index = None, type = None, id = None, data_JSON = None, print_server_response = False ):
		return self.ESLI.put_id( index = index, id = id, data_JSON = data_JSON, print_server_response = print_server_response )

	def delete_id( self, index = None, type = None, id = None, print_server_response = False ):
		return self.ESLI.delete_id( index = index, type = type, id = id, print_server_response = print_server_response )

	def delete_index( self, index = None, print_server_response = False ):
		return self.ESLI.delete_index( index = index, print_server_response = print_server_response )

	def update_index( self, index = None, type = None, mappings_JSON = None, print_server_response = False ):
		return self.ESLI.create_index( index = index, type = type, mappings_JSON = mappings_JSON, print_server_response = print_server_response )

	def create_index( self, index = None, type = None, mappings_JSON = None, settings_JSON = None, print_server_response = False ):
		return self.ESLI.create_index( index = index, type = type, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )

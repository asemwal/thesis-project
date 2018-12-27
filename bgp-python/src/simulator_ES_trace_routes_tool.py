import json, requests, os, sys, hashlib, copy, time

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from ask_tool import Ask_Tool
from file_tool import File_Tool
from are_you_sure_tool import Are_You_Sure_Tool
from time_tool import Time_Tool
from AS_rank_interface import AS_Rank_Interface
from ES_interface import ES_Interface

from simulator_link_types import Simulator_Link_Types

class Simulator_ES_Trace_Routes_Tool():
	P = None
	AT = None
	ARST = None
	ESI = None

	TRACE_ROUTES = None

	changed_dict = None
	found_dict = None
	not_found_dict = None

	def __init__( self, P = None, FT = None, ESI = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_ES_trace_Routes_Tool: __init__ : P is None" )

		self.P.write( "Simulator_ES_trace_Routes_Tool: Loading...", color = 'cyan' )
		self.AT = Ask_Tool( P = self.P )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_ES_trace_Routes_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_ES_trace_Routes_Tool" )

		self.ARST = Are_You_Sure_Tool( P = self.P, program_name = "Simulator_ES_trace_Routes_Tool" )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "Simulator_ES_trace_Routes_Tool: __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False, include_coverage = False, include_raw = False )

		self.TRACE_ROUTES = "bgp-trace-routes"

		self.setup_trace_routes_index()
		self.reset_ES_trace_routes_cache()

	def reset_ES_trace_routes_cache( self ):
		self.changed_dict = dict()
		self.found_dict = dict()
		self.not_found_dict = dict()

	def setup_trace_routes_index( self, print_server_response = False ):
		if self.ESI.exists_index( index = self.TRACE_ROUTES ) is False:
			self.P.write( "Simulator_ES_trace_Routes_Tool: setup_ES_trace_routes_index: ElasticSearch index '" + str(self.TRACE_ROUTES) + "' does not exists, creating..." )
			self.create_trace_routes_index( print_server_response = print_server_response )

	def reset_trace_routes_index( self, print_server_response = False ):
		self.delete_trace_routes_index( print_server_response = print_server_response )
		self.create_trace_routes_index( print_server_response = print_server_response )

	def create_trace_routes_index( self, print_server_response = False ):
		settings_JSON = dict()
		settings_JSON['number_of_shards'] = 2
		settings_JSON['number_of_replicas'] = 0
		settings_JSON['index.max_result_window'] = "100000"

		mappings_JSON = dict()
		mappings_JSON["path"] = dict()
		mappings_JSON["path"]["type"] = "integer"
		mappings_JSON["source_IP"] = dict()
		mappings_JSON["source_IP"]["type"] = "ip"
		mappings_JSON["dest_IP"] = dict()
		mappings_JSON["dest_IP"]["type"] = "ip"
		mappings_JSON["epoch_time"] = dict()
		mappings_JSON["epoch_time"]["type"] = "date"
		mappings_JSON["epoch_time"]["format"] = "epoch_second"
		mappings_JSON["relation_ids"] = dict()
		mappings_JSON["relation_ids"]["type"] = "text"

		data_ES = self.ESI.create_index( index = self.TRACE_ROUTES, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )

		if "status" in data_ES and data_ES['status'] == 400:
			self.P.write( "Simulator_ES_trace_Routes_Tool: create_ES_trace_routes_index: ElasticSearch index '" + self.TRACE_ROUTES + "' already exists" )
		else:
			self.P.write( "Simulator_ES_trace_Routes_Tool: create_ES_trace_routes_index: ElasticSearch index '" + self.TRACE_ROUTES + "' created" )

	def delete_trace_routes_index( self, print_server_response = False ):
		self.P.write("Simulator_ES_trace_Routes_Tool: delete_ES_trace_routes_index: Do you want to delete ElasticSearch index '" + self.TRACE_ROUTES + "'?", color = 'red' )
		if self.ARST.ask_are_you_sure() is False:
			return

		if self.ESI.exists_index( index = self.TRACE_ROUTES ) is False:
			self.P.write("Simulator_ES_trace_Routes_Tool: delete_ES_trace_routes_index: ElasicSearch index '" + str(self.TRACE_ROUTES) + "' does not exists" )
		else:
			self.P.write("Simulator_ES_trace_Routes_Tool: delete_ES_trace_routes_index: ElasticSearch index '" + str(self.TRACE_ROUTES) + "' deleted" )
			return self.ESI.delete_index( index = self.TRACE_ROUTES, print_server_response = print_server_response ) 

	def __get_ES_trace_route( self, _id = None, print_debug = False, print_server_response = False ):
		data_ES = self.ESI.get_id( index = self.TRACE_ROUTES, id = _id, print_server_response = print_server_response )

		if "found" not in data_ES:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: __get_ES_trace_route: trace_route_id = " + str(_id) + ": 'found' not in data_ES" )
			self.P.write_JSON( data_ES )
			return None

		if data_ES['found'] is False:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_trace_Routes_Tool: __get_ES_trace_route: trace_route_id = " + str(_id) + ": not found in ElasticSearch index bgp-trace-routes" )

			self.not_found_dict[_id] = None
		elif data_ES['found'] is True:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_trace_Routes_Tool: __get_ES_trace_route: trace_route_id = " + str(_id) + ": retrieved from ElasticSearch index bgp-trace-routes" )

			self.found_dict[_id] = data_ES['_source']

	def get_trace_route_id( self, trace_route = None, path = None, source_IP = None, dest_IP = None, epoch_time = None, print_debug = False ):
		if trace_route is not None:
			source_IP = trace_route['source_IP']
			path = trace_route['path']
			dest_IP = trace_route['dest_IP']
			epoch_time = trace_route['epoch_time']
	
		if source_IP is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: get_trace_route_id: source_IP is None" )
			return None

		if path is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: get_trace_route_id: path is None" )
			return None

		if dest_IP is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: get_trace_route_id: dest_IP is None" )
			return None

		if epoch_time is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: get_trace_route_id: epoch_time is None" )
			return None

		if print_debug:
			self.P.write_debug( "Simulator_ES_trace_Routes_Tool: get_trace_route_id: start" )

		_id = str( source_IP ) + str( path ) + str( dest_IP ) + str( epoch_time )
		_id = hashlib.sha256( _id ).hexdigest()	

		return _id

	def get_ES_trace_route( self, trace_route_id = None, print_debug = False, print_server_response = False ):
		if trace_route_id is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: get_ES_trace_route: _id is None" )
			return None  

		_id = trace_route_id

		if print_debug:
			self.P.write_debug( "Simulator_ES_trace_Routes_Tool: get_ES_trace_route: _id = " + str(trace_route_id) + ": start" )

		if _id not in self.found_dict and _id not in self.not_found_dict:
			self.__get_ES_trace_route( _id = trace_route_id, print_debug = print_debug, print_server_response = print_server_response )

		if _id in self.not_found_dict:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_trace_Routes_Tool: get_ES_trace_route: _id = " + str(trace_route_id) + ", relation_id = " + str(relation_id) + ": not in found_dict" )
			
			return None
		elif _id in self.found_dict:	
			return self.found_dict[trace_route_id]
		else:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: get_ES_trace_route: loop error" )
			return None

	def create_trace_route( self, path = None, source_IP = None, dest_IP = None, epoch_time = None ):
		if path is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: path is None" )
			return None

		if source_IP is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: source_IP is None" )
			return None

		if dest_IP is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: dest_IP is None" )
			return None

		if epoch_time is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: epoch_time is None" )
			return None 

		trace_route = dict()
		trace_route['source_IP'] = source_IP
		trace_route['dest_IP'] = dest_IP
		trace_route['path'] = path
		trace_route['epoch_time'] = epoch_time
		trace_route['relation_ids'] = list()

		return trace_route

	def add_ES_trace_route( self, trace_route = None, path = None, source_IP = None, dest_IP = None, epoch_time = None, overwrite = False, create = True, print_debug = False, print_server_response = False ):
		if trace_route is None:
			if path is None:
				self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: path is None" )
				return None

			if source_IP is None:
				self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: source_IP is None" )
				return None

			if dest_IP is None:
				self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: dest_IP is None" )
				return None

			if epoch_time is None:
				self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: epoch_time is None" )
				return None 

		if print_debug is True:
			self.P.write_debug( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: start" )

		if trace_route is None:
			trace_route = dict()
			trace_route['source_IP'] = source_IP
			trace_route['dest_IP'] = dest_IP
			trace_route['path'] = path
			trace_route['epoch_time'] = epoch_time
			trace_route['relation_ids'] = list()

		_id = self.get_trace_route_id( source_IP = trace_route['source_IP'], dest_IP = trace_route['dest_IP'], path = trace_route['path'], epoch_time = trace_route['epoch_time'] )
		
		if "path" not in trace_route:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: 'path' not in trace_route:" )
			return None

		if "source_IP" not in trace_route:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: 'source_IP' not in trace_route" )
			return None

		if "dest_IP" not in trace_route:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: 'dest_IP' not in trace_route" )
			return None

		if "epoch_time" not in trace_route:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: 'epoch_time' not in trace_route" )
			return None 

		if overwrite is True:
			self.found_dict[_id] = trace_route
			self.changed_dict[_id] = trace_route

			if _id in self.not_found_dict:
				del self.not_found_dict[_id]

			if print_debug:
				self.P.write_debug( "Simulator_ES_Relations_Tool: Simulator_ES_trace_Routes_Tool: added/overwritten trace_route_id = " + str(_id) + ":" )
				self.P.write_JSON( trace_route )

			return _id

		if _id not in self.found_dict and _id not in self.not_found_dict:
			self.__get_ES_trace_route( _id = _id, print_debug = print_debug, print_server_response = print_server_response )

		if _id in self.found_dict:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: trace_route_id = " + str(_id) + ": overwrite is False" )
			
			return _id
		elif _id in self.not_found_dict and create is False:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: trace_route_id = " + str(_id) + ": create is False" )
			
			return None
		elif _id in self.not_found_dict and create is True:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: added trace_route_id = " + str(_id) + ":" )
				self.P.write_JSON( trace_route )
			
			self.found_dict[ _id ] = trace_route
			self.changed_dict[ _id ] = trace_route
			del self.not_found_dict[ _id ]
			
			return _id
		else:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_route: loop error" )

	def add_ES_trace_routes( self, trace_routes = None, print_debug = False ):
		if trace_routes is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: add_ES_trace_routes: trace_routes is None" )
			return None

		counter = len(trace_routes)
		for trace_route in trace_routes:
			counter -= 1
			if counter % 1000 == 0:
				self.P.rewrite( "\tSimulator_ES_trace_Routes_Tool: add_ES_trace_routes: " + str(int(counter/1000)) + "k trace routes left" )

			self.add_ES_trace_route( trace_route = trace_route )

	def sync_ES_trace_routes( self, print_server_response = False ):
		self.P.write( "Simulator_ES_trace_Routes_Tool: sync_ES_trace_routes: start", color = 'green' )

		size = 8000

		data_JSON = dict()
		data_JSON['size'] = size
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		data_ES = self.ESI.search( index = self.TRACE_ROUTES, data_JSON = data_JSON, scroll = "1m", print_server_response = print_server_response )
		scroll_id = data_ES['_scroll_id']
		
		for data in data_ES['hits']['hits']:
			_id = data['_id']
			trace_route = data['_source']

			self.found_dict[_id] = trace_route

			if _id in self.not_found_dict:
				del self.not_found_dict[_id]

		amount_left = data_ES['hits']['total'] - size

		finished = False
		while finished is False:
			if amount_left < 0:
				amount_left = 0

			self.P.rewrite( "\tSimulator_ES_trace_Routes_Tool: sync_ES_trace_routes: " + str(int(amount_left/1000)) + "k relations left" )
			data_ES = self.ESI.scroll( index = self.TRACE_ROUTES, scroll = "1m", scroll_id = scroll_id, print_server_response = print_server_response )
			
			if len( data_ES['hits']['hits'] ) == 0:
				finished = True

			for data in data_ES['hits']['hits']:
				_id = data['_id']
				trace_route = data['_source']

				self.found_dict[_id] = trace_route

				if _id in self.not_found_dict:
					del self.not_found_dict[_id]

			amount_left -= size

		self.P.write( "Simulator_ES_trace_Routes_Tool: sync_ES_trace_routes: done!" )

	def flush_ES_trace_routes( self, print_server_response = False ):    
		self.P.write( "\tSimulator_ES_trace_Routes_Tool: flush_ES_trace_routes: start", color = 'green' )

		data_list = list()
		length = len(self.changed_dict)

		counter = len(self.changed_dict)
		for _id in self.changed_dict:
			counter -= 1
			if counter % 100 == 0:
				self.P.rewrite( "Simulator_ES_trace_Routes_Tool: flush_ES_trace_routes: preparing flush: " + str(counter/1000) + "k items left              " )

			data_JSON_index = dict()
			data_JSON_index['create'] = dict()
			data_JSON_index['create']['_id'] = _id

			data_list.append( json.dumps( data_JSON_index ) )
			data_list.append( json.dumps( self.changed_dict[_id] ) )

		data_ES = self.ESI.post_bulk_thread( index = self.TRACE_ROUTES, data_list = data_list, print_server_response = print_server_response, max_number_of_threads = 4 )
		self.changed_dict = dict()

		self.P.write( "\tSimulator_ES_trace_Routes_Tool: flush: updated " + str(length) + " item(s)" )

	def flush_ES_trace_routes_from_CSV( self, file_name = None, print_server_response = False, skip_counter = 0 ):
		if file_name is None:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: flush_ES_trace_routes_from_CSV: CSV_file_name is None" )
			self.P.write( "Simulator_Relation_Type_Improver_Tool: place CSV file in /data/simulator" )
			self.P.write( "Simulator_Relation_Type_Improver_Tool: enter file name including extension" )

			file_name = self.AT.ask( question = "File Name: " )

		if skip_counter is None:
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: flush_ES_trace_routes_from_CSV: skip_counter is None" )
			self.P.write_warning( "Simulator_Relation_Type_Improver_Tool: flush_ES_trace_routes_from_CSV: setting skip_counter to 0" )
			skip_counter = 0

		self.flush_ES_trace_routes()

		rows = self.FT.load_CSV_file( file_name = file_name )

		if rows is None:
			return

		counter = 0
		flush_counter = 0
		for row in rows:
			counter += 1
			flush_counter += 1

			if counter % 10000 == 0:
				self.P.rewrite( "\tSimulator_Relation_Type_Improver_Tool: flush_ES_trace_routes_from_CSV: " + str(counter/1000) + "k trace routes processed          " )

				if flush_counter  > 100000:
					self.flush_ES_trace_routes( print_server_response = print_server_response )

					self.changed_dict = dict()
					self.found_dict = dict()
					self.not_found_dict = dict()

					flush_counter = 0

			if counter < skip_counter:
				continue

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

			self.add_ES_trace_route( path = path, source_IP = "0.0.0.0", dest_IP = "0.0.0.0", epoch_time = epoch_time, overwrite = True, create = True, print_debug = False )
		

	def load_ES_trace_routes( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "Simulator_ES_trace_Routes_Tool: load_ES_trace_routes: file_name is None" )
			return None

		file_name = file_name.split('.')[0] + ".trace_routes"
		file_path = self.FT.get_file_path( file_name = file_name )

		if self.FT.check_file_exists( file_name = file_name ) is False:
			self.P.write_warning( "Simulator_ES_trace_Routes_Tool: load_ES_trace_routes: " + str(file_path) + " not found" )
		elif self.FT.check_checksum( file_name = file_name ) is True:
			data_JSON = self.FT.load_JSON_file( file_name = file_name, print_status = True )

			self.found_dict = data_JSON
		else:
			self.P.write_warning( "tSimulator_ES_trace_Routes_Tool: load_ES_trace_routes: " + str(file_path) + ": checksum incorrect or missing" )

	def save_ES_trace_routes( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "tSimulator_ES_trace_Routes_Tool: save_ES_trace_routes: file_name is None" )
			return None

		self.P.write( "tSimulator_ES_trace_Routes_Tool: save_ES_trace_routes: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".trace_routes"

		self.FT.save_JSON_file( data_JSON = self.found_dict, file_name = file_name, print_status = True )
		self.FT.create_checksum( file_name = file_name, print_status = True )




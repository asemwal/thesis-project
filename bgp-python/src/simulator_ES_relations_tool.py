import json, requests, os, sys, hashlib, copy, time

from netaddr import *
from collections import OrderedDict

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from alive_tool import Alive_Tool
from file_tool import File_Tool
from are_you_sure_tool import Are_You_Sure_Tool
from time_tool import Time_Tool
from AS_rank_interface import AS_Rank_Interface
from ES_interface import ES_Interface

from simulator_link_types import Simulator_Link_Types

class Simulator_ES_Relations_Tool():
	P = None
	FT = None
	ESI = None
	ASRI = None
	ARST = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	RELATIONS = None

	found_dict = None
	not_found_dict = None

	def __init__( self, P = None, FT = None, ASRI = None, ESI = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_ES_Relations_Tool: __init__ : P is None" )

		self.P.write( "Simulator_ES_Relations_Tool: Loading...", color = 'cyan' )
		self.ARST = Are_You_Sure_Tool( P = self.P, program_name = "Simulator_ES_Relations_Tool" )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_ES_Relations_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_ES_Relations_Tool" )

		if ASRI is not None:
			self.ASRI = ASRI
		else:
			self.P.write_warning( "Simulator_ES_Relations_Tool: __init__ : ASRI is None" )
			self.ASRI = AS_Rank_Interface( P = self.P )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "Simulator_ES_Relations_Tool: __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False, include_coverage = False, include_raw = False )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_ES_Relations_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

		self.RELATIONS = "bgp-relations"

		self.setup_relations_index()

		self.reset_ES_relations_cache()

	def reset_ES_relations_cache( self, print_debug = False ):
		if print_debug is True:
			self.P.write( "Simulator_ES_Relations_Tool: reset_ES_relations_cache: start" ) 

		self.found_dict = dict()
		self.not_found_dict = dict()

	def setup_relations_index( self, print_server_response = False ):
		if self.ESI.exists_index( index = self.RELATIONS ) is False:
			self.P.write( "Simulator_ES_Relations_Tool: setup_relations_index: ElasticSearch index '" + str(self.RELATIONS) + "' does not exists, creating..." )
			self.create_relations_index( print_server_response = print_server_response )

	def get_relation_id( self, relation = None, from_AS = None, to_AS = None ):
		if relation is not None:
			pass
		elif from_AS is not None and to_AS is not None:
			relation = dict()
			relation['from_AS'] = from_AS
			relation['to_AS'] = to_AS
		elif from_AS is not None or to_AS is not None:
			self.P.write_error( "Simulator_ES_Relations_Tool: get_relation_id: from_AS and to_AS are not all not None" )
			return None
		else:
			self.P.write_error( "Simulator_ES_Relations_Tool: get_relation_id: relation is None" )

		_id = str( relation['from_AS'] ) + "-" + str( relation['to_AS'] )
		_id = hashlib.sha256( _id ).hexdigest()	

		return _id

	def reset_relations_index( self, print_server_response = False ):
		self.delete_relations_index( print_server_response = print_server_response )
		self.create_relations_index( print_server_response = print_server_response )

	def create_relations_index( self, print_server_response = False ):
		settings_JSON = dict()
		settings_JSON['number_of_shards'] = 2
		settings_JSON['number_of_replicas'] = 0
		settings_JSON['index.max_result_window'] = "100000"

		mappings_JSON = dict()
		mappings_JSON["from_AS"] = dict()
		mappings_JSON["from_AS"]["type"] = "long"
		mappings_JSON["to_AS"] = dict()
		mappings_JSON["to_AS"]["type"] = "long"
		mappings_JSON["type"] = dict()
		mappings_JSON["type"]["type"] = "text"
		mappings_JSON["source"] = dict()
		mappings_JSON["source"]["type"] = "integer"
		mappings_JSON["trace_route_ids"] = dict()
		mappings_JSON["trace_route_ids"]["type"] = "text"
		mappings_JSON["p2p"] = dict()
		mappings_JSON["p2p"]["type"] = "integer"
		mappings_JSON["c2p"] = dict()
		mappings_JSON["c2p"]["type"] = "integer"
		mappings_JSON["p2c"] = dict()
		mappings_JSON["p2c"]["type"] = "integer"
		mappings_JSON["s2s"] = dict()
		mappings_JSON["s2s"]["type"] = "integer"
		
		data_ES = self.ESI.create_index( index = self.RELATIONS, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )

		if "status" in data_ES and data_ES['status'] == 400:
			self.P.write( "Simulator_ES_Relations_Tool: create_relations_index: ElasticSearch index '" + self.RELATIONS + "' already exists" )
		else:
			self.P.write( "Simulator_ES_Relations_Tool: create_relations_index: ElasticSearch index '" + self.RELATIONS + "' created" )

	def delete_relations_index( self, print_server_response = False ):
		self.P.write("Simulator_ES_Relations_Tool: delete_relations_index: Do you want to delete ElasticSearch index '" + self.RELATIONS + "'?", color = 'red' )
		if self.ARST.ask_are_you_sure() is False:
			return

		if self.ESI.exists_index( index = self.RELATIONS ) is False:
			self.P.write("Simulator_ES_Relations_Tool: delete_relations_index: ElasicSearch index '" + str(self.RELATIONS) + "' does not exists" )
		else:
			self.P.write("Simulator_ES_Relations_Tool: delete_relations_index: ElasticSearch index '" + str(self.RELATIONS) + "' deleted" )
			return self.ESI.delete_index( index = self.RELATIONS, print_server_response = print_server_response ) 

	def add_AS_rank_relations( self, overwrite = True, create = True, print_debug = False , print_server_response = False ):
		self.P.write( "Simulator_ES_Relations_Tool: add_AS_rank_relations: start", color = 'green' )

		if overwrite is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: add_AS_rank_relations: overwrite is None" )
			return None

		if create is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: add_AS_rank_relations: create is None" )
			return None

		AS_numbers = self.ASRI.get_all_saved_ASes()
		
		cache = dict()
		counter = len( AS_numbers )
		for from_AS in AS_numbers:
			counter -= 1
			if counter % 100 == 0:
				self.P.rewrite( "Simulator_ES_Relations_Tool: add_AS_rank_relations: " + str(counter/1000) + "k ASes left, added " + str(len(self.found_dict)/1000) + "k relations" )

			for to_AS in self.ASRI.get_peers( AS_number = from_AS ):
				self.add_ES_relation( from_AS = from_AS, to_AS = to_AS, type = self.TYPE_P2P, source = 0, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )	

			for to_AS in self.ASRI.get_customers( AS_number = from_AS ):
				self.add_ES_relation( from_AS = from_AS, to_AS = to_AS, type = self.TYPE_P2C, source = 0, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )	

			for to_AS in self.ASRI.get_providers( AS_number = from_AS ):
				self.add_ES_relation( from_AS = from_AS, to_AS = to_AS, type = self.TYPE_C2P, source = 0, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )	

		self.P.rewrite( "Simulator_ES_Relations_Tool: add_AS_rank_relations: done!                                " )	

	def create_relation( self, from_AS = None, to_AS = None, type = None, source = None ):
		if from_AS is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: create_relation: from_AS is None" )
			return None

		if to_AS is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: create_relation: to_AS is None" )
			return None

		relation = dict()
		relation['from_AS'] = from_AS
		relation['to_AS'] = to_AS
		
		if type is not None:
			relation['type'] = int(type)
		else:
			relation['type'] = -1

		if source is not None:
			relation['source'] = str(source)
		else:
			relation['source'] = ""

		relation['source'] = source
		relation['p2p'] = list()
		relation['c2p'] = list()
		relation['p2c'] = list()
		relation['s2s'] = list()
		relation['trace_route_ids'] = list()

		return relation

	def add_ES_relation( self, relation = None, from_AS = None, to_AS = None, type = None, source = None, overwrite = False, create = True,  print_debug = False, print_server_response = False):
		if relation is not None:
			pass
		elif from_AS is not None and to_AS is not None and type is not None and source is not None:
			relation = dict()
			relation['from_AS'] = from_AS
			relation['to_AS'] = to_AS
			relation['type'] = type
			relation['source'] = source
			relation['p2p'] = list()
			relation['c2p'] = list()
			relation['p2c'] = list()
			relation['s2s'] = list()
			relation['trace_route_ids'] = list()
		elif from_AS is not None or to_AS is not None or type is not None or source is not None:
			self.P.write_error( "Simulator_ES_Relations_Tool: add_ES_relation: from_AS, to_AS, type and source are not all not None" )
			return None
		else:
			self.P.write_error( "Simulator_ES_Relations_Tool: add_ES_relation: relation is None" )
			return None

		if print_debug is True:
			self.P.write_debug( "Simulator_ES_Relations_Tool: add_ES_relation: start" )

		_id = self.get_relation_id( relation = relation )

		from_AS = relation['from_AS']
		to_AS = relation['to_AS']
		type = relation['type']
		source = relation['source']

		if overwrite is True:
			self.found_dict[_id] = relation

			if _id in self.not_found_dict:
				del self.not_found_dict[_id]

			if print_debug:
				type_str = self.SLT.get_type_str( type = type )
				self.P.write_debug( "Simulator_ES_Relations_Tool: add_ES_relation: added/overwritten AS" + str(from_AS) + " - AS" + str(to_AS) + ", type = " + str(type_str) + ", source = " + str(source) )

			return _id

		print overwrite

		if _id not in self.found_dict and _id not in self.not_found_dict:
			self.__get_relation( _id = _id, from_AS = from_AS, to_AS = to_AS )

		if _id in self.found_dict:
			if print_debug:
				type_str = self.SLT.get_type_str( type = type )
				self.P.write_debug( "Simulator_ES_Relations_Tool: add_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ", type = " + str(type_str) + ", source = " + str(source) + ": overwrite is False" )

			return _id
		elif _id in self.not_found_dict and create is True:
			self.found_dict[_id] = relation

			if _id in self.not_found_dict:
				del self.not_found_dict[_id]

			if print_debug:
				type_str = self.SLT.get_type_str( type = type )
				self.P.write_debug( "Simulator_ES_Relations_Tool: add_ES_relation: added AS" + str(from_AS) + " - AS" + str(to_AS) + ", type = " + str(type_str) + ", source = " + str(source) )

			return _id
		elif _id in self.not_found_dict and create is False:
			if print_debug:
				type_str = self.SLT.get_type_str( type = type )
				self.P.write_debug( "Simulator_ES_Relations_Tool: add_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ", type = " + str(type_str) + ", source = " + str(source) + ": create is False" )

			return None
		else:
			self.P.write_error( "Simulator_ES_Relations_Tool: add_ES_relation: loop error" )
			return None

	def add_ES_relations( self, relations = None, overwrite = False, create = True, print_debug = False, print_server_response = False):
		if relations is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: add_ES_relations: relations is None" )
			return None

		if print_debug is True:
			self.P.write_debug( "Simulator_ES_Relations_Tool: add_ES_relations: start" )

		for relation in relations:
			self.add_ES_relation( relation = relation, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )

	def exist_ES_relation( self, relation_id = None, from_AS = None, to_AS = None, server_lookup = False, print_server_response = False, print_debug = False ):
		if relation_id is not None:
			pass
		elif from_AS is not None and to_AS is not None:
			pass
		elif from_AS is not None or to_AS is not None:
			self.P.write_error( "Simulator_ES_Relations_Tool: exist_ES_relation: from_AS or to_AS is None" )
			return None
		else:
			self.P.write_error( "Simulator_ES_Relations_Tool: exist_ES_relation: relation_id is None" )
			return None

		if print_debug is True:
			if from_AS is not None and to_AS is not None:
				self.P.write_debug( "Simulator_ES_Relations_Tool: exist_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": start" )
			else:
				self.P.write_debug( "Simulator_ES_Relations_Tool: exist_ES_relation: relation_id = " + str(relation_id) + ": start" )

		if relation_id is not None:
			_id = relation_id
		else:
			_id = None

		if _id is None:
			_id = self.get_relation_id( from_AS = from_AS, to_AS = to_AS )

		if _id is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: exist_ES_relation: relation_id is None" )
			return

		if _id in self.found_dict:
			return False
		elif _id in self.not_found_dict:
			return False

		self.__get_relation( _id = _id, from_AS = from_AS, to_AS = to_AS, print_server_response = print_server_response, print_debug = print_debug )

		if server_lookup is False:
			return False

		if _id in self.found_dict:
			return False
		elif _id in self.not_found_dict:
			return False


	def get_ES_relation( self, relation_id = None, from_AS = None, to_AS = None, print_server_response = False, print_debug = False ):
		if relation_id is not None:
			pass
		elif from_AS is not None and to_AS is not None:
			pass
		elif from_AS is not None or to_AS is not None:
			self.P.write_error( "Simulator_ES_Relations_Tool: get_ES_relation: from_AS or to_AS is None" )
			return None
		else:
			self.P.write_error( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id is None" )
			return None

		if print_debug is True:
			if from_AS is not None and to_AS is not None:
				self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": start" )
			else:
				self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id = " + str(relation_id) + ": start" )

		if relation_id is not None:
			_id = relation_id

		if _id is None:
			_id = self.get_relation_id( from_AS = from_AS, to_AS = to_AS )
		else:
			_id = None

		if _id is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id is None" )

		if _id in self.not_found_dict:
			if print_debug is True:
				if from_AS is not None and to_AS is not None:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": in not_found_dict")
				else:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id = " + str(relation_id) + ": in not_found_dict")

			return None

		if _id in self.found_dict:
			if print_debug is True:
				if from_AS is not None and to_AS is not None:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": in found_dict")
				else:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id = " + str(relation_id) + ": in found_dict")

			return self.found_dict[_id]

		self.__get_relation( _id = _id, from_AS = from_AS, to_AS = to_AS, print_server_response = print_server_response, print_debug = print_debug )

		if _id in self.not_found_dict:
			if print_debug is True:
				if from_AS is not None and to_AS is not None:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": in not_found_dict")
				else:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id = " + str(relation_id) + ": in not_found_dict")

			return None
		if _id in self.found_dict:
			if print_debug is True:
				if from_AS is not None and to_AS is not None:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": in found_dict")
				else:
					self.P.write_debug( "Simulator_ES_Relations_Tool: get_ES_relation: relation_id = " + str(relation_id) + ": in found_dict")


			return self.found_dict[_id]
		else:
			self.P.write_error( "Simulator_ES_Relations_Tool: get_ES_relation: _id not in self.not_found_dict and _id not in self.found_dict" )
			return None

	def __get_relation( self, _id = None, from_AS = None, to_AS = None, print_server_response = False, print_debug = False ):
		data_ES = self.ESI.get_id( index = self.RELATIONS, id = _id, print_server_response = print_server_response )

		if "found" not in data_ES:
			self.P.write_error( "Simulator_ES_Relations_Tool __get_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": 'found' not in data_ES" )
			self.P.write_JSON( data_ES )
			return None

		if data_ES['found'] is False:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_Relations_Tool: __get_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": not found in ElasticSearch index bgp-relations" )

			self.not_found_dict[_id] = None
		elif data_ES['found'] is True:
			if print_debug is True:
				self.P.write_debug( "Simulator_ES_Relations_Tool: __get_relation: AS" + str(from_AS) + " - AS" + str(to_AS) + ": retrieved from ElasticSearch index bgp-relations" )

			self.found_dict[_id] = data_ES['_source']

	def sync_ES_relations( self, overwrite = False, print_server_response = False ):
		self.P.write( "Simulator_ES_Relations_Tool: sync_relations: overwrite = " + str(overwrite) + ": start", color = 'green' )

		size = 100000

		data_JSON = dict()
		data_JSON['size'] = size
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		data_ES = self.ESI.search( index = self.RELATIONS, data_JSON = data_JSON, scroll = "1m", print_server_response = print_server_response )
		scroll_id = data_ES['_scroll_id']
		
		for data in data_ES['hits']['hits']:
			_id = data['_id']
			relation = data['_source']

			if overwrite is False and _id in self.found_dict:
				continue

			self.found_dict[_id] = relation

			if _id in self.not_found_dict:
				del self.not_found_dict[_id]

		amount_left = data_ES['hits']['total'] - size

		finished = False
		while finished is False:
			if amount_left < 0:
				amount_left = 0

			self.P.rewrite( "\tSimulator_ES_Relations_Tool: sync_relations: " + str(int(amount_left/1000)) + "k relations left" )
			data_ES = self.ESI.scroll( index = self.RELATIONS, scroll = "1m", scroll_id = scroll_id, print_server_response = print_server_response )
			
			if len( data_ES['hits']['hits'] ) == 0:
				finished = True

			for data in data_ES['hits']['hits']:
				_id = data['_id']
				relation = data['_source']

				if overwrite is False and _id in self.found_dict:
					continue

				self.found_dict[_id] = relation

				if _id in self.not_found_dict:
					del self.not_found_dict[_id]

			amount_left -= size

		self.P.write( "Simulator_ES_Relations_Tool: sync_relations: done!" )

	def flush_ES_relations( self, print_server_response = False ):    
		self.P.write( "Simulator_ES_Relations_Tool: flush_ES_relations: start", color = 'green' )

		data_list = list()
		length = len(self.found_dict)

		counter = len(self.found_dict)
		for _id in self.found_dict:
			counter -= 1
			if counter % 100 == 0:
				self.P.rewrite( "Simulator_ES_Relations_Tool: flush_ES_relations: preparing flush: " + str(counter/1000) + "k items left              " )

			data_JSON_index = dict()
			data_JSON_index['create'] = dict()
			data_JSON_index['create']['_id'] = _id

			data_list.append( json.dumps( data_JSON_index ) )
			data_list.append( json.dumps( self.found_dict[_id] ) )

			if len(data_list) > 200000:
				self.ESI.post_bulk_thread( index = self.RELATIONS, data_list = data_list, print_server_response = print_server_response, max_number_of_threads = 2 )
				data_list = list()

		self.ESI.post_bulk_thread( index = self.RELATIONS, data_list = data_list, print_server_response = print_server_response, max_number_of_threads = 2 )

		self.flush_counter = 0

		self.P.write( "Simulator_ES_Relations_Tool: flush: updated " + str(length) + " item(s)" )

	def flush_AS_rank_relations( self, print_debug = False, print_server_response = False ):    
		self.P.write( "Simulator_ES_Relations_Tool: flush_AS_rank_relations: start", color = 'green' )

		if print_debug is True:
			self.P.write( "Simulator_ES_Relations_Tool: flush_AS_rank_relations: resetting local cache" ) 

		self.reset_ES_relations_cache( print_debug = print_debug )

		self.add_AS_rank_relations( create = True, print_debug = print_debug, print_server_response = print_server_response )

		self.flush_ES_relations( print_server_response = print_server_response )

	def load_ES_relations( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: load_ES_relations: file_name is None" )
			return None

		file_name = file_name.split('.')[0] + ".relations"
		file_path = self.FT.get_file_path( file_name = file_name )

		if self.FT.check_file_exists( file_name = file_name ) is False:
			self.P.write_warning( "Simulator_ES_Relations_Tool: load_ES_relations: " + str(file_path) + " not found" )
		elif self.FT.check_checksum( file_name = file_name ) is True:
			data_JSON = self.FT.load_JSON_file( file_name = file_name, print_status = True )

			self.found_dict = data_JSON
		else:
			self.P.write_warning( "Simulator_ES_Relations_Tool: load_ES_relations: " + str(file_path) + ": checksum incorrect or missing" )

	def save_ES_relations( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "Simulator_ES_Relations_Tool: save_ES_relations: file_name is None" )
			return None

		self.P.write( "Simulator_ES_Relations_Tool: save_ES_relations: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".relations"

		self.FT.save_JSON_file( data_JSON = self.found_dict, file_name = file_name, print_status = True )
		self.FT.create_checksum( file_name = file_name, print_status = True )



import json, requests, hashlib, time, copy
from printer import Printer
from ES_local_interface import ES_Local_Interface
from ES_put_buffer import ES_Put_Buffer
from ES_stats_tool import ES_Stats_Tool
from time_tool import Time_Tool
from termcolor import colored
from are_you_sure_tool import Are_You_Sure_Tool

class ES_Withdraw_Tool():
	P = None
	ARST = None
	TT = None
	ESLI = None
	ESPB = None
	ESST = None
	ROUTES = None

	WITHDRAW = None

	processed_cache = None

	def __init__( self, P = None, ESLI = None, ESRB = None, ESST = None, ROUTES = None, WITHDRAWS = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "ES_Withdraw_Tool: P is None" )

		self.P.write( "ES_Withdraw_Tool: Loading...", color = 'cyan' )
		self.ARST = Are_You_Sure_Tool( P = self.P )

		if ROUTES is not None:
			self.ROUTES = ROUTES
		else:
			self.P.write_warning( "ES_Withdraw_Tool: ROUTES is None" )
			self.ROUTES = "bgp-routes"

		if ESLI is not None:
			self.ESLI = ESLI
		else:
			self.P.write_warning( "ES_Withdraw_Tool: ESLI is None" )
			self.ESLI = ES_Local_Interface( P = self.P )
			
		if ESRB is not None:
			self.ESRB = ESRB
		else:
			self.P.write_warning( "ES_Withdraw_Tool: ESRB is None" )
			self.ESRB = ES_Route_Buffer( P = self.P, ESLI = self.ESLI, index = self.ROUTES, print_run_time = False, print_debug = False )

		if ESST is not None:
			self.ESST = ESST
		else:
			self.P.write_warning( "ES_Withdraw_Tool: ESST is None" )
			self.ESST = ES_Stats_Tool( P = self.P, ESLI = self.ESLI )
			
		self.TT = Time_Tool( P = self.P )

		if WITHDRAWS is None:
			self.P.write_warning( "ES_Withdraw_Tool: WITHDRAWS is None" )
			self.WITHDRAWS = "bgp-withdraws"
		else:
			self.WITHDRAWS = WITHDRAWS

		self.ESPB = ES_Put_Buffer( index = self.WITHDRAWS, ESLI = self.ESLI, P = self.P, program_name = "ES_Withdraw_Tool" )

		self.setup_withdraws_index()

	def process_withdraws( self, RRC_number = None, RRC_range = None, time_interval = None ):
		self.processed_cache = dict()

		if time_interval is None:
			self.P.write_warning( "ES_Interface: process_withdraws: time_interval is None" )
			self.P.write_warning( "ES_Interface: process_withdraws: setting time_interval = [ 0, 2147483647 ]" )

		found_items = True
		while found_items is True:
			found_items = self.__process_withdraws( RRC_number = RRC_number, RRC_range = RRC_range, time_interval = time_interval )
			time.sleep(2)


	def __process_withdraws( self, RRC_number = None, RRC_range = None, time_interval = None ):
		if RRC_range is None and RRC_number is None:
			self.P.write_warning( "ES_Interface: process_withdraws: RRC_range is None and RRC_number is None" )
			self.P.write_warning( "ES_Interface: process_withdraws: setting RRC_range = [ 0, 42 ] " )
			RRC_range = [ 0, 42 ] 
		elif RRC_range is None and RRC_number is not None:
			RRC_range = [ RRC_number, RRC_number ] 

		for RRC_number in range( RRC_range[0], RRC_range[1] + 1 ):
			if RRC_number in self.processed_cache:
				continue

			self.P.write( "ES_Interface: process_withdraws: " + colored( "start: RRC" + str(RRC_number).zfill(2), color = 'green' ) )
			withdraw_data = self.__get_withdraw_data( RRC_number = RRC_number, time_interval = time_interval )

			if len(withdraw_data) == 0:
				self.processed_cache[ RRC_number ] = None

				if str(RRC_number) == str(RRC_range[1]):
					return False
				else:
					continue

			total = len(withdraw_data)
			counter = 0
			for _id in withdraw_data:
				counter += 1
				self.P.rewrite( "\tES_Withdraw_Tool: process_withdraw: processing withdraw " + str(counter) + " of " + str(total) + "                                     " )

				routes = withdraw_data[_id]

				for route in routes:
					[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = route['time'] )
					route['interval'] = interval_str

					_id = str(route['source_AS']) + str(route['dest_AS']) + str(route['path']) + str(route['start_IP']) + str(route['end_IP']) 
					_id = str(_id) + str(route['interval_start']) + str(route['interval_end']) + str(route['RRC_number']) 
					route['_id'] = hashlib.sha256( _id ).hexdigest()	

					if "interval" not in route:
						print "ERROR"
						print route 

					self.ESRB.put_route( route = route )
	
			self.ESRB.flush()
			self.P.rewrite( "\tES_Withdraw_Tool: process_withdraw: deleting withdraws                                                                 " )
			data_ES = self.ESLI.mdelete_ids( index = self.WITHDRAWS, type = None, ids = withdraw_data.keys(), print_server_response = False )

			if data_ES['errors'] is True:
				self.P.write_JSON( data_ES ) 

			time.sleep(2)

			return True

		return False

	def __update_stats( self, RRC_number = None ):
		if self.TT.get_elapsed_time_S_float() > 1.0:
			self.ESST.update_stats( RRC_number = RRC_number, mode = "stats" )
			self.TT.start()

	def __get_withdraw_data( self, RRC_number = None, time_interval = None ):
		withdraw_data = dict()

		if RRC_number is None:
			self.P.write_error( "ES_Withdraw_Tool: __get_withdraw_data: RRC_number is None" )
			return

		data_JSON = dict()
		data_JSON['size'] = 5000
		data_JSON['query'] = dict()
		data_JSON['query']['bool'] = dict()
		data_JSON['query']['bool']['must'] = list()

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['time'] = dict()
		data_JSON_2['range']['time']['gte'] = time_interval[0]
		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['time'] = dict()
		data_JSON_2['range']['time']['lte'] = time_interval[1]
		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['match'] = dict()
		data_JSON_2['match']['RRC_number'] = RRC_number
		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		#Retrieve Routes From ElasticSearch
		self.P.rewrite( "\tES_Withdraw_Tool: __get_withdraw_data: retrieving withdraws from ES index bgp-withdraws.." )
		filter_path = "hits.total, hits.hits"
		data_ES = self.ESLI.search( index = self.WITHDRAWS, data_JSON = data_JSON, filter_path = filter_path, print_server_response = False )

		withdraws = dict()
		for withdraw in data_ES['hits']['hits']:
			_id = withdraw['_id']
			withdraws[_id] = withdraw['_source']

		total = len(withdraws.keys())

		if len(withdraws) == 0:
			self.P.write( "\tES_Withdraw_Tool: __get_withdraw_data: no withdraws found" )

		send_data_JSON = dict()
		time_data_JSON = dict()
		_id_data_JSON = dict()

		counter = 0
		for _id in withdraws.keys():
			self.__update_stats( RRC_number = RRC_number )
			counter += 1
			self.P.rewrite( "\tES_Withdraw_Tool: __get_withdraw_data: prepare finding matching routes " + str(counter) + " of " + str(total) + "                                     " )

			withdraw = withdraws[_id]
			[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = withdraw['time'] ) 

			search_id = str(withdraw['dest_AS']) + str(withdraw['start_IP']) + str(withdraw['end_IP']) + str(withdraw['RRC_number']) 

			data_JSON = dict()
			data_JSON['size'] = 10000
			data_JSON['query'] = dict()
			data_JSON['query']['match'] = dict()
			data_JSON['query']['match']['search_id'] = hashlib.sha256( search_id ).hexdigest()

			if interval_str not in send_data_JSON:
				send_data_JSON[interval_str] = list()
				time_data_JSON[interval_str] = list()
				_id_data_JSON[interval_str] = list()

			send_data_JSON[interval_str].append( data_JSON )
			time_data_JSON[interval_str].append( withdraw['time'] )
			_id_data_JSON[interval_str].append( _id )

		for interval_str in send_data_JSON:
			self.__update_stats( RRC_number = RRC_number )
			data_list = send_data_JSON[interval_str]
			time_list = time_data_JSON[interval_str]
			_id_list = _id_data_JSON[interval_str]

			data_ES = self.ESLI.msearch_thread( index = self.ROUTES + interval_str, data_list = data_list, print_server_response = True )

			responses = data_ES['responses']
			index = 0
			counter = len(responses)
			for reponse in responses:
				self.P.rewrite( "\tES_Withdraw_Tool: __get_withdraw_data: finding matching routes: " + str(counter) + " withdraws left                                    " )
				counter -= 1
				#self.__update_stats( RRC_number = RRC_number )
				_time = time_list[index]
				_id = _id_list[index]

				withdraw_data[_id] = list()

				#if len(reponse['hits']['hits']) == 0:
				#	self.P.write_warning("ES_Withdraw_Tool: __get_withdraw_data: no routes found")
				#	self.P.write_JSON( withdraws[_id] )

				for hit in reponse['hits']['hits']:
					route = hit['_source']
					route['time'] = _time
					route['mode'] = "down"

					withdraw_data[_id].append( route )

				index += 1

		return withdraw_data

	def put_route( self, route = None, _id = None ):
		del route['mode']
		self.ESPB.put_id( id = _id, data_JSON = route )

	def flush( self ):
		self.ESPB.flush()

	def setup_withdraws_index( self, print_server_response = False ):
		if self.ESLI.exists_index( index = self.WITHDRAWS ) is False:
			self.P.write( "ES_Withdraw_Tool: setup_withdraws_index: ElasticSearch index '" + str(self.WITHDRAWS) + "' does not exists, creating..." )
			self.create_withdraws_index( print_server_response = print_server_response )

	def create_withdraws_index( self, print_server_response = False ):
		settings_JSON = dict()
		settings_JSON['number_of_shards'] = 2
		settings_JSON['number_of_replicas'] = 0

		mappings_JSON = dict()
		mappings_JSON["RRC_number"] = dict()
		mappings_JSON["RRC_number"]["type"] = "long"
		mappings_JSON["dest_AS"] = dict()
		mappings_JSON["dest_AS"]["type"] = "integer"
		mappings_JSON["start_IP"] = dict()
		mappings_JSON["start_IP"]["type"] = "ip"
		mappings_JSON["end_IP"] = dict()
		mappings_JSON["end_IP"]["type"] = "ip"
		mappings_JSON["date"] = dict() 
		mappings_JSON["date"]["type"] = "date"
		mappings_JSON["date"]["format"] = "epoch_second"

		data_ES = self.ESLI.create_index( index = self.WITHDRAWS, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = False )

		if "status" in data_ES and data_ES['status'] == 400:
			self.P.write( "ES_Withdraw_Tool: create_withdraws_index: ElasticSearch index '" + self.WITHDRAWS + "' already exists" )
		else:
			self.P.write( "ES_Withdraw_Tool: create_withdraws_index: ElasticSearch index '" + self.WITHDRAWS + "' created" )

	def delete_withdraws_index( self, print_server_response = False ):
		self.P.write("ES_Withdraw_Tool: delete_withdraws_index: Do you want to delete ElasticSearch index '" + self.WITHDRAWS + "'?", color = 'red' )
		if self.ARST.ask_are_you_sure() is False:
			return

		if self.ESLI.exists_index( index = self.WITHDRAWS ) is False:
			self.P.write("ES_Withdraw_Tool: delete_withdraws_index: ElasicSearch index '" + str(self.WITHDRAWS) + "' does not exists" )
		else:
			self.P.write("ES_Withdraw_Tool: delete_withdraws_index: ElasticSearch index '" + str(self.WITHDRAWS) + "' deleted" )
			return self.ESLI.delete_index( index = self.WITHDRAWS, print_server_response = print_server_response ) 




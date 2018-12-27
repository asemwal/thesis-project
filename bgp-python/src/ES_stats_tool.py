import json, requests, hashlib, time
from printer import Printer
from ES_local_interface import ES_Local_Interface

class ES_Stats_Tool():
	P = None
	ESLI = None
	STATS = None

	def __init__( self, P = None, ESLI = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "ES_Stats: P is None" )

		self.P.write( "ES_Stats: Loading...", color = 'cyan' )

		if ESLI is not None:
			self.ESLI = ESLI
		else:
			self.P.write_warning( "ES_Stats: ESLI is None" )
			self.ESLI = ES_Local_Interface( P = self.P )

		self.STATS = "bgp-stats"
		self.reset_stats_index()

	def update_stats( self, RRC_number = None, mode = None, count = None, ms = None, ps = None, done = None, todo = None ):
		if RRC_number is None:
			self.P.write_error( "ES_Stats: update_stats: RRC_number is None" )
			return

		_id = hashlib.sha256( str(RRC_number) ).hexdigest()	

		data_JSON = dict()
		data_JSON["RRC_number"] = int(RRC_number)
		data_JSON["date"] = int(time.time())

		if mode is not None:
			data_JSON["mode"] = str(mode)

		if count is not None:
			data_JSON["count"] = int(count)

		if ms is not None:
			data_JSON["ms"] = float(ms)

		if ps is not None:
			data_JSON["ps"] = float(ps)

		if done is not None:
			data_JSON["done"] = int(done)

		if todo is not None:
			data_JSON["todo"] = int(todo)

		self.ESLI.update_id( index = self.STATS, id = _id, data_JSON = data_JSON, print_server_response = False )

	def reset_stats_index( self, force_delete = False ):
		if force_delete is True:
			self.ESLI.delete_index( index = self.STATS, print_server_response = False ) 

		if self.ESLI.exists_index( index = self.STATS, print_server_response = False ) is False:
			settings_JSON = dict()
			settings_JSON['number_of_shards'] = 2
			settings_JSON['number_of_replicas'] = 0
			#settings_JSON['index.routing.allocation.exclude.size'] = "small"

			mappings_JSON = dict()
			mappings_JSON["RRC_number"] = dict()
			mappings_JSON["RRC_number"]["type"] = "long"
			mappings_JSON["mode"] = dict()
			mappings_JSON["mode"]["type"] = "text"
			mappings_JSON["date"] = dict()
			mappings_JSON["date"]["type"] = "date"
			mappings_JSON["date"]["format"] = "epoch_second"
			mappings_JSON["count"] = dict()
			mappings_JSON["count"]["type"] = "integer"
			mappings_JSON["ms"] = dict()
			mappings_JSON["ms"]["type"] = "float"
			mappings_JSON["ps"] = dict()
			mappings_JSON["ps"]["type"] = "float"
			mappings_JSON["done"] = dict()
			mappings_JSON["done"]["type"] = "integer"
			mappings_JSON["todo"] = dict()
			mappings_JSON["todo"]["type"] = "integer"

			self.ESLI.create_index( index = self.STATS, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = False )
			self.P.write( "\tES_Stats_Tool: reset_stats_index: created index 'bgp-stats'" )

		for RRC_number in range( 0, 41 ):
			self.P.rewrite( "\tES_Stats_Tool: reset_stats_index: RRC_number = " + str(RRC_number) )
			data_JSON = dict()
			data_JSON["RRC_number"] = int(RRC_number)
			data_JSON["date"] = 0
			data_JSON["mode"] = "closed"
			data_JSON["count"] = 0
			data_JSON["ms"] = 0
			data_JSON["ps"] = 0
			data_JSON["done"] = 0
			data_JSON["todo"] = 0

			_id = hashlib.sha256( str(RRC_number) ).hexdigest()	
			self.ESLI.put_id( index = self.STATS, id = _id, data_JSON = data_JSON, print_server_response = False )







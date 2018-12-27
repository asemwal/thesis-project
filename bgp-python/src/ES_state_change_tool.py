import json, requests, hashlib, time
from printer import Printer
from ES_local_interface import ES_Local_Interface
from ES_put_buffer import ES_Put_Buffer
from time_tool import Time_Tool
from are_you_sure_tool import Are_You_Sure_Tool

class ES_State_Change_Tool():
	P = None
	ARST = None
	TT = None
	ESLI = None
	ESPB_state_change = None

	STATE_CHANGE = None

	def __init__( self, P = None, ESLI = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "ES_State_Change_Tool: P is None" )

		self.P.write( "ES_State_Change_Tool: Loading...", color = 'cyan' )
		self.ARST = Are_You_Sure_Tool( P = self.P )

		if ESLI is not None:
			self.ESLI = ESLI
		else:
			self.P.write_warning( "ES_State_Change_Tool: ESLI is None" )
			self.ESLI = ES_Local_Interface( P = self.P )

		self.TT = Time_Tool( P = self.P )

		self.STATE_CHANGE = "bgp-state-change"
		self.ESPB_state_change = ES_Put_Buffer( index = self.STATE_CHANGE, ESLI = self.ESLI, P = self.P, program_name = "ES_State_Change_Tool" )

		self.setup_state_change_index()

	def setup_state_change_index( self, print_server_response = False ):
		if self.ESLI.exists_index( index = self.STATE_CHANGE ) is False:
			self.P.write( "ES_Withdraw_Tool: setup_state_change_index: ElasticSearch index '" + str(self.STATE_CHANGE) + "' does not exists, creating..." )
			self.create_state_change_index( print_server_response = print_server_response )

	def create_state_change_index( self, print_server_response = False ):
		settings_JSON = dict()
		settings_JSON['number_of_shards'] = 2
		settings_JSON['number_of_replicas'] = 0
		settings_JSON['index.routing.allocation.exclude.size'] = "small"

		mappings_JSON = dict()
		mappings_JSON["date"] = dict() 
		mappings_JSON["date"]["type"] = "date"
		mappings_JSON["date"]["format"] = "epoch_second"
		mappings_JSON["dest_AS"] = dict() 
		mappings_JSON["dest_AS"]["type"] = "long"
		mappings_JSON["new_state"] = dict() 
		mappings_JSON["new_state"]["type"] = "integer"

		data_ES = self.ESLI.create_index( index = self.STATE_CHANGE, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )

		if "status" in data_ES and data_ES['status'] == 400:
			self.P.write( "ES_State_Change_Tool: create_state_change_index: ElasticSearch index '" + self.STATE_CHANGE + "'' already exists" )
		else:
			self.P.write( "ES_State_Change_Tool: create_state_change_index: ElasticSearch index '" + self.STATE_CHANGE + "'' created" )

	def delete_state_change_index( self, print_server_response = False ):
		self.P.write("ES_State_Change_Tool: delete_state_change_index: Do you want to delete ElasticSearch index '" + self.STATE_CHANGE + "'?", color = 'red' )
		if self.ARST.ask_are_you_sure() is False:
			return

		if self.ESLI.exists_index( index = self.STATE_CHANGE ) is False:
			self.P.write("ES_State_Change_Tool: delete_state_change_index: ElasicSearch index '" + str(self.STATE_CHANGE) + "' does not exists" )
		else:
			self.P.write("ES_State_Change_Tool: delete_state_change_index: ElasticSearch index '" + str(self.STATE_CHANGE) + "' deleted" )
			return self.ESLI.delete_index( index = self.STATE_CHANGE, print_server_response = print_server_response ) 

	def put_state_change( self, peer_AS = None, time_stamp = None, new_state = None ):
			data_JSON = dict()
			data_JSON['dest_AS'] = peer_AS
			data_JSON['date'] = time_stamp
			data_JSON['new_state'] = new_state

			_id = str( peer_AS ) + str( time_stamp ) + str( new_state )
			_id = hashlib.sha256( _id ).hexdigest()	

			self.ESPB_state_change.put_id( id = _id, data_JSON = data_JSON, print_server_response = False )

	def flush( self ):
		self.ESPB_state_change.flush()


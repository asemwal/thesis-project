import json, requests
from printer import Printer
from file_tool import File_Tool
from ES_local_interface import ES_Local_Interface

class ES_Put_Buffer():
	buffer_send_size = None
	type = None
	__DEFAULT_TYPE = "default_type"
	auto_bulk_list = None
	print_debug = False
	FT = None
	ESLI = None

	headers_url = {'content-type': 'application/json'}
	main_url = None

	def __init__( self, index = None, buffer_send_size = 1000, print_debug = None, P = None, ESLI = None, program_name = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "ES_Put_Buffer : P is None" )

		if program_name is not None:
			self.P.write( "ES_Put_Buffer [" + str(program_name) +  "]: Loading...", color = 'cyan' )
		else:
			self.P.write( "ES_Put_Buffer: Loading...", color = 'cyan' )

		if ESLI is not None:
			self.ESLI = ESLI
		else:
			self.ESLI = ES_Local_Interface( P = self.P )
			self.P.write_warning( "File_Tool : ES_Put_Buffer : ESLI is None" )

		self.FT = File_Tool( P = self.P, program_name = "ES_Put_Buffer" )

		if index is None:
			self.P.write_error( "ES_Buffer : __init__ : index is None" )
			exit()

		if buffer_send_size is not None:
			self.buffer_send_size = buffer_send_size

		if print_debug is True:
			self.print_debug = True

		self.index = index
		self.type = self.__DEFAULT_TYPE
		self.auto_bulk_list = list()

		relative_folder_path = ""
		file_name = "ES_address.txt"
		counter = 0
		loaded = self.__load_ES_address( relative_folder_path = relative_folder_path, file_name = file_name )

		while counter < 3 and loaded is False:
			counter += 1
			relative_folder_path  = "../" + str(relative_folder_path)
			loaded = self.__load_ES_address( relative_folder_path = relative_folder_path, file_name = file_name )

		if loaded is False:
			self.P.write_error( "ES_Put_Buffer: __init__: Could not open ES_address.txt" )
			exit()

	def __load_ES_address( self, relative_folder_path = None, file_name = None ):
		self.main_url = self.FT.load_text_file( relative_folder_path = relative_folder_path, file_name = file_name )

		if self.main_url is None:
			return False
		else:
			self.main_url = self.main_url.replace( "\n", "" )
			return True

	def put_id( self, id = None, data = None, data_JSON = None, print_server_response = False ):
		if self.print_debug is True:
			self.P.write( "ES_Put_Buffer: put_id" )

		if data_JSON is not None:
			data = json.dumps(data_JSON)

		data_JSON_index = dict()
		data_JSON_index['index'] = dict()
		data_JSON_index['index']['_id'] = id

		self.auto_bulk_list.append( json.dumps(data_JSON_index) )
		self.auto_bulk_list.append( json.dumps(data_JSON) )

		if len( self.auto_bulk_list ) > self.buffer_send_size:
			self.ESLI.post_bulk( index = self.index, data_list = self.auto_bulk_list, print_server_response = print_server_response )
			self.auto_bulk_list = list()

	def flush( self, print_server_response = False ):
		if self.print_debug is True:
			self.P.write( "ES_Put_Buffer: flush" )

		if len( self.auto_bulk_list ) > 0:
			self.ESLI.post_bulk( index = self.index, data_list = self.auto_bulk_list, print_server_response = print_server_response )
			self.auto_bulk_list = list()

		





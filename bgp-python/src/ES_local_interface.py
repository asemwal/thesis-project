import json, requests, os, copy, hashlib, time, socket
from printer import Printer
from threading import Thread
from multiprocessing import Process, Value, Array, Manager, Lock
from time_tool import Time_Tool
from random import *
from time import sleep
from file_tool import File_Tool


class ES_Local_Interface():

	P = None
	TT = None
	FT = None
	manager = None
	headers_url = {'content-type': 'application/json'}
	main_url = ""
	__DEFAULT_TYPE = "default_type"

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] ES_Local_Interface: __init__: P is None", color = 'yellow' )

		self.P.write( "ES_Local_Interface: Loading...", color = 'cyan' )

		self.TT = Time_Tool( P = self.P )
		self.FT = File_Tool( P = self.P )
		self.manager = Manager()

		loaded = False

		os.environ['NO_PROXY'] = 'http://localhost:9200'

		relative_folder_path = ""
		file_name = "ES_address.txt"
		counter = 0
		loaded = self.__load_ES_address( relative_folder_path = relative_folder_path, file_name = file_name )

		while counter < 3 and loaded is False:
			counter += 1
			print self.FT.get_folder_path( relative_folder_path = relative_folder_path )
			loaded = self.__load_ES_address( relative_folder_path = relative_folder_path, file_name = file_name )

		if loaded is False:
			self.P.write_error( "ES_Local_Interface: __init__: Could not open ES_address.txt" )
			exit()

	def __load_ES_address( self, relative_folder_path = None, file_name = None ):
		self.main_url = self.FT.load_text_file( relative_folder_path = relative_folder_path, file_name = file_name )

		if self.main_url is None:
			return False
		else:
			self.main_url = self.main_url.replace( "\n", "" )
			return True

	def exists_index( self, index = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: search: index = None" )
			return None

		result = self.__exists_index( index = index, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__exists_index( index = index, print_server_response = print_server_response )

		return result

	def __exists_index( self, index = None, print_server_response = False ):
		url = self.main_url + str(index)

		try:
			text = requests.get(url=url, headers=self.headers_url ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: exists_index: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		if str(index) in data_ES:
			return True
		else:
			return False

	def get_index( self, index = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: get_index: index = None" )
			return None

		result = self.__get_index( index = index, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__get_index( index = index, print_server_response = print_server_response )

		return result

	def __get_index( self, index = None, print_server_response = False ):
		url = self.main_url + str(index)

		text = None

		try:
			text = requests.get(url=url, headers=self.headers_url ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: get_index: cannot connect to localhost:9200..." )
			return None

		if print_server_response is True:
			data_ES = json.loads( text )
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES )

		return json.loads( text )

	def msearch( self, index = None, type = None, data_list = list(), filter_path = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: msearch: index = None" ), 
			return None

		if data_list is None:
			self.P.write_error( "ES_Local_Interface: msearch: data_list = None" )
			return None
 
		result = self.__msearch( index = index, type = type, data_list = data_list, filter_path = filter_path, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__msearch( index = index, type = type, data_list = data_list, filter_path = filter_path, print_server_response = print_server_response )

		return result
		
	def __msearch( self, index = None, type = None, data_list = list(), filter_path = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		data = ""

		for item in data_list:
			data = str(data) + str(json.dumps(dict())) + "\n"
			data = str(data) + str(json.dumps(item)) + "\n"

		url = self.main_url + str(index) + "/" + str(type) + "/_msearch"
		
		if filter_path is not None:
			url = url + "?filter_path=" + str(filter_path)

		try:
			text = requests.get(url=url, headers=self.headers_url, data = data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: mget_ids: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def msearch_thread( self, index = None, type = None, data_list = list(), filter_path = None, max_number_of_threads = 10, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: msearch_thread: index = None" )
			return None

		if data_list is None:
			self.P.write_error( "ES_Local_Interface: msearch_thread: data_list = None" )
			return None

		result = None
		while result is None:
			try:
				result = self.__msearch_thread( index = index, type = type, data_list = data_list, filter_path = filter_path, max_number_of_threads = max_number_of_threads, print_server_response = print_server_response )
			except( OSError ):
				self.P.write_error( "ES_Local_Interface: msearch_thread: OSError, sleeping 1 minute" )
				sleep(60)
				result = None

		return result
		
	def __msearch_thread( self, index = None, type = None, data_list = list(), filter_path = None, max_number_of_threads = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		send_data_list = list()
		for item in data_list:
			send_data_list.append( str(json.dumps(dict())) )
			send_data_list.append( str(json.dumps(item)) )

		url_addon = str(index) + "/" + str(type) + "/_msearch"

		data_JSON = self.get_bulk_thread( self, url_addon = url_addon, data_list = send_data_list, max_number_of_threads = max_number_of_threads, print_server_response = False, print_debug = False )
		data_ES = dict()
		data_ES['responses'] = list()

		for key in list( sorted( data_JSON.keys() ) ):
			try:
				data_ES['responses'].extend( data_JSON[key]['responses'] )
			except( TypeError ):
				self.P.write_error( "ES_Local_Interface: __msearch_thread: TypeError" )
				return None

		return data_ES

	def mget_ids( self, index = None, type = None, ids = None, filter_path = None, source_filtering = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: mget_ids: index = None" )
			return None

		if ids is None:
			self.P.write_error( "ES_Local_Interface: mget_ids: ids = None" )
			return None

		if source_filtering is not None and 'list' not in str(source_filtering.__class__):
			self.P.write_warning( "ES_Local_Interface: mget_ids: source_filtering is not None and source_filtering not is list" )
			source_filtering = None

		result = self.__mget_ids( index = index, type = type, ids = ids, filter_path = filter_path, source_filtering = source_filtering, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__mget_ids( index = index, type = type, ids = ids, filter_path = filter_path, source_filtering = source_filtering, print_server_response = print_server_response )

		return result

	def __mget_ids( self, index = None, type = None, ids = None, filter_path = None, source_filtering = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		url = self.main_url + str(index) + "/" + str(type) + "/_mget"
		
		if filter_path is not None:
			url = url + "?filter_path=" + str(filter_path)

		if source_filtering is not None and source_filtering is list:
			url = url + "?source_filtering=" + str(source_filtering)

		data_JSON = dict()
		data_JSON['ids'] = ids
		data = json.dumps(data_JSON)

		try:
			text = requests.get(url=url, headers=self.headers_url, data = data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: mget_ids: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def mget( self, data_list = None, filter_path = None, source_filtering = None, print_server_response = False ):
		if data_list is None:
			self.P.write_error( "ES_Local_Interface: mget: data_list = None" )
			return None

		if source_filtering is not None and 'list' not in str(source_filtering.__class__):
			self.P.write_warning( "ES_Local_Interface: mget: source_filtering is not None and source_filtering not is list" )
			source_filtering = None

		result = self.__mget( data_list = data_list, filter_path = filter_path, source_filtering = source_filtering, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__mget( data_list = data_list, filter_path = filter_path, source_filtering = source_filtering, print_server_response = print_server_response )

			if len(result['docs']) > 0:
				if "found" not in data_ES['result'][0]:
					result = None
					self.P.write_error( "ES_Route_Buffer: __process_GL: 'found' not in docs[0], sleeping 1 minute" )
					sleep(60)

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = result ) 

		return result

	def __mget( self, data_list = None, filter_path = None, source_filtering = None, print_server_response = False ):
		url = self.main_url + "/_mget"

		if filter_path is not None:
			url = url + "?filter_path=" + str(filter_path)

		if source_filtering is not None and source_filtering is list:
			url = url + "?source_filtering=" + str(source_filtering)

		data_JSON = dict()
		data_JSON['docs'] = list()

		for item in data_list:
			data_JSON['docs'].append(item)

		data = json.dumps(data_JSON)

		try:
			text = requests.get(url=url, headers=self.headers_url, data = data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: mget: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def get_id( self, index = None, type = None, id = None, filter_path = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: get_id: index = None" )
			return None

		if id is None:
			self.P.write_error( "ES_Local_Interface: get_id: id = None" )
			return None

		result = self.__get_id( index = index, type = type, id = id, filter_path = filter_path, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__get_id( index = index, type = type, id = id, filter_path = filter_path, print_server_response = print_server_response )

		return result

	def __get_id( self, index = None, type = None, id = None, filter_path = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		url = self.main_url + str(index) + "/" + str(type) + "/" + str(id)
		
		if filter_path is not None:
			url = url + "?filter_path=" + str(filter_path)

		try:
			text = requests.get(url=url, headers=self.headers_url ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: get_id: cannot connect to localhost:9200..." )
			return None


		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def get_bulk_thread( self, index = None, url_addon = None, type = None, data_list = list(), max_number_of_threads = 10, print_server_response = False, print_debug = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: get_bulk_thread: index = None" )
			return None

		if data_list is None:
			self.P.write_error( "ES_Local_Interface: get_bulk_thread: data_list is None" )
			return None

		result = None

		while result is None:
			try:
				result = self.__get_bulk_thread_A( index = index, url_addon = url_addon, type = type, data_list = data_list, max_number_of_threads = max_number_of_threads, print_server_response = print_server_response, print_debug = print_debug )
			except( EOFError ):
				result = None
				self.P.write_error( "ES_Local_Interface: get_bulk_thread: EOFError, sleeping 1 miute" )
				sleep(60)
			except( IOError ):
				result = None
				self.P.write_error( "ES_Local_Interface: get_bulk_thread: IOError, sleeping 1 minute" )
				sleep(60)

		return result

	def __get_bulk_thread_A( self, index = None, url_addon = None, type = None, data_list = list(), max_number_of_threads = None, print_server_response = False, print_debug = False ):
		process_number_list = list()
		if max_number_of_threads == None:
			max_number_of_threads = 10

		for x in range( 0, max_number_of_threads ):
			process_number_list.append( 0 )

		current_number_of_processes = Value('i', 0)

		if print_debug:
			self.P.write( "ES_Local_Interface: get_bulk_thread: start", color = 'green' )

		get_bulk_thread_results = self.manager.dict()
		data_dict = dict()
		TT_dict = dict()
		finished_dict = self.manager.dict()
		error_dict = self.manager.dict()

		if type is None:
			type = self.__DEFAULT_TYPE

		if url_addon is not None:
			get_url = self.main_url + str(url_addon)

		wait_time = uniform(0.0, 1.0)

		data = ""
		thread_list = list()
		list_index = 0
		temp_index = 0
		counter = 0
		for item in data_list:
			counter += 1
			data = str(data) + str(item) + "\n"

			if counter > 1 and temp_index%2 == 1:
				counter = 0

				if current_number_of_processes.value >= max_number_of_threads:
					sleep(1)

					for name in finished_dict.keys():
						if finished_dict[name] is False:
							if TT_dict[name].get_elapsed_time_S_float() > 30 or error_dict[name] is True:
								sleep(wait_time)
								wait_time *= 1.2
								if wait_time > 60:
									wait_time = 60

								self.P.rewrite("\tES_Local_Interface: get_bulk_thread: force restart " + str(name) + " (wait time = " + str(wait_time) + ")                                         ", color = 'yellow' )
								#thread_list[ name ].close()
								thread_list[ name ] = Process( target=self.__get_bulk_thread, args=(get_url,copy.deepcopy(data_dict[name]),copy.deepcopy(name),print_server_response,print_debug,error_dict,finished_dict, get_bulk_thread_results,current_number_of_processes) )
								thread_list[ name ].start()
								TT_dict[name].start()

				else:
					if wait_time > 1:
						wait_time /= 1.5

					self.P.rewrite( "\tES_Local_Interface: get_bulk_thread: New Thread: list_index = " + str(list_index) + ", current_number_of_processes = " + str(current_number_of_processes.value) + ")" )
					thread_list.append( Process( target=self.__get_bulk_thread, args=(get_url,copy.deepcopy(data),copy.deepcopy(list_index),print_server_response,print_debug,error_dict,finished_dict, get_bulk_thread_results,current_number_of_processes) ) )
					thread_list[ list_index ].start()
					TT_dict[list_index] = Time_Tool( P = self.P )
					data_dict[list_index] = data
					sleep(0.1)

					data = ""
					list_index += 1

			temp_index += 1

		if len( data ) > 0:
			if current_number_of_processes.value >= max_number_of_threads:
				sleep(1)

			#if print_debug:
			self.P.rewrite( "\tES_Local_Interface: get_bulk_thread: New Thread: list_index = " + str(list_index) + ", current_number_of_processes = " + str(current_number_of_processes.value) + ")      " )
			thread_list.append( Process( target=self.__get_bulk_thread, args=(get_url,copy.deepcopy(data),list_index,print_server_response,print_debug,error_dict,finished_dict, get_bulk_thread_results,current_number_of_processes) ) )
			thread_list[ list_index ].start()
			data_dict[list_index] = data
			TT_dict[list_index] = Time_Tool( P = self.P )
			sleep(0.1)
			list_index += 1

		while ( len( finished_dict.keys() ) ) < list_index:
			sleep(1)

		data_JSON = dict()

		processed = dict()

		self.TT.start()

		done = False
		while done is False:
			done = True

			for name in finished_dict.keys():
				if finished_dict[name] is False:
					if TT_dict[name].get_elapsed_time_S_float() > 30 or error_dict[name] is True:
						sleep(wait_time)
						wait_time *= 1.2
						if wait_time > 60:
							wait_time = 60

						self.P.rewrite("\tES_Local_Interface: get_bulk_thread: force restart " + str(name) + " (wait time = " + str(wait_time) + ")                                    ", color = 'yellow' )
						#thread_list[ name ].close()
						thread_list[ name ] = Process( target=self.__get_bulk_thread, args=(get_url,copy.deepcopy(data_dict[name]),copy.deepcopy(name),print_server_response,print_debug,error_dict,finished_dict, get_bulk_thread_results,current_number_of_processes) )
						thread_list[ name ].start()
						TT_dict[name].start()
					done = False
				else:
					if name not in processed:
						processed[name] = True
						
						if wait_time > 1:
							wait_time /= 1.5

						data = get_bulk_thread_results[name]

						data_JSON[ name ] = data

		if print_debug is True:
			self.P.write(" \tES_Local_Interface: get_bulk_thread: Done!" )

		return data_JSON

	def __get_bulk_thread( self, get_url = None, data = None, list_index = None, print_server_response = False, print_debug = False, error_dict = None, finished_dict = None, results = None, current_number_of_processes = None ):
		current_number_of_processes.value += 1
		results[list_index] = None
		finished_dict[list_index] = False
		error_dict[list_index] = False

		try:
			text = requests.get(url=get_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: __get_bulk_thread: cannot connect to localhost:9200..." )
			return None

		while text is None:
			error_dict[list_index] = True
			sleep(10)

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: __get_bulk_thread: list_index = " + str(list_index), color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		results[ list_index ] = data_ES

		finished_dict[list_index] = True
		if current_number_of_processes.value > 0:
			current_number_of_processes.value -= 1

	def post_bulk_thread( self, index = None, url_addon = None, type = None, data_list = list(), max_number_of_threads = 3, print_server_response = False, print_debug = False ):
		if data_list is None:
			self.P.write_error( "ES_Local_Interface: post_bulk_thread: data_list is None" )
			return None

		result = False

		while result is False:
			try:
				return self.post_bulk_thread_A( index = index, url_addon = url_addon, type = type, data_list = data_list, max_number_of_threads = max_number_of_threads, print_server_response = print_server_response, print_debug = print_debug )
				result = True
			except( EOFError ):
				result = False
				self.P.write_error( "ES_Local_Interface: post_bulk_thread: EOFError, sleeping 1 minute" )
				sleep(60)
			except( IOError ):
				result = False
				self.P.write_error( "ES_Local_Interface: post_bulk_thread: IOError, sleeping 1 minute" )
				sleep(60)
			except( socket.error ):
				result = False
				self.P.write_error( "ES_Local_Interface: post_bulk_thread: socket.error, sleeping 1 minute" )
				sleep(60)

	def post_bulk_thread_A( self, index = None, url_addon = None, type = None, data_list = list(), max_number_of_threads = 3, print_server_response = False, print_debug = False ):
		process_number_list = list()
		for x in range( 0, max_number_of_threads ):
			process_number_list.append( 0 )

		max_number_of_threads = len(process_number_list)
		current_number_of_processes = Value('i', 0)

		if print_debug:
			self.P.write( "ES_Local_Interface: post_bulk_thread: start", color = 'green' )

		post_bulk_thread_results = self.manager.dict()
		data_dict = dict()
		TT_dict = dict()
		finished_dict = self.manager.dict()
		error_dict = self.manager.dict()

		if type is None:
			type = self.__DEFAULT_TYPE

		if url_addon is not None:
			post_url = self.main_url + str(url_addon)
		elif index is not None:
			post_url = self.main_url + str(index) + "/" + str(type) + "/_bulk"
		else:
			post_url = self.main_url + "/_bulk"

		wait_time = uniform(0.0, 1.0)

		data = ""
		thread_list = list()
		list_index = 0
		temp_index = 0
		for item in data_list:
			data = str(data) + str(item) + "\n"

			if len( data ) > 1000000 and temp_index%2 == 1:

				if current_number_of_processes.value >= max_number_of_threads:
					sleep(1)

					#self.P.rewrite("\tES_Local_Interface: post_bulk_thread: wait" + "                                                                                   ", color = 'yellow' )

					for name in finished_dict.keys():
						if finished_dict[name] is False:
							if TT_dict[name].get_elapsed_time_S_float() > 30 or error_dict[name] is True:
								sleep(wait_time)
								wait_time *= 1.2
								if wait_time > 60:
									wait_time = 60

								self.P.rewrite("\tES_Local_Interface: post_bulk_thread: force restart " + str(name) + " (wait time = " + str(wait_time) + ")                                         ", color = 'yellow' )
								#thread_list[ name ].close()
								thread_list[ name ] = Process( target=self.__post_bulk_thread, args=(post_url,copy.deepcopy(data_dict[name]),copy.deepcopy(name),print_server_response,print_debug,error_dict,finished_dict, post_bulk_thread_results,current_number_of_processes) )
								thread_list[ name ].start()
								TT_dict[name].start()
				else:
					if wait_time > 1:
						wait_time /= 1.5

					self.P.rewrite( "\tES_Local_Interface: post_bulk_thread: New Thread: list_index = " + str(list_index) + ", current_number_of_processes = " + str(current_number_of_processes.value) + ")" )
					thread_list.append( Process( target=self.__post_bulk_thread, args=(post_url,copy.deepcopy(data),copy.deepcopy(list_index),print_server_response,print_debug,error_dict,finished_dict, post_bulk_thread_results,current_number_of_processes) ) )
					thread_list[ list_index ].start()
					TT_dict[list_index] = Time_Tool( P = self.P )
					data_dict[list_index] = data
					sleep(0.1)

					data = ""
					list_index += 1

			temp_index += 1

		if len( data ) > 0:
			if current_number_of_processes.value >= max_number_of_threads:
					sleep(1)

			#if print_debug:
			self.P.rewrite( "\tES_Local_Interface: post_bulk_thread: New Thread: list_index = " + str(list_index) + ", current_number_of_processes = " + str(current_number_of_processes.value) + ")      " )
			thread_list.append( Process( target=self.__post_bulk_thread, args=(post_url,copy.deepcopy(data),list_index,print_server_response,print_debug,error_dict,finished_dict, post_bulk_thread_results,current_number_of_processes) ) )
			thread_list[ list_index ].start()
			data_dict[list_index] = data
			TT_dict[list_index] = Time_Tool( P = self.P )
			sleep(0.1)
			list_index += 1

		while ( len( finished_dict.keys() ) ) < list_index:
			sleep(1)

		data_ES = dict()
		data_ES['items'] = list()

		processed = dict()

		self.TT.start()

		done = False
		while done is False:
			done = True

			for name in finished_dict.keys():
				if finished_dict[name] is False:
					if TT_dict[name].get_elapsed_time_S_float() > 30 or error_dict[name] is True:
						sleep(wait_time)
						wait_time *= 1.2
						if wait_time > 60:
							wait_time = 60

						self.P.rewrite("\tES_Local_Interface: post_bulk_thread: force restart " + str(name) + " (wait time = " + str(wait_time) + ")                                    ", color = 'yellow' )
						#thread_list[ name ].close()
						thread_list[ name ] = Process( target=self.__post_bulk_thread, args=(post_url,copy.deepcopy(data_dict[name]),copy.deepcopy(name),print_server_response,print_debug,error_dict,finished_dict, post_bulk_thread_results,current_number_of_processes) )
						thread_list[ name ].start()
						TT_dict[name].start()
					done = False
				else:
					if name not in processed:
						processed[name] = True
						
						if wait_time > 1:
							wait_time /= 1.5

						item = post_bulk_thread_results[name]

						try:
							data_ES['items'].extend( item['items'] )
						except( TypeError ):
							print "ERRORR"
							print "ERRORR"
							print "ERRORR"
							print "ERRORR"
							print "ERRORR"
							print "ERRORR"
							print "ERRORR"
							print "ERRORR"
							self.P.write("ERRORR")
							self.P.write("ERRORR")
							self.P.write("ERRORR")
							self.P.write("ERRORR")
							self.P.write("ERRORR")
							self.P.rewrite("\tES_Local_Interface: post_bulk_thread: force restart " + str(name) + " (null error)                                    ", color = 'yellow' )
							#thread_list[ name ].close()
							thread_list[ name ] = Process( target=self.__post_bulk_thread, args=(post_url,copy.deepcopy(data_dict[name]),copy.deepcopy(name),print_server_response,print_debug,error_dict,finished_dict, post_bulk_thread_results,current_number_of_processes) )
							thread_list[ name ].start()
							TT_dict[name].start()

		if print_debug is True:
			print "Done"

		return data_ES

	def __post_bulk_thread( self, post_url, data = None, list_index = None, print_server_response = False, print_debug = False, error_dict = None, finished_dict = None, results = None, current_number_of_processes = None ):
		current_number_of_processes.value += 1
		results[list_index] = None
		finished_dict[list_index] = False
		error_dict[list_index] = True

		try:
			text = requests.post(url=post_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: post_bulk: cannot connect to localhost:9200..." )
			return None

		while text is None:
			error_dict[ list_index ] = True
			sleep(10)

		data_ES = json.loads( text )

		while "items" not in data_ES:
			error_dict[ list_index ] = True
			sleep(10)

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: __post_bulk_thread: list_index = " + str(list_index), color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		if "items" not in data_ES:
			error_dict[list_index] = True
			sleep(10)

		if data_ES is None:
			error_dict[list_index] = True
			sleep(10)

		results[ list_index ] = data_ES

		finished_dict[list_index] = True
		if current_number_of_processes.value > 0:
			current_number_of_processes.value -= 1

		#if print_debug:
		#	self.P.write( "ES_Local_Interface: __post_bulk_thread: Done (list_index = " + str(list_index) + ", current_number_of_processes = " + str(current_number_of_processes.value) + ")" )

	def post_bulk( self, index = None, type = None, data_list = list(), print_server_response = False ):
		if data_list is None:
			self.P.write_error( "ES_Local_Interface: post_bulk: data_list is None" )
			return None

		result = self.__post_bulk( index = index, type = type, data_list = data_list, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__post_bulk( index = index, type = type, data_list = data_list, print_server_response = print_server_response )
		
		return result

	def __post_bulk( self, index = None, type = None, data_list = list(), print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		data = ""

		for x in range(0, len(data_list) ):
			data = str(data) + str(data_list[x]) + "\n"

		if index is not None:
			post_url = self.main_url + str(index) + "/" + str(type) + "/_bulk"
		else:
			post_url = self.main_url + "/_bulk"

		try:
			text = requests.post(url=post_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: post_bulk: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def search( self, index = None, type = None, source_filtering = None, data_JSON = None, filter_path = None, scroll = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: search: index is None" )
			return None

		if filter_path is not None and scroll is not None:
			self.P.write_error( "ES_Local_Interface: search: filter_path is not None and scroll is not None" )
			return None

		if data_JSON is None:
			self.P.write_error( "ES_Local_Interface: search: data_JSON = None" )
			return None

		if source_filtering is not None and 'list' not in str(source_filtering.__class__):
			self.P.write_warning( "ES_Local_Interface: search: source_filtering is not None and source_filtering not is list" )
			source_filtering = None

		result = self.__search( index = index, type = type, source_filtering = source_filtering, data_JSON = data_JSON, filter_path = filter_path, scroll = scroll, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__search( index = index, type = type, source_filtering = source_filtering, data_JSON = data_JSON, filter_path = filter_path, scroll = scroll, print_server_response = print_server_response )
		
		return result

	def __search( self, index = None, type = None, source_filtering = None, data_JSON = None, filter_path = None, scroll = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		if source_filtering is not None and 'list' in str(source_filtering.__class__):
			data_JSON['_source'] = source_filtering

		if data_JSON is not None:
			data = json.dumps(data_JSON)

		if index is not None and type is not None:
			url = self.main_url + str(index) + "/" + str(type) + "/"
		elif index is not None:
			url = self.main_url + str(index) + "/"
		else:
			url = self.main_url

		search_url = url + "_search"

		if filter_path is not None:
			search_url = search_url + "?filter_path=" + str(filter_path)

		if scroll is not None:
			search_url = search_url + "?scroll=" + str(scroll)

		try:
			text = requests.get(url=search_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: search: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES )

		return data_ES

	def scroll( self, index = None, scroll = None, scroll_id = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: scroll: index is None" )
			return None

		if scroll is None:
			self.P.write_error( "ES_Local_Interface: scroll: scroll is None" )
			return None

		if scroll_id is None:
			self.P.write_error( "ES_Local_Interface: scroll: scroll_id is None" )
			return None

		result = self.__scroll( index = index, scroll = scroll, scroll_id = scroll_id, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__scroll( index = index, scroll = scroll, scroll_id = scroll_id, print_server_response = print_server_response )
		
		return result

	def __scroll( self, index = None, scroll = None, scroll_id = None, print_server_response = False ):
		scroll_url = self.main_url + "_search/scroll"

		data_JSON = dict()
		data_JSON['scroll'] = scroll
		data_JSON['scroll_id'] = scroll_id

		data = json.dumps(data_JSON)

		try:
			text = requests.post(url=scroll_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: scroll: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES )

		return data_ES

	def update_id( self, index = None, type = None, id = None, data_JSON = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: update_id: index is None" )
			return None

		if id is None:
			self.P.write_error( "ES_Local_Interface: update_id: id is None" )
			return None

		if data_JSON is None:
			self.P.write_error( "ES_Local_Interface: update_id: data_JSON is None" )
			return None

		result = self.__update_id( index = index, type = type, id = id, data_JSON = data_JSON, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__update_id( index = index, type = type, id = id, data_JSON = data_JSON, print_server_response = print_server_response )
		
		return result

	def __update_id( self, index = None, type = None, id = None, data_JSON = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		if data_JSON is not None:
			data_ES = dict()
			data_ES['doc'] = data_JSON
			data = json.dumps(data_ES)

		put_url = self.main_url + str(index) + "/" + str(type) + "/" + str(id) + "/_update"

		try:
			text = requests.post(url=put_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: update_id: cannot connect to localhost:9200..." )
			return None

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			data_ES = json.loads( text )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def mdelete_ids( self, index = None, type = None, ids = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: mdelete_ids: index is None" )
			return None

		if ids is None:
			self.P.write_error( "ES_Local_Interface: mdelete_ids: ids is None" )
			return None

		result = self.__mdelete_ids( index = index, type = type, ids = ids, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__mdelete_ids( index = index, type = type, ids = ids, print_server_response = print_server_response )

		return result

	def __mdelete_ids( self, index = None, type = None, ids = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		post_url = self.main_url + str(index) + "/" + str(type) + "/_bulk"
		data = ""

		for id in ids:
			data_JSON = dict()
			data_JSON['delete'] = dict()
			data_JSON['delete']['_id'] = id 
			data = str(data) + str( json.dumps(data_JSON) ) + "\n"

		try:
			text = requests.post(url=post_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: delete_id: cannot connect to localhost:9200..." )
			return None

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			data_ES = json.loads( text )
			self.P.write_JSON( data_JSON = data_ES ) 

		return json.loads( text )

	def delete_id( self, index = None, type = None, id = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: delete_id: index is None" )
			return None

		if id is None:
			self.P.write_error( "ES_Local_Interface: delete_id: id is None" )
			return None

		result = self.__delete_id( index = index, type = type, id = id, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__delete_id( index = index, type = type, id = id, print_server_response = print_server_response )

		return result

	def __delete_id( self, index = None, type = None, id = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		delete_url = self.main_url + str(index) + "/" + str(type) + "/" + str(id)

		try:
			text = requests.delete(url=delete_url, headers=self.headers_url ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: delete_id: cannot connect to localhost:9200..." )
			return None

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			data_ES = json.loads( text )
			self.P.write_JSON( data_JSON = data_ES ) 

		return json.loads( text )

	def put_id( self, index = None, type = None, id = None, data_JSON = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: put_id: index is None" )
			return None

		if id is None:
			self.P.write_error( "ES_Local_Interface: put_id: id is None" )
			return None

		if data_JSON is None:
			self.P.write_error( "ES_Local_Interface: put_id: data_JSON is None" )
			return None

		result = self.__put_id( index = index, type = type, id = id, data_JSON = data_JSON, print_server_response = print_server_response )

		if data_JSON is None:
			self.P.write_error( "ES_Local_Interface: put_id: data_JSON = None" )
			return

		while result is None:
			sleep(1)
			result = self.__put_id( index = index, type = type, id = id, data_JSON = data_JSON, print_server_response = print_server_response )

		return result

	def __put_id( self, index = None, type = None, id = None, data_JSON = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		if data_JSON is not None:
			data = json.dumps(data_JSON)

		put_url = self.main_url + str(index) + "/" + str(type) + "/" + str(id)

		try:
			text = requests.put(url=put_url, headers=self.headers_url, data=data ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: put_id: cannot connect to localhost:9200..." )
			return None

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			data_ES = json.loads( text )
			self.P.write_JSON( data_JSON = data_ES ) 

		return json.loads( text )

	def delete_index( self, index = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: delete_index: index is None" )
			return None

		result = self.__delete_index( index = index, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__delete_index( index = index, print_server_response = print_server_response )
		
		return result

	def __delete_index( self, index = None, print_server_response = False ):
		delete_url = self.main_url + str(index)

		try:
			text = requests.delete(url=delete_url, headers=self.headers_url ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: delete_index: cannot connect to localhost:9200..." )
			return None
		
		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			data_ES = json.loads( text )
			self.P.write_JSON( data_JSON = data_ES ) 

		return json.loads( text )

	def update_index( self, index = None, type = None, mappings_JSON = None,  print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: delete_index: index is None" )
			return None

		if mappings_JSON is None:
			self.P.write_error( "ES_Local_Interface: delete_index: mappings_JSON is None" )
			return None

		result = self.__update_index( index = index, type = type, mappings_JSON = mappings_JSON, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__update_index( index = index, type = type, mappings_JSON = mappings_JSON, print_server_response = print_server_response )
		
		return result

	def __update_index( self, index = None, type = None, mappings_JSON = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		put_url = self.main_url + str(index) + "/_mapping/" + str(type)

		data_JSON = dict()
		data_JSON['properties'] = dict()
		data_JSON['properties'] = mappings_JSON

		try:
			text = requests.put(url=put_url, headers=self.headers_url, data=json.dumps(data_JSON) ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: update_index: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES

	def create_index( self, index = None, type = None, mappings_JSON = None, settings_JSON = None, print_server_response = False ):
		if index is None:
			self.P.write_error( "ES_Local_Interface: create_index: index is None" )
			return None

		if mappings_JSON is None:
			self.P.write_error( "ES_Local_Interface: create_index: mappings_JSON is None" )
			return None

		result = self.__create_index( index = index, type = type, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )

		while result is None:
			sleep(1)
			result = self.__create_index( index = index, type = type, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = print_server_response )
		
		return result

	def __create_index( self, index = None, type = None, mappings_JSON = None, settings_JSON = None, print_server_response = False ):
		if type is None:
			type = self.__DEFAULT_TYPE

		put_url = self.main_url + str(index) 

		data_JSON = dict()
		data_JSON['mappings'] = dict()
		data_JSON['mappings'][str(type)] = dict()
		data_JSON['mappings'][str(type)]['properties'] = mappings_JSON

		if settings_JSON is not None:
			data_JSON['settings'] = settings_JSON

		try:
			text = requests.put(url=put_url, headers=self.headers_url, data=json.dumps(data_JSON) ).text
		except( requests.exceptions.ConnectionError ):
			self.P.rewrite_error( "ES_Local_Interface: create_index: cannot connect to localhost:9200..." )
			return None

		data_ES = json.loads( text )

		if print_server_response is True:
			self.P.write( "ElasticSearch server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		return data_ES


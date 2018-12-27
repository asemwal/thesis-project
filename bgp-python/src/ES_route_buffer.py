import json, random, copy
from printer import Printer
from time_tool import Time_Tool
from ES_local_interface import ES_Local_Interface
from alive_tool import Alive_Tool
from time import sleep
from threading import Thread
from random import randint

class ES_Route_Buffer():
	print_debug = False
	index = None
	print_run_time = False
	run_time = 0
	run_time_amount = 0

	buffer_send_size = 100
	cache_size = 10000
	cache_hit = 0
	cache_miss = 0
	in_system = 0
	not_in_system = 0

	P = None
	ES = None
	AT = None

	# New List
	NL_dict = None
	print_NL_processing_time = False

	# Update List
	UL_dict = None
	print_UL_processing_time = False

	# Get List
	GL_dict = None
	print_GL_processing_time = False

	# Cache List
	CL_dict = None

	# Input List
	IL_list = None
	IL_list_thread = None
	IL_list_thread_flush = None
	IL_list_thread_stop = None
	IL_list_thread_wait = None
	IL_list_thread_flush_busy = None

	def __init__( self, index = None, buffer_send_size = 4000, print_run_time = False, ESLI = None, print_debug = False, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "ES_Route_Buffer: P is None" )

		self.P.write( "ES_Route_Buffer: Loading...", color = 'cyan' )

		if index is None:
			self.P.write_error( "ES_Route_Buffer : __init__ : index is None" )
			exit()

		if buffer_send_size is not None:
			self.buffer_send_size = buffer_send_size

		if ESLI is not None:
			self.ESLI = ESLI
		else:
			self.ESLI = ES_Local_Interface( P = self.P )

		if print_run_time is not None and print_run_time is True:
			self.print_run_time = True

		if print_debug is True:
			self.print_debug = True

		self.index = index

		self.TT = Time_Tool( P = self.P )
		self.AT = Alive_Tool( P = self.P )

		self.reset_route_buffer_cache()

		self.IL_list_thread = Thread( target=self.thread_loop )
		self.IL_list_thread.deamon = True
		self.IL_list_thread.start()

	def reset_route_buffer_cache( self, index = None ):
		self.P.write( "ES_Route_Buffer: reset_route_buffer_cache" )
		
		if index is not None:
			self.index = index

		self.NL_dict = dict()
		self.UL_dict = dict()
		self.GL_dict = dict()
		self.CL_dict = dict()
		self.IL_list = list()

	def kill_thread( self ):
		self.IL_list_thread_stop = True

	def set_thread_alive( self ):
		return

	def thread_loop( self ):
		thread_TT = Time_Tool( P = self.P )
		self.IL_list_thread_flush = False
		self.IL_list_thread_stop = False
		self.IL_list_thread_wait = False

		while True:
			if self.IL_list_thread_stop is True:
				break

			if self.IL_list_thread_flush is True:
				self.IL_list_thread_wait = True
				while len( self.IL_list ) > 0:
					self.__put_route( route = self.IL_list[0] )
					self.IL_list.pop(0)

				if self.print_debug is True:
					self.P.write( "ES_Route_Buffer: thread_loop : len( self.IL_list ) == 0" )

				self.__flush()
				self.IL_list_thread_flush = False
				self.IL_list_thread_wait = False
				self.IL_list_thread_flush_busy = False

			if len( self.IL_list ) > 0:
				self.__put_route( route = self.IL_list[0] )
				self.IL_list.pop(0)

		self.P.write( "ES_Route_Buffer: thread_loop : stopping..." )
		self.__flush()

	def update_run_speed( self ):
		return

	def put_route( self, route ):
		if self.IL_list_thread_wait is None:
			self.IL_list_thread_wait = False

		while len( self.IL_list ) > 3 * int(self.buffer_send_size) or self.IL_list_thread_wait is True:
			sleep(1)

		self.IL_list.append( route )

	def __put_route( self, route ):
		route = dict(route)

		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: put_route" )

		if self.print_run_time is True:
			self.TT.start()

		# New List
		if str(route['_id']) in self.NL_dict:
			self.in_system += 1
			self.__update_NL_route( route = route )

		# Update List
		elif str(route['_id']) in self.UL_dict:
			self.in_system += 1
			self.__update_UL_route( route = route )

		# Get List
		elif str(route['_id']) in self.GL_dict:
			self.in_system += 1
			self.__update_GL_route( route = route )

		# Cache List
		elif str(route['_id']) in self.CL_dict:
			self.in_system += 1
			self.__in_CL_route( route = route )
		else:
			self.not_in_system = self.not_in_system + 1
			self.__not_in_CL_route( route = route )

		if self.print_run_time is True:
			self.run_time = float(self.run_time) + self.TT.get_elapsed_time_S_float()
			self.run_time_amount = int(self.run_time_amount) + 1

			if self.run_time_amount%10000 is 0:
				avg = str( round(float(self.run_time) / float(self.run_time_amount) * 1000000.0,2) ) + "us"
				cache_hit_perc = round(float(self.in_system) / float(self.in_system+self.not_in_system) * 100.0,2)
				sizes = "[ " + str(len(self.NL_dict)) + ", " + str(len(self.UL_dict)) + ", " + str(len(self.GL_dict)) + ", " + str(len(self.CL_dict)) + " ]"
				self.P.write( "\tES_Route_Buffer : put_route : Average time per call: " + avg + ", cache_size: " + str(len(self.CL_dict)) + ", cache_hit_perc: " + str(cache_hit_perc) + ", " + str(sizes), color = 'blue' )
				self.in_system = 0
				self.not_in_system = 0
				self.run_time = 0
				self.run_time_amount = 0

	def __update_NL_route( self, route ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __update_NL_route" )

		_id = route['_id']

		if "mode" in route and "time" in route:
			self.NL_dict[ _id ]['alive'] = self.AT.update( alive = self.NL_dict[ _id ]['alive'], time = route['time'], mode = route['mode'] )

		if "added_rib" in route:
			self.NL_dict[ _id ]['rib'] = self.__update_rib( current_rib = self.NL_dict[ _id ]['rib'], added_rib= route['added_rib'] )

		self.__process_NL()

	def __add_NL_route( self, GL_dict_item ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __add_NL_route" )

		route = GL_dict_item['route']
		_id = str(GL_dict_item['_id'])

		route['alive'] = list()
		for action in GL_dict_item['actions']:
			route['alive'] = self.AT.update( alive = route['alive'], time = action['time'], mode = action['mode'] )

		route['rib'] = list()
		for added_rib in GL_dict_item['added_ribs']:
			route['rib'] = self.__update_rib( current_rib = route['rib'], added_rib = added_rib )

		self.NL_dict[ _id ] = route
		self.clean_route( route = self.NL_dict[ _id ] )

		self.__process_NL()

	def __process_NL( self, flush = False ):
		if len( self.NL_dict ) > self.buffer_send_size * 20 or flush is True:
			if len( self.NL_dict ) == 0:
				return

			if self.print_NL_processing_time is True:
				temp_TT = Time_Tool( P = self.P )

			if self.print_debug is True:
				self.P.write( "ES_Route_Buffer: __process_NL" )

			data_list = list()

			for _id in self.NL_dict:
				data_JSON_index = dict()
				data_JSON_index['index'] = dict()
				data_JSON_index['index']['_id'] = _id
				data_JSON_index['index']['_type'] = "default_type"

				_interval = self.__del_key_dict( dict_data = self.NL_dict[_id], key = "interval" )
				data_JSON_index['index']['_index'] = self.index + str(_interval)

				data_list.append( json.dumps( data_JSON_index ) )
				data_list.append( json.dumps( self.NL_dict[_id] ) )

			data_ES = None
			items = None
			status_ok = False

			while status_ok is False:
				status_ok = True
				data_ES = self.ESLI.post_bulk_thread( data_list = data_list, print_server_response = False )
				items = data_ES['items']

				for item in items:
					if "index" not in item and status_ok is True:
						self.P.write( "ES_Route_Buffer: __process_NL: index AGAIN..., sleep 1 minute" )
						print item
						status_ok = False
						sleep(60)

					index = item['index']

					if "result" not in index and status_ok is True:
						reason = index['error']['caused_by']['reason']
						if "Numeric" in reason:
							self.P.write( "ES_Route_Buffer: __process_NL: Numeric ERROR" )
							print index
						else:
							self.P.write( "ES_Route_Buffer: __process_NL: result AGAIN..., sleep 1 minute" )
							print index
							status_ok = False
							sleep(60)

			items = data_ES['items']
			for item in items:
				if "index" not in item:
					continue

				index = item['index']
				_id = index['_id']

				if "result" not in index:
					continue
				
				if "created" in index['result']:
					self.__add_CL_route( self.NL_dict[ _id ], _id = _id )

			self.NL_dict = dict()

			if self.print_NL_processing_time is True:
				elapsed_time_float_MS = round( float(temp_TT.get_elapsed_time_S_float()) * float(1000.0), 2 )
				self.P.write( "\tES_Route_Buffer : __process_NL : took " + str(elapsed_time_float_MS) + "ms" )

	def __update_UL_route( self, route ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __update_UL_route" )

		_id = route['_id']

		if "time" in route and "mode" in route:
			self.UL_dict[ _id ]['alive'] = self.AT.update( alive = self.UL_dict[ _id ]['alive'], time = route['time'], mode = route['mode'] )

		if "added_rib" in route:
			self.UL_dict[ _id ]['rib'] = self.__update_rib( current_rib = self.UL_dict[ _id ]['rib'], added_rib = route['added_rib'] )

		self.clean_route( route = self.UL_dict[ _id ] )

		self.__process_UL()

	def __add_UL_route( self, GL_dict_item = None, route = None ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __add_UL_route" )

		if GL_dict_item is not None and route is not None:
			_id = GL_dict_item['_id']

			actions = GL_dict_item['actions']

			for action in actions:
				route['alive'] = self.AT.update( alive = route['alive'], time = action['time'], mode = action['mode'] )

			for added_rib in GL_dict_item['added_ribs']:
				route['rib'] = self.__update_rib( current_rib = route['rib'], added_rib = added_rib )

			self.clean_route( route = route )
			self.UL_dict[ _id ] = route
			self.UL_dict[ _id ]['interval'] = GL_dict_item['route']['interval']
		elif route is not None: #from __in_CL_route
			_id = route['_id']

			if "time" in route and "mode" in route:
				self.CL_dict[ _id ]['alive'] = self.AT.update( alive = self.CL_dict[ _id ]['alive'], time = route['time'], mode = route['mode'] )

			if "added_rib" in route:
				self.CL_dict[ _id ]['rib'] = self.__update_rib( current_rib = self.CL_dict[ _id ]['rib'], added_rib = route['added_rib'] )

			self.clean_route( route = self.CL_dict[ _id ] )

			self.UL_dict[ _id ] = self.CL_dict[ _id ]

		self.__process_UL()

	def __process_UL( self, flush = False ):
		if len( self.UL_dict ) > self.buffer_send_size * 20 or flush is True:
			if len( self.UL_dict ) == 0:
				return

			if self.print_UL_processing_time is True:
				temp_TT = Time_Tool( P = self.P )

			if self.print_debug is True:
				self.P.write( "ES_Route_Buffer: __process_UL" )

			data_list = list()

			for _id in self.UL_dict:
				data_JSON_index = dict()
				data_JSON_index['update'] = dict()
				data_JSON_index['update']['_id'] = _id
				data_JSON_index['update']['_type'] = "default_type"
				
				try:
					data_JSON_index['update']['_index'] = self.index + self.UL_dict[_id]['interval']
				except( KeyError ):
					self.UL_dict[_id]['interval'] = "_" + str( self.UL_dict[_id]['interval_start'] ) + "-" + str( self.UL_dict[_id]['interval_end'] )
					data_JSON_index['update']['_index'] = self.index + self.UL_dict[_id]['interval']

				data_JSON = dict()
				data_JSON['doc'] = dict()
				data_JSON['doc']['alive'] = self.UL_dict[_id]['alive']
				data_JSON['doc']['rib'] = self.UL_dict[_id]['rib']
				data_JSON['detect_noop'] = False

				data_list.append( json.dumps( data_JSON_index ) )
				data_list.append( json.dumps( data_JSON ) )

			data_ES = None
			items = None
			status_ok = False
			while status_ok is False:

				status_ok = True
				data_ES = self.ESLI.post_bulk_thread( data_list = data_list, print_server_response = False )
				items = data_ES['items']

				for item in items:
					update = item['update']
					_id = update['_id']

					if "result" not in update and status_ok is True:
						self.P.write( "ES_Route_Buffer: __process_UL: ERROR, sleep 5 seconds" )
						print update
						status_ok = False
						sleep(5)

			items = data_ES['items']
			for item in items:
				if "update" not in item:
					self.P.write_error( "ES_Route_Buffer : __process_UL : 'update' not in item" )
					continue

				update = item['update']
				_id = update['_id']

				if "result" not in update:
					self.P.write_error( "ES_Route_Buffer : __process_UL : 'result' not in update" )
					print update
					continue
				
				if "updated" in update['result']:
					self.__add_CL_route( self.UL_dict[ _id ], _id = _id )
				else:
					self.P.write_error( "ES_Route_Buffer : __process_UL : 'updated' not in update['result']" )

			self.UL_dict = dict()

			if self.print_UL_processing_time is True:
				elapsed_time_float_MS = round( float(temp_TT.get_elapsed_time_S_float()) * float(1000.0), 2 )
				self.P.write( "\tES_Route_Buffer : __process_UL : took " + str(elapsed_time_float_MS) + "ms" )

		return

	def __update_GL_route( self, route ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __update_GL_route" )

		_id = str(route['_id'])

		if "mode" in route and "time" in route:
			self.GL_dict[ str(route['_id']) ]['actions'].append( dict() )

			length = len( self.GL_dict[ str(route['_id']) ]['actions'] )
			self.GL_dict[ _id ]['actions'][ length - 1 ]['mode'] = route['mode']
			self.GL_dict[ _id ]['actions'][ length - 1 ]['time'] = route['time']

		if "added_rib" in route:
			self.GL_dict[ _id ]['added_ribs'].append( route['added_rib'] )

		self.__process_GL()
		return

	def __process_GL( self, flush = False ):
		if len( self.GL_dict ) > self.buffer_send_size or flush is True:
			if len( self.GL_dict ) == 0:
				return

			if self.print_GL_processing_time is True:
				temp_TT = Time_Tool( P = self.P )

			if self.print_debug is True:
				self.P.write( "ES_Route_Buffer: __process_GL" )

			data_list = list()

			for _id in self.GL_dict:
				data_JSON = dict()
				data_JSON['_index'] = self.index + self.GL_dict[_id]['route']['interval']
				data_JSON['_type'] = "default_type"
				data_JSON['_id'] = _id
				data_list.append(data_JSON)

			source_filtering = [ "alive", "rib" ]

			data_ES = self.ESLI.mget( data_list = data_list, source_filtering = source_filtering, print_server_response = False )

			docs = data_ES['docs']
			for x in range( 0, len( docs ) ):
				doc = docs[x]

				if doc['found'] is False:
					self.__add_NL_route( GL_dict_item = self.GL_dict[ str(doc['_id']) ] )
				elif doc['found'] is True:
					self.__add_UL_route( GL_dict_item = self.GL_dict[ str(doc['_id']) ], route = doc['_source'] )

			self.GL_dict = dict()

			if self.print_GL_processing_time is True:
				elapsed_time_float_MS = round( float(temp_TT.get_elapsed_time_S_float()) * float(1000.0), 2 )
				self.P.write( "\tES_Route_Buffer : __process_GL : took " + str(elapsed_time_float_MS) + "ms" )

	def __in_CL_route( self, route ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __in_CL_route" )

		self.__add_UL_route( route = route )
		return

	def __not_in_CL_route( self, route ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __not_in_CL_route" + " " + route['_id'] )

		if str(route['_id']) in self.GL_dict:
			self.P.write_error( "ES_Route_Buffer : __not_in_CL_route : str(route['_id']) in GL_dict" )

		_id = self.__del_key_dict( dict_data = route, key = "_id" )

		self.GL_dict[ _id ] = dict()
		self.GL_dict[ _id ]['_id'] = _id
		self.GL_dict[ _id ]['route'] = route
		self.GL_dict[ _id ]['actions'] = list()

		if "mode" in route and "time" in route:
			self.GL_dict[ _id ]['actions'].append( dict() )
			self.GL_dict[ _id ]['actions'][0]['mode'] = route['mode']
			self.GL_dict[ _id ]['actions'][0]['time'] = route['time']

		self.GL_dict[ _id ]['added_ribs'] = list()

		if "added_rib" in route:
			self.GL_dict[ _id ]['added_ribs'].append( route['added_rib'] )

		self.__process_GL()
		return

	def __add_CL_route( self, route = None, _id = None ):
		if self.print_debug is True:
			self.P.write( "ES_Route_Buffer: __add_CL_route" )

		if route is None:
			self.P.write_error( "ES_Route_Buffer : __add_CL_route : route is None" )

		if _id is not None and '_id' not in route:
			route['_id'] = _id

		if '_id' not in route:
			self.P.write_error( "ES_Route_Buffer : __add_CL_route : _id not in route" )
			return

		self.clean_route( route = route )

		while len( self.CL_dict ) > self.cache_size:
			for key in random.sample( self.CL_dict.keys(), 1000 ):
				del self.CL_dict[key]

		self.CL_dict[ route['_id'] ] = route

	def flush( self ):
		self.P.write( "ES_Route_Buffer: flush: start"  )

		self.IL_list_thread_flush = True
		self.IL_list_thread_flush_busy = True

		while self.IL_list_thread_flush_busy is True:
			sleep( 0.001 )

		self.P.write( "\tES_Route_Buffer: flush: done!", color = 'green' )

	def __flush( self ):
		self.__process_GL( flush = True )
		self.__process_UL( flush = True )
		self.__process_NL( flush = True )

	def __del_key_dict( self, dict_data, key ):
		result = dict_data[key]
		del dict_data[key]
		return result

	def __update_rib( self, current_rib = list(), added_rib = None ):
		if current_rib is None:
			self.P.write_error( "ES_Route_Buffer: __update_rib : current_rib is None" )
			return current_rib

		current_rib.append( added_rib )
		return list(set(current_rib))

	def clean_route( self, route ):
		if "mode" in route:
			del route['mode']

		if "time" in route:
			del route['time']

		if "added_rib" in route:
			del route['added_rib']






		




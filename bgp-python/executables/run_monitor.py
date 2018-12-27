import os, sys

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

import time, hashlib
from ES_interface import ES_Interface
from printer import Printer
from time import sleep

class Show_Stats():
	ES = None
	P = None
	STATS = None
	data_dict = dict()
	sync_dict = dict()

	def __init__( self ):
		self.P = Printer()
		self.ES = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False )
		self.STATS = "bgp-stats"
		self.data_dict = dict()

	def __get_data( self ):
		data_JSON = dict()
		data_JSON['size'] = 8000
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		data_ES = None

		while data_ES is None:
			data_ES = self.ES.search( index = self.STATS, data_JSON = data_JSON, filter_path = "hits.hits._source", print_server_response = False )
			if data_ES is None:
				sleep(1)

		if "hits" in data_ES:
				data_ES = data_ES['hits']
		else:
			return

		if "hits" in data_ES:
			data_ES = data_ES['hits']
		else:
			return

		for x in range( 0, len( data_ES ) ):
			_source = None

			if "_source" in data_ES[x]:
				_source = data_ES[x]['_source']
				self.data_dict[_source['RRC_number']] = _source

	def __print_header_top( self ):
		print "\n\n\n\n\n\n"
		self.P.write( data = "|-----------------------------------------------------------|", include_time_stamp = False )
		self.P.write( data = "| #  | ALIVE | STATUS | COUNTER |  MS  |  PS  | TODO | DONE |", include_time_stamp = False )
		self.P.write( data = "|-----------------------------------------------------------|", include_time_stamp = False )

	def __print_header_bottom( self ):
		self.P.write( data = "|-----------------------------------------------------------|", include_time_stamp = False )

	def __print_total( self ):
		done = 0
		todo = 0
		ps = 0

		for RRC_number in self.data_dict:
			_source = self.data_dict[RRC_number]
			#print _source

			alive = int( time.time() ) - int(_source['date'])
			if alive > 60:
				continue

			mode = _source['mode']

			if "view" in mode or "update" in mode:
				ps += _source['ps']
			
			done += _source['done']
			todo += _source['todo']

		ps = ps / 1000

		result = "| Total PS - " + str(int(ps)) + "k | "
		result = result + " Total TODO - " + str(int(todo)) + " | "
		result = result + " Total DONE - " + str(int(done)) + " | "

		self.P.write( data = result, include_time_stamp = False )

	def __print_line( self, _source ):
		result = "| "
		result = str(result) + str(_source['RRC_number']).zfill(2) + " |"

		current_time_epoch = int( time.time() )
		
		if _source['RRC_number'] in self.sync_dict:
			alive = current_time_epoch - int(_source['date']) + int(self.sync_dict[_source['RRC_number']])
		else:
			alive = current_time_epoch - int(_source['date'])
		
		mode = str(_source['mode'])

		if alive > 120:
			if not "closed" in mode:
				return

		if "closed" in mode:
			result = str(result) + " ----- |"
		else:
			result = str(result) + str(alive).rjust(5) + "s |"

		if len( mode ) == 4:
			mode = "  " + str(mode) + "  |"
		elif len( mode ) == 5:
			mode = "  " + str(mode) + " |"
		else:
			mode = " " + str(mode) + " |"

		result = str(result) + str(mode)

		counter = int(_source['count']/1000)
		ms = round( float(_source['ms']), 1)
		ps = int(_source['ps'])
		todo = int(_source['todo'])
		done = int(_source['done'])

		if "view" not in mode and "update" not in mode and "loaded" not in mode:
			counter = ""
			ms = ""
			ps = ""
			todo = ""
			done = ""
		else:
			counter = str(counter) + "k"

		result = str(result) + str(counter).rjust(8) + " |"
		result = str(result) + str(ms).rjust(5) + " |"
		result = str(result) + str(ps).rjust(5) + " |"
		result = str(result) + str(todo).rjust(5) + " |"
		result = str(result) + str(done).rjust(5) + " |"

		self.P.write( data = result, include_time_stamp = False )

	def __clear_terminal( self ):
		os.system('cls' if os.name == 'nt' else 'clear')

	def run( self ):
		while True:
			sleep(0.25)
			self.__get_data()

			self.__clear_terminal()
			self.__print_header_top()

			for RRC_number in sorted( self.data_dict.keys() ):
				self.__print_line( _source = self.data_dict[RRC_number] )

			self.__print_header_bottom()
			self.__print_total()
			self.__print_header_bottom()

SS = Show_Stats()
SS.run()

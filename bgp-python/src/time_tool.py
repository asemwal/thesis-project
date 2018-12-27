import sys, os, datetime
import json, time, thread, requests, calendar
from printer import Printer

class Time_Tool:
	start_time_float = None
	stop_time_float = None
	P = None

	def __init__( self, P = None, no_output = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Time_Tool: __init__: P is None" )

		if no_output is False:
			self.P.write( "Time_Tool: Loading...", color = 'cyan' )

		self.start()

	def start( self ):
		self.start_time_float = time.time()

	def __stop( self ):
		self.stop_time_float = time.time()

	def get_elapsed_time_S_str( self ):
		self.__stop()
		elapsed_time = float( self.stop_time_float ) - float( self.start_time_float )
		return str(float("{0:.2f}".format(elapsed_time))) + "s"

	def get_elapsed_time_S_float( self ):
		self.__stop()
		elapsed_time = float( self.stop_time_float ) - float( self.start_time_float )
		return float(elapsed_time)

	def print_elapsed_time( self, data_text = None ):
		elapsed_time_float_S = self.get_elapsed_time_S_float()

		unit_str = "s"

		if elapsed_time_float_S < 1.0:
			elapsed_time_float_S = float(elapsed_time_float_S) * 1000
			unit_str = "ms"

		if elapsed_time_float_S < 1.0:
			elapsed_time_float_S = float(elapsed_time_float_S) * 1000
			unit_str = "us"

		if data_text is None:
			self.P.write( "Time_Tool: print_elapsed_time:" + str(round(elapsed_time_float_S,2)) + str(unit_str) + " elapsed" )
		else:
			self.P.write( "Time_Tool: print_elapsed_time:" + str(data_text) + ": " + str(round(elapsed_time_float_S,2)) + str(unit_str) + " elapsed" )

	def __get_time_epoch( self, time_str, format ):
		time_epoch = None

		try:
			time_epoch = int(time_str)

			if time_epoch > 3000:
				return time_epoch
		except( ValueError, TypeError ):
			time_epoch = None

		try:
			time_epoch = calendar.timegm( time.strptime( time_str, format ) )
		except( ValueError, TypeError ):
			time_epoch = None

		return time_epoch

	def get_time_interval( self, time_start_str = None, time_end_str = None ):
		if time_start_str is None:
			self.P.write_error( "Time_Tool: get_time_interval: time_start_str is None" )
			return None

		if time_end_str is None:
			self.P.write_error( "Time_Tool: get_time_interval: time_end_str is None" )
			return None

		time_interval = list()

		time_start_epoch = self.get_time_epoch( time_str = time_start_str )
		time_end_epoch = self.get_time_epoch( time_str = time_end_str )

		time_interval.append( time_start_epoch )
		time_interval.append( time_end_epoch )

		return time_interval

	def get_time_interval_routes( self, time_epoch = None, interval = None ):
		if time_epoch is None:
			self.P.write_error( "Time_Tool: get_time_interval_routes: time_epoch is None" )
			return None

		if interval is None:
			interval = 172800	# Do Not Change This Value...
		else:
			interval = int(interval)
			
		interval_start = time_epoch / interval * interval	
		interval_end = interval_start + interval				

		interval_str = "_" + str(interval_start) + "-" + str(interval_end)

		return [ interval_start, interval_end, interval_str ]

	def get_time_epoch( self, time_str = None, no_output = False ):
		if time_str is None:
			self.P.write_error( "Time_Tool: get_time_epoch: time_str is None" )
			return None

		time_str = str(time_str)

		format_list = [ '%Y', '%Y-%m', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S UTC' ]

		if len( time_str ) > 0 and " " == time_str[ len(time_str) - 1 ]:
			time_str = time_str[:-1]

		for format in format_list:
			time_epoch = self.__get_time_epoch( time_str = time_str, format = format )
			if time_epoch is not None:
				return time_epoch

		if no_output is False:
			self.P.write_error( "Time_Tool: get_time_epoch: expecting %Y, %Y-%m, %Y-%m-%d, %Y-%m-%d %H:%M:%S, %Y-%m-%d %H:%M:%S UTC or epoch, got: " + time_str )
	
		return None

	def get_time_str( self, time_epoch = None ):
		if time_epoch is None:
			self.P.write_error( "Time_Tool: get_time_str: time_epoch is None" )
			return None

		return datetime.datetime.utcfromtimestamp( time_epoch ).strftime('%Y-%m-%d %H:%M:%S UTC')

	def get_time_interval_str( self, time_interval = None ):
		if time_interval is None:
			self.P.write_error( "Time_Tool: get_time_interval_str: time_interval is None" )
			return None
			
		time_start_str = self.get_time_str( time_epoch = time_interval[0] )
		time_end_str = self.get_time_str( time_epoch = time_interval[1] )
		
		return [ time_start_str, time_end_str ]






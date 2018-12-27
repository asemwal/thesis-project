import datetime, json, calendar, time

from termcolor import colored
from params_tool import Params_Tool
from printer import Printer
from time_tool import Time_Tool

class CLI_Input_Handler:
	PT = None
	P = None
	TT = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] CLI_Input_Handler : __init__ : P is None", color = 'yellow', attrs = ['bold'] )

		self.P.write( "CLI_Input_Handler: Loading...", color = 'cyan')
		self.TT = Time_Tool( P = self.P )

		self.PT = Params_Tool( P = self.P )

	def __is_int( self, data_str ):
		if str( data_str ).isdigit():
			return True
		else:
			return False

	def print_help( self ):
		include_time_stamp = False

		self.P.write( include_time_stamp = include_time_stamp )
		self.P.write( include_time_stamp = include_time_stamp, data = "   Use 'quit' or 'exit' to terminate the program ", color = 'blue' )
		self.P.write( include_time_stamp = include_time_stamp, data = "   The listed commands below can be used: ")
		self.P.write( include_time_stamp = include_time_stamp, data = "   " )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- GENERAL -*-*-*- :", color = 'blue' ) 
		#self.P.write( include_time_stamp = include_time_stamp, data = "       --calculate-rrc-coverage: " + colored( "calculate which part of the IP4-space a route collector is collecting", color = 'yellow' ) )
		#self.P.write( include_time_stamp = include_time_stamp, data = "                 --burst-prefix: " + colored( "drawing impact value of a prefix", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                  --draw-prefix: " + colored( "drawing a prefix", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "            --clear-temp-folder: " + colored( "clear content in the tmp folder", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "          --clear-output-folder: " + colored( "clear content in the output folder", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "          --reset-input-history: " + colored( "resetting input history", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- BGP-LINKS -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "                  --reset-links: " + colored( "delete and then create bgp-links ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                 --create-links: " + colored( "create bgp-links ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                 --delete-links: " + colored( "delete bgp-links ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                 --update-links: " + colored( "downloading RIPE and RouteViews download files links of the last 2 months to bgp-links ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                   --load-links: " + colored( "downloading RIPE and RouteViews download files links to the bgp-links ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "              --reset-processed: " + colored( "resetting bgp-links ElasticSearch links processed field to not processed (0)", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- BGP-STATS -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "                  --reset-stats: " + colored( "delete and then create bgp-stats ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*-  BGP-ROUTES -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "                 --reset-routes: " + colored( "delete all bgp-routes_* ElasticSearch indexes", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "              --download-routes: " + colored( "download RIPE and/or RouteViews RRC routes to the bgp-routes-* ElasticSearch indexes", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- BGP-WITHDRAWS -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "              --reset-withdraws: " + colored( "delete and then create bgp-withdraws ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "             --create-withdraws: " + colored( "create bgp-withdraws ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "             --delete-withdraws: " + colored( "delete bgp-withdraws ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "            --process-withdraws: " + colored( "process downloaded withdraws from the bgp-withdraws ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- BGP-STATE-CHANGE -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "           --reset-state-change: " + colored( "delete and then create bgp-state-change ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "          --create-state-change: " + colored( "create bgp-state-change ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "          --delete-state-change: " + colored( "delete bgp-state-change ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- BGP-RELATIONS -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "              --reset-relations: " + colored( "delete and then create bgp-relations ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "             --create-relations: " + colored( "create bgp-relations ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "             --delete-relations: " + colored( "delete bgp-relations ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "      --flush-AS-rank-relations: " + colored( "flush all local AS Rank relations to bgp-relations ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                           : -*-*-*- BGP-TRACE-ROUTES -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "           --reset-trace-routes: " + colored( "delete and then create bgp-trace-routes ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "          --create-trace-routes: " + colored( "create bgp-trace-routes ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "          --delete-trace-routes: " + colored( "delete bgp-trace-routes ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "  --flush-trace-routes-from-CSV: " + colored( "flush trace routes found in a CSV to bgp-trace-routes ElasticSearch index", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- INTERFACES -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp, data = "                --cache-AS-rank: " + colored( "download and cache all records from AS Rank", color = 'yellow' ) )
		#self.P.write( include_time_stamp = include_time_stamp, data = "               --cache-BGP-view: " + colored( "download and cache all records from BGP View", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "             --cache-peering-DB: " + colored( "download and cache all records from peering DB", color = 'yellow' ) )
		self.P.write( include_time_stamp = include_time_stamp, data = "                               : -*-*-*- END -*-*-*- :", color = 'blue' ) 
		self.P.write( include_time_stamp = include_time_stamp )

	def get_function( self, params = dict() ):
		function = None

		if "help" in params:
			self.print_help()
			function = "help"
	
		elif "clear-temp-folder" in params:
			self.P.write( "\tFUNCTION: clear content in the tmp folder")
			function = "clear-temp-folder"
		elif "clear-output-folder" in params:
			self.P.write( "\tFUNCTION: clear content in the output folder")
			function = "clear-output-folder"
		elif "reset-processed" in params:
			self.P.write( "\tFUNCTION: resetting bgp-links ElasticSearch links processed field to not processed (0)")
			function = "reset-processed"
		elif "reset-links" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-links ElasticSearch index")
			function = "reset-links"
		elif "create-links" in params:
			self.P.write( "\tFUNCTION: create bgp-links ElasticSearch index")
			function = "create-links"
		elif "delete-links" in params:
			self.P.write( "\tFUNCTION: delete bgp-links ElasticSearch index")
			function = "delete-links"
		elif "update-links" in params:
			self.P.write( "\tFUNCTION: downloading RIPE and RouteViews download files links of the last 2 months to bgp-links ElasticSearch index")
			function = "update-links"
		elif "load-links" in params:
			self.P.write( "\tFUNCTION: downloading RIPE and RouteViews download files links to the bgp-links ElasticSearch index")
			function = "load-links"
		elif "burst-prefix" in params:
			self.P.write( "\tFUNCTION: drawing progress of a prefix")
			function = "burst-prefix"
		elif "draw-prefix" in params:
			self.P.write( "\tFUNCTION: drawing a prefix")
			function = "draw-prefix"
		elif "reset-stats" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-stats ElasticSearch index")
			function = "reset-stats"
		elif "delete-routes" in params:
			self.P.write( "\tFUNCTION: delete all bgp-routes-* ElasticSearch indexes")
			function = "delete-routes"
		elif "download-routes" in params:
			self.P.write( "\tFUNCTION: download RIPE and/or RouteViews RRC routes to the bgp-routes-* ElasticSearch indexes")
			function = "download-routes"
		elif "custom-loop" in params:
			self.P.write( "\tFUNCTION: run function custom_loop() in ripe_interface.py")
			function = "custom-loop"
		elif "reset-withdraws" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-withdraws ElasticSearch index")
			function = "reset-withdraws"
		elif "delete-withdraws" in params:
			self.P.write( "\tFUNCTION: delete bgp-withdraws ElasticSearch index")
			function = "delete-withdraws"
		elif "create-withdraws" in params:
			self.P.write( "\tFUNCTION: create bgp-withdraws ElasticSearch index")
			function = "create-withdraws"
		elif "process-withdraws" in params:
			self.P.write( "\tFUNCTION: process downloaded withdraws from the bgp-withdraws ElasticSearch index")
			function = "process-withdraws"
		elif "reset-coverage" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-coverage ElasticSearch index")
			function = "reset-coverage"
		elif "create-coverage" in params:
			self.P.write( "\tFUNCTION: create bgp-coverage ElasticSearch index")
			function = "create-coverage"
		elif "delete-coverage" in params:
			self.P.write( "\tFUNCTION: delete bgp-coverage ElasticSearch index")
			function = "delete-coverage"
		elif "reset-state-change" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-state-change ElasticSearch index")
			function = "reset-state-change"
		elif "create-state-change" in params:
			self.P.write( "\tFUNCTION: create bgp-state-change ElasticSearch index")
			function = "create-state-change"
		elif "delete-state-change" in params:
			self.P.write( "\tFUNCTION: delete bgp-state-change ElasticSearch index")
			function = "delete-state-change"
		elif "cache-AS-rank" in params:
			self.P.write( "\tFUNCTION: download and cache all records from AS Rank")
			function = "cache-AS-rank"
		elif "cache-BGP-view" in params:
			self.P.write( "\tFUNCTION: download and cache all records from BGP View")
			function = "cache-BGP-view-"
		elif "cache-peering-DB" in params:
			self.P.write( "\tFUNCTION: download and cache all records from Peering DB")
			function = "cache-peering-DB"
		elif "reset-relations" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-relations ElasticSearch index")
			function = "reset-relations"
		elif "delete-relations" in params:
			self.P.write( "\tFUNCTION: delete bgp-relations ElasticSearch index")
			function = "delete-relations"
		elif "create-relations" in params:
			self.P.write( "\tFUNCTION: create bgp-relations ElasticSearch index")
			function = "create-relations"
		elif "flush-AS-rank-relations" in params:
			self.P.write( "\tFUNCTION: flush all local AS Rank relations to bgp-relations ElasticSearch index")
			function = "flush-AS-rank-relations"
		elif "reset-trace-routes" in params:
			self.P.write( "\tFUNCTION: delete and then create bgp-trace-routes ElasticSearch index")
			function = "reset-trace-routes"
		elif "delete-trace-routes" in params:
			self.P.write( "\tFUNCTION: delete bgp-trace-routes ElasticSearch index")
			function = "delete-trace-routes"
		elif "create-trace-routes" in params:
			self.P.write( "\tFUNCTION: create bgp-trace-routes ElasticSearch index")
			function = "create-trace-routes"
		elif "flush-trace-routes-from-CSV" in params:
			self.P.write( "\tFUNCTION: flush trace routes found in a CSV to bgp-trace-routes ElasticSearch index")
			function = "flush-trace-routes-from-CSV"
		elif "reset-input-history" in params:
			self.P.write( "\tFUNCTION: resetting input history")
			function = "reset-input-history"

		if function is None:
			if not "hide-info" in params:
				self.P.write( "\tInfo: no (good) parameter given, use --help", color = 'red')	

			function = None

		return function

	def get_AS_numbers( self, function = None, params = dict() ):
		if function is None:
			return None

		AS_Number = None

		use = False
		if "burst-prefix" in function or "draw-prefix" in function:
			use = True

		if use is False:
			return None

		if "asn" not in params:
			self.P.write( "\tInput Error: --asn parameter not given", color = 'red')
			return None
		elif params['asn'] is None:
			self.P.write( "\tInput Error: --asn parameter is empty", color = 'red')
			return None

		AS_Numbers = list()

		try:
			for AS_Number in params['asn']:
				AS_Numbers.append( int(AS_Number) )

		except( TypeError ):
			self.P.write( "\tInput Error: --asn parameter is not an integer", color = 'red')
			return

		self.P.write( "\tASN: " + str( AS_Numbers ))
		return AS_Numbers

	def get_prefix( self, function = None, params = dict() ):
		if function is None:
			return None

		prefix = None

		use = False
		if "burst-prefix" in function or "draw-prefix" in function:
			use = True

		if use is False:
			return None

		if "prefix" not in params:
			self.P.write( "\tInput Error: --prefix parameter not given", color = 'red')
			return None
		elif params['prefix'] is None:
			self.P.write( "\tInput Error: --prefix parameter is empty", color = 'red')
			prefix = "all"
		elif len( params['prefix'] ) > 0:
			prefix = params['prefix']

		self.P.write( "\tPREFIX: " + str( prefix ))
		return prefix

	def get_RRC_range( self, function = None, params = dict() ):
		if function is None:
			return None

		use = False
		if function == "reset-processed" or function == "update-links" or function == "load-links" or function == "load-RRC-coverage":
			use = True
		elif function == "burst" or function == "draw-prefix" or function == "download-routes" or function == "process-withdraws" or function == "custom-loop":
			use = True

		if use is False:
			return None

		RRC_range = list()
		RRC_range.append( None )
		RRC_range.append( None )

		if "from-rrc" in params:
			if params['from-rrc'] is None:
				self.P.write( "\tInput Error: --from-rrc parameter is empty", color = 'red')
			elif len(params['from-rrc']) > 1:
				self.P.write( "\tInput Error: --from-rrc parameter contains more than one argument", color = 'red')
			elif self.__is_int( params['from-rrc'][0] ) is False:
				self.P.write( "\tInput Error: --from-rrc parameter argument is not a integer", color = 'red')
			else:
				RRC_range[0] = int(params['from-rrc'][0])

		if "to-rrc" in params:
			if params['to-rrc'] is None:
				self.P.write( "\tInput Error: --to-rrc parameter is empty", color = 'red')
			elif len(params['to-rrc']) > 1:
				self.P.write( "\tInput Error: --to-rrc parameter contains more than one argument", color = 'red')
			elif self.__is_int( params['to-rrc'][0] ) is False:
				self.P.write( "\tInput Error: --to-rrc parameter argument is not a integer", color = 'red')
			else:
				RRC_range[1] = int(params['to-rrc'][0])

		if "rrc" in params:
			if params['rrc'] is None:
				self.P.write( "\tInput Error: --rrc parameter is empty", color = 'red')
			elif len(params['rrc']) > 1:
				self.P.write( "\tInput Error: --rrc parameter contains more than one argument", color = 'red')
			elif self.__is_int( params['rrc'][0] ) is False:
				self.P.write( "\tInput Error: --rrc parameter argument is not a integer", color = 'red')
			elif int(params['rrc'][0]) < 0:
				self.P.write( "\tInput Error: --rrc parameter argument smaller than 0", color = 'red')
			elif int(params['rrc'][0]) > 42:
				self.P.write( "\tInput Error: --rrc parameter argument greater than 40", color = 'red')
			else:
				RRC_range[0] = int(params['rrc'][0])
				RRC_range[1] = int(params['rrc'][0])

		if "from-rrc" not in params and "to-rrc" not in params and "rrc" not in params:
			self.P.write( "\tInput Warning: --from-rrc, --to-rrc or --rrc parameter(s) not given", color = 'yellow')

		if RRC_range[0] is None:
			RRC_range[0] = 0

		if RRC_range[1] is None:
			RRC_range[1] = 42

		if RRC_range[0]	< 0:
			RRC_range[0] = 0
			self.P.write( "\tInput Error: --from-rrc argument smaller than 0", color = 'red')

		if RRC_range[1]	> 42:
			RRC_range[1] = 42
			self.P.write( "\tInput Error: --to-rrc argument greater than 42", color = 'red')

		if RRC_range[0] > RRC_range[1]:
			RRC_range[0] = RRC_range[1]
			self.P.write( "\tInput Error: --from-rrc argument greater than --to-rrc argument", color = 'red')

		if RRC_range[0] == RRC_range[1]:
			self.P.write( "\tRRC_RANGE: RRC" + str( RRC_range[0] ).zfill(2))
		else:
			self.P.write( "\tRRC_RANGE: RRC" + str( RRC_range[0] ).zfill(2) + " to RRC" + str( RRC_range[1] ).zfill(2))

		return RRC_range

	def get_epoch_time( self, function = None, params = dict() ):
		if function is None:
			return None

		use = False
		if "time" in function:
			use = True

		if "draw-prefix" in function:
			use = True

		if use is False:
			return

		time_epoch = None

		if "time" in params and params['time'] is not None:
			time_str = ""

			for temp in params['time']:
				if len(time_str) > 0:
					time_str = time_str + " " + str(temp)
				else:
					time_str = str(temp)

			time_epoch = self.TT.get_time_epoch( time_str = time_str, no_output = True )

			if time_epoch is None:
				self.P.write( "\tInput Error: --time param wrong, expecting YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS UTC, YYYY-MM-DD, YYYY-MM, YYYY, or epoch, got: " + str(time_str), color = 'red' )
				return None

		if time_epoch is None:
			self.P.write( "\tInput Error: --time parameter not given, expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS UTC, YYYY-MM-DD, YYYY-MM, YYYY, or epoch", color = 'red')
			return None

		single_time = datetime.datetime.utcfromtimestamp( time_epoch ).strftime('%Y-%m-%d %H:%M:%S UTC')
		self.P.write( "\tTIME: " + str(single_time) + " (" + str(time_epoch) + ")")

		return time_epoch

	def get_time_interval( self, function = None, params = dict() ):
		if function is None:
			return None

		use = False
		if "reset-processed" in function or "load-links" in function or "load-RRC-coverage" in function:
			use = True
		elif "burst-prefix" in function or "download-routes" in function or "process-withdraws" in function:
			use = True

		if use is False:
			return None

		time_interval = list()

		from_epoch = None
		to_epoch = None
		default = True

		if "from" in params and params['from'] is not None and len( params['from'] ) > 0:
			time_str = ""
			for item in params['from']:
				time_str = time_str + str(item) + " "

			from_epoch = self.TT.get_time_epoch( time_str = time_str, no_output = True )

			if from_epoch is None:
				self.P.write( "\tInput Error: --from param wrong, expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS UTC, YYYY-MM-DD, YYYY-MM, YYYY, or epoch", color = 'red' )
			else:
				default = False


		if "from" not in params:
			if not "hide-info" in params:
				self.P.write( "\tInfo: --from parameter not given, expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS UTC, YYYY-MM-DD, YYYY-MM, YYYY, or epoch", color = 'cyan')	

		if "to" in params and params['to'] is not None and len( params['to'] ) > 0:
			time_str = ""
			for item in params['to']:
				time_str = time_str + str(item) + " "

			to_epoch = self.TT.get_time_epoch( time_str = time_str, no_output = True )

			if to_epoch is None:
				self.P.write( "\tInput Error: --to param wrong, expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS UTC, YYYY-MM-DD, YYYY-MM, YYYY, or epoch", color = 'red' )
			else:
				default = False

		if "to" not in params:
			if not "hide-info" in params:
				self.P.write( "\tInfo: --to parameter not given, expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS UTC, YYYY-MM-DD, YYYY-MM, YYYY or epoch", color = 'cyan')

		if from_epoch is None:
			from_epoch = 0

		if to_epoch is None:
			to_epoch = 2147483647

		if from_epoch > to_epoch:
			self.P.write( "\tInput Error: from_time > to_time, using entire range...", color = 'red')
			from_epoch = 0
			to_epoch = 2147483647

		from_time = datetime.datetime.utcfromtimestamp( from_epoch ).strftime('%Y-%m-%d %H:%M:%S UTC')
		to_time = datetime.datetime.utcfromtimestamp( to_epoch ).strftime('%Y-%m-%d %H:%M:%S UTC')

		time_interval.append( from_epoch )
		time_interval.append( to_epoch )

		if default is True:
			self.P.write( "\tINTERVAL: " + str(from_time) + " (" + str(from_epoch) + ") to " + str(to_time) + " (" + str(to_epoch) + ") | (default)")
		else:
			self.P.write( "\tINTERVAL: " + str(from_time) + " (" + str(from_epoch) + ") to " + str(to_time) + " (" + str(to_epoch) + ")")

		return time_interval

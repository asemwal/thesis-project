import sys, os, json, time

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from ask_tool import Ask_Tool
from time_tool import Time_Tool
from clear_screen_tool import Clear_Screen_Tool
from ES_interface import ES_Interface

class ES_Interaction():
	P = None
	AT = None
	TT = None

	ES = None
	ROUTES = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer()
		self.AT = Ask_Tool( P = self.P )
		self.TT = Time_Tool( P = self.P )
		self.ES = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False )
		self.ROUTES = self.ES.get_ES_ROUTES_index_name()

	def exists_index( self ):
		[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = 1473120000 )

		data_ES = self.ES.exists_index( index = self.ROUTES + interval_str )

		self.P.write( "ES_Interaction: exists_index: data_ES:", color = 'green' )
		self.P.write_JSON( data_ES )

	def search( self ):
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html
		data_JSON = dict()
		data_JSON['size'] = 1
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		#filter_path = "hits.hits._source.path"
		filter_path = None

		data_ES = self.ES.search( index = self.ROUTES + "_*", data_JSON = data_JSON, filter_path = filter_path, print_server_response = False )

		self.P.write( "ES_Interaction: search: data_ES:", color = 'green' )
		self.P.write_JSON( data_ES )

	def search_and_scroll( self ):
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-scroll.html
		size = 1

		data_JSON = dict()
		data_JSON['size'] = size
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()

		#filter_path must be None!
		data_ES = self.ES.search( index = self.ROUTES + "*", data_JSON = data_JSON, scroll = "1m", filter_path = None, print_server_response = False )

		self.P.write( "ES_Interaction: search_and_scroll: data_ES:", color = 'green' )
		self.P.write_JSON( data_ES )

		scroll_id = data_ES['_scroll_id']
		amount_left = data_ES['hits']['total'] - size

		finished = False
		while finished is False:
			if amount_left < 0:
				amount_left = 0

			data_ES = self.ES.scroll( index = self.ROUTES + "*", scroll = "1m", scroll_id = scroll_id, print_server_response = False )

			self.P.write( "ES_Interaction: search_and_scroll: data_ES: amount_left = " + str(amount_left), color = 'green' )
			self.P.write_JSON( data_ES )

			amount_left -= size

	def msearch( self ):
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/search-multi-search.html
		data_list = list()

		data_JSON = dict()
		data_JSON['size'] = 1
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()
		data_list.append( data_JSON )

		data_JSON = dict()
		data_JSON['size'] = 1
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()
		data_list.append( data_JSON )

		#filter_path = "hits.hits._source.path"
		filter_path = None

		data_ES = self.ES.msearch( index = self.ROUTES + "_*", data_list = data_list, filter_path = filter_path, print_server_response = False )

		self.P.write( "ES_Interaction: msearch: data_ES:", color = 'green' )
		self.P.write_JSON( data_ES )

	def msearch_thread( self ):
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/search-multi-search.html
		data_list = list()

		data_JSON = dict()
		data_JSON['size'] = 1
		data_JSON['query'] = dict()
		data_JSON['query']['match_all'] = dict()
		data_list.append( data_JSON )

		counter = 100000
		while counter > 0:
			data_JSON = dict()
			data_JSON['size'] = 1
			data_JSON['query'] = dict()
			data_JSON['query']['match_all'] = dict()
			data_list.append( data_JSON )
			counter -= 1

		#filter_path = "hits.hits._source.path"
		filter_path = None

		data_ES = self.ES.msearch_thread( index = self.ROUTES + "_*", data_list = data_list, max_number_of_threads = 5, filter_path = filter_path, print_server_response = True )

		self.P.write( "ES_Interaction: msearch: data_ES:", color = 'green' )
		self.P.write_JSON( data_ES )

	def get_id( self ):
		[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = 1473120000 )

		data_ES = self.ES.get_id( index = self.ROUTES + interval_str , id = "165121415680282637774edf7a59855405593e7fac462aea32bec1792ea9129a", filter_path = None, print_server_response = True )

		self.P.write( "ES_Interaction: get_id: data_ES:", color = 'green' )
		self.P.write_JSON( data_ES )

	def mget_ids( self ):
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-multi-get.html
		[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = 1473120000 )

		ids = list()
		ids.append("165121415680282637774edf7a59855405593e7fac462aea32bec1792ea9129a")
		ids.append("e73596f776440eedada28915e9b95871d22721cd5f15f608176b70105d6d7dfc")

		source_filtering = [ "alive", "rib" ]

		data_ES = self.ES.mget_ids( index = self.ROUTES + interval_str, ids = ids, filter_path = None, source_filtering = source_filtering, print_server_response = False )

		self.P.write( "ES_Interaction: get_id: mget_ids:", color = 'green' )
		self.P.write_JSON( data_ES )

	def mget( self ):
		#https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-multi-get.html
		[ interval_start, interval_end, interval_str ] = self.TT.get_time_interval_routes( time_epoch = 1473120000 )

		data_list = list()

		data_JSON = dict()
		data_JSON['_index'] = self.ROUTES + interval_str
		data_JSON['_type'] = "default_type"
		data_JSON['_id'] = "165121415680282637774edf7a59855405593e7fac462aea32bec1792ea9129a"
		data_list.append(data_JSON)

		data_JSON = dict()
		data_JSON['_index'] = self.ROUTES + interval_str
		data_JSON['_type'] = "default_type"
		data_JSON['_id'] = "e73596f776440eedada28915e9b95871d22721cd5f15f608176b70105d6d7dfc"
		data_list.append(data_JSON)

		source_filtering = [ "alive", "rib" ]

		data_ES = self.ES.mget( data_list = data_list, filter_path = None, source_filtering = source_filtering, print_server_response = False )

		self.P.write( "ES_Interaction: get_id: mget:", color = 'green' )
		self.P.write_JSON( data_ES )
	
	

	def run( self ):
		self.P.write( "ES_Interaction: run: start", color = 'green' ) 
		self.P.write( "\t(1) - exists_index" ) 
		self.P.write( "\t(2) - search" ) 
		self.P.write( "\t(3) - search_and_scroll" ) 
		self.P.write( "\t(4) - msearch" ) 
		self.P.write( "\t(5) - msearch_thread" ) 
		self.P.write( "\t(6) - get_id" ) 
		self.P.write( "\t(7) - mget_ids" ) 
		self.P.write( "\t(8) - mget" ) 
		mode = self.AT.ask( question = "Select mode (1/2/3/4/5/6/7/8):", expect_list = range( 1, 8 + 1 ) )

		if mode == "1":
			self.exists_index()
		elif mode == "2":
			self.search()
		elif mode == "3":
			self.search_and_scroll()
		elif mode == "4":
			self.msearch()
		elif mode == "5":
			self.msearch_thread()
		elif mode == "6":
			self.get_id()
		elif mode == "7":
			self.mget_ids()
		elif mode == "8":
			self.mget()

ES_Interaction().run()
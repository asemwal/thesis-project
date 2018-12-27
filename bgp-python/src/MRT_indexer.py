import sys, os, datetime, time, urllib2, urllib, requests, json, hashlib, shutil, glob, gzip, struct, base64, wget, calendar, copy

from ES_interface import ES_Interface
from printer import Printer
from string_tool import String_Tool
from file_tool import File_Tool
from calendar import timegm
from are_you_sure_tool import Are_You_Sure_Tool
from random import randint

class MRT_Indexer():
	P = None
	ESI = None
	ST = None
	FT = None
	ARST = None

	LINKS = None

	data_list = None
	ids = None
	RANDOM_STRING = None

	def __init__( self, P = None, ESI = None, MRTD = None, LINKS = None, TYPE_UPDATE = None, TYPE_RIB = None):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.write_warning( "MRT_Indexer: __init__ : P is None" )

		self.RANDOM_STRING = "_" + str(randint(0, 1000000000))
		self.P.write( "MRT_Indexer: Loading... (RANDOM_STRING = " + self.RANDOM_STRING + ")", color = 'cyan' )		
		self.ARST = Are_You_Sure_Tool( P = self.P, program_name = "MRT_Indexer" )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.write_warning( "MRT_Indexer: __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P )
			
		if MRTD is not None:
			self.MRTD = MRTD
		else:
			self.write_warning( "MRT_Indexer: __init__ : MRTD is None" )
			self.write_warning( "MRT_Indexer: __init__ : cannot use function reset_processed()" )

		if LINKS is None:
			self.P.write_warning( "MRT_Indexer: __init__: LINKS is None" )
			self.P.write_warning( "MRT_Indexer: __init__: setting LINKS = 'bgp-links'" )
			self.LINKS = "bgp-links"
		else:
			self.LINKS = LINKS

		if TYPE_UPDATE is None:
			self.P.write_warning( "MRT_Indexer: __init__: TYPE_UPDATE is None" )
			self.P.write_warning( "MRT_Indexer: __init__: setting TYPE_UPDATE = 0" )
			self.TYPE_UPDATE = 0
		else:
			self.TYPE_UPDATE = TYPE_UPDATE

		if TYPE_RIB is None:
			self.P.write_warning( "MRT_Indexer: __init__: TYPE_RIB is None" )
			self.P.write_warning( "MRT_Indexer: __init__: setting TYPE_RIB = 1" )
			self.TYPE_RIB = 1
		else:
			self.TYPE_RIB = TYPE_RIB

		self.ST = String_Tool()
		self.FT = File_Tool( base_path = "tmp", P = self.P, program_name = "MRT_Indexer" )

		self.__reset()
		self.setup_links_index()

	def __reset( self ):
		self.data_list = list()
		self.ids = list()

	def setup_links_index( self, print_server_response = False ):
		if self.ESI.exists_index( index = self.LINKS ) is False:
			self.P.write( "MRT_Indexer: check_ES_link_index_exists: ElasticSearch index '" + str(self.LINKS) + "' does not exists, creating..." )
			self.create_links_index( print_server_response = print_server_response )

	def create_links_index( self, print_server_response = False ):
		settings_JSON = dict()
		settings_JSON['number_of_shards'] = 2
		settings_JSON['number_of_replicas'] = 0
		settings_JSON['index.routing.allocation.exclude.size'] = "small"

		mappings_JSON = dict()
		mappings_JSON["link"] = dict()
		mappings_JSON["link"]["type"] = "text"
		mappings_JSON["RRC_number"] = dict()
		mappings_JSON["RRC_number"]["type"] = "integer"
		mappings_JSON["type"] = dict()
		mappings_JSON["type"]["type"] = "integer"
		mappings_JSON["processed"] = dict()
		mappings_JSON["processed"]["type"] = "date"
		mappings_JSON["processed"]["format"] = "epoch_second"
		mappings_JSON["date"] = dict()
		mappings_JSON["date"]["type"] = "date"
		mappings_JSON["date"]["format"] = "epoch_second"

		data_ES = self.ESI.create_index( index = self.LINKS, mappings_JSON = mappings_JSON, settings_JSON = settings_JSON, print_server_response = False )

		if "status" in data_ES and data_ES['status'] == 400:
			self.P.write( "MRT_Indexer: create_links_index: ElasticSearch index '" + self.LINKS + "' already exists" )
		else:
			self.P.write( "MRT_Indexer: create_links_index: ElasticSearch index '" + self.LINKS + "' created" )

	def delete_links_index( self, print_server_response = False ):
		self.P.write_error("MRT_Indexer: delete_ES_link_index: Do you want to delete ElasticSearch index '" + self.LINKS + "'?" )
		if self.ARST.ask_are_you_sure() is False:
			return

		if self.ESI.exists_index( index = self.LINKS ) is False:
			self.P.write("MRT_Indexer: delete_ES_link_index: ElasicSearch index '" + str(self.LINKS) + "' does not exists" )
			return

		self.P.write("MRT_Indexer: delete_ES_link_index: ElasticSearch index '" + str(self.LINKS) + "' deleted" )
		return self.ESI.delete_index( index = self.LINKS, print_server_response = print_server_response ) 

	def reset_processed( self, download_path = None, RRC_number = None, RRC_range = None, time_interval = None ):
		if self.MRTD is None:
			self.write_error( "MRT_Indexer : reset_processed : MRTD is None" )
			self.write_error( "MRT_Indexer : reset_processed : cannot use function reset_processed()" )
			return

		download_paths = list()

		if download_path is not None:
			download_paths.append( download_path )
		else:
			if time_interval is None:
				self.P.write_warning( "MRT_Indexer: set_processed: time_interval is None" )
				self.P.write_warning( "MRT_Indexer: set_processed: setting time_interval = [ 0, 2147483647 ]" )
				time_interval = [ 0, 2147483647 ]

			if RRC_range is None and RRC_number is None:
				self.P.write_warning( "MRT_Indexer: set_processed: RRC_range is None and RRC_number is None" )
				self.P.write_warning( "MRT_Indexer: set_processed: setting RRC_range = [ 0, 40 ] " )
				RRC_range = [ 0, 40 ] 
			elif RRC_range is None and RRC_number is not None:
				RRC_range = [ RRC_number, RRC_number ] 

			download_paths.extend( self.MRTD.get_download_paths( RRC_range = RRC_range, time_interval = time_interval, include_processed = True, include_not_processed = False ) )

		counter = 0
		total = len(download_paths)
		self.P.write( "MRT_Indexer: reset_processed: found " + str(total) + " download_paths" )

		for download_path in download_paths:
			counter += 1
			self.P.rewrite( "\t(" + str(counter) + " of " + str(total) + ") resetting " + str(download_path) )
			self.set_not_processed( download_path = download_path )

	def index( self, RRC_range = None, RRC_number = None, time_interval = None ):
		self.setup_links_index()

		if time_interval is None:
			self.P.write_warning( "MRT_Indexer: load_MRT_link: time_interval is None" )
			self.P.write_warning( "MRT_Indexer: load_MRT_link: setting time_interval = [ 0, 2147483647 ]" )
			time_interval = [ 0, 2147483647 ]

		if RRC_range is None and RRC_number is None:
			self.P.write_warning( "MRT_Indexer: load_MRT_link: RRC_range is None and RRC_number is None" )
			self.P.write_warning( "MRT_Indexer: load_MRT_link: setting RRC_range = [ 0, 40 ] " )
			RRC_range = [ 0, 42 ] 
		elif RRC_range is None and RRC_number is not None:
			RRC_number = int(RRC_number)
			RRC_range = [ RRC_number, RRC_number ] 

		for RRC_number in range( RRC_range[0], RRC_range[1] + 1 ):
			mode = self.__get_mode( RRC_number = RRC_number )
			self.__process( time_interval = time_interval, RRC_number = RRC_number, mode = mode )
			self.flush( no_output = True )
			time.sleep(1)

	def __get_mode( self, RRC_number ):
		if RRC_number >= 0 and RRC_number <= 23:
			return "RIPE"
		else:
			return "ROUTEVIEWS"

	def __get_url( self, RRC_number ):
		RRC_number = int(RRC_number)

		if RRC_number >= 0 and RRC_number <= 23:
			return "http://data.ris.ripe.net/rrc" + str(RRC_number).zfill(2)  + "/"
		elif RRC_number == 24:
			return "http://routeviews.org/bgpdata/"
		elif RRC_number == 25:
			return "http://routeviews.org/route-views3/bgpdata/"
		elif RRC_number == 26:
			return "http://routeviews.org/route-views4/bgpdata/"
		elif RRC_number == 27:
			return "http://routeviews.org/route-views6/bgpdata/"
		elif RRC_number == 28:
			return "http://routeviews.org/route-views.eqix/bgpdata/"
		elif RRC_number == 29:
			return "http://routeviews.org/route-views.isc/bgpdata/"
		elif RRC_number == 30:
			return "http://routeviews.org/route-views.kixp/bgpdata/"
		elif RRC_number == 31:
			return "http://routeviews.org/route-views.jinx/bgpdata/"
		elif RRC_number == 32:
			return "http://routeviews.org/route-views.linx/bgpdata/"
		elif RRC_number == 33:
			return "http://routeviews.org/route-views.napafrica/bgpdata/"
		elif RRC_number == 34:
			return "http://routeviews.org/route-views.nwax/bgpdata/"
		elif RRC_number == 35:
			return "http://routeviews.org/route-views.telxatl/bgpdata/"
		elif RRC_number == 36:
			return "http://routeviews.org/route-views.wide/bgpdata/"
		elif RRC_number == 37:
			return "http://routeviews.org/route-views.sydney/bgpdata/"
		elif RRC_number == 38:
			return "http://routeviews.org/route-views.saopaulo/bgpdata/"
		elif RRC_number == 39:
			return "http://routeviews.org/route-views.sg/bgpdata/"
		elif RRC_number == 40:
			return "http://routeviews.org/route-views.perth/bgpdata/"
		elif RRC_number == 41:
			return "http://routeviews.org/route-views.sfmix/bgpdata/"
		elif RRC_number == 42:
			return "http://routeviews.org/route-views.soxrs/bgpdata/"

		self.P.write_error( "Ripe_Interface: __get_url: RRC_number " + str(RRC_number).zfill(2) + " not supported..." )
		return None

	def __process( self, time_interval = None, RRC_number = None, mode = None ):
		folder_names = list()
		file_name = "temp_file_" + self.RANDOM_STRING + ".html"
		url = self.__get_url( RRC_number = RRC_number )

		if self.FT.check_file_exists( file_name = file_name ) is True:
			os.remove( self.FT.get_file_path( file_name = file_name ) )

		wget.download(url, out=self.FT.get_base_path() + file_name, bar = None )

		file_data = open( self.FT.get_base_path() + file_name, 'r' ).read()
		urls = file_data.replace('\r', '').split('\n')

		for file in urls:
			folder_name =  self.ST.get_words_after_substring( full_text=file, sub_text_before_words = "></td><td><a href=", numberOfWords = 2 )

			if len(folder_name) < 2:
				continue

			if len(folder_name[1]) <= 1:
				continue

			if "logs" in folder_name[1]:
				continue

			if "gz" in folder_name[1]:
				continue

			if "invalid" in folder_name[1]:
				continue

			folder_name = folder_name[1].replace('/', '')
			folder_names.append( folder_name )

		counter = 0
		size = len(folder_names)
		for folder_name in folder_names:
			counter = counter + 1
			if "RIPE" in mode:
				self.__process_RIPE( url = url, folder_name = folder_name, counter = counter, size = size, time_interval = time_interval, RRC_number = RRC_number )
			elif "ROUTEVIEWS" in mode:
				self.__process_ROUTEVIEWS_1( url = url, folder_name = folder_name, counter = counter, size = size, time_interval = time_interval, RRC_number = RRC_number )

		self.P.rewrite( force_new_line = True )

	def __process_ROUTEVIEWS_1( self, url = None, folder_name = None, counter = None, size = None, time_interval = None, RRC_number = None ):
		percentage_float = float(counter) / float(size) * 100.0
		percentage_string = " (" + str(float("{0:.2f}".format(percentage_float))) + "%)"

		url = url + str(folder_name) + "/"
		self.P.rewrite( "\tMRT_Indexer: __process_ROUTEVIEWS: loading RRC" + str(RRC_number).zfill(2) + ", url = " + str(url) + str(percentage_string) + "                           " )
	 
	 	time_stamp = 0
	 	try:
			time_stamp = timegm( time.strptime( str(folder_name), "%Y.%m") )
		except( ValueError ):
			return

		if time_interval[0] - 2764800 > time_stamp:
			return
		
		if time_interval[1] + 2764800 < time_stamp:
			return

		self.__process_ROUTEVIEWS_2( url = url + "UPDATES/", RRC_number = RRC_number )
		self.__process_ROUTEVIEWS_2( url = url + "RIBS/", RRC_number = RRC_number )

	def __process_ROUTEVIEWS_2( self, url = None, RRC_number = None ):
		file_name = "temp_file_" + self.RANDOM_STRING + ".html"

		if self.FT.check_file_exists( file_name = file_name ) is True:
			os.remove( self.FT.get_file_path( file_name = file_name ) )

		wget.download(url, out=self.FT.get_base_path() + file_name, bar = None )
		file_data = open( self.FT.get_base_path() + file_name, 'r' ).read()

		urls = file_data.replace('\r', '').split('\n')
		for file in urls:
			file_name =  self.ST.get_words_after_substring( full_text=file, sub_text_before_words = "></td><td><a href=", numberOfWords = 2 )

			if len(file_name) < 2 or len(file_name[1]) <= 1:
				continue
				
			if "rib" not in file_name[1] and "updates" not in file_name[1]:
				continue

			file_name = file_name[1]

			if "updates" in file_name:
				type = self.TYPE_UPDATE
				try:
					time_stamp = timegm( time.strptime(str(file_name), "updates.%Y%m%d.%H%M.bz2") )
				except( ValueError ):
					continue
			elif "rib" in file_name:
				type = self.TYPE_RIB
				try:
					time_stamp = timegm( time.strptime(str(file_name), "rib.%Y%m%d.%H%M.bz2") )
				except( ValueError ):
					continue
			else:
				continue

			self.__add_download_path( download_path = url + str(file_name), RRC_number = RRC_number, time_stamp = time_stamp, type = type )
			
		#print file_data

	def __process_RIPE( self, url = None, folder_name = None, counter = None, size = None, time_interval = None, RRC_number = None ):
		file_name = "temp_file_" + self.RANDOM_STRING + ".html"

		percentage_float = float(counter) / float(size) * 100.0
		percentage_string = " (" + str(float("{0:.2f}".format(percentage_float))) + "%)"

		url = url + str(folder_name) + "/"
		self.P.rewrite( "\tMRT_Indexer: __process_RIPE: loading RRC" + str(RRC_number).zfill(2) + ", url = " + str(url) + str(percentage_string) + "           " )
	 
		time_stamp = timegm( time.strptime( str(folder_name), "%Y.%m") )

		if time_interval[0] - 2764800 > time_stamp:
			return
		
		if time_interval[1] + 2764800 < time_stamp:
			return

		if self.FT.check_file_exists( file_name = file_name ) is True:
			os.remove( self.FT.get_file_path( file_name = file_name ) )

		wget.download(url, out=self.FT.get_base_path() + file_name, bar = None )

		file_data = open( self.FT.get_base_path() + file_name, 'r' ).read()
		urls = file_data.replace('\r', '').split('\n')

		for file in urls:
			file_name =  self.ST.get_words_after_substring( full_text=file, sub_text_before_words = "></td><td><a href=", numberOfWords = 2 )

			if len(file_name) < 2 or len(file_name[1]) <= 1 or "rrc" in file_name[1]:
				continue

			file_name = file_name[1].replace('/', '')

			if "bad" in file_name:
				continue

			if "update" in file_name:
				time_stamp = timegm( time.strptime(str(file_name), "updates.%Y%m%d.%H%M.gz") )
				self.__add_download_path( download_path = url + str(file_name), RRC_number = RRC_number, time_stamp = time_stamp, type = self.TYPE_UPDATE )
			elif "bview" in file_name:
				time_stamp = timegm( time.strptime(str(file_name), "bview.%Y%m%d.%H%M.gz") )
				self.__add_download_path( download_path = url + str(file_name), RRC_number = RRC_number, time_stamp = time_stamp, type = self.TYPE_RIB )
			elif "view" in file_name:
				time_stamp = timegm( time.strptime(str(file_name), "view.%Y%m%d.%H%M.gz") )
				self.__add_download_path( download_path = url + str(file_name), RRC_number = RRC_number, time_stamp = time_stamp, type = self.TYPE_RIB  )

	def __add_download_path( self, download_path = None, RRC_number = None, time_stamp = None, type = None ):
		_id = hashlib.sha256( str(download_path)  ).hexdigest()	
		self.ids.append( _id )

		data_JSON = dict()
		data_JSON['index'] = dict()
		data_JSON['index']['_id'] = _id

		self.data_list.append( json.dumps(data_JSON) )

		data_JSON_2 = dict()
		data_JSON_2["link"] = download_path
		data_JSON_2['RRC_number'] = int(RRC_number)
		data_JSON_2["type"] = int(type)
		data_JSON_2["date"] = time_stamp
		data_JSON_2["processed"] = 0

		self.data_list.append( json.dumps(data_JSON_2) )

		if len(self.data_list) > 1000:
			self.flush( no_output = True )

	def set_processed( self, download_path = None, print_server_response = False ):
		data_JSON = dict()
		data_JSON['processed'] = time.time()

		_id = hashlib.sha256( str(download_path) ).hexdigest()	
		return self.ESI.update_id( index = self.LINKS, id = _id, data_JSON = data_JSON, print_server_response = print_server_response )

	def set_not_processed( self, download_path = None, print_server_response = False ):
		data_JSON = dict()
		data_JSON['processed'] = 0

		_id = hashlib.sha256( str(download_path) ).hexdigest()	
		return self.ESI.update_id( index = self.LINKS, id = _id, data_JSON = data_JSON, print_server_response = print_server_response )

	def flush( self, no_output = False ):
		if no_output is False:
			self.P.write( "MRT_Indexer: flush" )

		if len(self.ids) == 0:
			return

		final_data_list = list()

		data_ES = self.ESI.mget_ids( index = self.LINKS, ids = self.ids, filter_path = "docs.found", print_server_response = False )
		docs = data_ES['docs']

		for x in range( 0, len(docs) ):
			doc = docs[x]

			if doc['found'] is False:
				final_data_list.append( self.data_list[x*2] )
				final_data_list.append( self.data_list[(x*2)+1] )

		if len( final_data_list ) > 0:
			self.ESI.post_bulk( index = self.LINKS, data_list = final_data_list, print_server_response = False )

		self.__reset()







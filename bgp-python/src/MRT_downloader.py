import sys, os, datetime, time, urllib2, urllib, requests, json, hashlib, shutil, glob, gzip, bz2, struct, base64, wget, calendar, copy

from ES_interface import ES_Interface
from printer import Printer
from string_tool import String_Tool
from file_tool import File_Tool
from calendar import timegm
from MRT_reader import MRT_Reader
from random import randint

class MRT_Downloader():
	P = None
	ESI = None
	ST = None
	FT = None
	MRTR = None

	LINKS = None
	RANDOM_STRING = None

	def __init__( self, P = None, ESI = None, MRTR = None, LINKS = None, TYPE_UPDATE = None, TYPE_RIB = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "MRT_Downloader : __init__ : P is None" )

		self.RANDOM_STRING = "_" + str(randint(0, 1000000000))
		self.P.write( "MRT_Downloader: Loading... (RANDOM_STRING = " + self.RANDOM_STRING + ")", color = 'cyan' )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "MRT_Downloader : __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P )

		if MRTR is not None:
			self.MRTR = MRTR
		else:
			self.P.write_warning( "MRT_Downloader : __init__ : MRTR is None" )
			self.MRTR = MRT_Reader( P = self.P )
			

		if LINKS is None:
			self.P.write_warning( "MRT_Downloader: __init__: LINKS is None" )
			self.P.write_warning( "MRT_Downloader: __init__: setting LINKS = 'bgp-links'" )
			self.LINKS = "bgp-links"
		else:
			self.LINKS = LINKS

		if TYPE_UPDATE is None:
			self.P.write_warning( "MRT_Downloader: __init__: TYPE_UPDATE is None" )
			self.P.write_warning( "MRT_Downloader: __init__: setting TYPE_UPDATE = 0" )
			self.TYPE_UPDATE = 0
		else:
			self.TYPE_UPDATE = TYPE_UPDATE

		if TYPE_RIB is None:
			self.P.write_warning( "MRT_Downloader: __init__: TYPE_RIB is None" )
			self.P.write_warning( "MRT_Downloader: __init__: setting TYPE_RIB = 1" )
			self.TYPE_RIB = 1
		else:
			self.TYPE_RIB = TYPE_RIB

		self.FT = File_Tool( base_path = "tmp/", P = self.P, program_name = "MRT_Downloader" )

	def get_download_paths( self, RRC_number = None, RRC_range = None, time_interval = None, include_processed = True, include_not_processed = True, only_updates = False, only_ribs = False ):
		if time_interval is None:
			self.P.write_warning( "MRT_Downloader: get_download_paths: time_interval is None" )
			self.P.write_warning( "MRT_Downloader: get_download_paths: setting time_interval = [ 0, 2147483647 ]" )
			time_interval = [ 0, 2147483647 ]

		if RRC_range is None and RRC_number is None:
			self.P.write_warning( "MRT_Downloader: get_download_paths: RRC_range is None and RRC_number is None" )
			self.P.write_warning( "MRT_Downloader: get_download_paths: setting RRC_range = [ 0, 40 ] " )
			RRC_range = [ 0, 40 ] 
		elif RRC_range is None and RRC_number is not None:
			RRC_range = [ RRC_number, RRC_number ] 

		if include_processed is False and include_not_processed is False:
			self.P.write_warning( "MRT_Downloader: __get_download_paths: include_processed is False and include_not_processed is False" )
			self.P.write_warning( "MRT_Downloader: get_download_paths: setting include_processed = True " )
			self.P.write_warning( "MRT_Downloader: get_download_paths: setting include_not_processed = True " )

		download_paths = list()

		for RRC_number in range( int(RRC_range[0]), int(RRC_range[1]) + 1 ):
			self.P.rewrite( "MRT_Downloader: get_download_list: Searching in RRC" + str(RRC_number).zfill(2) + "..." )
			start_time = time_interval[0]
			end_time = start_time + 1209600 #seconds in two weeks

			if end_time > time_interval[1]:
				end_time = time_interval[1]

				temp_time_interval = [ start_time, end_time ]

				time_left = time_interval[1] - end_time
				self.P.rewrite( "MRT_Downloader: get_download_list: Searching in RRC" + str(RRC_number).zfill(2) + "... (time left = " + str(time_left) + ")                  " )
				download_paths.extend( self.__get_download_paths( RRC_number = RRC_number, time_interval = temp_time_interval, include_processed = include_processed, include_not_processed = include_not_processed, only_updates = only_updates, only_ribs = only_ribs ) )
			else:
				while end_time <= time_interval[1]:
					if end_time > time_interval[1]:
						end_time = time_interval[1]

					temp_time_interval = [ start_time, end_time ]

					time_left = time_interval[1] - end_time
					self.P.rewrite( "MRT_Downloader: get_download_list: Searching in RRC" + str(RRC_number).zfill(2) + "... (time left = " + str(time_left) + ")                  " )
					download_paths.extend( self.__get_download_paths( RRC_number = RRC_number, time_interval = temp_time_interval, include_processed = include_processed, include_not_processed = include_not_processed, only_updates = only_updates, only_ribs = only_ribs ) )

					start_time = start_time + 1209600 #seconds in two weeks
					end_time = end_time + 1209600 #seconds in two weeks

		return download_paths

	def __get_download_paths( self, RRC_number = None, time_interval = None, include_processed = True, include_not_processed = True, only_updates = False, only_ribs = False ):
		download_paths = list()

		data_JSON = dict()
		data_JSON['size'] = 8000
		data_JSON['query'] = dict()
		data_JSON['query']['bool'] = dict()
		data_JSON['query']['bool']['must'] = list()
		data_JSON['query']['bool']['must_not'] = list()

		data_JSON_2 = dict()
		data_JSON_2['range'] = dict()
		data_JSON_2['range']['date'] = dict()
		data_JSON_2['range']['date']['gte'] = time_interval[0]
		data_JSON_2['range']['date']['lte'] = time_interval[1]

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_2 = dict()
		data_JSON_2['match'] = dict()
		data_JSON_2['match']['RRC_number'] = int(RRC_number)

		data_JSON['query']['bool']['must'].append( data_JSON_2 )

		data_JSON_3 = dict()
		data_JSON_3['match'] = dict()
		data_JSON_3['match']['processed'] = 0

		if include_processed is True and include_not_processed is False:
			data_JSON['query']['bool']['must_not'].append( data_JSON_3 )
		elif include_processed is False and include_not_processed is True:
			data_JSON['query']['bool']['must'].append( data_JSON_3 )

		filter_path = "hits.total,hits.hits._source.link"

		data_ES = self.ESI.search( index = self.LINKS, data_JSON = data_JSON, filter_path = filter_path, print_server_response = False )

		if "hits" in data_ES:
			data_ES = data_ES["hits"]

		total = data_ES['total']

		if "hits" in data_ES:
			_sources = data_ES["hits"]
		else:
			_sources = list()

		length = len(_sources)

		if length != total:
			self.P.write_error( "MRT_Downloader: __get_download_paths : length != total" )

		for item in _sources:
			if "_source" in item:
				_source = item['_source']

				if "link" in _source:
					download_paths.append( _source['link'] )

		if only_updates is False and only_ribs is False:
			return download_paths
		elif only_updates is True and only_ribs is False:
			final_download_paths = list()

			for download_path in download_paths:
				if "update" in download_path:
					final_download_paths.append(download_path)

			return final_download_paths
		elif only_ribs is True and only_updates is False:
			final_download_paths = list()

			for download_path in download_paths:
				if "rib" in download_path:
					final_download_paths.append(download_path)

				if "view" in download_path:
					if "route-view" not in download_path and "routeview" not in download_path:
						final_download_paths.append(download_path)

			return list(set(final_download_paths))
		elif only_ribs is True and only_updates is True:
			self.P.write_error( "MRT_Downloader: __get_download_paths: only_ribs is True and only_updates is True" )
			return list()

	def download_MRT_records( self, download_path = None, RRC_number = None ):
		if download_path is None:
			self.P.write( "Ripe_Interface: download_MRT_records: download_path is None" )
			return None

		if ".gz" in download_path:
			return self.__get_MRT_records_from_gz_file( download_path = download_path )
		if ".bz2" in download_path:
			return self.__get_MRT_records_from_bz2_file( download_path = download_path )
		else:
			self.P.write_error( "MRT_Downloader: download_MRT_records: '.gz' not in download_path and '.bz2' not in download_path" )
			return

	def __wget( self, download_path = None, file_name = None, RRC_number = None ):
		downloaded = False
		mode = "down"

		while downloaded is False:
			if RRC_number is not None:
				self.update_stats( RRC_number = RRC_number, mode = mode )

			try:
				self.P.rewrite( "                                                                                         " )
				wget.download( download_path, out=self.FT.get_base_path() + file_name )
				if RRC_number is not None:
					self.update_stats( RRC_number = RRC_number, mode = mode )
				downloaded = True
			except (IOError):
				self.P.rewrite( "MRT_Downloader: __wget : retry..." )
				mode = "IO err"

	def __get_MRT_records_from_gz_file( self, download_path = None ):
		if download_path is None:
			self.P.write_error( "MRT_Downloader: get_MRT_records_from_gz_file: download_path is None" )
			self.quit()

		#Remove Old Temp Files
		if self.FT.check_file_exists( file_name = "temp_file" + self.RANDOM_STRING + ".gz" ) is True:
			os.remove( self.FT.get_file_path( file_name = "temp_file" + self.RANDOM_STRING + ".gz" ) )

		self.P.rewrite( "Downloading " + download_path + "      ", color ='cyan' )

		self.__wget( download_path = download_path, file_name = "temp_file" + self.RANDOM_STRING + ".gz" )

		file_size = int(os.path.getsize( self.FT.get_base_path() + "temp_file" + self.RANDOM_STRING + ".gz")) / 1024
		self.P.rewrite( "Opening " + download_path + " (size=" + str(file_size) + "kb)      ", color ='cyan' )

		with gzip.open( self.FT.get_base_path() + "temp_file" + self.RANDOM_STRING + ".gz", 'rb') as f:
			try:
				file_content = f.read()
			except (IOError):
				self.P.write( "IOError..." )
				return None

			self.P.rewrite( "Unzipping " + download_path + " (size=" + str(file_size) + "kb)      ", color = 'cyan' )

			temp_file = open( self.FT.get_base_path() + "temp_file" + self.RANDOM_STRING + ".mrt", "w" )
			temp_file.write( file_content )
			temp_file.close()

			file_path = self.FT.get_base_path() + "temp_file" + self.RANDOM_STRING + ".mrt"
			MRT_file = open( file_path, "r" )

			self.P.rewrite( "Processing " + download_path + " (size=" + str(file_size) + "kb)      ", color = 'cyan' )
			print ""
			
			return self.MRTR.load_records( file_path = file_path )

		return None

	def __get_MRT_records_from_bz2_file( self, download_path = None ):
		if download_path is None:
			self.P.write_error( "MRT_Downloader: get_MRT_records_from_bz2_file: download_path is None" )
			return None

		file_name = "temp_file" + self.RANDOM_STRING + ".bz2"
		file_path = self.FT.get_base_path() + str(file_name)

		#Remove Old Temp Files
		if self.FT.check_file_exists( file_name = file_name ) is True:
			os.remove( self.FT.get_file_path( file_name = file_name ) )

		self.P.rewrite( "Downloading " + download_path + "      ", color ='cyan' )
		self.__wget( download_path = download_path, file_name = file_name )

		file_size = int( os.path.getsize( file_path ) ) / 1024
		self.P.rewrite( "Unzipping " + download_path + " (size=" + str(file_size) + "kb)      ", color ='cyan' )
		zip_file = bz2.BZ2File( file_path )
		file_content = zip_file.read()

		file_path = self.FT.get_base_path() + "temp_file" + self.RANDOM_STRING + ".mrt"
		temp_file = open( file_path, "w" )
		temp_file.write( file_content )
		temp_file.close()

		self.P.rewrite( "Processing " + download_path + " (size=" + str(file_size) + "kb)      ", color ='cyan' )
		print ""
		
		return self.MRTR.load_records( file_path = file_path )











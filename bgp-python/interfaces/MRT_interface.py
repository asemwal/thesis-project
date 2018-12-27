import sys, os, datetime, time, urllib2, urllib, requests, json, hashlib, shutil, glob, gzip, bz2, struct, base64, wget, calendar, copy

sys.path.append( str(os.getcwd()) + "/../src" )

from ES_interface import ES_Interface
from printer import Printer
from string_tool import String_Tool
from ask_tool import Ask_Tool
from file_tool import File_Tool
from calendar import timegm
from MRT_reader import MRT_Reader
from MRT_indexer import MRT_Indexer
from MRT_downloader import MRT_Downloader
from are_you_sure_tool import Are_You_Sure_Tool
from random import randint

class MRT_Interface():
	P = None
	FT = None
	ESI = None
	MRTI = None
	MRTD = None
	MRTR = None
	ARST = None

	LINKS = None
	TYPE_UPDATE = None
	TYPE_RIB = None

	indexing_cache = None

	def __init__( self, P = None, ESI = None  ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "MRT_Interface : __init__ : P is None" )

		self.P.write( "MRT_Interface: Loading...", color = 'cyan' )
		self.FT = File_Tool( P = self.P, base_path = "tmp/", program_name = "MRT_Interface" )
		self.ARST = Are_You_Sure_Tool( P = self.P, program_name = "MRT_Interface" )

		if ESI is not None:
			self.ESI = ESI
		else:
			self.P.write_warning( "MRT_Interface : __init__ : ESI is None" )
			self.ESI = ES_Interface( P = self.P, include_state_change = False, include_withdraw = False, include_route = False, include_stats = False, include_coverage = False )

		self.LINKS = "bgp-links"
		self.TYPE_UPDATE = 0
		self.TYPE_RIB = 1

		self.MRTR = MRT_Reader( P = self.P )
		self.MRTD = MRT_Downloader( P = self.P, ESI = self.ESI, MRTR = self.MRTR, LINKS = self.LINKS, TYPE_UPDATE = self.TYPE_UPDATE, TYPE_RIB = self.TYPE_RIB )
		self.MRTI = MRT_Indexer( P = self.P, ESI = self.ESI, MRTD = self.MRTD, LINKS = self.LINKS, TYPE_UPDATE = self.TYPE_UPDATE, TYPE_RIB = self.TYPE_RIB )

		self.indexing_cache = dict()

	#GETTERS
	def get_MRT_Indexer( self ):
		return self.MRTI

	def get_MRT_Downloader( self ):
		return self.MRTD

	def get_MRT_Reader( self ):
		return self.MRTR

	#MRT_READER
	def load_records( self, relative_folder_path = None, file_name = None, file_path = None ):
		return self.MRTR.load_records( relative_folder_path = relative_folder_path, file_name = file_name, file_path = file_path )

	def is_RIB_record( self, record = None ):
		return self.MRTR.is_RIB_record( record = record )

	def get_RIB_routes( self, record = None, split_prefix = True ):
		return self.MRTR.get_RIB_routes( record = record, split_prefix = split_prefix )

	def is_state_change_record( self, record = None ):
		return self.MRTR.is_state_change_record( record = record )

	def get_new_state( self, record = None ):
		return self.MRTR.get_new_state( record = record )

	def get_peer_AS( self, record = None  ):
		return self.MRTR.get_peer_AS( record = record )

	def is_update_record( self,record = None ):
		return self.MRTR.is_update_record( record = record )

	def get_update_routes( self, record = None, split_prefix = True ):
		return self.MRTR.get_update_routes( record = record, split_prefix = split_prefix )

	def print_record( self, record = None ):
		return self.MRTR.print_record( record = record )

	def get_data_JSON( self, record = None ):
		return self.MRTR.get_data_JSON( record = record )

	def get_time_stamp( self, record = None ):
		return self.MRTR.get_time_stamp( record = record )

	#MRT_INDEXER
	def setup_links_index( self ):
		self.MRTI.setup_links_index()

	def create_links_index( self ):
		self.MRTI.create_links_index()

	def delete_links_index( self ):
		self.MRTI.delete_links_index()

	def reset_processed( self, download_path = None, RRC_number = None, RRC_range = None, time_interval = None ):
		self.MRTI.reset_processed( download_path = download_path, RRC_number = RRC_number, RRC_range = RRC_range, time_interval = time_interval )

	def set_processed( self, download_path = None, print_server_response = False ):
		self.MRTI.set_processed( download_path = download_path, print_server_response = print_server_response )

	def index( self, RRC_range = None, RRC_number = None, time_interval = None ):
		self.MRTI.index( RRC_range = RRC_range, RRC_number = RRC_number, time_interval = time_interval )

	#MRT_DOWNLOADER
	def get_download_paths( self, RRC_number = None, RRC_range = None, time_interval = None, include_processed = True, include_not_processed = True, only_updates = False, only_ribs = False ):
		data_str = str(RRC_number) + "_" + str(RRC_range) + "_" + str(time_interval)
		if data_str not in self.indexing_cache:
			self.indexing_cache[ data_str ] = None
			self.MRTI.index( RRC_range = RRC_range, RRC_number = RRC_number, time_interval = time_interval )

		return self.MRTD.get_download_paths( RRC_number = RRC_number, RRC_range = RRC_range, time_interval = time_interval, include_processed = include_processed, include_not_processed = include_not_processed, only_updates = only_updates, only_ribs = only_ribs )

	def download_MRT_records( self, download_path = None, RRC_number = None ):
		return self.MRTD.download_MRT_records( download_path = download_path, RRC_number = RRC_number )



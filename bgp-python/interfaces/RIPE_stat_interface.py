import json, requests, os, sys, netaddr
from netaddr import *
from time import sleep

sys.path.append( str(os.getcwd()) + "/../src" )

from printer import Printer
from file_tool import File_Tool
from time_tool import Time_Tool
from ask_tool import Ask_Tool

class RIPE_Stat_Interface():
	prefix_to_AS_dict = None				# Prefix as input
	AS_to_IP4_prefixes_dict = None 			# AS as input
	AS_to_IP4_24_prefixes_dict = None 		# AS as input
	AS_to_IP6_prefixes_dict = None			# AS as input

	number_of_IP4_addresses_dict = None

	base_url = None
	P = None
	FT = None
	TT = None
	AT = None
	save_counter = None
	save_data_bool = None

	def __init__( self, P = None, save_data = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "RIPE_Stat_Interface: __init__ : P is None" )

		self.P.write( "RIPE_Stat_Interface: Loading...", color = 'cyan' )

		if save_data is not None:
			self.save_data_bool = save_data
		else:
			self.P.write_warning( "RIPE_Stat_Interface: __init__ : save_data is None" )
			self.save_data_bool = False

		self.P.write( "RIPE_Stat_Interface: __init__ : save_data = " + str(self.save_data_bool) )
		self.TT = Time_Tool( P = self.P )

		self.FT = File_Tool( P = self.P, base_path = "/data/RIPE_Stat", program_name = "RIPE_Stat_Interface" )
		self.AT = Ask_Tool( P = self.P )

		self.prefix_to_AS_dict = dict()
		self.AS_to_IP4_prefixes_dict = dict()
		self.AS_to_IP4_24_prefixes_dict = dict()
		self.AS_to_IP6_prefixes_dict = dict()

		self.number_of_IP4_addresses_dict = dict()

		self.base_url = "https://stat.ripe.net/data/ris-prefixes/data.json?resource="
		self.save_counter = 0
		self.__load_data()

	def __load_data( self ):
		if self.FT.check_checksum( file_name = "RIPE_Stat_Interface_prefix_to_AS.json" ):
			self.prefix_to_AS_dict = self.FT.load_JSON_file( file_name = "RIPE_Stat_Interface_prefix_to_AS.json", print_status = False )
			self.P.write( "\tLoaded prefix_to_AS_dict (" + str(len(self.prefix_to_AS_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded prefix_to_AS_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "RIPE_Stat_Interface_AS_to_IP4_prefixes.json" ):
			self.AS_to_IP4_prefixes_dict = self.FT.load_JSON_file( file_name = "RIPE_Stat_Interface_AS_to_IP4_prefixes.json", print_status = False )
			self.P.write( "\tLoaded AS_to_IP4_prefixes_dict (" + str(len(self.AS_to_IP4_prefixes_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_IP4_prefixes_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "RIPE_Stat_Interface_AS_to_IP4_24_prefixes.json" ):
			self.AS_to_IP4_24_prefixes_dict = self.FT.load_JSON_file( file_name = "RIPE_Stat_Interface_AS_to_IP4_24_prefixes.json", print_status = False )
			self.P.write( "\tLoaded AS_to_IP4_24_prefixes_dict (" + str(len(self.AS_to_IP4_24_prefixes_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_IP4_24_prefixes_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "RIPE_Stat_Interface_AS_to_IP6_prefixes.json" ):
			self.AS_to_IP6_prefixes_dict = self.FT.load_JSON_file( file_name = "RIPE_Stat_Interface_AS_to_IP6_prefixes.json", print_status = False )
			self.P.write( "\tLoaded AS_to_IP6_prefixes_dict (" + str(len(self.AS_to_IP6_prefixes_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_IP6_prefixes_dict", color = 'red' )
			
	def bulk_download( self, AS_numbers = None ):
		if AS_numbers is None:
			self.P.write_error( "RIPE_Stat_Interface : auto_download : AS_numbers is None" )
			return None

		self.P.write( "RIPE_Stat_Interface: auto_download: start", color = 'green' )

		counter = 1
		while counter != 0:
			counter = self.__bulk_download( AS_numbers = AS_numbers )

			if counter > 0:
				self.P.write( "RIPE_Stat_Interface: auto_download: found " + str(counter) + " new items, searching again...", color = 'cyan' )
			else:
				self.P.write( "RIPE_Stat_Interface: auto_download: done!", color = 'green' )

		self.save_data()

	def __bulk_download( self, AS_numbers = None ):
		AS_numbers = list(sorted(set(AS_numbers)))

		self.P.write( "RIPE_Stat_Interface: bulk_download: searching...")
		
		length = len(self.AS_to_IP4_prefixes_dict) + len(self.AS_to_IP4_24_prefixes_dict) + len(self.AS_to_IP6_prefixes_dict)

		counter = 0
		for AS_number in AS_numbers:
			counter += 1
			percentage = int( float(counter) / float(len(AS_numbers)) * 100 )
			percentage_str = "(" + str(percentage) + "%)"

			self.P.rewrite( "\tAS" + str(AS_number) + " - " + str(counter) + " of " + str(len(AS_numbers)) + " " + percentage_str + "           " )
			
			self.get_IP4_prefixes( AS_number = str(AS_number), split_in_24 = True )
			self.get_IP6_prefixes( AS_number = str(AS_number) )

		return len(self.AS_to_IP4_prefixes_dict) + len(self.AS_to_IP4_24_prefixes_dict) + len(self.AS_to_IP6_prefixes_dict) - length

	def save_data( self ):
		self.save_counter = 999999
		self.__save_data()

	def __save_data( self ):
		if self.save_data_bool is False:
			return

		self.save_counter += 1

		if self.save_counter > 100:
			self.P.rewrite( "\tRIPE_Stat_Interface: __save_data: start... -*-*-*- DO NOT TERMINATE PROGRAM -*-*-*-         ", color = 'yellow', force_new_line = True )

			self.FT.save_JSON_file( file_name = "RIPE_Stat_Interface_prefix_to_AS.json", data_JSON = self.prefix_to_AS_dict )
			self.FT.create_checksum( file_name = "RIPE_Stat_Interface_prefix_to_AS.json" )
			self.FT.save_JSON_file( file_name = "RIPE_Stat_Interface_AS_to_IP4_prefixes.json", data_JSON = self.AS_to_IP4_prefixes_dict )
			self.FT.create_checksum( file_name = "RIPE_Stat_Interface_AS_to_IP4_prefixes.json" )
			self.FT.save_JSON_file( file_name = "RIPE_Stat_Interface_AS_to_IP4_24_prefixes.json", data_JSON = self.AS_to_IP4_24_prefixes_dict )
			self.FT.create_checksum( file_name = "RIPE_Stat_Interface_AS_to_IP4_24_prefixes.json" )
			self.FT.save_JSON_file( file_name = "RIPE_Stat_Interface_AS_to_IP6_prefixes.json", data_JSON = self.AS_to_IP6_prefixes_dict )
			self.FT.create_checksum( file_name = "RIPE_Stat_Interface_AS_to_IP6_prefixes.json" )
			self.save_counter = 0

			self.P.rewrite( "\tRIPE_Stat_Interface: __save_data: done!                                                   ", color = 'green', keep_this_line = True )

	def __get_data_JSON( self, url ):
		try:
			text = requests.get( url=url ).text
			return json.loads(text)
		except( requests.exceptions.ConnectionError, ValueError ):
			self.P.rewrite_error( "RIPE_Stat_Interface: get_index: cannot connect to " + str(url) )
			sleep(1)
			return None

	def __format_prefixes( self, prefixes = None ):
		formatted_prefexis = list()

		for prefix in prefixes:
			try:
				formatted_prefexis.append( str( IPNetwork( prefix ) ) )
			except( netaddr.core.AddrFormatError ):
				continue

		return formatted_prefexis

	def get_all_saved_IP4_prefixes( self ):
		data_list = list()
		for prefix in self.prefix_to_AS_dict.keys():
			if "." in prefix:
				data_list.append( str(prefix) )

		return data_list

	def get_all_saved_IP6_prefixes( self ):
		data_list = list()
		for prefix in self.prefix_to_AS_dict.keys():
			if ":" in prefix:
				data_list.append( str(prefix) )

		return data_list

	def get_all_saved_prefixes( self ):
		data_list = list()
		for prefix in self.prefix_to_AS_dict.keys():
			data_list.append( str(prefix) )

		return data_list

	def get_all_saved_ASes( self ):
		data_list = list()

		for AS_number in self.AS_to_IP4_prefixes_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_IP6_prefixes_dict.keys():
			data_list.append( int(AS_number) )

		return list(sorted(set(data_list)))

	def get_number_of_IP4_addresses( self, AS_number = None, split_in_24 = False, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "RIPE_Stat_Interface: get_number_of_IP4_addresses: AS_number = None" )
			return list()

		if str(AS_number) in self.number_of_IP4_addresses_dict:
			return int( self.number_of_IP4_addresses_dict[ str(AS_number)] )

		IP4_prefixes = self.get_IP4_prefixes( AS_number = AS_number, split_in_24 = True )
		self.number_of_IP4_addresses_dict[ str(AS_number) ] = len( IP4_prefixes ) * 256

		return int( self.number_of_IP4_addresses_dict[ str(AS_number) ] )

	def get_prefixes( self, AS_number = None, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "RIPE_Stat_Interface: get_prefixes: AS_number = None" )
			return list()

		prefixes = list()

		prefixes.extend( self.get_IP4_prefixes( AS_number = AS_number, print_server_response = print_server_response ) )
		prefixes.extend( self.get_IP6_prefixes( AS_number = AS_number, print_server_response = print_server_response ) )

		return prefixes

	def get_IP4_prefixes( self, AS_number = None, split_in_24 = False, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "RIPE_Stat_Interface: get_IP4_prefixes: AS_number = None" )
			return list()

		if split_in_24 is True and str(AS_number) in self.AS_to_IP4_24_prefixes_dict:
			return self.AS_to_IP4_24_prefixes_dict[str(AS_number)]
		elif split_in_24 is False and str(AS_number) in self.AS_to_IP4_prefixes_dict:
			return self.AS_to_IP4_prefixes_dict[str(AS_number)]

		if str(AS_number) not in self.AS_to_IP4_prefixes_dict:
			url = "https://stat.ripe.net/data/ris-prefixes/data.json?resource=" + str(AS_number) + "&list_prefixes=true"

			data_JSON = None
			while data_JSON is None:
				data_JSON = self.__get_data_JSON( url = url )

			if print_server_response is True:
				self.P.write( "RIPE_Stat_Interface: get_IP4_prefixes: server response: ", color = 'cyan' )
				self.P.write_JSON( data_JSON = data_JSON ) 

			IP4_prefixes = data_JSON['data']['prefixes']['v4']['originating']
			IP4_prefixes = self.__format_prefixes( prefixes = IP4_prefixes )

			self.AS_to_IP4_prefixes_dict[str(AS_number)] = IP4_prefixes

			for IP4_prefix in IP4_prefixes:
				if str(IP4_prefix) not in self.prefix_to_AS_dict:
					self.prefix_to_AS_dict[str(IP4_prefix)] = list()

				if int(AS_number) not in self.prefix_to_AS_dict[str(IP4_prefix)]:
					self.prefix_to_AS_dict[str(IP4_prefix)].append( int(AS_number) )

			self.__save_data()

		if split_in_24 is True and str(AS_number) not in self.AS_to_IP4_24_prefixes_dict:	
			IP4_24_prefixes = list()
			for IP4_prefix in self.AS_to_IP4_prefixes_dict[str(AS_number)]:
				if "/0" in IP4_prefix:
					continue

				parent = IPNetwork( IP4_prefix )
				for item in list(parent.subnet(24)) :
					IP4_24_prefixes.append( str(item) )

			self.AS_to_IP4_24_prefixes_dict[str(AS_number)] = IP4_24_prefixes

		if split_in_24 is True:
			return self.AS_to_IP4_24_prefixes_dict[str(AS_number)]
		else:
			return self.AS_to_IP4_prefixes_dict[str(AS_number)]

	def get_IP6_prefixes( self, AS_number = None, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "RIPE_Stat_Interface: get_IP6_prefixes: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_IP6_prefixes_dict:
			return self.AS_to_IP6_prefixes_dict[str(AS_number)]

		url = self.base_url + str(AS_number) + "&list_prefixes=true"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if print_server_response is True:
			self.P.write( "RIPE_Stat_Interface: get_IP6_prefixes: server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_JSON ) 

		IP6_prefixes = data_JSON['data']['prefixes']['v6']['originating']
		IP6_prefixes = self.__format_prefixes( prefixes = IP6_prefixes )

		self.AS_to_IP6_prefixes_dict[str(AS_number)] = IP6_prefixes

		for IP6_prefix in IP6_prefixes:
			if str(IP6_prefix) not in self.prefix_to_AS_dict:
				self.prefix_to_AS_dict[str(IP6_prefix)] = list()

			if int(AS_number) not in self.prefix_to_AS_dict[str(IP6_prefix)]:
				self.prefix_to_AS_dict[str(IP6_prefix)].append( int(AS_number) )

		self.__save_data()
		return self.AS_to_IP6_prefixes_dict[str(AS_number)]

	def get_AS_numbers( self, IP4_address = None, IP6_address = None, prefix = None, print_server_response = False ):
		if IP4_address is None and IP6_address is None and prefix is None:
			self.P.write_error( "RIPE_Stat_Interface: get_AS_numbers: IP4_address is None and IP6_address is None and prefix is None" )
			return list()

		if prefix is not None:
			if str(prefix) in self.prefix_to_AS_dict:
				return self.prefix_to_AS_dict[str(prefix)]
			else:
				IP_address = prefix.split("/")[0]

		if IP4_address is not None:
			IP_address = IP4_address
		elif IP6_address is not None:
			IP_address = IP6_address
		
		url = "https://stat.ripe.net/data/network-info/data.json?resource=" + str(IP_address)

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if print_server_response is True:
			self.P.write( "RIPE_Stat_Interface: get_AS_numbers: server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_JSON ) 

		prefix = data_JSON['data']['prefix']
		AS_numbers = data_JSON['data']['asns']

		if str(prefix) in self.prefix_to_AS_dict:
			return self.prefix_to_AS_dict[str(prefix)]

		for AS_number in AS_numbers:
			self.get_IP4_prefixes( AS_number = AS_number, print_server_response = print_server_response )
			self.get_IP6_prefixes( AS_number = AS_number, print_server_response = print_server_response )

		if str(prefix) in self.prefix_to_AS_dict:
			return self.prefix_to_AS_dict[str(prefix)]
		else:
			self.P.write_warning( "RIPE_Stat_Interface: get_AS_numbers: prefix " + str(prefix) + " not found" )
			return list()
		





		








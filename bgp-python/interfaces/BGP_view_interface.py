import json, requests, os, sys, netaddr
from netaddr import *
from time import sleep

sys.path.append( str(os.getcwd()) + "/../src" )

from printer import Printer
from file_tool import File_Tool
from time_tool import Time_Tool
from ask_tool import Ask_Tool

class BGP_View_Interface():
	AS_to_peers_dict = None					# AS as input
	AS_to_customers_dict = None				# AS as input
	AS_to_providers_dict = None				# AS as input
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
			self.P.write_warning( "BGP_View_Interface: __init__ : P is None" )

		self.P.write( "BGP_View_Interface: Loading...", color = 'cyan' )

		if save_data is not None:
			self.save_data_bool = save_data
		else:
			self.P.write_warning( "BGP_View_Interface: __init__ : save_data is None" )
			self.save_data_bool = False

		self.P.write( "BGP_View_Interface: __init__ : save_data = " + str(self.save_data_bool) )
		self.TT = Time_Tool( P = self.P )

		self.FT = File_Tool( P = self.P, base_path = "/data/", program_name = "BGP_View_Interface" )
		self.AT = Ask_Tool( P = self.P )

		self.AS_to_peers_dict = dict()
		self.AS_to_customers_dict = dict()
		self.AS_to_providers_dict = dict()
		self.prefix_to_AS_dict = dict()
		self.AS_to_IP4_prefixes_dict = dict()
		self.AS_to_IP4_24_prefixes_dict = dict()
		self.AS_to_IP6_prefixes_dict = dict()

		self.number_of_IP4_addresses_dict = dict()

		self.base_url = "https://api.bgpview.io/asn/"
		self.save_counter = 0
		self.__load_data()

	def __load_data( self ):
		if self.FT.check_checksum( file_name = "BGP_View_Interface_AS_to_peers.json" ):
			self.AS_to_peers_dict = self.FT.load_JSON_file( file_name = "BGP_View_Interface_AS_to_peers.json", print_status = False  )
			self.P.write( "\tLoaded AS_to_peers_dict (" + str(len(self.AS_to_peers_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_peers_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "BGP_View_Interface_AS_to_customers.json" ):
			self.AS_to_customers_dict = self.FT.load_JSON_file( file_name = "BGP_View_Interface_AS_to_customers.json", print_status = False  )
			self.P.write( "\tLoaded AS_to_customers_dict (" + str(len(self.AS_to_customers_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_customers_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "BGP_View_Interface_AS_to_providers.json" ):
			self.AS_to_providers_dict = self.FT.load_JSON_file( file_name = "BGP_View_Interface_AS_to_providers.json", print_status = False )
			self.P.write( "\tLoaded AS_to_providers_dict (" + str(len(self.AS_to_providers_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_providers_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "BGP_View_Interface_prefix_to_AS.json" ):
			self.prefix_to_AS_dict = self.FT.load_JSON_file( file_name = "BGP_View_Interface_prefix_to_AS.json", print_status = False )
			self.P.write( "\tLoaded prefix_to_AS_dict (" + str(len(self.prefix_to_AS_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded prefix_to_AS_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "BGP_View_Interface_AS_to_IP4_prefixes.json" ):
			self.AS_to_IP4_prefixes_dict = self.FT.load_JSON_file( file_name = "BGP_View_Interface_AS_to_IP4_prefixes.json", print_status = False )
			self.P.write( "\tLoaded AS_to_IP4_prefixes_dict (" + str(len(self.AS_to_IP4_prefixes_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_IP4_prefixes_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "BGP_View_Interface_AS_to_IP6_prefixes.json" ):
			self.AS_to_IP6_prefixes_dict = self.FT.load_JSON_file( file_name = "BGP_View_Interface_AS_to_IP6_prefixes.json", print_status = False )
			self.P.write( "\tLoaded AS_to_IP6_prefixes_dict (" + str(len(self.AS_to_IP6_prefixes_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_IP6_prefixes_dict", color = 'red' )
			
	def save_data( self ):
		self.save_counter = 1001
		self.__save_data()

	def __save_data( self ):
		if self.save_data_bool is False:
			return

		self.save_counter += 1

		if self.save_counter > 1000:
			self.P.rewrite( "\tBGP_View_Interface: __save_data: start... -*-*-*- DO NOT TERMINATE PROGRAM -*-*-*-         ", color = 'yellow', force_new_line = True )

			self.FT.save_JSON_file( file_name = "BGP_View_Interface_AS_to_peers.json", data_JSON = self.AS_to_peers_dict )
			self.FT.create_checksum( file_name = "BGP_View_Interface_AS_to_peers.json" )
			self.FT.save_JSON_file( file_name = "BGP_View_Interface_AS_to_customers.json", data_JSON = self.AS_to_customers_dict )
			self.FT.create_checksum( file_name = "BGP_View_Interface_AS_to_customers.json" )
			self.FT.save_JSON_file( file_name = "BGP_View_Interface_AS_to_providers.json", data_JSON = self.AS_to_providers_dict )
			self.FT.create_checksum( file_name = "BGP_View_Interface_AS_to_providers.json" )
			self.FT.save_JSON_file( file_name = "BGP_View_Interface_prefix_to_AS.json", data_JSON = self.prefix_to_AS_dict )
			self.FT.create_checksum( file_name = "BGP_View_Interface_prefix_to_AS.json" )
			self.FT.save_JSON_file( file_name = "BGP_View_Interface_AS_to_IP4_prefixes.json", data_JSON = self.AS_to_IP4_prefixes_dict )
			self.FT.create_checksum( file_name = "BGP_View_Interface_AS_to_IP4_prefixes.json" )
			self.FT.save_JSON_file( file_name = "BGP_View_Interface_AS_to_IP6_prefixes.json", data_JSON = self.AS_to_IP6_prefixes_dict )
			self.FT.create_checksum( file_name = "BGP_View_Interface_AS_to_IP6_prefixes.json" )
			self.save_counter = 0

			self.P.rewrite( "\tBGP_View_Interface: __save_data: done!                                                   ", color = 'green', keep_this_line = True )

	def __get_data_JSON( self, url ):
		try:
			text = requests.get( url=url ).text
			return json.loads(text)
		except( requests.exceptions.ConnectionError, ValueError ):
			self.P.rewrite_error( "BGP_View_Interface: get_index: cannot connect to " + str(url) )
			sleep(1)
			return None

	def get_relation( self, dest_AS, source_AS ):
		if str(dest_AS) not in self.AS_to_peers_dict:
			self.get_peers( AS_number = dest_AS )

		if str(dest_AS) not in self.AS_to_customers_dict:
			self.get_customers( AS_number = dest_AS )

		if str(dest_AS) not in self.AS_to_providers_dict:
			self.get_providers( AS_number = dest_AS )

		if str(source_AS) not in self.AS_to_peers_dict:
			self.get_peers( AS_number = source_AS )

		if str(source_AS) not in self.AS_to_customers_dict:
			self.get_customers( AS_number = source_AS )

		if str(source_AS) not in self.AS_to_providers_dict:
			self.get_providers( AS_number = source_AS )

		if int(source_AS) in self.AS_to_peers_dict[ str(dest_AS) ]:
			return "p2p"

		if int(source_AS) in self.AS_to_customers_dict[ str(dest_AS) ]:
			return "c2p"

		if int(source_AS) in self.AS_to_providers_dict[ str(dest_AS) ]:
			return "p2c"

		if int(dest_AS) in self.AS_to_peers_dict[ str(source_AS) ]:
			return "p2p"

		if int(dest_AS) in self.AS_to_customers_dict[ str(source_AS) ]:
			return "p2c"

		if int(dest_AS) in self.AS_to_providers_dict[ str(source_AS) ]:
			return "c2p"

		return None

	def auto_download( self, AS_numbers = None ):
		self.P.write( "BGP_View_Interface: auto_download: start", color = 'green' )

		if AS_numbers is None:
			AS_numbers = [ 286 ]

		counter = 1
		while counter != 0:
			counter = self.__auto_download( AS_numbers = AS_numbers )

			if counter > 0:
				self.P.write( "BGP_View_Interface: auto_download: found " + str(counter) + " new items, searching again...", color = 'cyan' )
			else:
				self.P.write( "BGP_View_Interface: auto_download: done!", color = 'green' )

		self.save_data()
		self.__compute_inverse()

	def __auto_download( self, AS_numbers = None ):
		counter = 0
		cache_dict = dict()

		if AS_numbers is not None:
			AS_numbers.extend( self.get_all_saved_ASes() )
		else:
			AS_numbers = self.get_all_saved_ASes()

		AS_numbers = list(sorted(set(AS_numbers)))

		self.P.write( "BGP_View_Interface: auto_download: searching...")
		
		length = len(self.AS_to_peers_dict) + len(self.AS_to_customers_dict) + len(self.AS_to_providers_dict) + len(self.AS_to_IP4_prefixes_dict) + len(self.AS_to_IP6_prefixes_dict)

		counter = 0
		for AS_number in AS_numbers:
			counter += 1
			percentage = int( float(counter) / float(len(AS_numbers)) * 100 )
			percentage_str = "(" + str(percentage) + "%)"

			self.P.rewrite( "\tAS" + str(AS_number) + " - " + str(counter) + " of " + str(len(AS_numbers)) + " " + percentage_str + "           " )

			self.get_peers( AS_number = AS_number )
			self.get_customers( AS_number = AS_number )
			self.get_providers( AS_number = AS_number )
			self.get_IP4_prefixes( AS_number = AS_number )
			self.get_IP6_prefixes( AS_number = AS_number )

		return len(self.AS_to_peers_dict) + len(self.AS_to_customers_dict) + len(self.AS_to_providers_dict) + len(self.AS_to_IP4_prefixes_dict) + len(self.AS_to_IP6_prefixes_dict) - length

	def __compute_inverse( self ):
		self.P.write( "BGP_View_Interface: __compute_inverse: searching...")

		counter = 0
		for AS_number in self.AS_to_IP4_prefixes_dict:
			counter += 1
			percentage = int( float(counter) / float(len(self.AS_to_IP4_prefixes_dict)) * 100 )
			percentage_str = "(" + str(percentage) + "%)"

			self.P.rewrite( "\tAS" + str(AS_number) + " - " + str(counter) + " of " + str(len(self.AS_to_IP4_prefixes_dict)) + " " + percentage_str + "           " )

			IP4_prefixes = self.AS_to_IP4_prefixes_dict[ str(AS_number) ]
			for IP4_prefix in IP4_prefixes:
				if str(IP4_prefix) not in self.prefix_to_AS_dict:
					self.prefix_to_AS_dict[str(IP4_prefix)] = list()

				if int(AS_number) not in self.prefix_to_AS_dict[str(IP4_prefix)]:
					self.prefix_to_AS_dict[str(IP4_prefix)].append( int(AS_number) )

		counter = 0
		for AS_number in self.AS_to_IP6_prefixes_dict:
			counter += 1
			percentage = int( float(counter) / float(len(self.AS_to_IP6_prefixes_dict)) * 100 )
			percentage_str = "(" + str(percentage) + "%)"

			self.P.rewrite( "\tAS" + str(AS_number) + " - " + str(counter) + " of " + str(len(self.AS_to_IP6_prefixes_dict)) + " " + percentage_str + "           " )

			IP6_prefixes = self.AS_to_IP6_prefixes_dict[ str(AS_number) ]

			for IP6_prefix in IP6_prefixes:
				if str(IP6_prefix) not in self.prefix_to_AS_dict:
					self.prefix_to_AS_dict[str(IP6_prefix)] = list()

				if int(AS_number) not in self.prefix_to_AS_dict[str(IP6_prefix)]:
					self.prefix_to_AS_dict[str(IP6_prefix)].append( int(AS_number) )

		self.save_data()

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
		for AS_number in self.AS_to_peers_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_providers_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_customers_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_IP4_prefixes_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_IP6_prefixes_dict.keys():
			data_list.append( int(AS_number) )

		return list(sorted(set(data_list)))

	def get_peers( self, AS_number = None, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "BGP_View_Interface: get_peers: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_peers_dict:
			return self.AS_to_peers_dict[str(AS_number)]

		url = self.base_url + str(AS_number) + "/peers"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if print_server_response is True:
			self.P.write( "BGP View server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		if "data" not in data_JSON:
			self.P.write_error( "BGP_View_Interface: get_index: 'data' not in data_JSON: url = " + str(url) )
			return

		self.AS_to_peers_dict[str(AS_number)] = list()

		IP4_peers = data_JSON['data']['ipv4_peers']
		for IP4_peer in IP4_peers:
			self.AS_to_peers_dict[str(AS_number)].append( int(IP4_peer['asn']) )

		IP6_peers = data_JSON['data']['ipv6_peers']
		for IP6_peer in IP6_peers:
			self.AS_to_peers_dict[str(AS_number)].append( int(IP6_peer['asn']) )
				
		self.AS_to_peers_dict[str(AS_number)] = list( sorted(self.AS_to_peers_dict[str(AS_number)]) )

		self.__save_data()
		return self.AS_to_peers_dict[str(AS_number)]

	def get_customers( self, AS_number = None, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "BGP_View_Interface: get_customers: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_customers_dict:
			return self.AS_to_customers_dict[str(AS_number)]

		url = self.base_url + str(AS_number) + "/downstreams"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if print_server_response is True:
			self.P.write( "BGP View server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		if "data" not in data_JSON:
			self.P.write_error( "BGP_View_Interface: get_index: 'data' not in data_JSON: url = " + str(url) )
			return

		self.AS_to_customers_dict[str(AS_number)] = list()

		IP4_customers = data_JSON['data']['ipv4_downstreams']
		for IP4_customer in IP4_customers:
			self.AS_to_customers_dict[str(AS_number)].append( int(IP4_customer['asn']) )

		IP6_customers = data_JSON['data']['ipv6_downstreams']
		for IP6_customer in IP6_customers:
			self.AS_to_customers_dict[str(AS_number)].append( int(IP6_customer['asn']) )

		self.AS_to_customers_dict[str(AS_number)] = list( sorted(self.AS_to_customers_dict[str(AS_number)]) )

		self.__save_data()
		return self.AS_to_customers_dict[str(AS_number)]

	def get_providers( self, AS_number = None, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "BGP_View_Interface: get_providers: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_providers_dict:
			return self.AS_to_providers_dict[str(AS_number)]

		url = self.base_url + str(AS_number) + "/upstreams"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if print_server_response is True:
			self.P.write( "BGP View server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		if "data" not in data_JSON:
			self.P.write_error( "BGP_View_Interface: get_index: 'data' not in data_JSON: url = " + str(url) )
			return

		self.AS_to_providers_dict[str(AS_number)] = list()

		IP4_providers = data_JSON['data']['ipv4_upstreams']
		for IP4_provider in IP4_providers:
			self.AS_to_providers_dict[str(AS_number)].append( int(IP4_provider['asn']) )

		IP6_providers = data_JSON['data']['ipv6_upstreams']
		for IP6_provider in IP6_providers:
			self.AS_to_providers_dict[str(AS_number)].append( int(IP6_provider['asn']) )

		self.AS_to_providers_dict[str(AS_number)] = list( sorted(self.AS_to_providers_dict[str(AS_number)]) )

		self.__save_data()
		return self.AS_to_providers_dict[str(AS_number)]

	def get_AS_numbers( self, prefix = None, IP4_prefix = None, IP6_prefix = None, print_server_response = False ):
		if prefix is not None and str(prefix) in self.prefix_to_AS_dict:
			return self.prefix_to_AS_dict[ str(prefix)] 

		if IP4_prefix is not None and str(IP4_prefix) in self.prefix_to_AS_dict:
			return self.prefix_to_AS_dict[ str(IP4_prefix)] 

		if IP6_prefix is not None and str(IP6_prefix) in self.prefix_to_AS_dict:
			return self.prefix_to_AS_dict[ str(IP6_prefix)] 

		if prefix is not None:
			self.P.write_error( "BGP_View_Interface: get_AS_number: prefix not found")

		if IP4_prefix is not None:
			self.P.write_error( "BGP_View_Interface: get_AS_number: IP4_prefix not found" )

		if IP6_prefix is not None:
			self.P.write_error( "BGP_View_Interface: get_AS_number: IP6_prefix not found" )

		if prefix is not None and IP4_prefix is not None or IP6_prefix is not None:
			if "Y" in self.AT.ask( question = "BGP_View_Interface: get_AS_number: run auto_download (Y/N)?", expect_list = [ "Y", "N" ] ):
				self.auto_download()

			return None

		self.P.write_error( "BGP_View_Interface: get_AS_number: prefix is None and IP4_prefix is None and IP4_prefix is None" )
		return None

	def get_number_of_IP4_addresses( self, AS_number = None, split_in_24 = False, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "BGP_View_Interface: get_number_of_IP4_addresses: AS_number = None" )
			return list()

		if str(AS_number) in self.number_of_IP4_addresses_dict:
			return int( self.number_of_IP4_addresses_dict[ str(AS_number)] )

		IP4_prefixes = self.get_IP4_prefixes( AS_number = AS_number, split_in_24 = True )
		self.number_of_IP4_addresses_dict[ str(AS_number) ] = len( IP4_prefixes ) * 256

		return int( self.number_of_IP4_addresses_dict[ str(AS_number) ] )

	def get_prefixes( self, AS_number = None, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "BGP_View_Interface: get_prefixes: AS_number is None" )
			return list()

		prefixes = list()

		prefixes.extend( self.get_IP4_prefixes( AS_number = AS_number, print_server_response = print_server_response ) )
		prefixes.extend( self.get_IP6_prefixes( AS_number = AS_number, print_server_response = print_server_response ) )

		return prefixes

	def get_IP4_prefixes( self, AS_number = None, split_in_24 = False, print_server_response = False ):
		if AS_number is None:
			self.P.write_error( "BGP_View_Interface: get_IP4_prefixes: AS_number is None" )
			return list()

		if split_in_24 is True and str(AS_number) in self.AS_to_IP4_24_prefixes_dict:
			return self.AS_to_IP4_24_prefixes_dict[str(AS_number)]
		elif split_in_24 is False and str(AS_number) in self.AS_to_IP4_prefixes_dict:
			return self.AS_to_IP4_prefixes_dict[str(AS_number)]

		if str(AS_number) not in self.AS_to_IP4_prefixes_dict:
			print AS_number
			return list()
			url = self.base_url + str(AS_number) + "/prefixes"

			data_JSON = None
			while data_JSON is None:
				data_JSON = self.__get_data_JSON( url = url )

			if print_server_response is True:
				self.P.write( "BGP View server response: ", color = 'cyan' )
				self.P.write_JSON( data_JSON = data_ES ) 

			data_raw = data_JSON['data']['ipv4_prefixes']

			data_list = list()
			for element in data_raw:
				data_list.append( element['prefix'] )

			self.AS_to_IP4_prefixes_dict[str(AS_number)] = dict()
			self.AS_to_IP4_prefixes_dict[str(AS_number)] = data_list

			self.__save_data()

		if split_in_24 is True and str(AS_number) not in self.AS_to_IP4_24_prefixes_dict:	
			IP4_24_prefixes = list()
			for IP4_prefix in self.AS_to_IP4_prefixes_dict[str(AS_number)]:
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
			self.P.write_error( "BGP_View_Interface: get_IP6_prefixes: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_IP6_prefixes_dict:
			return self.AS_to_IP6_prefixes_dict[str(AS_number)]

		url = self.base_url + str(AS_number) + "/prefixes"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if print_server_response is True:
			self.P.write( "BGP View server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data_ES ) 

		data_raw = data_JSON['data']['ipv6_prefixes']

		data_list = list()
		for element in data_raw:
			data_list.append( element['prefix'] )

		self.AS_to_IP6_prefixes_dict[str(AS_number)] = data_list

		self.__save_data()
		return self.AS_to_IP6_prefixes_dict[str(AS_number)]













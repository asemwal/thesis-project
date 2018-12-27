import sys, os, socket, json, netaddr
from netaddr import *
from time import sleep

sys.path.append( str(os.getcwd()) + "/../src" )

from file_tool import File_Tool
from printer import Printer

class Geo_Interface():
	P = None
	FT = None

	cache_coordinates = None 
	cache_AS_number = None
	BUFFER_SIZE = None
	socket = None

	IP4_address_to_coordinate_dict = None
	cache_AS_number = None

	save_counter = None

	def __init__( self, P = None, save_data = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Geo_Interface : __init__ : P is None" )

		self.P.write( "Geo_Interface: Loading...", color = 'cyan' )

		if save_data is not None:
			self.save_data_bool = save_data
		else:
			self.P.write_warning( "Geo_Interface: __init__ : save_data is None" )
			self.save_data_bool = False

		self.P.write( "Geo_Interface: __init__ : save_data = " + str(self.save_data_bool) )

		self.FT = File_Tool( P = self.P,  base_path = "/data/", program_name = "Geo_Interface" )

		self.IP4_address_to_coordinate_dict = dict()
		self.cache_AS_number = dict()
		self.save_counter = 0

		self.__load_data()

		connected = self.__connect()
		while connected is False:
			sleep(1)
			connected = self.__connect()

	def __connect( self ):
		try:
			self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.socket.connect(('127.0.0.1', 4000))
			self.BUFFER_SIZE = 1024
			return True
		except( socket.error ):
			self.P.rewrite_error( "Geo_Interface : __connect : cannot connect to localhost:4000..." )
			return False

	def __load_data( self ):
		if self.FT.check_checksum( file_name = "Geo_Interface_IP4_address_to_coordinate.json" ):
			self.IP4_address_to_coordinate_dict = self.FT.load_JSON_file( file_name = "Geo_Interface_IP4_address_to_coordinate.json", print_status = False )
			self.P.write( "\tLoaded Geo_Interface_IP4_address_to_coordinate (" + str(len(self.IP4_address_to_coordinate_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded Geo_Interface_IP4_address_to_coordinate", color = 'red' )
			
	def save_data( self ):
		self.save_counter = 999999
		self.__save_data()

	def __save_data( self ):
		if self.save_data_bool is False:
			return

		self.save_counter += 1

		if self.save_counter > 10000:
			self.P.rewrite( "\tGeo_Interface: __save_data: start... -*-*-*- DO NOT TERMINATE PROGRAM -*-*-*-         ", color = 'yellow', force_new_line = True )

			self.FT.save_JSON_file( file_name = "Geo_Interface_IP4_address_to_coordinate.json", data_JSON = self.IP4_address_to_coordinate_dict )
			self.FT.create_checksum( file_name = "Geo_Interface_IP4_address_to_coordinate.json" )

			self.save_counter = 0

			self.P.rewrite( "\tGeo_Interface: __save_data: done!                                                   ", color = 'green', keep_this_line = True )

	def load_coordinates_file( self, relative_folder_path = "", file_name = None, print_status = True ):
		if file_name is None:
			self.P.write_error( "Geo_Interface: save_coordinate_to_file: file_name is None" )	
			return None

		file_name = file_name.split(".")[0] + ".coordinates"
		data_text = self.FT.load_text_file( relative_folder_path = relative_folder_path, file_name = file_name, print_status = print_status )
		
		lines = data_text.split("\n")
		coordinates = list()
		for x in range( 1, len(lines) ):
			coordinate = lines[x].split(",")

			if len(coordinate) == 2:
				coordinate[0] = float(coordinate[0])
				coordinate[1] = float(coordinate[1])

				coordinates.append( coordinate )

		return coordinates

	def save_coordinates_file( self, relative_folder_path = "", file_name = None, coordinates = None, print_status = True ):
		if coordinates is None:
			self.P.write_error( "Geo_Interface: save_coordinates_file: coordinates is None" )
			return None

		if file_name is None:
			self.P.write_error( "Geo_Interface: save_coordinates_file: file_name is None" )	
			return None

		file_name = file_name.split(".")[0] + ".coordinates"

		data_text = "latitude,longitude" + "\n"
		local_counter = 0
		counter = len( coordinates )
		for coordinate in coordinates:
			counter -= 1
			local_counter += 1
			
			if coordinate is None:
				continue

			if counter % 1000 == 0:
				self.P.rewrite( "\tGeo_Interface: save_coordinates_file: " + str(counter/1000) + "k coordinates left to process          " )

			data_text = data_text + str( coordinate[0] ) + "," + str( coordinate[1] ) + "\n"

			if local_counter > 50000:
				self.FT.add_text_to_file( data_text = data_text, relative_folder_path = relative_folder_path, file_name = file_name, print_status = False )
				data_text = ""

		self.FT.add_text_to_file( data_text = data_text, relative_folder_path = relative_folder_path, file_name = file_name, print_status = False )

	def get_all_coordinates( self ):
		coordinates = list()

		parent_0 = IPNetwork( "0.0.0.0/0" )
		subnet_8_list = list(parent_0.subnet(8))

		for subnet_8 in subnet_8_list:
			parent_8 = IPNetwork( subnet_8 )
			self.P.rewrite( str(parent_8) + "                        " )

			subnet_16_list = list(parent_8.subnet(16))

			for subnet_16 in subnet_16_list:
				parent_16 = IPNetwork( subnet_16 )
				subnet_24_list = list(parent_16.subnet(24))

				for subnet_24 in subnet_24_list:
					coordinate = self.get_coordinate( IP4_prefix = subnet_24 ) 

					if coordinate is None:
						self.P.rewrite( str(subnet_24[0]) + " - NOT FOUND " )
					else:
						coordinates.append( coordinate )

			return coordinates

	def __get_data( self, IP4_address = None ):
		try:
			self.socket.send(str(IP4_address) + "\n")
			data = self.socket.recv(self.BUFFER_SIZE).replace("\n","" )
		except( socket.error ):
			data = None

		while data is None or len(data) == 0:
			self.P.rewrite_error( "Geo_Interface : __connect : cannot connect to localhost:4000..." )
			sleep(1)
			self.__connect()

			try:
				self.socket.send(str(IP4_address) + "\n")
				data = self.socket.recv(self.BUFFER_SIZE).replace("\n","" )
			except( socket.error ):
				data = None

		return data

	def get_AS_number( self, IP4_address = None, IP4_prefix = None, no_output = False, print_server_response = False ):
		if IP4_address is None and IP4_prefix is None:
			self.P.write_error( "Geo_Interface: get_AS_number: IP4_address is None and IP4_prefix is None" )
			return None

		if IP4_prefix is not None:
			if "str" in str( type(IP4_prefix) ):
				IP4_address = IP4_prefix.split("/")[0]
			elif "unicode" in str( type(IP4_prefix) ):
				IP4_address = IP4_prefix.split("/")[0]
			elif "netaddr.ip.IPNetwork" in str( type(IP4_prefix) ):
				IP4_address = IP4_prefix[0]
			else:
				self.P.write_error( "Geo_Interface: get_AS_number: type(IP4_prefix) = " + str(type(IP4_prefix)) )
				return None

		if IP4_address is None:
			self.P.write_error( "Geo_Interface : get_AS_number : IP4_address is None", color = 'red' )

		if str(IP4_address) in self.cache_AS_number:
			return self.cache_AS_number[str(IP4_address)]

		if "/" in IP4_address:
			self.P.write_warning( "Geo_Interface: get_AS_number: IP4_address contains '/': " + str(IP4_address) )
			IP4_address.split("/")[0]
			self.P.write_warning( "Geo_Interface: get_AS_number: setting IP4_address = " + str(IP4_address) )

		data = self.__get_data( IP4_address = IP4_address )

		if print_server_response is True:
			self.P.write( "localhost 4000 server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data ) 

		if "null" in data:
			if no_output is False:
				self.P.write_error( "Geo_Interface: get_AS_number: " + str(IP4_address) + " not found" )
				self.P.write( "\tdata = " + str(data) )
			return None

		data_JSON = json.loads( data )

		if "asn" not in data_JSON:
			if no_output is False:
				self.P.write_error( "Geo_Interface: get_AS_number: " + str(IP4_address) + " not found" )
				self.P.write( "\tdata = " + str(data) )
			return None

		result = data_JSON['asn']
		self.cache_AS_number[str(IP4_address)] = result

		return result

	def get_coordinate( self, IP4_address = None, IP4_prefix = None, no_output = False, print_server_response = False ):
		if IP4_address is None and IP4_prefix is None:
			self.P.write_error( "Geo_Interface: get_coordinate: IP4_address is None and IP4_prefix is None" )
			return None

		if IP4_prefix is not None:
			if "str" in str( type(IP4_prefix) ):
				IP4_address = IP4_prefix.split("/")[0]
			elif "unicode" in str( type(IP4_prefix) ):
				IP4_address = IP4_prefix.split("/")[0]
			elif "netaddr.ip.IPNetwork" in str( type(IP4_prefix) ):
				IP4_address = IP4_prefix[0]
			else:
				self.P.write_error( "Geo_Interface: get_coordinate: type(IP4_prefix) = " + str(type(IP4_prefix)) )
				return None

		if IP4_address is None:
			self.P.write_error( "Geo_Interface : get_coordinate : IP4_address is None", color = 'red' )

		if "/" in IP4_address:
			self.P.write_warning( "Geo_Interface: get_coordinate: IP4_address contains '/': " + str(IP4_address) )
			IP4_address.split("/")[0]
			self.P.write_warning( "Geo_Interface: get_coordinate: setting IP4_address = " + str(IP4_address) )

		if str(IP4_address) in self.IP4_address_to_coordinate_dict:
			return self.IP4_address_to_coordinate_dict[str(IP4_address)]

		data = self.__get_data( IP4_address = IP4_address )

		if print_server_response is True:
			self.P.write( "localhost 4000 server response: ", color = 'cyan' )
			self.P.write_JSON( data_JSON = data ) 

		if "null" in data:
			if no_output is False:
				self.P.write_error( "Geo_Interface: get_coordinate: " + str(IP4_address) + " not found" )
			return None

		data_JSON = json.loads( data )

		if "geo" not in data_JSON:
			if no_output is False:
				self.P.write_error( "Geo_Interface: get_coordinate: " + str(IP4_address) + " not found" )
			return None

		geo = data_JSON['geo'].split(",")
		result = [ float(geo[0]), float(geo[1]) ]

		self.__save_data()

		self.IP4_address_to_coordinate_dict[str(IP4_address)] = result

		return result


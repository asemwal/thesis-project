import sys, os, time, thread, numpy, operator, json, netaddr, struct

from ryu.lib import mrtlib
from printer import Printer
from file_tool import File_Tool
from netaddr import *
from time_tool import Time_Tool
from mrtparse import *
from inspect import isclass


class MRT_Reader:
	P = None
	FT = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "MRT_Reader : __init__ : P is None" )
		
		self.P.write( "MRT_Reader: Loading...", color = 'cyan' )
		self.FT = File_Tool( base_path = "tmp/", program_name = "MRT_Reader", P = self.P )

	def load_records( self, relative_folder_path = None, file_name = None, file_path = None ):
		if file_path is not None:
			return Reader( file_path )
		else:
			file_path = self.FT.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

			if self.FT.check_file_exists( relative_folder_path = relative_folder_path, file_name = file_name ):
				return Reader( file_path )
			else:
				self.P.write_error( "MRT_Reader: load_records: " + str(file_path) + "does not exists..." )
				return None
			
	def is_RIB_record( self, record = None ):
		record = record.mrt

		if record.type is 13:
			if record.subtype is 2:
				return True
			elif record.subtype is 4:
				return True

		return False

	def __get_prefix( self, nlri ):
		return str( nlri.__dict__['prefix'] ) + "/" + str( nlri.__dict__['plen'] )

	def get_RIB_routes( self, record = None, split_prefix = True ):
		RIB_entries = record.mrt.__dict__['rib'].__dict__['entry']
		routes = list()

		for index in range( 0, len( RIB_entries ) ):
			routes.extend( self.__get_single_RIB_entry( record = record, index = index, split_prefix = split_prefix ) )

		return routes

	def __get_single_RIB_entry( self, record = None, index = None, split_prefix = None ):
		RIB_entries = record.mrt.__dict__['rib'].__dict__['entry']

		if index > len( RIB_entries ) - 1:
			return list()	

		RIB_enty = RIB_entries[index]

		routes = list()
		next_hops = list()

		prefixes = list()
		prefixes.append( self.__get_prefix( nlri = record.mrt.__dict__['rib'] ) )
		
		time_stamp = self.get_time_stamp( record = record )
	
		path = None
		for attr in RIB_enty.__dict__['attr']:
			if attr.__dict__['type'] == 2:

				if len( attr.__dict__['as_path'] ) == 0:
					return list()

				path = attr.__dict__['as_path'][0]['val']
				
				for x in range( 0, len(path) ):
					path[x] = int(path[x])

				if len(path) > 0:
					path = path[::-1]
				else:
					return list()

			if attr.__dict__['type'] == 3:
				next_hops.append( attr.__dict__['next_hop'] )

			if attr.__dict__['type'] == 14:
				next_hops.extend( attr.__dict__['mp_reach']['next_hop'] )

				for nlri in attr.__dict__['mp_reach']['nlri']:
					prefixes.append( self.__get_prefix( nlri = nlri ) )

		if path is None:
			self.P.write_error( "MRT_Reader: __get_single_RIB_entry: path is None" )
			self.print_record( record = record )
			return list()

		if next_hops is None:
			self.P.write_error( "MRT_Reader: __get_single_RIB_entry: next_hops is None" )
			self.print_record( record = record )
			return list()

		if len(next_hops) == 0:
			self.P.write_error( "MRT_Reader: __get_single_RIB_entry: len(next_hops) == 0" )
			self.print_record( record = record )
			return list()

		prefixes = list(set(prefixes))
		next_hops = list(set(next_hops))

		for prefix in prefixes:
			ip_range = IPNetwork( prefix )
			start_IP = str(ip_range[0])
			end_IP = str(ip_range[ ip_range.size - 1 ] )

			next_hops = [ "10.0.0.0" ]

			for next_hop in next_hops:
				route = dict()
				route['time'] = time_stamp

				if split_prefix is True:
					route['start_IP'] = start_IP
					route['end_IP'] = end_IP
				
				route['prefix'] = prefix
				route['path'] = path
				route['source_AS'] = int( path[0] )
				route['dest_AS'] = int( path[ len(path) - 1 ] )
				route['mode'] = "up"
				route['added_rib'] = route['time']
				#route['next_hop'] = next_hop

				routes.append( route)

		return routes

	def is_state_change_record( self, record = None ):
		record = record.mrt

		if record.type is 16:
			if record.subtype is 5:
				return True

		return False

	def get_new_state( self, record = None ):
		return record.mrt.bgp.__dict__['new_state']

	def get_peer_AS( self, record = None ):
		return record.mrt.bgp.__dict__['peer_as']

	def is_update_record( self,record = None ):
		record = record.mrt

		if record.type is 16:
			if record.subtype is 1:
				return True
			elif record.subtype is 4:
				return True

		return False

	def get_update_routes( self, record = None, split_prefix = True ):
		bgp = record.mrt.bgp
		routes = list()

		time = self.get_time_stamp( record = record )
		dest_AS = int( self.get_peer_AS( record = record ) )
		path = None
		source_AS = None

		nlris = list()
		if bgp.msg.__dict__['nlri'] is not None:
			for nlri in bgp.msg.__dict__['nlri']:
				nlris.append( self.__get_prefix( nlri = nlri ) )

		next_hops = list()

		withdraws = list()
		if record.mrt.__dict__['bgp'].__dict__['msg'].__dict__['withdrawn'] is not None:
			for withdraw in record.mrt.__dict__['bgp'].__dict__['msg'].__dict__['withdrawn']:
				withdraws.append( self.__get_prefix( nlri = withdraw ) )

		bgp = record.mrt.bgp
		attrs = bgp.msg.__dict__['attr']
		if attrs is not None:
			for attr in attrs:
				if attr.__dict__['type'] == 2:
					path = attr.__dict__['as_path'][0]['val'][::-1]

					for x in range( 0, len(path) ):
						path[x] = int(path[x])

					source_AS = int( path[0] )

				elif attr.__dict__['type'] == 3:
					next_hops.append( attr.__dict__['next_hop'] )

				elif attr.__dict__['type'] == 14:
					next_hops.extend( attr.__dict__['mp_reach']['next_hop'] )

					for nlri in attr.__dict__['mp_reach']['nlri']:
						nlris.append( self.__get_prefix( nlri = nlri ) )

				elif attr.__dict__['type'] == 15:
					for withdraw in attr.__dict__['mp_unreach']['withdrawn']:
						withdraws.append( self.__get_prefix( nlri = withdraw ) )

	
		next_hops.append( bgp.__dict__['peer_ip'] )
		next_hops = list(set(next_hops))
		withdraws = list(set(withdraws))

		for prefix in withdraws:
			route = dict()
			ip_range = IPNetwork( prefix )

			if split_prefix is True:
				route['start_IP'] = str(ip_range[0])
				route['end_IP'] = str(ip_range[ ip_range.size - 1 ])
			else:
				route['prefix'] = prefix

			route['time'] = time
			#route['next_hop'] = "10.0.0.0"

			if path is None or len(path) == 0:
				route['mode'] = "withdraw"
				route['dest_AS'] = dest_AS
				routes.append( route )
			else:
				route['mode'] = "down"
				route['path'] = path
				route['dest_AS'] = dest_AS
				route['source_AS'] = source_AS
				routes.append( route )

		for prefix in nlris:
			route = dict()
			ip_range = IPNetwork( prefix )

			if split_prefix is True:
				route['start_IP'] = str(ip_range[0])
				route['end_IP'] = str(ip_range[ ip_range.size - 1 ])
			
			route['prefix'] = prefix
			route['time'] = time
			route['mode'] = "up"
			route['path'] = path
			route['dest_AS'] = dest_AS
			route['source_AS'] = source_AS
			#route['next_hop'] = "10.0.0.0"
			routes.append( route )

		return routes

	def is_keep_alive_record( self,record = None ):
		return None

	def get_time_stamp( self, record = None ):
		return record.mrt.ts

	def __is_instance( self, item ):
		if "instance" in str( type(item) ):
			return True
		else:
			return False

	def print_record( self, record = None ):
		data_JSON = self.get_data_JSON( record = record )
		self.P.write_JSON( data_JSON = data_JSON )

	def get_data_JSON( self, record = None ):
		try:
			return self.__get_data_JSON( record = record.mrt )
		except( AttributeError ):
			return self.__get_data_JSON( record = record )

	def __get_data_JSON( self, record = None ):
		data_JSON = dict()

		if type(record) is dict:
			for key in record:
				data_JSON[key] = self.__get_data_JSON( record = record[key] )
		elif type(record) is list:
			temp_data = list()
			for item in record:
				temp_data.append( self.__get_data_JSON( record = item ) )

			return temp_data
		elif type(record) is int:	
			return record
		elif type(record) is str:	
			return str(record)
		else:
			for key in record.__dict__:
				item = record.__dict__[key]

				if item is None:
					continue

				elif self.__is_instance(item):
					data_JSON[key] = self.__get_data_JSON( record = record.__dict__[key] )

				elif type(item) is list:
					data_JSON[key] = list()
					for x in range( 0, len(item) ):
						data_JSON[key].append( self.__get_data_JSON( record = record.__dict__[key][x] ) )

				elif type(item) is dict:
					data_JSON[key] = dict()

					for key_2 in item:
						data_JSON[key][key_2] = self.__get_data_JSON( record = item[key_2] )

				elif "buf" not in key and "marker" not in key:
					data_JSON[key] = record.__dict__[key]

		return data_JSON










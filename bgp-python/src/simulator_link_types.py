import json, requests, os, sys, hashlib, copy, time

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer

class Simulator_Link_Types():
	P = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Link_Types: __init__ : P is None" )

		self.P.write( "Simulator_Link_Types: Loading...", color = 'cyan' )

		self.TYPE_P2P = 0
		self.TYPE_C2P = 1
		self.TYPE_P2C = 2
		self.TYPE_S2S = 3

	def get_P2P_type( self ):
		return self.TYPE_P2P

	def get_C2P_type( self ):
		return self.TYPE_C2P

	def get_P2C_type( self ):
		return self.TYPE_P2C

	def get_S2S_type( self ):
		return self.TYPE_S2S

	def get_type( self, AS_graph = None, from_AS = None, to_AS = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Link_Types: get_type: AS_graph is None")
			return

		if from_AS is None:
			self.P.write_error( "Simulator_Link_Types: get_type: from_AS is None")
			return

		if to_AS is None:
			self.P.write_error( "Simulator_Link_Types: get_type: to_AS is None")
			return

		if str(from_AS) not in AS_graph:
			self.P.write_error( "Simulator_Link_Types: get_type: AS" + str(from_AS) + " is not in AS_graph" )
			return -1 

		if str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			self.P.write_error( "Simulator_Link_Types: get_type: AS" + str(to_AS) + " is not connected with AS" + str(from_AS) )
			exit()
			return -1 

		return AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['type']

	def get_type_str( self, AS_graph = None, from_AS = None, to_AS = None, type = None ):
		if type is None:
			if AS_graph is None:
				self.P.write_error( "Simulator_Link_Types: get_type_str: AS_graph is None")
				return

			if from_AS is None:
				self.P.write_error( "Simulator_Link_Types: get_type_str: from_AS is None")
				return

			if to_AS is None:
				self.P.write_error( "Simulator_Link_Types: get_type_str: to_AS is None")
				return

			type = self.get_type( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )

		if int(type) == self.TYPE_P2P:
			return "p2p"
		elif int(type) == self.TYPE_C2P:
			return "c2p"
		elif int(type) == self.TYPE_P2C:
			return "p2c"
		elif int(type) == self.TYPE_S2S:
			return "s2s"
		else:
			return "NF"

	def get_types( self, AS_graph = None, route = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Link_Types: get_types: AS_graph is None")
			return

		if route is None:
			self.P.write_error( "Simulator_Link_Types: get_types: route is None")
			return
			
		AS_list = route['path']
		types = list()
		for x in range( 0, len(AS_list) - 1 ):
			from_AS = str(AS_list[x])
			to_AS = str(AS_list[x+1])

			type = self.get_type( AS_graph = AS_graph, from_AS = from_AS, to_AS = to_AS )
			types.append( type )

		return types

	def get_types_str( self, AS_graph = None, route = None, types = None ):
		if types is None:
			if AS_graph is None:
				self.P.write_error( "Simulator_Link_Types: get_types_str: AS_graph is None")
				return

			if route is None:
				self.P.write_error( "Simulator_Link_Types: get_types_str: route is None")
				return

			types = self.get_types( AS_graph = AS_graph, route = route )

		types_str = list()

		for type in types:
			types_str.append( self.get_type_str( type = type ) )

		return types_str

	def get_database_tag( self, AS_graph = None, from_AS = None, to_AS = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Link_Types: get_database_tag: AS_graph is None")
			return

		if from_AS is None:
			self.P.write_error( "Simulator_Link_Types: get_database_tag: from_AS is None")
			return

		if to_AS is None:
			self.P.write_error( "Simulator_Link_Types: get_database_tag: to_AS is None")
			return

		if str(from_AS) not in AS_graph:
			return -1 

		if str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			return -1 

		return AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['database_tag']

	def get_LOCAL_PREFERENCE( self, AS_graph = None, from_AS = None, to_AS = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Link_Types: get_LOCAL_PREFERENCE: AS_graph is None")
			return

		if from_AS is None:
			self.P.write_error( "Simulator_Link_Types: get_LOCAL_PREFERENCE: from_AS is None")
			return

		if to_AS is None:
			self.P.write_error( "Simulator_Link_Types: get_LOCAL_PREFERENCE: to_AS is None")
			return

		if str(from_AS) not in AS_graph:
			return -1 

		if str(to_AS) not in AS_graph[ str(from_AS) ]['NEIGHBORS']:
			return -1 

		return AS_graph[ str(from_AS) ]['NEIGHBORS'][ str(to_AS) ]['LOCAL_PREFERENCE']

	



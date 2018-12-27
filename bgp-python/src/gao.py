import json, requests, os, sys, hashlib, copy, time, random

from printer import Printer
from file_tool import File_Tool

from simulator_interface import Simulator_Interface

class Gao():
	P = None
	SI = None
	FT = None

	paths = None
	relations = None

	number_of_links = None
	transit = None
	not_p2p = None
	neighbours = None

	def __init__( self, P = None, FT = None, SI = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Gao: __init__ : P is None" )

		self.P.write( "Gao: Loading...", color = 'cyan' )

		if SI is None:
			self.P.write_error( "Gao: __init__ : SI is None" )
			return

		self.SI = SI

		if FT is None:
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Gao" )
		else:
			self.FT = FT

		self.paths = dict()
		self.relations = dict()

		self.transit = dict()
		self.not_p2p = dict()
		self.neighbours = dict()
		self.degree = dict()

	def reset( self ):
		self.paths = dict()
		self.relations = dict()

		self.transit = dict()
		self.not_p2p = dict()
		self.neighbours = dict()
		self.degree = dict()

	def load_paths( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "Gao: load_paths: file_name is None" )
			return None

		file_name = file_name.split('.')[0] + ".paths"
		file_path = self.FT.get_file_path( file_name = file_name )

		if self.FT.check_file_exists( file_name = file_name ) is False:
			self.P.write_warning( "Gao: load_paths: " + str(file_path) + " not found" )
		elif self.FT.check_checksum( file_name = file_name ) is True:
			data_JSON = self.FT.load_JSON_file( file_name = file_name, print_status = True )

			self.paths = data_JSON
		else:
			self.P.write_warning( "Gao: load_paths: " + str(file_path) + ": checksum incorrect or missing" )

	def save_paths( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "Gao: save_paths: file_name is None" )
			return None

		self.P.write( "Gao: save_paths: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".paths"

		self.FT.save_JSON_file( data_JSON = self.paths, file_name = file_name, print_status = True )
		self.FT.create_checksum( file_name = file_name, print_status = True )

	def add_paths( self, paths = None ):
		if paths is None:
			self.P.write_error( "Gao: add_paths: paths is None" )
			return

		for path in paths:
			self.add_path( path = path )

	def add_path( self, path = None ):
		if path is None:
			self.P.write_error( "Gao: add_path: path is None" )
			return

		for x in range(len(path) - 1, 0, -1):
			if path[x] == path[x-1]:
				path.pop(x)

		if str(path) not in self.paths:
			self.paths[ str(path) ] = 0

		self.paths[ str(path) ] += 1

	def run( self, print_debug = False ):
		self.P.write( "Gao: run: start", color = 'green' )
		self.__stage_1( print_debug = print_debug )
		self.__stage_2( print_debug = print_debug )
		self.__stage_3( print_debug = print_debug )
		self.__stage_4( print_debug = print_debug )
		self.__stage_5( print_debug = print_debug )
		self.__stage_6( print_debug = print_debug )
		self.__stage_statistics( print_debug = print_debug )

	def get_relations( self ):
		return self.relations 

	def __increment_transit( self, from_AS = None, to_AS = None ):
		_id = str(from_AS) + "_" + str(to_AS)

		if _id not in self.transit:
			self.transit[ _id ] = 0
		else:
			self.transit[ _id ] += 1

	def __get_transit( self, from_AS = None, to_AS = None ):
		_id = str(from_AS) + "_" + str(to_AS)

		if _id in self.transit:
			return self.transit[ _id ]
		else:
			return 0

	def __set_not_p2p( self, from_AS = None, to_AS = None, status = None ):
		_id = str(from_AS) + "_" + str(to_AS)
		self.not_p2p[ _id ] = status
		
	def __get_not_p2p( self, from_AS = None, to_AS = None ):
		_id = str(from_AS) + "_" + str(to_AS)
		return self.not_p2p[ _id ]

	def __add_neighbour( self, AS_number = None, neighbour_AS = None ):
		if str(AS_number) not in self.neighbours:
			self.neighbours[ str(AS_number) ] = list()

		if neighbour_AS not in self.neighbours[ str(AS_number) ]:
			self.neighbours[ str(AS_number) ].append( neighbour_AS )

	def __add_relation( self, from_AS = None, to_AS = None, type = None ):
		relation = self.SI.create_relation( from_AS = from_AS, to_AS = to_AS, type = type )
		relation_id = self.SI.get_relation_id( relation = relation )

		if relation_id not in self.relations:
			self.relations[ relation_id ] = relation
			return 1
		else:
			return 0

	def __get_relation_type( self, from_AS = None, to_AS = None ):
		relation_id = self.SI.get_relation_id( from_AS = from_AS, to_AS = to_AS )
		if relation_id in self.relations:
			return self.relations[ relation_id ]['type']
		else:
			return -1

	def __stage_1( self, print_debug = False ):
		self.P.write( "Gao: __stage_1: start" )

		AS_counter = dict()
		link_counter = dict()

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_1: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			for x in range(len(path) - 1, 0, -1):
				if path[x] not in AS_counter:
					AS_counter[ path[x] ] = None

				if path[x-1] not in AS_counter:
					AS_counter[ path[x-1] ] = None

				_id_1 = str( path[x] ) + "_" + str( path[x-1] )
				_id_2 = str( path[x-1] ) + "_" + str( path[x] )

				if _id_1 not in link_counter:
					link_counter[ _id_1 ] = None

				if _id_2 not in link_counter:
					link_counter[ _id_2 ] = None

				self.__set_not_p2p( from_AS = path[x], to_AS = path[x-1], status = False )
				self.__set_not_p2p( from_AS = path[x-1], to_AS = path[x], status = False )

		self.number_of_links = len(link_counter)
		self.P.write( "Gao: __stage_1: found " + str(len(AS_counter)) + " ASes and " + str(len(link_counter)) + " links" )

	def __stage_2( self, print_debug = False ):
		self.P.write( "Gao: __stage_2: start" )

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_2: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			for x in range(0, len(path) - 1):
				self.__add_neighbour( AS_number = path[x], neighbour_AS = path[x+1] )
				self.__add_neighbour( AS_number = path[x+1], neighbour_AS = path[x] )

		for AS_number in self.neighbours:
			self.degree[ str(AS_number) ] = len( self.neighbours[ str(AS_number) ] )	

	def __stage_3( self, print_debug = False ):
		self.P.write( "Gao: __stage_3: start" )

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_3: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			largest_degree = 0
			index = len(path) - 1
			for x in range(len(path) - 1, -1, -1):
				if self.degree[ str( path[x] ) ] >= largest_degree:
					largest_degree = self.degree[ str( path[x] ) ]
					index = x

			for x in range(0, index - 1):
				self.__increment_transit( from_AS = path[x], to_AS = path[x+1] )

			for x in range(index, len(path) - 1):
				self.__increment_transit( from_AS = path[x+1], to_AS = path[x] )

	def __stage_4( self, print_debug = False ):
		L = 1
		S2S_counter = 0
		C2P_counter = 0
		P2C_counter = 0

		self.P.write( "Gao: __stage_4: start (L = " + str(L) + ")" )

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_4: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			for x in range(0, len(path) - 1):
				transit_A = self.__get_transit( from_AS = path[x], to_AS = path[x+1] )
				transit_B = self.__get_transit( from_AS = path[x+1], to_AS = path[x] )

				if transit_A > L and transit_B > L:
					S2S_counter += self.__add_relation( from_AS = path[x], to_AS = path[x+1], type = self.SI.get_S2S_type() )
					S2S_counter += self.__add_relation( from_AS = path[x+1], to_AS = path[x], type = self.SI.get_S2S_type() )

				elif transit_A > 0 and transit_B > 0 and transit_A <= L and transit_B <= L:
					S2S_counter += self.__add_relation( from_AS = path[x], to_AS = path[x+1], type = self.SI.get_S2S_type() )
					S2S_counter += self.__add_relation( from_AS = path[x+1], to_AS = path[x], type = self.SI.get_S2S_type() )

				elif transit_B > L and transit_A == 0:
					P2C_counter += self.__add_relation( from_AS = path[x], to_AS = path[x+1], type = self.SI.get_P2C_type() )
					C2P_counter += self.__add_relation( from_AS = path[x+1], to_AS = path[x], type = self.SI.get_C2P_type() )

				elif transit_A > L and transit_B == 0:
					C2P_counter += self.__add_relation( from_AS = path[x], to_AS = path[x+1], type = self.SI.get_C2P_type() )
					P2C_counter += self.__add_relation( from_AS = path[x+1], to_AS = path[x], type = self.SI.get_P2C_type() )

		self.P.write( "Gao: __stage_4: inferred " + str(S2S_counter) + " s2s links, " + str(C2P_counter) + " c2p links and " + str(P2C_counter) + " p2c links" )

	def __stage_5( self, print_debug = False ):
		self.P.write( "Gao: __stage_5: start" )

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_5: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			largest_degree = 0
			index = len(path) - 1
			for x in range(len(path) - 1, -1, -1):
				if self.degree[ str( path[x] ) ] >= largest_degree:
					largest_degree = self.degree[ str( path[x] ) ]
					index = x

			for x in range( 0, index - 2 ):
				self.__set_not_p2p( from_AS = path[x], to_AS = path[x+1], status = True )

			for x in range( index + 1, len(path) - 1 ):
				self.__set_not_p2p( from_AS = path[x], to_AS = path[x+1], status = True )

			if index > 0 and index < len(path) - 1:
				type_A = self.__get_relation_type( from_AS = path[ index ], to_AS = path[ index + 1 ] )
				type_B = self.__get_relation_type( from_AS = path[ index + 1 ], to_AS = path[ index ] )

				if type_A != self.SI.get_S2S_type and type_B != self.SI.get_S2S_type:
					if self.degree[ str( path[ index - 1] ) ] > self.degree[ str( path[ index + 1 ] ) ]:
						self.__set_not_p2p( from_AS = path[ index ], to_AS = path[ index + 1 ], status = True )
					else:
						self.__set_not_p2p( from_AS = path[ index - 1 ], to_AS = path[ index ], status = True )

	def __stage_6( self, print_debug = False ):
		R = 0.1
		self.P.write( "Gao: __stage_6: start (R = " + str(R) + ")" )

		P2P_counter = 0
		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_6: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])
				
			for x in range(0, len(path) - 1):
				not_p2p_A = self.__get_not_p2p( from_AS = path[x], to_AS = path[x+1] )
				not_p2p_B = self.__get_not_p2p( from_AS = path[x+1], to_AS = path[x] )

				if not_p2p_A is False and not_p2p_B is False:
					degree_A = self.degree[ str( path[ x ] ) ]
					degree_B = self.degree[ str( path[ x + 1 ] ) ]

					if ( degree_A / degree_B ) < R and ( degree_B / degree_A ) < (1/R):
						P2P_counter += self.__add_relation( from_AS = path[x], to_AS = path[x+1], type = self.SI.get_P2P_type() )
						P2P_counter += self.__add_relation( from_AS = path[x+1], to_AS = path[x], type = self.SI.get_P2P_type() )

		self.P.write( "Gao: __stage_6: inferred " + str(P2P_counter) + " p2p links" )

	def __stage_statistics( self, print_debug = False ):
		if print_debug is True:
			self.P.write_debug( "Gao: __stage_statistics: start" )

		S2S_counter = 0
		P2P_counter = 0
		C2P_counter = 0
		P2C_counter = 0

		counter = len(self.relations)
		for relation_id in self.relations:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tGao: __stage_statistics: " + str(counter/1000)  + "k relations left      " )

			if self.relations[ relation_id ]['type'] == self.SI.get_S2S_type():
				S2S_counter += 1
			elif self.relations[ relation_id ]['type'] == self.SI.get_P2P_type():
				P2P_counter += 1
			elif self.relations[ relation_id ]['type'] == self.SI.get_C2P_type():
				C2P_counter += 1
			elif self.relations[ relation_id ]['type'] == self.SI.get_P2C_type():
				P2C_counter += 1

		self.P.write( "Gao: __stage_statistics: inferred " + str(S2S_counter) + " s2s links" )
		self.P.write( "Gao: __stage_statistics: inferred " + str(P2P_counter) + " p2p links" )
		self.P.write( "Gao: __stage_statistics: inferred " + str(C2P_counter) + " c2p links" )
		self.P.write( "Gao: __stage_statistics: inferred " + str(P2C_counter) + " p2c links" )
		self.P.write( "Gao: __stage_statistics: inferred " + str(S2S_counter+P2P_counter+C2P_counter+P2C_counter) + " s2s, p2p, c2p, and p2c links" )
		self.P.write( "Gao: __stage_statistics: started with " + str(self.number_of_links) + " unknown links" )
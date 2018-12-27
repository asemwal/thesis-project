import json, requests, os, sys, hashlib, copy, time, random, networkx

from printer import Printer
from file_tool import File_Tool

from simulator_interface import Simulator_Interface

class IMC13():
	P = None

	paths = None
	unique_paths = None
	triplet_paths = None
	relations = None

	transit = None
	degree = None
	neighbours = None
	sorted_ASes = None
	clique_ASes = None
	stub_ASes = None
	number_of_links = None
	
	def __init__( self, P = None, FT = None, SI = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "IMC13: __init__ : P is None" )

		self.P.write( "IMC13: Loading...", color = 'cyan' )

		if SI is None:
			self.P.write_error( "IMC13: __init__ : SI is None" )
			return

		self.SI = SI
		
		if FT is None:
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "IMC13" )
		else:
			self.FT = FT

		self.paths = dict()
		self.triplet_paths = dict()
		self.relations = dict()

		self.transit = dict()
		self.degree = dict()
		self.neighbours = dict()
		self.sorted_ASes = list()
		self.stub_ASes = list()

	def load_paths( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "IMC13: load_paths: file_name is None" )
			return None

		file_name = file_name.split('.')[0] + ".paths"
		file_path = self.FT.get_file_path( file_name = file_name )

		if self.FT.check_file_exists( file_name = file_name ) is False:
			self.P.write_warning( "Gao: load_paths: " + str(file_path) + " not found" )
		elif self.FT.check_checksum( file_name = file_name ) is True:
			data_JSON = self.FT.load_JSON_file( file_name = file_name, print_status = True )

			self.paths = data_JSON
		else:
			self.P.write_warning( "IMC13: load_paths: " + str(file_path) + ": checksum incorrect or missing" )

	def save_paths( self, file_name = None ):
		if file_name is None:
			self.P.write_error( "IMC13: save_paths: file_name is None" )
			return None

		self.P.write( "IMC13: save_paths: start", color = 'green' )

		file_name = file_name.split('.')[0] + ".paths"

		self.FT.save_JSON_file( data_JSON = self.paths, file_name = file_name, print_status = True )
		self.FT.create_checksum( file_name = file_name, print_status = True )

	def add_paths( self, paths = None ):
		if paths is None:
			self.P.write_error( "IMC13: add_paths: paths is None" )
			return

		for path in paths:
			self.add_path( path = path )

	def add_path( self, path = None ):
		if path is None:
			self.P.write_error( "IMC13: add_path: path is None" )
			return

		for x in range(len(path) - 1, 0, -1):
			if path[x] == path[x-1]:
				path.pop(x)

		if str(path) not in self.paths:
			self.paths[ str(path) ] = 0

		self.paths[ str(path) ] += 1

	def __add_triplet_path( self, triplet_path = None ):
		path_id = hashlib.sha256( str(triplet_path) ).hexdigest()	
		self.triplet_paths[ path_id ] = triplet_path
		return

	def __increment_transit( self, AS_number = None, amount = None ):
		if str(AS_number) not in self.transit:
			self.transit[ str(AS_number) ] = 0
		else:
			self.transit[ str(AS_number) ] += amount

	def __get_transit( self, AS_number = None ):
		if str(AS_number) in self.transit:
			return self.transit[ str(AS_number) ]
		else:
			return 0

	def __add_neighbour( self, AS_number = None, neighbour_AS = None ):
		if str(AS_number) not in self.neighbours:
			self.neighbours[ str(AS_number) ] = list()

		if str(neighbour_AS) not in self.neighbours[ str(AS_number) ]:
			self.neighbours[ str(AS_number) ].append( str(neighbour_AS) )

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

	def __maximum_clique( self, AS_numbers = None ):
		g = networkx.Graph()

		for AS_number in AS_numbers:
			for neighbour in self.neighbours[ str(AS_number) ]:
				if str(neighbour) in AS_numbers or int(neighbour) in AS_numbers:
					g.add_edge( int(AS_number), int(neighbour) )

		
		#print g.edges()

		cliques = list( networkx.find_cliques(g) )

		size = 0
		largest_clique = []
		for clique in cliques:
			if len(clique) > size:
				size = len(clique)
				largest_clique = clique

		return largest_clique

	def run( self, print_debug = False ):
		self.__stage_1( print_debug = print_debug )
		self.__stage_2( print_debug = print_debug )
		self.__stage_3( print_debug = print_debug )
		self.__stage_4( print_debug = print_debug )
		self.__stage_5( print_debug = print_debug )
		self.__stage_6( print_debug = print_debug )
		self.__stage_7( print_debug = print_debug )
		self.__stage_8( print_debug = print_debug )
		self.__stage_9( print_debug = print_debug )
		self.__stage_10( print_debug = print_debug )
		self.__stage_11( print_debug = print_debug )
		self.__stage_12( print_debug = print_debug )
		self.__stage_13( print_debug = print_debug )
		self.__stage_14( print_debug = print_debug )
		self.__stage_statistics( print_debug = print_debug )

	def get_relations( self ):
		return self.relations 

	def __stage_1( self, print_debug = False ):
		self.P.write( "IMC13: __stage_1: start", color = 'green' )

		AS_counter = dict()
		link_counter = dict()

		counter = len(self.paths)
		for path_str in self.paths:
			amount = self.paths[ path_str ]

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_1: " + str(counter/1000)  + "k paths left      " )

			for x in range( 0, amount ):
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

		self.number_of_links = len(link_counter)
		self.P.write( "IMC13: __stage_1: found " + str(len(AS_counter)) + " ASes and " + str(len(link_counter)) + " links" )

	def __stage_2( self, print_debug = False ):
		self.P.write( "IMC13: __stage_2: start", color = 'green' )

		remove_ids = dict()

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_2: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			for x in range(0, len(path)):
				for y in range(x+1, len(path)):
					if path[x] == path[y]:
						remove_ids[ path_str ] = None

		for path_str in remove_ids:
			del self.paths[path_str]

		self.P.write( "IMC13: __stage_2: removed " + str(len(remove_ids)) + " poisened paths" )

	def __stage_3( self, print_debug = False ):
		self.P.write( "IMC13: __stage_3: start", color = 'green' )

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_3: " + str(counter/1000)  + "k paths left      " )

			amount = self.paths[ path_str ]
			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			for x in range(0, len(path) - 1):
				self.__add_neighbour( AS_number = path[x], neighbour_AS = path[x+1] )
				self.__add_neighbour( AS_number = path[x+1], neighbour_AS = path[x] )

			for x in range(1, len(path) - 1):
				self.__increment_transit( AS_number = path[x], amount = amount )

		for AS_number in self.neighbours:
			self.degree[ str(AS_number) ] = len( self.neighbours[ str(AS_number) ] )	

		#Sorting the ASes in decreasing order of transit degree, then node degree
		temp = dict()
		for AS_number in self.transit:
			temp[str(AS_number)] = self.transit[str(AS_number)] * 1000 + self.degree[str(AS_number)]

		self.sorted_ASes = sorted( temp, key=temp.__getitem__, reverse = True )

	def __stage_4( self, print_debug = False ):
		self.P.write( "IMC13: __stage_4: start", color = 'green' )

		C1 = self.__maximum_clique( AS_numbers = self.sorted_ASes[:10] )
		C2 = list()

		temp_counter = len(self.sorted_ASes) - 10
		for x in range( 10, len(self.sorted_ASes) ):
			temp_counter -= 1
			self.P.rewrite( "\tIMC13: __stage_4: " + str(temp_counter)  + " ASes left      " )

			AS_number = self.sorted_ASes[ x ]
			counter = len(C1)

			for clique_AS in C1:
				if str(clique_AS) not in self.neighbours[ str(AS_number) ]:
					counter -= 1

			if counter == len(C1):
				if print_debug is True:
					self.P.write_debug( "\tIMC13: __stage_4: added AS" + str(AS_number) + " to C1" )

				C1.append( int(AS_number) )

			elif counter == len(C1) - 1:
				if print_debug is True:
					self.P.write_debug( "\tIMC13: __stage_4: added AS" + str(AS_number) + " to C2" )

				C2.append( int(AS_number) )

		self.clique_ASes = self.__maximum_clique( AS_numbers = list( set(C1 + C2) ) )
		if print_debug is True:
			self.P.write_debug( "\tIMC13: __stage_4: found " + str( len(self.clique_ASes) ) + " clique_AS" )
			self.P.write_debug( "\tIMC13: __stage_4: " + str(self.clique_ASes) )

		P2P_counter = 0
		for from_AS in self.clique_ASes:
			for to_AS in self.clique_ASes:
				if from_AS != to_AS:
					P2P_counter += self.__add_relation( from_AS = from_AS, to_AS = to_AS, type = self.SI.get_P2P_type() )

		self.P.write( "IMC13: __stage_4: inferred " + str(P2P_counter) + " p2p links" )

	def __stage_5( self, print_debug = False ):
		self.P.write( "IMC13: __stage_5: start", color = 'green' )

		remove_ids = dict()
		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_5: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])
			
			if len(path) < 3:
				continue

			for x in range(0, len(path) - 2):
				if path[x] in self.clique_ASes and not path[x+1] in self.clique_ASes and path[x+2] in self.clique_ASes:
					remove_ids[path_str] = None

		for path_str in remove_ids:
			del self.paths[path_str]

		self.P.write( "IMC13: __stage_5: removed " + str(len(remove_ids)) + " poisened paths" )

	def __stage_6( self, print_debug = False ):
		self.P.write( "IMC13: __stage_6: start", color = 'green' )

		possible_stubs = dict()
		non_stubs = dict()

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_6: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			if int( path[0] ) not in non_stubs:
				possible_stubs[ int( path[0] ) ] = None

			if int( path[ len(path) - 1 ] ) not in non_stubs:
				possible_stubs[ int( path[ len(path) - 1 ] ) ] = None

			for x in range(1, len(path) - 1):
				if int( path[x] ) not in non_stubs:
					non_stubs[ int( path[x] ) ] = None

					if int( path[x] ) in possible_stubs:
						del possible_stubs[ int( path[x] ) ]

		for stub_AS in possible_stubs:
			self.stub_ASes.append( int(stub_AS) )

		self.P.write( "IMC13: __stage_6: found " + str(len(self.stub_ASes)) + " stub ASes" )

	def __stage_7( self, print_debug = False ):
		self.P.write( "IMC13: __stage_7: start", color = 'green' )

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_7: " + str(counter/1000)  + "k paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			if len(path) < 3:
				continue

			for x in range(1, len(path) - 2):
				self.__add_triplet_path( triplet_path = path[x:x+3] )

		self.P.write( "IMC13: __stage_7: added " + str(len(self.triplet_paths)/1000) + "k unique AS triplets" )

	def __stage_8( self, print_debug = False ):
		self.P.write( "IMC13: __stage_8: start", color = 'green' )

		P2C_counter = 0
		C2P_counter = 0

		counter = len(self.sorted_ASes)
		for AS_number in self.sorted_ASes:
			counter -= 1
			self.P.rewrite( "\tIMC13: __stage_8: " + str(counter)  + " ASes left      " )

			for path_id in self.triplet_paths:
				triplet_path = self.triplet_paths[ path_id ]

				if int(triplet_path[2]) == int(AS_number):
					type = self.__get_relation_type( from_AS = triplet_path[0], to_AS = triplet_path[1] )

					if type == self.SI.get_P2P_type() or type == self.SI.get_P2C_type():
						P2C_counter += self.__add_relation( from_AS = triplet_path[1], to_AS = triplet_path[2], type = self.SI.get_P2C_type() )
						C2P_counter += self.__add_relation( from_AS = triplet_path[2], to_AS = triplet_path[1], type = self.SI.get_C2P_type() )

		self.P.write( "IMC13: __stage_8: inferred " + str(P2C_counter) + " p2c links, and " + str(C2P_counter) + " c2p links" )

	def __stage_9( self, print_debug = False ):
		self.P.write( "IMC13: __stage_9: start", color = 'green' )

	def __stage_10( self, print_debug = False ):
		self.P.write( "IMC13: __stage_10: start", color = 'green' )

		P2C_counter = 0
		C2P_counter = 0

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			self.P.rewrite( "\tIMC13: __stage_10: " + str(counter/1000)  + "k unique paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			length = len(path)

			if length > 2:
				type = self.__get_relation_type( from_AS = path[  length - 3 ], to_AS = path[  length - 2 ] )

				if type == self.SI.get_P2P_type():
					transit_A = self.__get_transit( AS_number = path[ length - 1 ] )
					transit_B = self.__get_transit( AS_number = path[ length - 2 ] )

					if transit_A > transit_B:
						P2C_counter += self.__add_relation( from_AS = path[ length - 2 ], to_AS = path[ length - 1 ], type = self.SI.get_P2C_type() )
						C2P_counter += self.__add_relation( from_AS = path[ length - 1 ], to_AS = path[ length - 2 ], type = self.SI.get_C2P_type() )

		self.P.write( "IMC13: __stage_10: inferred " + str(P2C_counter) + " p2c links, and " + str(C2P_counter) + " c2p links" )

	def __stage_11( self, print_debug = False ):
		self.P.write( "IMC13: __stage_11: start", color = 'green' )

		P2P_counter = 0
		P2C_counter = 0
		C2P_counter = 0

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			self.P.rewrite( "\tIMC13: __stage_11: " + str(counter/1000)  + "k unique paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			length = len(path)

			index = 0
			for x in range(0, length - 1):
				type = self.__get_relation_type( from_AS = path[  length - 3 ], to_AS = path[  length - 2 ] )

				if type == self.SI.get_C2P_type():
					index += 1
				else:
					break

			if index < length - 2:
				type = self.__get_relation_type( from_AS = path[ index ], to_AS = path[ index + 1 ] )
				if type == -1:
					P2P_counter += self.__add_relation( from_AS = path[ length - 2 ], to_AS = path[ length - 1 ], type = self.SI.get_P2P_type() )
					P2P_counter += self.__add_relation( from_AS = path[ length - 1 ], to_AS = path[ length - 2 ], type = self.SI.get_P2P_type() )

					for y in range(index + 1, length - 1):
						P2C_counter += self.__add_relation( from_AS = path[ y ], to_AS = path[ y + 1 ], type = self.SI.get_P2C_type() )
						C2P_counter += self.__add_relation( from_AS = path[ y + 1 ], to_AS = path[ y ], type = self.SI.get_C2P_type() )

		self.P.write( "IMC13: __stage_11: inferred " + str(P2C_counter) + " p2c links, " + str(C2P_counter) + " c2p links, and " + str(P2P_counter) + " p2p links" )

	def __stage_12( self, print_debug = False ):
		self.P.write( "IMC13: __stage_12: start", color = 'green' )

		P2C_counter = 0
		C2P_counter = 0

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			self.P.rewrite( "\tIMC13: __stage_12: " + str(counter/1000)  + "k unique paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			if len(path) == 2:
				if path[0] in self.clique_ASes and path[1] in self.stub_ASes:
					type = self.__get_relation_type( from_AS = path[0], to_AS = path[1] )
					if type == -1:
						P2C_counter += self.__add_relation( from_AS = path[0], to_AS = path[1], type = self.SI.get_P2C_type() )
						C2P_counter += self.__add_relation( from_AS = path[1], to_AS = path[0], type = self.SI.get_C2P_type() )

		self.P.write( "IMC13: __stage_12: inferred " + str(P2C_counter) + " p2c links, and " + str(C2P_counter) + " c2p links" )

	def __stage_13( self, print_debug = False ):
		self.P.write( "IMC13: __stage_13: start", color = 'green' )

		P2C_counter = 0
		C2P_counter = 0

		counter = len(self.sorted_ASes)
		for AS_number in self.sorted_ASes:
			counter -= 1
			self.P.rewrite( "\tIMC13: __stage_13: " + str(counter)  + " ASes left      " )

			for path_id in self.triplet_paths:
				triplet_path = self.triplet_paths[ path_id ]

				if int( AS_number ) == int( triplet_path[1] ):
					type_A = self.__get_relation_type( from_AS = triplet_path[0], to_AS = triplet_path[1] )
					type_B = self.__get_relation_type( from_AS = triplet_path[1], to_AS = triplet_path[2] )

					if type_A == -1 and type_B == -1:
						for path_id_2 in self.triplet_paths:
							triplet_path_2 = self.triplet_paths[ path_id_2 ]

							if int(AS_number) == int( triplet_path_2[1] ) and int( triplet_path[0] ) == int( triplet_path_2[0] ):
								type_C = self.__get_relation_type( from_AS = triplet_path_2[1], to_AS = triplet_path_2[2] )

								if type_C == self.SI.get_C2P_type():
									P2C_counter += self.__add_relation( from_AS = triplet_path_2[0], to_AS = triplet_path_2[1], type = self.SI.get_P2C_type() )
									C2P_counter += self.__add_relation( from_AS = triplet_path_2[1], to_AS = triplet_path_2[0], type = self.SI.get_C2P_type() )

		self.P.write( "IMC13: __stage_13: inferred " + str(P2C_counter) + " p2c links, and " + str(C2P_counter) + " c2p links" )

	def __stage_14( self, print_debug = False ):
		self.P.write( "IMC13: __stage_14: start", color = 'green' )

		P2P_counter = 0

		counter = len(self.paths)
		for path_str in self.paths:
			counter -= 1
			self.P.rewrite( "\tIMC13: __stage_14: " + str(counter/1000)  + "k unique paths left      " )

			path = path_str[1:-1]
			path = path.split(",")
			for x in range( 0, len(path) ):
				path[x] = int(path[x])

			for x in range( 0, len(path) - 1 ):
				type_A = self.__get_relation_type( from_AS = path[x], to_AS = path[x+1] )
				type_B = self.__get_relation_type( from_AS = path[x+1], to_AS = path[x] )

				if type_A == -1 or type_A == -1:
					P2P_counter += self.__add_relation( from_AS = path[x], to_AS = path[x+1], type = self.SI.get_P2P_type() )
					P2P_counter += self.__add_relation( from_AS = path[x+1], to_AS = path[x], type = self.SI.get_P2P_type() )

		self.P.write( "IMC13: __stage_14: inferred " + str(P2P_counter) + " p2p links" )

	def __stage_statistics( self, print_debug = False ):
		self.P.write( "IMC13: __stage_statistics: start", color = 'green' )

		S2S_counter = 0
		P2P_counter = 0
		C2P_counter = 0
		P2C_counter = 0

		counter = len(self.relations)
		for relation_id in self.relations:
			counter -= 1
			if counter%1000 == 0:
				self.P.rewrite( "\tIMC13: __stage_statistics: " + str(counter/1000)  + "k relations left      " )
				
			if self.relations[ relation_id ]['type'] == self.SI.get_S2S_type():
				S2S_counter += 1
			elif self.relations[ relation_id ]['type'] == self.SI.get_P2P_type():
				P2P_counter += 1
			elif self.relations[ relation_id ]['type'] == self.SI.get_C2P_type():
				C2P_counter += 1
			elif self.relations[ relation_id ]['type'] == self.SI.get_P2C_type():
				P2C_counter += 1

		self.P.write( "IMC13: __stage_statistics: inferred " + str(S2S_counter) + " s2s links" )
		self.P.write( "IMC13: __stage_statistics: inferred " + str(P2P_counter) + " p2p links" )
		self.P.write( "IMC13: __stage_statistics: inferred " + str(C2P_counter) + " c2p links" )
		self.P.write( "IMC13: __stage_statistics: inferred " + str(P2C_counter) + " p2c links" )
		self.P.write( "IMC13: __stage_statistics: inferred " + str(S2S_counter+P2P_counter+C2P_counter+P2C_counter) + " s2s, p2p, c2p, and p2c links" )
		self.P.write( "IMC13: __stage_statistics: started with " + str(self.number_of_links) + " unknown links" )
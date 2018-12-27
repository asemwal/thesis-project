import json, requests, os, sys, hashlib, copy, time, random, ipaddress

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool
from simulator_AS_graph_tool import Simulator_AS_Graph_Tool
from simulator_routing_table_tool import Simulator_Routing_Table_Tool
from simulator_ES_trace_routes_tool import Simulator_ES_Trace_Routes_Tool

class Simulator_Random_AS_Graph_Tool():
	P = None
	FT = None
	SASGT = None
	SRTT = None
	SESTRT = None
	SLT = None

	def __init__( self, P = None, FT = None, SASGT = None, SRTT = None, SLT = None, SESTRT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Random_AS_Graph_Tool: __init__ : P is None" )

		self.P.write( "Simulator_Random_AS_Graph_Tool: Loading...", color = 'cyan' )
		
		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_Random_AS_Graph_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Random_AS_Graph_Tool" )

		if SASGT is not None:
			self.SASGT = SASGT
		else:
			self.P.write_warning( "Simulator_Random_AS_Graph_Tool: __init__ : SASGT is None" )
			self.SASGT = Simulator_AS_graph_Tool( P = self.P, SLT = self.SLT )

		if SRTT is not None:
			self.SRTT = SRTT
		else:
			self.P.write_warning( "Simulator_Random_AS_Graph_Tool: __init__ : SRTT is None" )
			self.SRTT = Simulator_Routing_Table_Tool( P = self.P, SLT = self.SLT )

		if SESTRT is not None:
			self.SESTRT = SESTRT
		else:
			self.P.write_warning( "Simulator_Random_AS_Graph_Tool: __init__ : SESTRT is None" )
			self.SESTRT = Simulator_ES_Trace_Routes_Tool( P = self.P )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_Random_AS_Graph_Tool: __init__ : SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

	def generate_random_AS_graph( self, start_size = None, AS_multiplier = None, number_of_tiers = None, second_provider_probability = None, peer_probability = None, print_debug = False ):
		if start_size is None:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: start_size is None" )
			return None

		if start_size < 2:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: start_size < 2" )
			return None

		if AS_multiplier is None:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: AS_multiplier is None" )
			return None

		if number_of_tiers is None:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: number_of_tiers is None" )
			return None	

		if second_provider_probability is None:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: second_provider_probability is None" )
			return None

		if peer_probability is None:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: peer_probability is None" )
			return None


		if len(second_provider_probability) != number_of_tiers:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: len(second_provider_probability) != number_of_tiers" )
			return None

		if len(peer_probability) != number_of_tiers:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: len(peer_probability) != number_of_tiers" )
			return None

		self.P.write( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: start", color = 'green' )

		p2p_counter = 0
		c2p_counter = 0
		AS_counter = 0
		tiers_dict = dict()
		AS_graph = self.SASGT.init_AS_graph()

		# Create ASes per tier
		current_size = start_size
		for current_tier in range( 0, number_of_tiers ):
			tiers_dict[ current_tier ] = dict()
			
			if current_tier != 0:
				current_size = current_size * AS_multiplier

			counter = current_size 
			for y in range( 0, current_size ):
				counter -= 1
				self.P.rewrite( "\tSimulator_Random_AS_Graph_Tool: Creating ASes for tier-" + str(current_tier+1) + ": " + str(counter) + " ASes left               " )

				AS_number = AS_counter
				AS_counter += 1
				tiers_dict[ current_tier ][ AS_number ] = None
				AS_graph = self.SASGT.add_AS( AS_graph = AS_graph, AS_number = AS_number, print_debug = print_debug )

		# Interconnect with P2P
		AS_numbers = tiers_dict[ 0 ].keys()
		counter = len(AS_numbers)
		for x in range( 0, len(AS_numbers) ):
			counter -= 1
			self.P.rewrite( "\tSimulator_Random_AS_Graph_Tool: Adding p2p links for tier-1: " + str(counter) + " ASes left               " )

			for y in range( x + 1, len(AS_numbers) ):
				if random.uniform(0, 1) < peer_probability[0]:
					AS_graph = self.SASGT.add_peer( AS_graph = AS_graph, AS_number = AS_numbers[x], peer = AS_numbers[y], print_debug = print_debug )
					p2p_counter += 2

		# From T2 to TN
		for current_tier in range( 1, number_of_tiers ):
			AS_numbers = tiers_dict[ current_tier ].keys()
			counter = len(AS_numbers)
			for x in range( 0, len(AS_numbers) ):
				counter -= 1
				self.P.rewrite( "\tSimulator_Random_AS_Graph_Tool: Adding p2p links for tier-" + str(current_tier+1) + ": " + str(counter) + " ASes left      " )

				if peer_probability[current_tier] != 0:
					for y in range( x + 1, len(AS_numbers) ):
						if random.uniform(0, 1) < peer_probability[current_tier]:
							AS_graph = self.SASGT.add_peer( AS_graph = AS_graph, AS_number = AS_numbers[x], peer = AS_numbers[y], print_debug = print_debug )
							p2p_counter += 2

				number_of_providers = 1
				if random.uniform(0, 1) < second_provider_probability[current_tier]:
					number_of_providers += 1

				higher_tier_AS_number = tiers_dict[current_tier-1].keys()
				random_providers = random.sample(higher_tier_AS_number, number_of_providers)

				for to_AS in random_providers:
					AS_graph = self.SASGT.add_provider( AS_graph = AS_graph, AS_number = AS_numbers[x], provider = to_AS, print_debug = print_debug )
					c2p_counter += 1

		self.P.write( "Simulator_Random_AS_Graph_Tool: generate_random_AS_graph: generated " + str(p2p_counter) + " p2p links, " + str(c2p_counter) + " c2p/p2c pairs" )
		return AS_graph

	def generate_random_trace_routes( self, AS_graph = None ):
		if AS_graph is None:
			self.P.write_error( "Simulator_Random_AS_Graph_Tool: generate_random_trace_routes: AS_graph is None" )
			return None

		self.P.write( "Simulator_Random_AS_Graph_Tool: generate_random_trace_routes: start", color = 'green' )
		self.FT.clear_folder( relative_folder_path = "trace_routes" )

		base_AS_graph = copy.deepcopy( AS_graph )
		AS_graph = copy.deepcopy( base_AS_graph )
		number_of_trace_routes = 0
		self.FT.save_text_file( data_text = str(len(AS_graph)), file_name = "number_of_ASes.txt", print_status = True )

		file_counter = 0
		counter = 0
		AS_counter = len(AS_graph)
		for AS_number in AS_graph:
			AS_counter -= 1
			counter += 1
			prefix = str(ipaddress.ip_address(int(AS_number)*256)) + "/24"
			announcement = self.SASGT.create_announcement( prefix = prefix, AS_number = AS_number, good = True )
			AS_graph = self.SASGT.insert_announcement( AS_graph = AS_graph, announcement = announcement )


			if counter > 250:
				counter = 0
				self.P.write()
				self.P.write( "Simulator_Random_AS_Graph_Tool: *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*", color = 'green' )
				self.P.write( "Simulator_Random_AS_Graph_Tool: *-* generate_random_trace_routes: " + str(AS_counter+100) + " ASes left    ", color = 'green' )
				self.P.write( "Simulator_Random_AS_Graph_Tool: *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*", color = 'green' )

				number_of_trace_routes = self.__generate_random_trace_routes( AS_graph = AS_graph, number_of_trace_routes = number_of_trace_routes, file_counter = file_counter )
				file_counter += 1
				AS_graph = copy.deepcopy( base_AS_graph )

		if counter > 0:
			number_of_trace_routes = self.__generate_random_trace_routes( AS_graph = AS_graph, number_of_trace_routes = number_of_trace_routes, file_counter = file_counter )

		counter = file_counter + 1
		for x in range( 0, file_counter + 1 ):
			counter -= 1

			trace_routes = self.FT.load_JSON_file( relative_folder_path = "trace_routes", file_name = "trace_routes_" + str(x).zfill(2) + ".json", print_status = False )

			AS_counter = len(trace_routes) 
			for AS_number in trace_routes:
				AS_counter -= 1
				self.P.rewrite( "Simulator_Random_AS_Graph_Tool: *-* generate_random_trace_routes: " + str(counter) + " files left, " + str(AS_counter) + " ASes left       " )

				AS_number_str = str(AS_number).zfill(10)
				if self.FT.check_file_exists( relative_folder_path = "trace_routes", file_name = "trace_routes_AS_" + AS_number_str + ".json") is True:
					trace_routes_AS = self.FT.load_JSON_file( relative_folder_path = "trace_routes", file_name = "trace_routes_AS_" + AS_number_str + ".json", print_status = False )
				else:
					trace_routes_AS = dict()

				for trace_route in trace_routes[ str(AS_number) ]:
					trace_route_id = self.SESTRT.get_trace_route_id( trace_route = trace_route )
					trace_routes_AS[trace_route_id] = trace_route

				
				self.FT.save_JSON_file( data_JSON = trace_routes_AS, relative_folder_path = "trace_routes", file_name = "trace_routes_AS_" + AS_number_str + ".json", print_status = False )
				trace_routes_AS = None

			trace_routes = None

	def __generate_random_trace_routes( self, AS_graph = None, number_of_trace_routes = None, file_counter = None ):
		AS_graph = self.SASGT.iterate_AS_graph( AS_graph = AS_graph )
		routing_table = self.SRTT.generate_routing_table( AS_graph = AS_graph, prefixes_do_not_overlap = True )

		trace_routes = dict()
		counter = len(routing_table)
		for AS_number in routing_table:
			counter -= 1
			self.P.rewrite( "\tSimulator_Random_AS_Graph_Tool: generate_random_trace_routes: " + str(counter) + " ASes left to process          " )
			
			if "statistics" in AS_number or "data" in AS_number:
				continue

			for prefix in routing_table[AS_number]:
				for item in routing_table[AS_number][prefix]:
					if item['used'] is True:
						path = item['path'][::-1]
						source_AS = path[0]
						source_IP = str(ipaddress.ip_address(int(source_AS)*256)) + "/24"
						dest_IP = item['prefix']

						if str(AS_number) not in trace_routes:
							trace_routes[ str(AS_number) ] = list()

						if len(path) < 2:
							continue
						
						trace_route = self.SESTRT.create_trace_route( source_IP = str(source_IP), dest_IP = str(dest_IP), path = path, epoch_time = 0 )
						trace_routes[ str(AS_number) ].append( trace_route )

		routing_table = None
		self.FT.save_JSON_file( data_JSON = trace_routes, relative_folder_path = "trace_routes", file_name = "trace_routes_" + str(file_counter).zfill(2) + ".json", print_status = True )
		
		for AS_number in trace_routes:
			number_of_trace_routes += len( trace_routes[ str(AS_number) ] )

		self.P.write( "Simulator_Random_AS_Graph_Tool: generate_random_trace_routes: generated " + str(number_of_trace_routes/1000) + "k total trace_routes" )

		trace_routes = None
		return number_of_trace_routes


			






		
		



		

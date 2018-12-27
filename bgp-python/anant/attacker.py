import sys, os, json, time, copy, requests
from os import listdir
from os.path import isfile, join

from netaddr import *

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from AS_rank_interface import AS_Rank_Interface
from RIPE_stat_interface import RIPE_Stat_Interface
from geo_interface import Geo_Interface

from printer import Printer
from time_tool import Time_Tool
from file_tool import File_Tool
from clear_screen_tool import Clear_Screen_Tool
from simulator_interface import Simulator_Interface
from ask_tool import Ask_Tool

class Simulator():
	P = None
	TT = None
	FT = None
	AT = None

	ASRI = None
	BGPVI = None
	GI = None
	SI = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer()
		self.TT = Time_Tool( P = self.P )
		self.FT = File_Tool( P = self.P, base_path = "tmp", program_name = "Simulator" )
		self.AT = Ask_Tool( P = self.P )

		self.ASRI = AS_Rank_Interface( P = self.P )
		self.RSI = RIPE_Stat_Interface( P = self.P )
		self.GI = Geo_Interface( P = self.P )
		self.SI = Simulator_Interface( P = self.P, ASRI = self.ASRI, RSI = self.RSI, GI = self.GI )
		
	def ES_links_demo( self ):
		self.P.write( "ES_links_demo: start", color = 'green' )

		# Use AS Rank data to initialise the AS_graph
		AS_graph = self.SI.init_AS_graph( use_AS_rank = True, print_debug = False )

		# Add Sibling relations from Christian
		AS_graph = self.SI.add_possible_siblings( AS_graph = AS_graph, print_debug = False )

		# Add found links in routes to AS_graph 
		time_interval = self.TT.get_time_interval( time_start_str = "2016-09-07", time_end_str = "2016-09-07 07:50:00" )
		AS_graph = self.SI.add_ES_links( AS_graph = AS_graph, RRC_number = 6, time_interval = time_interval, print_debug = False, print_server_response = False )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_links_demo_stage_1", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_1", print_status = True )

		# Create and Add BAD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "82.118.233.0/24", AS_number = 201133, good = True )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_links_demo_stage_2", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_2", print_status = True )

		# Create and Add BAD route to AS_graph
		announcement = self.SI.create_announcement( prefix = "82.118.233.0/24", AS_number = 203959, good = False )
		AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )		

		# Iterate the AS_graph until no changes are detected
		AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_links_demo_stage_3", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_3", print_status = True )

		# Calculate and Print Routing Table
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )

		# save and load routing_table to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_table)
		self.SI.save_routing_table( file_name = "ES_links_demo", routing_table = routing_table, print_status = True )
		routing_table = self.SI.load_routing_table( file_name = "ES_links_demo", print_status = True )

		# Calculate and Print routing_state
		routing_state = self.SI.generate_routing_state( routing_table = routing_table, calculate_passing_ASes = False )

		# save and load routing_state to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_state)
		self.SI.save_routing_state( file_name = "ES_links_demo", routing_state = routing_state, print_status = True )
		routing_state = self.SI.load_routing_state( file_name = "ES_links_demo", print_status = True )

		AS_graph = self.SI.load_AS_graph( file_name = "ES_links_demo_stage_3", print_status = True )
		routing_table = self.SI.load_routing_table( file_name = "ES_links_demo", print_status = True )
		routing_state = self.SI.load_routing_state( file_name = "ES_links_demo", print_status = True )

		# Print routing_table statistics
		self.SI.write_routing_table_statistics( routing_table = routing_table )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

	def ES_routes_demo( self ):
		self.P.write( "ES_routes_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph( use_AS_rank = True, print_debug = False )

		# Add Sibling relations from Christian
		AS_graph = self.SI.add_possible_siblings( AS_graph = AS_graph, print_debug = False )

		# Add found links in routes to AS_graph 
		time_interval = self.TT.get_time_interval( time_start_str = "2016-09-07", time_end_str = "2016-09-07 07:50:00" )
		AS_graph = self.SI.add_ES_links( AS_graph = AS_graph, RRC_number = 6, time_interval = time_interval, print_debug = False, print_server_response = False )

		# Load ES routes into AS_graph that are alive at 2016-09-07 00:05:00 which encapsulates 82.118.233.0/24
		AS_graph = self.SI.add_ES_routes( AS_graph = AS_graph, RRC_range = [0,21], prefix = "82.118.233.0/24", good_ASes = [ 201133 ], ignore_ASes = [ 23456 ], time_str = "2016-09-07 07:50:00" )

		# save and load AS_graph to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.AS_graph)
		self.SI.save_AS_graph( file_name = "ES_routes_demo", AS_graph = AS_graph, print_status = True )
		AS_graph = self.SI.load_AS_graph( file_name = "ES_routes_demo", print_status = True )

		# Calculate and Print routing_state
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )

		# save and load routing_state to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_state)
		self.SI.save_routing_table( file_name = "ES_routes_demo", routing_table = routing_table, print_status = True )
		self.SI.load_routing_table( file_name = "ES_routes_demo", print_status = True )

		# Generate Routing Statue
		routing_state = self.SI.generate_routing_state( routing_table = routing_table, calculate_passing_ASes = False )
		
		# save and load routing_state to disc - FILE EXTENSION ARE ADDED AUTOMATICALLY (.routing_state)
		self.SI.save_routing_state( file_name = "ES_routes_demo", routing_state = routing_state, print_status = True )
		self.SI.load_routing_state( file_name = "ES_routes_demo", print_status = True )
	
		# Draw Routing State
		self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state )

		# Print routing_table statistics
		self.SI.write_routing_table_statistics( routing_table = routing_table )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

	def insert_announcements_demo( self , graphname = 'graph_300_1539520494' , pfxfile = 'prefixassoc_300_1539520494' ):
		self.P.write( "insert_announcements_demo: start", color = 'green' )

		# Initialise empy AS_graph
		filestamp = "_".join(pfxfile.split("_")[1:])
		AS_graph = self.SI.init_AS_graph()
		dir = '/home/asemwal/raw_data/experiments/'
		file = open( dir + 'graphs/' + graphname ,'r')
		#file = open('/home/asemwal/raw_data/2018/old_proc/edgelist','r')
		
		l = str(file.readline()).strip()
		while l !='':
			if l.find("#") > -1:
				pass
			else:
				x = l.split("|")
				if str(x[2]) == 'peer-to-peer':
					AS_graph = self.SI.add_peer( AS_graph = AS_graph, AS_number =  int(x[0].split("_")[1]) , peer =  int(x[1].split("_")[1]) )
				elif str(x[2]) == 'provider-to-customer':
					AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number =  int(x[0].split("_")[1]) , customer = int(x[1].split("_")[1]) )
				elif str(x[2]) == 'customer-to-provider':
					AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number =  int(x[1].split("_")[1]) , customer = int(x[0].split("_")[1]) )
				elif str(x[2]) == 'sibling-to-sibling':
					AS_graph = self.SI.add_sibling( AS_graph = AS_graph, AS_number = int(x[0].split("_")[1]), sibling = int(x[1].split("_")[1]) )
			l = str(file.readline()).strip()

		file = open( dir + 'graphs/' + pfxfile ,'r')
		#file = open('/home/asemwal/raw_data/2018/old_proc/edgelist','r')
		prefixassociation = dict()
		l = str(file.readline()).strip()
		while l !='':
			if l.find("#") > -1:
				pass
			else:
				x = l.split("|")
				i = x[0]
				y = x[1].split(",")
				for j in y:
					try:
						prefixassociation[j.split("_")[1]].append(i)
					except KeyError:
						prefixassociation[j.split("_")[1]] = [i]

			l = str(file.readline()).strip()
				
#		# Add forwarding rule
#		AS_graph = self.SI.add_forwarding_rule( AS_graph = AS_graph, AS_number = 1, from_type = self.SI.get_P2P_type(), to_type = self.SI.get_C2P_type(), allow = True )

		# Save / Load AS Graph
		self.SI.save_AS_graph( AS_graph = AS_graph, file_name = "insert_announcements_demo"+"_"+ filestamp, print_status = True )
           
		#AS_Graph = self.SI.load_AS_graph( file_name = "insert_announcements_demo", print_status = True )
		# Create and Add GOOD route to AS_graph
		for i in prefixassociation.keys():
			for j in prefixassociation[i]:
				self.P.write(j)

				announcement = self.SI.create_announcement( prefix = j, AS_number = i, good = True )
				AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

				# Iterate the AS_graph until no changes are detected
				AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )
		
		self.SI.save_AS_graph( AS_graph = AS_graph, file_name = "insert_announcements_demo"+"_"+ filestamp, print_status = True )
        
		# Create and Add BAD route to AS_graph
		#announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 44, good = False )
		#AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		#AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# Print AS_graph
		#self.P.write_JSON( AS_graph )

		# Calculate and Print unique path found
		#unique_paths = self.SI.get_unique_paths( AS_graph = AS_graph )
		self.P.write( "Simulator: custom_demo: unique paths:")
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph,  prefixes_do_not_overlap = True )
		self.SI.save_routing_table( routing_table = routing_table, file_name = "insert_announcements_demo"+"_"+ filestamp, print_status = True )
		routing_state = self.SI.generate_routing_state( routing_table = routing_table )
		self.SI.save_routing_state( file_name = "insert_announcements_demo"+"_"+ filestamp, routing_state = routing_state, print_status = True )
		
		

	def insert_announcements_demo2( self ,   graphname = 'graph_60000_1539450306', filestamp = ''  ):
		self.P.write( "insert_announcements_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link
		#file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
		dir = '/home/asemwal/raw_data/experiments/'
		
		# Save / Load AS Graph
		AS_graph = self.SI.load_AS_graph( file_name = filestamp, print_status = True )
		routing_table = self.SI.load_routing_table( file_name = filestamp, print_status = True )
		file = open( dir + 'graphs/monitors_' + graphname ,'r')
		peerlist = list()
		#file = open('/home/asemwal/raw_data/2018/old_proc/edgelist','r')
		l = str(file.readline()).strip()
		while l != '':
			if l.find("is_monset") > -1:
				mon = l.split(":")[1].split(",")
				for j in mon:
					peerlist.append(int(j.split("_")[1]))
				break
			l = str(file.readline()).strip()
		file.close()
		prefixassociation = dict()
		for i in routing_table['statistics'].keys():
			#print i
			prefixassociation.update({i:[]})
			for j in routing_table['statistics'][i]:
				#print j
				if j.find("AS") > -1:
					prefixassociation[i].append(j.split("S")[1])
		   
		#AS_Graph = self.SI.load_AS_graph( file_name = "insert_announcements_demo", print_status = True )
		# Create and Add GOOD route to AS_graph


		# Create and Add BAD route to AS_graph
		#announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 44, good = False )
		#AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

		# Iterate the AS_graph until no changes are detected
		#AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

		# Print AS_graph
		#self.P.write_JSON( AS_graph )

		# Calculate and Print unique path found
		#unique_paths = self.SI.get_unique_paths( AS_graph = AS_graph )
		self.P.write( "Simulator: custom_demo: unique paths:")
		#self.P.write_JSON( unique_paths )

		# Calculate and Print Routing Table
		#routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
		#self.P.write( "Simulator: custom_demo: routing table:")
		#self.P.write_JSON( routing_table["6939"] )
		#peerlist = "38726,18106,24482,38883,293,3277,14061,63956,6082,1916,58511,39351,4826,28917,25152,19151,1351,9304,4739,7575,28634,38880,53070,34288,20912,28571,15301,52720,20080,42541,6667,15547,1280,2914,41722,15605,59891,38809,1798,9002,41497,29140,41695,16735,2497,23367,47692,262757,24516,6939,10026,25220,52873,23106,12637,6762,53828,20764,53767,25091,13030,40191,37497,852,49788,48526,2518,52863,3491,54728,50877,49605,39122,6830,31019,37353,1403,29686,680,19653,19754,28329,5413,15435,3257,553,4181,8426,209,37100,37468,264268,204028,8455,37271,3741,22652,41811,46450,4589,30844,286,47147,57866,32212,701,7018,59469,63927,3356,5396,8283,5645,40387,59715,53013,14361,1299,23673,36351,3267,52888,52871,13760,2895,51185,5392,6453,45177,3252,39821,45352,11686,27678,32709,17639,37474,25227,14537,13237,2152,8492,6423,206479,25933,262354,29479,41095,48285,327960,263584,3303,52940,1221,3292,5650,3561,28220,8222,32354,53364,7500,27446,1239,3549,3130,36236,24441,15008,19016,7660,57111,5769,12779,29680,57463,58901,34224,53067,263508,263075,262317,264911,263152,9902,35699,43578,202032,513,38001,13004,2613,12307,6539,37239,263945,26162,14840,4777,1103,59414,45896,32653,6720,20932,2516,2857,8268,28929,8758,328145,10102,31424,63055,2905,12859,35369,196621,3333,50763,29075,263047,49463,8607,8218,56730,16347,50300,31742,59689,25160,15562,58299,198385,20612,50304,64050,198249,35054,8896,6881,29222,12350,1836,29608,64463,29691,51405,29504,57821,21232,30132,34177,4608,202194,58308,198290,57381,2500,22548,263651,4558,37578,34019,11666,20562,37640,11039,24115,5511,6079,37989,328206,20495,1273,2018,8928,4637,11537,19782,58682,31122,29636,8359,12956,263702,7606,50620,33891,37680,327995,8220,50384,37105,9505,31500,35320,31133,21320,43100,8966,8447,6730,9266,2854,12713,31042,42708,33132,21385,8529,28283,59318,17451,6774,2603,53237,12989,8560,134708,37662,5056,5588,9583,29838,13101,8331,4780,8470,10310,5400,9268,9063,32787,63516,1853,8708,30733,60169,32098,27257,15600,6866,9264,8365,38182,59605,1668,32869,39912,3327,136168,2116,10474,8075,2686,22691,49835,28300,21156,327984,2856,49544,8319,11403,8551,42,16086,21263,3301,26744,22822,6067,8781,203201,15830,5430,6805,21013,24753,2044,8816,15699,45494,16030,37053,15695,262868,20940,16637,32934,58436,714,53240,12306,559,29449,20704,60171,16265,33764,8674,3856,16700,262427,7795,13285,24592,19551,9026,25061,4844,37685,8648,13727,45634,34347,15133,13041,12605,12414,20507,7363,29590,39651,8422,10848,262612,9318,28589,6968,34309,65000,62275,31680,25182,6656,6798,57118,26415,6083,8342,23131,24905,38930,48166,64396,25310,20747,327813,24880,50292,20953,63949,21336,49375,8468,251,29053,31715,31800,15879,15469,5552,13184,134363,28303,49065,44160,8851,8596,30892,28941,28760,263674,4788,264144,24875,327991,11995,6679,41039,16570,2848,34790,264016,37515,12355,60458,28624,54104,24793,12401,8224,5385,21911,44030,8330,21473,29049,52342,20640,29611,12399,25478,264552,47441,20920,15598,25435,28138,5403,12008,24931,12635,12634,14633,34305,16004,8591,14026,41617,29550,47872,39591,6850,13703,30914,12333,25560,31383,8442,20718,9104,15703,15479,5524,35829,17697,33843,328220,28878,13105,48147,36968,8763,41445,34781,42473,8419,12902,30653,34146,61673".split(",")
		
		# Save / Load Routing Table
		#l=""
		#for peer in peerlist:
		#	if peer in routing_table.keys():
		#		l = l+ str(peer)+"|"+str(len(routing_table[str(peer)]['192.168.0.0/24']))+"\n"
		#	else:
		#		l = l+ str(peer)+"|KeyError\n" 
		#self.P.write(l)
		self.P.write("Number of Nodes:"+ str(len(AS_graph.keys()) ))
		#file = open('/home/asemwal/thesis/bgp-python_safe/data/simulator/myrun/as_graph','w')
		#file.write(str(AS_Graph.keys()))
		#file.flush()
		#file.close()
		for p in prefixassociation.keys():
			process = AS_graph.keys()
			for q in prefixassociation[p]:
				process.remove(q)
			for i in process:
				AS_graph = self.SI.load_AS_graph( file_name =  filestamp , print_status = True )
				self.P.write("Number of Nodes:"+ str(len(AS_graph.keys()) ))
				# Create and Add GOOD route to AS_graph
				announcement = self.SI.create_announcement( prefix =  p , AS_number = i, good = False )
				AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

				# Iterate the AS_graph until no changes are detected
				
				# Create and Add BAD route to AS_graph
				#announcement = self.SI.create_announcement( prefix = "192.168.0.0/24", AS_number = 44, good = False )
				#AS_graph = self.SI.insert_announcement( AS_graph = AS_graph, announcement = announcement )

				# Iterate the AS_graph until no changes are detected
				AS_graph = self.SI.iterate_AS_graph( AS_graph = AS_graph )

				# Print AS_graph
				#self.P.write_JSON( AS_graph )

				# Calculate and Print unique path found
				#unique_paths = self.SI.get_unique_paths( AS_graph = AS_graph )
				#self.P.write( "Simulator: custom_demo: unique paths:")
				#self.P.write_JSON( unique_paths )

				# Calculate and Print Routing Table
				routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
				#self.P.write( "Simulator: custom_demo: routing table:")
				#self.P.write_JSON( routing_table["6939"] )
				#peerlist = "38726,18106,24482,38883,293,3277,14061,63956,6082,1916,58511,39351,4826,28917,25152,19151,1351,9304,4739,7575,28634,38880,53070,34288,20912,28571,15301,52720,20080,42541,6667,15547,1280,2914,41722,15605,59891,38809,1798,9002,41497,29140,41695,16735,2497,23367,47692,262757,24516,6939,10026,25220,52873,23106,12637,6762,53828,20764,53767,25091,13030,40191,37497,852,49788,48526,2518,52863,3491,54728,50877,49605,39122,6830,31019,37353,1403,29686,680,19653,19754,28329,5413,15435,3257,553,4181,8426,209,37100,37468,264268,204028,8455,37271,3741,22652,41811,46450,4589,30844,286,47147,57866,32212,701,7018,59469,63927,3356,5396,8283,5645,40387,59715,53013,14361,1299,23673,36351,3267,52888,52871,13760,2895,51185,5392,6453,45177,3252,39821,45352,11686,27678,32709,17639,37474,25227,14537,13237,2152,8492,6423,206479,25933,262354,29479,41095,48285,327960,263584,3303,52940,1221,3292,5650,3561,28220,8222,32354,53364,7500,27446,1239,3549,3130,36236,24441,15008,19016,7660,57111,5769,12779,29680,57463,58901,34224,53067,263508,263075,262317,264911,263152,9902,35699,43578,202032,513,38001,13004,2613,12307,6539,37239,263945,26162,14840,4777,1103,59414,45896,32653,6720,20932,2516,2857,8268,28929,8758,328145,10102,31424,63055,2905,12859,35369,196621,3333,50763,29075,263047,49463,8607,8218,56730,16347,50300,31742,59689,25160,15562,58299,198385,20612,50304,64050,198249,35054,8896,6881,29222,12350,1836,29608,64463,29691,51405,29504,57821,21232,30132,34177,4608,202194,58308,198290,57381,2500,22548,263651,4558,37578,34019,11666,20562,37640,11039,24115,5511,6079,37989,328206,20495,1273,2018,8928,4637,11537,19782,58682,31122,29636,8359,12956,263702,7606,50620,33891,37680,327995,8220,50384,37105,9505,31500,35320,31133,21320,43100,8966,8447,6730,9266,2854,12713,31042,42708,33132,21385,8529,28283,59318,17451,6774,2603,53237,12989,8560,134708,37662,5056,5588,9583,29838,13101,8331,4780,8470,10310,5400,9268,9063,32787,63516,1853,8708,30733,60169,32098,27257,15600,6866,9264,8365,38182,59605,1668,32869,39912,3327,136168,2116,10474,8075,2686,22691,49835,28300,21156,327984,2856,49544,8319,11403,8551,42,16086,21263,3301,26744,22822,6067,8781,203201,15830,5430,6805,21013,24753,2044,8816,15699,45494,16030,37053,15695,262868,20940,16637,32934,58436,714,53240,12306,559,29449,20704,60171,16265,33764,8674,3856,16700,262427,7795,13285,24592,19551,9026,25061,4844,37685,8648,13727,45634,34347,15133,13041,12605,12414,20507,7363,29590,39651,8422,10848,262612,9318,28589,6968,34309,65000,62275,31680,25182,6656,6798,57118,26415,6083,8342,23131,24905,38930,48166,64396,25310,20747,327813,24880,50292,20953,63949,21336,49375,8468,251,29053,31715,31800,15879,15469,5552,13184,134363,28303,49065,44160,8851,8596,30892,28941,28760,263674,4788,264144,24875,327991,11995,6679,41039,16570,2848,34790,264016,37515,12355,60458,28624,54104,24793,12401,8224,5385,21911,44030,8330,21473,29049,52342,20640,29611,12399,25478,264552,47441,20920,15598,25435,28138,5403,12008,24931,12635,12634,14633,34305,16004,8591,14026,41617,29550,47872,39591,6850,13703,30914,12333,25560,31383,8442,20718,9104,15703,15479,5524,35829,17697,33843,328220,28878,13105,48147,36968,8763,41445,34781,42473,8419,12902,30653,34146,61673".split(",")
				# Save / Load Routing Table
				#self.P.write(routing_table["10"])
				#self.SI.save_routing_table( routing_table = routing_table, file_name = "insert_announcements_demo"+i, print_status = True )
				routing_state = self.SI.generate_routing_state( routing_table = routing_table )
		
				# Save / Load Routing State
				#self.SI.save_routing_state( file_name = "insert_announcements_demo"+i, routing_state = routing_state, print_status = True )
				#routing_state = self.SI.load_routing_state( file_name = "insert_announcements_demo"+i, print_status = True )

				self.SI.write_routing_state_statistics( routing_state = routing_state )
				badcount = 0 
				#h="H|V|A|O"
				l=  graphname +"|" +str(",".join(prefixassociation[p]))+"|"+str(i) +"|"
				for peer in peerlist:
					used0 = False;
					used1 = False;
					good = False
					bad = False
					code = 'N'
					for j in range(0, len(routing_table[str(peer)][p])):
						if routing_table[str(peer)][p][j]['used'] == True :
							used0 = True
							if routing_table[str(peer)][p][0]['good'] == True:
								good = True
							else:
								bad = True
					if good == True and bad == False:
						code='G'
					elif good == False and bad == True:
						badcount +=1
					elif good == True and bad == True:
						code= 'C'
					else:
						code = 'N'


					
				file = open( dir + 'attackervictimanalysis.txt','a')
				l += str(badcount)+"/"+ str(len(peerlist))+"\n"
				file.write(l)
				file.flush()
				file.close()


		self.SI.save_routing_table( routing_table = routing_table, file_name = filestamp + '2', print_status = True )
		routing_table = self.SI.load_routing_table( file_name =  filestamp + '2', print_status = True )

		# Calculate and Print routing_state
		routing_state = self.SI.generate_routing_state( routing_table = routing_table )
		
		# Save / Load Routing State
		self.SI.save_routing_state( file_name =  filestamp + '2', routing_state = routing_state, print_status = True )
		routing_state = self.SI.load_routing_state( file_name =  filestamp + '2', print_status = True )


		self.P.write( "Simulator: custom_demo: routing_state:")
		self.P.write_JSON( routing_state )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

		# Draw AS_graph State
		#self.SI.draw_AS_graph( AS_graph = AS_graph, file_name = "insert_announcements_demoasda" )

		# Draw Routing State
		#self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, draw_unused_links = True, file_name = "insert_announcements_demo" )

		#self.SI.compare_routing_states( routing_state_1 = routing_state, routing_state_2 = routing_state )

	def insert_routes_demo( self ):
		self.P.write( "insert_routes_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link

		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 1, customer = 2 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 2, customer = 3 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 3, customer = 4 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 4, customer = 5 )

		# create route
		route = dict()
		route['prefix'] = "192.168.2.0/24"
		route['path'] = [ 2, 3, 3, 3, 4, 4, 5 ]
		route['source_AS'] = 2

		# insert route
		AS_graph = self.SI.insert_route( AS_graph = AS_graph, route = route, good = True )

		# create route
		route2 = dict()
		route2['prefix'] = "192.168.2.0/20"
		route2['path'] = [ 1, 2, 3, 4, 4, 5 ]
		route2['source_AS'] = 1

		# insert route
		AS_graph = self.SI.insert_route( AS_graph = AS_graph, route = route2, good = False )

		# Print AS Graph
		self.P.write( "Simulator: insert_routes_demo: AS Graph:")
		self.P.write_JSON( AS_graph )

		# Calculate and Print unique path found
		unique_paths = self.SI.get_unique_paths( AS_graph = AS_graph )
		self.P.write( "Simulator: insert_routes_demo: unique paths:")
		self.P.write_JSON( unique_paths )

		# Calculate and Print Routing Table
		routing_table = self.SI.generate_routing_table( AS_graph = AS_graph )
		self.P.write( "Simulator: insert_routes_demo: routing_table:")
		self.P.write_JSON( routing_table )

		# Calculate and Print routing_state
		routing_state = self.SI.generate_routing_state( routing_table = routing_table )
		self.P.write( "Simulator: insert_routes_demo: routing_state:")
		self.P.write_JSON( routing_state )

		# Print routing_state statistics
		self.SI.write_routing_state_statistics( routing_state = routing_state )

		# Draw AS_graph State
		self.SI.draw_AS_graph( AS_graph = AS_graph, file_name = "AS_graph" )

		# Draw Routing State
		self.SI.draw_routing_state( AS_graph = AS_graph, routing_table = routing_table, routing_state = routing_state, draw_unused_links = True )

	def type_prediction_demo( self ):
		self.P.write( "type_prediction_demo: start", color = 'green' )

		#TODO
		return

	def graph_validation_connectivity_demo( self ):
		self.P.write( "graph_validation_connectivity_demo: start", color = 'green' )

		# Initialise empy AS_graph
		AS_graph = self.SI.init_AS_graph()

		# add p2p, c2p and p2c links to the AS_graph
		# also creates the reversed link
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 1, customer = 2 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 2, customer = 3 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 3, customer = 4 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 4, customer = 5 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 12, customer = 11 )
		AS_graph = self.SI.add_customer( AS_graph = AS_graph, AS_number = 11, customer = 3 )

		self.SI.validate_connectivity( AS_graph = AS_graph, AS_number = 1, print_debug = True )

		return

	def graph_create_legend_demo( self ):
		self.P.write( "graph_create_legend_demo: start", color = 'green' )
		self.SI.create_legend()
		return

	def load_save_relations_demo( self ):
		self.P.write( "load_save_relations_demo: start", color = 'green' )

		# -----
		# Simulator_ES_Relations_Tool serves as an interface between YOU and ElasticSeach index bgp-relations.
		# With flush() you send your local changes to ElasticSeach index bgp-relations
		# flush() is called internally every X updates. 
		# See simulation_interface.py: You can use the following arguments:
		#	print_server_response - print ES server response
		#	print_debug			  - print Simulator_ES_Relations_Tool debug information
		#	overwrite			  - overwrite existing entries (default = False)
		#	create 				  - add a new relation when True and relation does not yet exists (default = True)
		# An relation consists of:
		# 	from_AS
		# 	to_AS
		# 	source 				- where was the link found
		# 	type 					- [P2P, C2P, P2C, S2S, UNKOWN] = [0, 1, 2, 3, -1]
		# 	p2p 					- when the type switch to p2p 	
		# 	p2c					- when the type switch to p2c 
		# 	c2p 					- when the type switch to c2p 
		# 	s2s 					- when the type switch to s2s 
		# 	trace_route_ids 		- list of trace_route_ids asociated with it
		# -----

		# Reset ElasticSeach index bgp-relations 
		self.SI.delete_relations_index()
		self.SI.create_relations_index()

		# Add AS Rank data
		self.SI.add_AS_rank_relations( overwrite = True )

		# sync ElasticSeach index bgp-relations locally for faster processing 
		self.SI.sync_ES_relations()								# For all ASes

		# save and load LOCAL data
		self.SI.save_ES_relations( file_name = "test" )
		self.SI.load_ES_relations( file_name = "test" )

		# Add relation [USING dict()]
		relation = dict()
		relation['from_AS'] = 999
		relation['to_AS'] = 1000
		relation['type'] = self.SI.get_P2P_type()
		relation['source'] = 0 
		relation_id = self.SI.add_ES_relation( relation = relation, print_debug = True )

		# Add relation [USING arguments]
		relation_id = self.SI.add_ES_relation( from_AS = 999, to_AS = 1000, type = self.SI.get_P2P_type(), source = 1, overwrite = True, print_debug = True )

		# Retrieve relation [USING from_AS, to_AS]
		#relation = self.SI.get_ES_relation( from_AS = 286, to_AS = 1136, print_debug = True )
		#self.P.write_JSON( relation )

		# Retrieve relation [USING relation_id]
		relation = self.SI.get_ES_relation( relation_id = relation_id, print_debug = True )
		self.P.write_JSON( relation )

		# Send changed data to ES
		self.SI.flush_ES_relations()

	def load_save_trace_routes_demo( self ):
		self.P.write( "load_save_relations_demo: start", color = 'green' )

		# -----
		# Simulator_ES_Trace_Routes_Tool serves as an interface between YOU and ElasticSeach index bgp-trace-routes.
		# With flush() you send your local changes to ElasticSeach index bgp-trace-routes
		# flush() is called internally every X updates. 
		# See simulation_interface.py: You can use the following arguments:
		#	print_server_response - print ES server response
		#	print_debug			  - print Simulator_ES_Trace_Routes_Tool debug information
		# An traceroute consists of:
		# 	source_IP 		- for example: 192.168.2.1
		# 	dest_IP 		- for example: 133.168.2.1
		# 	path 			- for example: [AS1, AS2, ..., ASX ]
		# 	epoch time 		- when the traceroute was performed
		# 	relation_ids  	- list of relation_ids asociated with it
		# -----

		# Reset ElasticSeach index bgp-trace-routes 
		self.SI.delete_trace_routes_index()
		self.SI.create_trace_routes_index()

		# sync ElasticSeach index bgp-relations locally for faster processing 
		self.SI.sync_ES_trace_routes()							

		# save and load LOCAL data
		self.SI.save_ES_trace_routes( file_name = "test" )
		self.SI.load_ES_trace_routes( file_name = "test" )

		# Add traceroute METHOD 1
		trace_route = dict()
		trace_route['source_IP'] = "192.168.2.1"
		trace_route['dest_IP'] = "133.168.2.1"
		trace_route['path'] = [ 2, 4, 6, 8 ]
		trace_route['epoch_time'] = 3423423423
		trace_route_id = self.SI.add_ES_trace_route( trace_route = trace_route, print_debug = True )

		# Add traceroute METHOD 2
		trace_route_id = self.SI.add_ES_trace_route( source_IP = "127.127.127.0", dest_IP = "133.168.2.1", path = [ 2, 4, 6, 8 ], epoch_time = 3423423423, print_debug = True )
		
		# Get and Print trace_route
		trace_route = self.SI.get_ES_trace_route( trace_route_id = trace_route_id )
		self.P.write_JSON( trace_route )

		# Flush
		self.SI.flush_ES_trace_routes()

	def improver_missing_relatations_demo( self ):
		# Download ElasticSearch index bgp-relations locally
		#self.SI.sync_ES_relations( overwrite = True )

		#Save all relations in Simulator_ES_Relations_Tool to a file - FILE EXTENSION ARE ADDED AUTOMATICALLY (.relations)
		#self.SI.save_ES_relations( file_name = "demo")

		#Load known relations from file to Simulator_Relation_Type_Improver_Tool - FILE EXTENSION ARE ADDED AUTOMATICALLY (.relations)
		self.SI.load_improver_relations( file_name = "demo" )

		mode = None

		if mode == 1:			# Compute missing relations using locally stored trace routes
			trace_route = self.SI.create_trace_route( path = [99, 100, 101, 102], source_IP = "0.0.0.0", dest_IP = "1.1.1.1", epoch_time = 2222 )
			self.SI.add_improver_trace_route( trace_route = trace_route, print_debug = True )
			self.SI.compute_missing_relations( mode = "local", print_debug = True )
		elif mode == 2:			# Compute missing relations using relations found in ElasticSearch index bgp-trouce-routes
			self.SI.compute_missing_relations( mode = "ES", print_debug = False )
		elif mode == 3:			# Compute missing relations using relations found in an external CSV File
			self.SI.compute_missing_relations( mode = "CSV", file_name = "traceroutes_asn.csv", print_debug = False )
		else:					# Choose for menu
			self.SI.compute_missing_relations()
		
		#Save all missing relations in Simulator_Relation_Type_Improver_Tool to a file - FILE EXTENSION ARE ADDED AUTOMATICALLY (.missing_relation)
		self.SI.save_improver_missing_relations( file_name = "demo" )

	def improver_predicting_relatations_demo( self ):
		self.SI.load_improver_relations( file_name = "demo" )
		self.SI.load_improver_missing_relations( file_name = "demo" )

		self.SI.predict_missing_relations( print_debug = False )

	def improver_rectify_relatations_demo( self ):
		self.SI.load_improver_relations( file_name = "demo" )
		self.SI.rectify_relations( minimum_trace_routes = 1000, print_debug = False, print_server_response = False )

	def run( self ):
		self.P.write( "Simulator Demos: run: has multiple modes:", color = 'green' ) 
		self.P.write( "\t(1)  - ES links" ) 
		self.P.write( "\t(2)  - ES routes" ) 
		self.P.write( "\t(3)  - announcements" ) 
		self.P.write( "\t(4)  - routes" ) 
		self.P.write( "\t(5)  - type prediction" ) 
		self.P.write( "\t(6)  - graph validation" ) 
		self.P.write( "\t(7)  - create legend" ) 
		self.P.write( "\t(8)  - load / save relations" ) 
		self.P.write( "\t(9)  - load / save trace routes" ) 
		self.P.write( "\t(10) - relation improver - missing relations" ) 
		self.P.write( "\t(11) - relation improver - predicting relations" )
		self.P.write( "\t(12) - relation improver - rectify relations" )  

		#mode = self.AT.ask( question = "Select mode (1/2/3/4/5/6/7/8/9/10/11/12):", expect_list = range( 1, 12 + 1 ) )
		mode = '3'
		if mode == "1":
			self.ES_links_demo()
		elif "2" in mode:
			self.ES_routes_demo()
		elif "3" in mode:
			mypath ='/home/asemwal/git/bgp-python/data/simulator/done/'
			onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.find("AS_graph") > -1]
			for f in onlyfiles:
				print f
			onlyfiles = ['insert_announcements_demo_300_1540809507.AS_graph']
			for f in onlyfiles:
				filestamp = "done/"+f.split(".")[0]
				graphname = "_".join(f.split(".")[0].split("_")[3:])
				self.insert_announcements_demo2( graphname = graphname , filestamp = filestamp )
				#os.rename(mypath+f , mypath+"completed/"+f)
				#os.rename(mypath+filestamp +'.routing_state' , mypath+"completed/"+filestamp +'.routing_state')
				#os.rename(mypath+filestamp +'.routing_table' , mypath+"completed/"+filestamp +'.routing_table')


		elif "4" in mode:
			self.insert_routes_demo()
		elif "5" in mode:
			self.type_prediction_demo()
		elif "6" in mode:
			self.graph_validation_demo()
		elif "7" in mode:
			self.graph_create_legend_demo()
		elif "8" in mode:
			self.load_save_relations_demo()
		elif "9" in mode:
			self.load_save_trace_routes_demo()
		elif "10" in mode:
			self.improver_missing_relatations_demo()
		elif "11" in mode:
			self.improver_predicting_relatations_demo()
		elif "12" in mode:
			self.improver_rectify_relatations_demo()

Simulator().run()







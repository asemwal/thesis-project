import json, requests, os, sys, functools

import graphviz as gv

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool

class Simulator_Graph_Draw_Tool():
	P = None
	FT = None
	graph = None
	print_debug = False
	
	processed_edges = None
	used_ASes = None 

	def __init__( self, P = None, FT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Graph_Draw_Tool : __init__ : P is None" )

		self.P.write( "Simulator_Graph_Draw_Tool: Loading...", color = 'cyan' )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_Graph_Draw_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Graph_Draw_Tool" )

		self.reset()

	def __set_graph( self, graph_type = None ):
		if graph_type is not None:
			if "basic" in graph_type:
				self.graph = gv.Graph(format='png')
			elif "directed" in graph_type:
				self.graph = gv.Digraph(format='png')
		else:
			self.graph = gv.Graph(format='png')

	def reset( self ):
		self.processed_edges = dict()
		self.__set_graph( graph_type = "directed" )
		self.used_ASes = dict()
		return

	def add_node( self, node_name = None, node_type = "default" ):
		if node_name not in self.used_ASes:
			self.used_ASes[node_name] = None

		if "good" in node_type:
			self.graph.node( str(node_name), shape = "oval", color = 'green' )
		elif "contested" in node_type:
			self.graph.node( str(node_name), shape = "diamond", color = 'black' )
		elif "bad" in node_type:
			self.graph.node( str(node_name), shape = "hexagon", color = 'red' )
		elif "no_routing" in node_type:
			self.graph.node( str(node_name), shape = "box", color = 'blue' )
		elif "default" in node_type:
			self.graph.node( str(node_name), shape = "oval", color = 'black' )
		else:
			self.P.write_error( "good, contested, bad or default not in node_type" )

	def add_edge( self, from_node_name = None, from_node_type = "default", to_node_name = None, to_node_type = "default", edge_color = "not_present", edge_style = "solid", label = None, dir = None ):
		if "not_present" in edge_color:
			return

		if str(from_node_name) == str(to_node_name):
			return
		
		if label is not None:
			label = str(label)

		_id = str(from_node_name) + str(to_node_name) + str(label) 

		if _id not in self.processed_edges:
			self.processed_edges[ str(to_node_name) + str(from_node_name) + str(label) ] = None
			self.processed_edges[ str(from_node_name) + str(to_node_name) + str(label) ] = None

			self.add_node( node_name = from_node_name, node_type = from_node_type )
			self.add_node( node_name = to_node_name, node_type = to_node_type )

			if label is not None:
				label = "  " + str(label)

			penwidth = None
			if "bold" in edge_style:
				penwidth = "2.5"
			elif "dotted" in edge_style:
				penwidth = "1.5"

			self.graph.edge( str(from_node_name), str(to_node_name), color = edge_color, label = label, style = edge_style, penwidth = penwidth, dir = dir )

	def draw_graph( self, relative_folder_path = "", file_name = None ):
		if self.graph is None:
			self.P.write_error( "Simulation_Graph_Draw_Tool : draw_graph : self.graph is None" )
			return

		self.P.write( "Simulator_Graph_Draw_Tool : draw_graph: start (found " + str(len(self.used_ASes)) + " ASes)", color = 'green' )

		if file_name is not None:
			file_name = str(relative_folder_path) + str(file_name)
			file_name = file_name.split(".")[0] 
		else:
			file_name = str(relative_folder_path) + "temp"

		file_path = self.FT.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )
		file_path = self.graph.render( filename = file_path )
		self.FT.remove_file( relative_folder_path = relative_folder_path, file_path = file_path.replace(".png","") )

		self.P.write( "Simulator_Graph_Draw_Tool : created file " + str(file_path), color = 'blue' )



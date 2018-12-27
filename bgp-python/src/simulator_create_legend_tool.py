import json, requests, os, sys, hashlib, copy, time, math

import graphviz as gv

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from file_tool import File_Tool

from simulator_link_types import Simulator_Link_Types

class Simulator_Create_Legend_Tool():
	P = None
	FT = None
	SLT = None

	TYPE_P2P = None
	TYPE_C2P = None
	TYPE_P2C = None
	TYPE_S2S = None

	graph = None

	def __init__( self, P = None, FT = None, SLT = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Simulator_Create_Legend_Tool: __init__: P is None" )

		self.P.write( "Simulator_Create_Legend_Tool: Loading...", color = 'cyan' )

		if FT is not None:
			self.FT = FT
		else:
			self.P.write_warning( "Simulator_Create_Legend_Tool: __init__ : FT is None" )
			self.FT = File_Tool( P = self.P, base_path = "data/simulator", program_name = "Simulator_Create_Legend_Tool" )

		if SLT is not None:
			self.SLT = SLT
		else:
			self.P.write_warning( "Simulator_Create_Legend_Tool: __init__: SLT is None" )
			self.SLT = Simulator_Link_Types( P = self.P )

		self.TYPE_P2P = self.SLT.get_P2P_type()
		self.TYPE_C2P = self.SLT.get_C2P_type()
		self.TYPE_P2C = self.SLT.get_P2C_type()
		self.TYPE_S2S = self.SLT.get_S2S_type()

	def __reset( self ):
		self.graph = gv.Digraph(format='png')

	def create_legend( self, relative_folder_path = "" ):
		self.__reset()
		self.__add_nodes()
		self.__draw_legend( relative_folder_path = relative_folder_path, file_name = "legend_nodes" )

		self.__reset()
		self.__add_AS_relations()
		self.__draw_legend( relative_folder_path = relative_folder_path, file_name = "legend_relations" )

		self.__reset()
		self.__add_egde_type()
		self.__draw_legend( relative_folder_path = relative_folder_path, file_name = "legend_edges" )

	def __add_nodes( self ):
		self.graph.node( "GOOD", shape = "oval", color = 'green' )
		self.graph.node( "CONTESTED", shape = "diamond", color = 'black' )
		self.graph.node( "BAD", shape = "hexagon", color = 'red' )
		self.graph.node( "NO_ROUTING", shape = "box", color = 'blue' )

	def __add_AS_relations( self ):
		self.graph.node( "AS1", shape = "oval", color = 'black' )
		self.graph.node( "AS2", shape = "oval", color = 'black' )
		self.graph.edge( "AS1", "AS2", color = "black", label = " p2p", style = "solid", penwidth = None, dir = "both" )

		self.graph.node( "AS3", shape = "oval", color = 'black' )
		self.graph.node( "AS4", shape = "oval", color = 'black' )
		self.graph.edge( "AS3", "AS4", color = "black", label = " s2s", style = "dotted", penwidth = "2", dir = "both" )

		self.graph.node( "AS5", shape = "oval", color = 'black' )
		self.graph.node( "AS6", shape = "oval", color = 'black' )
		self.graph.edge( "AS6", "AS5", color = "black", label = " p2c", style = "dashed" )

		self.graph.node( "AS7", shape = "oval", color = 'black' )
		self.graph.node( "AS8", shape = "oval", color = 'black' )
		self.graph.edge( "AS7", "AS8", color = "black", label = " c2p ", style = "bold", penwidth = "2.5" )

	def __add_egde_type( self ):
		self.graph.node( "AS1", shape = "oval", color = 'black' )
		self.graph.node( "AS2", shape = "oval", color = 'black' )
		self.graph.edge( "AS1", "AS2", color = "green", label = " GOOD", style = "solid", penwidth = None )

		self.graph.node( "AS3", shape = "oval", color = 'black' )
		self.graph.node( "AS4", shape = "oval", color = 'black' )
		self.graph.edge( "AS3", "AS4", color = "red", label = " BAD", style = "solid", penwidth = None )

		self.graph.node( "AS5", shape = "oval", color = 'black' )
		self.graph.node( "AS6", shape = "oval", color = 'black' )
		self.graph.edge( "AS5", "AS6", color = "blue", label = " NOT USED", style = "solid", penwidth = None )

	def __draw_legend( self, relative_folder_path = "", file_name = None ):
		if file_name is not None:
			file_name = str(relative_folder_path) + str(file_name)
			file_name = file_name.split(".")[0] 
		else:
			file_name = str(relative_folder_path) + "legend"

		file_path = self.FT.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )
		file_name = self.graph.render( filename = file_path )

		self.P.write( "\tSimulator_Create_Legend_Tool : __draw_legend: created file " + str(file_name), color = 'blue' )
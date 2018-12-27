import sys, os, netaddr
from netaddr import *

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from clear_screen_tool import Clear_Screen_Tool
from printer import Printer
from BGP_view_interface import BGP_View_Interface
from coordinate_interface import Coordinate_Interface

class Coordinates():
	P = None
	CI = None
	BGPVI = None

	def __init__( self ):
		self.CST = Clear_Screen_Tool()
		self.CST.clear_screen()

		#Tool to print output
		self.P = Printer()

		self.CI = Coordinate_Interface( P = self.P )
		self.BGPVI = BGP_View_Interface( P = self.P )

	def run( self ):
		AS_number = 286
		IP4_prefixes = self.BGPVI.get_IP4_prefixes( AS_number = AS_number )

		# Convert IP4 prefixes to coordinates
		coordinates = list()
		for IP4_prefix in IP4_prefixes:
			coordinates.append( self.CI.get_coordinate( IP4_prefix = IP4_prefix ) )

		# Print found coordinates
		self.P.write( "-- Before --", color = 'green' )

		self.P.write_JSON( data_JSON = coordinates )
		for coordinate in coordinates:
			self.P.write( coordinate, include_time_stamp = False, color = 'yellow' )

		# Save and load coordainte to /tmp/
		self.CI.save_coordinates_to_file( coordinates = coordinates, relative_folder_path = "tmp", file_name = "temp" )
		coordinates = self.CI.load_coordinates_file( relative_folder_path = "tmp", file_name = "temp" )

		# Print found coordinates
		self.P.write( "-- After --", color = 'green' )
		for coordinate in coordinates:
			self.P.write( coordinate, include_time_stamp = False, color = 'yellow' )

C = Coordinates()
C.run()













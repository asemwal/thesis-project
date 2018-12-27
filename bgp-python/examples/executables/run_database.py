import sys, os
from time import sleep

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from clear_screen_tool import Clear_Screen_Tool
from AS_rank_interface import AS_Rank_Interface
from BGP_view_interface import BGP_View_Interface
from peering_DB_interface import Peering_DB_Interface

class Database():
	P = None
	ASRI = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer()
		self.ASRI = AS_Rank_Interface( P = self.P )
		self.BGPVI = BGP_View_Interface( P = self.P )
		self.PDBI = Peering_DB_Interface( P = self.P )

	def __run_AS_Rank( self, AS_number = None ):
		peers = self.ASRI.get_peers( AS_number = AS_number )
		self.P.write( "AS Rank: peers", color = 'green ')
		self.P.write_JSON( peers )

		providers = self.ASRI.get_providers( AS_number = AS_number )
		self.P.write( "AS Rank: providers", color = 'green ')
		self.P.write_JSON( providers )

		customers = self.ASRI.get_customers( AS_number = AS_number )
		self.P.write( "AS Rank: customers", color = 'green ')
		self.P.write_JSON( customers )

	def __run_BGP_View( self, AS_number = None ):
		peers = self.BGPVI.get_peers( AS_number = AS_number )
		self.P.write( "BGP View: peers", color = 'green ')
		self.P.write_JSON( peers )

		providers = self.BGPVI.get_providers( AS_number = AS_number )
		self.P.write( "BGP View: providers", color = 'green ')
		self.P.write_JSON( providers )

		customers = self.BGPVI.get_customers( AS_number = AS_number )
		self.P.write( "BGP View: customers", color = 'green ')
		self.P.write_JSON( customers )

		#Normal
		IP4_prefixes = self.BGPVI.get_IP4_prefixes( AS_number = AS_number, split_in_24 = False )
		self.P.write( "BGP View: IP4_prefixes", color = 'green ')
		self.P.write_JSON( IP4_prefixes )

		#Split in /24 parts
		IP4_prefixes = self.BGPVI.get_IP4_prefixes( AS_number = AS_number, split_in_24 = True )
		self.P.write( "BGP View: IP4_prefixes", color = 'green ')
		self.P.write_JSON( IP4_prefixes )

		IP4_prefixes = self.BGPVI.get_IP4_prefixes( AS_number = AS_number, split_in_24 = False )
		self.P.write( "BGP View: IP4_prefixes", color = 'green ')
		self.P.write_JSON( IP4_prefixes )

	def __run_Peering_DB( self, AS_number = None ):	
		IXs = self.PDBI.get_IXs( AS_number = AS_number )
		self.P.write_JSON( IXs )

	def run( self ):
		self.P.write( "Start" )

		#AS Rank Interface
		self.__run_AS_Rank( AS_number = 286 )
		
		#BGP View Interface
		self.__run_BGP_View( AS_number = 286 )

		#Peering DB
		self.__run_Peering_DB( AS_number = 286 )

Database().run()



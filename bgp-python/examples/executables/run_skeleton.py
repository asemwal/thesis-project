import sys, os, json, time

sys.path.append( str(os.getcwd()) + "/../../src" )
sys.path.append( str(os.getcwd()) + "/../../interfaces" )
sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from printer import Printer
from clear_screen_tool import Clear_Screen_Tool

class Skeleton():
	P = None

	def __init__( self ):
		Clear_Screen_Tool().clear_screen()
		self.P = Printer( write_to_file = True, printer_id = "Test" )

	def run( self ):
		counter = 0
		while True:
			self.P.write( "Hello World! " + str(counter) )
			counter += 1
			time.sleep(1)

Skeleton().run()
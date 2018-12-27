import os, sys

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from ES_interface import ES_Interface
from printer import Printer

P = Printer( write_to_file = True, printer_id = "withdraw" )
ESI = ES_Interface( P = P )
ESI.process_withdraws( RRC_range = [ int(sys.argv[1]), int(sys.argv[2]) ] )
ESI.kill_thread()
exit()


#!/usr/bin/env python2.7

import os, sys

sys.path.append( str(os.getcwd()) + "/../src" )
sys.path.append( str(os.getcwd()) + "/../interfaces" )

from CLI import CLI
from printer import Printer
from AS_rank_interface import AS_Rank_Interface
from BGP_view_interface import BGP_View_Interface

P = None

if len(sys.argv) > 1:
	P = Printer( write_to_file = True, printer_id = str(sys.argv[1]) )
else:
	P = Printer( write_to_file = False, printer_id = "2" )

CLI = CLI( stand_alone = True, P = P )


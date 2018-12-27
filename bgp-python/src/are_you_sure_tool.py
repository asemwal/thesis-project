from termcolor import colored
from printer import Printer

class Are_You_Sure_Tool():
	P = None

	def __init__( self, P = None, program_name = None, no_output = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] Are_You_Sure_Tool: __init__: P is None", color = 'yellow' )

		if no_output is False:
			if program_name is not None:
				self.P.write( "Are_You_Sure_Tool: [" + str(program_name) +  "]: Loading...", color = 'cyan' )
			else:
				self.P.write( "Are_You_Sure_Tool: Loading...", color = 'cyan' )

	def ask_are_you_sure( self, print_output = True ):
		var = ""
		
		while var == "":
			var = raw_input( self.P.get_time_stamp() + colored( "Are you sure? (Y/N): ", attrs=['bold']) )

		if var == "Y":
			return True
		else:	
			if print_output is True:
				self.P.write( "\tAborting...", color = 'cyan' )
			return False
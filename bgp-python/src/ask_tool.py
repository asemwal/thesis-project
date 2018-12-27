from termcolor import colored
from printer import Printer

class Ask_Tool():
	P = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write_warning( "Ask_Tool : __init__ : P is None" )

	def ask( self, question = None, allow_empty = False, expect_list = None, expect_int = None, expect_float = None ):
		if question is None:
			self.P.write_error( "Ask_Tool : ask : question is None" )
			return None

		question = str(question) + " "
		var = raw_input( self.P.get_time_stamp() + colored( str(question).replace("  "," "), attrs=['bold']) )
		
		while self.__check_input( var = var, question = question, allow_empty = allow_empty, expect_list = expect_list, expect_int = expect_int, expect_float = expect_float ) is True:
			var = raw_input( self.P.get_time_stamp() + colored( str(question) + " ", attrs=['bold']) )

		return var

	def __check_input( self, var, question, allow_empty, expect_list, expect_int, expect_float ):
		if var == "" and allow_empty is False:
			if expect_list is not None and len(expect_list) > 0:
				expect_list_str = "Expecting "

				for item in expect_list:
					expect_list_str = expect_list_str + str(item) + " or "

				expect_list_str = expect_list_str + "."
				expect_list_str = expect_list_str.replace(" or .", "." )

				self.P.write( expect_list_str, color = 'red' )
				return True
			elif expect_int is True:
				self.P.write_error( "Ask_Tool: expecting integer" )
				return True
			elif expect_float is True:
				self.P.write_error( "Ask_Tool: expecting float" )
				return True
			else:
				self.P.write_error( "Ask_Tool: expecting something" )
				return True
			
		if expect_int is True:
			try:
				int(var)
			except ( ValueError ):
				self.P.write_error( "Ask_Tool: expecting integer" )
				return True

		if expect_float is True:
			try:
				float(var)
			except ( ValueError ):
				self.P.write( "Ask_Tool: expecting integer", color = 'red' )
				return True


		if expect_list is not None and len(expect_list) > 0:
			found = False

			for item in expect_list:
				if str(item) == str(var):
					found = True

			if found is False:
				expect_list_str = "Ask_Tool: expecting "

				for item in expect_list:
					expect_list_str = expect_list_str + str(item) + " or "

				expect_list_str = expect_list_str + "."
				expect_list_str = expect_list_str.replace(" or .", "." )

				self.P.write_error( expect_list_str )
				return True

		return False


import sys

from printer import Printer

class Params_Tool:
	P = None

	def __init__( self, P = None ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] Params_Tool : __init__ : P is None", color = 'yellow', attrs = ['bold'] )

		self.P.write( "Params_Tool: Loading...", color = 'cyan', attrs=['bold'] )

	def get_params( self, index = 0, wishlist = list(), keywords = None ):
		
		if keywords is None:
			keywords = self.get_argv_keywords()

		params = dict()
		current_key = ""

		for item in wishlist:
			params[item] = None

		while len(keywords) > index:
			if keywords[index].startswith( "--" ):
				current_key = keywords[index].replace("--","")

				if current_key not in params:
					params[current_key] = None
			else:
				if current_key in params:
					if params[current_key] is None:
						params[current_key] = list()
						params[current_key].append( keywords[index] )
					elif type( params[current_key] ) is list:
						params[current_key].append( keywords[index] )
						
			index = index + 1


		result = dict()

		for key in params:
			result_list = list()
			param = params[key]

			if param is None:
				result[key] = None
			else:
				for list_item in param:
					if len( str(list_item) ) != 0:
						result_list.append( list_item )

				result[key] = result_list
				
		return result

	def get_argv_keywords( self ):
		keywords = list()

		index = 1
		amount_of_argvs = len(sys.argv) - 1
		for x in range( 1, amount_of_argvs + 1 ):
			keywords.append( sys.argv[x] )

		return keywords
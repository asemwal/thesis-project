import datetime, sys, time, json
from termcolor import colored
import random, string

class Printer:
	FT = None
	__write_to_file = None
	__write_to_file_cache_size = None
	__write_to_file_file_name = None

	__last_was_rewrite = False
	__keep_this_line = False

	def __init__( self, write_to_file = False, write_to_file_cache_size = 100, printer_id = "temp" ):
		self.__write_to_file = write_to_file
		self.__write_to_file_cache_size = write_to_file_cache_size
		self.__write_to_file_file_name = str(printer_id) + ".output"
		from file_tool import File_Tool

		if self.__write_to_file is True:
			self.FT = File_Tool( base_path = "output/", program_name = "Printer", write_to_file = True )
			self.FT.save_text_file( data_text = "", file_name = self.__write_to_file_file_name )


		if self.__write_to_file is True:
			self.write( "Loading Printer... (write_to_file = " + str(self.__write_to_file) + ", printer_id = " + str(printer_id) + ")", color = 'cyan' )
			self.write( "Printer: To capture the output, run /executables/capture.sh" )
		else:
			self.write( "Loading Printer... (write_to_file = " + str(self.__write_to_file) + ")", color = 'cyan' )

	def get_last_was_rewrite( self ):
		return self.__last_was_rewrite

	def reset_last_was_rewrite( self ):
		self.__last_was_rewrite = False

	def write_JSON( self, data_JSON = None ):
		lines = json.dumps( data_JSON, sort_keys=True, indent=2, separators=(',', ': ') ) 

		for line in lines.split("\n"):
			self.write( line, include_time_stamp = False )

	def write_debug( self, data = "" ):
		data = "[DEBUG] " + str(data)

		if "\t" in data:
			data = data.replace("\t","")
			data = "\t" + data

		self.write( data = data, color = 'blue' )

	def write_warning( self, data = "" ):
		data = "[WARNING] " + str(data)

		if "\t" in data:
			data = data.replace("\t","")
			data = "\t" + data

		self.write( data = data, color = 'yellow' )

	def write_error( self, data = "" ):
		data = "[ERROR] " + str(data)

		if "\t" in data:
			data = data.replace("\t","")
			data = "\t" + data

		self.write( data = data, color = 'red' )

	def write( self, data = "", color = None, attrs = None, force_new_line = False, include_time_stamp = True ):
		if self.__last_was_rewrite is True:
			self.__last_was_rewrite = False
			self.__write( "" )

		if force_new_line is True:
			self.__write( "" )

		if attrs is None:
			attrs = ['bold']

		if include_time_stamp is True:
			self.__write( self.get_time_stamp() + colored( str(data), color = color, attrs = attrs ) )
		elif include_time_stamp is False:
			self.__write( colored( str(data), color = color, attrs = attrs ) )

		self.__last_was_rewrite = False
		self.__keep_this_line is False

	def rewrite_debug( self, data = "" ):
		data = "[DEBUG] " + data

		if "\t" in data:
			data = data.replace("\t","")
			data = "\t" + data

		self.rewrite( data = data, color = 'blue' )

	def rewrite_warning( self, data = "" ):
		data = "[WARNING] " + data

		if "\t" in data:
			data = data.replace("\t","")
			data = "\t" + data

		self.rewrite( data = data, color = 'yellow' )

	def rewrite_error( self, data = "" ):
		data = "[ERROR] " + data

		if "\t" in data:
			data = data.replace("\t","")
			data = "\t" + data

		self.rewrite( data = data, color = 'red' )

	def rewrite( self, data = "", color = None, attrs = None, force_new_line = False, keep_this_line = False, include_time_stamp = True ):
		if force_new_line is True and self.__last_was_rewrite is True:
			self.__write( "" )
		elif self.__keep_this_line is True:
			self.__write( "" )

		if attrs is None:
			attrs = ['bold']

		if include_time_stamp is True:
			self.__rewrite( "\r" + self.get_time_stamp() + colored( str(data), color = color, attrs = attrs ) )
		elif include_time_stamp is False:
			self.__rewrite( "\r" + colored( str(data), color = color, attrs = attrs ) )

		self.__last_was_rewrite = True
		self.__keep_this_line = keep_this_line

	def get_time_stamp( self ):
		time_stamp = datetime.datetime.fromtimestamp( time.time() ).strftime('%Y-%m-%d %H:%M:%S')
		return colored( '[' + time_stamp + '] ', 'blue' )

	def __rewrite( self, line ):
		if self.__write_to_file is True:
			self.__rewrite_to_CSV_file( line = line )
		
		sys.stdout.write( line )
		sys.stdout.flush()

	def __write( self, line ):
		if self.__write_to_file is True:
			self.__write_to_CSV_file( line = line )
		
		print line

	def __rewrite_to_CSV_file( self, line ):
		if self.FT.check_file_exists( file_name = self.__write_to_file_file_name ) is True:
			lines = self.FT.load_CSV_file( file_name = self.__write_to_file_file_name, seperator = "\n", simple_mode = True )
			if self.__last_was_rewrite is False:
				lines.append( str(line).replace( "\n", "" ) )
		else:
			lines = list()

		#print lines

		if len(lines) == 0:
			lines.append( str(line).replace( "\n", "" ) )

		lines[ len(lines) - 1 ] = str(line).replace( "\n", "" )

		self.FT.save_CSV_file( data_list = lines, file_name = self.__write_to_file_file_name, seperator = "\n" )

	def __write_to_CSV_file( self, line ):
		if self.FT.check_file_exists( file_name = self.__write_to_file_file_name ) is True:
			lines = self.FT.load_CSV_file( file_name = self.__write_to_file_file_name, seperator = "\n", simple_mode = True )
			lines.append( str(line).replace( "\n", "" ) )
		else:
			lines = list()

		if len(lines) > self.__write_to_file_cache_size:
			lines.pop(0)

		self.FT.save_CSV_file( data_list = lines, file_name = self.__write_to_file_file_name, seperator = "\n" )












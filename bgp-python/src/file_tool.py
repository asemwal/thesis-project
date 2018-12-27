import os, json, hashlib, glob, time, csv
from termcolor import colored

from printer import Printer

class File_Tool():
	P = None
	base_path = None
	write_to_file = None
	printer_id = None
	project_path = None
	program_name = None

	def __init__( self, base_path = None, program_name = None, P = None, write_to_file = False ):
		self.write_to_file = write_to_file

		if self.write_to_file is False:
			from are_you_sure_tool import Are_You_Sure_Tool
			from printer import Printer

		if self.write_to_file is False:
			if P is not None:
				self.P = P
			else:
				self.P = Printer()
				self.__write_warning( "File_Tool: __init__: P is None" )

		self.__set_project_path()
		self.__clean_project_path()

		self.base_path = ""
		if base_path is not None:
			self.base_path = base_path
		
		self.base_path = self.base_path.replace( "//", '/' )

		if len(self.base_path) > 0:
			if self.base_path[ len( self.base_path ) - 1 ] != '/':
				self.base_path = self.base_path + "/"

			if self.base_path[ 0 ] == '/':
				self.base_path = self.base_path[1:]

			if program_name is not None:
				self.program_name = str(program_name)

			self.__write( "\tFile_Tool" + self.__get_program_name() + ": Initialised with base path " + colored( str( self.get_base_path() ), color = 'green' ) )
		elif program_name is not None:
			self.program_name = str(program_name)
			self.__write( "\tFile_Tool" + self.__get_program_name() + ": Initialised with base path " + colored( str( self.get_base_path() ), color = 'green' ) )

		self.check_folder_exists()

	def __get_program_name( self ):
		if self.program_name is None:
			return ""
		else:
			return " [" + str(self.program_name) + "]"

	def __set_project_path( self ):
		project_path = os.getcwd() + "/"
		for x in range( 0, 5 ):
			file_paths = glob.glob( project_path + str("*") )

			for file_path in file_paths:
				file_path = file_path.split('/')
				file_name = file_path[ len(file_path) - 1 ]

				if "ES_address.txt" in file_name:
					self.project_path = project_path
					return

			project_path = project_path + "../"

		self.__write_error( "File_Tool" + self.__get_program_name() + ": __find_project_path: ES_address.txt not found..." )
		exit()

	def __clean_project_path( self, print_status = False ):
		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": __clean_project_path: before: project_path = " + str(self.project_path) )

		folders = self.project_path.split('/')
		folders = folders[1:-1]

		new_folders = ['']

		skip_counter = 0
		for x in range( len(folders) - 1, -1, -1 ):
			if ".." in folders[x]:
				skip_counter += 1
				continue

			if skip_counter > 0:
				skip_counter -= 1
				continue

			new_folders.append( folders[x] )

		new_folders.append('')
		new_folders = list( reversed( new_folders ) )

		self.project_path = "/".join(new_folders)

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": __clean_project_path:  after: project_path = " + str(self.project_path) )

	def __ask_are_you_sure( self ):
		var = ""
		
		while var == "":
			var = raw_input( self.P.get_time_stamp() + colored( "Are you sure? (Y/N): ", attrs=['bold']) )

		if var == "Y":
			return True
		else:	
			self.__write( "\tAborting...", color = 'cyan' )
			return False

	def get_base_path( self ):
		return self.project_path + str( self.base_path )

	def clear_folder( self, relative_folder_path = "", keep_list = list(), required_alive_time = 300, print_status = True ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": clear_folder: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": clear_folder: setting relative_folder_pathname = ''" )
			relative_folder_path = ""
			
		if self.check_folder_exists( relative_folder_path = relative_folder_path ) is False:
			return
			
		folder_path = self.get_folder_path( relative_folder_path = relative_folder_path )

		if not str(folder_path).endswith("tmp/"):
			self.__write_warning( "File_Tool" + self.__get_program_name() + ": clear_folder: Deleting content of folder with folder_path not ending with 'tmp'" )
			self.__write_warning( "File_Tool" + self.__get_program_name() + ": clear_folder: folder_path = " + str(folder_path) )

			if len(keep_list) != 0:
				self.__write( "File_Tool" + self.__get_program_name() + ": clear_folder: keep_list = " + str(keep_list) )

			if self.write_to_file is False:
				if self.__ask_are_you_sure() is False:
					return

		file_paths = glob.glob( folder_path + str("*") )

		if len( file_paths ) == 0:
			if print_status:
				self.__write( "\tNo Files found..." )

		for file_path in file_paths:
			try:
				keep = False
				new = False

				time_epoch = os.path.getmtime(file_path)
				current_time = time.time()

				if current_time - time_epoch < required_alive_time and str(folder_path).endswith("tmp/"):
					new = True

				for item in keep_list:
					if str(item) in file_path:
						keep = True

				if os.path.isdir(file_path):
					temp_list = file_path.split('/')
					folder_name = temp_list[ len(temp_list) - 1 ]
					self.clear_folder( relative_folder_path = relative_folder_path + str(folder_name) + "/", keep_list = keep_list, required_alive_time = required_alive_time )
				elif new is True:
					if print_status:
						self.__write( "\tToo Recent: " + str(file_path), color = 'blue' )		
				elif keep is True:
					if print_status:
						self.__write( "\tKeeping: " + str(file_path), color = 'blue' )
				else:
					os.remove(file_path)
					if print_status:
						self.__write( "\tDeleted: " + str(file_path)  )
			except( OSError ):
				if print_status:
					self.__write( "\tOSError: " + str(file_path) )
			except( IOError ):
				if print_status:
					self.__write( "\tIOError: " + str(file_path) )
			
	def remove_file( self, relative_folder_path = "", file_name = None, file_path = None, print_status = False ):
		if file_path is None:
			if relative_folder_path is None:
				self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": remove_file: relative_folder_pathname is None" )
				self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": remove_file: setting relative_folder_pathname = ''" )
				relative_folder_path = ""

			if file_name is None:
				self.__write_error( "File_Tool" + self.__get_program_name() + ": remove_file: file_name is None" )
				return None

			file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )
		
		if file_path is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": remove_file: file_name and file_path is None" )
			return

		try:
			os.remove(file_path)
		except( IOError ):
			self.__write_error( "File_Tool" + self.__get_program_name() + ": remove_file: file not found" )

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": remove_file: deleted " + str(file_path) )

	def create_checksum( self, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": create_checksum: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": create_checksum: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": create_checksum: file_name is None" )
			return None

		checksum = None

		if self.check_file_exists( relative_folder_path = relative_folder_path, file_name = file_name ):
			file_data = self.load_file( relative_folder_path = relative_folder_path, file_name = file_name )
			checksum = hashlib.md5( file_data.read() ).hexdigest()
		else:
			return
		
		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": create_checksum: file_name = " + file_name + ", checksum = " + checksum, color = 'cyan' )

		file_name = file_name + ".checksum"

		self.save_text_file( data_text = checksum, relative_folder_path = relative_folder_path, file_name = file_name )

		return checksum

	def check_checksum( self, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": check_checksum: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": check_checksum: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": check_checksum: file_name is None" )
			return False

		checksum = None

		if self.check_file_exists( relative_folder_path = relative_folder_path, file_name = file_name ):
			checksum_file_name = file_name + ".checksum"

			if self.check_file_exists( relative_folder_path = relative_folder_path, file_name = checksum_file_name ):
				checksum = self.load_text_file( relative_folder_path = relative_folder_path, file_name = checksum_file_name )

		if checksum is not None:
			file_data = self.load_file( relative_folder_path = relative_folder_path, file_name = file_name )
			new_checksum = hashlib.md5( file_data.read() ).hexdigest()

			if checksum == new_checksum:
				if print_status is True:
					self.__write( "File_Tool" + self.__get_program_name() + ": check_checksum: file_name = " + file_name + " has a valid checksum", color = 'cyan' )

				return True

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": check_checksum: file_name = " + file_name + " does not has a valid checksum", color = 'cyan' )

		return False

	def load_CSV_file( self, relative_folder_path = "", file_name = None, seperator = ",", simple_mode = False, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_CSV_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_CSV_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_CSV_file: file_name is None" )
			return None

		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )
		file_data = None

		try:
			if simple_mode is True:
				file_data = open( file_path, 'rb' ).read()
			elif simple_mode is False:
				file_data = open( file_path, 'rb' )
		except (IOError):
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_CSV_file: Cannot open " + str(file_path) )
			return None

		if simple_mode is True:
			file_data = file_data.split(seperator)

			result = list()
			for data in file_data:
				result.append(data)

		elif simple_mode is False:
			if print_status is True:
				self.__write( "File_Tool" + self.__get_program_name() + ": load_CSV_file: loaded " + str(file_path), color = 'cyan' )

			return csv.reader(file_data)

		if print_status is True:
				self.__write( "File_Tool" + self.__get_program_name() + ": load_CSV_file: loaded " + str(file_path), color = 'cyan' )


		return result

	def save_CSV_file( self, data_list = None, relative_folder_path = "", file_name = None, seperator = ",", print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": save_CSV_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": save_CSV_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""
			
		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": save_CSV_file: file_name is None" )
			return None

		self.check_folder_exists( relative_folder_path = relative_folder_path )
		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		data_text = ""

		for item in data_list:
			data_text = str(data_text) + str(item) + str(seperator)

		data_text = str(data_text) + "]"
		data_text = data_text.replace( str(seperator) + "]", "" ) 

		file = open( file_path, 'w' )
		file.write( str(data_text) )
		file.close()

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": save_CSV_file: saved " + str(file_path), color = 'cyan' )

	def save_JSON_file( self, data_JSON = None, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": save_JSON_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": save_JSON_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": save_JSON_file: file_name is None" )
			return None

		if data_JSON is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": save_JSON_file: data_JSON is None" )
			return

		self.check_folder_exists( relative_folder_path = relative_folder_path )
		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		file = open( file_path, 'w' )
		data_text = json.dumps( data_JSON )
		file.write( data_text )
		file.close()

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": save_JSON_file: saved " + str(file_path), color = 'cyan' )

	def add_text_to_file( self, data_text = None, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": add_text_to_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": add_text_to_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": add_text_to_file: file_name is None" )
			return None

		self.check_folder_exists( relative_folder_path = relative_folder_path )
		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		if self.check_file_exists( relative_folder_path = relative_folder_path, file_name = file_name ) is False:
			file = open( file_path, 'w' )
			file.write( data_text )
			file.close()	
		else:
			file = open( file_path, 'a' )
			file.write( data_text )
			file.close()	

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": add_text_to_file: added " + str(data_text) + " to " + str(file_path), color = 'cyan' )

	def save_text_file( self, data_text = None, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": save_text_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": save_text_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": save_text_file: file_name is None" )
			return None

		self.check_folder_exists( relative_folder_path = relative_folder_path )
		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		file = open( file_path, 'w' )
		file.write( str(data_text) )
		file.close()

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": save_text_file: saved " + str(file_path), color = 'cyan' )

	def load_JSON_file( self, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_JSON_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_JSON_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_JSON_file: file_name is None" )
			return None

		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )
		file_data = None

		try:
			file_data = open( file_path, 'r' )
		except (IOError):
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_JSON_file: Cannot open " + str(file_path) )
			return None

		if print_status is True:
			self.__write( "File_Tool" + self.__get_program_name() + ": load_JSON_file: loaded " + str(file_path), color = 'cyan' )

		return json.load( file_data )	

	def load_file( self, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool: load_file: file_name is None" )
			return None

		if relative_folder_path is None:
			relative_folder_path = ""

		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		try:
			result = open( file_path, 'r' )
			if print_status is True:
				self.__write( "File_Tool" + self.__get_program_name() + ": load_file: loaded " + str(file_path), color = 'cyan' )

			return result
		except (IOError):
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_file: Cannot open " + str(file_path) )
			return ""
			
	def load_text_file( self, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_text_file: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": load_text_file: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_text_file: file_name is None" )
			return None

		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name )

		try:
			result = open( file_path, 'r' ).read()
			if print_status is True:
				self.__write( "File_Tool" + self.__get_program_name() + ": load_text_file: loaded " + str(file_path), color = 'cyan' )
			
			return result
		except (IOError):
			self.__write_error( "File_Tool" + self.__get_program_name() + ": load_text_file: Cannot open " + str(file_path), color = 'cyan' )
			return None

	def get_file_path( self, relative_folder_path = "", file_name = None ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": get_file_path: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": get_file_path: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": get_file_path: file_name is None" )
			return None

		if not str(relative_folder_path).endswith("/"): 
			relative_folder_path = relative_folder_path + "/"

		result = self.get_base_path() + str(relative_folder_path) + str(file_name)
		return result.replace( "//", "/" )

	def get_folder_path( self, relative_folder_path = "" ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": get_folder_path: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": get_folder_path: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if not str(relative_folder_path).endswith("/"): 
			relative_folder_path = relative_folder_path + "/"

		result = self.get_base_path() + relative_folder_path 
		return result.replace( "//", "/" )

	def check_file_exists( self, relative_folder_path = "", file_name = None, print_status = False ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": check_file_exists: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": check_file_exists: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		if file_name is None:
			self.__write_error( "File_Tool" + self.__get_program_name() + ": check_file_exists: file_name is None" )
			return False

		file_path = self.get_file_path( relative_folder_path = relative_folder_path, file_name = file_name ) 
		status = os.path.isfile( file_path )

		if status is True:
			if print_status is True:
				self.__write( "File_Tool" + self.__get_program_name() + ": check_file_exists: " + str(file_path) + " exists", color = 'cyan' )

			return True
		else:
			if print_status is True:
				self.__write( "File_Tool" + self.__get_program_name() + ": check_file_exists: " + str(file_path) + " does not exist", color = 'cyan' )

			return False

	def check_folder_exists( self, relative_folder_path = "" ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": check_folder_exists: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": check_folder_exists: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		file_path = self.get_folder_path( relative_folder_path = relative_folder_path ) 

		if not os.path.exists( file_path ):
			self.__write("File_Tool" + self.__get_program_name() + ": check_folder_exists: Folder " + file_path + " does not exist -> Creating..." )
			os.makedirs(file_path)
			return False

		return True

	def get_file_list( self, relative_folder_path = "" ):
		if relative_folder_path is None:
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": get_file_list: relative_folder_pathname is None" )
			self.P.__write_warning( "File_Tool" + self.__get_program_name() + ": get_file_list: setting relative_folder_pathname = ''" )
			relative_folder_path = ""

		folder_path = self.get_folder_path( relative_folder_path = relative_folder_path )
		file_paths = glob.glob( folder_path + str("*") )

		result = list()
		for file_path in file_paths:
			file_path = file_path.split('/')
			file_path = file_path[ len(file_path) - 1 ]
			result.append( file_path )

		return result

	def __write( self, line, color = None, attrs = None ):
		if self.write_to_file is False:
			self.P.write( data = line, color = color, attrs = None )

	def __write_warning( self, line ):
		line = "[WARNING] " + str(line)

		if self.write_to_file is False:
			self.P.write( data = line, color = "yellow" )

	def __write_error( self, line ):
		line = "[ERROR] " + str(line)

		if self.write_to_file is False:
			self.P.write( data = line, color = "red" )



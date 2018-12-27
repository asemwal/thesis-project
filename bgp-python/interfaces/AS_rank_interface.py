import json, requests, os, sys, wget, bz2
from time import sleep

sys.path.append( str(os.getcwd()) + "/../src" )

from printer import Printer
from file_tool import File_Tool
from string_tool import String_Tool
from ask_tool import Ask_Tool

class AS_Rank_Interface():
	AS_to_peers_dict = None
	AS_to_customers_dict = None
	AS_to_providers_dict = None

	base_url = None
	FT = None
	ST = None
	AT = None
	save_counter = None
	save_data_bool = None

	def __init__( self, P = None, save_data = True ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] AS_Rank_Interface: __init__ : P is None", color = 'yellow' )

		self.P.write( "AS_Rank_Interface: Loading...", color = 'cyan' )

		if save_data is not None:
			self.save_data_bool = save_data
		else:
			self.P.write( "[WARNING] AS_Rank_Interface: __init__ : save_data is None", color = 'yellow' )
			self.save_data_bool = False

		self.P.write( "AS_Rank_Interface: __init__ : save_data = " + str(self.save_data_bool) )

		self.FT = File_Tool( P = self.P, base_path = "/data/AS_Rank", program_name = "AS_Rank_Interface" )
		self.ST = String_Tool()
		self.AT = Ask_Tool( P = self.P )

		self.AS_to_peers_dict = dict()
		self.AS_to_customers_dict = dict()
		self.AS_to_providers_dict = dict()

		self.base_url = "http://as-rank.caida.org/api/v1/"
		self.save_counter = 0
		self.__load_data()
		#self.count()

	def __count( self ):
		cache = dict()
		temp = 0
		AS_numbers = self.get_all_saved_ASes()

		counter = len( AS_numbers )
		for from_AS in AS_numbers:
			counter -= 1
			if counter % 100 == 0:
				self.P.rewrite( "AS_Rank_Interface_AS_to_peers: __count: " + str(counter) + " ASes left, found " + str(temp/1000) + "k items      " )

			for to_AS in self.get_peers( AS_number = from_AS ):
				_id = str(from_AS) + "-" + str(to_AS) 
				if _id in cache:
					continue
				else:
					cache[_id] = None

				temp += 1

				#self.add_ES_relation( from_AS = from_AS, to_AS = to_AS, type = self.TYPE_P2P, source = 0, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )	

			for to_AS in self.get_customers( AS_number = from_AS ):
				_id = str(from_AS) + "-" + str(to_AS) 
				if _id in cache:
					continue
				else:
					cache[_id] = None

				temp += 1

				#self.add_ES_relation( from_AS = from_AS, to_AS = to_AS, type = self.TYPE_P2C, source = 0, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )	

			for to_AS in self.get_providers( AS_number = from_AS ):
				_id = str(from_AS) + "-" + str(to_AS) 
				if _id in cache:
					continue
				else:
					cache[_id] = None

				temp += 1

				#self.add_ES_relation( from_AS = from_AS, to_AS = to_AS, type = self.TYPE_C2P, source = 0, overwrite = overwrite, create = create, print_debug = print_debug, print_server_response = print_server_response )	


	def __load_data( self ):
		if self.FT.check_checksum( file_name = "AS_Rank_Interface_AS_to_peers.json" ):
			self.AS_to_peers_dict = self.FT.load_JSON_file( file_name = "AS_Rank_Interface_AS_to_peers.json", print_status = False  )
			self.P.write( "\tLoaded AS_to_peers_dict (" + str(len(self.AS_to_peers_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_peers_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "AS_Rank_Interface_AS_to_customers.json" ):
			self.AS_to_customers_dict = self.FT.load_JSON_file( file_name = "AS_Rank_Interface_AS_to_customers.json", print_status = False  )
			self.P.write( "\tLoaded AS_to_customers_dict (" + str(len(self.AS_to_customers_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_customers_dict", color = 'red' )

		if self.FT.check_checksum( file_name = "AS_Rank_Interface_AS_to_providers.json" ):
			self.AS_to_providers_dict = self.FT.load_JSON_file( file_name = "AS_Rank_Interface_AS_to_providers.json", print_status = False )
			self.P.write( "\tLoaded AS_to_providers_dict (" + str(len(self.AS_to_providers_dict)) + " items)", color = 'green' )
		else:
			self.P.write( "\tNot Loaded AS_to_providers_dict", color = 'red' )
			
	def save_data( self ):
		self.save_counter = 1001
		self.__save_data()

	def __save_data( self ):
		if self.save_data_bool is False:
			return

		self.save_counter += 1

		if self.save_counter > 1000:
			self.P.rewrite( "\tAS_Rank_Interface: __save_data: start -*-*-*- DO NOT TERMINATE PROGRAM -*-*-*-         ", color = 'yellow', force_new_line = True )

			self.FT.save_JSON_file( file_name = "AS_Rank_Interface_AS_to_peers.json", data_JSON = self.AS_to_peers_dict )
			self.FT.create_checksum( file_name = "AS_Rank_Interface_AS_to_peers.json" )
			self.FT.save_JSON_file( file_name = "AS_Rank_Interface_AS_to_customers.json", data_JSON = self.AS_to_customers_dict )
			self.FT.create_checksum( file_name = "AS_Rank_Interface_AS_to_customers.json" )
			self.FT.save_JSON_file( file_name = "AS_Rank_Interface_AS_to_providers.json", data_JSON = self.AS_to_providers_dict )
			self.FT.create_checksum( file_name = "AS_Rank_Interface_AS_to_providers.json" )
			self.save_counter = 0

			self.P.rewrite( "\tAS_Rank_Interface: __save_data: done!                                                   ", color = 'green', keep_this_line = True )

	def __get_data_JSON( self, url ):
		try:
			text = requests.get( url=url ).text
			return json.loads(text)
		except( requests.exceptions.ConnectionError, ValueError ):
			self.P.rewrite_error( "[ERROR] AS_Rank_Interface: get_index: cannot connect to " + str(url) )
			sleep(1)
			return None

	def get_relation_type( self, dest_AS = None, source_AS = None ):
		if dest_AS is None:
			self.P.write_error( "AS_Rank_Interface: get_relation_type: dest_AS = None" )
			return None

		if source_AS is None:
			self.P.write_error( "AS_Rank_Interface: get_relation_type: source_AS = None" )
			return None

		if str(dest_AS) not in self.AS_to_peers_dict:
			self.get_peers( AS_number = dest_AS )

		if str(dest_AS) not in self.AS_to_customers_dict:
			self.get_customers( AS_number = dest_AS )

		if str(dest_AS) not in self.AS_to_providers_dict:
			self.get_providers( AS_number = dest_AS )

		if str(source_AS) not in self.AS_to_peers_dict:
			self.get_peers( AS_number = source_AS )

		if str(source_AS) not in self.AS_to_customers_dict:
			self.get_customers( AS_number = source_AS )

		if str(source_AS) not in self.AS_to_providers_dict:
			self.get_providers( AS_number = source_AS )

		if int(source_AS) in self.AS_to_peers_dict[ str(dest_AS) ]:
			return "p2p"

		if int(source_AS) in self.AS_to_customers_dict[ str(dest_AS) ]:
			return "c2p"

		if int(source_AS) in self.AS_to_providers_dict[ str(dest_AS) ]:
			return "p2c"

		if int(dest_AS) in self.AS_to_peers_dict[ str(source_AS) ]:
			return "p2p"

		if int(dest_AS) in self.AS_to_customers_dict[ str(source_AS) ]:
			return "p2c"

		if int(dest_AS) in self.AS_to_providers_dict[ str(source_AS) ]:
			return "c2p"

		return None

	def bulk_download( self, force_remove = False, force_save_results = False, use_serial_1 = False, use_serial_2 = False ):
		self.P.write( "AS_Rank_Interface: bulk_download: start", color = 'green' )

		if force_remove is False:
			answer = self.AT.ask( question = "AS_Rank_Interface: bulk_download: delete local data (Y/N)?", expect_list = ["Y","N"] )
		else:
			answer = "Y"

		if "Y" in answer:
			self.P.write( "AS_Rank_Interface: bulk_download: local data deleted" )
			self.AS_to_peers_dict = dict()
			self.AS_to_customers_dict = dict()
			self.AS_to_providers_dict = dict()

		if self.FT.check_file_exists( relative_folder_path = "../../tmp", file_name = "AS_rank_file_names.txt" ) is True:
			os.remove( self.FT.get_file_path( relative_folder_path = "../../tmp", file_name = "AS_rank_file_names.txt" ) )

		if use_serial_1 is False and use_serial_2 is False:
			answer = self.AT.ask( question = "AS_Rank_Interface: bulk_download: serial-1 or serial-2 (1/2)?", expect_list = [1,2] )

			if "1" == answer:
				url = "http://data.caida.org/datasets/as-relationships/serial-1/"
			elif "2" == answer:
				url = "http://data.caida.org/datasets/as-relationships/serial-2/"
		elif use_serial_1 is True:
			url = "http://data.caida.org/datasets/as-relationships/serial-1/"
		elif use_serial_2 is True:
			url = "http://data.caida.org/datasets/as-relationships/serial-2/"
		else:
			self.P.write_error( "AS_Rank_Interface: use_serial_1 is True and use_serial_2 is True" )

		file_path = self.FT.get_file_path( relative_folder_path = "../../tmp", file_name = "AS_rank_file_names.txt" )

		wget.download(url, out= file_path, bar = None )

		lines = self.FT.load_text_file( relative_folder_path = "../../tmp", file_name = "AS_rank_file_names.txt" )
		lines = lines.split("\n")

		file_names = list()
		for line in lines:
			file_name = self.ST.get_words_after_substring( full_text = line, sub_text_before_words = '/unknown.gif" alt="[   ]"> <a href="', numberOfWords = 1 )

			if len(file_name) > 0 and "as-rel" in file_name[0]:
				file_names.append( file_name[0] )

		self.P.write( "AS_Rank_Interface: bulk_download: found " + str( len(file_names) ) + " files:" )
		counter = 0
		expect_list = list()
		modes = "("
		for file_name in file_names:
			self.P.write( "\t(" + str(counter).zfill(2) + ") - " + str(file_name) )
			expect_list.append( counter )
			
			if counter != 0:
				modes = str(modes) + "/" + str(counter)
			else:
				modes = str(modes) + str(counter)

			counter += 1

		modes += ")"

		file_name_index = int( self.AT.ask( question = "Select file " + str(modes) + ":", expect_list = expect_list ) )
		file_name = file_names[ file_name_index ]

		download_path = url + file_name

		if self.FT.check_file_exists( file_name = file_name ) is True:
			os.remove( self.FT.get_file_path( relative_folder_path = "../../tmp", file_name = file_name ) )

		self.P.write( "\tAS_Rank_Interface: bulk_download: Downloading " + download_path + "      " )

		file_path = self.FT.get_file_path( relative_folder_path = "../../tmp", file_name = file_name )
		wget.download(download_path, out= file_path  )
		print ""

		file_size = int( os.path.getsize( file_path ) ) / 1024
		self.P.write( "\tAS_Rank_Interface: bulk_download: Unzipping " + file_path + " (size=" + str(file_size) + "kb)      "  )

		zip_file = bz2.BZ2File( file_path )
		file_content = zip_file.read()

		file_content = file_content.split("\n")

		temp = 0
		counter = len(file_content)
		for line in file_content:
			counter -= 1
			if counter % 1000 == 0:
				self.P.rewrite( "\tAS_Rank_Interface: bulk_download: " + str(counter/1000) + "k lines left, found " + str(temp/1000) + "k relationship      " )

			elements = line.split('|')

			try:
				from_AS = int(elements[0])
				to_AS = int(elements[1])

				if from_AS == to_AS:
					print line

				type = int(elements[2])

				if type == -1:
					if str(from_AS) not in self.AS_to_customers_dict:
						self.AS_to_customers_dict[str(from_AS)] = list()

					if str(from_AS) not in self.AS_to_providers_dict:
						self.AS_to_providers_dict[str(from_AS)] = list()

					if str(from_AS) not in self.AS_to_peers_dict:
						self.AS_to_peers_dict[str(from_AS)] = list()

					if str(to_AS) not in self.AS_to_customers_dict:
						self.AS_to_customers_dict[str(to_AS)] = list()

					if str(to_AS) not in self.AS_to_providers_dict:
						self.AS_to_providers_dict[str(to_AS)] = list()

					if str(to_AS) not in self.AS_to_peers_dict:
						self.AS_to_peers_dict[str(to_AS)] = list()

					self.AS_to_customers_dict[str(from_AS)].append( int(to_AS) )
					self.AS_to_customers_dict[str(from_AS)] = list( sorted(self.AS_to_customers_dict[str(from_AS)]) )

					self.AS_to_providers_dict[str(to_AS)].append( int(from_AS) )
					self.AS_to_providers_dict[str(to_AS)] = list( sorted(self.AS_to_providers_dict[str(to_AS)]) )

					temp += 2
				elif type == 0:
					if str(from_AS) not in self.AS_to_customers_dict:
						self.AS_to_customers_dict[str(from_AS)] = list()

					if str(from_AS) not in self.AS_to_providers_dict:
						self.AS_to_providers_dict[str(from_AS)] = list()

					if str(from_AS) not in self.AS_to_peers_dict:
						self.AS_to_peers_dict[str(from_AS)] = list()

					if str(to_AS) not in self.AS_to_customers_dict:
						self.AS_to_customers_dict[str(to_AS)] = list()

					if str(to_AS) not in self.AS_to_providers_dict:
						self.AS_to_providers_dict[str(to_AS)] = list()

					if str(to_AS) not in self.AS_to_peers_dict:
						self.AS_to_peers_dict[str(to_AS)] = list()

					self.AS_to_peers_dict[str(from_AS)].append( int(to_AS) )
					self.AS_to_peers_dict[str(from_AS)] = list( sorted(self.AS_to_peers_dict[str(from_AS)]) )

					self.AS_to_peers_dict[str(to_AS)].append( int(from_AS) )
					self.AS_to_peers_dict[str(to_AS)] = list( sorted(self.AS_to_peers_dict[str(to_AS)]) )

					temp += 2
			except( ValueError ):
				continue

		print ""
		if force_save_results is False:
			answer = self.AT.ask( question = "AS_Rank_Interface: bulk_download: save results (Y/N)?", expect_list = ["Y","N"] )
		else:
			answer = "Y"

		if "Y" in answer:
			self.save_data()

	def get_all_saved_ASes( self ):
		data_list = list()
		for AS_number in self.AS_to_peers_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_providers_dict.keys():
			data_list.append( int(AS_number) )

		for AS_number in self.AS_to_customers_dict.keys():
			data_list.append( int(AS_number) )

		return list(sorted(set(data_list)))

	def get_peers( self, AS_number = None ):
		if AS_number is None:
			self.P.write_error( "AS_Rank_Interface: get_peers: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_peers_dict:
			return self.AS_to_peers_dict[str(AS_number)]

		url = self.base_url + "asns/" + str(AS_number) + "/links"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if "data" not in data_JSON:
			self.P.write_error( "[ERROR] AS_Rank_Interface: get_index: 'data' not in data_JSON: url = " + str(url) )
			return

		self.AS_to_peers_dict[str(AS_number)] = list()

		data = data_JSON['data']
		for item in data:
			if "peer" in item['relationship']:
				self.AS_to_peers_dict[str(AS_number)].append( int(item['asn']) )

		self.AS_to_peers_dict[str(AS_number)] = list( sorted(self.AS_to_peers_dict[str(AS_number)]) )

		self.__save_data()
		return self.AS_to_peers_dict[str(AS_number)]

	def get_customers( self, AS_number ):
		if AS_number is None:
			self.P.write_error( "AS_Rank_Interface: get_customers: AS_number = None" )
			return list()
		
		if str(AS_number) in self.AS_to_customers_dict:
			return self.AS_to_customers_dict[str(AS_number)]

		url = self.base_url + "asns/" + str(AS_number) + "/links"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if "data" not in data_JSON:
			self.P.write_error( "[ERROR] AS_Rank_Interface: get_index: 'data' not in data_JSON: url = " + str(url) )
			return

		self.AS_to_customers_dict[str(AS_number)] = list()

		data = data_JSON['data']
		for item in data:
			if "customer" in item['relationship']:
				self.AS_to_customers_dict[str(AS_number)].append( int(item['asn']) )

		self.AS_to_customers_dict[str(AS_number)] = list( sorted(self.AS_to_customers_dict[str(AS_number)]) )

		self.__save_data()
		return self.AS_to_customers_dict[str(AS_number)]

	def get_providers( self, AS_number = None ):
		if AS_number is None:
			self.P.write_error( "AS_Rank_Interface: get_providers: AS_number = None" )
			return list()

		if str(AS_number) in self.AS_to_providers_dict:
			return self.AS_to_providers_dict[str(AS_number)]

		url = self.base_url + "asns/" + str(AS_number) + "/links"

		data_JSON = None
		while data_JSON is None:
			data_JSON = self.__get_data_JSON( url = url )

		if "data" not in data_JSON:
			self.P.write_error( "AS_Rank_Interface: get_index: 'data' not in data_JSON: url = " + str(url) )
			return

		self.AS_to_providers_dict[str(AS_number)] = list()

		data = data_JSON['data']
		for item in data:
			if "provider" in item['relationship']:
				self.AS_to_providers_dict[str(AS_number)].append( int(item['asn']) )

		self.AS_to_providers_dict[str(AS_number)] = list( sorted(self.AS_to_providers_dict[str(AS_number)]) )

		self.__save_data()
		return self.AS_to_providers_dict[str(AS_number)]


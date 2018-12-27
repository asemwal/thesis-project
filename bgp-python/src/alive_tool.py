import sys, copy
from printer import Printer
from time_tool import Time_Tool

class Alive_Tool():
	P = None
	TT = None

	def __init__( self, P = None, no_output = False ):
		if P is not None:
			self.P = P
		else:
			self.P = Printer()
			self.P.write( "[WARNING] Alive_Tool : __init__ : P is None", color = 'yellow', attrs = ['bold'] )
	
		if no_output is False:
			self.P.write( "Alive_Tool: Loading...", color = 'cyan', attrs=['bold'] )

		self.TT = Time_Tool( P = self.P )

	def check_alive( self, alive = None, time = None ):
		if alive is None:
			self.P.write_error( "Alive_Tool: check_alive: alive is None" )
			return None

		if time is None:
			self.P.write_error( "Alive_Tool: check_alive: time is None" )
			return None

		time = int(time)

		for x in range( 0, len(alive) ):
			temp_list = alive[x]
			length = len( temp_list )

			if len( temp_list ) == 0:
				continue
			elif length == 1:
				if time >= temp_list[0]:
					return True
			elif length > 1:
				if time >= temp_list[0] and time < temp_list[ length - 1 ]:
					if temp_list[0] != temp_list[ length - 1 ]:
						return True

		return False

	def get_delta_time( self, alive, time ):
		if alive is None:
			self.P.write_error( "Alive_Tool: get_delta_time: alive is None" )
			return None

		if time is None:
			self.P.write_error( "Alive_Tool: get_delta_time: time is None" )
			return None

		if self.check_alive( alive = alive, time = time ) is False:
			return -1

		temp_time = sys.maxsize

		for x in range( 0, len(alive) ):
			temp_list = alive[x]
			length = len( temp_list )

			if len( temp_list ) == 0:
				continue
			elif length == 1:
				if time >= temp_list[0]:
					if ( time - temp_list[0] ) < temp_time:
						temp_time = time - temp_list[0]
			elif length > 1:
				if time >= temp_list[0] and time < temp_list[ length - 1 ]:
					for y in range( 0, length - 1 ):
						delta_time = time - temp_list[y]
						if delta_time >= 0 and delta_time < temp_time:
							temp_time = delta_time

		return temp_time

	def update( self, alive = None, mode = None, time = None ):
		if alive is None:
			self.P.write_error( "Alive_Tool: update: alive is None" )
			return None

		if mode is None:
			self.P.write_error( "Alive_Tool: update: mode is None" )
			return None

		if time is None:
			self.P.write_error( "Alive_Tool: update: time is None" )
			return None

		if mode == "up":
			if len(alive) == 0:
				alive.append(list())
				alive[0].append( time )
			else:
				index = -1
				index_list = list()

				for x in range( 0, len(alive) ):
					temp_list = alive[x]
					length = len( temp_list )

					if temp_list[0] <= time and temp_list[ length - 1 ] >= time:
						index = x
						index_list.append(x)


				if index != -1:
					if len(index_list) == 2:
						alive_0 = alive[ index_list[0] ]
						alive_1 = alive[ index_list[1] ]

						if alive_0[ len(alive_0) - 1 ] == alive_1[ 0 ] or alive_1[ len(alive_1) - 1 ] == alive_0[ 0 ]:
							alive.pop( index_list[1] )

							for temp_time in alive_1:
								alive_0.append( temp_time )
								alive[ index_list[0] ] = alive_0
							
							return self.prettify( alive = alive )	

					if len( alive[index] ) == 1:
						return alive

					if alive[index][ len( alive[index] ) - 1 ] == time:
						temp_alive = alive[index]
						alive.pop( index )

						for temp_time in temp_alive:
							temp_list = [ temp_time ]
							alive.append(temp_list)

						return self.prettify( alive = alive )

					alive[index].append( time )
					return self.prettify( alive = alive )
				else:
					alive.append(list())
					alive[ len(alive) - 1 ].append( time )
					return self.prettify( alive = alive )

			return self.prettify( alive = alive )

		elif mode == "down":
			if len(alive) == 0:
				alive.append(list())
				alive[0].append( time )
				alive[0].append( time )
				return alive
			else:
				index = 0
				distance_1 = time - alive[0][0] 
				distance_2 = time - alive[0][len(alive[0])-1] 

				for x in range( 1, len(alive) ):
					temp_list = alive[x]
					temp_distance = time - temp_list[0]

					if temp_distance < distance_1 and temp_distance >= 0:
						distance_1 = temp_distance
						distance_2 = time - temp_list[len(temp_list)-1]
						index = x

				if distance_1 < 0:
					alive.append(list())
					alive[len(alive)-1].append( time )
					alive[len(alive)-1].append( time )
					alive = self.prettify( alive = alive )
					return alive

				if distance_1 == distance_2 and distance_1 == 0:
					if len( alive[index] ) == 1:
						alive[index].append( alive[index][0] )
						return self.prettify( alive = alive )

					return alive

				if distance_2 <= 0:
					if distance_2 == 0 and len(alive[index]) != 0:
						return alive

					alive[index].append(time)
					alive[index] = sorted( alive[index] )

					temp_index = alive[index].index( time )
					alive.append( alive[index][:temp_index+1] )
					alive.append( alive[index][temp_index+1:] )
					alive.pop(index) 

					if alive[ len(alive) - 2 ][ len(alive[ len(alive) - 2 ]) - 1 ] == alive[ len(alive) - 1 ][0]:
						if len( alive[ len(alive) - 1 ] ) > 1:
							alive[ len(alive) - 1 ].pop(0)

					if len( alive[ len(alive) - 1 ] ) == 1:
						alive[ len(alive) - 1 ].append( alive[ len(alive) - 1 ][0] )

					if len( alive[ len(alive) - 2 ] ) == 1:
						alive[ len(alive) - 2 ].append( alive[ len(alive) - 2 ][0] )

					return self.prettify( alive = alive )

				else:
					alive.append( list() )
					alive[ len(alive) -1 ].append( time )
					alive[ len(alive) -1 ].append( time )

					return self.prettify( alive = alive )
		return alive

	def prettify( self, alive = None ):
		if alive is None:
			self.P.write_error( "Alive_Tool: prettify: alive is None" )
			return None

		new_alive = list(alive)
		old_alive = None

		while new_alive != old_alive:
			old_alive = list(new_alive)
			new_alive = self.__prettify( alive = old_alive )
		return new_alive

	def __prettify( self, alive = None ):
		alive = sorted( alive )
		#print "before: " + str(alive)

		x = 0
		new_alive = list()

		while x < len(alive):
			if len(alive[x]) == 1 and x < len(alive) - 1 and len(alive[x+1]) != 1:
				temp_list = alive[x]
				temp_list.extend( alive[x+1] )
				new_alive.append( temp_list )
				x = x + 2
			else:
				new_alive.append( alive[x] )
				x = x + 1

		for x in range( 0, len(new_alive) ):
			if len( new_alive[x] ) > 2:
				new_alive[x] = list(sorted(set(new_alive[x])))

		#print "after: " + str(new_alive)
		return new_alive



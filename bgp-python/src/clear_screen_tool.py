import os

class Clear_Screen_Tool():
	def __init__( self ):
		return

	def clear_screen( self ):
		os.system('cls' if os.name == 'nt' else 'clear')
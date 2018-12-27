class String_Tool():
	def __init__( self ):
		return

	def get_words_after_substring( self, full_text = None, sub_text_before_words = None, numberOfWords = None ):
		full_text = str(full_text)
		sub_text_before_words = str(sub_text_before_words)

		if sub_text_before_words not in full_text:
			return list()

		index = full_text.index( sub_text_before_words )
		data = full_text[index + len(sub_text_before_words):]
		data = data.split("\"")

		if numberOfWords == 0:
			numberOfWords = len( data ) 

		if len( data ) < numberOfWords:
			return list()

		result = list()
		for x in range(0, numberOfWords):
			result.append( data[x] )

		return result
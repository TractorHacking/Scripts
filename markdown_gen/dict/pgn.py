class can_id:

	def __init__ (self, can_id, description, attributes):
		self.can_id = can_id.upper()
		self.pgn = self.get_pgn(can_id)
		self.description = description
		self.attributes = attributes

	def get_pgn(self, can_id):
		if(can_id[2].upper() == 'E'):
			return int(can_id[2:4], 16)
		else:
			return int(can_id[2:6], 16)

class pgn:
	
	def __init__ (self, pgn, description, attributes):
		self.pgn = pgn
		self.description = description
		self.attributes = attributes

class attribute:
	
	def __init__ (self, description, byte_offset, size):
		self.description = description
		self.byte_offset = byte_offset
		self.size = size
			

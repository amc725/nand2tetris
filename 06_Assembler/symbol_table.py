class symbol_table:
	def __init__(self):
		self.st= {
			"SP":0,
			"LCL":1,
			"ARG":2,
			"THIS":3,
			"THAT":4,
			"R0":0,
			"R1":1,
			"R2":2, 
			"SCREEN":16384,
			"KBD":24576,
			}
	
	def addEntry(self, symbol, address):
		self.st[symbol] = address
			
	def contains(self, symbol):
		if symbol in self.st:
			return True
		else:
			return False

	def GetAddress(self, symbol):
		address = self.st[symbol]
		address = int(address)
		return address

#a = symbol_table()
#print a.contains("LCL")
#a.addEntry("asdf", 6)
#print a.st
#print a.GetAddress("LCL")


class SymbolTable:
	def __init__(self):		
		self.globalScopeStatus = True 
		self.classTable = []
		self.subroutineTable = []
		self.counter = { "STATIC" : 0, "FIELD" : 0, "ARG" : 0, "VAR" : 0}

	def constructor(self):
		self.globalScopeStatus = True 
		self.classTable = []
		self.subroutineTable = []
		for type,index in self.counter.items(): #reset dict "counter"
			self.counter[type] = 0

	def startSubroutine(self):
		self.globalScopeStatus = False
		self.subroutineTable = []
		self.counter["ARG"] = 0
		self.counter["VAR"] = 0

	def define(self, name, type, kind):
		if self.globalScopeStatus == True:
			self.classTable.append((name, type, kind, self.counter[kind]))
			self.counter[kind] += 1
		else:
			self.subroutineTable.append((name, type, kind, self.counter[kind]))
			self.counter[kind] += 1
		

	def varCount(self, kind):
		return self.counter[kind]

	def kindOf(self, name):
		kind = "NONE"
		if self.globalScopeStatus == False:
			for i in self.subroutineTable:
				if (i[0] == name):
					kind = i[2]
		elif self.globalScopeStatus == True:
			for i in self.classTable:
				if (i[0] == name):
					kind = i[2]

		return kind
	
	def typeOf(self, name):
		type = "NONE"
		if self.globalScopeStatus == False:
			for i in self.subroutineTable:
				if (i[0] == name):
					type = i[1]
		elif self.globalScopeStatus == True:
			for i in self.classTable:
				if (i[0] == name):
					type = i[1]
		return type

	def indexOf(self, name):
		index = "NONE"
		if self.globalScopeStatus == False:
			for i in self.subroutineTable:
				if (i[0] == name):
					index = i[3]
		elif self.globalScopeStatus == True:
			for i in self.classTable:
				if (i[0] == name):
					index = i[3]

		return index

	def typeOfFallback(self, name):
		type = ""
		if self.globalScopeStatus == False:
			for i in self.subroutineTable:
				if (i[0] == name):
					type = i[1]
		if (self.globalScopeStatus == True or type == ""):
			for i in self.classTable:
				if (i[0] == name):
					type = i[1]
		if (type == ""):
			print("Error variable \"" + name + "\" not found"  )
		return type
	
	def kindOfFallback(self, name):
		kind = ""
		if self.globalScopeStatus == False:
			for i in self.subroutineTable:
				if (i[0] == name):
					kind = i[2]
		if (self.globalScopeStatus == True or kind == ""):
			for i in self.classTable:
				if (i[0] == name):
					kind = i[2]
		if (kind == ""):
			print("Error variable \"" + name + "\" not found"  )
		return kind

	def indexOfFallback(self, name):
		index = ""
		if self.globalScopeStatus == False:
			for i in self.subroutineTable:
				if (i[0] == name):
					index = i[3]
		if (self.globalScopeStatus == True or index == ""):
			for i in self.classTable:
				if (i[0] == name):
					index = i[3]
		if (index == ""):
			print("Error variable \"" + name + "\" not found"  )
		return index

    
	def debugTable(self, subroutine, className):
		print("------------------------------------------")
		print(className + " " + subroutine)
		print(className)
		for i in self.classTable:
			print (i)
		print("\r\n")
		print(subroutine)
		for i in self.subroutineTable:
			print (i)
		print("--------------------------------------------")

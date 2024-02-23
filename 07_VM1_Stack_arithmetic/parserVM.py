import re
class parserVM:
	def __init__(self, input_file):
		self.filename = input_file.rstrip(".vm")
		self.file = open(input_file, "r")
		self.commands = 0
		self.list = ["Filler_for_1_index"]
		for i in self.file:
			if i != "\r\n" and i != "\n" and i[0] != "/":
				self.commands += 1
				self.list.append(i)
				print("COMANDO  " + i)
		self.linea_actual = 0
		self.arithmetic = [ "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not" ]

	def hasMoreCommands(self):
		if self.linea_actual < self.commands:
			return True
		else:
			return False

	def advance(self):
		self.linea_actual += 1
		self.comando_actual = self.list[self.linea_actual]
		self.comando_actual = self.comando_actual.lstrip()
		self.comando_actual = self.comando_actual.rstrip("\r\n")

	def commandType(self):		
		if re.search("^push", self.comando_actual):
			return "C_PUSH"
		elif re.search("^pop", self.comando_actual):
			return "C_POP"
		elif self.comando_actual in self.arithmetic:
			return "C_ARITHMETIC"
		elif re.search("^if", self.comando_actual):
			return "C_IF"
		elif re.search("^function", self.comando_actual):
			return "C_FUNCTION"
		elif re.search("^return", self.comando_actual):
			return "C_RETURN"
		elif re.search("^call", self.comando_actual):
			return "C_CALL"
		else:
			return "Error"

	def arg1(self):
		arg1 = self.comando_actual.split()
		if len(arg1) == 1:
			return self.comando_actual
		else:
			return arg1[1]

	def arg2(self):
		arg2 = self.comando_actual.split()
		arg2 = arg2[2]
		arg2 = int(arg2)
		return arg2
	

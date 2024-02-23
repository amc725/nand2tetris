import re
class parser:
	def __init__(self, input_file):
		self.file = open(input_file, "r")
		self.output_name = input_file.rstrip(".asm") + ".hack"
		self.output = open(self.output_name, "w")
		#contar lineas y crear lista
		self.commands = 0
		self.list = ["filler_for_1_index"]
		for i in self.file:
			#get rid of blank lines and comments with an arbitraty number of whitespaces preceding
			if re.match(r'\s+', i) == None  and re.match(r'\s*\/\/', i) == None: 
				self.commands += 1
				#strip side comments
				command = re.sub(r"//.*", "", i)
				#strip end of line
				command = command.rstrip()
				self.list.append(command)
				print(command)
		#linea_actual
		self.linea_actual = 0

	def hasMoreCommands(self):
		if self.linea_actual < self.commands:
			return True
		else:
			return False

	def advance(self):
			self.linea_actual += 1
			self.current_command = self.list[self.linea_actual]

	def commandType(self):
		if (self.current_command[0] == "@"):
			return "A_COMMAND"
		elif (self.current_command[0] == "("):
			return "L_COMMAND"
		else:
			return "C_COMMAND"

	def symbol(self):
			symbol = self.current_command
			if symbol[0] == "@":	
				symbol = symbol.lstrip("@")
				return symbol
			elif symbol[0] == "(":
				symbol = symbol.lstrip("(")
				#strip newline and ")"
				symbol = symbol.rstrip()
				symbol = symbol.rstrip(")")
				return symbol

	def dest(self):
		if "=" in self.current_command:
			dest = self.current_command.split("=")
			return dest[0].rstrip()
		else:
			return "NULL"
			
	def comp(self):
		comp = self.current_command 
		comp = re.sub(r'.*=', '', comp)
		comp = re.sub(r';.*', '', comp)
		return comp
	
	def jump(self):
		if ";" in self.current_command:
			jump = self.current_command.split(";")
			jump = jump[1]
			jump = jump.rstrip()
			return jump
		else:
			return "NULL"

#a=parser("Fill_commented.asm")


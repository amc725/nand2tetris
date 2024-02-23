from parser import parser
from symbol_table import symbol_table
import code
import re
import sys



class assembler:
	def __init__(self, filename):
		self.filename = filename
		self.table = symbol_table()
		self.ROM_address = 0
		self.variable_address = 15
		
	def first_pass(self):
		assembler = parser(self.filename)
		while assembler.hasMoreCommands() == True:
			assembler.advance()
			type = assembler.commandType()	
			if type == "A_COMMAND":
				self.ROM_address += 1
			elif type == "L_COMMAND":
				command = assembler.symbol()
				self.table.addEntry(command, self.ROM_address)
			elif type == "C_COMMAND":
				self.ROM_address += 1
	
	def second_pass(self):
		assembler = parser(self.filename)
		while assembler.hasMoreCommands() == True:
			assembler.advance()
			type = assembler.commandType()
			if type == "A_COMMAND":
				command = assembler.symbol()
				if re.match("^[0-9]",command):
					command = int(command)
				#variable or goto
				elif re.match("^[a-z]",command) or re.match("^[A-Z]",command):
					if self.table.contains(command) == True:
						command = self.table.GetAddress(command)
						command = int(command)
					else:
						self.variable_address += 1
						self.table.addEntry(command, self.variable_address)
						command = int(self.variable_address)
						
				#int to binary
				command = bin(command)
				command = command.lstrip("0b")
				command = command.zfill(16)
				assembler.output.write(command + "\n")
			elif type == "L_COMMAND":
				pass	
			elif type == "C_COMMAND":
				command_dest = assembler.dest()
				command_dest = code.dest(command_dest)
				command_comp = assembler.comp()
				command_comp = code.comp(command_comp)
				command_jump = assembler.jump()
				command_jump = code.jump(command_jump)
				command = command_comp + command_dest + command_jump
				assembler.output.write(command + "\n")
			else:
				command = assembler.current_command
				print("Error linea" + " " + str(assembler.linea_actual))
				print(assembler.current_command)
				break

def main():
	archivo = sys.argv[1]
	a = assembler(archivo)
	a.first_pass()
	a.second_pass()

main()		
			

		




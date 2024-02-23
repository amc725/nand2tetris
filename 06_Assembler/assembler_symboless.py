from parser import parser
import code
import re
filename = "Fill"
assembler = parser(str(filename + ".asm"))
while assembler.hasMoreCommands() == True:
	assembler.advance()
	type = assembler.commandType()
	if type == "A_COMMAND" :
		command = assembler.symbol()
		if re.match("^[0-9]", command):
			command = int(command)
			command = bin(command)
			command = command.lstrip("0b")
		else:
			command = "variable"
	elif type == "C_COMMAND":
		command_dest = assembler.dest()
		command_dest = code.dest(command_dest)
		command_comp = assembler.comp()
		command_comp = code.comp(command_comp)
		command_jump = assembler.jump()
		command_jump = code.jump(command_jump)
		command = command_dest + command_comp + command_jump
	else:
		command = assembler.current_command
		print "Error linea" + " " + str(assembler.linea_actual)
		print assembler.current_command
		break
	command = command.zfill(15)
	assembler.output.write(command + "\n")


assembler.file.close()
assembler.output.close()
	
		
	
		

		




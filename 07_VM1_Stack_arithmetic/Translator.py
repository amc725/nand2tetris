from codeWriterVM import codeWriterVM
from parserVM import parserVM
import sys
import os

class Translator:
	def __init__(self, filename):
		self.filename = filename
		self.directory = ""

	
	def _main(self):
		input_file = self.filename

		input_file = input_file.rstrip(".vm");

		parser = parserVM(input_file + ".vm")
		codeWriter = codeWriterVM(input_file + ".asm")

		#Initialize stack
		codeWriter.output_file.write("@256" + "\n")
		codeWriter.output_file.write("D=A" + "\n")
		codeWriter.output_file.write("@SP" + "\n")
		codeWriter.output_file.write("M=D" + "\n")
		
		while parser.hasMoreCommands() == True:
			parser.advance()
			if parser.commandType() == "C_PUSH" or parser.commandType() == "C_POP":
				codeWriter.output_file.write("//" + parser.commandType() + "\n")
				codeWriter.WritePushPop(parser.commandType(), parser.arg1(), parser.arg2())
				codeWriter.output_file.write("//End of" + parser.commandType() + "\n")
			elif parser.commandType() == "C_ARITHMETIC":
				codeWriter.output_file.write("//" + parser.commandType() + "\n")
				codeWriter.writeArithmetic(parser.arg1())
				codeWriter.output_file.write("//End of" + parser.commandType() + "\n")
			elif parser.commandType() == "Error":
				print ("Error")
def main():
	archivo = sys.argv[1]
	t = Translator(archivo)
	t._main()


main()	
				
		
	
	
	

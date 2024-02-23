from codeWriterVM import codeWriterVM
from parserVM import parserVM
import sys
import os


class Translator:
	def __init__(self, filename):
		self.iterator = 0		        	#iterator 
		self.num_of_files = 0		        #number of ".jack" files
		self.filename = filename            
		self.dir_ls = []		            #list of ".jack" files
		self.input_filename = ""
		self.directory = ""
		self.isadirectory = False


	def _main(self):
		if os.path.isdir(self.filename) == True:
			#get last subdirectory to name the assembler file
			self.directory = os.path.abspath(self.filename)
			self.input_filename = self.directory.split("/")
			self.input_filename_length = len(self.input_filename)
			self.input_filename = self.input_filename[self.input_filename_length - 1]
			
			self.isadirectory = True
			#create a list with all files in the directory
			pre_dir_ls = os.listdir(self.directory) 	
			#count number of files and save a list with the ones that have the ".vm" extension
			for i in pre_dir_ls:
				temp_filename = i
				temp_filename = temp_filename.split(".")
				if temp_filename[1] == "vm":
					self.num_of_files +=1
					self.dir_ls.append(temp_filename[0])
			#change the working directory to the folder
			os.chdir(self.directory)
		else:
			#argument is a file
			self.input_filename = self.filename.rstrip(".vm")
			self.num_of_files = 1
		

		codeWriter = codeWriterVM(self.input_filename + ".asm")
		#Initialize stack
		codeWriter.writeInit()

		while self.iterator < self.num_of_files:
			current_filename = self.get_current_filename()
			print(current_filename)
			parser = parserVM(current_filename)
			codeWriter.setFileName(current_filename)
			while parser.hasMoreCommands() == True:
				parser.advance()
				if parser.commandType() == "C_PUSH" or parser.commandType() == "C_POP":
					codeWriter.WritePushPop(parser.commandType(), parser.arg1(), parser.arg2())
				elif parser.commandType() == "C_ARITHMETIC":
					codeWriter.writeArithmetic(parser.comando_actual)
				elif parser.commandType() == "C_IF":
					codeWriter.writeIf(parser.arg1())
				elif parser.commandType() == "C_FUNCTION":
					codeWriter.writeFunction(parser.arg1(), parser.arg2())
				elif parser.commandType() == "C_RETURN":
					codeWriter.writeReturn()
				elif parser.commandType() == "C_CALL":
					codeWriter.writeCall(parser.arg1(),parser.arg2())
				elif parser.commandType() == "C_LABEL":
					codeWriter.writeLabel(parser.arg1())
				elif parser.commandType() == "C_GOTO":
					codeWriter.writeGoto(parser.arg1())
				elif parser.commandType() == "Error":
					print("Error linea" + " " + str(parser.linea_actual) + "\n")
					print(parser.comando_actual)
					break #the first loop will continue to run
			self.iterator+=1
		codeWriter.close()
		
		
	def get_current_filename(self):
		if self.isadirectory == True:
			return self.dir_ls[self.iterator] 
		else:
			return self.input_filename	
		


def main():
	archivo = sys.argv[1]
	t = Translator(archivo)
	t._main()


main()	
				
		
	
	
	

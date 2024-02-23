from CompilationEngine import CompilationEngine
import sys
import os


class JackCompiler:
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
			self.isadirectory = True
			self.directory = self.filename
			#create a list with all files in the directory
			pre_dir_ls = os.listdir(self.directory) 	
			#count number of files and save a list with the ones that have the ".jack" extension
			for i in pre_dir_ls:
				print(i)
				temp_filename = i
				temp_filename = temp_filename.split(".")
				if temp_filename[1] == "jack":
					self.num_of_files +=1
					self.dir_ls.append(temp_filename[0])
			#change the working directory to the folder
			os.chdir(self.directory)
		else:
			#argument is a file
			self.input_filename = self.filename.rstrip(".jack")
			self.num_of_files = 1
		
		print(self.directory)
		print(self.input_filename)

		

		while self.iterator < self.num_of_files:
			current_filename = self.get_current_filename()
			compEngine = CompilationEngine(current_filename)
			compEngine.Tokenizer.remove_comments()
			compEngine.Tokenizer.getTokens()
			#compEngine.Tokenizer.debugTokens()
			compEngine.compileClass()
			self.iterator += 1
		
		
	def get_current_filename(self):
		if self.isadirectory == True:
			return self.dir_ls[self.iterator] 
		else:
			return self.input_filename	
		


def main():
	archivo = sys.argv[1]
	compiler = JackCompiler(archivo)
	compiler._main()


main()	
				
		
	
	
	

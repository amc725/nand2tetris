class VMWriter:
	def __init__(self, input_file):
		#initialize output
		self.outputName = input_file + ".test.vm"
		self.outputFile = open(self.outputName, "w")
    
	def writePush(self, segment, index):
		self.outputFile.write("push " + segment + " " + str(index) + "\r\n")

	def writePop(self, segment, index):
		self.outputFile.write("pop " + segment + " " + str(index) + "\r\n")

	def writeArithmetic(self, command):
		self.outputFile.write(command + "\r\n")
	
	def writeLabel(self, label):
		self.outputFile.write("label " + label + "\r\n")

	def writeGoto(self, label):
		self.outputFile.write("goto " + label + "\r\n")

	def writeIf(self, label):
		self.outputFile.write("if-goto " + label + "\r\n")

	def writeCall(self, name, nArgs):
		self.outputFile.write("call " + name + " " + str(nArgs) + "\r\n")

	def writeFunction(self, name, nLocals):
		self.outputFile.write("function " + name + " " + str(nLocals) + '\r\n')

	def writeReturn(self):
		self.outputFile.write("return\r\n")
	
	def close(self):
		self.outputFile.close()


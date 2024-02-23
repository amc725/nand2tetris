import re
class codeWriterVM:
	def __init__(self, output_file):
		self.output_file = open(output_file, "w")
		self.name = output_file.split(".")
		self.name = self.name[0]
		self.symbols = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
		self.label_counter = 0 #(END1)...(END8)
	def setFileName(self, fileName):
		############
		pass

	def writeArithmetic(self, comando):
		self.output_file.write("//" + comando + "\n")
		#binary A=&x D=y
		if comando == "add":
			self.binary()
			self.output_file.write("M=M+D" + "\n")
		elif comando == "sub":
			self.binary()
			self.output_file.write("M=M-D" + "\n")
		elif comando == "neg":
			self.unary()
			self.output_file.write("M=-M" + "\n")
		elif comando == "eq":
			self.compare("D;JEQ")
		elif comando == "gt":
			self.compare("D;JGT")		
		elif comando == "lt":
			self.compare("D;JLT")		
		elif comando == "and":
			self.binary()
			self.output_file.write("M=D&M" + "\n")
		elif comando == "or":
			self.binary()
			self.output_file.write("M=D|M" + "\n")
		elif comando == "not":
			self.unary()
			self.output_file.write("M=!M" + "\n")
		else:
			print("Error")

	def WritePushPop(self, command, segment, index):
		self.output_file.write("//" + command + " " + segment + " " + str(index) + "\n")
		if command == "C_PUSH" and (segment == "this" or segment == "that" or segment == "argument" or segment == "local"):
			self.output_file.write("@" + str(index) + "\n")		#A=index
			self.output_file.write("D=A" + "\n")			#D=index
			self.output_file.write("@" + self.symbols[segment] + "\n") 	#@LCL
			self.output_file.write("A=M" + "\n")			#A=M[LCL]
			self.output_file.write("A=A+D" + "\n")			#A=local+index
			self.output_file.write("D=M" + "\n")			#D=M[local+index]
			self.d_into_stack()
		if command == "C_PUSH" and segment == "temp":
			suma = index + 5
			self.output_file.write("@" + str(suma) + "\n")
			self.output_file.write("D=M" + "\n")
			self.d_into_stack()
		if command == "C_PUSH" and segment == "pointer":
			suma = index + 3
			self.output_file.write("@" + str(suma) + "\n")
			self.output_file.write("D=M" + "\n")
			self.d_into_stack()			
		elif command == "C_PUSH" and segment == "constant":
			self.output_file.write("@" + str(index) + "\n")
			self.output_file.write("D=A" + "\n")
			self.d_into_stack()
		elif command == "C_POP" and (segment == "this" or segment == "that" or segment == "argument" or segment == "local"):
			#temporal_pointer=@R5
			self.output_file.write("@" + str(index) + "\n")	#A=index
			self.output_file.write("D=A" + "\n")		#D=index
			self.output_file.write("@" + self.symbols[segment] + "\n") # A=segment
			self.output_file.write("D=D+M" + "\n")		#D=index +M[local]
			self.output_file.write("@R5" + "\n")		#temporal_pointer to [local + index]
			self.output_file.write("M=D" + "\n")		#temporal_pointer to [local + index]
			self.pop_from_stack() 				#D = stack
			self.output_file.write("@R5" + "\n")		#A=temporal_pointer
			self.output_file.write("A=M" + "\n")		#A=[local+index]
			self.output_file.write("M=D" + "\n")		#M[local+index]=stack
		elif command == "C_PUSH" and segment == "static":
			self.output_file.write("@" + self.name + "." + str(index) + "\n")	
			self.output_file.write("D=M" + "\n")
			self.d_into_stack()
		elif command == "C_POP" and segment == "pointer":
			suma = index + 3
			self.pop_from_stack()
			self.output_file.write("@" + str(suma) + "\n")
			self.output_file.write("M=D" + "\n")
		elif command == "C_POP" and segment == "temp":
			suma = index + 5
			self.pop_from_stack()
			self.output_file.write("@" + str(suma) + "\n")
			self.output_file.write("M=D" + "\n")
		elif command == "C_POP" and segment == "static":
			self.pop_from_stack()
			self.output_file.write("@" + self.name + "." + str(index) + "\n")
			self.output_file.write("M=D" + "\n")
			

	def d_into_stack(self):
		self.output_file.write("@SP" + "\n")			#@SP
		self.output_file.write("A=M" + "\n")			#A=M[SP]
		self.output_file.write("M=D" + "\n")			#M[SP]=D
		self.output_file.write("@SP" + "\n")			#@SP
		self.output_file.write("M=M+1" + "\n")			#@SP++

	def pop_from_stack(self):
		self.output_file.write("@SP" + "\n")
		self.output_file.write("M=M-1" + "\n")
		self.output_file.write("A=M" + "\n")
		self.output_file.write("D=M" + "\n")
		#clean stack
		self.output_file.write("M=0" + "\n")

	def unary(self):
		self.output_file.write("@SP" + "\n")
		self.output_file.write("A=M-1" + "\n")

	def binary(self):
		# A=&x  D=y 
		#top of the stack is "y" and is stored into D-register
		#A-register ends pointing to x, so x-y is "M-D"
		self.output_file.write("@SP" + "\n")	
		self.output_file.write("M=M-1" + "\n")	#@SP-=1
		self.output_file.write("A=M" + "\n")	#A=*y
		self.output_file.write("D=M" + "\n")	#D=y
		self.output_file.write("@SP" + "\n")	#
		self.output_file.write("A=M-1" + "\n") 	#A=*x

	def compare(self, comparison):
		#top of the stack is "y"
		#D=y
		self.label_counter += 1
		self.output_file.write("@SP" + "\n")		#@SP
		self.output_file.write("M=M-1" + "\n")		#SP-=1 decrease stack_pointer
		self.output_file.write("A=M" + "\n")		#A=&y
		self.output_file.write("D=M" + "\n")		#D=y
		#clean stack
		self.output_file.write("M=0" + "\n")
		#
		self.output_file.write("A=A-1" + "\n")		#A=&x
		self.output_file.write("A=M" + "\n")		#A=x
		self.output_file.write("D=A-D" + "\n")		#D=x-y
		self.output_file.write("@SP" + "\n")		#@SP
		self.output_file.write("A=M-1" + "\n") 		#A=&x
		self.output_file.write("M=-1" + "\n")		#default "x" to TRUE
		self.output_file.write("@END" + str(self.label_counter) + "\n")		#jump to END
		self.output_file.write(comparison + "\n")	#if condition is TRUE jump to end, if FALSE set "x" to false
		self.output_file.write("@SP" + "\n")			#@SP
		self.output_file.write("A=M-1" + "\n")			#A=&x
		self.output_file.write("M=0" + "\n")			#set "x" to FALSE
		self.output_file.write("(END" + str(self.label_counter) + ")" + "\n")		#END

	def writeLabel(self,label):
		self.output_file.write("//LABEL" + "\n")
		self.output_file.write("(" + label + ")" + "\n")
	
	def writeGoto(self,label):
		self.output_file.write("//GOTO" + "\n")
		self.output_file.write("@" + label + "\n")
		self.output_file.write("0;JMP" + "\n")

	def writeIf(self, label):
		self.output_file.write("//IF-GOTO" + "\n")
		self.pop_from_stack()
		self.output_file.write("@" + label + "\n")
		self.output_file.write("D;JNE" + "\n")		
			
	def close(self):
		self.output_file.close()
		


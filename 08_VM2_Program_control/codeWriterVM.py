import re
class codeWriterVM:
	def __init__(self, output_file):
		self.output_file = open(output_file, "a+")
		self.symbols = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
		self.label_compare_counter = 0 #(END1)...(END8)
		self.return_counter = 0 #(RETURN1)...(RETURN8)

	def setFileName(self, fileName):
		self.current_filename = fileName.rstrip(".vm")

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
			self.output_file.write("@" + self.current_filename + "." + str(index) + "\n")	
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
			self.output_file.write("@" + self.current_filename + "." + str(index) + "\n")
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
		self.label_compare_counter += 1
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
		self.output_file.write("@END" + str(self.label_compare_counter) + "\n")		#jump to END
		self.output_file.write(comparison + "\n")	#if condition is TRUE jump to end, if FALSE set "x" to false
		self.output_file.write("@SP" + "\n")			#@SP
		self.output_file.write("A=M-1" + "\n")			#A=&x
		self.output_file.write("M=0" + "\n")			#set "x" to FALSE
		self.output_file.write("(END" + str(self.label_compare_counter) + ")" + "\n")		#END

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

	def writeCall(self, functionName, numArgs):
		self.output_file.write("//CALL" + " " + functionName + " " + str(numArgs) + "\n")
		self.return_counter += 1
		#push return address
		self.output_file.write("\t" + "//PUSH RETURN ADDRESS" + "\n")
		self.output_file.write("@" + "RETURN" + str(self.return_counter) + "\n")
		self.output_file.write("D=A" + "\n")
		self.d_into_stack()
		#push LCL
		self.output_file.write("\t" + "//PUSH LCL" + "\n")
		self.output_file.write("@LCL" + "\n")
		self.output_file.write("D=M" + "\n")
		self.d_into_stack()
		#push ARG
		self.output_file.write("\t" + "//PUSH ARG" + "\n")
		self.output_file.write("@ARG" + "\n")
		self.output_file.write("D=M" + "\n")
		self.d_into_stack()
		#push THIS
		self.output_file.write("\t" + "//PUSH THIS" + "\n")
		self.output_file.write("@THIS" + "\n")
		self.output_file.write("D=M" + "\n")
		self.d_into_stack()
		#push THAT
		self.output_file.write("\t" + "//PUSH THAT" + "\n")
		self.output_file.write("@THAT" + "\n")
		self.output_file.write("D=M" + "\n")
		self.d_into_stack()
		#reposition ARG = SP - n -5
		self.output_file.write("\t" + "//Reposition ARG" + "\n")
		n = numArgs + 5
		self.output_file.write("@SP" + "\n")
		self.output_file.write("D=M" + "\n")
		self.output_file.write("@" + str(n) + "\t" + "//numArgs + 5" + "\n")
		self.output_file.write("D=D-A" + "\n")
		self.output_file.write("@ARG" + "\n")
		self.output_file.write("M=D" + "\n")
		#reposition LCL
		self.output_file.write("\t" + "//Reposition LCL" + "\n")
		self.output_file.write("@SP" + "\n")
		self.output_file.write("D=M" + "\n")
		self.output_file.write("@LCL" + "\n")
		self.output_file.write("M=D" + "\n")
		#transfer control
		self.output_file.write("\t" + "//Transfer control" + "\n")
		self.writeGoto(functionName)
		#label for the return address
		self.output_file.write("\t" + "//Label for return address" + "\n")
		self.writeLabel(str("RETURN" + str(self.return_counter)))
		
	def writeReturn(self):
		self.output_file.write("//RETURN" + "\n")
		#FRAME = R5
		#RET = R6
		#FRAME is a temporary variable
		self.output_file.write("\t" + "//Save frame adress in temp variable" + "\n")
		self.output_file.write("@LCL" + "\n")
		self.output_file.write("D=M" + "\n")
		self.output_file.write("@R5" + "\n")	#FRAME
		self.output_file.write("M=D" + "\n")	
		#save return address in a temp variable 
		self.output_file.write("\t" + "//Save return adress in a temp variable" + "\n")
		self.output_file.write("@R5" + "\n")
		self.output_file.write("D=M" + "\n")
		self.output_file.write("@5" + "\n")
		self.output_file.write("D=D-A" + "\n") #D=&RET
		self.output_file.write("A=D" + "\n")
		self.output_file.write("D=M" + "\n")
		self.output_file.write("@R6" + "\n")	#RET
		self.output_file.write("M=D" + "\n")
		#Return value for caller
		self.output_file.write("\t" +"//Return value" + "\n")
		self.pop_from_stack()
		self.output_file.write("@ARG" + "\n")
		self.output_file.write("A=M" + "\n")
		self.output_file.write("M=D" + "\n")
		#restore SP for caller,  SP=ARG+1
		self.output_file.write("\t" +"//Restore SP" + "\n")
		self.output_file.write("@ARG" + "\n")
		self.output_file.write("D=M" + "\n")
		self.output_file.write("@SP" + "\n")
		self.output_file.write("M=D+1" + "\n")
		#restore THAT of caller function
		self.output_file.write("\t" +"//Restore THAT" + "\n")
		self.restore("THAT")
		#restore THIS of caller function
		self.output_file.write("\t" +"//Restore THIS" + "\n")
		self.restore("THIS")
		#restore ARG of caller function
		self.output_file.write("\t" +"//Restore ARG" + "\n")
		self.restore("ARG")
		#restore LCL of caller function
		self.output_file.write("\t" +"//Restore LCL" + "\n")
		self.restore("LCL")
		#GOTO the return-address
		self.output_file.write("\t" +"//Jump to return adress" + "\n")
		self.output_file.write("@R6" + "\n")
		self.output_file.write("A=M" + "\n")
		self.output_file.write("0;JMP" + "\n")

	def restore(self,segment):
		self.output_file.write("\t" + "//Restore" + " " + segment + "\n")
		self.output_file.write("@R5" + "\n")		#A=R5=ARG=FRAME
		self.output_file.write("M=M-1" + "\n")		#M[R5]-=1  	FRAME-1...FRAME-4
		self.output_file.write("A=M" + "\n")		#A=M[R5]	
		self.output_file.write("D=M" + "\n")		#D=M[A]		D=M[FRAME-1]...D=M[FRAME-5]
		self.output_file.write("@" + segment + "\n")	#@LCL...THAT
		self.output_file.write("M=D" + "\n")		#LCL...THAT=D

	def writeFunction(self, functionName, numLocals):
		self.output_file.write("//FUNCTION" + " " + functionName + " " + str(numLocals) + "\n")
		self.writeLabel(functionName)
		i = numLocals
		self.output_file.write("\t" + "//Initialize LOCAL variables to zero" + "\n")
		self.output_file.write("D=0" + "\n")
		while i > 0:
			self.d_into_stack()
			i -= 1

	def writeInit(self):
		self.output_file.write("//INIT" + "\n")
		#Initialize stack
		self.output_file.write("@256" + "\n")
		self.output_file.write("D=A" + "\n")
		self.output_file.write("@SP" + "\n")
		self.output_file.write("M=D" + "\n")
		#Call sys.init
		self.writeCall("Sys.init", 0)
	
	def close(self):
		self.output_file.close()
		


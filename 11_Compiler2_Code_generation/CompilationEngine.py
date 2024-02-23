#print("Error malformed expression" + " " + self.tokens_list[self.current_line - 1] + self.token + self.tokens_list[self.current_line + 1])		
import re
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from Tokenizer import Tokenizer
class CompilationEngine:
	def __init__(self, input_file):
		#initialize objects
		self.Table = SymbolTable()
		self.Writer = VMWriter(input_file)
		self.Tokenizer = Tokenizer(input_file)

		#ALIASES
		self.advance = self.Tokenizer.advance		#self.advance() has an optional argument "expected" that output an error if the returned token doesn't match 
		self.peek = self.Tokenizer.peek
		self.peekType = self.Tokenizer.peekType

		#JACK compiler variables
		self.statements = ("let", "if", "while", "do", "return")
		self.op = ('+', '-', '*', '&', '/', '|', '=', '<', '>')
		self.unaryOp = ('-', '~')
		self.keywords2 = ('true', 'false', 'null', 'this')
		self.counter = 0
		self.className = ""
		self.builtinFunctions = ("Keyboard", "Sys", "Memory", "Output", "Screen", "Math")

		#compileIF()
		self.maxIFcounter = -1
		#compileWHILE()
		self.maxWHILEcounter = -1

	def compileClass(self):
		self.advance()								#reach keyword "class"
		self.className = self.advance()				#reach identifier "class_name"
		self.advance("{")							#reach symbol "{"
		if (self.peek() == "field" or self.peek() == "static"):	#check for next statement
			self.CompileClassVarDec()
		while (self.peek() == "constructor" or self.peek() == "method" or self.peek() == "function"):
			self.CompileSubroutine()
		self.advance("}")							#reach symbol "}"			
		self.Writer.close()							#END
		

	
	def CompileClassVarDec(self):
		while (self.peek() == "field" or self.peek() == "static"):
			kind = self.advance(); kind = kind.upper()	#reach keyword kind "field|static"
			type = self.advance()						#reach keyword "type" 
			name = self.advance()						#reach identifier "name" 
			self.Table.define(name, type, kind)			
			while(self.peek() == ","):					#handle multiple declarations at once
				self.advance()							#reach symbol ","
				name = self.advance()					#reach identifier "name"
				self.Table.define(name, type, kind) 	
			self.advance(";")							#reach symbol ";"


	def CompileSubroutine(self):
		while(self.peek() == "constructor" or self.peek() == "method" or self.peek() == "function"):
			self.maxIFcounter = -1
			self.maxWHILEcounter = -1
			#"constructor Name new" | "function type name" | "method type name"  
			subroutine = self.advance()								#reach keyword "method|constructor|function"
			constructor_name = self.advance()						#reach keyword "type" or identifier "constructor_name"
			identifier_name = self.advance()						#reach identifier "name"
			self.Table.startSubroutine()						
			#object reference as first argument if it's a method
			if subroutine == "method":	
				self.Table.define("this", self.className, "ARG")
			#compile parameters
			if (self.peek() == "("):
				self.compileParameterList()
			self.advance("{")				#reach symbol "{" 
			#check if there is variable declarations
			if (self.peek() == "var"):	
				self.compileVarDec()
			nVars = self.Table.varCount("VAR")			#get number of local variables
			#determine subroutine name
			if (subroutine == "constructor"):
				name = constructor_name + ".new"
			else: #identifier == method|function
				name = self.className + "." + identifier_name
			self.Writer.writeFunction(name, nVars)				#declare function VM "function Main.main 5" 
			#set pointers
			if (subroutine == "method"):
				self.Writer.writePush("argument", 0)			
				self.Writer.writePop("pointer", 0)
			elif (subroutine == "constructor"):
				nVars = self.Table.varCount("FIELD") 		
				self.Writer.writePush("constant", nVars)
				self.Writer.writeCall("Memory.alloc", 1)
				self.Writer.writePop("pointer", 0)
			self.compileStatements()								#compile statements
			self.advance("}")										#reach "}" symbol
			self.Table.debugTable((constructor_name + " " + identifier_name), self.className)


	def compileParameterList(self):
		self.advance()										#reach symbol "("
		if (self.peek() == ")"):							#check for empty p_list
			pass
		else:
			type = self.advance()							#reach keyword|identifier "type"
			name = self.advance()							#reach identifier "name"
			kind = "ARG"									#set argument kind 
			self.Table.define(name, type, kind)
			while(self.peek() == ","):						#check for multiple parameters
				self.advance()								#reach symbol ","
				type = self.advance()						#reach keyword "type"
				name = self.advance()						#reach identifier "name"
				self.Table.define(name, type, kind)
		self.advance(")")										#reach symbol ")"

	def compileVarDec(self):
		while (self.peek() == "var"):
			kind = self.advance(); kind = kind.upper()		#reach keyword "var"
			type = self.advance()							#reach keyword type "int|boolean..."
			name = self.advance()							#reach idetifier "name"
			self.Table.define(name, type, kind)	
			while (self.peek() == ","):						#check if there is multiple declarations at once
				self.advance()								#reach symbol ","
				name = self.advance()						#reach identifier "name"
				self.Table.define(name, type, kind)	
			self.advance(";")								#reach symbol ";"

	def compileStatements(self):
		while(self.peek() in self.statements):
			if (self.peek() == "do"):
				self.compileDo()
			elif (self.peek() == "let"):
				self.compileLet()
			elif (self.peek() == "while"):
				self.compileWhile()
			elif (self.peek() == "return"):
				self.compileReturn()
			elif (self.peek() == "if"):
				self.compileIf()
			
	
	def compileDo(self):
		#Within a class, methods are called using the syntax methodName(argument-list), while functions and constructors must be called using their full-names, i.e. className.subroutineName(argument-list). 
		fullnameCall = False
		self.advance()										#reach keyword do
		classORfunction = self.advance()					#reach identifier "functionName|className"
		if (self.peek() == "."):							#check if it's a method
			fullnameCall = True								#set method flag
			self.advance()									#reach symbol "." 
			methodName = self.advance()						#reach identifier method name
			self.pushValue(classORfunction)					#push object address as first argument		
		self.advance("(")									#reach "("
		if (fullnameCall == True): 							
			self.compileExpressionList()					#push arguments
			if (classORfunction == self.className or classORfunction in self.builtinFunctions): #handle builtin function and calls to functions in the same class eg:"do Test.method()"
				arguments = self.counter
			else:																				#handle calls to methods in antoher class
				arguments = self.counter + 1													
				classORfunction = self.Table.typeOfFallback(classORfunction) 							#get className
			self.Writer.writeCall((classORfunction + "." + methodName), arguments)
		else:																					#handle calls to method in the same class
			self.Writer.writePush("pointer", 0)
			self.compileExpressionList()														
			arguments = self.counter + 1
			self.Writer.writeCall(self.className + "." + classORfunction , arguments)
		self.Writer.writePop("temp", 0)						#discard return value regardless of function type not being void. Do statements can't be used to assign values or in expressions ie:"let x = do Class.method(arg1)" or "if(do Classs.method() > 5)" are both illegal statements
		self.advance(")")									#reach symbol ")"
		self.advance(";")									#reach symbol ";"

	def compileExpressionList(self):
		self.counter = 0 									#Reset counter
		if (self.peek() == ")"):							#check if there's not an expression
			pass
		else:	
			self.compileExpression()
			self.counter += 1 								#update counter to get number of arguments
			while (self.peek() == ","):						#check for multiple argunments
				self.counter += 1 							#update counter to get number of arguments
				self.advance(",")								#reach symbol ","
				self.compileExpression()

	def compileExpression(self):
		self.compileTerm() 
		while(self.peek() in self.op):					#handle multiple arithmetic
			op = self.advance()							#reach symbol op and save it to a variable
			self.compileTerm()							#get next term into the stack before issuing operation vm command ie: "7 + 8" --> "7, 8, add"
			if op == '+':
				self.Writer.writeArithmetic('add')
			elif op == '-':
				self.Writer.writeArithmetic('sub')
			elif op == '*':
				self.Writer.writeCall('Math.multiply', 2)
			elif op == '/':
				self.Writer.writeCall('Math.divide', 2)
			elif op == '|':
				self.Writer.writeArithmetic('or')
			elif op == '&':
				self.Writer.writeArithmetic('and')
			elif op == '<':
				self.Writer.writeArithmetic('lt')
			elif op == '>':
				self.Writer.writeArithmetic('gt')
			elif op == '=':
				self.Writer.writeArithmetic('eq')
			

	def compileTerm(self):
		if (self.peekType() == "INT_CONST"):
			stack = self.advance()										
			self.Writer.writePush("constant", stack)					
		elif (self.peekType() == "STRING_CONST"):
			string = self.advance() 	
			string = string[1:-1]										#get rid of quotes
			#call builtin functions as said in Chapter11.pdf page 9
			self.Writer.writePush("constant", len(string))				#push string length into the stack
			self.Writer.writeCall("String.new" , 1)						#create object string
			for stack in string:										#push every character individually into the stack
				self.Writer.writePush("constant", ord(stack))			#convert character to ascii and push it into the stack
				self.Writer.writeCall("String.appendChar" , 2)			#2 arguments, first is object reference
		elif (self.peek() in self.keywords2):
			self.advance()	#reach keyword
			if (self.Tokenizer.token == "this"):
				self.Writer.writePush("pointer", 0) 
			elif (self.Tokenizer.token == "false" or self.Tokenizer.token == "null"):
				self.Writer.writePush("constant", 0)
			elif (self.Tokenizer.token == "true"):						#True is mapped to the VM constant –1 (that is obtained via “push constant 0” followed by “neg”.)
				self.Writer.writePush("constant", 0)
				#self.Writer.writeArithmetic("neg")  					#does not work, compiler use not
				self.Writer.writeArithmetic("not")
		elif (self.peekType() == "IDENTIFIER"):
			identifier = self.advance() 								#reach identifier
			if (self.peek() == "[" ):									#handle array
				self.advance()											#reach symbol "["
				self.compileExpression() 								#call compile to get index in the stack
				self.pushValue(identifier)								#call to get array base_adress in the stack
				self.Writer.writeArithmetic("add")						#[base_adress + index]
				self.Writer.writePop("pointer", 1)						#pop [base_array_address + index] into that
				self.Writer.writePush("that", 0)						#push M[base_array_address + index] that into top stack 
				self.advance("]")										#reach symbol "]"
			elif (self.peek() == "("):  							#call method on the same class ie:"let a = method()"
				self.advance()										#reach symbol "("
				self.Table.writePush("pointer", 0)					#pass object reference as first argument
				self.compileExpressionList()						#call compile let arguments at the top of the stack
				nArguments = self.counter + 1
				self.Writer.writeCall((self.className + "." + identifier), nArguments)
				self.advance(")")									#reach symbol ")"
			elif (self.peek() == "."): 			
				self.advance()										#reach symbol "."
				methodName = self.advance()							#reach method name			
				self.advance("(")									#reach symbol "("
				if (identifier in self.builtinFunctions or methodName == "new" or identifier == self.className): #dont pass object reference as first argument in case of a builtin, a constructor or a call to a function in the same class
					self.compileExpressionList()
					nArguments = self.counter
				else:
					self.pushValue(identifier)						#pass object addres as first argument
					self.compileExpressionList()
					nArguments = self.counter + 1
					identifier = self.Table.typeOfFallback(identifier)	#get real class object name
				self.Writer.writeCall((identifier + "." + methodName), nArguments)		
				self.advance(")")									#reach symbol ")"
			else:
				self.pushValue(identifier)						#push identifier value into the stack
		elif (self.peek() == "("): 				#handle nested expresion ie:"(i * (-j) )" #step1 (-j)
			self.advance()						#reach "(" symbol
			self.compileExpression()			#call compile
			self.advance(")")					#reach symbol ")"
		elif (self.peek() in self.unaryOp): #handle "(i * (-j))"  #step2 -j
			unaryOp = self.advance()		#reach symbol unaryOp and save it to a variable to issue the command later
			self.compileTerm()				#call compile term, push "j" intConstant into the stack before issuing op command
			if unaryOp == "-":
				self.Writer.writeArithmetic("neg")	#issue op command	
			elif unaryOp == "~":
				self.Writer.writeArithmetic("not")	#issue op command
			

	def compileLet(self): #pop pointer 1 -> set THAT to top of the stack	#pop that 0 -> set Memory[THAT + 0] to top of the stack 
		isanarray = False
		self.advance()								#reach let
		identifier = self.advance() 				#reach var name
		if self.peek() == "[":						#check next token if array
			isanarray = True
			self.advance() 							#reach symbol "["
			self.compileExpression()				#get array index
			self.pushValue(identifier)				#push array base_addres into the top of the stack
			self.Writer.writeArithmetic("add")		#get [base_address + index]
			#self.Writer.writePop("temp", "0")		#may get overwriten by compileTerm
			self.advance("]")						#reach ending symbol "]"
		self.advance("=")					#reach symbol "="
		self.compileExpression()			#push value_to_assign at the top of stack
		if (isanarray == True):
			self.Writer.writePop("temp", 0)			#save value_to_assign temporally
			self.Writer.writePop("pointer", 1)		#pop [base_address + index] into that
			self.Writer.writePush("temp", 0)		#retrieve value to stack top
			self.Writer.writePop("that", 0)			#pop value into M[that] 
		else:
			self.popValue(identifier)		#pop value into the variable
		self.advance(";")					#reach symbol ";"
		

	def compileIf(self):
		#handle recursion
		#since Python keeps a private copy of local variables for each instance of the function there's no need for aditional code keeping track of the correct IFcounter value	in case of nested ifs
		IFcounter = self.maxIFcounter + 1			#each instance of the function call will have its own copy with its own different value	
		self.maxIFcounter = IFcounter				#keep track of highest value used
		##############################
		self.advance()									#reach keyword if	 
		self.advance("(")								#reach symbol "("			
		self.compileExpression()						#(x < y), get "x,y,<" into the stack 
		self.advance(")")					 			#reach symbol ")" 
		self.Writer.writeIf("IF_TRUE" + str(IFcounter))
		self.Writer.writeGoto("IF_FALSE" + str(IFcounter))
		self.Writer.writeLabel("IF_TRUE" + str(IFcounter))
		self.advance("{")								#reach symbol "{"
		self.compileStatements()						#call compile
		self.advance("}")								#reach "}" symbol
		#handle ELSE block
		if (self.peek() == "else"):
			self.Writer.writeGoto("IF_END" + str(IFcounter)) #avoid executing else statement in case of condition being True
		self.Writer.writeLabel("IF_FALSE" + str(IFcounter))  #part of IF block, always get written 
		if (self.peek() == "else"):
			self.advance()								#reach keyword "else"
			self.advance("{")							#reach symbol "{"
			self.compileStatements()					#compile statements inside ELSE
			self.advance("}")							#reach symbol "}"
			self.Writer.writeLabel("IF_END" + str(IFcounter))
		

	def compileWhile(self):
		#handle recursion
		#since Python keeps a private copy of local variables for each instance of the function there's no need for aditional code keeping track of the correct "WHILEcounter" value in case of nested WHILES
		WHILEcounter = self.maxWHILEcounter + 1		#each function call will have its own copy
		self.maxWHILEcounter = WHILEcounter			#keep track of highest value used
		######################################
		self.advance()							#reach keyword "while"
		self.Writer.writeLabel("WHILE_EXP" + str(WHILEcounter)) #label, jump here to check after each iteration
		self.advance()							#reach symbol "(" 
		self.compileExpression()				#call compile
		self.advance()							#reach symbol ")"
		self.Writer.writeArithmetic("not") 		#invert value so doesn't skip the loop when the condition is met
		self.Writer.writeIf("WHILE_END" + str(WHILEcounter)) #if, jump to the end if condition for a iteration is not met
		self.advance()							#reach symbol "{"
		self.compileStatements()				#call compile
		self.Writer.writeGoto("WHILE_EXP" + str(WHILEcounter)) 	#goto, do another check
		self.Writer.writeLabel("WHILE_END" + str(WHILEcounter)) 	#label, jump here if the condition for a new iteration is not met
		self.advance("}")						#reach symbol "}"

	def compileReturn(self):
		self.advance()					#reach keyword "return"
		if(self.peek() == ";" ):
			self.Writer.writePush("constant", 0)
		else:
			self.compileExpression()	#call compile
		self.Writer.writeReturn()
		self.advance(";")				#reach symbol ";"

	def pushValue(self, identifier):
		kind = self.Table.kindOfFallback(identifier) 
		if (kind == "VAR"):
				self.Writer.writePush("local", self.Table.indexOfFallback(identifier))
		elif (kind == "ARG"):
				self.Writer.writePush("argument", self.Table.indexOfFallback(identifier))
		elif (kind == "STATIC"):
				self.Writer.writePush("static", self.Table.indexOfFallback(identifier))
		elif (kind == "FIELD"):
				self.Writer.writePush("this", self.Table.indexOfFallback(identifier))

	def popValue(self, identifier):
		kind = self.Table.kindOfFallback(identifier) 
		if (kind == "VAR"):
				self.Writer.writePop("local", self.Table.indexOfFallback(identifier))
		elif (kind == "ARG"):
				self.Writer.writePop("argument", self.Table.indexOfFallback(identifier))
		elif (kind == "STATIC"):
				self.Writer.writePop("static", self.Table.indexOfFallback(identifier))
		elif (kind == "FIELD"):
				self.Writer.writePop("this", self.Table.indexOfFallback(identifier))




		
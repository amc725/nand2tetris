import re
from Tokenizer import Tokenizer
class CompilationEngine:
	def __init__(self, input_file):

		#initialize objects
		self.Tokenizer = Tokenizer(input_file)
		
		#ALIASES
		self.advance = self.Tokenizer.advance
		self.peek = self.Tokenizer.peek
		self.peekType = self.Tokenizer.peekType
		self.writeXML = self.Tokenizer.writeXML
		self.outputFile = self.Tokenizer.outputFile

		#compilationEngine variables
		self.statements = ("let", "if", "while", "do", "return")
		self.op = ('+', '-', '*', '&', '/', '|', '=', '<', '>')
		self.unaryOp = ('-', '~')
		self.keywords2 = ('true', 'false', 'null', 'this')


	def compileClass(self):
		self.outputFile.write("<class>\r\n")	#write XML tag
		self.advance(); self.writeXML()			#write "class" keyword
		self.advance(); self.writeXML()			#write name
		self.advance(); self.writeXML()			#write { symbol 

		if (self.peek() == "field" or self.peek() == "static"):	#check for next statement
			self.CompileClassVarDec()
		while (self.peek() == "constructor" or self.peek() == "method" or self.peek() == "function"):
			self.CompileSubroutine()
		
		self.advance(); self.writeXML()			#write "}" symbol	
		self.outputFile.write("</class>\r\n")	#write end tag
		self.outputFile.close()					#END
		
		   
	def CompileClassVarDec(self):
		while (self.peek() == "field" or self.peek() == "static"):
			self.outputFile.write("<classVarDec>\r\n")
			self.advance(); self.writeXML()			#write keyword kind "field|static"
			self.advance(); self.writeXML()			#write keyword "type" 
			self.advance(); self.writeXML()			#write identifier "name"
			
			while(self.peek() == ","):				#handle multiple declarations at once
				self.advance(); self.writeXML()		#write symbol ","
				self.advance(); self.writeXML()		#write identifier name 

			self.advance(); self.writeXML()			#write symbol ";"
			self.outputFile.write("</classVarDec>\r\n")


	def CompileSubroutine(self):
		while(self.peek() == "constructor" or self.peek() == "method" or self.peek() == "function"):
			self.outputFile.write("<subroutineDec>\r\n")
			self.advance(); self.writeXML()		#write keyword "method|constructor|function"
			self.advance(); self.writeXML()		#write identifier type
			self.advance(); self.writeXML()		#write identifier "name"
			if (self.peek() == "("):
				self.compileParameterList()
			self.outputFile.write("<subroutineBody>\r\n")
			self.advance(); self.writeXML()		#reach and write symbol "{" 
			if (self.peek() == "var"):			#check if there is variable declarations
				self.compileVarDec()
			self.compileStatements()			
			self.advance(); self.writeXML()					#write "}" symbol
			self.outputFile.write("</subroutineBody>\r\n")	#write end tag
			self.outputFile.write("</subroutineDec>\r\n")	#write end tag

			
			
	def compileParameterList(self):
		self.advance(); self.writeXML()					#write symbol "("
		self.outputFile.write("<parameterList>\r\n")	#write tag
		if (self.peek() == ")"):						#write identifer and check for empty p_list
			pass
		else:
			self.advance(); self.writeXML()				#write keyword "type"
			self.advance(); self.writeXML()				#write identifier "name"
			while(self.peek() == ","):					#check for multiple parameters
				self.advance(); self.writeXML()				#write symbol ","
				self.advance(); self.writeXML()				#write keyword "type"
				self.advance(); self.writeXML()				#write identifier "name"
		self.outputFile.write("</parameterList>\r\n")	
		self.advance(); self.writeXML()					#write symbol ")"

	def compileVarDec(self):
		while (self.peek() == "var"):
			self.outputFile.write("<varDec>\r\n")			
			self.advance(); self.writeXML()				#write keyword "var"
			self.advance(); self.writeXML()				#write keyword type "int|boolean..."
			self.advance(); self.writeXML()				#write idetifier "name"
			while (self.peek() == ","):					#check if there is multiple declarations at once
				self.advance(); self.writeXML()				#write symbol ","
				self.advance(); self.writeXML()				#write identfier name
			self.advance(); self.writeXML()				#write symbol ";"
			self.outputFile.write("</varDec>\r\n")
		

	def compileStatements(self):
		self.outputFile.write("<statements>\r\n")
		while(self.peek() in self.statements):
			if (self.peek() == "do"):
				print("compileDo")
				self.compileDo()
			elif (self.peek() == "let"):
				print("compileLet")
				self.compileLet()
			elif (self.peek() == "while"):
				print("compileWhile")
				self.compileWhile()
			elif (self.peek() == "return"):
				print("compileReturn")
				self.compileReturn()
			elif (self.peek() == "if"):
				print("compileIf")
				self.compileIf()
		self.outputFile.write("</statements>\r\n")
	
	def compileDo(self):
		self.outputFile.write("<doStatement>\r\n")		#write tag
		self.advance(); self.writeXML()					#write keyword "do"
		self.advance(); self.writeXML()					#write identifier "function|class"
		if (self.peek() == "."):						#check if it's a different class call
			self.advance(); self.writeXML()					#write symbol "."
			self.advance(); self.writeXML()					#write identifier method name
		self.advance(); self.writeXML()				#write "("
		self.compileExpressionList()				
		self.advance(); self.writeXML()				#write symbol ")" 
		self.advance(); self.writeXML()				#write symbol ";"
		self.outputFile.write("</doStatement>\r\n")

	def compileExpressionList(self):
		self.outputFile.write("<expressionList>\r\n")
		if (self.peek() == ")"):	#check if there's expression
			pass
		else:
			self.compileExpression()
			while (self.peek() == ","):
				self.advance(); self.writeXML()		#write symbol ","
				self.compileExpression()
		self.outputFile.write("</expressionList>\r\n")


	def compileExpression(self):
		self.outputFile.write("<expression>\r\n")
		self.compileTerm()
		while(self.peek() in self.op):
			self.advance(); self.writeXML()		#write symbol op
			self.compileTerm()					#call compile
		self.outputFile.write("</expression>\r\n")



	def compileTerm(self):
		self.outputFile.write("<term>\r\n")
		#check next value
		if (self.peekType() == "INT_CONST" or self.peekType() == "STRING_CONST" or self.peek() in self.keywords2):
			self.advance(); self.writeXML()			#write constant
		elif (self.peekType() == "IDENTIFIER"):
			self.advance(); self.writeXML()			#write identifier
			if (self.peek() == "[" ): #array
				self.advance(); self.writeXML()		#write array symbol "["
				self.compileExpression() 
				self.advance(); self.writeXML()		#write symbol "]"
			elif (self.peek() == "("): 	
				self.advance(); self.writeXML()		#write symbol "("
				self.compileExpressionList()		
				self.advance(); self.writeXML()		#write symbol ")"
			elif (self.peek() == "."): 
				self.advance(); self.writeXML()		#write symbol "."				
				self.advance(); self.writeXML()		#write method name				
				self.advance(); self.writeXML()		#write symbol "("				
				self.compileExpressionList()					
				self.advance(); self.writeXML()		#write symbol ")"
		elif (self.peek() == "("): 
			self.advance(); self.writeXML()		#write "(" symbol
			self.compileExpression()
			self.advance(); self.writeXML()		#write ")" symbol
		elif (self.peek() in self.unaryOp): 	
			self.advance(); self.writeXML()		#write symbol unaryOp
			self.compileTerm()
		self.outputFile.write("</term>\r\n")

	def compileLet(self):
		self.outputFile.write("<letStatement>\r\n")
		self.advance(); self.writeXML()		#write let
		self.advance(); self.writeXML()		#write var name
		if self.peek() == "[":				#check next token if array
			self.advance(); self.writeXML()		#write symbol "["
			self.compileExpression()					
			self.advance(); self.writeXML()		#write ending symbol "]"
		self.advance(); self.writeXML()		#write symbol "="
		self.compileExpression()
		self.advance(); self.writeXML()		#write symbol ";"
		self.outputFile.write("</letStatement>\r\n")

	def compileIf(self):
		self.outputFile.write("<ifStatement>\r\n")	
		self.advance(); self.writeXML()		#write if
		self.advance(); self.writeXML()		#write symbol "(" 
		self.compileExpression()
		self.advance(); self.writeXML()		#write symbol ")" 
		self.advance(); self.writeXML()		#write symbol "{"
		self.compileStatements()			
		self.advance(); self.writeXML()		#write "}" symbol
		while (self.peek() == "else"):
			self.advance();self.writeXML()	#write keyword "else"
			self.advance(); self.writeXML()	#write symbol "{"
			self.compileStatements()
			self.advance(); self.writeXML()	#write symbol "}"
		self.outputFile.write("</ifStatement>\r\n")
		
	def compileWhile(self):
		self.outputFile.write("<whileStatement>\r\n")
		self.advance(); self.writeXML()		#write identfier "while"
		self.advance(); self.writeXML()		#write symbol "(" 
		self.compileExpression()			#call compile
		self.advance(); self.writeXML()		#write symbol ")"
		self.advance(); self.writeXML()		#write symbol "{"
		self.compileStatements()			#call compile
		self.advance(); self.writeXML()		#write symbol "}"
		self.outputFile.write("</whileStatement>\r\n")

	def compileReturn(self):
		self.outputFile.write("<returnStatement>\r\n")
		self.advance(); self.writeXML()		#write keyword "return"
		while(self.peek() != ";" ):
			self.compileExpression()
		self.advance(); self.writeXML()		#write symbol ";"
		self.outputFile.write("</returnStatement>\r\n")

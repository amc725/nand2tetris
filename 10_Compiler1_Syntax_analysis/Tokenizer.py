import re
class Tokenizer:
	def __init__(self, input_file):
		self.keywords = ("class", "constructor", "method", "function", "field", "static", "var", "int", "char", "boolean","void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return")
		self.symbols = ('{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '<', '>', '=', '~')

		self.file = open(input_file, "r")
		self.list = []
		self.tokens_list = []
		
		self.current_line = -1 #list starts at 0

		#initialize xml output
		self.outputName = input_file + ".temp.xml"
		self.outputFile = open(self.outputName, "w")
		

		#expressions
		self.keywords_exp = ""
		for keyword in self.keywords:
			self.keywords_exp += r'\b' + keyword + r'\b' + '|'
		index = len(self.keywords_exp) - 1
		self.keywords_exp = self.keywords_exp[0:index]	#get rid of ending "|"
		######
		string = ""
		for i in self.symbols:
			string += re.escape(i) + re.escape('|')
		index = len(string) - 2
		string = string[0:index]	#get rid of ending "\|"
		self.symbols_exp = "[" + string + "]"
		#####
		self.integer_exp = '\d+'
		self.strings_exp =  '"[^"]*"'
		self.identifiers_exp = '[\w]+'
		
		#pattern
		self.pattern = re.compile(self.keywords_exp + '|' + self.symbols_exp + '|' + self.integer_exp + '|' + self.strings_exp + '|' + self.identifiers_exp)


	def remove_comments(self): 
		inside_multicomment = False #flag if inside a multicomment
		for i in self.file:
			line = i.strip()
			
			#chek if we are inside a multicomment
			if (inside_multicomment == True and "*/" not in line): #check if we are inside a multicomment and skip the iteration if the closing statement it's not there
				continue
			elif (inside_multicomment == True and "*/" in line):  #check if we are inside a multicomment and we reached the end 
				line = re.sub(".*\*/", "" , line)
				inside_multicomment = False
			else: #just skip the check if we are not inside a multicomment
				pass

			#handle multiline comments
			if "/*" in line: 
				if "*/" in line: #handle end of comment on the same line
					line = re.sub("/\*.*\*/", "" , line) 
				else:
					line = re.sub("/\*.*", "", line) #get rid of the comment
					inside_multicomment = True

			#handle side comments
			if "//" in line: 
				line = re.sub("//.*", "", line)
			else:
				pass

			#handle empty lines and lines from stripped comments
			line = line.strip()
			if (line == "" or line == "\r\n" or line == "\n"): 
				pass
			else:
				self.list.append(line)
			
			
	def getTokens(self):
		for i in self.list:
			tokens = re.findall(self.pattern, i)
			self.tokens_list.extend(tokens)
		
		self.length = len(self.tokens_list) - 1 
		print(self.length)
				

	def advance(self):
		self.current_line += 1
		self.token = self.tokens_list[self.current_line]
		print(self.token)


	def hasMoreCommands(self):
		if self.current_line < self.length:
			return True
		else:
			return False

	def tokenType(self):
		if re.match(self.keywords_exp, self.token):
			return "KEYWORD"
		elif re.match(self.symbols_exp, self.token):
			return "SYMBOL"
		elif re.match(self.integer_exp, self.token):
			return "INT_CONST"
		elif re.match(self.identifiers_exp, self.token):
			return "IDENTIFIER"
		elif re.match(self.strings_exp, self.token):
			return "STRING_CONST"
	
	def keyWord(self):
		return self.token
	

	def print_tokens(self):
		for i in self.tokens_list:
			print(i)
	
	def peek(self):
		line = self.current_line + 1
		peek = self.tokens_list[line]
		return peek

	def peekType(self):
		line = self.current_line + 1
		if re.match(self.keywords_exp, self.tokens_list[line]):
			return "KEYWORD"
		elif re.match(self.symbols_exp, self.tokens_list[line]):
			return "SYMBOL"
		elif re.match(self.integer_exp, self.tokens_list[line]):
			return "INT_CONST"
		elif re.match(self.identifiers_exp, self.tokens_list[line]):
			return "IDENTIFIER"
		elif re.match(self.strings_exp, self.tokens_list[line]):
			return "STRING_CONST"

	def writeXML(self):
		type = self.tokenType()
		if type == "KEYWORD":
			self.outputFile.write("<keyword>" + self.token + "</keyword>\r\n")
		elif type == "SYMBOL":
			if (self.token == "&"):
				self.token = "&amp;"
			elif self.token == "<":
				self.token = "&lt;"
			elif self.token == ">":
				self.token = "&gt;"
			elif self.token == "\"":
				self.token = "&quot;"
			self.outputFile.write("<symbol>" + self.token + "</symbol>\r\n")
		elif type == "INT_CONST":
			self.outputFile.write("<integerConstant>" + self.token + "</integerConstant>\r\n")
		elif type == "IDENTIFIER":
			self.outputFile.write("<identifier>" + self.token + "</identifier>\r\n")
		elif type == "STRING_CONST":
			self.outputFile.write("<stringConstant>" + self.token[1:-1] + "</stringConstant>\r\n")
	
	def end_writeXML(self):
		self.outputFile.write("</tokens>")

		

		
	
	
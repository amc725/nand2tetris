// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)



@resultado
M=0


@R2
M=0

@R1
D=M
//if R1==0
@fin
D;JEQ
@i
M=0
@i
M=M-D




(LOOP)
	@R0
	D=M
	@resultado
	M=M+D
	@i
	M=M+1
	@i
	D=M
	@LOOP
	D;JLT

@resultado
D=M
@R2
M=D


(fin)
@fin
0;JMP


	
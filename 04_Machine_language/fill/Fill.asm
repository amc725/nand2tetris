// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

//Variables globales
@16384
D=A
@pantalla
M=D
@8192
D=A
@longitud
M=D

(START)
@i
M=0




(WHITE_LOOP)    // WHITE LOOP infinite
@i
D=M
@pantalla
A=M+D
M=0
@longitud       // check if (longitud - i == O) to avoid writing out display memory
D=M
@i
M=M+1           // increment iterator before checking
D=D-M           
@START      
D;JEQ
@KBD            // check if any key is being pressed, if not keep in the loop
D=M
@WHITE_LOOP
D;JEQ

(RESET_ITERATOR)
@i              // reset iterator before blackening the screen
M=0

(BLACK_LOOP)
@i
D=M
@pantalla
A=M+D
M=-1
@KBD            // jump to begining if key stop to being pressed
D=M
@START      
D;JEQ
@longitud       // check if (longitud - i == O) to avoid writing out display memory
D=M
@i
M=M+1
D=D-M
@RESET_ITERATOR
D;JEQ
@BLACK_LOOP     // keep drawing the screen
0;JMP


// Input: a binary number n
// Ouput: accepts if n is a palindrome
// Example: accepts 10101
//
// Palindrome Algorithm
// for Turing Machine Simulator 
// turingmachinesimulator.com

name: Binary palindrome
init: q0
accept: qAccept

q0,0
qRight0,_,>

qRight0,0
qRight0,0,>

qRight0,1
qRight0,1,>

q0,1
qRight1,_,>

qRight1,0
qRight1,0,>

qRight1,1
qRight1,1,>

qRight0,_
qSearch0L,_,<

qSearch0L,0
q1,_,<

qRight1,_
qSearch1L,_,<

qSearch1L,1
q1,_,<

q1,0
qLeft0,_,<

qLeft0,0
qLeft0,0,<

qLeft0,1
qLeft0,1,<

q1,1
qLeft1,_,<

qLeft1,0
qLeft1,0,<

qLeft1,1
qLeft1,1,<

qLeft0,_
qSearch0R,_,>

qSearch0R,0
q0,_,>

qLeft1,_
qSearch1R,_,>

qSearch1R,1
q0,_,>

qSearch0R,1
qReject,1,-

qSearch1R,0
qReject,0,-

qSearch0L,1
qReject,1,-

qSearch1L,0
qReject,0,-

q0,_
qAccept,_,-

q1,_
qAccept,_,-

qSearch0L,_
qAccept,_,-

qSearch0R,_
qAccept,_,-

qSearch1L,_
qAccept,_,-

qSearch1R,_
qAccept,_,-
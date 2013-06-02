/*
Example how labels may produce a stack overflow. I have to think of a solution.
*/

a := 2000

label loop
  a := a - 1
  if a > 0 goto loop
  
a := a
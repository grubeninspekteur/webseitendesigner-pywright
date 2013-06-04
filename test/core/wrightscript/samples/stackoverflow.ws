/*
* A previous recursive solution for goto resulted in a stack overflow. The new Root
* class prevents this.
*/

a := 2000

label loop
  a := a - 1
  if a > 0 goto loop
  
a := a
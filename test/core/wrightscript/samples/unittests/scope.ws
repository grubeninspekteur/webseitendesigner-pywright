/**
* Tests the scoping rules.
**/

x := 42 # Global variable

def fun x # Shadowing the local variable
  a := 0
  return x
enddef

a := 4 # Dynamic scoping - a is visible in fun

assert (fun 9) = 9
assert a = 0
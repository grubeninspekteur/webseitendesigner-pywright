/* Test of simple recursion. Recursion depth is limited to Python recursion
   depth minus the nesting level of the initial function call. */
   
def factorial x

  if x = 0 return 1 else return x * (factorial x - 1)
enddef

assert (factorial 5) = 120
assert (factorial 1) = 1

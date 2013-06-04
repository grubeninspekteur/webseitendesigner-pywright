/**
* Tests using a function expecting a function as a parameter.
**/

def elem +: list
  return [elem] :: list
enddef

def map fun list
  if (isEmpty list) return []
  return (fun (first list)) +: (map fun (rest list))
enddef

def square x
  return x * x
enddef

assert (square 2) = 4
#print (listToStr (map square [1, 2, 3]))
assert (map square [1, 2, 3]) = [1, 4, 9]
  
#VERSION 2

/*
* Defines a simple function that adds one to a Number, calls it
* and shows the value.
*/

textbox (concat "Meaning of Life: " (addone 41))

/*
The function definition may be after the call, thus the semantic
analysis that retrieves the label positions should also extract
the function definition and bind it to the identifier.
*/

def addone x
  return 1 + x
enddef
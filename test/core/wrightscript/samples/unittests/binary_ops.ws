/* Same as binary ops syntax test, but with assertions. */

a := 5 + 5
assert a = 10

a := 10 - (2 * 3)
assert a = 4

a := (10 - 2) * 3
assert a = 24

a := 10 - 2 * 3
assert a = 24

if 5 = 5 (assert true) else (assert false)

assert ([1, 2, 3] :+ 5) = [1, 2, 3, 5]

assert ([1, 2, 3] :+ (5 - 1)) = [1, 2, 3, 4] 

def list :+ elem
  return list :: [elem]
enddef
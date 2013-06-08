/* Tests some assertions on entities. */

entity Point
  x
  y
  z := 0
endentity

coord := Point {x := 4, y := 6}
assert coord.x = 4
assert coord.y = 6
assert coord.z = 0

/* As of now, fields may be created on the fly */
coord.foo := "bar"
assert coord.foo = "bar"

/* Test of nested entites */
entity Character
  name
  blipsound
endentity

entity Sound
  filename
endentity

Phoenix := Character {name := "Phoenix", blipsound := Sound {filename := "blipmale.wav"} }
assert Phoenix.name = "Phoenix"
assert Phoenix.blipsound.filename = "blipmale.wav"

/* Test for entities as reference */
Phoenix2 := Phoenix
Phoenix2.name := "Phoenix2"

assert Phoenix2.name = "Phoenix2"
assert Phoenix.name = "Phoenix2"

def isNamedPhoenix2 ent
   return ent.name = "Phoenix2"
enddef

assert (isNamedPhoenix2 Phoenix2)
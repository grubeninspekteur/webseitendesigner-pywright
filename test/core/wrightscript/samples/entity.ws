/**
* Tests the entity definition and creation syntax.
**/

entity Character
  name := "???"
  blipsound
endentity

Apollo := Character {
  name := "Apollo",
  blipsound := "male"
  # Portrait definitions etc.
}

speaker Apollo
"I have Chords of Steel!"

speaker Character {name := "", blipsound := "typewriter"} /* Creation on the fly (Just an example,
                                                             you wouldn't do typewriter that way)*/
"March 22"

Apollo.blipsound := "silent" # Entity fields are mutable variables
speaker Apollo
"What happened to my voice?"
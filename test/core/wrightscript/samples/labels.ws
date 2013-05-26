#VERSION 2

/*
* Some simple label, goto and resume expressions.
*/

goto main

label pre
"Count: 2"
resume

"This should never be displayed."

label main
"Hello from label main!"

label a
"Count: 1"
goto pre

"Count: 3"
"FIN"
/**
* A simple conditional test.
**/

if true goto step1
"This should never be displayed"

label step1
if false noop else goto step2
"This should never be displayed"

label step2
if false goto fail

goto success

label fail
"This should never be displayed"

label success
"Success"

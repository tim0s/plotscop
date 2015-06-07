# Plotscop

The LLVM's polyhedral optimizer Polly has the ability to export static control
parts (SCOPs) as JSON files. It can also import user modified SCOPs in the JSON
format and generate code for them instead of the ones the default optimizer
built. This is a really useful feature if you want to play with polyhedral
optimization.

Unfortunately, if you are not yet expierienced in the polyhedral optimization,
understanding what a JSCOP actually means can be quite hard. The goal of this
tool is to help you with that by creating a visual representation of the SCOP
in the form of an animation that shows which memory locations are accessed at
what time.

## Example

This code

	int* A = (int*) malloc(arraysize*sizeof(int));
	int* B = (int*) malloc(arraysize*sizeof(double));

	memset(&A[0], 0, arraysize*sizeof(int));

	for(int i=0; i<arraysize-4; i++) {
		B[42] += A[i+2];
	}

	printf("sum=%d\n", B[42]);


will produce the following JSCOP when compiled with a debug-build of llvm (if
you use a regular release build the variable names are mostly replaced by
numbers in order to save space, but it works the same way):

    {
       "context" : "{  :  }",
       "name" : "for.body => for.end",
       "statements" : [
          {
             "accesses" : [
                {
                   "kind" : "read",
                   "relation" : "{ Stmt_for_body[i0] -> MemRef_call[2 + i0] }"
                },
                {
                   "kind" : "read",
                   "relation" : "{ Stmt_for_body[i0] -> MemRef_call1[42] }"
                },
                {
                   "kind" : "write",
                   "relation" : "{ Stmt_for_body[i0] -> MemRef_call1[42] }"
                }
             ],
             "domain" : "{ Stmt_for_body[i0] : i0 >= 0 and i0 <= 95 }",
             "name" : "Stmt_for_body",
             "schedule" : "{ Stmt_for_body[i0] -> [i0] : i0 >= 0 and i0 <= 95 }"
          }
       ]
    }

You can visualize this as an ASCII art animation with 
    ./plotscop pollyoutput.jscop

It will look something like this:
	![image](https://cloud.githubusercontent.com/assets/4130382/8023159/6aaa8000-0cfe-11e5-8868-5f7eda36e3f6.gif)

You can produce an animated gif like the one above with a patched version of
ansi2gif (https://github.com/tim0s/ansi2gif):

    ./plotscop foo.jscop > foo.ans
    .ansi2gif --xsize 160 --ysize=10 --animate --frameperrefresh foo.ans foo.gif


 

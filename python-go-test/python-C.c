//this is the call from Python to C
//main issue is registering callbacks
#include <stdio.h>
#include "python-C.h"

// CMPFUNC = CFUNCTYPE(c_int, c_int)

typedef int(*cb)(int);

// for first test, just register int values
typedef struct Regtable {
    int w;
    int z;
    cb callback;
} Regtable;

Regtable regtable;



void callbackRegister(cb cbi) 
{
    regtable.callback = cbi;   
}

void printregtable()
{
    printf("w = %d z = %d \n", regtable.w, regtable.z);
}

//pseudo callback using C registered callbacks, 
//transparent to the Go code.  Just looks like
//C.gocallback() to the Go code
int Gocallback(void)
{
    //printregtable();
    regtable.callback(99);
    return 100;
}


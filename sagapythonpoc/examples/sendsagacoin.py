# Sending sagacoin from current account to another
# transaction is from curracct to 'bbb'
# the signature on the transaction script
# verifies the caller.
# No verification on the receiver. 

def __hdr():
    hdr = { 'acct': 'aaa', 
	    'seq': 1000,        # whatever the next sequence number is 
		'maxGU': 10, 
		'feePerGU': 1,
		'extraPerGU': 2
        }
    return hdr 

def __body():
    toacct = ClsObjVar('bbb')
    coins, err = curracct().take(NNN)    # subtracts amount from the current account
    if coins != NNN:
        ErrorExit(err)

    err = toacct.put(NNN)    # adds NNN coins to account referenced by toacct
    if err != None:
        ErrorExit(err)                                  

def __tail():
    return {'hash': 12345,
            'sig': (rvalue, svalue)    # tuple of r and s value for signature
    }                  
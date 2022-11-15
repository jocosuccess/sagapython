# Sending sagacoin from one account to another
# assumes 2 accounts exist with oids: 'aaa' and 'bbb'
# transaction is from 'aaa' to 'bbb'
# transaction is submitted by 'aaa' with its signature

def __hdr():
    hdr = { 'acct': 'aaa', 
	    'seq': 1000,        # whatever the next sequence number is 
		'maxGU': 10, 
		'feePerGU': 1,
		'extraPerGU': 2
        }
    return hdr 

def __body():
    objvar = ClsObjVar('aaa')
    toacct = ClsObjVar('bbb')
    objvar().sendto(toacct, NNN)    # send NNN coins to account referenced by toacct
                                    # class account will generate error if insufficient funds

def __tail():
    return {'hash': 12345,
            'sig': (rvalue, svalue)    # tuple of r and s value for signature
    }                  
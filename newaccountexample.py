# transaction script to create a new account
# Creating a new account by sending a transaction
# to an account manager object that acts as a 
# factory object. 
# The account contianing the account manager must
# publish its private key as a wellknown key for
# this use. Not advisable for general accounts.

def __hdr():
    owningaccount = 'ABCDE'         # normally a single global wellknown account for creating accounts
    transactionseqnum = 0           # special seq number when transaction ordering is unimportant
    hdr = { 'acct': owningaccount, 
	    'seq': transactionseqnum, 
		'maxGU': 10, 
		'feePerGU': 1,
		'extraPerGU': 2
        }
    return hdr                      # must be a dictionary with the transaction header values
                                    # does not return to the client, return is used here as a convenience
                                    # for transaction execution only


# the body of the transaction sends a message to the account manager to create a new account
def __body():
    accmgr = ClsObjVar('bbbb')      # object ID of the account manager object which is owned by the value
                                    # of owningaccount
    newacct = accmgr().MakeAcct()   # returns a ClsObjVar instance for the new account
    log(newacct.oid)                # records the oid in the transaction log in the block. 
                                    # transaction do not "return" values
                                    # must listen to blockchain for confirmation

# tail contains hash of __hdr and __body functions.
def __tail():
    return {'hash': 12345,
            'sig': (rvalue, svalue)    # tuple of r and s value for signature
    }
    

                        





# testing if the order of imports versus class and function are meaningless
# that is, if an import happens in the middle of a function, it should still be visible to the entire function
# or is it only visible after it is run over in the code?

def func1():
    import xtest
    print(xtest.x)

def func():
    import xtest
    print (xtest.x)
    print (xtest.ytest.y)
    xtest.x = 2
    xtest.ytest.y = 30

def func2():
    import ytest
    print(ytest.y)



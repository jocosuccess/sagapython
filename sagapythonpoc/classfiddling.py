

# first create a class with something in the instance dictionary
class c1:
    def __init__(self):
        self.x = 1
        self.y = 2


# now a class without anything in the instance dictionary
class c2:
    pass

# now create an instance of the first class
e1 = c1()
print (e1.x, e1.y)

e1dict = e1.__dict__.copy()

print(e1dict)

del e1

# create an object of a different class
e2 = c2.__new__(c2)

# give it the dict from c1
e2.__dict__.update(e1dict)

print (e2.x, e2.y)
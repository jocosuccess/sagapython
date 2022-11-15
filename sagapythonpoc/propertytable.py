# propertytable.py
#
# A property consists of a property table of entries and byte arrays.
# A byte array can itself be a property.  That is, properties nest.
#
# Each object is stored as a property.
# First entry is the type of the object
# Second entry is the object instance data
# For metaclasses -- by definition, the second entry is a property with the runtime info in it.
#
# For all other objects, the class and ancestor classes are responsible for reading the list of
# properties in the second entry, each of which is for a given class.
# 
# The SagaPythonObject uses the class OID (or index) to look up the property that matches the
# current class context for the object.  The classes are ordered by the head class linearization.
#   
# Property Table Definition
# 
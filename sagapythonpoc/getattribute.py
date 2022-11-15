# code for getattribute override for the stub and skeleton objects
#
# Adds in the following behaviors:
# For the skeleton:
#   looks for a CMI field name first
#   then looks for a CMI method name
#   then need to have all the Python instance objects
#   checked for descriptors. To do so, the skeleton class __dict__
#   would normally contain the class names.
#   instead should look at dict of objects read f


def _PyType_Lookup(tp, name):
    mro = tp.mro()
    assert isinstance(mro, tuple)

    for base in mro:
       assert isinstance(base, type)

       # PEP 447 will change these lines:
       try:
           return base.__dict__[name]
       except KeyError:
           pass

    return None


class object:
    def __getattribute__(self, name):
        assert isinstance(name, str)

        tp = type(self)
        descr = _PyType_Lookup(tp, name)

        f = None
        if descr is not None:
            f = descr.__get__
            if f is not None and descr.__set__ is not None:
                # Data descriptor
                return f(descr, self, type(self))

        dict = self.__dict__
        if dict is not None:
            try:
                return self.__dict__[name]
            except KeyError:
                pass

        if f is not None:
            # Non-data descriptor
            return f(descr, self, type(self))

        if descr is not None:
            # Regular class attribute
            return descr

        raise AttributeError(name)


class super:
    def __getattribute__(self, name):
       assert isinstance(name, unicode)

       if name != '__class__':
           starttype = self.__self_type__
           mro = startype.mro()

           try:
               idx = mro.index(self.__thisclass__)

           except ValueError:
               pass

           else:
               for base in mro[idx+1:]:
                   # PEP 447 will change these lines:
                   try:
                       descr = base.__dict__[name]
                   except KeyError:
                       continue

                   f = descr.__get__
                   if f is not None:
                       return f(descr,
                           None if (self.__self__ is self.__self_type__) else self.__self__,
                           starttype)

                   else:
                       return descr

       return object.__getattribute__(self, name)


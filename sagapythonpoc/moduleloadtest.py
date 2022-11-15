

def get_data(self, path):
        """Return the data from path as raw bytes."""
        if isinstance(self, (SourceLoader, ExtensionFileLoader)):
            with _io.open_code(str(path)) as file:
                return file.read()
        else:
            with _io.FileIO(path, 'r') as file:
                return file.read()


        if source_bytes is None:
            source_bytes = self.get_data(source_path)
        code_object = self.source_to_code(source_bytes, source_path)


def source_to_code(self, data, path, *, _optimize=-1):
        """Return the code object compiled from source.

        The 'data' argument can be any object type that compile() supports.
        """
        return _bootstrap._call_with_frames_removed(compile, data, path, 'exec',
                                        dont_inherit=True, optimize=_optimize)

def _call_with_frames_removed(f, *args, **kwds):
        return f(*args, **kwds)

# this should read in the raw data as source code.
# returns as a bytes object, not a str.
def get_data(path):
    with open(path, "rb", buffering=0) as file:
        return file.read()

def makecode(data, path):
    return compile(data, path, flags=exec, dont_inherit=true, optimize=-1)

def makemodule():
    pass

def execmodule():
    pass


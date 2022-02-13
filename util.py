import os


def getpassword(fn = None):
    if fn is None: #  By default read from file "pw" in same dir as python scripts
        fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pw")  
    if not os.path.exists(fn):
        return "12345678"  #  If pw file does not exist, return default password
    with open(fn, 'rt') as fh:
        # Read first 128 bytes of file and return as a string
        return fh.read(128).strip()
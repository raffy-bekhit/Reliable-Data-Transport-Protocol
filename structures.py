import struct

class packet:

    def __init__(self,length,seqno,data):
        self.length = struct.pack('H',length)
        self.seqno=struct.pack('I',seqno)
        self.data=data

        #data yet

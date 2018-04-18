import struct

class packet:

    def __init__(self,pkd_data=None,length=0,seqno=0,data=''):
        if pkd_data:
            var, data = self.unpack(pkd_data)
            self.length = var[0]
            self.seqno = var[1]
            self.data = data.decode()
        else:
            self.length = length
            self.seqno = seqno
            self.data = data


    def unpack(self, data):
        size = struct.calcsize('HI')
        print()
        print(size)
        return struct.unpack('HI', data[:size]), data[size:]

    def pack(self):
        encoded_data = self.data.encode()
        str_len = len(encoded_data)
        packet_length = len(self.data) + 6
        fmt ='HI%ds' % str_len
        packed_packet = struct.pack(fmt, packet_length,self.seqno,encoded_data)
        return packed_packet
import memoria as mem

def read(img):
   disco = open(img, 'rb')
   byte = disco.read(1)
   byte_address = 0
   while byte:
      mem.write_byte(byte_address, int.from_bytes(byte, "little"))
      byte = disco.read(1)
      byte_address += 1
   disco.close()

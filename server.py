import socket               # Import socket module

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)         # Create a socket object
host = socket.gethostname() # Get local machine name

file = open('server.in','r')

port = int(file.readline())
window_size = int(file.readline()) #in datagrams
random_seed = int(file.readline())
probability = float(file.readline())


port = 12348             # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5) # Now wait for client connection.
while True:
   c, addr = s.accept()     # Establish connection with client.

   print(addr)
   c.send('Thank you for connecting')
              # Close the connection


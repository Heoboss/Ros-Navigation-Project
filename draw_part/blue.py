from bluetooth import *

socket = BluetoothSocket( RFCOMM )
socket.connect(("98:DA:60:0B:96:AF", 1))
print("bluetooth connected!")

msg = input("send message : ")
socket.send(msg)

print("finished")
socket.close()

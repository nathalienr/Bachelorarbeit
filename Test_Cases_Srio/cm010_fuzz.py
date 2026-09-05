from boofuzz import *
session= Session(target=Target(connection=TCPSocketConnection("192.168.0.2", 80)))
s_initialize("request")
s_string("GET")
s_delim(" ")
s_string("/")
session.connect(s_get("request"))
session.fuzz()

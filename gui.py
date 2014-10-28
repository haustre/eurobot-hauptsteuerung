__author__ = 'mw'

import time
from ethernet import Client

def main():
    host = 'localhost'  #Test
    port = 42233        #Test
    data = {'message':'hello world!', 'test': 123.4}
    tcp = Client(host, port)
    tcp.write(data)
    while 1:
        data = tcp.read()
        if data:
            print(data)
            pass
        time.sleep(0.1)

main()
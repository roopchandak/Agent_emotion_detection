#!/usr/bin/python

import logging
from tlibclient import *
from tcpServer import *

#Global Flag for shutdown
gshutDown = False

def sigHandler(sig,frame):
  global gshutDown
  print("Signal Received - %d"%int(sig))
  gshutDown = True

signal.signal(signal.SIGINT,sigHandler)

FORMAT = "%(asctime)-15s %(levelname)s %(thread)d %(message)s"
logging.basicConfig(filename="pytlibclient.log",level=logging.DEBUG,format=FORMAT)
log = logging.getLogger("pytlibclient")

def main():
  try:
    logging.debug("Starting.....")
    sipServerIP = "172.24.130.40"
    sipServerPort = "7011"
    sipServerDN = "8989"
    tclient = TlibClient(sipServerIP,sipServerPort,sipServerDN)
    tclient.initialize()
    serverInst = serverSocket(9090,tclient)
    serverInst.createSocket()
    tclient.registerTCPServer(serverInst)
    while(not gshutDown):
      time.sleep(0.5)
    tclient.uninitialize()
    serverInst.destroySocket()
  except Exception as e:
    tclient.uninitialize()
    serverInst.destroySocket()
    print(e)

if __name__ == '__main__':
  main()
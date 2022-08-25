#!/usr/bin/python
import logging
import socket
import threading
from app import *

class serverSocket(threading.Thread):

  def __init__(self,localPort,tlibClient):
    threading.Thread.__init__(self)
    self._localPort = localPort
    self._serverSocket = None
    self._clientSocket = None
    self._shutDown = False
    self._tlibClient = tlibClient
    self._lock = threading.Lock()
    self._callEstablished = False

  def destroySocket(self):
    logging.debug("Destroying server...")
    self._shutDown = True
    if self._serverSocket:
      self._serverSocket.close()

  def createSocket(self):
    self._serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = socket.gethostbyname("0.0.0.0")
    try:
      self._serverSocket.bind((host,self._localPort))
      self._serverSocket.listen(1) #Max of one connection
      self.start()
    except Exception as e:
      print(e)
      logging.error(e)

  def sendDataToClient(self,onOFF):
    self._callEstablished = onOFF
    try:
      if self._clientSocket:
        if onOFF:
          self._clientSocket.send("EventStartVideo")
        else:
          self._clientSocket.send("EventStopVideo")
      else:
        logging.error("No active client connection to send events %s"%str(onOFF))
    except Exception as e:
      print(e)
      logging.error(e)

  def processClientSocket(self,clientSocket):
    self._clientSocket = clientSocket # In case of more than one connection the latest will be used
    self.sendDataToClient(self._callEstablished)
    while(not self._shutDown):
      try:
        data = self._clientSocket.recv(1024)
      except Exception as e:
        print(e)
        logging.error(e)
        break
      if data:
        self._tlibClient.dataFromRemote(data)
    if clientSocket:
      self._clientSocket.close()

  def run(self):
    while(not self._shutDown):
      clientSocket, clientAddress = self._serverSocket.accept()
      logging.debug("New connection received %s"%str(clientAddress))
      cThread = threading.Thread(target=self.processClientSocket,args=(clientSocket,))
      cThread.start()


if __name__ == '__main__':
  pass
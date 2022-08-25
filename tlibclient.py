#!/usr/bin/python
import logging
import os,sys
import signal
import threading
import time
import json
import app

gpath = os.path.realpath(__file__)
libpath = os.path.abspath(os.path.join(gpath,os.pardir))
sys.path.insert(0,os.path.join(libpath,"common_lib"))

#from gcti_cfg import *
from gcti_tlib.ptlib import *
#import common
from app import *


class TlibClient(threading.Thread):

  def __init__(self,sipServerHost,sipServerPort,sipDN):
    threading.Thread.__init__(self)
    self._sipServerHost = sipServerHost
    self._sipServerPort = sipServerPort
    self._sipDN = sipDN
    self._shutDown = False
    self.tlibServer = None
    self.connID = ""
    self._tcpserver = None
    self._videoInProgress = False

  def registerTCPServer(self,tcpServer):
    self._tcpserver = tcpServer

  def uninitialize(self):
    logging.debug("Uninitialzing tlib client....")
    self._shutDown = True

  def initialize(self):
    try:
      self.tlibServer = CreateTserverClient(self._sipServerHost, self._sipServerPort)
      if (self.tlibServer):
        self.tlibServer.RegisterAddress(self._sipDN)
      else:
        print("Tserver connection failed %s:%s"%(self._sipServerHost,self._sipServerPort))
    except Exception as e:
      print(e)
      exit(1)
    self.start()
    return True

  def reInitialize(self):
    try:
      self.tlibServer = CreateTserverClient(self._sipServerHost, self._sipServerPort)
      if(self.tlibServer):
        self.tlibServer.RegisterAddress(self._sipDN)
    except Exception as e:
      logging.error(e)
  
  def run(self):
    while (not self._shutDown):
      try:
        event = self.tlibServer.WaitEvent(timeout=1)
        if (event):
          print(event)
          logging.debug(str(event))
          if(event.Event == "Established"):
            self.connID = ConnIDToStr(event.ConnID)
            self._videoInProgress = True
            self.dataSendToRemote(self._videoInProgress)
          elif(event.Event == "Released"):
            if self._videoInProgress:
              self._videoInProgress = False
              self.dataSendToRemote(self._videoInProgress)
            # For testing added
            #self.sendUserEvent(pyDictUserData={'Emotion':'sad'})
      except Exception as e:
        logging.error(e)
        self.reInitialize()


  def sendUserEvent(self,connID=None,pyDictUserData={}):
    try:        
      userEvent = Event()
      userEvent.UserData = pyDictUserData
      userEvent.EventName = 'UserEvent'
      strConnID = ""
      if (connID):
        strConnID = StrToConnID(connID)
      else:
        strConnID = StrToConnID(self.connID)
      
      userEvent.ConnID = strConnID
      self.tlibServer.SendUserEvent(self._sipDN, userEvent)
    except Exception as e:
      print(e)
      logging.error(e)
    return True

  def dataFromRemote(self,data):
    try:
      if(data):
        pyDict = json.loads(data)
        strDict = {str(key):str("%.3f")%value for (key,value) in pyDict.items()}
        logging.debug(strDict)
        self.sendUserEvent(pyDictUserData=strDict)
      else:
        logging.error("No data")
    except Exception as e:
      print(e)
      logging.error(e)
    return True

  def dataSendToRemote(self,onOff):
    if self._tcpserver:
      self._tcpserver.sendDataToClient(onOff)
    else:
      logging.error("No TCP server to send data")
      return False
    return True

#def main():
#  tclient = TlibClient("172.24.130.40","7011","8989")
#  tclient.initialize()
#  while(not gshutDown):
#    time.sleep(0.5)

#if __name__ == '__main__':
#  main()

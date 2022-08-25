#
#                  === Access to ConfigLibrary ===
#
#
# - Implementsconvenient interface to ConfigLibrary
# - Define classes:
#  - CServer0
#    - CServer0 instance is ConfigServer client
#      - Several CServer0 instances can be used at the same time
#    - Methods are ConfigLibrary functions + some suplementary functions
#    - In function parametes all  enumeration values are substituted by EnumElem



import copy
import time
import re
import socket

from common  import *
from common_enum import *
from enum  import *
from conflib  import *
                            
_emptyRawEvent = (   
  0,                                     # "cfgServer",            
  0,                                     # "cfgEventType",           
  0,                                     # "cfgRequestID",      
  0,                                     # "cfgObjectType",     
  0,                                     # "dbid",
  None,                                  # "cfgObject",
  0,                                     # "cfgObjectCount",
  0,                                     # "cfgErrorCode
  0,                                     # "cfgTimestamp",       
  0,                                     # "cfgEventNumber",     
  None,                                  # "cfgDescription", 
  None                                   # "errorDescription
)




class CfgEvent:   


  eventEnumTbl = ( # Table used to create Event from raw CfgLib event.
                   # consist of (attr name, attr enum, function to get attr, default value, additional func to transform value) 

    
   ("cfgServer",             None), 
   ("cfgEventType",          CfgEventName),         
   ("cfgRequestID",          None),         
   ("cfgObjectType",         None),         
   ("DBID",                  None), 
   ("cfgObject",             None),  
   ("cfgObjectCount",        None),
   ("cfgErrorCode",          None),
   ("cfgTimestamp",          None),     
   ("cfgEventNumber",        None),         
   ("cfgDescription",        None),
   ("errorDescription",      None))          


                                   
                                   
  def __init__(self, rawEvent = None):
    """ Creates Event instance from rawEvent (CfgLibrary event)"""
 
    i = 0
    for (nm, en) in self.eventEnumTbl:
      if rawEvent:
        if en:
          setattr(self, nm, ValToEnumElem(en, rawEvent[i]))
        else:
          setattr(self, nm, rawEvent[i])
      else:
        setattr(self, nm, None)
      i = i+1


  def fldToStr(self, fldName):
    """ String representation on Event field"""
    val = getattr(self, fldName)
    if val:
      str = `val`
      return str

  def __repr__(self):
    str = ""
    for (nm, en) in self.eventEnumTbl:
      s = self.fldToStr(nm)
      if s: str = str + "%-17s = %s\n" % (nm, s)
    return str                            


class CServer0:
  def __init__(self):
    self.fd = -1
    self.eventQueue = []
    self.defaultTimeout = 15
  
  def ConnectionError(self):
    ConnectionError("ConfigServer")


  def OpenServerEx(self, host, port, userName = "default", password = "password", appName = "default", appType = CfgAppType.CFGSCE):
    PrintLog("Opening connection to Configuration Server %s, %s" %(host, port))
    self.fd = ConfOpenServerEx(host, port, appType.val, appName,  "password", userName, password) 
    if self.fd <= 0:
      OpenError("Can't open ConfigServer %s " % str((host, port)))
    return self.fd
  

  def CloseSocket(self):
    if self.fd == -1: return
    res = ConfCloseServer(self.fd)
    if res < 0:
      self.ConnectionError()
    self.fd = -1
  
  def GetLastErrorCode(self):
    return  ConfGetLastErrorCode()
      
  def WaitEvent(self, requestID = None, eventName = None, timeout = None):
    """ Wait event from CfgServer for this client and return the event as result"""
  

    if eventName and (type(eventName) <> type([])):
      eventName = [eventName]

    if not timeout:
      timeout = self.defaultTimeout

    i = 0 
    # Wait event from CfgServer
      
    ev = None
    otherEvCnt = 0
    found = 0  
    eventToPutBackList = []
    while i < len(self.eventQueue):   # Search event in self.eventQueue
      ev = self.eventQueue[i]
      if (not requestID ) or (requestID == ev.cfgRequestID): 

        del self.eventQueue[i]
        
        if (not eventName) or (ev.cfgEventType in eventName):
          found = 1    
          break      
        else:
          eventToPutBackList.insert(0, ev)
      else: 
        i = i+1
    if not found:
      # Wait event from CfgServer
      
      ev = None
      startedAt = time.time()
      while (not ev):
        if time.time() > startedAt + timeout: break
        rawEventSet = ConfReadEvent(self.fd, int(timeout)) 
        if rawEventSet:
          for rawEvent in rawEventSet:
            ev0 = CfgEvent(copy.deepcopy(rawEvent))
            if (not ev and ((not requestID ) or (requestID == ev0.cfgRequestID))):
              if (not eventName) or (ev0.cfgEventType in eventName):
                ev = ev0
              else:
                eventToPutBackList.insert(0, ev0)
            else: 
              self.eventQueue.append(ev0) 
        time.sleep(0.01)
    for ev1 in eventToPutBackList:
      self.PutBackEvent(ev1)     
    #print ev
    return ev   


  def PutBackEvent(self, event):
    """ Put event back to self.eventQueue - operation reverse to WaitEvent."""
    self.eventQueue.insert(0, event)  
  
  
  
  
  def RegisterObjectType(self, objectType):
    res = ConfRegisterObjectType(self.fd, objectType.val)
    if res < 0:
      self.ConnectionError()
      
  def RegisterObjectTypeEx(self, subscription = {}):
    res = ConfRegisterObjectTypeEx(self.fd, subscription)
    #print "Registering %s" %subscription
    if res < 0:
      self.ConnectionError()      


  def SetAccount(self, appDBID, dbid, objectType):
    """Return value - int"""
    res = ConfSetAccount(self.fd,  appDBID, 9, dbid, objectType.val)
    if type(object) is type(0):
      if res < 0:
        FatalError("Error in GetACLAsync")
    return res
  
  def GetACLAsync(self, csid, dbid, objectType):
    """Return value - int """
    res = ConfGetACLAsync(self.fd, csid, dbid, objectType.val)
    if type(object) is type(0):
      if res < 0:
        FatalError("Error in GetACLAsync")
    return res
  
  def GetACL(self, csid, dbid, objectType):
    """Return value - string object"""
    object = ConfGetACL(self.fd, csid, dbid, objectType.val)
    if type(object) is type(0):
      if object < 0:
          FatalError("Error in GetACL")
    if GetOption("PrintConfigDebugInfo"):
      print "GetACL"
      print object        
          
    return object  


  def SetACL(self, ACL, isRecursive):
    """Return value - string object"""
    if GetOption("PrintConfigDebugInfo"):
      print "SetACL"
      print ACL
    status = ConfSetACL(self.fd, ACL, isRecursive)
    if status < 0:
      FatalError("Error in SetACL")
    return status     
  
  def GetObjectInfo(self, objectType, filter):
    """Return value - list of string objects in case of success, int < 0 in case of fail"""
    if GetOption("PrintConfigDebugInfo"):
      print "GetObjectInfo, filter %s" %filter
    objects = ConfGetObjectInfo(self.fd, objectType.val, filter)
    if type(objects) is type(0):
      if objects < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
        FatalError("Error in ConfGetObjectInfo")
    if GetOption("PrintConfigDebugInfo"):
      for ob in objects:
        print ob        
    return objects
  
  def GetObjectInfoAsync(self, objectType, filter):
    """Return value - int > 0, int < 0 in case of fail"""
    if GetOption("PrintConfigDebugInfo"):
      print "GetObjectInfo, filter %s" %filter
    status = ConfGetObjectInfoAsync(self.fd, objectType.val, filter)
    if status < 0:
      FatalError("Error in GetObjectInfoAsync")
    return status   
  

  def GetObjectCount(self, objectType, filter):
    """Return value - int > 0, int < 0 in case of fail"""
    if GetOption("PrintConfigDebugInfo"):
      print "GetObjectInfo, filter %s" %filter
    status = ConfGetObjectCount(self.fd, objectType.val, filter)
    if status < 0:
      FatalError("Error in ConfGetObjectCount")
    return status   
  
  
  def ChangeObject(self, objectType, oldObject, newObject):
    """Return value - int > 0, int < 0 in case of fail"""
    if Synchronizer().GetControlStatus() == Monitor and Synchronizer().GetCommonTServer() and oldObject <> newObject:
      return 1
    
    if GetOption("PrintConfigDebugInfo"):
      print "ChangeObject"
      print "***********OldObj***********"
      print     oldObject
      print "***********NewObj***********"
      print newObject 
          
    if oldObject == newObject: 
      print "objs are identical"
      return 0


    status = ConfChangeObject(self.fd, objectType.val, oldObject, newObject)
    if status < 0:
      #try one more time
      time.sleep(1)
      Message("Unsuccessful ConfChangeObject. Trying one more time...")
      status = ConfChangeObject(self.fd, objectType.val, oldObject, newObject)
      if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
        FatalError("Error in ConfChangeObject")
    return status    
    

  def AddObject(self, objectType, object):
    """Return value - int > 0, int < 0 in case of fail"""
    if Synchronizer().GetControlStatus() == Monitor and Synchronizer().GetCommonTServer():
      return 1        
    status = ConfAddObject(self.fd, objectType.val, object)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in ConfAddObject", beep = 0)
    return status        
    

  def AddObjectEx(self, objectType, folderDBID, object):
    """Return value - int > 0, int < 0 in case of fail"""
    if Synchronizer().GetControlStatus() == Monitor and Synchronizer().GetCommonTServer():
      return 1        
    status = ConfAddObjectEx(self.fd, objectType.val, folderDBID, object)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in ConfAddObjectEx")
    return status
    
  def DeleteObject(self, objectType, dbid):
    """Return value - int > 0, int < 0 in case of fail"""
    if Synchronizer().GetControlStatus() == Monitor and Synchronizer().GetCommonTServer():
      return 1        
    status = ConfDeleteObject(self.fd, objectType.val, dbid)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in ConfDeleteObject", beep = 0)
    return status   
    

      
  def GetObjectDBIDFromString(self, strObj):
    pattern = "\035" + "DBID" + "=([0-9]+)"
    matchObj = re.search(pattern, strObj)
    if matchObj:
      return int(matchObj.group(1))
    else:
      ProgrammError("Cannot retrieve object property: DBID")      
    return int(matchObj.group(1))       
      
      
  def GetObjectCharPropertyFromString(self, strObj, propName):
    pattern = "\030" + propName + "=\037([^\030\031\032\033\035\036\037]*)\037"
    matchObj = re.search(pattern, strObj)
    if matchObj:
      return matchObj.group(1)    
    else:
      ProgrammError("Cannot retrieve object property: %s" % propName)      
      
  def GetObjectIntPropertyFromString(self, strObj, propName):
    pattern = "\030" + propName + "=([0-9\-]+)"
    matchObj = re.search(pattern, strObj)
    if matchObj:
      return int(matchObj.group(1))
    else:
      ProgrammError("Cannot retrieve object property: %s" % propName)      

  
  def GetObjectCharPropertyByObjectTypeAndDBID(self, propName, objType, dbid):
    if objType == CfgObjectType.CFGTenant and dbid == 1 and propName == "name": 
      return "Environment"
    objects = self.GetObjectInfo(objType, {"dbid": dbid})
    if len(objects) <> 1:                                         #should be only one object
      FatalError("Incorrect number of objects: %s, filter: {\"dbid\": %d }, object type: %s" % (len(objects), dbid, objType))
    strObj = objects[0]  
    return self.GetObjectCharPropertyFromString(strObj, propName)

      
  def GetObjectIntPropertyByObjectTypeAndDBID(self, propName, objType, dbid):
    objects = self.GetObjectInfo(objType, {"dbid": dbid})
    if len(objects) <> 1:                                         #should be only one object
      FatalError("Incorrect number of objects: %s, filter: {\"dbid\": %d }, object type: %s" % (len(objects), dbid, objType))
    strObj = objects[0]  
    return self.GetObjectIntPropertyFromString(strObj, propName)
   
      
  def GetObjectDBID(self, objType, filtr):
    if objType == CfgObjectType.CFGTenant and filtr == {"name": "Environment"}:
      return 1
    objects = self.GetObjectInfo(objType, filtr)
    if len(objects) <> 1:                                         #should be only one object
      FatalError("Incorrect number of objects: %s, filter: %s, object type: %s" % (len(objects), filtr, objType))
    strObj = objects[0]   
    return self.GetObjectDBIDFromString(strObj)

  def GetObjectNameByObjectTypeAndDBID(self, objType, dbid):
    if objType == CfgObjectType.CFGTenant and dbid == 1: 
      return "Environment"
    objects = self.GetObjectInfo(objType, {"dbid": dbid})
    if len(objects) <> 1:                                         #should be only one object
      FatalError("Incorrect number of objects: %s, filter: {\"dbid\": %d }, object type: %s" % (len(objects), dbid, objType))
    strObj = objects[0]   
    return self.GetObjectCharPropertyFromString(strObj, "name")
      
  def GetObjectTenantNameByObjectTypeAndDBID(self, objType, dbid):
    objects = self.GetObjectInfo(objType, {"dbid": dbid})
    if len(objects) <> 1:                                         #should be only one object
      FatalError("Incorrect number of objects: %s, filter: {\"dbid\": %d }, object type: %s" % (len(objects), dbid, objType))
    strObj = objects[0]   
    pattern = "\030tenantDBID=([0-9]+)"
    matchObj = re.search(pattern, strObj)
    if matchObj:
      return self.GetObjectNameByObjectTypeAndDBID(CfgObjectType.CFGTenant, int(matchObj.group(1)))
    else:
      ProgrammError("Object does not have property tenantDBID: %s, object type: %s" % (dbid, objType))      

  def GetObjectSwitchNameByObjectTypeAndDBID(self, objType, dbid):
    objects = self.GetObjectInfo(objType, {"dbid": dbid})
    if len(objects) <> 1:                                         #should be only one object
      FatalError("Incorrect number of objects: %s, filter: {\"dbid\": %d }, object type: %s" % (len(objects), dbid, objType))
    strObj = objects[0]   
    pattern = "\030switchDBID=([0-9]+)"
    matchObj = re.search(pattern, strObj)
    if matchObj:
      return self.GetObjectNameByObjectTypeAndDBID(CfgObjectType.CFGSwitch, int(matchObj.group(1)))
    else:
      ProgrammError("Object does not have property switchDBID: %s, object type: %s" % (dbid, objType))                  
      
  def SetPrintDebugInfo(self, val):
    ConfSetPrintDebugInfo(val)
    
  def PrepareClient(self, thisApplicationDBID, thisHostDBID, connDBID,
                    serverApplicationDBID, serverHostDBID):
    """all args - dbids"""                
    return ConfPrepareClient(self.fd, thisApplicationDBID, thisHostDBID, connDBID,
                    serverApplicationDBID, serverHostDBID)
    
  def OpenServerNew(self, previousServer, host, port, appType = CfgAppType.CFGSCE, appName = "default", appPassword = "password", userName= "default", password = "password"):
    """
    Parameters
      previousServer - int,
      host - str,
      port - str
      appType - enum CfgAppType,
      appName = str,
      appPassword - str,
      userName - str,
      password = - str,
    return
      fd - int
    """
    PrintLog("Opening connection (new) to Configuration Server %s %s, %s, %s, %s" %(previousServer, host, port, userName, password))
    self.fd = ConfOpenServerNew(previousServer, host, port, appType.val, appName,  appPassword, userName, password) 
    if self.fd <= 0:
      print "_________"
      print ConfGetLastErrorCode()
      print "_________"
      OpenError("Can't open ConfigServer %s " % str((host, port)))
    return self.fd
  
  def GetHistoryLog(self, timeStamp):
    """
    Parameters
      timeStamp - int;
    return
      status - int
    """
    status = ConfGetHistoryLog(self.fd, timeStamp)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in GetHistoryLog")    
    return status

  def SetOperationalMode(self, opMode):
    """
    Parameters
      opMode - enum CfgOperationalMode
    return
      status - int
    """
    status = ConfSetOperationalMode(self.fd, opMode.val)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in SetOperationalMode")
    return status

  def GetOperationalMode(self):
    """
    Parameters
    return
        status - int, opMode or -1
    """
    status = ConfGetOperationalMode(self.fd)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in GetOperationalMode")
    return status
  
  def GetHistoryLogByNumber(self, eventNumber):
    """
    Parameters:
      eventNumber - int;
    Return:
      status - int
    """
    status = ConfGetHistoryLogByNumber(self.fd, eventNumber)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in GetHistoryLogByNumber")    
    return status     
      
  def ConfCompareObject(self, objectType, oldObject, newObject):
    """
    Parameters:
      objectType - enum CfgObjectType;
      oldObject - str
      newObject - str
    Return:
      status - int, 1 if objects are different, 0 if identical 
    """

    if GetOption("PrintConfigDebugInfo"):
      print "CompareObject"
      print "***********OldObj***********"
      print     oldObject
      print "***********NewObj***********"
      print newObject 
          
    status = ConfCompareObject(objectType.val, oldObject, newObject)
    if status < 0 and not InTrue(GetOption("IgnoreCfgErrors")):
      FatalError("Error in ConfCompareObject")
    return status 
    
  def DiffObject(self, objectType, oldObject, newObject):
    """
    Parameters:
      objectType - enum CfgObjectType;
      oldObject - str
      newObject - str
    Return:
      delta - str
    """
  
    delta = ConfDiffObject(objectType.val, oldObject, newObject)
    if type(delta) is type(0):
      if delta < 0:
        FatalError("Error in ConfDiffObject")
    return delta
  
  def UpdateObject(self, objectType, oldObject, delta):
    """
    Parameters:
      objectType - enum CfgObjectType;
      oldObject - str
      delta - str (should be got by DiffObject)
    Return:
      newObject - str
    """

    if GetOption("PrintConfigDebugInfo"):
      print "UpdateObject"
      print "***********OldObj***********"
      print     oldObject
      print "***********Delta***********"
      print delta 
          
    newObject = ConfUpdateObject(objectType.val, oldObject, delta)
    if GetOption("PrintConfigDebugInfo"):
      print "UpdateObject"
      print "***********NewObj***********"
      print newObject
    return newObject     

#-----------------------------------------------------------
# Function not related to CS, but to Lib only
#-----------------------------------------------------------

def PrepareConnParams(host, port):
  return ConfPrepareConnParams(host, int(port))         
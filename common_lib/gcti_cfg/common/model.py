

import string
import sys
import copy
import time
import re
import os

from common                 import *
from common_enum            import *
from enum                   import *



import model_logtracer        

import StringIO          

#==================================================================================
#
#                  === Abstract Container model ===
#
#
#==================================================================================



class Container:
  def __init__(self):
    self.ObjectList = []   
    self.Statistics = ""
    self.warnings = 0
    self.errors = 0    
    self.errorCounts = 0
    self.initObjectsFunction = None
    self.preTestResetFunction = None
    self.type = None
    self.globalName= ""  
    self.copyObjectList = []
    
  def __getitem__(self, i):
    """To make calls like
       for item in container:
         item.DoSomething()
    """
    return self.ObjectList[i] 

  def addToObjectList(self, obj):
    obj.pyObjectType = obj.__class__.__name__
    self.ObjectList.append(obj)

  def getObjectsByClassName(self, objClassName):
    objList = []
    for obj in  self.ObjectList:
      if obj.pyObjectType == objClassName:
        objList.append(obj)
    return objList
    
  def Open(self, toPrimOnly = 0):
    pass
    
  def Close(self):
    self.CloseObjectList()

    

  def InitOwnObjects(self, resetObjList = 1):
    if not self.initObjectsFunction: return
    if resetObjList:
      self.ObjectList = []
    apply(self.initObjectsFunction, ())
    
  def PreTestReset(self):
    if not GetOption("PretestReset") or not self.preTestResetFunction: return
    apply(self.preTestResetFunction, ())      


  def CloseObjectListNoCleanUp(self):  # should be rewritten in inherited containers
    pass
  
  def SaveConfigState(self):
    for obj in self.ObjectList:
      if hasattr(obj, "SaveConfigState"):
        obj.SaveConfigState()
    if self.cfgApp:
      self.cfgApp.SaveState()
    if self.cfgBackupApp:
      self.cfgBackupApp.SaveState()      
      
  def RestoreConfigState(self):
    startTime = time.time()
    for obj in self.ObjectList:
      if hasattr(obj, "RestoreConfigState"):
        obj.RestoreConfigState()
    if self.cfgApp:
      self.cfgApp.RestoreState()
    if self.cfgBackupApp:
      self.cfgBackupApp.RestoreState()
    PrintLog("RestoreConfigState lasted %s sec"%(time.time() - startReset))
  
    
  def CloseObjectList(self):  # should be rewritten in inherited containers
    self.copyObjectList = copy.copy(self.ObjectList)
    for obj in self.ObjectList:
      if hasattr(obj, "Close"):
        try:
          obj.Close()
        except:        #try to close all objects
          pass  
      if hasattr(obj, "getStat"):
        self.Statistics = self.Statistics + obj.getStat()    
    self.ObjectList = []     
    
  def SemiCloseObjectList(self):  
    """ SemiClose each object and set ObjectList = []
    """
    self.copyObjectList = copy.copy(self.ObjectList)
    for obj in self.ObjectList:
      if hasattr(obj, "SemiClose"):
        obj.SemiClose()  
    if hasattr(self, "AgentList"):
      for obj in self.AgentList:
        obj.SemiClose()      
    self.ObjectList = []    
    
  def ClearObjectList(self):
    for obj in self.ObjectList:
      if hasattr(obj, "Clear"):
        obj.Clear()
      
  def UsualCleanUp(self):
    for obj in self.ObjectList:
      if hasattr(obj, "UsualCleanUp"):
        obj.UsualCleanUp()            

 
  def getStatistics(self):
    stat = ""
    if self.warnings:
      stat = stat + ("\n  Warnings              - %5d" % self.warnings)
      stat = stat + ("\n")
    if  self.errors:
      stat = stat + ("\n  Errors                - %5d" % self.errors)
      stat = stat + ("\n")
    self.Statistics = stat
    return self.Statistics
    
  def printStat(self):
    PrintStat(self.getStatistics(), 1)
    

#==================================================================================
#
#                  === Abstract Server model ===
#
#
#==================================================================================

_defaultServerContainer = None


def ServerContainer():
  global _defaultServerContainer
  if not _defaultServerContainer:
    _defaultServerContainer = Container()
  return _defaultServerContainer
  
def FindServerByCfgAppType(cfgAppType):
  for obj in ServerContainer():
    if obj.cfgApp and obj.cfgApp.type == cfgAppType.val:
        return obj
        
def FindLastServerByCfgAppType(cfgAppType):
  sc = copy.copy(ServerContainer().ObjectList)
  sc.reverse()
  for obj in sc:
    if obj.cfgApp and obj.cfgApp.type == cfgAppType.val:
        return obj        
        
def FindTserverByCSName(name):        
  for server in ServerContainer():
    if server.cfgApp and server.cfgApp.type == CfgAppType.CFGTServer.val and server.cfgApp.name == name:
      return server

def GetServersByType(type):
  objs = []
  for obj in ServerContainer():
    if obj.appGCTIType == type:
      objs.append(obj)
  return objs 
  
def GetServersExcept(objTypes = []):
  objs = []
  for obj in ServerContainer():
    if not (obj.appGCTIType in objTypes):
      objs.append(obj)
  return objs      


    
def AddToServerContainer(obj):
  index = len(ServerContainer().ObjectList)#by default - place at the end
  if obj.cfgApp and type(obj.cfgApp) != types.StringType:
    app = None
    if obj.cfgApp.type == CfgAppType.CFGConfigurationServer.val: # 1
      index = 0
    elif obj.cfgApp.type == CfgAppType.CFGSCS.val: #2
      app = FindServerByCfgAppType(CfgAppType.CFGConfigurationServer)
    elif obj.cfgApp.type == CfgAppType.CFGRealDBServer.val:
      app = FindServerByCfgAppType(CfgAppType.CFGSCS) #3 place after SCS, if no SCS place after CS
      if not app:
        app = FindServerByCfgAppType(CfgAppType.CFGConfigurationServer) #3
      
    elif obj.cfgApp.type == CfgAppType.CFGTServer.val:
      app = FindLastServerByCfgAppType(CfgAppType.CFGRealDBServer) #4
    else:
      app = FindLastServerByCfgAppType(CfgAppType.CFGTServer) # all others after tservers
    if app:
      index = ServerContainer().ObjectList.index(app) + 1 
  ServerContainer().ObjectList.insert(index, obj)  

class AbstractServer(Container):
  def __init__(self, cfgApp = None):
    Container.__init__(self)
    self.warBadOtherCnt              = 0    
    self.errBadOtherCnt              = 0
    self.serErrBadOtherCnt           = 0
    self.warUnreadEvCnt              = 0
    self.ActionOnUnexpectedEvent     = self.actionOnUnexpectedEvent
    self.ActionOnNoEvent             = self.actionOnNoEvent   
    self.ActionOnUnexpectedProtocolEvent = self.actionOnUnexpectedProtocolEvent
    self.oldActionOnUnexpectedEvent   = None
    self.oldActionOnNoEvent          = None
    self.oldActionOnUnexpectedProtocolEvent = None
    self.originalActionOnUnexpectedEvent = None
    self.ActionOnEUE                 = self.actionOnEUE
    self.cfgApp                      = cfgApp
    self.appType                     = "AbstractServer"
    self.appGCTIType                 = ""
    self.cfgBackupApp                = None
    #self.ObjectList                 = []           # list of objects that belong to this server
    self.Host                        = ""           #either host and port or sectionName should be set
    self.Port                        = ""
    self.sectionName                 = ""
    self.serverInfo                  = None
     
    self.fd                          = -1
    self.appVersion                  = ""
    self.countErrorsAndWarnings      = 1             # set to 0 in reset between tests
    self.testAttrMask                = {}
    self.logFileDir                  = ""
    self.logFileName                 = ""
    self.LogTracer                   = None
    self.testMarker                  = None
    self.forceMarker                 = None
    self.ResetAfterTestSet           = (TestResEnum.SeriousError, TestResEnum.ForceReset) 
    self.testRes                     = ()
    self.doNotTest                   = False
    self.connectTo                   = 1
    self.opened                      = 0
    self.cfgType                     = None
    self.cfgName                     = ""
    self.viaProxy                    = 0
    self.dbMessageServerLogTable     = None
    self.startBeforeTest             = NotDefined
    self.startAfterTest              = NotDefined
    self.startBeforeTestBack         = NotDefined
    self.startAfterTestBack          = NotDefined
    self.optionsCaseSensitive        = False
                     
    if self.cfgApp:
      self.cfgType = ValToEnumElem(CfgAppType, self.cfgApp.type)
      self.cfgName = self.cfgApp.name   

    self.dependableServers           = []
    #Container for the servers (basicaly list of servers) is created when first server is initialized
    self.container = ServerContainer()
    AddToServerContainer(self)
  
  def __repr__(self):
    type = self.cfgType
    if not self.cfgType: type = ""
    return "Server %s %s %s" %(self.globalName, type, self.cfgName)
    
  def actionOnUnexpectedEvent(self, arg1 = None, arg2 = None, arg3 = None):
    pass
    
  def actionOnNoEvent(self, eventName = None, arg2 = None, arg3 = None):
    pass      

  def actionOnNoEventInInit(self, eventName = None, arg2 = None, arg3 = None):
    pass
    
  def actionOnUnexpectedProtocolEvent(self, arg1 = None, arg2 = None, arg3 = None):
    pass
    
  def actionOnUnexpectedEventInGetUnread(self, *args, **keywords):
    pass
    
  def WaitUnreadEvents(self, timeout = None):  
    pass
  
  def actionOnEUE(self, *args, **keywords):
    pass
  
  def AfterSwitchover(self):
    pass

  def handleEvent(self, eventName, timeout = 5):
    #for compatibility 
    return self.HandleEvent(eventName, timeout)
  
  def HandleEvent(self, eventName, timeout = 5, shift = 4*" "):
    """Waits for specified event, prints it to log,
      if event is not received during timeout current actionOnNoEventis called
      parameters:
        eventName - enum element (specific by server)
        timeout   - int
      return:     - event
        
    """
    PrintLog("\n  Waiting: %s" % eventName)
    ev = self.WaitEvent(eventName = eventName, timeout = timeout)  
    if not ev:
      if self.ActionOnNoEvent:
        self.ActionOnNoEvent(eventName = eventName)
        return
    s = "%s" %shift + ev.__repr__()
    s = string.replace(s, "\n", "\n%s"%shift)
    PrintLog("Received:\n" + s)      

    #no verifications here
    return ev    

    
  def SetOptions(self, options = {}):
    for key in options.keys():
      if getattr(self, key):
        cfgOpt = 0
        if self.cfgApp and self.cfgApp.options:
          for section in self.cfgApp.options.keys():
            if  self.cfgApp.options[section].has_key(string.replace(key, "_","-")):
              # we cannot "force" cfg options
              ProgrammWarning("Cfg option %s cannot be overwritten " %key)
              cfgOpt = 1
              break
        if not cfgOpt: setattr(self, key, options[key])
        
  def SemiClose(self):
    self.SemiCloseObjectList()
    
  def InitOwnObjects(self, resetObjList = 1):
    if not self.initObjectsFunction:
      return
    PrintLog("Executing %s" %self.initObjectsFunction.__name__)
    self.oldActionOnNoEvent   = self.ActionOnNoEvent
    self.ActionOnNoEvent = self.actionOnNoEventInInit
    self.oldActionOnUnexpectedEvent   = self.ActionOnUnexpectedEvent
    self.ActionOnUnexpectedEvent = None
    if resetObjList:
      self.ObjectList = []
    try:
      apply(self.initObjectsFunction, ()) #second arg for compatibility with jython
      self.saveInitialObjectStates()
    finally: 
      self.ActionOnNoEvent = self.oldActionOnNoEvent
      self.ActionOnUnexpectedEvent = self.oldActionOnUnexpectedEvent  

  def PreTestReset(self):
    if InFalse(GetOption("PretestReset")) or not self.preTestResetFunction: return
    self.oldActionOnUnexpectedEvent   = self.ActionOnUnexpectedEvent
    self.ActionOnUnexpectedEvent = None  
    try:
      self.ActionOnUnexpectedEvent
      apply(self.preTestResetFunction, ())     

    finally:
      self.ActionOnUnexpectedEvent = self.oldActionOnUnexpectedEvent 

     
  
  def ResetObjects(self, seriousReset = 0):
    if seriousReset:
      self.oldActionOnNoEvent   = self.ActionOnNoEvent
      self.ActionOnNoEvent = None
      self.oldActionOnUnexpectedEvent   = self.ActionOnUnexpectedEvent
      self.ActionOnUnexpectedEvent = None
      self.oldCountErrorsAndWarnings = self.countErrorsAndWarnings
      self.CountErrorsAndWarnings = 0
    try:
      if seriousReset:
        self.ClearObjectList()
      else:
        self.UsualCleanUp()
    finally: 
      if seriousReset:
        self.ActionOnNoEvent = self.oldActionOnNoEvent
        self.ActionOnUnexpectedEvent = self.oldActionOnUnexpectedEvent
        self.CountErrorsAndWarnings = self.oldCountErrorsAndWarnings  
        
  
  def ClearQueue(self):
    pass

  def GetUnprocessedEvents(self, unexpected = 0, timeout = 1): 
    self.oldActionOnUnexpectedEvent = self.ActionOnUnexpectedEvent
    self.oldActionOnUnexpectedProtocolEvent = self.ActionOnUnexpectedProtocolEvent
    if unexpected == 1:
      self.ActionOnUnexpectedEvent = self.actionOnUnexpectedEvent
      self.ActionOnUnexpectedProtocolEvent = self.actionOnUnexpectedProtocolEvent
    elif unexpected == 0:
      self.ActionOnUnexpectedEvent = self.actionOnUnexpectedEventInGetUnread
      self.ActionOnUnexpectedProtocolEvent = None

    self.WaitUnreadEvents(timeout = timeout)
    self.ActionOnUnexpectedEvent = self.oldActionOnUnexpectedEvent 
    self.ActionOnUnexpectedProtocolEvent = self.oldActionOnUnexpectedProtocolEvent      
      
      
  def saveInitialObjectStates(self):
    pass
  
  def getStatistics(self):   #can be rewritten in child classes. Now it differs from Container printStat, since the stat is per server, not per object.
    stat = ""
    if self.serErrBadOtherCnt:
      stat = stat + ("\n  Serious Errors:           - %5d" % self.serErrBadOtherCnt)
      stat = stat + ("\n")       
    if self.warBadOtherCnt:
      stat = stat + ("\n  Warnings:                 - %5d" % self.warBadOtherCnt)
      stat = stat + ("\n")
    if self.errBadOtherCnt:
      stat = stat + ("\n  Errors:                   - %5d" % self.errBadOtherCnt)
      stat = stat + ("\n")
  
    self.Statistics = stat
    return (self.Statistics)    
  
  def GetDoNotTest(self):
    if self.doNotTest or InTrue(GetOption("DoNotTest")): # self or global donottest is set
      return 1
    return 0
    
  def SetDoNotTest(self, val = 1):
    self.doNotTest = val
  
  def countFaults(self, eventName, fldName, eventTestRes):
    if self.GetDoNotTest(): return
    if not self.countErrorsAndWarnings: return
    fldInf = ("    expected value :%s\n" % `eventTestRes[0]` + 
              "    received value :%s\n" % `eventTestRes[1]`) 

    self.warBadOtherCnt       = self.warBadOtherCnt+1

    self.Warning("Bad field %s in %s" % (fldName, eventName), fldInf)      
  
  
  
  def testValue(self, value = None, expectedValue = None,  description = "", error = 0,
                errCnt = None, forceReset = -1, exactMatch = 1):

    if self.GetDoNotTest(): return
    bad, fldInf = testValue(value, expectedValue, description, error, errCnt, forceReset, exactMatch, byServer = 1)
    if bad:
      if error == 1:
        if errCnt == None: # not specififed
          self.errBadOtherCnt       = self.errBadOtherCnt+1
        else:
          errCnt = errCnt + 1
        self.Error(description, fldInf)
      elif error == 2:
        if errCnt == None:
          self.serErrBadOtherCnt       = self.serErrBadOtherCnt + 1
        else:
          errCnt = errCnt + 1           
        self.SeriousError(description, fldInf, forceReset = forceReset)
      elif error == 3:
        FatalError(description, fldInf)        
      elif error == 0:
        if errCnt == None:
          self.warBadOtherCnt       = self.warBadOtherCnt+1
        else:
          errCnt = errCnt + 1          
        self.Warning(description, fldInf)
      else:
        ProgramWarning("incorrect value of error parameter in TestValue")    
    return bad

  def testKVListValue(self, value = {}, expectedValue = {},  description = "", error = False, errCnt = None,
                      forceReset = -1, exactMatch = 1):
    if self.GetDoNotTest(): return 
    fldInf = testKVListValue(value, expectedValue, description, error, errCnt, forceReset, exactMatch, byServer = 1)
    if fldInf:
      if error == 1:
        if errCnt == None: # not specififed
          self.errBadOtherCnt       = self.errBadOtherCnt+1
        else:
          errCnt = errCnt + 1
        self.Error(description, fldInf)
      elif error == 2:
        if errCnt == None:
          self.serErrBadOtherCnt       = self.serErrBadOtherCnt + 1
        else:
          errCnt = errCnt + 1           
        self.SeriousError(description, fldInf, forceReset = forceReset)
      elif error == 0:
        if errCnt == None:
          self.warBadOtherCnt       = self.warBadOtherCnt+1
        else:
          errCnt = errCnt + 1          
        self.Warning(description, fldInf)
    return fldInf
  
  def VerifyValue(self, receivedValue, expectedValue,  description = "", error = 0, errCnt = None,
                  forceReset = -1, exactMatch = 1):
    """Universal method to check value for server
       receivedValue - any type, received value
       expectedValue - any type, expected value
                       if expectedValue is dictionary type, values are verified per key, 
                       extra keys present in received value are ignored
       description - string, error/warning description
       error - 0, 1, 2, indicates if incorrect value is error (1),serious error (2) or warning (0)
       errCnt - specific error counter. If not specified, errBadOtherCnt/serErrOtherCnt/warBadOtherCnt is used
       exactMatch - boolean, defines if values should match exactly. exactMatch 0 is applicable for strings only.
    """
    if type(expectedValue) == type ({}):
      return self.testKVListValue(receivedValue, expectedValue,  description, error, errCnt, forceReset, exactMatch)
    else:
      return self.testValue(receivedValue, expectedValue,  description, error,  errCnt, forceReset, exactMatch)
 
  def DetectError(self, description, errCnt = None):
    """Universal method to indicate error for server
       description - string, error description
       errCnt - specific error counter. If not specified, errBadOtherCnt is used
    """
    self.testValue(description = description, error = 1, errCnt = errCnt)
 
  def DetectSeriousError(self, description, errCnt = None, forceReset = -1 ):
    """Universal method to indicate Serious error for server
       description - string, error description
       errCnt - specific error counter. If not specified, errBadOtherCnt is used
    """
    self.testValue(description = description, error = 2, errCnt = errCnt, forceReset = forceReset)
    
  def DetectWarning(self, description, errCnt = None):
    """Universal method to indicate error for server
       description - string, warning description
       errCnt - specific warning counter. If not specified, warBadOtherCnt is used
    """    
    self.testValue( description = description, error = 0, errCnt = errCnt)
    
  
  def FindPrimaryScsApp(self):
    if self.cfgApp and self.cfgApp.scsObj and self.cfgApp.scsObj.appWorkMode == AppRunMode.APP_RUNMODE_PRIMARY:
      return self.cfgApp.scsObj
    elif self.cfgApp.backupApp and self.cfgApp.backupApp.scsObj and self.cfgApp.backupApp.scsObj.appWorkMode == AppRunMode.APP_RUNMODE_PRIMARY:
      return self.cfgApp.backupApp.scsObj
    else:
      ProgrammWarning("No primary application is running")

  def RestartPrimary(self, timeout = 2):
    prim = None
    if self.cfgApp and self.cfgApp.scsObj and self.cfgApp.scsObj.appWorkMode == AppRunMode.APP_RUNMODE_PRIMARY:
      if not self.cfgApp.backupApp or not self.cfgApp.backupApp.scsObj or not self.cfgApp.backupApp.scsObj.status == AppLiveStatus.SCS_APP_STATUS_RUNNING:
        ProgrammWarning("RestartPrimary: no backup application is running")
        return
      else:
        prim = self.cfgApp.scsObj
    elif self.cfgApp.backupApp and self.cfgApp.backupApp.scsObj and self.cfgApp.backupApp.scsObj.appWorkMode == AppRunMode.APP_RUNMODE_PRIMARY:
      prim = self.cfgApp.backupApp.scsObj
    else:
      ProgrammWarning("RestartPrimary: no primary application is running")
    if prim:
      prim.Stop()
      time.sleep(timeout)
      prim.Start()
    

  def FindPrimaryCfgApp(self):
    if self.cfgApp and self.cfgApp.scsObj and self.cfgApp.scsObj.appWorkMode == AppRunMode.APP_RUNMODE_PRIMARY:
      return self.cfgApp
    elif self.cfgApp.backupApp and self.cfgApp.backupApp.scsObj and self.cfgApp.backupApp.scsObj.appWorkMode == AppRunMode.APP_RUNMODE_PRIMARY:
      return self.cfgApp.backupApp
    else:
      ProgrammWarning("No primary application is running")    

  def CheckUnsupported(self, funcSource):
    return 0

  def OpenConnection(self, toPrimOnly = 0):
    if self.cfgApp:
      PrintLog ("Opening connection to %s, host %s, port %s" %(self.cfgApp.name, self.cfgApp.Host, self.cfgApp.Port))
    
  def CloseSocket(self):
    pass
  
  def Open(self, toPrimOnly = 0):
    self.OpenConnection(toPrimOnly)           
    self.SetLogTracer()
    self.opened = 1
    
  def Close(self):
    """Close object list, close connection"""
    PrintLog("Closing server %s" %self)
    self.CloseObjectList()
    self.CloseSocket()
    if self.LogTracer:
      self.LogTracer.Close()  
    self.opened = 0
    
  def CloseNoCleanUp(self):
    self.SemiCloseObjectList()
    self.CloseSocket()
    if self.LogTracer:
      self.LogTracer.Close()  
    self.opened = 0   
    
  def Erase(self):
    self.Close()
    if self in self.container.ObjectList:
      self.container.ObjectList.remove(self)
    
  def SilentErase(self):    
    self.SemiCloseObjectList()
    self.CloseSocket()
    if self in self.container.ObjectList:
      self.container.ObjectList.remove(self)    
    
    
  def Start(self, backup = 0):
    if self.cfgApp.scsObj:
      if not backup:
        self.cfgApp.scsObj.Start()
      else:
        self.cfgApp.backupApp.scsObj.Start()
    else:
      ProgrammError("Server %s does not have related ScsApplication")
    
  def Stop(self, backup = 0, cleanup = 1):
    if self.cfgApp.scsObj:
      if not backup:
        self.cfgApp.scsObj.Stop(cleanup = cleanup)
      else:
        self.cfgApp.backupApp.scsObj.Stop(cleanup = cleanup)
    else:
      ProgrammError("Server %s does not have related ScsApplication")    
  
  def AfterStop(self):
    pass

  def AfterStart(self):
    pass
   
  def GetLogCfgDAP(self):
    """returns CfgApplication - DAP for MessageServer (if application has MS in connections)"""
    return self.cfgApp.GetLogCfgDAP()
   
  def getDBLogTable(self):
    
    try:
      from model_dbtable import DBMessageServerLogTable
    except:
      return
    cfgDAP = self.cfgApp.GetLogCfgDAP()  
    if not cfgDAP: return
    oldPrintOn = GetPrintOn()
    PrintOn(0)
    try:
      self.dbMessageServerLogTable = DBMessageServerLogTable(cfgDAP, self)
    except:
      ResetFatalErrorCnt()
    PrintOn(oldPrintOn)
      
     
    
  def CleanLogDB(self):
    self.getDBLogTable()
    if not self.dbMessageServerLogTable: 
      ProgrammWarning("Application either has no connection to MessageServer, or DAP in MessageServer is not configured")
      return
    self.dbMessageServerLogTable.DeleteListOfRecords()
    
  def TestEmptyMessageID(self, expectedMessageID = 0, expectedSubText = "", afterDateTime = "" ):
    self.getDBLogTable()
    if not self.dbMessageServerLogTable: 
      ProgrammWarning("Application either has no connection to MessageServer, or DAP in MessageServer is not configured")
      return
    return self.dbMessageServerLogTable.TestEmptyMessageID(self.cfgApp, expectedMessageID, expectedSubText, afterDateTime)

  def TestLastMessageID(self, expectedMessageID = 0, expectedSubText = "", afterDateTime = "" ):
    self.getDBLogTable()
    if not self.dbMessageServerLogTable: 
      ProgrammWarning("Application either has no connection to MessageServer, or DAP in MessageServer is not configured")
      return
    return self.dbMessageServerLogTable.TestLastMessageID(self.cfgApp, expectedMessageID, expectedSubText, afterDateTime)
        
  def ListMessageID(self, afterDateTime = ""):
    self.getDBLogTable()
    if not self.dbMessageServerLogTable: 
      ProgrammWarning("Application either has no connection to MessageServer, or DAP in MessageServer is not configured")
      return
    return self.dbMessageServerLogTable.ListMessageID(self.cfgApp, afterDateTime)

  def GetMessage(self, expectedSubText = "", afterDateTime = ""):
    self.getDBLogTable()
    if not self.dbMessageServerLogTable: 
      ProgrammWarning("Application either has no connection to MessageServer, or DAP in MessageServer is not configured")
      return
    return self.dbMessageServerLogTable.GetMessage(self.cfgApp, expectedSubText, afterDateTime)

    
  def TestMessages(self, expectedMessageID = 0, expectedSubText = "", afterDateTime = ""):
    self.getDBLogTable()
    if not self.dbMessageServerLogTable: 
      ProgrammWarning("Application either has no connection to MessageServer, or DAP in MessageServer is not configured")
      return
    return self.dbMessageServerLogTable.TestMessages(self.cfgApp, expectedMessageID, expectedSubText, afterDateTime)
    
        
  #Server related errors and warnings. Functions with the same name from  common are used for printing only 
  def Warning(self, str1 = "", str2 = ""):
    self.SetTestResult(TestResEnum.Warning)
    if str1:  str1 = self.appType + ": " + str1
    self.errorCounts = 1
    Warning(str1, str2, byServer = 1)
    
    
  def MinorError(self, str1 = "", str2 = ""):
    self.SetTestResult(TestResEnum.MinorError)
    if str1:  str1 = self.appType + ": " + str1
    self.errorCounts = 1
    MinorError(str1, str2, byServer = 1)  
    
  def Error(self, str1 = "", str2 = ""):
    self.SetTestResult(TestResEnum.Error)
    if str1:  str1 = self.appType + ": " + str1
    self.errorCounts = 1
    Error(str1, str2, byServer = 1)  
  
  def SeriousError(self, str1 = "", str2 = "", forceReset = -1, nonServer = 0):
    self.SetTestResult(TestResEnum.SeriousError)
    if str1:  str1 = self.appType + ": " + str1
    if forceReset == -1:
      forceReset = GetOption("ResetTestAfterError")
    self.errorCounts = 1
    SeriousError(forceReset, str1, str2, byServer = 1)
  
  def ConnectionError(self):
    self.SetTestResult(TestResEnum.ConnectionError)
    str1 = self.appType 
    self.errorCounts = 1
    ConnectionError(str1)    
  
  def OpenError(self, str1 = "", str2 = ""):
    OpenError(str1, str2)
    
  
  def Message(self, str1 = "", str2 = ""):
    if str1:  str1 = self.appType + ": " + str1
    Message(str1, str2)  
  
  
  
  def SetTestResult(self, val = None):  #should be called with arg = None before each test
    if not val:
      self.testRes = ()
    else:
      if not (val  in self.testRes):
        self.testRes = self.testRes + (val,)
    #if val:
    #  PrintLog("setting test result %s for server %s" %(val, self))
    #  traceback.print_stack(limit = 50, file = sys.stdout)
    #  f = StringIO.StringIO()
    #  traceback.print_exc(limit=50, file=f)
    #  s = f.getvalue()
    #  PrintLog("%s" %s)        

  def TestResultIn(self, setToCheckIn):
    return In(self.testRes, setToCheckIn)   
    
  def TestResultInResetSet(self):
    return self.TestResultIn(self.ResetAfterTestSet)
    
  def SetLogTracer(self):  
    self.LogTracer = model_logtracer.ServerLogTracer(self)
    self.markTestLog()  # this marker is used when Start/Stop server is called in test
      
  def MarkLog(self):  #public, to be called from any place in test
    if self.LogTracer and self.LogTracer.isFunctional():
      return self.LogTracer.Mark() #returns marker
    else:
      ProgrammError("Cannot perform MarkLog, log parameters are not specified")
    
  
  def CutLog(self, marker, name = None, path = None, save = 1): #public, to be called from any place in test, after MarkLog
    if self.LogTracer and self.LogTracer.isFunctional():
      if not name or not path:
        th = TestHandler()
        if th:
          name = th.testName + ".forced"
          path = os.path.join(th.testResFolder, self.cfgApp.appType)
          return self.LogTracer.CutAndSave(marker, name, path, save)
      else:
        return self.LogTracer.CutAndSave(marker, name, path, save)
    else:
      ProgrammError("Cannot perform CutLog, log parameters are not specified")
  
  def markTestLog(self):  #to be called before test and in SetLogTracer
    if self.LogTracer:
      self.testMarker = self.LogTracer.Mark() #returns marker
  
  def cutTestLog(self, testName, path):#to be called after test
    if self.LogTracer:
      return self.LogTracer.CutAndSave(self.testMarker, testName, path)


  
  def ChangeOption(self, section, key, value, annex = 0, inBackupToo = 1): 
    return self.cfgApp.ChangeOption(section, key, value, annex, inBackupToo) 
    
  def AddOption(self, section, key, value, annex = 0, inBackupToo = 1):
    return self.cfgApp.AddOption(section, key, value, annex, inBackupToo) 

  def DeleteOption(self, section, key, annex = 0, inBackupToo = 1): 
    return self.cfgApp.DeleteOption(section, key, annex, inBackupToo)

  def DeleteSection(self, section, annex = 0, inBackupToo = 1):  
    return self.cfgApp.DeleteSection(section, annex, inBackupToo)
    
  def FindOption(self, section = "", key = "", annex = 0):
    return self.cfgApp.FindOption(section, key, annex)     

  def setDefaultOptionValue(self, optionName):
    pass

  def translateOption(self, optionName):
    pass

  def WaitEvent(self, *args, **keywords):
    pass

  def WaitAllEvents(self, timeout = 1):
    while 1:
      ev = self.WaitEvent(timeout = timeout)
      if not ev:
        break  
      PrintLog(ev)

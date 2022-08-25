#==================================================================================
#
#                  === Config Server model ===
#
#
#==================================================================================

import sys
import copy
import time
import common
import re
import os

from common                 import *
from common_enum            import *

import  model

if InTrue(GetOption("Java")):
  import j_pconflib as pconflib
elif InTrue(GetOption("DotNet")):
  import n_pconflib as pconflib
else:
  import  pconflib  
from model_cfgpersonplace import CfgPerson, CfgPlace, CfgAgentLogin, CfgSkill, CfgActionCode
from model_cfgsolution import CfgSolution
from model_cfgstatdaytable import CfgStatDay, CfgStatTable
from model_cfgswitch import CfgSwitch, CfgPhysicalSwitch
from model_cfgtableaccess import CfgTableAccess
from model_cfgtenant import CfgTenant
from model_cfgtreatmentfilter import CfgTreatment, CfgFilter
from model_cfgalarms import CfgAlarmCondition, CfgScript
from model_cfgapplication import CfgApplication, CfgQaartApplication, CfgHost, CfgAppPrototype
from model_cfgcampaign import CfgCampaign, CfgCallingList, CfgCampaignGroup
from model_cfgdn import CfgDN
from model_cfggroup import CfgPlaceGroup, CfgAgentGroup, CfgAccessGroup
from model_cfgenumerator import CfgBusinessAttribute, CfgAttributeValue, CfgEnumerator, CfgEnumeratorValue
from model_cfgivr import CfgIVR, CfgIVRPort, CfgGVPIVRProfile
from model_cfgfolder import CfgFolder
from model_cfgtransaction import CfgTransaction
from model_cfgtable import CfgField, CfgFormat, CfgObjectiveTable
from model_cfgobject import  CfgAddress,\
                             CfgOS,\
                             CfgSwitchAccessCode,\
                             CfgConnInfo,\
                             CfgServer,CfgServerInfo,\
                             CfgAlarmEvent,\
                             CfgCallingListInfo,\
                             CfgCampaignGroupInfo,\
                             CfgDNAccessNumber,\
                             CfgPhones,\
                             CfgAppRank,\
                             CfgAgentInfo,\
                             CfgSkillLevel,\
                             CfgAgentLoginInfo,\
                             CfgGroup,\
                             CfgAppServicePermission,\
                             CfgSolutionComponentDefinition,\
                             CfgSolutionComponent,\
                             CfgStatInterval,\
                             CfgServiceInfo, \
                             CfgSubcode, \
                             CfgID, CfgACE, CfgACL, AccessMask, \
                             CfgObjectResource, CfgPortInfo, \
                             CfgObjectiveTableRecord, CfgRoleMember
from model_cfgrole import CfgRole
from model_cfgtimezone import CfgTimeZone

class CServer(pconflib.CServer0, model.AbstractServer):

  
  def __init__(self, servName):
    pconflib.CServer0.__init__(self)
    model.AbstractServer.__init__(self)
    #it is a (Host, Port, UserName, Password)
    self.backupHost = None
    self.backupPort = 0
    try:
      self.Host, self.Port, self.UserName, self.Password, self.backupHost, self.backupPort = servName
    except ValueError:
      self.Host, self.Port, self.UserName, self.Password = servName #old version
    #self.IPaddress = self.Host # to open first time, before cfgApp is initialized
    self.Port = str(self.Port)
    self.serverInfo = servName
    self.registeredObjectTypes = []
    self.ignoreClientList = []
    
  def OpenConnection(self, toPrimOnly = 0):
    """ Open connection to the Config Server
    Parameters:
      toPrimOnly - Int
      
      If toPrimOnly = 1 it performs connection to the primary config server only,
      by default - connection to the primary and backup servers
    """
    model.AbstractServer.OpenConnection(self, toPrimOnly)
    try: 
      self.OpenServerEx(self.Host, self.Port, self.UserName, self.Password) 
    except OpenErrorExcept:
      if toPrimOnly or not self.backupHost:
        FatalError("Cannot open ConfigServer " + self.Host + ":" + self.Port)  
      try:
        print "connecting to backup"
        self.OpenServerEx(self.backupHost, self.backupPort, self.UserName, self.Password) 
      except OpenErrorExcept:
        FatalError("Cannot open ConfigServer " + self.backupHost + ":" + self.backupPort)  

  def OpenConnectionAs(self, appName, appType, toPrimOnly=1):
    """ Open connection to the Config Server
    Parameters:
       appName - application name in CME,
       appType - application type in CME, 
    """
    try:
      self.OpenServerEx(self.Host, self.Port, appName=appName, appType=appType)
    except OpenErrorExcept:
      if toPrimOnly or not self.backupHost:
        FatalError("Cannot open ConfigServer " + self.Host + ":" + self.Port)
      try:
        print "connecting to backup"
        self.OpenServerEx(self.backupHost, self.backupPort, appName=appName, appType=appType)
      except OpenErrorExcept:
        FatalError("Cannot open ConfigServer %s:%s, application %s, app type %s" %
                   (self.Host, self.Port, appName, appType))

  def actionOnNoEvent(self, message):
    if self.GetDoNotTest(): return
    self.serErrBadOtherCnt = self.serErrBadOtherCnt + 1
    self.SeriousError(message)

  def actionOnNoEventInInit(self, message):
    if self.GetDoNotTest(): return
    FatalError(message)
    
  def addToObjectList(self, obj):
   
    obj.pyObjectType = obj.__class__.__name__
    if not self.FindObjectByTypeAndDBID(obj.objType, obj.DBID):
      if InTrue(GetOption("XS")):
        if (obj.objType, 0) not in self.registeredObjectTypes:
          self.RegisterObjectTypeEx({"subscription": {"object_type": obj.objType.val}})
          self.GetUpdates(timeout = 0)
          self.registeredObjectTypes.append((obj.objType, 0))        
      else:
        if (obj.objType, obj.DBID) not in self.registeredObjectTypes:
          self.RegisterObjectTypeEx({"subscription": {"object_type": obj.objType.val, "object_dbid":  obj.DBID}})
          self.GetUpdates(timeout = 0)
          self.registeredObjectTypes.append((obj.objType, obj.DBID))
      self.ObjectList.append(obj)
    #else - it is already in OL



  def FindObjectsByType(self, objType):
    """ Returns all objects by type
    Parameters:
      objType     - Int
    """
    # returns existing list
    objects = []
    for obj in self.ObjectList:
      if obj.objType == objType and obj not in objects:
        objects.append(obj)
    return objects
          
  
  #some objects could be get by name, use only for applicable objects (applications, solutions and some others)
  #for other objects use FindObjectByTypeAndDBID, GetObjectByTypeAndDBID
  def FindObjectByTypeAndName(self, objType, objName): 
    """ Returns existing object by type and name 
    Parameters:
      objType     - Int
      objName     - Char
    """
    # returns existing or None
    for obj in self.ObjectList:
      if obj.objType == objType:
        if hasattr(obj, "name") and obj.name == objName:
            return obj
      
  
  def GetObjectByTypeAndName(self, objType, objName): 
    """ Returns existing object by type and name or creates new one
    Parameters:
      objType     - Int
      objName     - Char
    """
    # returns existing or creates
    obj = self.FindObjectByTypeAndName(objType, objName)
    if obj:
      return obj
    else:
      if objType == CfgObjectType.CFGTenant and objName == "Environment":
        filter = {"dbid": 1}
      else:
        filter = {"name": objName}
      strObjs = self.GetObjectInfo(objType, filter)
      if strObjs:
        className = eval("Cfg" + objType.name[3:])
        obj = className(strObj = strObjs[0], cfgServer = self)
        return obj
      else:
        ProgrammWarning("No object %s with name %s found" %(objType, objName))  
        
  def FindObjectByTypeAndTenantNameAndName(self, objType, tenantName, objName): 
    """ Returns existing object by type and name and tenant name
    Parameters:
      objType     - Int
      tenantName  - Char    
      objName     - Char
    """
    # returns existing or None
    filter = {"name" : tenantName}
    tenantDBID = self.GetObjectDBID(CfgObjectType.CFGTenant, filter)
    for obj in self.ObjectList:
      if obj.objType == objType:
        if hasattr(obj, "name") and obj.name == objName and hasattr(obj, "tenantDBID") and obj.tenantDBID == tenantDBID :
            return obj

  def FindObjectByTypeAndTenantDBIDAndName(self, objType, objName, tenantDBID): 
    """ Returns existing object by type and name and tenant DBID
    Parameters:
      objType     - Int
      tenantDBID  - Int    
      objName     - Char
    """
    # returns existing or None
    for obj in self.ObjectList:
      if obj.objType == objType:
        if hasattr(obj, "name") and obj.name == objName and hasattr(obj, "tenantDBID") and obj.tenantDBID == tenantDBID :
            return obj
      
        
  def GetObjectByTypeAndTenantNameAndName(self, objType, tenantName, objName) : 
    """ Returns existing object by type and name and tenant name or creates new one
    Parameters:
      objType     - Int
      tenantName  - Char    
      objName     - Char
    """
    # returns existing or creates
    filter = {"name" : tenantName}
    tenantDBID = self.GetObjectDBID(CfgObjectType.CFGTenant, filter)    
    obj = self.FindObjectByTypeAndTenantDBIDAndName(objType, tenantDBID, objName)
    if obj:
      return obj
    else:
      strObjs = self.GetObjectInfo(objType, {"name": objName, "tenant_dbid": tenantDBID})
      if strObjs:
        className = eval("Cfg" + objType.name[3:])
        obj = className(strObj = strObjs[0], cfgServer = self)
        return obj
      else:
        ProgrammWarning("No object %s with name %s  and tenant %s found" %(objType, objName, tenantName))          
  
    
    
  
  def FindObjectByTypeAndDBID(self, objType, objDBID): 
    """ Returns existing object by type and DBID
    Parameters:
      objType     - Int
      objDBID     - Int    
    """
    # returns existing or None
    for obj in self.ObjectList:
      if obj.objType == objType:
        if hasattr(obj, "DBID") and obj.DBID == objDBID:
            return obj
      
        
  def GetObjectByTypeAndDBID(self, objType, objDBID): 
    """ Returns existing object by type and DBID or creates new one
    Parameters:
      objType     - Int
      objDBID     - Int    
    """
    # returns existing or creates
    obj = self.FindObjectByTypeAndDBID(objType, objDBID)
    if obj:
      return obj
    else:
      strObjs = self.GetObjectInfo(objType, {"dbid": objDBID})
      if strObjs:

        className = eval("Cfg" + objType.name[3:])
        obj = className(strObj = strObjs[0], cfgServer = self)
        return obj
      else:
        ProgrammWarning("No object %s with DBID %d found" %(objType, objDBID))
    
  def FindAllObjectsByTypeAndDBID(self, objType, objDBID):
    """ Returns all objects by type and type and DBID
    Parameters:
      objType     - Int
      objDBID     - Int    
    """
    objs = []
    for obj in self.ObjectList:
      if obj.objType == objType :
        if hasattr(obj, "DBID"):
          if obj.DBID == objDBID:
            objs.append(obj)
        #elif objType in (CfgObjectType.CFGAgentGroup, CfgObjectType.CFGPlaceGroup, CfgObjectType.CFGDNGroup):
        #  if obj.groupInfo["DBID"] == objDBID:
        #    objs.append(obj)      
    return objs
        
  def GetObjectDBID(self, objType, filtr):
    """ Returns object DBID
    Parameters:
      objType     - Int
      filtr       - dict
    Example:
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, {"name" : "Tenant1"})
    """
    #found = 0
    #for obj in self.ObjectList:
    #  if obj.objType == objType and obj.exists:
    #    for key in filtr.keys():
    #      if hasattr(obj, key) and (getattr(obj, key) == filtr[key]):
    #        found = 1
    #      else:
    #        found = 0
    #        break
    #    if found:
    #      return obj.DBID
    #if not found:
    return pconflib.CServer0.GetObjectDBID(self, objType, filtr)
      
  def GetObjectNameByObjectTypeAndDBID(self, objType, dbid):
    """ Returns object name by type and DBID
    Parameters:
      objType     - Int
      dbid        - Int    
    """
    if objType == CfgObjectType.CFGTenant and dbid == 1: 
      return "Environment"
    found = 0
    for obj in self.ObjectList:
      if obj.objType == objType and hasattr(obj, "DBID") and obj.DBID == dbid and hasattr(obj, "name"):      
        found = 1
        return obj.name
    if not found:
      return pconflib.CServer0.GetObjectNameByObjectTypeAndDBID(self, objType, dbid)
      
      
  def GetObjectTenantNameByObjectTypeAndDBID(self, objType, dbid):
    """ Returns object tenant name by type and DBID
    Parameters:
      objType     - Int
      dbid        - Int    
    """
    found = 0
    for obj in self.ObjectList:
      if obj.objType == objType and hasattr(obj, "DBID") and obj.DBID == dbid and hasattr(obj, "tenantDBID"):      
        found = 1
        return self.GetObjectNameByObjectTypeAndDBID(CfgObjectType.CFGTenant, obj.tenantDBID)
    if not found:
      return pconflib.CServer0.GetObjectTenantNameByObjectTypeAndDBID(self, objType, dbid)  
  
  def SetIgnoreClientList(self): 
    cfgApps = self.FindObjectsByType(CfgObjectType.CFGApplication)
    for cfgApp in cfgApps:  
      if cfgApp.ignoreAsClient:
        if cfgApp.name not in self.ignoreClientList:
          self.ignoreClientList.append(cfgApp.name) 
    return self.ignoreClientList
  
  
  def GetUpdates(self, timeout = 0.1, csService = None, firstTimeout = 0.5):
    update = 0
    i = 0
    while 1:
      if i == 0:
        tout = firstTimeout
      else:
        tout = timeout
      if not tout: return
        
      ev = self.WaitEvent(timeout = tout)
      i += 1
      if not ev:
        break
      else:
        if GetOption("PrintConfigDebugInfo"):
          PrintStdout(["received event:", ev])
        objType = ValToEnumElem(CfgObjectType, ev.cfgObjectType)
        if ev.DBID and ev.cfgObjectType:
          objs = self.FindAllObjectsByTypeAndDBID(objType, ev.DBID)
          #print "found suitable objects ++++++++++++++++++++++++++"
          if objs:
            for obj in objs:
              try:
                PrintStdout("Processing %s %s %s" %(str(ValToEnumElem(CfgEventName, ev.cfgEventType)),  ev.DBID, ev.cfgObjectType))
                method = getattr(obj, "process" + str(ValToEnumElem(CfgEventName, ev.cfgEventType)))
                method(ev)
              except AttributeError:
                pass
          if csService: # callbacks
            try:
              if ev.cfgEventType == CfgEventName.CFGObjectAdded:
                objType = ValToEnumElem(CfgObjectType, ev.cfgObjectType)
                className = eval("Cfg" + str(objType)[3:])
                obj = className(strObj = ev.cfgObject, cfgServer = self)
                csService.objectAdded(self.FindObjectByTypeAndDBID(objType, obj.DBID))
              elif ev.cfgEventType == CfgEventName.CFGObjectDeleted:
                obj = self.FindObjectByTypeAndDBID(objType, obj.DBID)
                if obj:
                  csService.objectDeleted(obj)
            except:
              pass
              
        #else:
        #  print "update event does not have ev.DBID and ev.cfgObjectType"
    #if update:
    #  print "FINAL Got update"
    #else:
    #  print "No update"
      
  def SaveConfigurationToFile(self, saveConfFileName = None):
    """ Save configuration to the file
    Parameters:
      saveConfFileName     -   Char
    """
    if not saveConfFileName:
      saveConfFileName = GetOption("SaveConfFileName")
    if not saveConfFileName: 
      FatalError("Cannot save configuration. File is not specified" )
    try:
      cfgApps = self.FindObjectsByType(CfgObjectType.CFGApplication)
      cfgDNs = self.FindObjectsByType(CfgObjectType.CFGDN)
      saveConfFile = open(saveConfFileName, "w")

      SetOption("SaveConfFileName", saveConfFileName)

      strCfgApps = []
      for cfgApp in cfgApps:
        strCfgApp = cfgApp.fromPythonObjectToString()
        saveConfFile.write(repr(strCfgApp) + "\n")
        
      for cfgDN in cfgDNs:
        strCfgDN = cfgDN.fromPythonObjectToString()
        saveConfFile.write(repr(strCfgDN) + "\n")        
      saveConfFile.close()
    except Exception, mess:

      FatalError("Cannot save configuration to %s.\n%s" %(saveConfFileName, mess))

    PrintLog("Configuration saved successfully to %s" %saveConfFileName)
      
  def RestoreConfigurationFromFile(self, saveConfFileName = None):
    """ Restore configuration from file
    Parameters:
      saveConfFileName     -   Char
    """
    if not saveConfFileName:
      saveConfFileName = GetOption("RestoreConfFileName")
    if not saveConfFileName: 
      FatalError("Cannot restore configuration. File is not specified" )
    cfgApps = self.FindObjectsByType(CfgObjectType.CFGApplication)
    cfgDNs = self.FindObjectsByType(CfgObjectType.CFGDN)
    
    try:
      saveConfFile = open(saveConfFileName, "r")
    except Exception, mess:
      FatalError("Cannot restore configuration from %s.\n%s" %(saveConfFileName, mess))
    try:
      strCfgObjs = saveConfFile.readlines()
    except Exception, mess:
      FatalError("Cannot restore configuration from %s.\n%s" %(saveConfFileName, mess))
      
      
    loadedCfgApps = []
    loadedCfgDNs = []
    try:
      for strCfgObj in strCfgObjs:
        if strCfgObj.find("CfgApplication") <> -1:
          strCfgApp = eval(strCfgObj)
          cfgApp = CfgApplication(strObj = strCfgApp)
          del self.ObjectList[-1] #trick - remove appended object
          loadedCfgApps.append(cfgApp)        
        elif strCfgObj.find("CfgDN") <> -1:
          strCfgDN = eval(strCfgObj)
          cfgDN = CfgDN(strObj = strCfgDN)
          del self.ObjectList[-1] #trick - remove appended object
          loadedCfgDNs.append(cfgDN)
    except Exception, mess:
      FatalError("Cannot restore configuration from %s.\n%s" %(saveConfFileName, mess))
     
    #try to compare by dbid
    for origCfgApp in cfgApps:
      foundInLoaded = 0
      for loadedCfgApp in loadedCfgApps:
        if loadedCfgApp.DBID == origCfgApp.DBID:
          foundInLoaded = 1
          break
      if not foundInLoaded:
        mess = "Cannot find application with name %s, DBID %s in file" %( origCfgApp.name, origCfgApp.DBID)
        ProgrammWarning("Cannot fully restore configuration from %s.\n%s" %(saveConfFileName, mess))
    for origCfgApp in cfgApps:
      for loadedCfgApp in loadedCfgApps:
        if loadedCfgApp.DBID == origCfgApp.DBID:

          origCfgApp.BeginChange()
          origCfgApp.options = loadedCfgApp.options
          origCfgApp.userProperties = loadedCfgApp.userProperties
          origCfgApp.appServerDBIDs = loadedCfgApp.appServerDBIDs
          origCfgApp.serverInfo = loadedCfgApp.serverInfo
          changed = origCfgApp.EndChange()
          if not changed:
            saveConfFile.close()
            FatalError("Cannot restore configuration from %s" %(saveConfFileName))
          try:
            if not loadedCfgApp.serverInfo or (loadedCfgApp.serverInfo.hostDBID <> origCfgApp.serverInfo.hostDBID):
              origCfgApp.ChangeHostDBID(loadedCfgApp.serverInfo.hostDBID)
            if not loadedCfgApp.serverInfo or (loadedCfgApp.serverInfo.port <> origCfgApp.serverInfo.port):
              origCfgApp.ChangePort(loadedCfgApp.serverInfo.port)
          except Exception, mess:
            FatalError("Cannot restore configuration from %s.\n%s" %(saveConfFileName, mess))          
          break
        
          
    for origCfgDN in cfgDNs:
      foundInLoaded = 0
      for loadedCfgDN in loadedCfgDNs:
        if loadedCfgDN.DBID == origCfgDN.DBID:
          foundInLoaded = 1
          break
    for origCfgDN in cfgDNs:
      for loadedCfgDN in loadedCfgDNs:
        if loadedCfgDN.DBID == origCfgDN.DBID:

          origCfgDN.BeginChange()
          origCfgDN.userProperties = loadedCfgDN.userProperties
          changed = origCfgDN.EndChange()
          if not changed:
            saveConfFile.close()
            FatalError("Cannot restore configuration from %s" %(saveConfFileName))
          break          
    saveConfFile.close()
    PrintLog("Configuration restored successfully from %s" %saveConfFileName)
  #----------------------------------------------------    
  #get some specific objects
  #----------------------------------------------------
  def GetBusinessAttribute(self, tenantName, name):
    """ Returns business attribute
    Parameters:
      tenantName      - Char
      name            - Char
    """
    return self.GetObjectByTypeAndTenantNameAndName(CfgObjectType.CFGEnumerator, tenantName, name)

  
  def GetBusinessAttributeValue(self, tenantName, businessAttributeName, name):
    """ Returns business attribute value
    Parameters:
      tenantName            - Char
      businessAttributeName - Char
      name                  - Char
    """
    cfgBA = self.GetBusinessAttribute(tenantName, businessAttributeName)
    if not cfgBA: return
    filter = {"name" : tenantName}
    tenantDBID = self.GetObjectDBID(CfgObjectType.CFGTenant, filter)     
    strObjs = self.GetObjectInfo(CfgObjectType.CFGEnumeratorValue, {"name": name, "tenant_dbid": tenantDBID, "enumerator_dbid": cfgBA.DBID})
    if strObjs:
      className = eval("CfgAttributeValue")
      obj = className(strObj = strObjs[0], cfgServer = self)
      return obj

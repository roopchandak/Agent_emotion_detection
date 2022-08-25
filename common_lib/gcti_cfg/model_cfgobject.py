#
#            === CfgObject model ===
#

import copy
import time
from common      import *
from common_enum import *
from enum        import *
import re
try:
  from default_servers        import *
except:
  pass
try:
  from javax.xml.parsers import *
except:
  pass
  
try:
  import clr
  clr.AddReference('System.Xml')
  from System.Xml import *
except:
  pass  
#==================================================================================

servSym = ['\027','\030','\031','\032','\033','\034','\035','\036','\037']
#==================================================================================
 
#==================================================================================  
class CfgStruct:
  initialized = 0
  title = ""
  fields = ()
  translation = {}
  def __init__(self, strObj = None, cfgServer = None):
    if cfgServer == None: self.cfgServer = GetDefaultCServer()
    else:               self.cfgServer = cfgServer
    self.tmpStrObj = ""
    if strObj:
      self.fromStringToPythObject(strObj)
    else:
      self.createEmptyObject()
    self.initialized = 1

  def createEmptyObject(self):
    for pair in self.fields:
      attr, type = pair
      if type == "Int":
        val = 0
      elif type == "Char":
        val = ""
      elif type == "DBID":
        val = 0
      else:
        val = None
      setattr(self, attr, val)    
  
  def __setattr__(self, attr, value):
    if attr == "initialized" or not self.initialized or attr == "state":
      self.__dict__[attr] = value
      return
    found = 0
    for  (attrName, attrType) in self.fields:
      if attr == attrName:
        found = 1
        break

    if not found:
      print self.fields
      ProgrammError("Object does not have attribute %s" %attr)     
    error = 0

    if attrType == "Int" and isinstance (value, EnumElem):
      if self.translation.has_key(attr):
        if NameToEnumElem(eval(self.translation[attr]), str(value)):
          value = NameToEnumElem(eval(self.translation[attr]), str(value)).val
        else:
          error = 1
          expected =  self.translation[attr]
      else:
        error = 1
        expected =  attrType

    elif attrType == "Int" and type(value) != type(0):
      error = 1
      expected =  "Integer"
    elif attrType == "Char" and type(value) not in (type(""), type(None), type(u'')):
      error = 1
      expected =  "String"
    if error:
      ProgrammError("Wrong type in attribute %s, value %s, expected %s" %(attr, value, expected))     

    self.__dict__[attr] = value

        
  def prettyRepr(self, shift = 4):
 
    str = "\n"+ ' '*shift + self.title + "\n"
    for (nm, tp) in self.fields:
      if nm == "password":
          sval = "*********"
      else:
          val = self.getField(nm)
          if hasattr(val, 'prettyRepr'):
            sval = val.prettyRepr(shift + 2)
          else:
            sval = val
      str = str + ' '*(shift + 2) + "%-20s = %s\n" % (nm, sval)

    return str   
  
  def __repr__(self):
    return self.prettyRepr(shift = 4) 
    
  def shortRepr(self, shift = 4):
    str = ""
    for nm in self.requiredFields:
      val = self.getField(nm)
      if hasattr(val, 'shortRepr'):
        sval = val.shortRepr(shift + 2)
      else:
        sval = val
      str = str + " "*(shift+ 2) + "%-20s = %s\n" % (nm, sval)   
    return str
  
  def veryShortRepr(self):
    if hasattr(self, "name"):
      str = self.name
    elif hasattr(self, "number"):
      str = self.number
    else:
      str = self.shortRepr()
    return str    
    
class CfgObject:
  """Ancestor of other CfgObjects"""
  fields = ()  #pairs ("AttrName", "AttrType")
  translation = {"state":  "CfgObjectState"}
  requiredFields = []
  toXmlTranslation = {}
  fromXmlTranslation = {}  
  def __init__(self, objType, filtr = {}, cfgServer = None, strObj = None): 
    if cfgServer == None: self.cfgServer = GetDefaultCServer()
    else:               self.cfgServer = cfgServer
    if self.cfgServer == None:
      ProgrammError("ConfigServer is not defined") 
    self.tmpStrObj = ""
    self.objType = objType 
    self.exists = 0
    self.requestID = 0
    self.cfgID = None
    if filtr or strObj:
      if filtr:
        objects = self.cfgServer.GetObjectInfo( self.objType, filtr)
        if len(objects) <> 1:                                         #should be only one object
          FatalError("Incorrect number of objects: %s, filter: %s, object type: %s" % (len(objects), filtr, self.objType))

        strObj = objects[0]  

      self.fromStringToPythObject(strObj)     #set self fields, fields should be defined in 
                                              #child object __init__ before call of CfgObject.__init__
      obj = self.cfgServer.FindObjectByTypeAndDBID(self.objType, self.DBID)                                        
      if  obj:# this object was read before
        self.initialObject = obj.initialObject        
      else:
        self.initialObject = strObj  
      self.exists = 1
      self.getCfgID()
      self.cfgServer.addToObjectList(self)
    else:
      self.initialObject = ""
      self.createEmptyObject()
    
    self.title = ""
    self.scsObj = None
    self.pyObjs = []
    self.restored = 0
    self.lastChangeTimestamp = 0
    self.ACL = None

  
  def getCfgID(self):
    self.cfgID = CfgID(cfgServer  = self.cfgServer)#()
    self.cfgID.SetAttributes({"CSID": 0, "DBID": self.DBID, "type": self.objType})
    return self.cfgID  
    
  def createEmptyObject(self):
    for pair in self.fields:
      attr, type = pair
      if type == "Int":
        val = 0
      elif type == "Char":
        val = ""
      elif type == "DBID":
        val = 0
      else:
        val = None
      
      setattr(self, attr, val)
    self.state = CfgObjectState.CFGEnabled.val
  
  def GetTenantName(self):
    for  (attrName, attrType) in self.fields:
      if attrName == "tenantDBID":
        return self.cfgServer.GetObjectNameByObjectTypeAndDBID(CfgObjectType.CFGTenant, self.tenantDBID)        
    
    
  def SetAttributes(self, attrDict):
    for attr in attrDict:
      #check attr presence
      found = 0
      for  (attrName, attrType) in self.fields:
        if attrName == attr:
          found = 1
          break
      if not found:
        print self.fields
        ProgrammError("SetAttributes: attribute %s does not belong to the object %s" %(attr, self.__class__.__name__))
        
      #check type
      value = attrDict[attr]
      typeCorrect = 0
      error = 0
      expected = ""
      if isinstance (value, EnumElem):
        if self.translation.has_key(attr):
          if NameToEnumElem(eval(self.translation[attr]), str(value)):
            value = NameToEnumElem(eval(self.translation[attr]), str(value)).val
          else:
            error = 1
            expected =  self.translation[attr]
        else:
          error = 1
          expected =  attrType
      elif attrType =="Int" and type(value) != type(0):
        error = 1
        expected =  "Integer"
      elif attrType == "Char" and type(value) not in (type(""), type(None), type(u'')):
        error = 1
        expected =  "String"
      if error:
        ProgrammError("Wrong type in attribute %s, value %s, object %s, expected %s" %(attr, value, self.title, expected))     
      setattr(self, attr, value)
  
  def prettyRepr(self, shift = 2):
    str = "\n"+ ' '*shift + self.title + "\n"
    for (nm, tp) in self.fields:
      #riprint nm, tp
      if nm == "password":
          sval = "*********"
      else:
          val = self.getField(nm)
          sval = repr(val)
          if hasattr(val, 'prettyRepr'):
            sval = val.prettyRepr(shift + 2)
          else:
            sval = val
      str = str + ' '*(shift + 2) + "%-20s = %s\n" % (nm, sval)
    return str    
  
  def __repr__(self):
    return self.prettyRepr()
    
  def shortRepr(self, shift = 2):
    str = "\n" + " "*shift + self.title + "\n"
    for nm in self.requiredFields:
      val = self.getField(nm)
      if hasattr(val, 'shortRepr'): 
        sval = val.shortRepr(shift + 2)
      else:
        sval = val
      str = str + " "*(shift + 2) + "%-20s = %s\n" % (nm, sval)   
    return str
  
  def veryShortRepr(self):
    if hasattr(self, "name"):
      str = self.name
    elif hasattr(self, "number"):
      str = self.number
    else:
      str = self.shortRepr()
    return str   
      
    
  def GetInfo(self):
    if self.exists:
      filtr =  {"dbid": self.DBID}
      objects = self.cfgServer.GetObjectInfo(self.objType, filtr)
      if len(objects) > 0:                                         #should be only one object
        #FatalError("Incorrect number of objects: %s, filter: %s, object type: %s" % (len(objects), filtr, self.objType))
        strObj = objects[0]  
        self.fromStringToPythObject(strObj)   
        return 1
    return 0

  def prepareToAdd(self):
    if self.exists:
      ProgrammWarning("Object %s already exists %s" %(self.title, self.shortRepr()))
      return
      
    self.printLog("Add object %s, %s" %(self.title, self.shortRepr()))
    #check if all required fields are on place
    
    for  (attr, attrType) in self.fields:
      value = getattr(self, attr)
      if attr in self.requiredFields and not getattr(self, attr):
        #ProgrammError("Field %s should be initialized before adding object %s" %(attr, self.title))
        ProgrammError("Fields %s should be initialized before adding object %s" %(self.requiredFields, self.title))
      error = 0
      expected = ""
      if isinstance (value, EnumElem):
        if self.translation.has_key(attr):
          if NameToEnumElem(eval(self.translation[attr]), str(value)):
            value = NameToEnumElem(eval(self.translation[attr]), str(value)).val
            setattr(self, attr, value)
          else:
            error = 1
            expected =  self.translation[attr]
        else:
          error = 1
          expected =  attrType
      elif attrType == "Int" and type(value) != type(0):
        error = 1
        expected =  "Integer"
      elif attrType == "Char" and type(value) not in (type(""), type(None), type(u'')):
        error = 1
        expected =  "String"
      if error:
        ProgrammError("Wrong type in attribute %s, value %s, object %s, expected %s" %(attr, value, self.title, expected))     
    strObj = self.fromPythonObjectToString()
    return strObj
  
  def afterAdd(self, requestID, timeout = 0.1):
    """timeout is for GetUpdates, for objectAdded a fixed timeout is used"""
    if self.objType == CfgObjectType.CFGTenant:
      timeout1 = 60
    else:
      timeout1 = 10
    ev = self.cfgServer.WaitEvent(requestID, timeout = timeout1)
    if ev:
      #try:
      method = getattr(self, "process" + str(ValToEnumElem(CfgEventName, ev.cfgEventType)))
      method(ev)
      #except AttributeError:
      #  print "Unknown event %s"%ValToEnumElem(CfgEventName, ev.cfgEventType)
    self.cfgServer.GetUpdates(timeout)
    if not self.exists:
      self.cfgServer.ActionOnNoEvent("Object %s is not added " %self.title)
    else:
      self.cfgServer.addToObjectList(self)
        
  
  def Add(self, timeout = 0.1):
    
    strObj = self.prepareToAdd()
    if strObj:
      requestID = self.cfgServer.AddObject(self.objType, strObj)
      self.afterAdd(requestID, timeout)

  def AddToFolder(self, folder, timeout = 0.1):
    strObj = self.prepareToAdd()
    if strObj:
      requestID = self.cfgServer.AddObjectEx(self.objType, folder.DBID, strObj)
      self.afterAdd(requestID, timeout)
  
      
  def Delete(self, timeout = 0.1):
    if not self.exists:
      ProgrammWarning("Object %s does not exist %s" %(self.title, self.shortRepr())) 
      return
    #SetOption("SaveConfigurationChanges", True)
    self.printLog("Delete object %s, %s" %(self.title, self.shortRepr()))
    requestID = self.cfgServer.DeleteObject(self.objType, self.DBID)
    if self.objType == CfgObjectType.CFGTenant:
      timeout1 = 60
    else:
      timeout1 = 10
    ev = self.cfgServer.WaitEvent(requestID, timeout = timeout1)    
    if ev:
      method = None
      try:
        method = getattr(self, "process" + str(ValToEnumElem(CfgEventName, ev.cfgEventType)))
        
      except AttributeError:
        print "Unknown event %s"%ValToEnumElem(CfgEventName, ev.cfgEventType)
      if method:
        method(ev)
    self.cfgServer.GetUpdates(timeout)
    if self.exists:
       self.cfgServer.ActionOnNoEvent("Object %s is not deleted " %self.title)


  def MoveToFolder(self, folder):
    """folder is CfgFolder object"""
    self.printLog("Move object %s to folder %s" %(self.shortRepr(), folder.name))
    folder.addObjectToList(self)
    
  #Permissions

  def GetACL(self):
    """retrieves objects ACL"""
    self.printLog("Getting ACL for %s" %self.shortRepr())
    if InTrue(GetOption("Java")) or InTrue(GetOption("DotNet")): 
      self.getCfgID()
      xmlCfgID = self.cfgID.fromPythonObjectToString()
      strObj = self.cfgServer.GetACL(xmlCfgID)
    
    else:
      strObj = self.cfgServer.GetACL(0, self.DBID, self.objType)
    if not strObj:
      self.ACL = None
    else:
      self.ACL = CfgACL(strObj = strObj, cfgServer = self.cfgServer)
    self.printLog("ACL for %s\n%s" %(self.shortRepr(), self.ACL))
    return self.ACL

  
  def GetACEByObjectID(self, objectID):
    """objectID - struct CfgID, use <object>.cfgID """
    self.GetACL()
    if not self.ACL.ACEs: return None
    for ace in self.ACL.ACEs:
      if ace.ID.identical(objectID):
        return ace

  def SetACEPropagate(self, objectID, propagate = 1, isRecursive = 1):
    """objectID    - struct CfgID, use <object>.cfgID
       propagate   - 0 or 1
       isRecursive - 0 or 1
    """
       
    PrintLog("Setting propagate flag on object %s for %s to %s" %(self.shortRepr(), objectID, propagate))
    ace = self.GetACEByObjectID(objectID)
    if not ace:
      ProgrammWarning("No ACE found in %s for %s" %(self.shortRepr(), objectID))
      return
    am = ace.GetAccessMask()
    oldMask = str(am)
    newMask = oldMask
    prop = 1
    if oldMask.find("N") <> -1:
      prop = 0
    if propagate : #Remove No propagate
      if not prop: # no prop on old mask "N" present
        newMask = oldMask[1:]
    else: #set NO propagate
      if prop: #
        newMask = "N" + oldMask
    am.Set(newMask)    
    ace.SetAccessMask(am)
    self.SetACL(isRecursive)
    
    
  def ChangeACE(self, objectID, newMask, propagate = 1, isRecursive = 1):
    """objectID    - struct CfgID, use <object>.cfgID 
       newMask     - string of symbols  'P', 'E', 'D', 'X', 'H', 'C', 'R'
       propagate   - 0 or 1
       isRecursive - 0 or 1
    """
    PrintLog("Setting permissions on object %s for %s to %s, propagate =  %s" %(self.shortRepr(), objectID, newMask, propagate))
    ace = self.GetACEByObjectID(objectID)
    if not ace:
      return self.AddACE(objectID, newMask, propagate, isRecursive)
    am = ace.GetAccessMask()
    if not propagate:
      newMask = "N" + newMask    
    am.Set(newMask)
    ace.SetAccessMask(am)
    self.SetACL(isRecursive)
    

  def AddACE(self, objectID, maskString, propagate = 1, isRecursive = 1):
    """objectID    - struct CfgID, use <object>.cfgID
       maskString  - string of symbols  'P', 'E', 'D', 'X', 'H', 'C', 'R'
       propagate   - 0 or 1
       isRecursive - 0 or 1
    """      
    self.GetACL()
    
    if not self.ACL.ACEs: self.ACL.ACEs = []
    for existingACE in self.ACL.ACEs: 
      if objectID.identical(existingACE.ID):
        return self.ChangeACE(objectID, maskString, propagate, isRecursive)
    PrintLog("Adding permissions on object %s for %s to %s, propagate =  %s" %(self.shortRepr(), objectID, maskString, propagate))
    newACE = CfgACE(cfgServer = self.cfgServer)
    if not propagate:
      maskString = "N" + maskString
    mask = AccessMask(maskString)
    newACE.SetAttributes({"ID":objectID,
                          "accessMask": mask.ToIntMask()})        
    self.ACL.ACEs.append(newACE)
    self.ACL.count = self.ACL.count + 1
    self.SetACL(isRecursive)
    
  def RemoveACE(self, objectID, isRecursive = 1):
    """objectID - struct CfgID, use <object>.cfgID """
    self.GetACL()
    found = 0
    ind = 0
    for existingACE in self.ACL.ACEs: 
      if objectID.identical(existingACE.ID):
        found = 1
        break
      ind = ind + 1
    if not found:
      ProgrammWarning("ACE for %s is not in ACL" %objectID)
      return
    PrintLog("Removing permissions on object %s for %s" %(self.shortRepr(), objectID))
    del self.ACL.ACEs[ind]
    self.ACL.count = self.ACL.count - 1
    self.SetACL(isRecursive)   
    return self.ACL
  
  def HasACE(self, objectID):
    """
    Check if ACL has ACE for objectID
    objectID - struct CfgID, use <object>.cfgID
    return   - 0 or 1
    """
    self.GetACL()
    found = 0
    ind = 0
    for existingACE in self.ACL.ACEs:
      if objectID.identical(existingACE.ID):
        found = 1
        break
      ind = ind + 1
    if found:
      print "Object has ace"
    else:
      print "Object does not have ace"
      
    return found    
    
  def IdenticalACE(self, objectID, maskString):
    """
    Check if ACE is present and identical with maskString for objectID
    objectID    - struct CfgID, use <object>.cfgID
    maskString  - string of symbols  'P', 'E', 'D', 'X', 'H', 'C', 'R'
    return      - 0 or 1
    """    
    self.GetACL()
    found = 0
    ind = 0
    for existingACE in self.ACL.ACEs: 
      if objectID.identical(existingACE.ID):
        found = 1
        break
      ind = ind + 1
    if found:
      ace = self.ACL.ACEs[ind]
      print "1 current  access mask", str(ace.GetAccessMask())
      print "2 expected access mask", str(AccessMask(maskString))
      if  str(ace.GetAccessMask()) == str(AccessMask(maskString)):
        return 1
    return 0
      
  
  def SetACL(self, isRecursive = 1):
    if not self.ACL: ProgrammError("Object goes not have ACL. Call GetACL first")
    self.cfgServer.SetACL(self.ACL.fromPythonObjectToString(), isRecursive)
    self.cfgServer.GetUpdates()
  #End permissions
  
  #Update object
  def BeginChange(self):
    """Saves current object. Use before making changes to the python object"""
    self.oldObject = self.fromPythonObjectToString()
    
    
  def EndChange(self, timeout = 0.1, changeTimeout = 8, noEvents = 0):
    """Commits changes made to python object. Sends request UpdateObject to CS, waits for updates"""
    self.changed = 0
    newObject = self.fromPythonObjectToString()
    if self.oldObject == newObject: 
      self.printLog("Object is identical to previous. No change is performed %s, %s" %(self.title, self.shortRepr()))
      return 1    

    self.printLog("Change object %s, %s" %(self.title, self.shortRepr()))
    

    requestID = self.cfgServer.ChangeObject(self.objType, self.oldObject, newObject)
    if noEvents: return requestID
    if requestID:
      PrintStdout("expecting event to req %d\n" %requestID)
      ev = self.cfgServer.WaitEvent(requestID, timeout = changeTimeout)
      if ev:
        method = None
        try:
          method = getattr(self, "process" + str(ValToEnumElem(CfgEventName, ev.cfgEventType)))
        except AttributeError:
          print "Unknown event %s"%ValToEnumElem(CfgEventName, ev.cfgEventType)          
        if method:
          method(ev)

      self.cfgServer.GetUpdates(timeout)
      
      
      if not self.changed:
        self.GetInfo()
        self.cfgServer.ActionOnNoEvent("Object %s is not changed " %self.title)
 
        
        return 0
      else:
        pass 
        #newestObject = self.fromPythonObjectToString()
        #delta = self.cfgServer.CreateDelta(self.objType, newObject, newestObject)
        #print "+++++++++++"
        #print self.cfgServer.xmlDoc2Str(delta)
        #print "+++++++++++"
        
    #self.lastChangeTimestamp = time.time()    
    return requestID
  #Update object
  def afterEndChange(self, requestID, timeout = 0.1, changeTimeout = 8):
    PrintStdout("expecting event to req %d\n" %requestID)
    ev = self.cfgServer.WaitEvent(requestID, timeout = changeTimeout)
    if ev:
      method = None
      try:
        method = getattr(self, "process" + str(ValToEnumElem(CfgEventName, ev.cfgEventType)))
      except AttributeError:
        print "Unknown event %s"%ValToEnumElem(CfgEventName, ev.cfgEventType)          
      if method:
        method(ev)

    self.cfgServer.GetUpdates(timeout)
    
    
    if not self.changed:
      self.GetInfo()
      self.cfgServer.ActionOnNoEvent("Object %s is not changed " %self.title)
    
  def SetPyObj(self, pyObj):
    if pyObj not in self.pyObjs:
      self.pyObjs.append(pyObj)
    pyObj.cfgObj = self
    if hasattr(pyObj, "ApplyCfgChanges"):
      pyObj.ApplyCfgChanges()
              
  #Event processing
  
  def processCFGError(self, ev):
    if ev != None and ev.errorDescription != None:
        SetOption("LastErrorDescription", ev.errorDescription)
    self.printLog(ev)

  
  def processCFGObjectAdded(self, ev):
    if GetOption("PrintConfigDebugInfo"):
      self.printLog(ev)
    self.fromStringToPythObject(ev.cfgObject) 
    self.printLog("Object %s added %s" %(self.title, self.shortRepr()))
    self.exists = 1
    self.getCfgID()
    
  def processCFGObjectDeleted(self, ev):
    if GetOption("PrintConfigDebugInfo"):
      self.printLog(ev)
    self.printLog("Object %s deleted %s" %(self.title, self.shortRepr()))
    self.exists = 0 
    if self.pyObjs:
      for pyObj in self.pyObjs:
        pyObj.cfgObj = None
      self.pyObjs = []
    
  def processCFGObjectInfoChanged(self, ev):
    if GetOption("PrintConfigDebugInfo"):
      self.printLog(ev)
    self.lastChangeTimestamp = time.time()

    if GetOption("UpdateCfgObjects"):
      if ev.cfgObject:
        newStrObj = self.cfgServer.UpdateObject(self.objType, self.fromPythonObjectToString(), ev.cfgObject)
        self.fromStringToPythObject(newStrObj)
      else:
        pass
    else:
      ret = self.GetInfo() #object might be already deleted
      if not ret: return   
    self.printLog("Object %s changed %s" % (self.title, self.shortRepr()))
    #self.printLog("Object %s changed %s" % (self.title, self))
    self.changed = 1
    
    if self.pyObjs:
      for pyObj in self.pyObjs:
        self.SetPyObj(pyObj)
    otherObj = self.cfgServer.FindObjectByTypeAndDBID(self.objType, self.DBID)
    if otherObj and otherObj <> self:
      otherObj.GetInfo()
      if otherObj.pyObjs:
        for pyObj in otherObj.pyObjs:
           otherObj.SetPyObj(pyObj)        
  #End event processing
          
  
  def printLog(self, str):            
    PrintLog(str)              


  def Close(self):
    self.Restore(newObject = self.initialObject)
    
 
  def getField(self, fldName):
    if self.translation.has_key(fldName):
      return ValToEnumElem(eval(self.translation[fldName]), getattr(self, fldName))
    return getattr(self, fldName)
 
#---------------------------------------------------------------
#XML
#---------------------------------------------------------------
  def simpleFields(self):
    
    fldNames = []
    for pair in self.fields:
      if pair[1] in ("DBID", "Int", "Char"):
        fldNames.append(pair[0])
    return fldNames

  def structFieldsX(self):
    fldNames = []
    for pair in self.fields:
      if pair[1].find("Struct_") <> -1:
        fldNames.append(pair[1][7:])

    return fldNames
    
  def structFields(self):
    fldNames = []
    for pair in self.fields:
      if pair[1].find("Struct_") <> -1:
        fldNames.append(pair[0])
    return fldNames    

    
  def listOfStructsFields(self):
    fldNames = []
    for pair in self.fields:
      if pair[1].find("ListOfStructs_") <> -1:
        fldNames.append(pair[0])
    return fldNames     
    
  def arrayOfStructsFields(self):
    fldNames = []
    for pair in self.fields:
      if pair[1].find("ArrayOfStructs_") <> -1:
        fldNames.append(pair[0])
    return fldNames
  
  def kvListFields(self):
    fldNames = []
    for pair in self.fields:
      if pair[1] == "KVList":
        fldNames.append(pair[0])
    return fldNames  
    
  def dbidListFields(self):
    fldNames = []
    for pair in self.fields:
      if pair[1] == "DBIDList":
        fldNames.append(pair[0])
    return fldNames      
    
  def setValueWithSimpleType(self, fieldName, value):
    #print self.fromXmlTranslation
    if self.fromXmlTranslation.has_key(fieldName):
      fieldName = self.fromXmlTranslation[fieldName]

    for pair in self.fields:
      attr, type = pair
      if fieldName == attr:
        if type == "Int":
          value = int(value)
        elif type == "Char":
          pass
        elif type == "DBID":
          value = int(value)
        else:
          ProgrammError("zasada 1 type %s" %type)
        setattr(self, attr, value)
        
        return 
      
    ProgrammError("zasada 2 - fieldName  %s not found in self.fields %s" %(fieldName, self.fields))
    
  #JAVA    
  def toElemList_J(self, el):
    confElemList = None
    if el: 
      el = el.getFirstChild() #first CfgObj
      if el:
        confElemList = []
        confElemList.append(el)
        while 1:
          el = el.getNextSibling() #next CfgObj
          if el:
            confElemList.append(el)  
          else:
            break
    return confElemList  
  
  def setAttrFromElem_J(self, nd):
    fieldName = nd.getNodeName()
    fieldValue = nd.getAttribute("value")
    
    if fieldValue: #simple type:
      #print "1 setting %s, %s" %(fieldName, fieldValue)
      self.setValueWithSimpleType(fieldName, fieldValue)
    else: # complexType
      if fieldName in self.structFieldsX():
        #print "2 setting %s, %s" %(fieldName, fieldValue)
        structType = eval(fieldName)
        cfgStruct = structType(cfgServer = self.cfgServer)
        cfgStruct.fromXMLToPyObj_J(nd)
        if self.fromXmlTranslation.has_key(fieldName):
          fieldName = self.fromXmlTranslation[fieldName]  
          #print "new fieldName %s" %fieldName
        else:
          ProgrammError("please send to masha, no %s in %s fromXMLTranslation" %(fieldName, self))
        setattr(self, fieldName, cfgStruct)
        
        
      elif fieldName in self.listOfStructsFields() or fieldName in self.arrayOfStructsFields():
        #print "3 setting %s, %s" %(fieldName, fieldValue)
        elemList = self.toElemList_J(nd)
        if elemList == None: return
        valList = []
        for elem in elemList:
          elemName = elem.getNodeName()
          if self.fromXmlTranslation.has_key(elemName):
            elemName = self.fromXmlTranslation[elemName]
          structType = eval(elemName)          
          cfgStruct = structType(cfgServer = self.cfgServer)        
          cfgStruct.fromXMLToPyObj_J(elem)
          valList.append(cfgStruct)
        setattr(self, fieldName, valList) 
      elif fieldName in self.dbidListFields():
        #print "4 setting %s, %s" %(fieldName, fieldValue)
        
        elemList = self.toElemList_J(nd)
        if elemList == None: return
        valList = []
        for elem in elemList:
          valList.append(int(elem.getAttribute("value")))
        setattr(self, fieldName, valList)   
      elif fieldName in self.kvListFields():
        #print "5 setting %s, %s" %(fieldName, fieldValue)
        kvValue = self.getKVListFromElem_J(nd)
        setattr(self, fieldName, kvValue)  
      else:
        ProgrammError("Unknown type %s " %fieldName)
  
  def getKVListFromElem_J(self, el):
    pairList = self.toElemList_J(el)
    if pairList == None: return None
    options = {}
    for pair in pairList: 
      if pair.getNodeName() == "list_pair":
        pairKey = pair.getAttribute("key")
        pairValue = self.getKVListFromElem_J(pair)
        options[pairKey] = pairValue

      elif pair.getNodeName() == "str_pair":
        pairKey = pair.getAttribute("key")
        pairValue = pair.getAttribute("value")
        options[pairKey] = pairValue

      elif pair.getNodeName() == "int_pair":
        pairKey = pair.getAttribute("key")
        pairValue = int(pair.getAttribute("value"))
        options[pairKey] = pairValue
      elif pair.getNodeName() == "bin_pair":
        pairKey = pair.getAttribute("key")
        pairValue = "BINARY_" + pair.getAttribute("value")
        options[pairKey] = pairValue          
    return options
              

      
      
  def fromKvListToXmlEl_J(self, doc, kvList, tag, key = None):
    #print "Section %s" %tag
    
    listik = doc.createElement(tag)
    
    if key:
      listik.setAttribute("key", key)
    for key in kvList.keys():
      pair = None
      if type(kvList[key]) == type({}):
        pair = self.fromKvListToXmlEl_J(doc, kvList[key], "list_pair", key, )
      elif type(kvList[key]) == type(0):
        pair = doc.createElement("int_pair")
        pair.setAttribute("key", key)
        pair.setAttribute("value", str(kvList[key]))
      elif type(kvList[key]) in (type(""), type(u'')) and  kvList[key].find("BINARY_") <> -1:
        pair = doc.createElement("bin_pair")
        pair.setAttribute("key", key)
        pair.setAttribute("value", kvList[key][7:])      
      elif type(kvList[key]) in (type(""), type(u'')) :
        pair = doc.createElement("str_pair")
        pair.setAttribute("key", key)
        pair.setAttribute("value", str(kvList[key]))
      elif type(kvList[key]) == type(None):
        pair = doc.createElement("str_pair")
        pair.setAttribute("key", key)
      else:
        ProgrammError("Unknown type kvList %s key %s" %(kvList, key))
      
      listik.appendChild(pair)
    return listik
         
        
    
  def fromPythonObjectToXMLEl_J(self, doc, tag): 
    elCfgObj = doc.createElement(tag)
    for pair in self.fields:
      fieldName = pair[0]
      fieldType = pair[1]
      fieldEl = None
      fieldValue = getattr(self, fieldName)
      if fieldName in self.simpleFields():
        #if fieldValue or (isinstance(self, CfgStruct) and fieldType == "Int") or fieldName == "customType":
        if fieldValue or isinstance(self, CfgStruct) or fieldType == "Int" or fieldName == "customType":  
        
          if self.toXmlTranslation.has_key(fieldName):
            fieldName = self.toXmlTranslation[fieldName]
          fieldEl = doc.createElement(fieldName)
          fieldEl.setAttribute("value", str(fieldValue))

      elif fieldName in self.structFields():
        if  fieldValue:
          xmlFieldName = self.toXmlTranslation[fieldName]
          fieldEl = fieldValue.fromPythonObjectToXMLEl_J(doc, xmlFieldName)
      elif fieldName in self.listOfStructsFields():
        if  fieldValue:  
          fieldEl = doc.createElement(fieldName)
          for fieldValueI in fieldValue:
            if fieldValueI:
              xmlFieldNameI = fieldType[14:]
              fieldElI = fieldValueI.fromPythonObjectToXMLEl_J(doc, xmlFieldNameI)
              fieldEl.appendChild(fieldElI)
      elif fieldName in self.arrayOfStructsFields():
        if  fieldValue:  
          fieldEl = doc.createElement(fieldName)
          for fieldValueI in fieldValue:
            if fieldValueI:
              xmlFieldNameI = fieldType[15:]
              fieldElI = fieldValueI.fromPythonObjectToXMLEl_J(doc, xmlFieldNameI)
              fieldEl.appendChild(fieldElI)
      elif fieldName in self.dbidListFields():
        if  fieldValue:  
          fieldEl = doc.createElement(fieldName)
          for fieldValueI in fieldValue:
            fieldElI = doc.createElement("DBID")
            fieldElI.setAttribute("value", str(fieldValueI))
            fieldEl.appendChild(fieldElI)

      elif fieldName in self.kvListFields():
        if  fieldValue: 
          fieldEl = self.fromKvListToXmlEl_J(doc, fieldValue, fieldName)
          #fieldEl.appendChild(self.fromKvListToXmlEl_J(doc, fieldValue, fieldName))
      else:
        ProgrammError("2 Unknown type %s " %fieldName)
      if fieldEl:
        elCfgObj.appendChild(fieldEl)
    return elCfgObj
    
  #.NET    
  def toElemList_N(self, el):
    confElemList = None
    if el: 
      el = el.FirstChild #first CfgObj
      if el:
        confElemList = []
        confElemList.append(el)
        while 1:
          el = el.NextSibling #next CfgObj
          if el:
            confElemList.append(el)  
          else:
            break
    return confElemList  
  
  def setAttrFromElem_N(self, nd):
    fieldName = nd.Name
    fieldValue = nd.GetAttribute("value")

    if fieldValue: #simple type:
      #print "1 setting %s, %s" %(fieldName, fieldValue)
      self.setValueWithSimpleType(fieldName, fieldValue)
    else: # complexType
      if fieldName in self.structFieldsX():
        #print "2 setting %s, %s" %(fieldName, fieldValue)
        structType = eval(fieldName)
        cfgStruct = structType(cfgServer = self.cfgServer)
        cfgStruct.fromXMLToPyObj_N(nd)
        if self.fromXmlTranslation.has_key(fieldName):
          fieldName = self.fromXmlTranslation[fieldName]  
          #print "new fieldName %s" %fieldName
        else:
          ProgrammError("please send to masha, no %s in %s fromXMLTranslation" %(fieldName, self))
        setattr(self, fieldName, cfgStruct)
        
        
      elif fieldName in self.listOfStructsFields() or fieldName in self.arrayOfStructsFields():
        #print "3 setting %s, %s" %(fieldName, fieldValue)
        elemList = self.toElemList_N(nd)
        if elemList == None: return
        valList = []
        for elem in elemList:
          elemName = elem.Name
          if self.fromXmlTranslation.has_key(elemName):
            elemName = self.fromXmlTranslation[elemName]           
          structType = eval(elemName)
          cfgStruct = structType(cfgServer = self.cfgServer)        
          cfgStruct.fromXMLToPyObj_N(elem)
          valList.append(cfgStruct)
        setattr(self, fieldName, valList) 
      elif fieldName in self.dbidListFields():
        #print "4 setting %s, %s" %(fieldName, fieldValue)
        
        elemList = self.toElemList_N(nd)
        if elemList == None: return
        valList = []
        for elem in elemList:
          valList.append(int(elem.GetAttribute("value")))
        setattr(self, fieldName, valList)   
      elif fieldName in self.kvListFields():
        #print "5 setting %s, %s" %(fieldName, fieldValue)
        kvValue = self.getKVListFromElem_N(nd)
        setattr(self, fieldName, kvValue)  
      else:
        ProgrammError("Unknown type %s " %fieldName)
  
  def getKVListFromElem_N(self, el):
    pairList = self.toElemList_N(el)
    if pairList == None: return None
    options = {}
    for pair in pairList: 
      if pair.Name == "list_pair":
        pairKey = pair.GetAttribute("key")
        pairValue = self.getKVListFromElem_N(pair)
        options[pairKey] = pairValue

      elif pair.Name == "str_pair":
        pairKey = pair.GetAttribute("key")
        pairValue = pair.GetAttribute("value")
        options[pairKey] = pairValue

      elif pair.Name == "int_pair":
        pairKey = pair.GetAttribute("key")
        pairValue = int(pair.GetAttribute("value"))
        options[pairKey] = pairValue
      elif pair.Name == "bin_pair":
        pairKey = pair.GetAttribute("key")
        pairValue = "BINARY_" + pair.GetAttribute("value")
        options[pairKey] = pairValue          
    return options
              

      
      
  def fromKvListToXmlEl_N(self, doc, kvList, tag, key = None):
    #print "Section %s" %tag
    
    listik = doc.CreateElement(tag)
    
    if key:
      listik.SetAttribute("key", key)
    for key in kvList.keys():
      pair = None
      if type(kvList[key]) == type({}):
        pair = self.fromKvListToXmlEl_N(doc, kvList[key], "list_pair", key, )
      elif type(kvList[key]) == type(0):
        pair = doc.CreateElement("int_pair")
        pair.SetAttribute("key", key)
        pair.SetAttribute("value", str(kvList[key]))
      elif type(kvList[key]) == type("") and  kvList[key].find("BINARY_") <> -1:
        pair = doc.CreateElement("bin_pair")
        pair.SetAttribute("key", key)
        pair.SetAttribute("value", kvList[key][7:])      
      elif type(kvList[key]) in (type(""), type(u'')) :
        pair = doc.CreateElement("str_pair")
        pair.SetAttribute("key", key)
        pair.SetAttribute("value", str(kvList[key]))
      elif type(kvList[key]) == type(None):
        pair = doc.CreateElement("str_pair")
        pair.SetAttribute("key", key)
      else:
        ProgrammError("Unknown type kvList %s key %s" %(kvList, key))
      
      listik.AppendChild(pair)
    return listik
         
        
    
  def fromPythonObjectToXMLEl_N(self, doc, tag):
    elCfgObj = doc.CreateElement(tag)
    for pair in self.fields:
      fieldName = pair[0]
      fieldType = pair[1]
      fieldEl = None
      fieldValue = getattr(self, fieldName)

      if fieldName in self.simpleFields():
        if fieldValue or (isinstance(self, CfgStruct) and fieldType == "Int"):
        
          if self.toXmlTranslation.has_key(fieldName):
            fieldName = self.toXmlTranslation[fieldName]
          fieldEl = doc.CreateElement(fieldName)
          fieldEl.SetAttribute("value", str(fieldValue))

      elif fieldName in self.structFields():
        if  fieldValue:
          xmlFieldName = self.toXmlTranslation[fieldName]
          fieldEl = fieldValue.fromPythonObjectToXMLEl_N(doc, xmlFieldName)
      elif fieldName in self.listOfStructsFields():
        if  fieldValue:  
          fieldEl = doc.CreateElement(fieldName)
          for fieldValueI in fieldValue:
            if fieldValueI:
              xmlFieldNameI = fieldType[14:]
              fieldElI = fieldValueI.fromPythonObjectToXMLEl_N(doc, xmlFieldNameI)
              fieldEl.AppendChild(fieldElI)
      elif fieldName in self.arrayOfStructsFields():
        if  fieldValue:  
          fieldEl = doc.CreateElement(fieldName)
          for fieldValueI in fieldValue:
            if fieldValueI:
              xmlFieldNameI = fieldType[15:]
              fieldElI = fieldValueI.fromPythonObjectToXMLEl_N(doc, xmlFieldNameI)
              fieldEl.AppendChild(fieldElI)
      elif fieldName in self.dbidListFields():
        if  fieldValue:  
          fieldEl = doc.CreateElement(fieldName)
          for fieldValueI in fieldValue:
            fieldElI = doc.CreateElement("DBID")
            fieldElI.SetAttribute("value", str(fieldValueI))
            fieldEl.AppendChild(fieldElI)

      elif fieldName in self.kvListFields():
        if  fieldValue: 
          fieldEl = self.fromKvListToXmlEl_N(doc, fieldValue, fieldName)
          #fieldEl.appendChild(self.fromKvListToXmlEl_N(doc, fieldValue, fieldName))
      else:
        ProgrammError("3 Unknown type %s " %fieldName)
      if fieldEl:
        elCfgObj.AppendChild(fieldEl)
    return elCfgObj  
  #-----------------------
  #  2 BASIC FUNCTIONS
  #-----------------------
  #JAVA
  

  def fromXMLToPyObj_J(self, confElem):
    self.createEmptyObject()
    nd = confElem.getFirstChild() #firstAttr
    self.setAttrFromElem_J(nd)
    while 1:
      nd = nd.getNextSibling() #nextAttr
      if not nd:
        break  
      self.setAttrFromElem_J(nd)
      
  def fromPythonObjectToXML_J(self):
    dbf = DocumentBuilderFactory.newInstance()
    dbf.setNamespaceAware(True);
    documentBuilder = dbf.newDocumentBuilder()
    doc = documentBuilder.newDocument()
    CFG_NS = self.cfgServer.serverProtocol.PROTOCOL_DESCRIPTION.getNS();
    
    elConfData = doc.createElementNS(CFG_NS, "ConfData")
    elCfgObj = self.fromPythonObjectToXMLEl_J(doc, self.title ) 
    elConfData.appendChild(elCfgObj)
    doc.appendChild(elConfData)
    
    return doc
  #.NET  
  def fromXMLToPyObj_N(self, confElem):
    self.createEmptyObject()
    nd = confElem.FirstChild #firstAttr
    self.setAttrFromElem_N(nd)
    while 1:
      nd = nd.NextSibling #nextAttr
      if not nd:
        break  
      self.setAttrFromElem_N(nd)
      
  def fromPythonObjectToXML_N(self):
    doc = XmlDocument()
    elConfData = doc.CreateElement("ConfData")
    elCfgObj = self.fromPythonObjectToXMLEl_N(doc, self.title) 
    elConfData.AppendChild(elCfgObj)
    doc.AppendChild(elConfData)
    
    return doc    
    
#------------------------------------------------------------------
#END XML !!!
#------------------------------------------------------------------
  def fromXMLToPythObject(self, obj):
    if InTrue(GetOption("Java")): #java
      return self.fromXMLToPyObj_J(obj)
    elif InTrue(GetOption("DotNet")): #dotnet
      return self.fromXMLToPyObj_N(obj)  

  def fromStringToPythObject(self, obj):
    if InTrue(GetOption("Java")): #java
      return self.fromXMLToPyObj_J(obj)
    elif InTrue(GetOption("DotNet")): #dotnet
      return self.fromXMLToPyObj_N(obj)       
    if not obj: return None
    self.tmpStrObj = obj
    for (attr, type) in self.fields:
      if type:
        if type[0:13] =="ListOfStructs":
          structType = type[14:]
          meth = "getListOfStructsAttr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to get attribute " + meth + " is not found")
          obj = method(attr, structType, obj)    
        elif type[0:14] =="ArrayOfStructs":
          structType = type[15:]
          meth = "getArrayOfStructsAttr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to get attribute " + meth + " is not found")
          obj = method(attr, structType, obj)     
          
        elif type[0:6] =="Struct":
          structType = type[7:]
          meth = "getStructAttr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to get attribute " + meth + " is not found")
          obj = method(attr, structType, obj)            
        else:
          meth = "get" + type + "Attr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to get attribute " + meth + " is not found")
          try:
            obj = method(attr, obj)
          except Exception, mess:
            ProgrammError("Cannot set attribute %s"%attr + " " + str(mess))
          #print "NextObj"
          #print self.tmpStrObj
          #print "@@@@@@@@@@"
    return


  def fromPythonObjectToXML(self):
    if InTrue(GetOption("Java")):
      return self.fromPythonObjectToXML_J()
    elif InTrue(GetOption("DotNet")): #dotnet
      return self.fromPythonObjectToXML_N()
    
  def fromPythonObjectToString(self):
    if InTrue(GetOption("Java")):
      return self.fromPythonObjectToXML_J()
    elif InTrue(GetOption("DotNet")): #dotnet
      return self.fromPythonObjectToXML_N()
    if self.title:
      cfgString = self.title + "="
    else:
      cfgString = ""
      
    attr, type =  self.fields[0]  
    if type:
      if type[0:13] =="ListOfStructs":
        structType = type[14:]
        meth = "setListOfStructsAttr"
        try:
          method = getattr(self, meth)
        except AttributeError:
          ProgrammError("Method to set attribute " + meth + " is not found")
        cfgString = cfgString + '\035' + method(attr, structType, getattr(self,attr))
      elif type[0:14] =="ArrayOfStructs":
        structType = type[15:]
        meth = "setArrayOfStructsAttr"
        try:
          method = getattr(self, meth)
        except AttributeError:
          ProgrammError("Method to set attribute " + meth + " is not found")
        cfgString = cfgString + '\035' + method(attr, structType, getattr(self,attr))
     
      elif type[0:6] =="Struct":
      
        structType = type[7:]
        meth = "setStructAttr"
        try:
          method = getattr(self, meth)
        except AttributeError:
          ProgrammError("Method to set attribute " + meth + " is not found")
        cfgString = cfgString + '\035' +method(attr, structType, getattr(self,attr))          
      else:
        meth = "set" + type + "Attr"
        try:
          method = getattr(self, meth)
        except AttributeError:
          ProgrammError("Method to set attribute " + meth + " is not found")
        cfgString = cfgString + '\035' +method(attr, getattr(self,attr))    
    for (attr, type) in self.fields[1:]:
      if type:
        if type[0:13] =="ListOfStructs":
          structType = type[14:]
          meth = "setListOfStructsAttr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to set attribute " + meth + " is not found")
          cfgString = cfgString + '\030' +method(attr, structType, getattr(self,attr))
        elif type[0:14] =="ArrayOfStructs":
          structType = type[15:]
          meth = "setArrayOfStructsAttr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to set attribute " + meth + " is not found")
          cfgString = cfgString + '\030' + method(attr, structType, getattr(self,attr))
          
        elif type[0:6] =="Struct":
          structType = type[7:]
          meth = "setStructAttr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to set attribute " + meth + " is not found")
          cfgString = cfgString + '\030' + method(attr, structType, getattr(self,attr))          
        else:
          meth = "set" + type + "Attr"
          try:
            method = getattr(self, meth)
          except AttributeError:
            ProgrammError("Method to set attribute " + meth + " is not found")
          cfgString = cfgString + '\030' +method(attr, getattr(self,attr))
    cfgString = cfgString + "\036"
    return cfgString
     
  def SaveInitialObject(self):
    """Call this function to save a specific object state, at the end of testing
    objects will be set to this state"""
    self.initialObject = self.fromPythonObjectToString() 
    
    
  #Get attributes - methods to get attrs from cfgString 
  
  def getStructAttr(self, attr, structType, obj):
    pattern = attr + "=(NIL)"
    matchObj = re.search(pattern, self.tmpStrObj)
    if matchObj:
      self.tmpStrObj = obj[matchObj.end(1)+1:]
      setattr(self, attr, None)
    else:
      structType = eval(structType)
      st = structType(self.tmpStrObj, cfgServer = self.cfgServer)
      setattr(self, attr, st)
      self.tmpStrObj = st.tmpStrObj
    return obj

    
  def setStructAttr(self, attr, structType, pyAttr): 
    cfgString = ""
    if pyAttr == None:
      cfgString = attr + "=NIL"
    else: 
      cfgString = attr + "="
      addStr = pyAttr.fromPythonObjectToString()
      cfgString = cfgString + addStr
    return cfgString
  
  def getListOfStructsAttr(self, attr, structType, obj):

    pattern = attr + "=(NIL)"
    matchObj = re.search(pattern, self.tmpStrObj)
    if matchObj:
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
      setattr(self, attr, None)
    else:
      structType = eval(structType)
      listOfStructs = [] 
      pattern = attr + "=\033(.*?\034)?[\030\036]"
      #pattern = attr + "=\033(.*\035)"
      matchObj1 = re.search(pattern, self.tmpStrObj)
      strStructs = matchObj1.group(1) 
      pattern = "(.*?\036)?[\030\034]"
      #pattern = "([^\036]*\036)"
      matchObj = re.search(pattern, strStructs)
      strStruct = matchObj.group(1) 
      while strStruct:
        matchObj = re.search(pattern, strStructs)
        if matchObj:
          strStruct = matchObj.group(1)    
          strStructs  = strStructs[matchObj.end(1)+1:]
          st = structType(strStruct, cfgServer = self.cfgServer)
          listOfStructs.append(st)
        else:
          strStruct = ""
      self.tmpStrObj = self.tmpStrObj[matchObj1.end(1)+1:]
      setattr(self, attr, listOfStructs)
    return obj
    
    
  def setListOfStructsAttr(self, attr, structType, pyAttr): 
    cfgString = ""
    if pyAttr == None:
      cfgString = attr + "=NIL"
    else: 
      cfgString = attr + "=\033"
      if pyAttr:
        struct = pyAttr[0]
        addStr = struct.fromPythonObjectToString()
        cfgString = cfgString + addStr
        i = 1
        for struct in pyAttr[1:]:
          cfgString = cfgString +"\030"
          addStr = struct.fromPythonObjectToString()
          cfgString = cfgString + addStr
          i = i + 1
      cfgString = cfgString + "\034"  
    return cfgString  

  def getArrayOfStructsAttr(self, attr, structType, obj):

    pattern = attr + "=(NIL)"
    matchObj = re.search(pattern, self.tmpStrObj)
    if matchObj:
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
      setattr(self, attr, None)
    else:
      structType = eval(structType)
      listOfStructs = [] 
      pattern = attr + "=\035(.*)"
      matchObj1 = re.search(pattern, self.tmpStrObj)
      strStructs = matchObj1.group(1)
      pattern = "(\035.*?%s)" %attr
      
      patternEnd = "(\035.*?\034)"
      matchObj = re.search(pattern, strStructs)
      strStruct = matchObj.group(1) 
      while 1:
        structEnd = 0
        matchObj = re.search(pattern, strStructs)
        if matchObj:
          strStruct = matchObj.group(1)  
        else:
          structEnd = 1
          matchObj = re.search(patternEnd, strStructs)
          strStruct = matchObj.group(1)  
          
        strStructs  = strStructs[matchObj.end(1)+1:]

        st = structType(strStruct, cfgServer = self.cfgServer)
        listOfStructs.append(st)
        if structEnd: break
        else:
          strStruct = ""
      self.tmpStrObj = self.tmpStrObj[matchObj1.end(1)+1:]
      setattr(self, attr, listOfStructs)
    return obj

  def setArrayOfStructsAttr(self, attr, structType, pyAttr): 

    cfgString = ""
    if pyAttr == None:
      cfgString = attr + "=NIL"
    else: 
      cfgString = attr + "=\033"
      if pyAttr:
        struct = pyAttr[0]
        addStr = attr + "=" + struct.fromPythonObjectToString()
        cfgString = cfgString + addStr
        i = 1
        for struct in pyAttr[1:]:
          cfgString = cfgString +"\030"
          addStr = struct.fromPythonObjectToString()
          cfgString = cfgString + attr + "=" + addStr
          i = i + 1
      cfgString = cfgString + "\034"  
    return cfgString  

  def retrieveFirstSect(self):
    pattern = "\031(([^\027\030\031\032\033\035\036\037]*?=)(.*?\032)).*"
    matchObj = re.match(pattern, self.tmpStrObj)
    if matchObj:
      sect = matchObj.group(2)[:-1]
      self.tmpStrObj = self.tmpStrObj[matchObj.end(2):]
      return sect

  def retrieveNextSect(self):
    pattern = "\030(([^\027\030\031\032\033\035\036\037]*?=)(.*?\032)).*"
    matchObj = re.match(pattern, self.tmpStrObj)
    if matchObj:
      sect = matchObj.group(2)[:-1]
      self.tmpStrObj = self.tmpStrObj[matchObj.end(2):]
      return sect

  def retrieveFirstOpt(self):
    pattern = "\031\032.*"       #empty section
    matchObj = re.match(pattern, self.tmpStrObj)
    if matchObj:
      self.tmpStrObj = self.tmpStrObj[2:]
      return
    pattern = "\031(([^\027\030\031\032\033\035\036\037]*?=)(\037.*?\037)).*"       #string value
    matchObj = re.match(pattern, self.tmpStrObj)
    if matchObj:
      key = matchObj.group(2)[:-1]
      val = matchObj.group(3)[1:-1] 
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1):]
      return (key, val)
    else:
      pattern = "^\031(([^\027\030\031\032\033\035\036\037]*?=)([0-9]+)).*"          #int value
      matchObj = re.match(pattern, self.tmpStrObj)
      if matchObj:
        key = matchObj.group(2)[:-1]
        val = int(matchObj.group(3))
        self.tmpStrObj = self.tmpStrObj[matchObj.end(1):]
        return (key, val)   
      else:
        pattern = "^\031(([^\027\030\031\032\033\035\036\037]*?=)(\027.*?\027)).*"          #bin value
        matchObj = re.match(pattern, self.tmpStrObj)
        if matchObj:
          key = matchObj.group(2)[:-1]
          val = (matchObj.group(3)[1:-1])
          self.tmpStrObj = self.tmpStrObj[matchObj.end(1):]
          val = "BINARY" + val
          return (key, val)
        else:
          if self.tmpStrObj[0] <> '\031':
            self.tmpStrObj = self.tmpStrObj[1:]
          

  def retrieveNextOpt(self):
    pattern = "^\030(([^\027\030\031\032\033\035\036\037]*?=)(\037.*?\037)).*"       #string value
    matchObj = re.match(pattern, self.tmpStrObj)
    if matchObj:
      key = matchObj.group(2)[:-1]
      val = matchObj.group(3)[1:-1]
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1):]
      return (key, val)  
    else:
      pattern = "^\030(([^\027\030\031\032\033\035\036\037]*?=)([0-9]+)).*"          #int value
      matchObj = re.match(pattern, self.tmpStrObj)
      if matchObj:
        key = matchObj.group(2)[:-1]
        val = int(matchObj.group(3))
        self.tmpStrObj = self.tmpStrObj[matchObj.end(1):]
        return (key, val)  
      else:
        pattern = "^\030(([^\027\030\031\032\033\035\036\037]*?=)(\027.*?\027)).*"          #bin value
        matchObj = re.match(pattern, self.tmpStrObj)
        if matchObj:
          key = matchObj.group(2)[:-1]
          val = (matchObj.group(3)[1:-1])
          self.tmpStrObj = self.tmpStrObj[matchObj.end(1):]
          val = "BINARY" + val
          return (key, val)
        else:
          if self.tmpStrObj[0] <> '\031':
            self.tmpStrObj = self.tmpStrObj[1:]
  
  def retrieveVals(self):
    opts = self.retrieveOpts()   
    if opts:
      return opts
    else:
      opts = {}
      sect = self.retrieveFirstSect()
      while sect:
        opts[sect] = self.retrieveVals()
        sect = self.retrieveNextSect()      
      return opts
    
  
  def retrieveOpts(self):
    opts = {}
    tup = self.retrieveFirstOpt()
    while tup:
      opts[tup[0]] = tup[1]
      tup = self.retrieveNextOpt()      
    return opts    
  

  def getKVListAttr(self, attr, obj):

    self.tmpStrObj = self.tmpStrObj.replace("\r\n", "")
    options = None
    pattern = attr + "=(NIL)"
    matchObj = re.search(pattern, self.tmpStrObj)
    if matchObj: 
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
      setattr(self, attr, None)
      
    else:
      if attr == "flexibleProperties":
        pass
      pattern = attr + "=\031\032"
      matchObj = re.search(pattern, self.tmpStrObj)
      if matchObj:
        setattr(self, attr, {})
      else:
        pattern = attr + "=(.*?\032\032)"
        matchObj = re.search(pattern, self.tmpStrObj)
        oldStr = self.tmpStrObj
        self.tmpStrObj = matchObj.group(1) 
        options = {}
        sect = self.retrieveFirstSect()
        while sect:
          options[sect] = self.retrieveVals()
          sect = self.retrieveNextSect()
        setattr(self, attr,  options)
        self.tmpStrObj = oldStr[matchObj.end(1)+1:]
    return obj
  
  def getDBIDAttr(self, attr, obj):
    return  self.getIntAttr(attr, obj)
  
        
  def getCharAttr(self, attr, obj):
    pattern = attr + "=(NIL)"
    matchObj = re.search(pattern, self.tmpStrObj)
    if matchObj: 
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
      setattr(self, attr, None)
    else:
      pattern = attr + "=\037([^\030\031\032\033\035\036\037]*)\037[\030,\036]"
      matchObj = re.search(pattern, self.tmpStrObj)
      setattr(self, attr, matchObj.group(1))
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
    return obj
      
  
  def getIntAttr(self, attr, obj):
    pattern = attr + "=([0-9\-]+)[\030,\036]"
    matchObj = re.search(pattern, self.tmpStrObj)
    setattr(self, attr, int(matchObj.group(1)) ) 
    self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
    return obj


  def getDBIDListAttr(self, attr, obj):
    #----DBIDList---
    DBIDList = None
    pattern = attr + "=(NIL)"
    matchObj = re.search(pattern, self.tmpStrObj)
    if matchObj:
      self.tmpStrObj = self.tmpStrObj[matchObj.end(1)+1:]
      setattr(self, attr, None)
    else:
      DBIDList = []
      pattern = attr + "=\033(.*?\034)[\030,\036]"
      matchObj1 = re.search(pattern, self.tmpStrObj)
      structs = matchObj1.group(1)
      
      while 1:
        pattern = "([0-9]+)"
        matchObj = re.search(pattern, structs)
        DBIDList.append(int(matchObj.group(1)))
        structs = structs[matchObj.end(1):]
        if structs == "\034": break  
      self.tmpStrObj = self.tmpStrObj[matchObj1.end(1)+1:]
      setattr(self, attr, DBIDList) 
    return obj
  #Set attributes - methods to retrieve attrs from python object and set them to CfgString object

  def setCharAttr(self, attr, pyAttr):
    cfgStr = ""
    if pyAttr == None:
      cfgStr = attr + "=NIL"
    else:
      cfgStr =  attr + "=\037" + pyAttr + "\037"
    return cfgStr
    
  def setIntAttr(self, attr, pyAttr):
    cfgStr = ""
    cfgStr = attr + "=" + str(pyAttr)
    return cfgStr
    
  def setDBIDAttr(self, attr, pyAttr):
    return self.setIntAttr(attr, pyAttr)
    
  def setKVListAttr(self, attr, pyAttr):
    cfgStr = ""
    options = pyAttr
    if options == None:
      cfgStr =  attr +"=NIL"
    else:
      cfgStr =  attr +"=" 
      s = self.setRecKVlist(options)
      cfgStr = cfgStr + s
    return cfgStr
   
  
  def setRecKVlist(self,  options): 
    cfgStr = ""
    if options == {}:
      cfgStr = cfgStr + "\031\032"
      return cfgStr  
    else:
      i = 1
      

      for optName in options.keys():
        if i == 1: cfgStr = cfgStr + "\031"
        else:        cfgStr = cfgStr + "\030"
        i = i + 1    
        cfgStr = cfgStr + str(optName) + "="
        j = 1
        nextOptions = options[optName]

        if nextOptions == {}:
          cfgStr = cfgStr + "\031\032"
        else:
          if type(nextOptions) == type({}):
            cfgStr = cfgStr + self.setRecKVlist(nextOptions)
          elif type(nextOptions) in (type(""), type(u'')) :
            if len(nextOptions) > 6 and nextOptions[0:6] == "BINARY":
              cfgStr = cfgStr +  "\027" + nextOptions[6:] + "\027"
            else:  
              cfgStr = cfgStr +  "\037" + nextOptions + "\037"
          else:
            cfgStr = cfgStr +  str(nextOptions)            
    cfgStr = cfgStr + "\032" 
    return cfgStr  
  
  

   
  def setDBIDListAttr(self, attr, pyAttr):
    #-----DBIDList-----
    cfgString = ""
    if pyAttr == None:
      cfgString = attr + "=NIL"
    else:
      cfgString =  attr + "=\033"
      if pyAttr:
        ten = pyAttr[0]
        cfgString = cfgString + str(ten)  
      for ten in pyAttr[1:]:
        cfgString = cfgString + '\030' + str(ten)  
      cfgString = cfgString + "\034"
    return cfgString   
  
     
  def ChangeState(self, state):
    self.BeginChange()
    if type(state) == type(0):
      self.state = state
    else:
      self.state = state.val # enum
    return self.EndChange()
    
    
    
  def Enable(self):
    self.ChangeState(CfgObjectState.CFGEnabled)


  def Disable(self):
    self.ChangeState(CfgObjectState.CFGDisabled)
  
     
  def AddOption(self, section, key, value, annex = 0): 
    """return 1 - success, desired option is set to desired value, 0 - option not changed"""
    if not annex:
      options = copy.deepcopy(self.options)
    else:
      options = copy.deepcopy(self.userProperties)
    if not options: options = {}
    changeNeeded = 1
    sec = dicGetKeyNoCase(options, str(section))
    if not sec:
      options[str(section)] = {str(key): value}
    else:
      opts = options[sec]
      k = dicGetKeyNoCase(opts, str(key))
      if k:
        if opts[k] <> value:
          opts[k] = value
        else:
          changeNeeded = 0
      else:
        opts[key] = value
    nm = ""
    if hasattr(self, "name"):
      nm = self.name + ":"
    elif hasattr(self, "number"):
      nm = self.number + ":"       
        
    if changeNeeded:
      self.printLog("%s setting option %s to %s in section %s, annex = %s" %(nm,  key, value, section, annex))
      self.BeginChange()  
      if not annex:
        self.options = copy.copy(options)
      else:
        self.userProperties = copy.copy(options)
      return self.EndChange()
    else:
      self.printLog("%s option %s in section %s, annex = %s is already set to %s" %(nm,  key, section, annex, value))
    return 1 # no change needed

  def ChangeOption(self, section, key, value, annex = 0): 
    return CfgObject.AddOption(self, section, key, value, annex)
 
 
  def DeleteOption(self, section, key, annex = 0):  
    """section could be None, in this case first found option with key = key is deleted"""
    self.BeginChange()
    if not annex:
      options = copy.deepcopy(self.options)
    else:
      options = copy.deepcopy(self.userProperties)
    if not options:
      self.printLog(" Option " + key + " is not found")  
      return 1
    oldKey = key
    if not section:
      for sect in options.keys():
        opts = options[sect]
        key = dicGetKeyNoCase(opts, str(key))
        if key:
          nm = ""
          if hasattr(self, "name"):
            nm = self.name + ":"
          elif hasattr(self, "number"):
            nm = self.number + ":"       
          self.printLog("%s deleting option %s in section %s, annex = %s" %(nm,  key, section, annex))
        
          del opts[key]
          options[sect] = opts
          if not annex:
            self.options = copy.copy(options)
          else:
            self.userProperties = copy.copy(options)
          return self.EndChange()
          
    else:
      section = dicGetKeyNoCase(options, str(section))
      if section:
        opts = options[str(section)]
        key = dicGetKeyNoCase(opts, str(key))
        if key:
          nm = ""
          if hasattr(self, "name"):
            nm = self.name + ":"
          elif hasattr(self, "number"):
            nm = self.number + ":"       
          self.printLog("%s deleting option %s in section %s, annex = %s" %(nm,  key, section, annex))
        
          del opts[key]
          options[str(section)] = opts
          if not annex:
            self.options = copy.copy(options)
          else:
            self.userProperties = copy.copy(options)
          return self.EndChange()


    self.printLog(" Option " + str(oldKey) + " is not found")
    return 1
    
  def DeleteSection(self, section, annex = 0):
    self.BeginChange()
    if not annex:
      options = self.options
    else:
      options = self.userProperties
    if not options or not options.has_key(section):
      self.printLog(" Section " + str(section) + " is not found")
      return 1
    oldSection = section
    section = dicGetKeyNoCase(options, str(section))
    if section:
      nm = ""
      if hasattr(self, "name"):
        nm = self.name + ":"
      elif hasattr(self, "number"):
        nm = self.number + ":"       
      self.printLog("%s deleting section %s, annex = %s" %(nm, section, annex))
    
      del options[str(section)]
      if not annex:
        self.options = options
      else:
        self.userProperties = options
      return self.EndChange()
    else:
      self.printLog(" Section " + str(oldSection) + " is not found")
      return 1
  
  
  def FindOption(self, section = "", key = "", annex = 0): 
    """returns option value, None if option not found. if section is not scpecified, look in all sections, return the first found"""
    if not annex:
      options = self.options
    else:
      options = self.userProperties
    if not options: return None
    if section:
      sec = dicGetKeyNoCase(options, str(section))
      if sec:
        opts = options[sec]
        k = dicGetKeyNoCase(opts, str(key))
        if k: return opts[k]
    else:
      for sec in options.keys():
        if not sec[0] == '#': #do not look for commented sections
          opts = options[sec]
          k = dicGetKeyNoCase(opts, str(key))
          if k: return opts[k]      
    return None
  

  fields =     (("appServerDBID",       "Int"),
                ("connProtocol",        "Char"),
                ("timoutLocal",         "Int"),
                ("timoutRemote",        "Int"),
                ("traceMode",           "Int"),
                ("id",                  "Char"),
                ("transportParams",     "Char"),
                ("appParams",           "Char"),
                ("proxyParams",         "Char"),
                ("description",         "Char"),
                ("charField1",          "Char"),
                ("charField2",          "Char"),
                ("charField3",          "Char"),   
                ("charField4",          "Char"),
                ("longField1",          "Int"),
                ("longField2",          "Int"),   
                ("longField3",          "Int"),
                ("longField4",          "Int")) 
  
      

  


  def AddDBIDToDBIDList(self, attrName, DBID):
    DBIDList = getattr(self, attrName)
    if DBIDList and (DBID in DBIDList):
      Message("DBID %d is is already in the list, object type %s" %(DBID, str(self.objType)))  
      return
    self.BeginChange()
    if DBIDList == None:
      DBIDList = []    
    DBIDList.append(DBID)
    setattr(self, attrName, DBIDList)
    self.EndChange()

    
    
  def DeleteDBIDFromDBIDList(self, attrName, DBID):
    DBIDList = getattr(self, attrName)
    if not DBIDList or not (DBID in DBIDList):
      Message("Cannot delete from DBID list, DBID %d is not in the list, object type %s" %(DBID, str(self.objType)))
      return
    self.BeginChange()
    DBIDList.remove(DBID)
    setattr(self, attrName, DBIDList)
    self.EndChange()

  def SaveState(self):
    PrintLogStat("Save config state for object %s" % self.shortRepr()) 
    self.savedObject = self.fromPythonObjectToString() 
  
  def RestoreState(self, timeout = 5):
    if not self.savedObject: return
    PrintLogStat("Going to restore object %s" %self.veryShortRepr())
    currentObject = self.fromPythonObjectToString()
    if self.savedObject and self.savedObject != currentObject:
      try:
        PrintLogStat("Restoring object %s" %self.veryShortRepr())
        requestID = self.cfgServer.ChangeObject(self.objType, currentObject, self.savedObject)
        if requestID:
          ev = self.cfgServer.WaitEvent(requestID, timeout = timeout)
          if ev:
            method = getattr(self, "process" + str(ValToEnumElem(CfgEventName, ev.cfgEventType)))
            method(ev)
            self.cfgServer.GetUpdates(timeout = 0.1)
            PrintLogStat("Done")
          else:
            PrintLogStat("Object %s was not restored - no response" %self.veryShortRepr()) 
      except: # try to restore object in any case.
        PrintLogStat("Object %s was not restored" %self.veryShortRepr()) 
    else:
      PrintLogStat("Current object is identical to saved")
      
  def Restore(self, newObject = None, timeout = 0.1) :
    """Change object to newObject(string) or self.preserved"""
    if not self.restored:
      oldObject = self.fromPythonObjectToString()
      if newObject and newObject != oldObject:
        try:
          if self.cfgServer.ChangeObject(self.objType, oldObject, newObject): 
            self.cfgServer.GetUpdates(timeout = timeout)
        except: # try to restore object in any case.
          pass 
        self.restored = 1
        objs = self.cfgServer.FindAllObjectsByTypeAndDBID(self.objType, self.DBID)      
        for obj in objs:
          obj.restored = 1
          
  def GetLogCfgDAP(self):
    cfgMessageServer = None
    cfgSrvs = self.GetServers()
    for cfgSrv in cfgSrvs:
      if cfgSrv.type == CfgAppType.CFGMessageServer:
        cfgMessageServer = cfgSrv
        break
    if not cfgMessageServer: return     
    cfgSrvs = cfgMessageServer.GetServers()
    cfgDAP = None
    for cfgSrv in cfgSrvs:
      if cfgSrv.type == CfgAppType.CFGDBServer:
        #get DAP
        cfgDAP = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, cfgSrv.DBID) 
    return cfgDAP            

def GetObjectDBIDFromString(strObj):
  if InTrue(GetOption("Java")):
    return GetObjectDBIDFromString_J(strObj)
  if InTrue(GetOption("DotNet")):
    return GetObjectDBIDFromString_N(strObj)
  else:
    return GetObjectDBIDFromString_C(strObj)
    
def GetObjectCharPropertyFromString(strObj, propName):
  if InTrue(GetOption("Java")):
    return GetObjectCharPropertyFromString_J(strObj, propName)
  if InTrue(GetOption("DotNet")):
    return GetObjectCharPropertyFromString_N(strObj, propName)
  else:
    return GetObjectCharPropertyFromString_C(strObj, propName)   
  
def GetObjectIntPropertyFromString(strObj, propName):
  if InTrue(GetOption("Java")):
    return GetObjectIntPropertyFromString_J(strObj, propName)
  if InTrue(GetOption("DotNet")):
    return GetObjectIntPropertyFromString_N(strObj, propName)
  else:
    return GetObjectIntPropertyFromString_C(strObj, propName)
  
def GetObjectStructPropertyFromString(obj, strObj, propName, structType):
  if InTrue(GetOption("Java")):
    return GetObjectStructPropertyFromString_J(obj, strObj, propName, structType)
  if InTrue(GetOption("DotNet")):
    return GetObjectStructPropertyFromString_N(obj, strObj, propName, structType)
  else:
    return GetObjectStructPropertyFromString_C(obj, strObj, propName, structType)

def GetObjectDBIDFromString_J(strObj):
  #from xml
  nd = strObj.getFirstChild()
  fieldName = nd.getNodeName()
  if fieldName == "DBID":
    return int(nd.getAttribute("value"))
  while 1:
    nd = nd.getNextSibling() #nextAttr
    if not nd:
      break  
    fieldName = nd.getNodeName()
    if fieldName == "DBID":
      return int(nd.getAttribute("value"))
  ProgrammError("Cannot retrieve object property: DBID")      
    
    
def GetObjectCharPropertyFromString_J(strObj, propName):
  nd = strObj.getFirstChild()
  fieldName = nd.getNodeName()

  if fieldName == propName:
    return nd.getAttribute("value")
  while 1:
    nd = nd.getNextSibling() #nextAttr
    
    if not nd:
      break  
    fieldName = nd.getNodeName()
    if fieldName == propName:
      return nd.getAttribute("value")
  return ""
    
def GetObjectIntPropertyFromString_J(strObj, propName):
  nd = strObj.getFirstChild()
  fieldName = nd.getNodeName()

  if fieldName == propName:
    return int(nd.getAttribute("value"))
  while 1:
    nd = nd.getNextSibling() #nextAttr
    if not nd:
      break  
    fieldName = nd.getNodeName()
    if fieldName == propName:
      return int(nd.getAttribute("value"))
  return 0

def GetObjectStructPropertyFromString_J(obj, strObj, propName, structType):
  nd = strObj.getFirstChild()
  fieldName = nd.getNodeName()
  structType = eval(structType)
  cfgStruct = structType(cfgServer = obj.cfgServer)
  if obj.toXmlTranslation.has_key(propName):
    propName = obj.toXmlTranslation[propName]
  if fieldName == propName:
    cfgStruct.fromXMLToPyObj_J(nd)
    return cfgStruct 
  while 1:
    nd = nd.getNextSibling() #nextAttr
    if not nd:
      break  
    fieldName = nd.getNodeName()
    if fieldName == propName:
      cfgStruct.fromXMLToPyObj_J(nd)
      return cfgStruct 
  return None   
  
    
def GetObjectDBIDFromString_N(strObj):
  #from xml
  
  nd = strObj.FirstChild
  fieldName = nd.Name
  if fieldName == "DBID":
    return int(nd.GetAttribute("value"))
  while 1:
    nd = nd.NextSibling #nextAttr
    if not nd:
      break  
    fieldName = nd.Name
    if fieldName == "DBID":
      return int(nd.GetAttribute("value"))
  ProgrammError("Cannot retrieve object property: DBID")      
    
    
def GetObjectCharPropertyFromString_N( strObj, propName):
  nd = strObj.FirstChild
  fieldName = nd.Name

  if fieldName == propName:
    return nd.GetAttribute("value")
  while 1:
    nd = nd.NextSibling #nextAttr
    
    if not nd:
      break  
    fieldName = nd.Name
    if fieldName == propName:
      return nd.GetAttribute("value")
  return ""
    
def GetObjectIntPropertyFromString_N(strObj, propName):
  nd = strObj.FirstChild
  fieldName = nd.Name

  if fieldName == propName:
    return int(nd.GetAttribute("value"))
  while 1:
    nd = nd.NextSibling #nextAttr
    if not nd:
      break  
    fieldName = nd.Name
    if fieldName == propName:
      return int(nd.GetAttribute("value"))
  return 0

def GetObjectStructPropertyFromString_N(obj, strObj, propName, structType):
  nd = strObj.FirstChild
  fieldName = nd.Name
  structType = eval(structType)
  cfgStruct = structType(cfgServer = obj.cfgServer)
  if obj.toXmlTranslation.has_key(propName):
    propName = obj.toXmlTranslation[propName]
    
  if fieldName == propName:
    cfgStruct.fromXMLToPyObj_N(nd)
    return cfgStruct 
  while 1:
    nd = nd.NextSibling #nextAttr
    if not nd:
      break  
    fieldName = nd.Name
    if fieldName == propName:
      cfgStruct.fromXMLToPyObj_N(nd)
      return cfgStruct 
        
  return None

  
def GetObjectDBIDFromString_C(strObj):
  pattern = "\035" + "DBID" + "=([0-9]+)"
  matchObj = re.search(pattern, strObj)
  if matchObj:
    return int(matchObj.group(1))
  else:
    ProgrammError("Cannot retrieve object property: DBID")      
  return int(matchObj.group(1))       


def GetObjectCharPropertyFromString_C(strObj, propName):
  pattern = "\030" + propName + "=\037([^\030\031\032\033\035\036\037]*)\037"
  matchObj = re.search(pattern, strObj)
  if matchObj:
    return matchObj.group(1)    
  else:
    ProgrammError("Cannot retrieve object property: %s" % propName)      

def GetObjectIntPropertyFromString_C(strObj, propName):
  pattern = "\030" + propName + "=([0-9\-]+)"
  matchObj = re.search(pattern, strObj)
  if matchObj:
    return int(matchObj.group(1))
  else:
    ProgrammError("Cannot retrieve object property: %s" % propName)      

     
     
def GetObjectStructPropertyFromString_C(obj, strObj, propName, structType):
  pattern = propName + "=(NIL)"
  matchObj = re.search(pattern, strObj)  
  if matchObj: return None
  pattern = propName +"(=)"
  matchObj = re.search(pattern, strObj)  
  structType = eval(structType)
  st = structType(strObj[matchObj.end(1):])
  return st      
      
    
    
#==================================================================================
# Common CfgStructs
#==================================================================================
class CfgAddress(CfgStruct, CfgObject):
  """ CfgAddress object
  Fields:
    addressLine1 -        Char
    addressLine2 -        Char
    addressLine3 -        Char
    addressLine4 -        Char
    addressLine5 -        Char
  """
  fields =     (("addressLine1",          "Char"),
                ("addressLine2",          "Char"),
                ("addressLine3",          "Char"),
                ("addressLine4",          "Char"),
                ("addressLine5",          "Char"))
#==================================================================================
class CfgOS     (CfgStruct, CfgObject):
  """ CfgOS object
  Fields:
    OStype    -      Int
    OSversion -      Char
  """
  fields =     (("OStype",                "Int"),
                ("OSversion",             "Char"))
  translation = {"OStype":  "CfgOSType"}                 
  requiredFields = ["OStype"]   
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.OStype = CfgOSType.CFGWindows2000.val
    
CfgOSinfo = CfgOS # alias
#==================================================================================

class CfgSwitchAccessCode(CfgStruct, CfgObject):
  """ CfgSwitchAccessCode object
  Fields:
    switchDBID         -    Int
    accessCode         -    Char
    targetType         -    Int
    routeType          -    Int
    dnSource           -    Char
    destinationSource  -    Char
    locationSource     -    Char
    dnisSource         -    Char
    reasonSource       -    Char
    extensionSource    -    Char
  """
  fields =     (("switchDBID",           "Int"),
                ("accessCode",           "Char"),
                ("targetType",           "Int"),
                ("routeType",            "Int"),
                ("dnSource",             "Char"),
                ("destinationSource",    "Char"),
                ("locationSource",       "Char"),
                ("dnisSource",           "Char"),
                ("reasonSource",         "Char"),
                ("extensionSource",      "Char"))
  
  translation = {"targetType":  "CfgTargetType", "routeType": "CfgRouteType"} 
  requiredFields = ["switchDBID"] 
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.targetType = CfgTargetType.CFGTargetISCC.val
    self.routeType = CfgRouteType.CFGDefault.val
#==================================================================================

class CfgConnInfo(CfgStruct, CfgObject):
  """ CfgConnInfo object
  Fields:
    appServerDBID     -   Int
    connProtocol      -   Char
    timoutLocal       -   Int
    timoutRemote      -   Int
    traceMode         -   Int
    id                -   Char
    transportParams   -   Char
    appParams         -   Char
    proxyParams       -   Char
    description       -   Char
    charField1        -   Char
    charField2        -   Char
    charField3        -   Char
    charField4        -   Char
    longField1        -   Int
    longField2        -   Int
    longField3        -   Int
    longField4        -   Int
  """
  fields =     (("appServerDBID",       "Int"),
                ("connProtocol",        "Char"),
                ("timoutLocal",         "Int"),
                ("timoutRemote",        "Int"),
                ("traceMode",           "Int"),
                ("id",                  "Char"),
                ("transportParams",     "Char"),
                ("appParams",           "Char"),
                ("proxyParams",         "Char"),
                ("description",         "Char"),
                ("charField1",          "Char"),
                ("charField2",          "Char"),
                ("charField3",          "Char"),   
                ("charField4",          "Char"),
                ("longField1",          "Int"),
                ("longField2",          "Int"),   
                ("longField3",          "Int"),
                ("longField4",          "Int"))                  
              
                
  translation = {"traceMode":  "CfgTraceMode"} 
  requiredFields = ["appServerDBID"]   
  toXmlTranslation = {"traceMode": "mode"}
  fromXmlTranslation = {"mode": "traceMode"}
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.traceMode = CfgTraceMode.CFGTMNoTraceMode.val
    
CfgConnectionInfo = CfgConnInfo
#==================================================================================    
class CfgServer(CfgStruct, CfgObject):
  """ CfgServer object
  Fields:
    hostDBID          -   Int
    port              -   Char
    backupServerDBID  -   Int
    timeout           -   Int
    attempts          -   Int
  """
  fields =     (("hostDBID",            "Int"),
                ("port",                "Char"),
                ("backupServerDBID",    "Int"),
                ("timeout",             "Int"),
                ("attempts",            "Int"))
  requiredFields = ["hostDBID", "port"]  
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.timeout = 10
    self.timeout = 1
    
CfgServerInfo = CfgServer
#==================================================================================    
class CfgAlarmEvent(CfgStruct, CfgObject):
  """ CfgAlarmEvent object
  Fields:
    logEventID      -       Int
    selectionMode   -       Int
    appType         -       Int
    appDBID         -       Int
  """
  fields =     (("logEventID",            "Int"),
                ("selectionMode",         "Int"),
                ("appType",               "Int"),
                ("appDBID",               "Int"))
CfgDetectEvent =  CfgAlarmEvent
CfgRemovalEvent =  CfgAlarmEvent
#==================================================================================    
class CfgCallingListInfo(CfgStruct, CfgObject):
  """ CfgCallingListInfo object
  Fields:
    callingListDBID   -     Int
    share             -     Int
    isActive          -     Int
  """
  fields =     (("callingListDBID",       "Int"),
                ("share",                 "Int"),
                ("isActive",              "Int"))

  translation = {"isActive":  "CfgFlag"} 
#==================================================================================    
class CfgCampaignGroupInfo(CfgStruct, CfgObject):
  """ CfgCampaignGroupInfo object
  Fields:
    groupDBID         -     Int
    groupType         -     Int
    description       -     Char
    dialerDBID        -     Int
    statServerDBID    -     Int
    isActive          -     Int
    dialMode          -     Int
    origDNDBID        -     Int
    numOfChannels     -     Int
    operationMode     -     Int
    minRecBuffSize    -     Int
    optRecBuffSize    -     Int
    optMethod         -     Int
    optMethodValue    -     Int
    scriptDBID        -     Int
    trunkGroupDNDBID  -     Int
  """
  fields =     (("groupDBID",             "Int"),
                ("groupType",             "Int"),
                ("description",           "Char"),
                ("dialerDBID",            "Int"),
                ("statServerDBID",        "Int"),
                ("isActive",              "Int"),
                ("dialMode",              "Int"),
                ("origDNDBID",            "Int"),
                ("numOfChannels",         "Int"),
                ("operationMode",         "Int"),
                ("minRecBuffSize",        "Int"),
                ("optRecBuffSize",        "Int"),
                ("optMethod",             "Int"),     
                ("optMethodValue",        "Int"),
                ("scriptDBID",            "Int"),
                ("trunkGroupDNDBID",      "Int"))

  

  translation = {"groupType":  "CfgObjectType", "isActive": "CfgFlag",
                 "dialMode": "CfgDialMode", "operationMode": "CfgOperationMode",
                 "optMethod": "CfgOptimizationMethod"}   
#==================================================================================    
class CfgDNAccessNumber(CfgStruct, CfgObject):
  """ CfgDNAccessNumber object
  Fields:
    switchDBID    -   Int
    number        -   Char
  """
  fields =     (("switchDBID",            "Int"),
                ("number",                "Char"))
#==================================================================================    
class CfgPhones(CfgStruct, CfgObject):
  """ CfgPhones object
  Fields:
    office          -       Char
    home            -       Char
    mobile          -       Char
    pager           -       Char
    fax             -       Char
    modem           -       Char
    phonesComment   -       Char
  """
  fields =     (("office",                "Char"),
                ("home",                  "Char"),
                ("mobile",                "Char"),
                ("pager",                 "Char"),
                ("fax",                   "Char"),
                ("modem",                 "Char"),
                ("phonesComment",         "Char"))                
#==================================================================================    
class CfgAppRank(CfgStruct, CfgObject):
  """ CfgAppRank object
  Fields:
    appType         -       Int
    appRank         -       Int
  """
  fields =     (("appType",               "Int"),
                ("appRank",               "Int"))
  translation = {"appType":  "CfgAppType","appRank":  "CfgRank" }     

CfgPersonRank = CfgAppRank
#==================================================================================    
class CfgAgentInfo(CfgStruct, CfgObject):
  """ CfgAgentInfo object
  Fields:
    placeDBID         -       Int
    skillLevels       -       ListOfStructs_CfgSkillLevel
    agentLogins       -       ListOfStructs_CfgAgentLoginInfo
    capacityRuleDBID  -       Int
    siteDBID          -       Int
    contractDBID      -       Int
  """
  fields =     (("placeDBID",             "Int"),
                ("skillLevels",           "ListOfStructs_CfgSkillLevel"),
                ("agentLogins",           "ListOfStructs_CfgAgentLoginInfo"),
                ("capacityRuleDBID",      "Int"),
                ("siteDBID",              "Int"),
                ("contractDBID",          "Int"))
#==================================================================================    
class CfgSkillLevel(CfgStruct, CfgObject):
  """ CfgSkillLevel object
  Fields:
    skillDBID       -       Int
    level           -       Int
  """
  fields =     (("skillDBID",             "Int"),
                ("level",                 "Int"))
#==================================================================================    
class CfgAgentLoginInfo(CfgStruct, CfgObject):
  """ CfgAgentLoginInfo object
  Fields:
    agentLoginDBID  -       Int
    wrapupTime      -       Int
  """
  fields =     (("agentLoginDBID",        "Int"),
                ("wrapupTime",            "Int"))
#==================================================================================    
class CfgGroup(CfgStruct, CfgObject):
  """ CfgGroup object
  Fields:
    DBID                 -  Int
    tenantDBID           -  Int
    name                 -  Char
    managerDBIDs         -  DBIDList
    routeDNDBIDs         -  DBIDList
    capacityTableDBID    -  Int
    quotaTableDBID       -  Int
    state                -  Int
    userProperties       -  KVList
    capacityRuleDBID     -  Int
    siteDBID             -  Int
    contractDBID         -  Int
  """
  fields =     (("DBID",                  "Int"),
                ("tenantDBID",            "Int"),
                ("name",                  "Char"),
                ("managerDBIDs",          "DBIDList"),
                ("routeDNDBIDs",          "DBIDList"),
                ("capacityTableDBID",     "Int"),
                ("quotaTableDBID",        "Int"),
                ("state",                 "Int"),
                ("userProperties",        "KVList"),
                ("capacityRuleDBID",      "Int"),
                ("siteDBID",              "Int"),
                ("contractDBID",          "Int"))

                
  requiredFields = ["tenantDBID", "name"]  
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.state = CfgObjectState.CFGEnabled.val
#==================================================================================    
class CfgAppServicePermission(CfgStruct, CfgObject):
  """ CfgAppServicePermission object
  Fields:
    appType           -     Int
    permissionMask    -     Int
  """
  fields =     (("appType",        "Int"),
                ("permissionMask",        "Int"))
  translation = {"appType":  "CfgAppType"} 
#==================================================================================    
class CfgSolutionComponentDefinition(CfgStruct, CfgObject):
  """ CfgSolutionComponentDefinition object
  Fields:
    startupPriority   -     Int
    isOptional        -     Int
    appType           -     Int
    appVersion        -     Char
  """
  fields =     (("startupPriority",       "Int"),
                ("isOptional",            "Int"),
                ("appType",               "Int"),
                ("appVersion",            "Char"))
  toXmlTranslation = {"appType": "type", "appVersion": "version"}
  fromXmlTranslation = {"type": "appType", "version": "appVersion"}
  
  translation = {"appType":  "CfgAppType", "isOptional":  "CfgFlag"} 
#==================================================================================    
class CfgSolutionComponent(CfgStruct, CfgObject):
  """ CfgSolutionComponent object
  Fields:
    startupPriority   -     Int
    isOptional        -     Int
    appDBID           -     Int
  """
  fields =     (("startupPriority",       "Int"),
                ("isOptional",            "Int"),
                ("appDBID",               "Int"))
  translation = {"isOptional":  "CfgFlag"}
  
  
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.isOptional = CfgFlag.False.val
    self.startupPriority = 1
#==================================================================================    
class CfgStatInterval(CfgStruct, CfgObject):
  """ CfgStatInterval object
  Fields:
    intervalCount     -       Int
    statValue1        -       Int
    statValue2        -       Int
    statValue3        -       Int
    statValue4        -       Int
  """
  fields =     (("intervalCount",           "Int"),
                ("statValue1",              "Int"),
                ("statValue2",              "Int"),
                ("statValue3",              "Int"),
                ("statValue4",              "Int"))  
#==================================================================================    
class CfgServiceInfo(CfgStruct, CfgObject):
  """ CfgServiceInfo
  Fields:
    serviceDBID       -       Int
    isChargeable      -       Int
  """
  fields =     (("serviceDBID",             "Int"),
                ("isChargeable",            "Int"))
  translation = {"isChargeable":  "CfgFlag"} 

#==================================================================================    
class CfgSubcode(CfgStruct, CfgObject):
  """ CfgSubcode object
  Fields:
    name              -       Char
    code              -       Char
  """
  fields = (("name",      "Char"),
            ("code",      "Char")) 

#==================================================================================    
class CfgDNInfo(CfgStruct, CfgObject):
  """ CfgDNInfo object
  Fields:
    DNDBID            -       Int
    trunks            -       Int
  """
  fields =     (("DNDBID",             "Int"),
                ("trunks",            "Int"))
#==================================================================================    
class CfgID(CfgStruct, CfgObject):
  """ CfgID object
  Fields:
    CSID            -       Int
    DBID            -       Int
    type            -       Int
  """
  fields = (("CSID",            "Int"),
            ("DBID",            "Int"),
            ("type",            "Int"))
  translation = {"type":  "CfgObjectType"} 
  requiredFields = ["DBID", "type"]
  if InTrue(GetOption("Java")) or InTrue(GetOption("DotNet")):
    title = "CfgID"  
  def __repr__(self):
    if self.DBID > 0:
      obj = self.cfgServer.GetObjectByTypeAndDBID(ValToEnumElem(CfgObjectType, self.type), self.DBID)
      return obj.shortRepr(shift = 6)
    else:
      return CfgObject.shortRepr(self, shift = 6)
    
  def identical(self, other):
    if self.CSID == other.CSID and self.DBID == other.DBID and self.type == other.type:
      return 1
    return 0

CfgOwnerID = CfgID   
CfgParentID = CfgID
CfgACLID = CfgID
CfgACEID = CfgID
CfgObjectID = CfgID

#==================================================================================    
class CfgACE(CfgStruct, CfgObject):
  """ CfgACE object
  Fields:
    ID              -   Struct_CfgACEID
    accessMask      -   Int
  """
  fields = (("ID",              "Struct_CfgACEID"),
            ("accessMask",      "Int")) 
            
  toXmlTranslation = {"ID": "CfgACEID"}                 
  fromXmlTranslation = {"CfgACEID": "ID"}  
  
  requiredFields = ["ID"]   
  def __repr__(self):
    st = repr(self.ID)
    st = st + ' '*6 + repr(AccessMask(self.accessMask))
    return st
    
  def GetAccessMask(self):
    return AccessMask(self.accessMask)
    
  def SetAccessMask(self, accessMask):
    self.accessMask = accessMask.ToIntMask()
   

#==================================================================================    
            
class CfgACL(CfgStruct, CfgObject):
  """ CfgACL object
  Fields:
    objectID        - Struct_CfgACLID
    count           - Int
    ACEs            - ArrayOfStructs_CfgACE
  """
  fields = (("objectID",         "Struct_CfgACLID"),
            ("count",           "Int"),
            ("ACEs",            "ArrayOfStructs_CfgACE")) 
            
  toXmlTranslation = {"objectID": "CfgACLID"}                 
  fromXmlTranslation = {"CfgACLID": "objectID"}  
  
  title = "CfgACL"  
  def GetACEByObjectID(self, objectID):
    if not self.ACEs: return None
    for ace in self.ACEs:
      if ace.ID == objectID:
        return ace

    
  
class AccessMask:
  N = 0
  P = 0
  E = 0
  D = 0
  X = 0
  H = 0
  C = 0
  R = 0
  liters = ('N','P', 'E', 'D', 'X', 'H', 'C', 'R')
  def __init__(self, value = 0):
    if type(value) == type(0):
      if value < 0 or value > 255:
        ProgrammError("Incorrect value for access mask, must be >=0 and <255")
      self.N = value&128
      self.P = value&64
      self.E = value&32
      self.D = value&16
      self.X = value&8  
      self.H = value&4
      self.C = value&2
      self.R = value&1     
    elif type(value) in (type(""), type(u'')) :
      self.Set(value)
    else:
      ProgrammError("Value must be integer or string")   
  
  def Set(self, permissions):
    self.ResetAll()
    for liter in permissions:
      if liter.upper() not in self.liters: ProgrammError("No such permission %s in access mask; use %s" %(liter, self.liters))
      setattr(self, liter.upper(), 1) 
  
  def SetTo1(self, liter):
    if liter.upper() not in self.liters: ProgrammError("No such permission %s in access mask; use %s" %(liter, self.liters))
    setattr(self, liter.upper(), 1) 
    
  def ResetTo0(self, liter):
    if liter.upper() not in self.liters: ProgrammError("No such permission %s in access mask; use %s" %(liter, self.liters))
    setattr(self, liter.upper(), 0)     
  
  def ResetAll(self):
    for liter in self.liters:
      setattr(self, liter, 0)
   
  def SetAll(self):
    for liter in self.liters:
      setattr(self, liter, 1)

  def ToIntMask(self) :
    intVal = 0
    intVal = intVal|(self.N<<7)|(self.P<<6)|(self.E<<5)|(self.D<<4)|(self.X<<3)|(self.H<<2)|(self.C<<1)|(self.R)
    return intVal

  def __str__(self):
    st = ""
    for liter in self.liters:
      if getattr(self, liter):
        st = st + liter
    return st
  
  def __repr__(self):
    st = "%-20s = " %"AccessMask"
    m = 0
    for liter in self.liters:
      if getattr(self, liter):
        st = st + " " + liter
        m = 1
    if not m: st = st + "00000000"
    st = st + "\n"
    return st

#==================================================================================  
class CfgObjectResource(CfgStruct, CfgObject):
  """ CfgObjectResource object
  Fields:
    resourceType        -     Int
    objectDBID          -     Int
    objectType          -     Int
    description         -     Char
    charField1          -     Char
    charField2          -     Char
    charField3          -     Char
    charField4          -     Char
    longField1          -     Int
    longField2          -     Int
    longField3          -     Int
    longField4          -     Int
  """
  fields =     (("resourceType",            "Int"),
                ("objectDBID",              "Int"),
                ("objectType",              "Int"),
                ("description",             "Char"),
                ("charField1",              "Char"),
                ("charField2",              "Char"),
                ("charField3",              "Char"),   
                ("charField4",              "Char"),
                ("longField1",              "Int"),
                ("longField2",              "Int"),   
                ("longField3",              "Int"),
                ("longField4",              "Int"))  

#==================================================================================

class CfgPortInfo(CfgStruct, CfgObject):
  """ CfgPortInfo object
  Fields:
    id                -       Char
    port              -       Char
    transportParams   -       Char
    connProtocol      -       Char
    appParams         -       Char
    description       -       Char
    charField1        -       Char
    charField2        -       Char
    charField3        -       Char
    charField4        -       Char
    longField         -       Int
    longField2        -       Int
    longField3        -       Int
    longField4        -       Int
  """
  fields =     (("id",                      "Char"),
                ("port",                    "Char"),
                ("transportParams",         "Char"),
                ("connProtocol",            "Char"),
                ("appParams",               "Char"),
                ("description",             "Char"),
                ("charField1",              "Char"),
                ("charField2",              "Char"),
                ("charField3",              "Char"),   
                ("charField4",              "Char"),
                ("longField1",              "Int"),
                ("longField2",              "Int"),   
                ("longField3",              "Int"),
                ("longField4",              "Int"))  
#==================================================================================

class CfgObjectiveTableRecord(CfgStruct, CfgObject):
  """ CfgObjectiveTableRecord object
  Fields:
    mediaTypeDBID        -       Int
    serviceTypeDBID      -       Int
    customerSegmentDBID  -       Int
    objectiveThreshold   -       Int
    objectiveDelta       -       Int
    contractDBID         -       Int
  """
  fields =     (("mediaTypeDBID",           "Int"),
                ("serviceTypeDBID",         "Int"),
                ("customerSegmentDBID",     "Int"),
                ("objectiveThreshold",      "Int"),
                ("objectiveDelta",          "Int"),
                ("contractDBID",            "Int"))
#==================================================================================
class CfgRoleMember(CfgStruct, CfgObject):
  """ CfgRoleMember object
  Fields:
    objectDBID          -       Int
    objectType          -       Int
  """
  fields =     (("objectDBID",           "Int"),
               ("objectType",         "Int"))


#==================================================================================


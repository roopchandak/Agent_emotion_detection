#
#                  === CfgSwitch model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *
#==================================================================================
        
class CfgSwitch(CfgObject):
  """ CfgSwitch object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    physSwitchDBID        - Int
    type                  - Int
    name                  - Char
    TServerDBID           - Int
    linkType              - Int
    switchAccessCodes     - ListOfStructs_CfgSwitchAccessCode
    DNRange               - Char
    state                 - Int
    userProperties        - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("physSwitchDBID",      "Int"),
                 ("type",                "Int"),
                 ("name",                "Char"),
                 ("TServerDBID",         "Int"),
                 ("linkType",            "Int"),
                 ("switchAccessCodes",   "ListOfStructs_CfgSwitchAccessCode"),
                 ("DNRange",             "Char"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "physSwitchDBID", "name"]

  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGSwitch
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      cfgTenant = cfgServer.GetObjectByTypeAndName(CfgObjectType.CFGTenant, tenant)
      tenantDBID = cfgTenant.DBID

      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgSwitch"

  def FindAccessCode(self, otherSwitch):
    """Find access code from this switch to other switch. Return first found access code, matched by switch DBID only
    parameters:
      otherSwitch - CfgSwitch object
    return        - CfgSwitchAccessCode object
    """
    accessCode = None
    if self.switchAccessCodes:
      for ac in self.switchAccessCodes:
        if ac.switchDBID == otherSwitch.DBID:
          accessCode = ac
          break
    return accessCode

  def ChangeRouteType(self, switch = None, routeType = CfgRouteType.CFGXRouteTypeDefault, matchTargetType = None):
    if switch:
      dbid = switch.DBID
    else:
      dbid = 0
    if type(routeType) != type(0):
      routeType = routeType.val 
    if matchTargetType and type(matchTargetType) != type(0):
      matchTargetType = matchTargetType.val
    self.BeginChange()
    if self.switchAccessCodes:
      for ac in self.switchAccessCodes:
        if ac.switchDBID == dbid: 
          if ac.routeType == routeType and (not matchTargetType or ac.targetType == matchTargetType): 
            Message("Switch " + self.name + " already has identical access code to switch " + switch.name)    
            return    
    if self.switchAccessCodes:
      for ac in self.switchAccessCodes:
        if ac.switchDBID == dbid:
          if not matchTargetType or ac.targetType == matchTargetType: 
            ac.routeType = routeType
            self.EndChange()    
            return
    if matchTargetType:
      ProgrammWarning("Switch %s does not have access code to switch %s with specified target type" %(self.name, switch.name))
    else:
      ProgrammWarning("Switch %s does not have access code to switch %s" %(self.name, switch.name))
    
    
    
    
    
  def ChangeAccessCode(self, switch = None, accessCode = None, routeType = None, targetType = None,
                      dnSource = None, destinationSource = None, locationSource = None,
                   dnisSource = None, reasonSource = None, extensionSource = None, matchBy = None):  #how to dial from this switch (self) to the switch in args
    """if arg is not specified (None) it is not changed;
    if no ac to specified switch exist, it is added"""
    if switch:
      dbid = switch.DBID
    else:
      dbid = 0
    if matchBy == "accessCode" and accessCode == None:
      ProgrammError("accessCode must be specified if matchBy = accessCode")
    if matchBy == "accessCodeAndRouteType" and (accessCode == None or routeType == None):
      ProgrammError("accessCode and routeType must be specified if matchBy = accessCodeAndRouteType")  
    if matchBy == "routeTypeAndTargetType" and (targetType == None or routeType == None):
      ProgrammError("targetType and routeType must be specified if matchBy = routeTypeAndTargetType")      
      
    if targetType <> None:
      if type(targetType) != type(0): #enum
        targetType = targetType.val
    if routeType <> None:    
      if type(routeType) != type(0):
        routeType = routeType.val  
    #if self.switchAccessCodes:
    #  for ac in self.switchAccessCodes:
    #    if ac.switchDBID == dbid: 
    #      if ac.targetType == targetType and ac.routeType == routeType and ac.accessCode == accessCode:
    #        Message("Switch " + self.name + " already has identical access code to switch " + switch.name)    
    #        return
    self.BeginChange()
    matchingAc = None
    if self.switchAccessCodes:
      for ac in self.switchAccessCodes:
        if ac.switchDBID == dbid: 
          
          if matchBy == None: #change the first switch
            matchingAc = ac
            break
          elif matchBy == "accessCode":
            if ac.accessCode == accessCode:
              matchingAc = ac
              break
          elif matchBy == "accessCodeAndRouteType":
            if ac.accessCode == accessCode and ac.routeType == routeType:
              matchingAc = ac
              break            
          elif matchBy == "routeTypeAndTargetType":
            if ac.routeType == routeType and ac.targetType == targetType:
              matchingAc = ac
              break  
      if matchingAc:
        if accessCode != None:
          matchingAc.accessCode = accessCode
        if targetType != None:
          matchingAc.targetType = targetType
        if routeType != None:
          matchingAc.routeType = routeType
        if dnSource != None:
          matchingAc.dnSource = dnSource
        if destinationSource != None:
          matchingAc.destinationSource = destinationSource
        if locationSource != None:
          matchingAc.locationSource = locationSource      
        if dnisSource != None:
          matchingAc.dnisSource = dnisSource        
        if reasonSource != None:
          matchingAc.reasonSource = reasonSource         
        if extensionSource != None:
          matchingAc.extensionSource = extensionSource                     
        self.EndChange()       
        return
    #does not have access code to specified switch with match
    if accessCode == None:
      accessCode = ""
    if routeType == None:
      routeType = CfgRouteType.CFGXRouteTypeDefault
    if targetType == None:
      targetType = CfgTargetType.CFGTargetISCC
    if dnSource == None:
      dnSource = ""
    if destinationSource == None:
      destinationSource = "" 
    if locationSource == None:
      locationSource = ""       
    if dnisSource == None:
      dnisSource = ""
    if reasonSource == None:
      reasonSource = "" 
    if extensionSource == None:
      extensionSource = ""         
    self.AddAccessCode(switch, accessCode, routeType, targetType, dnSource,
                      destinationSource, locationSource, dnisSource, reasonSource, extensionSource)
    
    
  def AddAccessCode(self, switch, accessCode = "", routeType = CfgRouteType.CFGXRouteTypeDefault, 
                   targetType = CfgTargetType.CFGTargetISCC, 
                   dnSource = "", destinationSource = "", locationSource = "",
                   dnisSource = "", reasonSource = "", extensionSource = ""):
    dbid = switch.DBID
    self.BeginChange()
    if not self.switchAccessCodes:
      self.switchAccessCodes = []
    if type(targetType) != type(0): #enum
      targetType = targetType.val
    if type(routeType) != type(0):
      routeType = routeType.val   
    for ac in self.switchAccessCodes:
      if ac.switchDBID == dbid: 
        if ac.targetType == targetType and ac.routeType == routeType and ac.accessCode == accessCode:
          Message("Switch " + self.name + " already has identical access code to switch " + switch.name)    
          return
    
    newAc = CfgSwitchAccessCode()
    newAc.switchDBID = dbid
    newAc.accessCode = accessCode
    newAc.targetType = targetType
    newAc.routeType = routeType
    newAc.dnSource = dnSource
    newAc.destinationSource = destinationSource
    newAc.locationSource = locationSource
    newAc.dnisSource = dnisSource
    newAc.reasonSource = reasonSource
    newAc.extensionSource = extensionSource
    
    
    self.switchAccessCodes.append(newAc)
    self.EndChange() 
    
  def DeleteAccessCode(self, switch):
    dbid = switch.DBID
    if self.switchAccessCodes:
      for ac in self.switchAccessCodes:
        if ac.switchDBID == dbid: 
          self.BeginChange()
          self.switchAccessCodes.remove(ac)
          self.EndChange()        
          return      
        
        
  def ChangeTserver(self, newTserver):
    oldSwitchDBID = ""
    if newTserver.flexibleProperties and newTserver.flexibleProperties.has_key('CONN_INFO'):
      conn_info = newTserver.flexibleProperties['CONN_INFO']
      if conn_info and conn_info.has_key("CFGSwitch"):
        switchDBIDs = conn_info["CFGSwitch"].keys()
        oldSwitchDBID = switchDBIDs[0]
    print "oldSwitchDBID", oldSwitchDBID
    if oldSwitchDBID:
      oldSwitchDBID = int(oldSwitchDBID)

      oldSwitch = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGSwitch, oldSwitchDBID)
      if oldSwitch:
        oldSwitch.BeginChange()
        print oldSwitch.TServerDBID
        print "remove tserver from its old switch"
        oldSwitch.TServerDBID = 0 #remove tserver from its old switch
        oldSwitch.EndChange()
      newTserver.BeginChange()
      newTserver.flexibleProperties = None
      newTserver.EndChange()
     
      
    newTserver.BeginChange()
    print "change tserver tenantDBID"
    newTserver.tenantDBIDs = [self.tenantDBID]
    #newTserver.flexibleProperties = {"CONN_INFO": {"CfgSwitch": {self.DBID: {}}}}
    newTserver.EndChange()
    self.BeginChange()
    print "change switch TServerDBID"
    self.TServerDBID = newTserver.DBID
    self.EndChange()
    
  def EnableOnlyDNs(self, dnNumberList):  
    """Enables only objects which belong to 'dnNumberList' list"""
    PrintLog("Enabling DNs for testing, disabling the rest")
    filtr = {"tenant_id" : self.tenantDBID, "switch_dbid": self.DBID}
    strObjList = self.cfgServer.GetObjectInfo(CfgObjectType.CFGDN, filtr) # get all DNs on this switch
    for strObj in strObjList:
      
      cfgDNName = self.cfgServer.GetObjectCharPropertyFromString(strObj, "number")
      cfgDNDBID = self.cfgServer.GetObjectDBIDFromString(strObj)

      if not cfgDNName in dnNumberList:
        PrintLog("  DN='%s' is NOT in the list - disable it"%cfgDNName)
        GetObjectByTypeAndDBID(CfgObejctType.CfgDN, cfgDNDBID).Disable()
        
      else:
        PrintLog("  DN='%s' is in the list - enable it"%cfgDNName)
        GetObjectByTypeAndDBID(CfgObejctType.CfgDN, cfgDNDBID).Enable()    
#==================================================================================
class CfgPhysicalSwitch(CfgObject):
  """ CfgPhysicalSwitch object
  Fields:
    DBID                  - Int
    name                  - Char
    type                  - Int
    address               - Struct_CfgAddress
    contactPersonDBID     - Int
    state                 - Int
    userProperties        - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("name",                "Char"),
                 ("type",                "Int"),
                 ("address",             "Struct_CfgAddress"),
                 ("contactPersonDBID",   "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
                 
  toXmlTranslation = {"address": "CfgAddress"}                 
  fromXmlTranslation = {"CfgAddress": "address"}
                 
  translation = All([CfgObject.translation,  {"type":        "CfgSwitchType"}])              
  requiredFields = ["name","type"]
  
  def __init__(self, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGPhysicalSwitch
    filter = {}
    if name:
      filter = {"name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgPhysicalSwitch"
 
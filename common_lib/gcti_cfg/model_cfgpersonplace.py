#
#                  === CfgPreson and CfgPlace model ===
#
#

from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *
#==================================================================================
class CfgPerson(CfgObject):
  """ CfgPerson object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    lastName            - Char
    firstName           - Char
    address             - Struct_CfgAddress
    phones              - Struct_CfgPhones
    birthdate           - Char
    comment             - Char
    employeeID          - Char
    userName            - Char
    password            - Char
    appRanks            - ListOfStructs_CfgAppRank
    isAgent             - Int
    agentInfo           - Struct_CfgAgentInfo
    isAdmin             - Int
    assignedTenantDBIDs - DBIDList
    state               - Int
    userProperties      - KVList
    emailAddress        - Char
    externalID          - Char
    isExternalAuth      - Int
    changePasswordOnNextLogin - Int
    passwordHashAlgorithm 	  - Int
    PasswordUpdatingDate  	  - Int    
  """
  fields =      (("DBID",                   "DBID"),
                 ("tenantDBID",             "Int"),
                 ("lastName",               "Char"),
                 ("firstName",              "Char"),
                 ("address",                "Struct_CfgAddress"),
                 ("phones",                 "Struct_CfgPhones"),
                 ("birthdate",              "Char"), 
                 ("comment",                "Char"),
                 ("employeeID",             "Char"),
                 ("userName",               "Char"),
                 ("password",               "Char"),
                 ("appRanks",               "ListOfStructs_CfgAppRank"),
                 ("isAgent",                "Int"),
                 ("agentInfo",              "Struct_CfgAgentInfo"),
                 ("isAdmin",                "Int"),
                 ("assignedTenantDBIDs",    "DBIDList"),
                 ("state",                  "Int"),
                 ("userProperties",         "KVList"),
                 ("emailAddress",           "Char"),
                 ("externalID",             "Char"),
                 ("isExternalAuth",         "Int"),
                 ("changePasswordOnNextLogin", "Int"), #to be added when rebuilt with newer cfglib
                 ("passwordHashAlgorithm",  "Int"),
                 ("PasswordUpdatingDate",   "Int"))                 
              
  toXmlTranslation = {"address": "CfgAddress", "phones": "CfgPhones", "agentInfo": "CfgAgentInfo"}                 
  fromXmlTranslation = {"CfgAddress": "address", "CfgPhones": "phones", "CfgAgentInfo": "agentInfo"}  
                
  translation = All([CfgObject.translation,  {"isAgent": "CfgFlag", "isAdmin": "CfgFlag", "isExternalAuth": "CfgFlag"}])
  requiredFields = ["employeeID", "userName", "tenantDBID"]
  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGPerson
    filter = {}
    if tenant and name:
      cfgTenant = cfgServer.GetObjectByTypeAndName(CfgObjectType.CFGTenant, tenant)
      tenantDBID = cfgTenant.DBID
      #filter = {"name" : tenant}
      #tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgPerson"

    
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.isAgent = CfgFlag.True.val
    self.isAdmin = CfgFlag.False.val
  
  def AddSkill(self, cfgSkill, skillLevel, noEvents = 0):
    """Add skill with specified skill level to person's skill list"""
    if not self.agentInfo:
      agentInfo = CfgAgentInfo()
    else:
      agentInfo = self.agentInfo
    #for compatibility. should be alsways cfgskill, but used to be dbid in argument
    if type(cfgSkill) <> type(0):
      cfgSkillDBID = cfgSkill.DBID
    else:
      cfgSkillDBID = cfgSkill       
    skillLevels = agentInfo.skillLevels
    if skillLevels:
      for skill in skillLevels:
        if skill.skillDBID == cfgSkillDBID:
          Message("Person %s already has skill DBID %s, skill cannot be added" %(self.userName, cfgSkillDBID))
          return
    
    self.BeginChange()
    if skillLevels == None: skillLevels = []
    newSkill = CfgSkillLevel()
    newSkill.SetAttributes({"skillDBID": cfgSkillDBID, "level": skillLevel})
    skillLevels.append(newSkill)
    agentInfo.skillLevels = skillLevels
    self.agentInfo = agentInfo
    reqID = self.EndChange(noEvents = noEvents)
    return reqID, time.time()

  def ChangeSkill(self, cfgSkill, skillLevel, noEvents = 0):
    """Change skill level"""
    if not self.agentInfo:
      agentInfo = CfgAgentInfo()
    else:
      agentInfo = self.agentInfo
    cfgSkillDBID = cfgSkill.DBID
    skillLevels = agentInfo.skillLevels
    if skillLevels == None: skillLevels = []
    reqID = 0
    for skill in skillLevels:
      if skill.skillDBID == cfgSkillDBID:
        self.BeginChange()
        skill.level = skillLevel
        self.agentInfo = agentInfo
        reqID = self.EndChange(noEvents = noEvents)    
        return reqID, time.time()
    return self.AddSkill(cfgSkill, skillLevel, noEvents)


  def DeleteSkill(self, cfgSkill, noEvents = 0):
    """Delete skill from person's skill list"""
    cfgSkillDBID = cfgSkill.DBID
    if not self.agentInfo or not self.agentInfo.skillLevels:
      Message("Person %s does not have skill %s, skill cannot be removed" %(self.userName, cfgSkill.name))
      return
    found = 0
    self.BeginChange()
    reqID = 0
    for skill in self.agentInfo.skillLevels:
      if skill.skillDBID == cfgSkillDBID:
        found = 1
        self.agentInfo.skillLevels.remove(skill)
        reqID = self.EndChange(noEvents = noEvents)
        
        break
    if not found:
      Message("Person %s does not have skill %s, skill cannot be removed" %(self.userName, cfgSkill.name))
    return reqID, time.time()

  def RemoveSkill(self, cfgSkillDBID, noEvents = 0): #for compatibilty
    return self.DeleteSkill(cfgSkill, noEvents)

      
  def __setAgentInfoSimpleProp(self, propName, cfgObj):
    if cfgObj == None:
      cfgObjDBID = 0
    else:
      cfgObjDBID = cfgObj.DBID
    if not self.agentInfo:
      agentInfo = CfgAgentInfo()
    else:
      agentInfo = self.agentInfo
    self.BeginChange()
    setattr(agentInfo, propName, cfgObjDBID)
    self.agentInfo = agentInfo
    self.EndChange()
  
  def SetDefaultPlace(self, cfgPlace):
    """Set persons's default place"""
    self.__setAgentInfoSimpleProp("placeDBID", cfgPlace)

  def SetCapacityRule(self, cfgScript):
    """Set persons's capacity rule property"""
    self.__setAgentInfoSimpleProp("capacityRuleDBID", cfgScript)

  def SetCostContract(self, cfgScript):
    """Set persons's cost contract property"""
    self.__setAgentInfoSimpleProp("contractDBID", cfgScript)
    
  def SetSite(self, cfgFolder):
    """Set persons's site property"""
    self.__setAgentInfoSimpleProp("siteDBID", cfgFolder)


  def AddAgentLogin(self, cfgAgentLogin, wrapupTime = 0):
    """Add agent login with specified wrap up time"""
    if not self.agentInfo:
      agentInfo = CfgAgentInfo()
    else:
      agentInfo = self.agentInfo
    cfgAgentLoginDBID = cfgAgentLogin.DBID
    agentLogins = agentInfo.agentLogins
    if agentLogins:
      for agentLogin in agentLogins:
        if agentLogin.agentLoginDBID == cfgAgentLoginDBID:
          Message("Person %s already has agentLogin DBID %s, agentLogin cannot be added" %(self.userName, cfgAgentLoginDBID))
          return
    
    self.BeginChange()
    if agentLogins == None: agentLogins = []
    newAgentLogin = CfgAgentLoginInfo()
    newAgentLogin.SetAttributes({"agentLoginDBID": cfgAgentLoginDBID, "wrapupTime": wrapupTime})
    agentLogins.append(newAgentLogin)
    agentInfo.agentLogins = agentLogins
    self.agentInfo = agentInfo
    self.EndChange()    


  def ChangeAgentLogin(self, cfgAgentLogin, wrapupTime):
    """Change agent login  wrap up time"""
    if not self.agentInfo:
      agentInfo = CfgAgentInfo()
    else:
      agentInfo = self.agentInfo
    cfgAgentLoginDBID = cfgAgentLogin.DBID
    agentLogins = agentInfo.agentLogins
    if agentLogins == None: agentLogins = []
    for agentLogin in agentLogins:
      if agentLogin.agentLoginDBID == cfgAgentLoginDBID:
        self.BeginChange()
        agentLogin.wrapupTime = wrapupTime
        self.agentInfo = agentInfo
        self.EndChange()    
        return
    return self.AddAgentLogin(cfgAgentLogin, wrapupTime)
  

  def DeleteAgentLogin(self, cfgAgentLogin):
    """Delete agetn login from person's login list"""
    cfgAgentLoginDBID = cfgAgentLogin.DBID
    if not self.agentInfo or not self.agentInfo.agentLogins:
      Message("Person %s does not have agent login %s, login cannot be removed" %(self.userName, cfgAgentLogin.name))
      return
    found = 0
    self.BeginChange()
    for agentLogin in self.agentInfo.agentLogins:
      if agentLogin.agentLoginDBID == cfgAgentLoginDBID:
        self.agentInfo.agentLogins.remove(agentLogin)
        self.EndChange()      
        found = 1
        break
    if not found:
      Message("Person %s does not have agent login %s, login cannot be removed" %(self.userName, cfgAgentLogin.name))
      return
    
  def GetDefaultDNs(self):
    """Returns a list of CfgDNs for default place, or empty list"""
    CfgDNs = []
    if self.agentInfo and self.agentInfo.placeDBID:
      cfgPlace = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGPlace, self.agentInfo.placeDBID)
      for DNDBID in cfgPlace.DNDBIDs:
        cfgDN = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGDN, cfgPlace.DNDBIDs[0])
        CfgDNs.append(cfgDN)
    return CfgDNs
    
#==================================================================================


class CfgPlace(CfgObject):
  """ CfgPlace object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    name                - Char
    DNDBIDs             - DBIDList
    state               - Int
    userProperties      - KVList
    capacityRuleDBID    - Int
    siteDBID            - Int
    contractDBID        - Int
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("DNDBIDs",             "DBIDList"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("capacityRuleDBID",    "Int"),
                 ("siteDBID",            "Int"),
                 ("contractDBID",        "Int"))                 
                 
  requiredFields = ["name",  "tenantDBID"] 
  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGPlace
    filter = {}
    if tenant and name:
      cfgTenant = cfgServer.GetObjectByTypeAndName(CfgObjectType.CFGTenant, tenant)
      tenantDBID = cfgTenant.DBID
      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)

    self.title = "CfgPlace"    


  def AddDN(self, cfgDN):
    """Add DN shortcut to place"""
    self.printLog("Place %s: adding shortcut to DN %s" %(self.name, cfgDN.number))
    self.AddDBIDToDBIDList("DNDBIDs", cfgDN.DBID)
    
  
  def DeleteDN(self, cfgDN):
    """Delete DN shortcut from place"""
    self.printLog("Place %s: deleting shortcut to DN %s" %(self.name, cfgDN.number))
    self.DeleteDBIDFromDBIDList("DNDBIDs", cfgDN.DBID)
    
#==================================================================================
class CfgAgentLogin(CfgObject):
  """ CfgAgentLogin object
  Fields:
    DBID                - Int
    switchDBID          - Int
    tenantDBID          - Int
    loginCode           - Char
    state               - Int
    userProperties      - KVList
    override            - Char
    useOverride         - Int
    switchSpecificType  - Int
    password            - Char
  """
  fields =      (("DBID",                "DBID"),
                 ("switchDBID",          "Int"),
                 ("tenantDBID",          "Int"),
                 ("loginCode",           "Char"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("override",            "Char"),
                 ("useOverride",         "Int"),
                 ("switchSpecificType",  "Int"),
                 ("password",            "Char"))
                 
  translation = All([CfgObject.translation,  {"useOverride": "CfgFlag"}])
  
  requiredFields = ["loginCode", "switchDBID", "tenantDBID"]
  
  def __init__(self, tenant = None, switch = None, loginCode = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGAgentLogin
    filter = {}
    if tenant and switch and loginCode:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : switch}

      switchDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGSwitch, filter)

      self.switchDBID = switchDBID 
      filter = {"login_code" : loginCode, "switch_dbid": self.switchDBID }

    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)

    self.title = "CfgAgentLogin" 

  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.useOverride = CfgFlag.True.val
    self.switchSpecificType = 1

#==================================================================================
class CfgSkill(CfgObject):
  """ CfgSkill object
  Fields:
    DBID                - Int
    name                - Char
    tenantDBID          - Int
    state               - Int
    userProperties      - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("name",                "Char"),
                 ("tenantDBID",          "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
                 
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGSkill
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      
      cfgTenant = cfgServer.GetObjectByTypeAndName(CfgObjectType.CFGTenant, tenant)
      tenantDBID = cfgTenant.DBID

      filter = {"tenant_dbid": tenantDBID, "name" : name}

    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)

    self.title = "CfgSkill"  

#==================================================================================
class CfgActionCode(CfgObject):
  """ CfgActionCode object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    name                - Char
    type                - Int
    code                - Char
    subcodes            - ListOfStructs_CfgSubcode
    state               - Int
    userProperties      - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("type",                "Int"),
                 ("code",                "Char"),
                 ("subcodes",            "ListOfStructs_CfgSubcode"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "name", "type", "code"]  
  translation = All([CfgObject.translation,  {"type": "CfgActionCodeType"}])
  
  def __init__(self, tenant = None, name = None, code = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGActionCode
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      if name:
        filter = {"tenant_dbid": tenantDBID, "name" : name}
      elif code:
        filter = {"tenant_dbid": tenantDBID, "code" : code}
      elif name and code:
        filter = {"tenant_dbid": tenantDBID, "code" : code, "name" : name}

    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)

    self.title = "CfgActionCode"  

  def AddSubcode(self, subcodeName, code):
    if self.subcodes:
      for subcode in self.subcodes:
        if subcode.name == subcodeName:
          Message("Subcode %s already in %s" % (subcode.name, self.name))  
          return
    self.printLog("ActionCode %s: adding subcode %s" %(self.name, subcodeName))
    self.BeginChange()
    if not self.subcodes: self.subcodes = []
    subcode = CfgSubcode()
    subcode.name = subcodeName
    subcode.code = code
    self.subcodes.append(subcode)
    self.EndChange()
    
  def DeleteSubcode(self, subcodeName):
    subcodeToDelete = None
    if self.subcodes:
      for subcode in self.subcodes:
        if subcode.name == subcodeName:
          subcodeToDelete = subcode
          break
    if not subcodeToDelete:    
      Message("Subcode %s is not in %s" % (subcodeName, self.name)) 
      return
    self.printLog("ActionCode %s: deleting subcode %s" %(self.name, subcodeName))
    self.BeginChange()
    self.subcodes.remove(subcodeToDelete)
    self.EndChange()


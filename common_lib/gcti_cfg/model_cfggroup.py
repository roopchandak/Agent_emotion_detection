#
#                  === CfgGroup model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *
#==================================================================================

class BaseCfgGroup:
  
  def AddRouteDN(self, cfgRouteDN):
    """ Adds route DN DBID to CfgGroup object
    Parameters:
      cfgRouteDN  -     CfgDN object
    """
    if self.groupInfo.routeDNDBIDs and cfgRouteDN.DBID in self.groupInfo.routeDNDBIDs:
      Message("Route DN %s already belongs to the group %s" % (cfgRouteDN.number, self.groupInfo.name))  
      return
    self.printLog("Group %s: adding shortcut to RouteDN %s" %(self.groupInfo.name, cfgRouteDN.number))
  
    self.BeginChange()
    if not self.groupInfo.routeDNDBIDs: self.groupInfo.routeDNDBIDs = []
    self.groupInfo.routeDNDBIDs.append(cfgRouteDN.DBID)
    self.EndChange()
  
  def DeleteRouteDN(self, cfgRouteDN):
    """ Deletes route DN DBID from CfgGroup object
    Parameters:
      cfgRouteDN  -     CfgDN object
    """
    if not self.groupInfo.routeDNDBIDs or not (cfgRouteDN.DBID in self.groupInfo.routeDNDBIDs):
      Message("Route DN %s does not belong to the group %s" % (cfgRouteDN.number, self.groupInfo.name)) 
      return
    self.printLog("Group %s: deleting shortcut to place %s" %(self.groupInfo.name, cfgRouteDN.number))
    self.BeginChange()
    self.groupInfo.routeDNDBIDs.remove(cfgRouteDN.DBID)
    self.EndChange()
  
  def AddOption(self, section, key, value, annex = 1): 
    """ Adds option to the CfgGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    return 1 - success, desired option is set to desired value, 0 - option not changed
    """
    options = copy.deepcopy(self.groupInfo.userProperties)
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
      self.groupInfo.userProperties = copy.copy(options)
      return self.EndChange()
    else:
      self.printLog("%s option %s in section %s, annex = %s is already set to %s" %(nm,  key, section, annex, value))
    return 1 # no change needed

  def ChangeOption(self, section, key, value, annex = 1): 
    """ Changes option in CfgGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    """
    return self.AddOption(section, key, value, annex)
 
 
  def DeleteOption(self, section, key, annex = 1):  
    """ Deletes option from CfgGroup object
    Parameters:
      section     -   char
      key         -   char
      annex       -   int
    section could be None, in this case first found option with key = key is deleted
    """
    self.BeginChange()
    options = self.groupInfo.userProperties
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
          self.groupInfo.userProperties = options
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
          self.groupInfo.userProperties = options
          return self.EndChange()


    self.printLog(" Option " + str(oldKey) + " is not found")
    return 1
    
  def DeleteSection(self, section, annex = 1):
    """ Deletes section from CfgGroup object
    Parameters:
      section     -   char
      annex       -   int
    """
    self.BeginChange()
    options = self.groupInfo.userProperties
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
      self.groupInfo.userProperties = options
      return self.EndChange()
    else:
      self.printLog(" Section " + str(oldSection) + " is not found")
      return 1
    
class CfgPlaceGroup(CfgObject, BaseCfgGroup):
  """ CfgPlaceGroup object
  Fields:
    groupInfo           -  Struct_CfgGroup
    placeDBIDs          -  DBIDList
  """
  fields =      (("groupInfo",           "Struct_CfgGroup"),
                 ("placeDBIDs",          "DBIDList"))
                 
  toXmlTranslation = {"groupInfo": "CfgGroup"}                 
  fromXmlTranslation = {"CfgGroup": "groupInfo"}  
                 

  requiredFields = ["groupInfo"]  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGPlaceGroup
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
     
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID
    self.title = "CfgPlaceGroup"
  
  def fromStringToPythObject(self, strObj):
    CfgObject.fromStringToPythObject(self, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID
  
    
  def AddPlace(self, place):
    """ Adds place DBID to the CfgPlaceGroup object
    Parameters:
      place     -   CfgPlace object
    """
    self.printLog("Place Group %s: adding shortcut to place %s" %(self.groupInfo.name, place.name))
    self.AddDBIDToDBIDList("placeDBIDs", place.DBID)
    
  def DeletePlace(self, place):
    """ Deletes place DBID from CfgPlaceGroup object
    Parameters:
      place     -   CfgPlace object
    """
    self.printLog("Place Group %s: deleting shortcut to place %s" %(self.groupInfo.name, place.name))
    self.DeleteDBIDFromDBIDList("placeDBIDs", place.DBID)
    
  def AddOption(self, section, key, value, annex = 1):
    """ Adds option to the CfgPlaceGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    return 1 - success, desired option is set to desired value, 0 - option not changed
    """
    return BaseCfgGroup.AddOption(self, section, key, value, annex)
    
  def ChangeOption(self, section, key, value, annex = 1): 
    """ Changes option in CfgPlaceGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    """
    return BaseCfgGroup.ChangeOption(self, section, key, value, annex)

  def DeleteOption(self, section, key, annex = 1):
    """ Deletes option from CfgPlaceGroup object
    Parameters:
      section     -   char
      key         -   char
      annex       -   int
    section could be None, in this case first found option with key = key is deleted
    """
    return BaseCfgGroup.DeleteOption(self, section, key, annex)
    
  def DeleteSection(self, section, annex = 1):
    """ Deletes section from CfgPlaceGroup object
    Parameters:
      section     -   char
      annex       -   int
    """
    return BaseCfgGroup.DeleteSection(self, section, annex)      
    
class CfgAgentGroup(CfgObject, BaseCfgGroup):
  """ CfgAgentGroup object
  Fields:
    groupInfo           -  Struct_CfgGroup
    agentDBIDs          -  DBIDList
  """
  fields =      (("groupInfo",           "Struct_CfgGroup"),
                 ("agentDBIDs",          "DBIDList"))
                 
  toXmlTranslation = {"groupInfo": "CfgGroup"}                 
  fromXmlTranslation = {"CfgGroup": "groupInfo"}  
  
  requiredFields = ["groupInfo"]  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGAgentGroup
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
     
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.DBID = 0
    if self.exists:
      if self.groupInfo:
        self.DBID = self.groupInfo.DBID
    self.title = "CfgAgentGroup"    

  def fromStringToPythObject(self, strObj):
    CfgObject.fromStringToPythObject(self, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID  
    
    
  def AddAgent(self, person):
    """ Adds agent DBID to the CfgAgentGroup object
    Parameters:
      person      -   CfgPerson object
    """
    if person.isAgent != CfgFlag.True:
      ProgrammError("Person %s is not an agent" % person.userName) 
    self.printLog("Agent Group %s: adding shortcut to agent %s" %(self.groupInfo.name, person.userName))
    self.AddDBIDToDBIDList("agentDBIDs", person.DBID)
    
  def DeleteAgent(self, person):
    """ Deletes agent DBID from the CfgAgentGroup object
    Parameters:
      person      -   CfgPerson object
    """
    self.printLog("Agent Group %s: deleting shortcut to agent %s" %(self.groupInfo.name, person.userName))
    self.DeleteDBIDFromDBIDList("agentDBIDs", person.DBID)
    
    
  def AddOption(self, section, key, value, annex = 1):
    """ Adds option to the CfgAgentGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    return 1 - success, desired option is set to desired value, 0 - option not changed
    """
    return BaseCfgGroup.AddOption(self, section, key, value, annex)
    
  def ChangeOption(self, section, key, value, annex = 1): 
    """ Changes option in CfgAgentGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    """
    return BaseCfgGroup.ChangeOption(self, section, key, value, annex)

  def DeleteOption(self, section, key, annex = 1):
    """ Deletes option from CfgAgentGroup object
    Parameters:
      section     -   char
      key         -   char
      annex       -   int
    section could be None, in this case first found option with key = key is deleted
    """
    return BaseCfgGroup.DeleteOption(self, section, key, annex)
    
  def DeleteSection(self, section, annex = 1):
    """ Deletes section from CfgAgentGroup object
    Parameters:
      section     -   char
      annex       -   int
    """
    return BaseCfgGroup.DeleteSection(self, section, annex)    
    
class CfgDNGroup(CfgObject, BaseCfgGroup):
  """ CfgDNGroup object
  Fields:
    groupInfo           - Struct_CfgGroup
    type                - Int
    DNs                 - ListOfStructs_CfgDNInfo
  """
  fields =      (("groupInfo",           "Struct_CfgGroup"),
                 ("type",                "Int"),
                 ("DNs",                 "ListOfStructs_CfgDNInfo"))
                 
  toXmlTranslation = {"groupInfo": "CfgGroup", "CfgDNInfo": "CfgGroupDN"}                 
  fromXmlTranslation = {"CfgGroup": "groupInfo","CfgGroupDN": "CfgDNInfo"}  
  
  translation = All([CfgObject.translation,  {"type":        "CfgDNGroupType"}])
  requiredFields = ["groupInfo"]  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGDNGroup
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
     
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID
    self.title = "CfgDNGroup"    

  def fromStringToPythObject(self, strObj):
    CfgObject.fromStringToPythObject(self, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID  
    
    
  def AddDN(self, dn, trunks = 0):
    """ Adds DN DBID to the CfgDNGroup object
    Parameters:
      dn      -   CfgDN object
      trunks  -   int
    """
    if self.DNs:
      for dnInfo in self.DNs:
        if dnInfo.DNDBID == dn.DBID:
          Message("DN %s already belongs to the group %s" % (dn.number, self.groupInfo.name))  
          return
    self.printLog("DN Group %s: adding shortcut to dn %s" %(self.groupInfo.name, dn.number))
    self.BeginChange()
    if not self.DNs: self.DNs = []
    dnInfo = CfgDNInfo()
    dnInfo.DNDBID = dn.DBID
    dnInfo.trunks = trunks
    self.DNs.append(dnInfo)
    self.EndChange()
    
  def DeleteDN(self, dn):
    """ Adds DN DBID from the CfgDNGroup object
    Parameters:
      dn      -   CfgDN object
    """
    dnInfoToDelete = None
    if self.DNs:
      for dnInfo in self.DNs:
        if dnInfo.DNDBID == dn.DBID:
          dnInfoToDelete = dnInfo
          break
    if not dnInfoToDelete:    
      Message("DN %s does not belong to the group %s" % (dn.number, self.groupInfo.name)) 
      return
    self.printLog("DN Group %s: deleting shortcut to dn %s" %(self.groupInfo.name, dn.number))
    self.BeginChange()
    self.DNs.remove(dnInfoToDelete)
    self.EndChange()
    
  def AddOption(self, section, key, value, annex = 1):
    """ Adds option to the CfgDNGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    return 1 - success, desired option is set to desired value, 0 - option not changed
    """
    return BaseCfgGroup.AddOption(self, section, key, value, annex)
    
  def ChangeOption(self, section, key, value, annex = 1): 
    """ Changes option in CfgDNGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    """
    return BaseCfgGroup.ChangeOption(self, section, key, value, annex)

  def DeleteOption(self, section, key, annex = 1):
    """ Deletes option from CfgDNGroup object
    Parameters:
      section     -   char
      key         -   char
      annex       -   int
    section could be None, in this case first found option with key = key is deleted
    """
    return BaseCfgGroup.DeleteOption(self, section, key, annex)
    
  def DeleteSection(self, section, annex = 1):
    """ Deletes section from CfgDNGroup object
    Parameters:
      section     -   char
      annex       -   int
    """
    return BaseCfgGroup.DeleteSection(self, section, annex)      
    
    
class CfgAccessGroup(CfgObject):
  """ CfgAccessGroup object
  Fields:
    groupInfo           - Struct_CfgGroup
    memberIDs           - ListOfStructs_CfgID
    type                - Int
  """
  fields =      (("groupInfo",          "Struct_CfgGroup"),
                 ("memberIDs",          "ListOfStructs_CfgID"),
                 ("type",               "Int"))
                 
  toXmlTranslation = {"groupInfo": "CfgGroup"}                 
  fromXmlTranslation = {"CfgGroup": "groupInfo"}  
  
  requiredFields = ["groupInfo"]  
  translation = All([CfgObject.translation, {"type": "CfgAccessGroupType"}])                   
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGAccessGroup
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
     
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID
    self.title = "CfgAccessGroup"    

  def fromStringToPythObject(self, strObj):
    CfgObject.fromStringToPythObject(self, strObj)
    self.DBID = 0
    if self.groupInfo:
      self.DBID = self.groupInfo.DBID
      
  def AddOption(self, section, key, value, annex = 1):
    """ Adds option to the CfgAccessGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    return 1 - success, desired option is set to desired value, 0 - option not changed
    """
    return BaseCfgGroup.AddOption(self, section, key, value, annex)
    
  def ChangeOption(self, section, key, value, annex = 1): 
    """ Changes option in CfgAccessGroup object
    Parameters:
      section     -   char
      key         -   char
      value       -   char
      annex       -   int
    """
    return BaseCfgGroup.ChangeOption(self, section, key, value, annex)

  def DeleteOption(self, section, key, annex = 1):
    """ Deletes option from CfgAccessGroup object
    Parameters:
      section     -   char
      key         -   char
      annex       -   int
    section could be None, in this case first found option with key = key is deleted
    """
    return BaseCfgGroup.DeleteOption(self, section, key, annex)
    
  def DeleteSection(self, section, annex = 1):
    """ Deletes section from CfgAccessGroup object
    Parameters:
      section     -   char
      annex       -   int
    """
    return BaseCfgGroup.DeleteSection(self, section, annex)

  def AddMember(self, cfgUser):
    self.BeginChange()
    if self.memberIDs is None:
        self.memberIDs =  []
    found = False
    for memberID in self.memberIDs:
        if memberID.DBID == cfgUser.DBID:
            found = True
            break
    if not found:
        self.memberIDs.append(cfgUser.cfgID)
    self.EndChange()


  def DeleteMember(self, cfgUser):
    self.BeginChange()
    if self.memberIDs is None:
        self.memberIDs =  []
    found = False
    for memberID in self.memberIDs:
        if memberID.DBID == cfgUser.DBID:
            found = True
            break
    if found:
        self.memberIDs.remove(memberID)
    self.EndChange()


#
#                  === CfgAlarmCondition model ===
#
#

from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *

#==================================================================================
class CfgAlarmCondition(CfgObject):
  """ CfgAlarmCondition object
  Fields:
    DBID                     DBID
    name                     Char
    description              Char
    category                 Int
    alarmDetectEvent         CfgDetectEvent
    alarmRemovalEvent        CfgRemovalEvent
    alarmDetectScriptDBID    Int
    clearanceTimeout         Int
    reactionScriptDBIDs      DBIDList
    isMasked                 Int
    state                    Int
    userProperties           KVList
    clearanceScriptDBIDs     DBIDList
  """
  fields =       (("DBID",                   "DBID"),
                 ("name",                   "Char"),
                 ("description",            "Char"),
                 ("category",               "Int"),
                 ("alarmDetectEvent",       "Struct_CfgDetectEvent"),
                 ("alarmRemovalEvent",      "Struct_CfgRemovalEvent"),
                 ("alarmDetectScriptDBID",  "Int"),
                 ("clearanceTimeout",       "Int"),
                 ("reactionScriptDBIDs",    "DBIDList"),
                 ("isMasked",               "Int"),
                 ("state",                  "Int"),
                 ("userProperties",         "KVList"),
                 ("clearanceScriptDBIDs",   "DBIDList"))
                 
  toXmlTranslation = {"alarmDetectEvent": "CfgDetectEvent", "alarmRemovalEvent": "CfgRemovalEvent",}                 
  fromXmlTranslation = {"CfgDetectEvent": "alarmDetectEvent", "CfgRemovalEvent": "alarmRemovalEvent"}     
  
  requiredFields = ["category", "name", "alarmDetectEvent"]
  
  def __init__(self, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGAlarmCondition
    filter = {}
    if name: 
      filter = {"name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgAlarmCondition"
 
    
#==================================================================================
class CfgScript(CfgObject):
  """ CfgScript object
  Fields:
    DBID                    DBID
    name                    Char
    tenantDBID              Int
    index                   Int
    type                    Int
    contactPersonDBID       Int
    state                   Int
    userProperties          KVList
    resources               ListOfStructs_CfgObjectResource
  """
  fields =       (("DBID",                  "DBID"),
                 ("name",                   "Char"),
                 ("tenantDBID",             "Int"),
                 ("index",                  "Int"),
                 ("type",                   "Int"),
                 ("contactPersonDBID",      "Int"),
                 ("state",                  "Int"),
                 ("userProperties",         "KVList"),
                 ("resources",              "ListOfStructs_CfgObjectResource"))     
                 
  translation = All([CfgObject.translation,  {"type":        "CfgScriptType"}])

  requiredFields = ["type", "name", "tenantDBID"]
                 
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGScript
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID}          
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgScript"
     
  def LoadXOStrategy(self, url, other = {}):
    """
    Loads strategy to the Orchestration Server
      url   - string - storage path
      other - dict - parameters
    """
    self.BeginChange()
    userProperties = self.userProperties
    if userProperties == None:
      userProperties = {}
    opts = {"application": url}
    if other:
      for key in other:
        opts[key] = other[key]
    userProperties["Orchestration"] = opts
    self.userProperties = userProperties
    self.EndChange()

  def UnloadXOStrategy(self):
    """
    Unloads strategy from Orchestration Server
    """
    self.BeginChange()
    userProperties = self.userProperties
    if userProperties and userProperties.has_key("Orchestration"):
      del userProperties["Orchestration"]
      self.userProperties = userProperties
      self.EndChange()
     
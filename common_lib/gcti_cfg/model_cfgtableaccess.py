#
#                  === CfgTableAccess model ===
#
#

from common                 import *
from common_enum            import *
from enum                   import *
from model_cfgobject        import *

#==================================================================================
class CfgTableAccess(CfgObject):
  """ CfgTableAccess object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    name                  - Char
    type                  - Int
    description           - Char
    dbAccessDBID          - Int
    formatDBID            - Int
    dbTableName           - Char
    isCachable            - Int
    updateTimeout         - Int
    state                 - Int
    userProperties        - KVList
  """
  fields =      (("DBID",                "DBID"),               
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("type",                "Int"),
                 ("description",         "Char"),
                 ("dbAccessDBID",        "Int"),
                 ("formatDBID",          "Int"),
                 ("dbTableName",         "Char"),
                 ("isCachable",          "Int"),
                 ("updateTimeout",       "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["type", "name", "dbAccessDBID", "tenantDBID", "formatDBID", "dbTableName"]  
  translation = All([CfgObject.translation,  {"type": "CfgTableType", "isCachable": "CfgFlag"}])
  
  def __init__(self, name = None, tenant = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGTableAccess
    if cfgServer == None: cfgServer = GetDefaultCServer() 
    filter = {}
    if name and tenant:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgTableAccess"
    self.dbAccessPoint = None
    if self.dbAccessDBID:
      self.dbAccessPoint = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, self.dbAccessDBID)

  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.isCachable = CfgFlag.False.val
   
    
# corrected sequence of parameters in init
class CfgTableAccess_N(CfgTableAccess):
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    CfgTableAccess.__init__(self, name, tenant, cfgServer, strObj)

#
#                  === CfgTimeZone model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *

#==================================================================================
class CfgTimeZone(CfgObject):
  """ CfgTimeZone object
  Fields:
    DBID                    - Int
    tenantDBID              - Int
    name                    - Char
    description             - Char
    offset                  - Int
    isDSTObserved           - Int
    DSTStartDate            - Int
    DSTStopDate             - Int
    nameNetscape            - Char
    nameMSExplorer          - Char
    state                   - Int
    userProperties          - KVList
    DSTOffset               - Int
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("description",         "Char"),
                 ("offset",              "Int"),
                 ("isDSTObserved",       "Int"),
                 ("DSTStartDate",        "Int"),
                 ("DSTStopDate",         "Int"),
                 ("nameNetscape",        "Char"),
                 ("nameMSExplorer",      "Char"),                 
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("DSTOffset",           "Int"))
  requiredFields = ["tenantDBID", "name", "offset", "nameNetscape", "nameMSExplorer"]
  translation = All([CfgObject.translation,  {"isDSTObserved": "CfgFlag"}])
  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGTimeZone
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgTimeZone"
    
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.isDSTObserved = CfgFlag.True.val

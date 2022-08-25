#
#                  === CfgVoicePrompt model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *
#==================================================================================
class CfgVoicePrompt(CfgObject):
  """ CfgVoicePrompt object
  Fields:
    DBID                    - Int
    switchDBID              - Int
    tenantDBID              - Int
    name                    - Char
    description             - Char
    scriptDBID              - Int
    state                   - Int
    userProperties          - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("switchDBID",          "Int"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("description",         "Char"),
                 ("scriptDBID",          "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "switchDBID", "name"]

  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGVoicePrompt
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name: # otherwise create empty object
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID }
      
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgVoicePrompt"
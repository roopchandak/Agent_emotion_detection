from model_cfgobject      import *
class CfgTransaction(CfgObject):
  """ CfgTransaction object
  Fields:
    DBID                    - Int
    tenantDBID              - Int
    name                    - Char
    type                    - Int
    recordPeriod            - Int
    alias                   - Char
    description             - Char
    state                   - Int
    userProperties          - KVList
  """
  fields =      (("DBID",                   "DBID"),
                 ("tenantDBID",             "Int"),
                 ("name",                   "Char"),
                 ("type",                   "Int"),
                 ("recordPeriod",           "Int"),
                 ("alias",                  "Char"),
                 ("description",            "Char"),
                 ("state",                  "Int"),
                 ("userProperties",         "KVList"))
  translation = {"Int":  "CfgTransactionType"}                       
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    if cfgServer == None: cfgServer = GetDefaultCServer()
    self.objType = CfgObjectType.CFGTransaction
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgTransaction"


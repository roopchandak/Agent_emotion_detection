from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *



class CfgRole(CfgObject):
  """ CfgRole object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    name                - Char
    description         - Char
    state               - Int
    userProperties      - KVList
    members             - ListOfStructs_CfgRoleMember
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("description",         "Char"),  
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("members",             "ListOfStructs_CfgRoleMember"),
                )
  requiredFields = ["tenantDBID", "name"]
  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGRole
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID}          
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgRole"
    
  def AddMember(self, cfgObj):
    found = 0
    if not self.members: self.members = []
    for member in self.members:
      if member.objectDBID == cfgObj.DBID:
        found = 1
        break
    if not found:
      cfgRoleMember = CfgRoleMember()
      cfgRoleMember.objectDBID = cfgObj.DBID
      cfgRoleMember.objectType = cfgObj.objType.val
      self.BeginChange()
      self.members.append(cfgRoleMember)
      self.EndChange()
    else:
      ProgrammWarning("Object %s, DBID %s is already a member of %s"%(cfgObj.objType, cfgObj.DBID, self.name))


  def RemoveMember(self, cfgObj):
    ind = -1
    if self.members:
      i = 0
      for member in self.members:
        if member.objectDBID == cfgObj.DBID:
          ind = i
          break
        i = i + 1
    if ind > -1:
      
      self.BeginChange()
      self.members.remove(self.members[ind])
      self.EndChange()
    else:
      ProgrammWarning("Object %s, DBID %s is not a member of %s"%(cfgObj.objType, cfgObj.DBID, self.name))
                
#
#                  === CfgSolution model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *
#==================================================================================
class CfgSolution(CfgObject):
  """ CfgSolution object
  Fields:
    DBID                  - Int
    name                  - Char
    abbr                  - Char
    type                  - Int
    appServicePermissions - Struct_CfgAppServicePermission
    state                 - Int
    userProperties        - KVList
    solutionType          - Int
    components            - ListOfStructs_CfgSolutionComponent
    SCSDBID               - Int
    assignedTenantDBID    - Int
    version               - Char
    componentDefinitions  - ListOfStructs_CfgSolutionComponentDefinition
    startupType           - Int
    resources             - ListOfStructs_CfgObjectResource
  """
  fields =      (("DBID",                     "DBID"),
                 ("name",                     "Char"),
                 ("abbr",                     "Char"),
                 ("type",                     "Int"),
                 ("appServicePermissions",    "Struct_CfgAppServicePermission"),
                 ("state",                    "Int"),
                 ("userProperties",           "KVList"),
                 ("solutionType",             "Int"),
                 ("components",               "ListOfStructs_CfgSolutionComponent"),
                 ("SCSDBID",                  "Int"),
                 ("assignedTenantDBID",       "Int"),
                 ("version",                  "Char"),
                 ("componentDefinitions",     "ListOfStructs_CfgSolutionComponentDefinition"),
                 ("startupType",              "Int"),
                 ("resources",           "ListOfStructs_CfgObjectResource"))
                 
  toXmlTranslation = {"appServicePermissions": "CfgAppServicePermission"}                 
  fromXmlTranslation = {"CfgAppServicePermission": "appServicePermissions"}
                 
  def __init__(self, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGService
    filter = {}
    if name:
      filter =  {"name" : name }
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)

    self.title = "CfgService" 


  def AddComponent(self, cfgApp, startupPriority = 1, isOptional = CfgFlag.False):
    dbid = cfgApp.DBID

    if self.components <> None:
      for comp in self.components:
       if comp.appDBID == dbid: 
         ProgrammWarning("Application %s is already a component of the solution %s" %(cfgApp.name, self.name))
    else:
      self.components = []
    newComp = CfgSolutionComponent()
    newComp.appDBID = dbid
    newComp.startupPriority = startupPriority
    newComp.isOptional = isOptional.val
    self.BeginChange()
    self.components.append(newComp)
    self.EndChange()
    
  def DeleteComponent(self, cfgApp):
    dbid = cfgApp.DBID
    found = 0
    for comp in self.components:
     if comp.appDBID == dbid: 
       found = 1
       break
    if not found:
      ProgrammError("Application %s is not a component of the solution %s" %(cfgApp.name, self.name))
    self.BeginChange()
    self.components.remove(comp)
    self.EndChange()
 
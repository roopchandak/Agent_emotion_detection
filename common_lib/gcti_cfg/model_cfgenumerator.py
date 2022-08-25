from common               import *
from common_enum          import *
from model_cfgobject      import *

class CfgBusinessAttribute(CfgObject):
  """ CfgBusinessAttribute object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    name                - Char
    description         - Char
    state               - Int
    userProperties      - KVList
    type                - Int
    displayName         - Char
  """
  fields =        (("DBID",                "DBID"   ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("description",         "Char"   ),
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ),
                   ("type",                "Int"    ),
                   ("displayName",         "Char"   ))

                   
  requiredFields = ["type", "name", "displayName", "tenantDBID"]                  
  translation = All([CfgObject.translation,  {"type":        "CfgEnumeratorType"}])
  def __init__(self, tenant = None, name = None, displayName = None, cfgServer = None, strObj = None):
    """object can be extracted by tenant name and either name or display name"""
    self.objType = CfgObjectType.CFGEnumerator
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and (name or displayName):
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      if name:
        filter = {"name" : name, "tenant_dbid": tenantDBID }
      else: # display name
        filter = {"display_name" : displayName, "tenant_dbid": tenantDBID }
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgEnumerator"
    

class CfgAttributeValue(CfgObject):
  """ CfgAttributeValue object
  Fields:
    DBID                - Int
    enumeratorDBID      - Int
    tenantDBID          - Int
    name                - Char
    description         - Char
    isDefault           - Int
    state               - Int
    userProperties      - KVList
    displayName         - Char
  """
  fields =        (("DBID",                "DBID"   ),
                   ("enumeratorDBID",      "Int"    ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("description",         "Char"   ),
                   ("isDefault",           "Int"    ),
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ),
                   ("displayName",         "Char"   ))

                   
  requiredFields = ["enumeratorDBID", "name", "displayName", "tenantDBID"]                         

  def __init__(self, tenant = None, businessAttributeName = None, businessAttributeDisplayName = None, name = None, displayName = None, cfgServer = None, strObj = None):
    """object can be extracted by tenant name and either (businessAttribute name and value name) or (businessAttribute display name and value display name)"""
    self.objType = CfgObjectType.CFGEnumeratorValue
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant:
    
    
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      
      if (businessAttributeName):
        filter = {"name" : businessAttributeName, "tenant_dbid": tenantDBID}
        enumeratorDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGEnumerator, filter)
      elif (businessAttributeDisplayName):
        filter = {"display_name" : businessAttributeDisplayName, "tenant_dbid": tenantDBID}
        enumeratorDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGEnumerator, filter)
      else:
        ProgrammError("Either businessAttributeName or businessAttributeDisplayName should be provided")
      if name:  
        filter = {"name" : name, "tenant_dbid": tenantDBID,  "enumerator_dbid": enumeratorDBID}
      elif displayName:
        filter = {"display_name" : displayName, "tenant_dbid": tenantDBID,  "enumerator_dbid": enumeratorDBID}
      else:
        ProgrammError("Either value name or value displayName should be provided")
     
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgEnumeratorValue"
    
CfgEnumerator = CfgBusinessAttribute
CfgEnumeratorValue = CfgAttributeValue


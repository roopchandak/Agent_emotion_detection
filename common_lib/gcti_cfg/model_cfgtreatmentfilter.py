
from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *
import time
#==================================================================================
class CfgTreatment(CfgObject):
  """ CfgTreatment object
  Fields:
    DBID                    - Int
    tenantDBID              - Int
    name                    - Char
    description             - Char
    callResult              - Int
    recActionCode           - Int
    attempts                - Int
    dateTime                - Int
    cycleAttempt            - Int
    interval                - Int
    increment               - Int
    callActionCode          - Int
    destDNDBID              - Int
    state                   - Int
    userProperties          - KVList
    range                   - Int
  """
  fields =        (("DBID",                "DBID"   ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("description",         "Char"   ),
                   ("callResult",          "Int"    ),
                   ("recActionCode",       "Int"    ),
                   ("attempts",            "Int"    ), #Interval
                   ("dateTime",            "Int"    ),
                   ("cycleAttempt",        "Int"    ),
                   ("interval",            "Int"    ), #Days*24*60 + Hrs*60 + Mins
                   ("increment",           "Int"    ),
                   ("callActionCode",      "Int"    ),   
                   ("destDNDBID",          "Int"    ),                   
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ),
                   ("range",               "Int"))
  translation = All([CfgObject.translation, {"callResult":     "CallState",
                                             "recActionCode":  "CfgRecActionCode",
                                             "callActionCode": "CfgCallActionCode"}])  
  requiredFields = ["tenantDBID", "name", "callResult", "recActionCode"]                                             

  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGTreatment
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID }

    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgTreatment"

  def ChangeDateTime(self, newDateTime = time.time()):
    """newDateTime - in seconds"""
    self.BeginChange()
    self.dateTime = newDateTime
    self.EndChange() 
      

#==================================================================================    
class CfgFilter(CfgObject):
  """ CfgFilter object
  Fields:
    DBID                    - Int
    tenantDBID              - Int
    name                    - Char
    description             - Char
    formatDBID              - Int
    state                   - Int
    userProperties          - KVList
  """
  fields =        (("DBID",                "DBID"   ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("description",         "Char"   ),
                   ("formatDBID",          "Int"    ),                   
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ))
                   
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGFilter
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID }
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgFilter"
    



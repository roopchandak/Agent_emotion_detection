

from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *
#==================================================================================

#
#                  === CfgStatDay model ===
#
#
#==================================================================================


class CfgStatDay(CfgObject):
  """ CfgStatDay object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    name                  - Char
    isDayOfWeek           - Int
    day                   - Int
    startTime             - Int
    endTime               - Int
    minValue              - Int
    maxValue              - Int
    targetValue           - Int
    intervalLength        - Int
    statIntervals         - ListOfStructs_CfgStatInterval
    state                 - Int
    userProperties        - KVList
    date                  - Int
    type                  - Int
    useFlatRate           - Int
    flatRate              - Int
  """
  fields =       (("DBID",               "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("isDayOfWeek",         "Int"),                 
                 ("day",                 "Int"),  
                 ("startTime",           "Int"),  
                 ("endTime",             "Int"),  
                 ("minValue",            "Int"),    
                 ("maxValue",            "Int"),  
                 ("targetValue",         "Int"),  
                 ("intervalLength",      "Int"),                   
                 ("statIntervals",       "ListOfStructs_CfgStatInterval"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("date",                "Int"),
                 ("type",                "Int"),
                 ("useFlatRate",         "Int"),
                 ("flatRate",            "Int"))                 
        

  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGStatDay
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgStatDay"


#==================================================================================
#   
#
#                  === CfgStatTable model ===
#
#
#==================================================================================

class CfgStatTable(CfgObject):
  """ CfgStatTable object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    name                  - Char
    type                  - Int
    statDayDBIDs          - DBIDList
    state                 - Int
    userProperties        - KVList
    waitThreshold         - Int
    flatRate              - Int
    agentHourlyRate       - Int
    useFlatRate           - Int
  """
  fields =       (("DBID",               "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("type",                "Int"),                 
                 ("statDayDBIDs",        "DBIDList"),  
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("waitThreshold",       "Int"),
                 ("flatRate",            "Int"),                 
                 ("agentHourlyRate",     "Int"),  
                 ("useFlatRate",         "Int"))                 

  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGStatTable
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : name}

    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgStatTable"
  
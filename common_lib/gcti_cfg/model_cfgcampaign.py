#
#                  === CfgCampaign model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *
#==================================================================================
class CfgCampaign(CfgObject):
  """ CfgCampaign object
  Fields:
    DBID              -   Int
    tenantDBID        -   Int
    name              -   Char
    description       -   Char
    callingLists      -   ListOfStructs_CfgCallingListInfo
    campaignGroups    -   ListOfStructs_CfgCampaignGroupInfo
    scriptDBID        -   Int
    state             -   Int
    userProperties    -   KVList
  """
  fields =       (("DBID",               "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),                  
                 ("description",         "Char"),
                 ("callingLists",        "ListOfStructs_CfgCallingListInfo"),
                 ("campaignGroups",      "ListOfStructs_CfgCampaignGroupInfo"),
                 ("scriptDBID",          "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "name"]
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGCampaign
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : name}
 
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgCampaign"


  def AddCallingList(self, cfgCallingList, listWeight = 10, isActive = CfgFlag.True):
    """Add calling list to campaign"""
    cfgCallingListDBID = cfgCallingList.DBID
    if self.callingLists:
      for callingList in self.callingLists:
        if callingList.callingListDBID == cfgCallingListDBID:
          ProgrammWarning("Campaign %s already has calling list %s" %(self.name, cfgCallingList.name))
          return
    self.BeginChange()
    if self.callingLists == None: self.callingLists = []    
    cfgCallingListInfo = CfgCallingListInfo()
    cfgCallingListInfo.SetAttributes({"callingListDBID": cfgCallingListDBID, 
                                      "share": listWeight,
                                      "isActive": isActive})
    self.callingLists.append(cfgCallingListInfo)
    self.EndChange()
      
  def ChangeCallingList(self, cfgCallingList, listWeight = 10, isActive = CfgFlag.True):
    """Change specified calling list parameters"""
    cfgCallingListDBID = cfgCallingList.DBID
    if self.callingLists:
      for callingList in self.callingLists:
        if callingList.callingListDBID == cfgCallingListDBID:
          self.BeginChange()
          callingList.listWeight = listWeight
          callingList.isActive = isActive
          self.EndChange()
          return
    self.AddCallingList(cfgCallingList, isActive)


  def DeleteCallingList(self, cfgCallingList):
    """Delete calling list from campaign"""
    cfgCallingListDBID = cfgCallingList.DBID
    if not self.callingLists:
      Message("Campaign %s does not have calling list %s, calling list cannot be removed" %(self.name, cfgCallingList.name))
      return
    found = 0
    self.BeginChange()
    if self.callingLists:
      for callingList in self.callingLists:
        if callingList.callingListDBID == cfgCallingListDBID:
          found = 1
          self.callingLists.remove(callingList)
          self.EndChange()
          break
    if not found:
      Message("Campaign %s does not have calling list %s, calling list cannot be removed" %(self.name, cfgCallingList.name))
      return
  
#==================================================================================
class CfgCallingList(CfgObject):
  """ CfgCallingList object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    name                - Char
    description         - Char
    tableAccessDBID     - Int
    filterDBID          - Int
    treatmentDBIDs      - DBIDList
    logTableAccessDBID  - Int
    timeFrom            - Int
    timeUntil           - Int
    maxAttempts         - Int
    scriptDBID          - Int
    state               - Int
    userProperties      - KVList
  """
  fields =       (("DBID",               "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),                  
                 ("description",         "Char"),
                 ("tableAccessDBID",     "Int"),
                 ("filterDBID",          "Int"),
                 ("treatmentDBIDs",      "DBIDList"),
                 ("logTableAccessDBID",  "Int"),
                 ("timeFrom",            "Int"),
                 ("timeUntil",           "Int"),
                 ("maxAttempts",         "Int"),
                 ("scriptDBID",          "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "name", "tableAccessDBID"]               
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGCallingList
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : name}
 
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgCallingList"
  
  def AddTreatment(self, cfgTreatment):
    self.printLog("Calling list %s: adding shortcut to treatment %s" %(self.name, cfgTreatment.name))
    self.AddDBIDToDBIDList("treatmentDBIDs", cfgTreatment.DBID)
    
  def DeleteTreatment(self, cfgTreatment):
    self.printLog("Calling list %s: deleting shortcut to treatment %s" %(self.name, cfgTreatment.name))
    self.DeleteDBIDFromDBIDList("treatmentDBIDs", cfgTreatment.DBID)
    
#==================================================================================
class CfgCampaignGroup(CfgObject):
  """ CfgCampaignGroup object
  Fields:
    DBID                  - Int
    campaignDBID          - Int
    tenantDBID            - Int
    name                  - Char
    groupDBID             - Int
    groupType             - Int
    description           - Char
    serverDBIDs           - DBIDList
    IVRProfileDBID        - Int
    dialMode              - Int
    origDNDBID            - Int
    numOfChannels         - Int
    operationMode         - Int
    minRecBuffSize        - Int
    optRecBuffSize        - Int
    maxQueueSize          - Int
    optMethod             - Int
    optMethodValue        - Int
    interactionQueueDBID  - Int
    scriptDBID            - Int
    state                 - Int
    userProperties        - KVList
    trunkGroupDNDBID      - Int
  """
  fields =    (("DBID",                 "DBID"), 
              ("campaignDBID",          "Int"),
              ("tenantDBID",            "Int"),
              ("name",                  "Char"),
              ("groupDBID",             "Int"),
              ("groupType",             "Int"),
              ("description",           "Char"),
              ("serverDBIDs",           "DBIDList"),
              ("IVRProfileDBID",        "Int"),
              ("dialMode",              "Int"),
              ("origDNDBID",            "Int"),
              ("numOfChannels",         "Int"),
              ("operationMode",         "Int"),
              ("minRecBuffSize",        "Int"),
              ("optRecBuffSize",        "Int"),
              ("maxQueueSize",          "Int"),
              ("optMethod",             "Int"),
              ("optMethodValue",        "Int"),
              ("interactionQueueDBID",  "Int"),
              ("scriptDBID",            "Int"),
              ("state",                 "Int"),
              ("userProperties",        "KVList"),
              ("trunkGroupDNDBID",      "Int"))
  translation = All([CfgObject.translation,  {"groupType": "CfgObjectType", "dialMode": "CfgDialMode", "operationMode": "CfgOperationMode",
                 "optMethod": "CfgOptimizationMethod"}])                       
  requiredFields = ["tenantDBID", "name", "campaignDBID", "groupDBID"]

  def __init__(self, tenant = None, campaign = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGCampaignGroup
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter =  {"tenant_dbid": tenantDBID, "name" : campaign}
      campaignDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGCampaign, filter)

      filter = {"tenant_dbid": tenantDBID, "campaign_dbid": campaignDBID, "name" : name}
 
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgCampaignGroup"

  def AddConnectionDBID(self, serverDBID):
    self.AddDBIDToDBIDList("serverDBIDs", serverDBID)
    
  def DeleteConnectionDBID(self, serverDBID):
    self.DeleteDBIDFromDBIDList("serverDBIDs", serverDBID)

  def AddConnection(self, cfgApp):
    """Add connection to cfgApp"""
    self.AddConnectionDBID(cfgApp.DBID) 
    
  def DeleteConnection(self, cfgApp):
    """Delete connection to cfgApp"""
    self.DeleteConnectionDBID(cfgApp.DBID) 
    

from common_enum       import *
from model_cfgobject   import *

class CfgField(CfgObject):
  """ CfgField object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    name                  - Char
    type                  - Int
    description           - Char
    length                - Int
    fieldType             - Int
    defaultValue          - Char
    isPrimaryKey          - Int
    isUnique              - Int
    isNullable            - Int
    state                 - Int
    userProperties        - KVList
  """
  fields =        (("DBID",                "DBID"   ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("type",                "Int"    ),
                   ("description",         "Char"   ),
                   ("length",              "Int"    ),
                   ("fieldType",           "Int"    ),
                   ("defaultValue",        "Char"   ),
                   ("isPrimaryKey",        "Int"    ),
                   ("isUnique",            "Int"    ),
                   ("isNullable",          "Int"    ),
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ))

                   
  requiredFields = ["type", "name", "fieldType", "tenantDBID"]  
  translation = All([CfgObject.translation, {"type": "CfgDataType",
                                             "fieldType": "CfgFieldType",
                                             "isPrimaryKey": "CfgFlag",
                                             "isUnique": "CfgFlag",
                                             "isNullable": "CfgFlag"}])    

  def __init__(self, tenant = None,  name = None, fieldType = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGField
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID}
      if fieldType <> None:
        filter["field_type"] = fieldType.val
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgField"
    
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.isPrimaryKey = CfgFlag.False.val
    self.isUnique = CfgFlag.False.val
    self.isNullable = CfgFlag.False.val
#==================================================================================    
class CfgFormat(CfgObject):
  """ CfgFormat object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    name                  - Char
    description           - Char
    fieldDBIDs            - DBIDList
    state                 - Int
    userProperties        - KVList
  """
  fields =        (("DBID",                "DBID"   ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("description",         "Char"   ),
                   ("fieldDBIDs",          "DBIDList"),
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ))
  requiredFields = ["name", "tenantDBID"]  
  
  def __init__(self, tenant = None,  name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGFormat
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgFormat"
    
    
  def AddField(self, cfgField):
    """Add Field shortcut to Format"""
    self.printLog("Format %s: adding shortcut to field %s" %(self.name, cfgField.name))
    self.AddDBIDToDBIDList("fieldDBIDs", cfgField.DBID)
    
  
  def DeleteField(self, cfgField):
    """Delete Field shortcut from Format"""
    self.printLog("Format %s: deleting shortcut to field %s" %(self.name, cfgField.name))
    self.DeleteDBIDFromDBIDList("fieldDBIDs", cfgField.DBID)
        
#==================================================================================    

class CfgObjectiveTable(CfgObject):
  """ CfgObjectiveTable object
  Fields:
    DBID                  - Int
    tenantDBID            - Int
    name                  - Char
    description           - Char
    objectiveRecords      - ListOfStructs_CfgObjectiveTableRecord
    state                 - Int
    userProperties        - KVList
    prepaidCost           - Int
    timeZoneDBID          - Int
    timeStart             - Int
    timeEnd               - Int
    type                  - Int
  """
  fields =        (("DBID",                "DBID"   ),
                   ("tenantDBID",          "Int"    ),
                   ("name",                "Char"   ),
                   ("description",         "Char"   ),
                   ("objectiveRecords",    "ListOfStructs_CfgObjectiveTableRecord"),
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ),
                   ("prepaidCost",         "Int"    ),
                   ("timeZoneDBID",        "Int"    ),
                   ("timeStart",           "Int"    ),
                   ("timeEnd",             "Int"    ),
                   ("type",                "Int"    ))

  requiredFields = ["name", "tenantDBID"]  
  translation = All([CfgObject.translation, {"type": "CfgObjectiveTableType"}])    
  def __init__(self, tenant = None,  name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGObjectiveTable
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"name" : name, "tenant_dbid": tenantDBID}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgObjectiveTable"

  def AddRecord(self, mediaType, serviceType, customerSegment, objectiveThreshold = 0,
                 objectiveDelta = 0, contract = None):
    cfgObjectiveTableRecord = CfgObjectiveTableRecord()
    cfgObjectiveTableRecord.mediaTypeDBID = mediaType.DBID
    cfgObjectiveTableRecord.serviceTypeDBID = serviceType.DBID
    cfgObjectiveTableRecord.customerSegmentDBID = customerSegment.DBID
    cfgObjectiveTableRecord.objectiveThreshold = objectiveThreshold
    cfgObjectiveTableRecord.objectiveDelta = objectiveDelta
    if contract == None:
      contractDBID = 0
    else:
      contractDBID = contract.DBID
    self.BeginChange()
    if not self.objectiveRecords: self.objectiveRecords = []
    self.objectiveRecords.append(cfgObjectiveTableRecord)
    self.EndChange()

  def DeleteRecord(self, mediaType, serviceType, customerSegment):
    objRecordToDelete = None
    if not self.objectiveRecords:
      Message("Objective record with params %s, %s, %s does not belong to objective table %s" %(mediaType.name, serviceType.name, customerSegment.name, self.name))
      return
    
    for objRecord in self.objectiveRecords:
      if objRecord.mediaTypeDBID == mediaType.DBID and \
         objRecord.serviceTypeDBID == serviceType.DBID and \
         objRecord.customerSegmentDBID == customerSegment.DBID:
         objRecordToDelete = objRecord
    if not objRecordToDelete:
      Message("Objective record with params %s, %s, %s does not belong to objective table %s" %(mediaType.name, serviceType.name, customerSegment.name, self.name))
      return
       
    self.BeginChange()
    self.objectiveRecords.remove(objRecordToDelete)
    self.EndChange()
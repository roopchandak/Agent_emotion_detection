from common_enum          import *
from enum                 import *
from model_cfgobject      import *

#==================================================================================
class CfgFolder(CfgObject):
  """ CfgFolder object
  Fields:
    DBID                - Int
    name                - Char
    type                - Int
    ownerID             - Struct_CfgOwnerID
    state               - Int
    userProperties      - KVList
    objectIDs           - ListOfStructs_CfgID
    parentID            - Struct_CfgParentID
    description         - Char
    folderClass         - Int
    customType          - Int
    resources           - ListOfStructs_CfgObjectResource
  """
  
  fields =        (("DBID",                "DBID"   ),
                   ("name",                "Char"   ),
                   ("type",                "Int"    ),
                   ("ownerID",             "Struct_CfgOwnerID"),
                   ("state",               "Int"    ),
                   ("userProperties",      "KVList" ),
                   ("objectIDs",           "ListOfStructs_CfgID"),
                   ("parentID",            "Struct_CfgParentID"),
                   ("description",         "Char"),
                   ("folderClass",         "Int"),
                   ("customType",          "Int" ),
                   ("resources",           "ListOfStructs_CfgObjectResource"))                   
                   
  toXmlTranslation = {"ownerID": "CfgOwnerID", "parentID": "CfgParentID"}                 
  fromXmlTranslation = {"CfgOwnerID": "ownerID", "CfgParentID": "parentID"}  
          
  translation = All([CfgObject.translation, {"type":     "CfgObjectType"}])                   
  requiredFields = ["name", "type"
                    ]   
  def __init__(self, name = None, ownerName = None, ownerType = None, parentName = None, parentType = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGFolder
    if cfgServer == None: self.cfgServer = GetDefaultCServer()
    else:               self.cfgServer = cfgServer
    filter = {}
    if name:
      if ownerName and ownerType and parentName and parentType: #and parentName
        filter = {"name" : ownerName}
        ownerDBID = self.cfgServer.GetObjectDBID(ownerType, filter)
        filter = {"name" : name, "owner_dbid": ownerDBID, "owner_type": ownerType.val}
        objects = self.cfgServer.GetObjectInfo(self.objType, filter)

        for obj in objects:
          parentID = GetObjectStructPropertyFromString(self, obj, propName = "parentID", structType = "CfgID")
          if parentID.type == parentType.val:
            parentNameFromID = self.cfgServer.GetObjectNameByObjectTypeAndDBID(parentType, parentID.DBID)
            if parentName == parentNameFromID:
              strObj = obj
              break
        if not strObj:
          FatalError("Cannot find CfgFolder with parameters name %s ownerName %s ownerType %s parentName %s parentType %s" %(name, ownerName, ownerType, parentName, parentType))
        filter = {}
      elif ownerName and ownerType:
        filter = {"name" : ownerName}
        ownerDBID = self.cfgServer.GetObjectDBID(ownerType, filter)
        filter = {"name" : name, "owner_dbid": ownerDBID, "owner_type": ownerType.val}
        objects = self.cfgServer.GetObjectInfo(self.objType, filter)
        if len(objects) > 1:
          FatalError("Cannot find CfgFolder with parameters name %s ownerName %s ownerType %s parentName %s parentType %s" %(name, ownerName, ownerType, parentName, parentType))        
        else:
          strObj = objects[0]
        filter = {}
      else: # try to get by name only
        filter = {"name" : name }
      
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj = strObj)
    #reqID = self.cfgServer.RegisterObjectType(self.objType)
    #self.cfgServer.WaitEvent(reqID)
    self.title = "CfgFolder"



  def addObjectToList(self, object):
    """object must exist and be the same type as folder"""

    if object.objType <> self.type:
      ProgrammError("Types of object and folder are different")
    if self.objectIDs:
      for id in self.objectIDs:
        if id.DBID == object.DBID:
          ProgrammWarning("Object (DBID %s) is already in folder %s" %(object.DBID, self.name))
        
    objectID = CfgID()
    objectID.SetAttributes({"DBID": object.DBID,
                            "type": self.type})
    self.BeginChange()                          
    if self.objectIDs == None:                            
      self.objectIDs = []
      
    self.objectIDs.append(objectID)
    self.EndChange()                          
  
  


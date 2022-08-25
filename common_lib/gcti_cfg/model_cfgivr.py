from model_cfgobject import *
#==================================================================================
class CfgIVRPort(CfgObject):
  """ CfgIVRPort object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    portNumber          - Char
    description         - Char
    IVRDBID             - Int
    DNDBID              - Int
    state               - Int
    userProperties      - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("portNumber",          "Char"),
                 ("description",         "Char"),
                 ("IVRDBID",             "Int"),
                 ("DNDBID",              "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "portNumber", "IVRDBID"]

  
  def __init__(self, tenant = None, portNumber = None, IVR = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGIVRPort
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and portNumber and IVR:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)
      filter = {"tenant_dbid": tenantDBID, "name" : IVR}
      IVRDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGIVR, filter)
      filter = {"tenant_dbid": tenantDBID, "port_number" : portNumber, "ivr_dbid": IVRDBID}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgIVRPort"


#==================================================================================
class CfgIVR(CfgObject):
  """ CfgIVR object
  Fields:
    DBID                - Int
    tenantDBID          - Int
    name                - Char
    description         - Char
    type                - Int
    version             - Char
    IVRServerDBID       - Int
    state               - Int
    userProperties      - KVList
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("name",                "Char"),
                 ("description",         "Char"),
                 ("type",                "Int"),
                 ("version",             "Char"),
                 ("IVRServerDBID",       "Int"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"))
  requiredFields = ["tenantDBID", "name", "type", "version"]
  translation = All([CfgObject.translation,  {"type": "CfgIVRType"}])               

  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGIVR
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgIVR"
    
#==================================================================================
class CfgGVPIVRProfile(CfgObject):
  """ CfgGVPIVRProfile object
  Fields:
     DBID                -  Int
     tenantDBID          -  Int
     customerDBID        -  Int
     resellerDBID        -  Int
     name                -  Char
     displayName         -  Char
     type                -  Int
     notes               -  Char
     description         -  Char
     startServiceDate    -  Int
     endServiceDate      -  Int
     isProvisioned       -  Int
     tfn                 -  Char
     status              -  Char
     DIDDBIDs            -  DBIDList
     state               -  Int
     userProperties      -  KVList
     resources           -  List Of Structs CfgObjectResource                    
  """
  fields =      (("DBID",                "DBID"),
                 ("tenantDBID",          "Int"),
                 ("customerDBID",        "Int"),
                 ("resellerDBID",        "Int"),
                 ("name",                "Char"),
                 ("displayName",         "Char"),
                 ("type",                "Int"),
                 ("notes",               "Char"),
                 ("description",         "Char"),
                 ("startServiceDate",    "Int"),
                 ("endServiceDate",      "Int"),
                 ("isProvisioned",       "Int"),
                 ("tfn",                 "Char"),
                 ("status",              "Char"),
                 ("DIDDBIDs",            "DBIDList"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("resources",           "ListOfStructs_CfgObjectResource"))                      

  requiredFields = ["tenantDBID", "name"]
  
  def __init__(self, tenant = None, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGGVPIVRProfile
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and name:
      filter = {"name" : tenant}
      tenantDBID = cfgServer.GetObjectDBID(CfgObjectType.CFGTenant, filter)

      filter = {"tenant_dbid": tenantDBID, "name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
   
    self.title = "CfgGVPIVRProfile"
    
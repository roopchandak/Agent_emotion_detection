#
#                  === CfgDN model ===
#
#

from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *
import model_cfgapplication
#==================================================================================
class CfgDN(CfgObject):
  """ CfgDN object
  Fields:
    DBID                - Int
    switchDBID          - Int
    tenantDBID          - Int
    type                - Int
    number              - Char
    association         - Char
    destDNDBIDs         - DBIDList
    loginFlag           - Int
    DNLoginID           - Char
    registerAll         - Int
    groupDBID           - Int
    trunks              - Int
    routeType           - Int
    override            - Char
    state               - Int
    userProperties      - KVList
    name                - Char
    useOverride         - Int
    switchSpecific      - Int
    accessNumbers       - ListOfStructs_CfgDNAccessNumber
    siteDBID            - Int
    contractDBID        - Int
  """
  fields =       (("DBID",               "DBID"),
                 ("switchDBID",          "Int"),
                 ("tenantDBID",          "Int"),
                 ("type",                "Int"),
                 ("number",              "Char"),
                 ("association",         "Char"),
                 ("destDNDBIDs",         "DBIDList"),
                 ("loginFlag",           "Int"),
                 ("DNLoginID",           "Char"),
                 ("registerAll",         "Int"),
                 ("groupDBID",           "Int"),
                 ("trunks",              "Int"),
                 ("routeType",           "Int"),
                 ("override",            "Char"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("name",                "Char"),
                 ("useOverride",         "Int"),
                 ("switchSpecificType",  "Int"),
                 ("accessNumbers",       "ListOfStructs_CfgDNAccessNumber"),
                 ("siteDBID",            "Int"),
                 ("contractDBID",        "Int"))
  translation = All([CfgObject.translation,  {"type":        "CfgDNType",
                                              "loginFlag":   "CfgFlag",
                                              "registerAll": "CfgDNRegisterFlag",
                                              "useOverride": "CfgFlag",
                                              "routeType":   "CfgRouteType"}])  
  requiredFields = ["type", "number", "switchDBID", "tenantDBID"]
  
  def __init__(self, tenant = None, switch = None, number = None, type = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGDN
    if cfgServer == None: cfgServer = GetDefaultCServer()
    filter = {}
    if tenant and switch and number: # otherwise create empty object
      cfgTenant = cfgServer.GetObjectByTypeAndName(CfgObjectType.CFGTenant, tenant)
      tenantDBID = cfgTenant.DBID
      cfgSwitch = cfgServer.GetObjectByTypeAndTenantNameAndName(CfgObjectType.CFGSwitch, tenant, switch)
      self.switchDBID = cfgSwitch.DBID
      filter = {"dn_number" : number, "switch_dbid": self.switchDBID }
    if type:
      if isinstance(type, EnumElem):
        type = type.val
      filter["dn_type"] = type
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgDN"


  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.loginFlag = CfgFlag.False.val
    self.registerAll = CfgFlag.False.val
    self.useOverride = CfgFlag.True.val
    self.routeType = CfgRouteType.CFGDefault.val
    self.switchSpecificType = 1
    


  def UnloadStrategy(self, cfgRouterApp, firstTime = 1):
    """ Unload strategy from DN - Universal Routing Server """
    if type(cfgRouterApp) == type(""): # appName
      cfgRouterApp = model_cfgapplication.CfgApplication(cfgRouterApp)
    if not isinstance(cfgRouterApp, model_cfgapplication.CfgApplication):
      ProgrammError("First parameter should be CfgApplication or string, name of Router Server")
    self.BeginChange()
    userProperties = self.userProperties
    routerName = cfgRouterApp.name
    if userProperties and userProperties.has_key(str(routerName)):
      del userProperties[str(routerName)]
      self.userProperties = userProperties
      newObject = self.fromPythonObjectToString()
      self.EndChange()

    if not firstTime:
      return
    else:
      if cfgRouterApp.backupApp:
        self.UnloadStrategy(cfgRouterApp.backupApp, 0)      

  def LoadStrategy(self, cfgRouterApp, scriptName, firstTime = 1):
    """ Load strategy to DN - Universal Routing Server """
    
    if type(cfgRouterApp) == type(""): # appName
      cfgRouterApp = model_cfgapplication.CfgApplication(cfgRouterApp)
    if not isinstance(cfgRouterApp, model_cfgapplication.CfgApplication):
      ProgrammError("First parameter should be CfgApplication or string, name of Router Server")
    self.BeginChange()
    userProperties = self.userProperties
    routerName = cfgRouterApp.name
    if userProperties == None:
      userProperties = {}
    opts = {"Loaded by": "default", "strategy": scriptName, "event_arrive": "routerequest",
            "Loaded": time.strftime("%c",time.localtime(time.time()))}
    userProperties[routerName] = opts
    self.userProperties = userProperties
    self.EndChange()
    if not firstTime:
      return
    else:
      if cfgRouterApp.backupApp:
        self.LoadStrategy(cfgRouterApp.backupApp, scriptName, 0)
 
  def LoadXStrategy(self, url, other = {}):
    """ Load scxml strategy to DN - Universal Routing Server """
    self.BeginChange()
    userProperties = self.userProperties
    if userProperties == None:
      userProperties = {}
    opts = {"url": url}
    if other:
      for key in other:
        opts[key] = other[key]
    userProperties["xstrategy"] = opts
    self.userProperties = userProperties
    self.EndChange()

  def UnloadXStrategy(self):
    """ Unload scxml strategy from DN - Universal Routing Server """
    self.BeginChange()
    userProperties = self.userProperties
    if userProperties and userProperties.has_key("xstrategy"):
      del userProperties["xstrategy"]
      self.userProperties = userProperties
      self.EndChange()
   
  def LoadXOStrategy(self, url, other = {}):
    """ Load scxml strategy to DN - Orchestration Server """
    self.BeginChange()
    userProperties = self.userProperties
    if userProperties == None:
      userProperties = {}
    opts = {"application": url}
    if other:
      for key in other:
        opts[key] = other[key]
    userProperties["Orchestration"] = opts
    self.userProperties = userProperties
    self.EndChange()

  def UnloadXOStrategy(self):
    """ Unload scxml strategy from DN - Orchestration Server """
    self.BeginChange()
    userProperties = self.userProperties
    if userProperties and userProperties.has_key("Orchestration"):
      del userProperties["Orchestration"]
      self.userProperties = userProperties
      self.EndChange()

 
  def processCFGObjectInfoChanged(self, ev):
    CfgObject.processCFGObjectInfoChanged(self, ev)
    if self.changed:
      if self.pyObjs:
        for pyObj in self.pyObjs:
          if hasattr(pyObj, "CfgDNChanged"):
            pyObj.CfgDNChanged()
          
    
    
class _CfgDN(CfgDN):
  def __init__(self, DBID = 0, cfgServer = None):
    self.objType = CfgObjectType.CFGDN
    filter = {}
    if DBID: filter = {"dbid": DBID }
    CfgObject.__init__(self, self.objType, filter, cfgServer)
    self.title = "CfgDN"

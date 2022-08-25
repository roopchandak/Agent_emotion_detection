#
#                  === CfgApplication model ===
#
#

from common            import *
from common_enum       import *
from enum              import *
from model_cfgobject   import *
import model
import os
import copy

try:
  import connector
except:
  pass


#==================================================================================
class CfgApplication(CfgObject):
  """ CfgApplication object
  Fields:
    DBID                    - Int
    name                    - Char
    password                - Char
    type                    - Int
    version                 - Char
    appServerDBIDs          - ListOfStructs_CfgConnInfo
    tenantDBIDs             - DBIDList
    isServer                - Int
    serverInfo              - Struct_CfgServerInfo
    options                 - KVList
    state                   - Int
    userProperties          - KVList
    appPrototypeDBID        - Int
    flexibleProperties      - KVList
    workDirectory           - Char
    commandLine             - Char
    autoRestart             - Int
    startupTimeout          - Int
    shutdownTimeout         - Int
    redundancyType          - Int
    isPrimary               - Int
    startupType             - Int
    commandLineArgument     - Char
    portInfos               - ListOfStructs_CfgPortInfo
    resources               - ListOfStructs_CfgObjectResource
    componentType           - Int
  """
  fields =       (("DBID",               "DBID"),
                 ("name",                "Char"),
                 ("password",            "Char"),
                 ("type",                "Int"),
                 ("version",             "Char"),
                 ("appServerDBIDs",      "ListOfStructs_CfgConnInfo"),
                 ("tenantDBIDs",         "DBIDList"),
                 ("isServer",            "Int"),
                 ("serverInfo",          "Struct_CfgServerInfo"),
                 ("options",             "KVList"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("appPrototypeDBID",    "Int"),
                 ("flexibleProperties",  "KVList"),
                 ("workDirectory",       "Char"),
                 ("commandLine",         "Char"),
                 ("autoRestart",         "Int"),
                 ("startupTimeout",      "Int"),
                 ("shutdownTimeout",     "Int"),
                 ("redundancyType",      "Int"),
                 ("isPrimary",           "Int"),
                 ("startupType",         "Int"),
                 ("commandLineArguments","Char"),
                 ("portInfos",           "ListOfStructs_CfgPortInfo"),
                 ("resources",           "ListOfStructs_CfgObjectResource"),
                 ("componentType",       "Int"))
                 
  toXmlTranslation = {"serverInfo": "CfgServerInfo", }                 
  fromXmlTranslation = {"CfgServerInfo": "serverInfo"}    
                 
  requiredFields = ["name"] #much more...                  
  def __init__(self, name = None, backup = None, appType = "Other",
              logFileDir = "",  cfgServer = None, strObj = None): 
    self.objType = CfgObjectType.CFGApplication
    self.appType = appType
    self.pyApp = None
    self.logFileDir = logFileDir
    self.logFileName = ""
    self.backupApp = None
    filter = {}
    if name:
      filter = {"name" : name }
     
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)  
    self.cfgHost = None

    if self.serverInfo and self.serverInfo.hostDBID:
      hostDBID = self.serverInfo.hostDBID
      #self.Host = self.cfgServer.GetObjectCharPropertyByObjectTypeAndDBID("name", CfgObjectType.CFGHost, self.serverInfo.hostDBID)
 
      #self.IPaddress = self.cfgServer.GetObjectCharPropertyByObjectTypeAndDBID("IPaddress", CfgObjectType.CFGHost, self.serverInfo.hostDBID)
      self.Port = self.serverInfo.port
      self.cfgHost = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGHost, hostDBID)
      self.Host = self.cfgHost.name
      self.IPaddress = self.cfgHost.IPaddress
       
      #self.cfgHost = CfgHost(self.Host, cfgServer = cfgServer) 
    else:
      self.Host = None
      self.Port = None
      self.IPaddress = None
    
    self.isPrim = 1

    backup = self.GetBackup()
    if not backup:
      backup = self.GetPrim()
      if backup:
        self.isPrim = 0 # self is backup
    self.SetBackup(backup)

    self.title = "CfgApplication"       

    for server in model.ServerContainer():
      if server.cfgApp and server.cfgApp.DBID == self.DBID:
        self.SetPyApp(server)
        break
    if not self.pyApp:
      backup = self.FindPrim()
      if not backup:
        backup = self.FindBackup()
      if backup and backup.pyApp:
        self.pyApp = backup.pyApp
        backup.pyApp.cfgBackupApp = self

    self.oldOptionsForLinkDisconnect = None
    self.cfgProxy = None

    self.connectorApp = None
    self.connectorController = None # initialized only together with connectorApp

    self.connectedToTheMessageServer = 0
    self.ignoreAsClient = 0



   
  def SetBackup(self, cfgBackupApp = None):
    """ Set backup for application
    Parameters:
      cfgBackupApp - CfgApplication object
    """
    self.backupApp = cfgBackupApp
    if cfgBackupApp:
      cfgBackupApp.backupApp = self  #cross reference

  def SetPyApp(self, pyApp):
    if pyApp:
      self.pyApp = pyApp
      pyApp.cfgApp = self
      pyApp.serverInfo = (self.Host, self.Port)
      pyApp.Host = self.Host
      pyApp.Port = self.Port
      if not pyApp.appType:
        pyApp.appType = self.appType
      if not pyApp.appGCTIType:
        pyApp.appGCTIType = self.appType
      
      if self.backupApp:
        self.backupApp.pyApp = pyApp
        pyApp.cfgBackupApp = self.backupApp
      #try to set options read from config server
      if self.options:
        for section in self.options.keys():
          if not section[0] == '#': #do not look for commented sections
            for option in self.options[section].keys():
              if hasattr(self.pyApp, option) or hasattr(self.pyApp, option.replace("-","_")):
                if self.pyApp.optionsCaseSensitive:
                  val = self.options[section][option]
                else:
                  val = self.options[section][option].lower()
                if InTrue(val) : val = "1"                        #for consistency
                if InFalse(val): val = "0"
                setattr(self.pyApp, option.replace("-","_"), val)
                self.pyApp.translateOption(option.replace("-","_"))
                PrintLog("\n%s option %s set to %s"%(pyApp.appType, option.replace("-","_"), str(val)))
            
      if self.logFileDir:      
        pyApp.logFileDir, pyApp.logFileName = self.logFileDirAndName()

      
  def Delete(self):
    CfgObject.Delete(self)
    if self.scsObj and not self.exists and self.scsObj in self.scsObj.scServer.ObjectList:
      self.scsObj.scServer.ObjectList.remove(self.scsObj)
      
  def logFileDirAndName(self):

    verbose = ""
    fileName = ""
    dir = ""  
    good = 0
    segment = ""
    buffering = "on"
    for sect in self.options.keys():
      if sect.lower() == "log":
        for optName in self.options[sect].keys():
          if optName.lower() == "verbose":
            verbose = self.options[sect][optName]

          elif optName.lower() == "segment":     
            segment = self.options[sect][optName]
            segment = segment.lower()
            
          elif optName.lower() == "buffering":     
            buffering = self.options[sect][optName]
            buffering = buffering.lower()

        if buffering in ("off", "false", "0", "no") and \
          segment in ("", "false", "off", "0", "no"):
          good = 1


        
        if verbose and good:
          fileName = None
          for optName in self.options[sect].keys():
            if optName.lower() == verbose:  
              allValues = self.options[sect][optName].split(",")
              for opt in allValues:
                if opt.lower() not in ["stderr", "network", "stdout", "syslog"]:
                  fileName = opt.strip()
                  break
            if fileName: break
        else:
          ProgrammError("Incorrect log options for application %s" %self.name,
                        " To cut log files option verbose must be specified,\n segment - must be absent or empty,\n buffering - must be \"off\"" )
        break       
    if fileName:
      dir, self.logFileName = os.path.split(fileName)

    return self.logFileDir, self.logFileName

  def GetSwitchFromTserver(self):
    """ Return CfgSwitch """
    if self.type != CfgAppType.CFGTServer:
      ProgrammWarning("Incorrect app type to get switch")
      return
    switchDBID = 0
    if self.flexibleProperties and self.flexibleProperties.has_key('CONN_INFO'):
      conn_info = self.flexibleProperties['CONN_INFO']
      if conn_info and conn_info.has_key("CFGSwitch"):
        switchDBIDs = conn_info["CFGSwitch"].keys()
        switchDBID = switchDBIDs[0]
    if switchDBID:
      switchDBID = int(switchDBID)

      cfgSwitch = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGSwitch, switchDBID)
      return cfgSwitch
    else:
      ProgrammError("No switch assigned to tserver %s" %self.name)

  def GetSwitchTypeFromTserver(self):
    """ Return switch type """
    cfgSwitch = self.GetSwitchFromTserver()
    if cfgSwitch:
      cfgSwitchType = self.cfgServer.GetObjectIntPropertyByObjectTypeAndDBID("type", CfgObjectType.CFGPhysicalSwitch, cfgSwitch.physSwitchDBID)
      return cfgSwitchType
   
   
   
  def processCFGObjectInfoChanged(self, ev):
    if GetOption("PrintConfigDebugInfo"):
      self.printLog(ev)  
    if self.GetInfo(): #object might be already deleted
      self.printLog("Object %s changed %s" % (self.title, self.shortRepr()))
      self.changed = 1
      if self.pyApp:
        if self.pyApp.cfgApp.DBID == self.DBID: # do not do it on backup
          self.SetPyApp(self.pyApp) 

  def AddOption(self, section, key, value, annex = 0, inBackupToo = 1):
    """ Add option to the application
    Parameters:
      section     - Char
      key         - Char
      value       - Char
      annex       - int
      inBackupToo - int
    Example:
      cfgScript.AddOption("Queue", "Persistent", "false", 1)
    """
    if self.oldOptionsForLinkDisconnect:
      ProgrammError("No changing options allowed before link is reconnected")
    CfgObject.AddOption(self, section, key, value, annex)
    if self.backupApp and inBackupToo: #to avoid dead loops because of cross references
      self.backupApp.AddOption(section, key, value, annex, 0)
    if self.pyApp:
      if hasattr(self.pyApp, key.replace("-","_")):
        sec = dicGetKeyNoCase(self.options, str(section))
        setattr(self.pyApp, key.replace("-","_"), self.options[sec][key]) 
        self.pyApp.translateOption(key.replace("-","_"))
        
        
  def ChangeOption(self, section, key, value, annex = 0, inBackupToo = 1): 
    """ Change option in application
    Parameters:
      section     - Char
      key         - Char
      value       - Char
      annex       - int
      inBackupToo - int
    Example:
      cfgScript.ChangeOption("Queue", "Persistent", "true", 1)
    """
    if self.oldOptionsForLinkDisconnect:
      ProgrammError("No changing options allowed before link is reconnected")  
    CfgObject.ChangeOption(self, section, key, value, annex)
    if self.backupApp and inBackupToo: #to avoid dead loops because of cross references
      self.backupApp.ChangeOption(section, key, value, annex, 0)    
    if self.pyApp and self.pyApp.cfgApp.DBID == self.DBID:
      if hasattr(self.pyApp, key.replace("-","_")):
        sec = dicGetKeyNoCase(self.options, str(section))
        setattr(self.pyApp, key.replace("-","_"), self.options[sec][key]) 
        self.pyApp.translateOption(key.replace("-","_"))
        
  def DeleteOption(self, section, key, annex = 0, inBackupToo = 1):  
    """ Delete option from application
    Parameters:
      section     - Char
      key         - Char
      annex       - int
      inBackupToo - int
    Example:
      cfgScript.DeleteOption("Queue", "Persistent", 1)
    """
    if self.oldOptionsForLinkDisconnect:
      ProgrammError("No changing options allowed before link is reconnected")  
    CfgObject.DeleteOption(self, section, key, annex)
    if self.backupApp and inBackupToo: #to avoid dead loops because of cross references
      self.backupApp.DeleteOption(section, key, annex, 0)        
    if self.pyApp:
      if hasattr(self.pyApp, key.replace("-","_")):
        self.pyApp.setDefaultOptionValue(key.replace("-","_"))

  def DeleteSection(self, section, annex = 0, inBackupToo = 1):  
    """ Delete section from application
    Parameters:
      section     - Char
      annex       - int
      inBackupToo - int
    Example:
      cfgScript.DeleteSection("Queue", 1)
    """
    if self.oldOptionsForLinkDisconnect:
      ProgrammError("No changing options allowed before link is reconnected")  
    if not annex:
      options = self.options
    else:
      options = self.userProperties
    if not options or not options.has_key(section):
      ProgrammWarning(" Section " + str(section) + " is not found")
      return

    if self.pyApp:
      for key in self.options[section].keys():
        if hasattr(self.pyApp, key.replace("-","_")):
          self.pyApp.setDefaultOptionValue(key.replace("-","_"))
    CfgObject.DeleteSection(self, section, annex)
    if self.backupApp and inBackupToo:
      self.backupApp.DeleteSection(section, annex, 0)         

  def SetRedundancyType(self, redType = CfgHAType.CFGHTColdStanby):
    """ Set redundancy type
    Parameters:
      redType     - Int
    """
    self.printLog("Application %s, set redundancy type %s" %(self.name, redType))
    #Some addtional verifications"
    if self.backupApp:
      if ((self.redundancyType == CfgHAType.CFGHTWarmStanby or self.redundancyType == CfgHAType.CFGHTHotStanby) 
          and redType == CfgHAType.CFGHTColdStanby):
        ProgrammError("Redundancy type  cannot be changed from WarmStandBy/HotStandBy to ColdStandBy",
                      "You have to remove backup first. Application %s " %self.name)
    else:
      if (redType == CfgHAType.CFGHTWarmStanby or redType == CfgHAType.CFGHTWarmStanby): 
        ProgrammError("Backup is not configured for application %s (at least it is absent in Python configuration)" %self.name,
                      "Redundancy type  cannot be changed to WarmStandBy/HotStandBy")
    
    if self.scsObj and self.scsObj.status != AppLiveStatus.SCS_APP_STATUS_STOPPED:
      ProgrammError("Application %s should be stopped before changing redundancy type" %self.name)
    if self.backupApp and self.backupApp.scsObj and self.backupApp.scsObj.status != AppLiveStatus.SCS_APP_STATUS_STOPPED:
      ProgrammError("Application %s should be stopped before changing redundancy type" %self.backupApp.name)
    if self.isPrimary != CfgFlag.True.val:
      ProgrammError("Application %s is not primary,redundancy type cannot be changed" %self.name)
    self.BeginChange()  
    self.redundancyType = redType.val
    self.EndChange() 
    #if self.backupApp:  # config server will change redundancyType in backup automatically, we just need to update our object
    #  self.backupApp.redundancyType = redType
    

  def AddConnectionDBID(self, appServerDBID, connProtocol = "", \
                              timoutLocal = 0, timoutRemote = 0, traceMode = 0,
                              id = "", transportParams = "", appParams = "", proxyParams = ""):
    found = 0
    if self.appServerDBIDs:
      for conn in self.appServerDBIDs:
        if conn.appServerDBID == appServerDBID:
          found = 1
          break
    if not found:
      self.BeginChange()
      if self.appServerDBIDs == None: self.appServerDBIDs = []    
      conn = CfgConnInfo()
      conn.appServerDBID = appServerDBID
      conn.connProtocol = connProtocol
      conn.timoutLocal = timoutLocal
      conn.timoutRemote = timoutRemote
      conn.traceMode = traceMode      
      conn.id = id
      conn.transportParams = transportParams
      conn.appParams = appParams
      conn.proxyParams = proxyParams      
      self.appServerDBIDs.append(conn)
      self.EndChange()
      if self.backupApp:
        self.backupApp.GetInfo()
    else:
      ProgrammWarning("AddConnectionDBIDTo: Connection to server with DBID " + str(appServerDBID) + " already exists" )
      
  def ChangeConnectionDBIDParams(self, appServerDBID, connProtocol = None, timoutLocal = None, timoutRemote = None, \
                      traceMode = None, id = None, transportParams = None, appParams = None, proxyParams = None):
    found = 0
    if self.appServerDBIDs:
      for conn in self.appServerDBIDs:
        if conn.appServerDBID == appServerDBID:
          found = 1
          break
    if not found:
      ProgrammWarning("ChangeConnectionDBIDParams: Connection to server with DBID " + str(appServerDBID) + " does not exists" )
      return
    self.BeginChange()
    if connProtocol <> None:
      conn.connProtocol = connProtocol
    if timoutLocal <> None:
      conn.timoutLocal = timoutLocal
    if timoutRemote <> None:
      conn.timoutRemote = timoutRemote
    if traceMode <> None:
      conn.traceMode = traceMode
    if id <> None:
      conn.id = id
    if transportParams <> None:
      conn.transportParams = transportParams      
    if appParams <> None:
      conn.appParams = appParams      
    if proxyParams <> None:
      conn.proxyParams = proxyParams              
    self.EndChange()

  def DeleteConnectionDBID(self, appServerDBID):
    removed = 0
    self.BeginChange()
    if self.appServerDBIDs:
      for conn in self.appServerDBIDs:
        if conn.appServerDBID == appServerDBID:
          self.appServerDBIDs.remove(conn)
          if self.appServerDBIDs == []:
            self.appServerDBIDs = None          
          self.EndChange()
          if self.backupApp:
            self.backupApp.GetInfo()
          removed = 1
          break
    if not removed:
      ProgrammWarning("Server with DBID " + str(appServerDBID) + " is not found" )
     
  def GetConnectionDBIDs(self):
    """Return list of server(connections) DBIDs"""
    dbids = []
    if self.appServerDBIDs:
      for conn in  self.appServerDBIDs:
        dbids.append(conn.appServerDBID)
    return dbids
  
  def AddConnection(self, cfgApp, connProtocol = "", timoutLocal = 0, timoutRemote = 0, traceMode = 0, 
                      id = "", transportParams = "", appParams = "", proxyParams = ""  ):
    """Add connection to cfgApp with specified params. if id  == "", default is used by CS"""
    self.AddConnectionDBID(cfgApp.DBID, connProtocol, timoutLocal, timoutRemote, traceMode, \
                              id, transportParams, appParams, proxyParams) 
  
  def ChangeConnectionParams(self, cfgApp, connProtocol = None, timoutLocal = None, timoutRemote = None,
                      traceMode = None, id = None, transportParams = None, appParams = None, proxyParams = None):
    """Change connection params, connection to cfgApp must exist. change only params <> None"""                  
    self.ChangeConnectionDBIDParams(cfgApp.DBID, connProtocol, timoutLocal, timoutRemote, traceMode, \
                              id, transportParams, appParams, proxyParams) 

      
    
  def DeleteConnection(self, cfgApp):
    """ Delete connection """
    self.DeleteConnectionDBID(cfgApp.DBID)
    
      
  def DisconnectLinksByChangingOptions(self, port = None):
    if self.type == CfgAppType.CFGTServer:
      self.BeginChange()  
      self.oldOptionsForLinkDisconnect = copy.deepcopy(self.options)
      self.printLog("Trying to disconnect link by changing link options for application %s" %self.name)
      found = 0
      sec = dicGetKeyNoCase(self.options, "tserver")
      print sec
      if sec:
        pat = "link-[0-9]+-name"
        for optName in self.options[sec].keys():
          if re.search(pat, optName):
            linkSectionName = self.options[sec][optName]
            if self.options.has_key(linkSectionName):
              linkSection = self.options[linkSectionName]
              if linkSection.has_key("port"):
                found = 1
                if port:
                  linkSection["port"] = str(port)
                else:
                  linkSection["port"] = "0"
                self.options[linkSectionName] = linkSection
      if not found:
        ProgrammWarning("DisconnectLinksByChangingOptions cannot be completed.\nApplication options are not in required format link-n-name/port. Make sure it is TCP connection")
        self.oldOptionsForLinkDisconnect = None
        return
      self.EndChange() 
      
      if self.pyApp:
        self.pyApp.LinkDisconnected()


      
  def ReconnectLinksByChangingOptions(self):
    if self.type == CfgAppType.CFGTServer:
      self.printLog("Trying to reconnect link by changing link options for application %s" %self.name)
   
      if not self.oldOptionsForLinkDisconnect:
        ProgrammWarning("Link was not previously disconnected")
        return
      self.BeginChange()  
      self.options = self.oldOptionsForLinkDisconnect
      self.oldOptionsForLinkDisconnect = None
      self.EndChange()      
      if self.pyApp:
        time.sleep(8)
        self.pyApp.LinkReconnected()
          
  def GetAllClients(self, exclude=[]):
    """ Return all application clients
    Parameters:
      exclude     - List
    """
    clients = []
    filtr = {"server_dbid" : self.DBID}   
    objects = self.cfgServer.GetObjectInfo(CfgObjectType.CFGApplication, filtr) 
    
    for strObj in objects:
      dbid = self.cfgServer.GetObjectDBIDFromString(strObj)
      cfgApp = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid) 
      if cfgApp.name not in exclude:  
        clients.append(cfgApp)
    return clients  
    
  def GetAllClientsListedInQaart(self, exclude = []): 
    clients = []
    filtr = {"server_dbid" : self.DBID}   
    objects = self.cfgServer.GetObjectInfo(CfgObjectType.CFGApplication, filtr) 
    
    for strObj in objects:
      dbid = self.cfgServer.GetObjectDBIDFromString(strObj)
      cfgApp = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid) 
      for serv in model.ServerContainer():
        if serv.cfgApp and serv.cfgApp.DBID == cfgApp.DBID and cfgApp.name not in exclude:  
          clients.append(cfgApp)
          if cfgApp.backupApp: clients.append(cfgApp.backupApp)
    return clients     
  
  
  def GetAllClientsForDBServerListedInQaart(self, exclude = []): 
    clients = []
    filtr = {"server_dbid" : self.DBID}   
    objects = self.cfgServer.GetObjectInfo(CfgObjectType.CFGApplication, filtr) #all DAPs
    
    for strObj in objects:
      dbid = self.cfgServer.GetObjectDBIDFromString(strObj)
      cfgApp = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid) 
      assert(cfgApp.type == CfgAppType.CFGDBServer) #DAP
      #cfgApp is DAP. lets find all clients listed in qaart for this DAP
      realClients = cfgApp.GetAllClientsListedInQaart(exclude) #DAP clients
      for realClient in realClients:
        for serv in model.ServerContainer():
          if serv.cfgApp and serv.cfgApp.DBID == realClient.DBID and realClient.name not in exclude:  
            if realClient not in clients:
              clients.append(realClient)
              if realClient.backupApp: clients.append(realClient.backupApp)
    return clients     
  
  def GetAllDAPClientsForDBServerListedInQaart(self, exclude = []): 
    clients = []
    filtr = {"server_dbid" : self.DBID}   
    objects = self.cfgServer.GetObjectInfo(CfgObjectType.CFGApplication, filtr) #all DAPs
    
    for strObj in objects:
      dbid = self.cfgServer.GetObjectDBIDFromString(strObj)
      cfgApp = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid) 
      assert(cfgApp.type == CfgAppType.CFGDBServer) #DAP
      #cfgApp is DAP. lets find all clients listed in qaart for this DAP
      realClients = cfgApp.GetAllClientsListedInQaart(exclude) #DAP clients
      for realClient in realClients:
        for serv in model.ServerContainer():
          if serv.cfgApp and serv.cfgApp.DBID == realClient.DBID and realClient.name not in exclude:  
            if cfgApp not in clients:
              clients.append(cfgApp)
              if cfgApp.backupApp: clients.append(cfgApp.backupApp)
    return clients 
    

  def GetServers(self): # Connections
    """ Return server list """
    servers = []
    connectionDBIDs = self.GetConnectionDBIDs()
    for dbid in connectionDBIDs:
      cfgApp = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid)    
      servers.append(cfgApp) 
    return servers

  def GetBackup(self):
    """ Return backup application """
    if self.serverInfo and self.serverInfo.backupServerDBID:  
      #Get backup server from Configuration Server
      backup = self.cfgServer.GetObjectByTypeAndDBID(
                      CfgObjectType.CFGApplication,
                      self.serverInfo.backupServerDBID)
      return backup
      
  def FindBackup(self):
    """ Return backup application """
    if self.serverInfo and self.serverInfo.backupServerDBID:  
      #Find backup server from Configuration Server
      backup = self.cfgServer.FindObjectByTypeAndDBID(
                      CfgObjectType.CFGApplication,
                      self.serverInfo.backupServerDBID)
      return backup


      
  def GetPrim(self):
    """ Return primary application """
    filtr = {"backup_server_dbid" : self.DBID}
    strObjList = self.cfgServer.GetObjectInfo(CfgObjectType.CFGApplication, filtr)
    prim = None
    for strObj in strObjList:
      dbid = self.cfgServer.GetObjectDBIDFromString(strObj)
      prim = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid) 
      return prim

  def FindPrim(self):
    """ Return primary application """
    filtr = {"backup_server_dbid" : self.DBID}
    strObjList = self.cfgServer.GetObjectInfo(CfgObjectType.CFGApplication, filtr)
    prim = None
    for strObj in strObjList:
      dbid = self.cfgServer.GetObjectDBIDFromString(strObj)
      prim = self.cfgServer.FindObjectByTypeAndDBID(CfgObjectType.CFGApplication, dbid) 
      return prim

  def DisconnectFromPrim(self):
    """ Set backup field of application to 0 """
    prim = self.GetPrim()
    if prim:
      prim.BeginChange()
      prim.serverInfo.backupServerDBID = 0
      prim.EndChange()
    return prim

  def ReconnectPrim(self, prim):
    """ Set backup field of application to the backup application DBID """
    if prim:
      prim.BeginChange()
      prim.serverInfo.backupServerDBID = self.DBID
      prim.EndChange()

  
  
  def DisconnectAllClientsDBserver(self, exclude = []):
    """Removes this server from all the connections - DAP"""
  
    clients = self.GetAllClients(exclude)  
   
    clientConnectionList = []
    for client in clients:
      client.BeginChange()
      servers = client.appServerDBIDs
      ind = 0
      savedConn = None
      for conn in servers:
        if conn.appServerDBID == self.DBID:
          savedConn = copy.copy(conn)
          break
        ind = ind + 1 
      del servers[ind]  
      client.serverInfo = None
      #if client.portInfos and len(client.portInfos):
      #  del client.portInfos[0]
      clientConnectionList.append((client, savedConn))
      client.EndChange()
    return clientConnectionList
    
  def DisconnectAllClientsDBserverListedInQaart(self, exclude = []):
    """Removes this server from all the connections - DAP, listed in qaart"""
  
    clients = self.GetAllDAPClientsForDBServerListedInQaart(exclude)  

    clientConnectionList = []
    for client in clients:
      client.BeginChange()
      servers = client.appServerDBIDs
      ind = 0
      savedConn = None
      for conn in servers:
        if conn.appServerDBID == self.DBID:
          savedConn = copy.copy(conn)
          break
        ind = ind + 1 
      del servers[ind]  
      client.serverInfo = None

      clientConnectionList.append((client, savedConn))
      client.EndChange()
    return clientConnectionList    


  def ReconnectClientsDBserver(self, clientConnectionList):
    for clientConnection in clientConnectionList:
      client, connection = clientConnection
      client.BeginChange()
      if not client.appServerDBIDs:
        client.appServerDBIDs = []
      client.appServerDBIDs.append(connection)
      client.serverInfo = self.serverInfo
      client.portInfos[0] = self.portInfos[0]
      client.EndChange()

  
  def DisconnectAllClientsListedInQaart(self, exclude = []): 
    """Removes this server from the connections listed in qaart"""
    if self.type == CfgAppType.CFGRealDBServer:
      return self.DisconnectAllClientsDBserverListedInQaart(exclude)
    clients = self.GetAllClientsListedInQaart(exclude)    
    # Remove all backup server from clients, it is supposed that if we remove  connection in
    # prime application it is automattically removed from backup application
    backupDBIDList = []
    for client in clients:
      if client.serverInfo and client.serverInfo.backupServerDBID:
        backupDBIDList.append(client.serverInfo.backupServerDBID)
    if backupDBIDList:
      clientsCopy = copy.copy(clients)
      for client in clientsCopy:
        if client.DBID in backupDBIDList: 
          clients.remove(client)
    clientConnectionList = []
    for client in clients:
      client.BeginChange()
      servers = client.appServerDBIDs
      ind = 0
      savedConn = None
      for conn in servers:
        if conn.appServerDBID == self.DBID:
          savedConn = copy.copy(conn)
          break
        ind = ind + 1 
      del servers[ind]  
      clientConnectionList.append((client, savedConn))

      client.EndChange()
      
    return clientConnectionList          
  
  
  def DisconnectAllClients(self, exclude = []): 
    """Removes this server from all the connections"""
    if self.type == CfgAppType.CFGRealDBServer:
      return self.DisconnectAllClientsDBserver(exclude)
    clients = self.GetAllClients(exclude)    
    # Remove all backup server from clients, it is supposed that if we remove  connection in
    # prime application it is automattically removed from backup application
    backupDBIDList = []
    for client in clients:
      if client.serverInfo and client.serverInfo.backupServerDBID:
        backupDBIDList.append(client.serverInfo.backupServerDBID)
    if backupDBIDList:
      clientsCopy = copy.copy(clients)
      for client in clientsCopy:
        if client.DBID in backupDBIDList: 
          clients.remove(client)
    
    clientConnectionList = []
    for client in clients:
      client.BeginChange()
      servers = client.appServerDBIDs
      ind = 0
      savedConn = None
      for conn in servers:
        if conn.appServerDBID == self.DBID:
          savedConn = copy.copy(conn)
          break
        ind = ind + 1 
      del servers[ind]  
      clientConnectionList.append((client, savedConn))

      client.EndChange()
      
    return clientConnectionList


          
  def ReconnectClients(self, clientConnectionList):
    if self.type == CfgAppType.CFGRealDBServer:
      return self.ReconnectClientsDBserver(clientConnectionList)
  
    for clientConnection in clientConnectionList:
      client, connection = clientConnection
      client.BeginChange()
      if not client.appServerDBIDs:
        client.appServerDBIDs = []
      client.appServerDBIDs.append(connection)
      client.EndChange()


  def ChangeHost(self, newHostName):
    """ Change application host by name
    Parameters:
      newHostName     - Char
    """
    filtr = {"name" : newHostName.lower()}
    newHostDBID = self.cfgServer.GetObjectDBID(CfgObjectType.CFGHost, filtr)
    self.ChangeHostDBID(newHostDBID)
    self.Host = newHostName
    self.IPaddress = self.cfgServer.GetObjectCharPropertyByObjectTypeAndDBID("IPaddress", CfgObjectType.CFGHost, self.serverInfo.hostDBID)
    self.cfgHost = CfgHost(self.Host)     


    
  def ChangeHostDBID(self, newHostDBID):
    """ Change application host by DBID
    Parameters:
      newHostDBID     - Int
    """
    prim = self.DisconnectFromPrim()
    clientConnectionList = self.DisconnectAllClients()
    self.BeginChange()
    self.serverInfo.hostDBID = newHostDBID
    self.EndChange()  
    self.ReconnectClients(clientConnectionList)
    self.ReconnectPrim(prim)
    
  def ChangePort(self, newPort):
    """ Change application host by DBID
    Parameters:
      newPort     - Int
    """
    prim = self.DisconnectFromPrim()
    clientConnectionList = self.DisconnectAllClients() 

    self.BeginChange()
    self.serverInfo.port = newPort
    self.EndChange() 
    self.Port = newPort
    self.ReconnectClients(clientConnectionList)
    self.ReconnectPrim(prim)
    
    

  def AddPortInfo(self, portId, port, transportParams = "", connProtocol = "", 
                  appParams = "", description = "", charField1 = "", charField2 = "",
                  charField3 = "", charField4 = "", longField1 = 0,
                  longField2 = 0, longField3 = 0, longField4 = 0):
    if self.portInfos:
      for portInfo in self.portInfos:
        if portInfo.id == portId:
          ProgrammWarning("AddPortInfo: port id " + portId + " already exists")
          return
    prim = self.DisconnectFromPrim()
    clientConnectionList = self.DisconnectAllClients()          
    self.BeginChange()
    newPortInfo = CfgPortInfo()
    newPortInfo.id = portId
    newPortInfo.port = str(port)
    newPortInfo.transportParams = transportParams
    newPortInfo.connProtocol = connProtocol
    newPortInfo.appParams = appParams
    newPortInfo.description = description
    newPortInfo.charField1 = charField1
    newPortInfo.charField2 = charField2
    newPortInfo.charField3 = charField3
    newPortInfo.charField4 = charField4
    newPortInfo.longField1 = longField1
    newPortInfo.longField2 = longField2
    newPortInfo.longField3 = longField3
    newPortInfo.longField4 = longField4
    if not self.portInfos: self.portInfos = []
    self.portInfos.append(newPortInfo)
    self.EndChange() 
    self.ReconnectClients(clientConnectionList)
    self.ReconnectPrim(prim)
    
  def DeletePortInfo(self, portId):
    portInfoToDelete = None
    if self.portInfos:
      for portInfo in self.portInfos:
        if portInfo.id == portId:
          portInfoToDelete = portInfo
          break
    if not portInfoToDelete:
      ProgrammWarning("DeletePortInfo: port id " + portId + " does not exist")
      return
    self.BeginChange()
    self.portInfos.remove(portInfoToDelete)
    self.EndChange()    

  def ChangePortInfo(self, portId = "default", newPort = None, transportParams = None, connProtocol = None,
                    appParams = None, description = None, charField1 = None, charField2 = None,
                    charField3 = None, charField4 = None, longField1 = None,
                    longField2 = None, longField3 = None, longField4 = None):

    portInfoToChange = None
    portInfos = self.portInfos
    for portInfo in portInfos:
      if portInfo.id == portId:
        portInfoToChange = portInfo
        break
    if not portInfoToChange:
      ProgrammWarning("ChangePortInfo: port id " + portId + " is not found")
      return

    prim = self.DisconnectFromPrim()
    clientConnectionList = self.DisconnectAllClients() 

    self.BeginChange()
    if newPort <> None:
      portInfoToChange.port = str(newPort)
    if transportParams <> None:
      portInfoToChange.transportParams = transportParams
    if connProtocol <> None:
      portInfoToChange.connProtocol = connProtocol
    if appParams <> None:
      portInfoToChange.appParams = appParams
    if description <> None:
      portInfoToChange.description = description      
    if charField1 <> None:
      portInfoToChange.charField1 = charField1
    if charField2 <> None:
      portInfoToChange.charField2 = charField2
    if charField3 <> None:
      portInfoToChange.charField3 = charField3
    if charField4 <> None:
      portInfoToChange.charField4 = charField4    
    if longField1 <> None:
      portInfoToChange.longField1 = longField1  
    if longField2 <> None:
      portInfoToChange.longField2 = longField2
    if longField3 <> None:
      portInfoToChange.longField3 = longField3
    if longField4 <> None:
      portInfoToChange.longField4 = longField4     
    self.EndChange() 
    self.ReconnectClients(clientConnectionList)
    self.ReconnectPrim(prim)

  def ChangeHostPort(self, newHostName, newPort):
    """ Change host and port of application
    Parameters:
      newHostName       - Char
      newPort           _ Int
    """
    filtr = {"name" : newHostName.lower()}
    newHostDBID = self.cfgServer.GetObjectDBID(CfgObjectType.CFGHost, filtr)
    prim = self.DisconnectFromPrim()
    clientConnectionList = self.DisconnectAllClients() 

    self.BeginChange()
    self.serverInfo.port = newPort
    self.serverInfo.hostDBID = newHostDBID
    self.EndChange()  
    self.Host = newHostName    
    self.Port = newPort
    self.ReconnectClients(clientConnectionList)
    self.ReconnectPrim(prim)
    self.cfgHost = CfgHost(self.Host) 
  

  def getAnexOption(self, folder, optName, exception=1):
    if( self.userProperties and self.userProperties.has_key(folder) and
        self.userProperties[folder].has_key(optName)):

      optVal = self.userProperties[folder][optName]
      optVal = optVal.replace("\\\\", "\\") # In options "\" is represented as "\\" so we removing extra "\"
      return optVal

    elif exception:
      ProgrammError("Error in config server data: option Annex|%s|%s is not defined in application '%s'" %
                    (folder, optName, self.name))
    else:
      return None  

  def getAddpTestOption(self, optName, exception=1):
    if self.userProperties and self.userProperties.has_key("AddpTest") and self.userProperties["AddpTest"].has_key(optName):
      srvName = self.getAnexOption("AddpTest", optName)
      return srvName
      
    elif self.options and self.options.has_key("AddpTest") and self.options["AddpTest"].has_key(optName):
      srvName = self.options["AddpTest"][optName]
      return srvName

    elif exception:
      ProgrammError("Error in config server data: AddpTest|%s is not defined in application '%s'" %
                    (optName, self.name))
    else:
      return None
      
  def getPlatformOptionFromAnex(self, optName, folder=None, useCommon=True, exception=True):
    """Gets option corresponding to some platform from Anex
     Parameters:
        optName   - option name  
        folder    - subfolder in anex, if None then value of field curnConfig
                    in Anex|CommonConfig is used.
        useCommon - if useCommon == false then curnConfig (see above) is not used
        exception - if exception == true then exception is generated when the option
                    or the folder are absent.
    Result:
        option value
    """
      
    if not folder:
      folder = self.getAnexOption("CommonConfig", "curnConfig")
      
    optVal = self.getAnexOption(folder, optName, exception=0)
    if not optVal and useCommon:   
      folder = "CommonConfig"
      optVal = self.getAnexOption(folder, optName, exception=exception)
    return optVal 


  def addConnector(self, backup = 0): 
    """adds the same app with name __Conn__ + name and different port"""
    print "adding connector for %s" %self.name
    assert(self.isServer == CfgFlag.True)
    objListCopy = copy.copy(self.cfgServer.ObjectList)
    connName = "__Conn__" + self.name
    #try to get obj first
    filtr = {"name": connName}
    objects = self.cfgServer.GetObjectInfo( self.objType, filtr)
    if len(objects) == 1: 
      existingApp = CfgApplication(connName)
      existingApp.DisconnectAllClients()
      existingApp.DisconnectFromPrim()
      existingApp.Delete()
    newApp = copy.copy(self)
    newApp.pyApp = None
    newApp.name = connName
    newApp.DBID = 0
    newApp.exists = 0
    oldPort = newApp.serverInfo.port
    portInfoToChange = None
    portInfos = newApp.portInfos

    for portInfo in portInfos:
      if portInfo.id == "default":
        portInfoToChange = portInfo
        break
    if not portInfoToChange:
      ProgrammError("Add Connector: port id default is not found")
      return  
      
    oldPort = portInfoToChange.port
    newPort = str(5000 + int(oldPort))
    portInfoToChange.port = newPort
    newApp.Port = newPort
    
    newApp.serverInfo.backupServerDBID = 0
    #portInfoToChange.transportParams = transportParams
    #if connProtocol:
    #  portInfoToChange.connProtocol = connProtocol
    newApp.appServerDBIDs = []
    newApp.appType = "Other"
    newApp.Add()
    if not backup:
      if self.backupApp:
        backupConnector = self.backupApp.addConnector(backup = 1)
        newApp.BeginChange()
        newApp.serverInfo.backupServerDBID = backupConnector.DBID
        newApp.EndChange()
    self.connectorApp = newApp
    self.cfgServer.ObjectList = objListCopy    
    return newApp
    
  def deleteConnector(self):
    if self.connectorApp:
      self.connectorApp.Delete()
      if self.backupApp and self.backupApp.connectorApp:
        self.backupApp.connectorApp.Delete()
      
    
  def initConnectorController(self):
    if self.type != CfgAppType.CFGConfigurationServer:
      self.connectorController = connector.ConnectorController(self.Host)
    else:
      #checking that all primary clients are running on ONE host (it also must be windows)
      #connect controller to this host using IP address
      if self.isPrim:
        serv = self
      else:
        serv = self.backupApp
      clients = serv.GetAllClientsListedInQaart()
      if not clients:
        if not self.backupApp: ProgrammError("No clients/no backup app for configserver found")
        if self.isPrim:
          self.connectorController = connector.ConnectorController(self.backupApp.IPaddress)
        else:
          self.connectorController = self.backupApp.connectorController
        #ProgrammError("No clients of configserver found")
      else:
        firstHostDBID = None
        for client in clients:
          if client.isPrim:
            if not firstHostDBID: #yet
              firstHostDBID = client.serverInfo.hostDBID
              someClient = client
            else:
              if hostDBID <> firstHostDBID:
                print client
                print clients[0]
              assert(hostDBID == firstHostDBID)
              someClient = client
        if self.backupApp:
          assert(firstHostDBID == self.backupApp.IPaddress) # backup and clients must be on the same host
        assert(someClient.IPaddress)
        self.connectorController = connector.ConnectorController(someClient.IPaddress)


  def insertConnector(self, backup = 0):
    """ Self is a server. Insert self.connectorApp between server and server clients."""
    print "inserting connector for %s" %self.name
    assert(self.connectorApp)   
    assert(self.scsObj)
    self.initConnectorController()
    if not backup and self.backupApp:
      self.backupApp.initConnectorController()
    
    proxyHostName = self.Host  
    proxyPort = self.connectorApp.serverInfo.port
    appPort = self.serverInfo.port
    if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
        
      clientConnectionList = self.DisconnectAllClientsListedInQaart(self.cfgServer.ignoreClientList)
      for client, conn in clientConnectionList:
        conn.appServerDBID = self.connectorApp.DBID
      self.ReconnectClients(clientConnectionList)

    else:
      pass
    self.scsObj.initConnector(backup) #connectorOpenServer is called there
    if not backup:
      if self.backupApp:
   
        self.backupApp.insertConnector(backup = 1)
    
  
  def connectorOpenServer(self):
    if self.connectorApp:
      if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
        serverInfo = (self.Host, self.Port)
        proxyPort = self.connectorApp.serverInfo.port
        self.connectorController.openServer(serverInfo, proxyPort) 
        
      else:
        serverInfo = (self.IPaddress, self.Port)
        proxyPort = self.Port
        if self.isPrim:
          self.connectorController.openServer(serverInfo, proxyPort) 
        
      time.sleep(1)

    
  def connectorCloseServer(self):
    if self.connectorApp and self.connectorController:
      if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
        serverInfo = (self.Host, self.Port)
      else:
        serverInfo = (self.IPaddress, self.Port)
   
      self.connectorController.closeServer(serverInfo) 
      time.sleep(1)

      
  def connectorBreakServer(self):
    if self.connectorApp:
      if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
        serverInfo = (self.Host, self.Port)
      else:
        serverInfo = (self.IPaddress, self.Port)
    
      self.connectorController.breakServer(serverInfo) 
      time.sleep(1)

  def connectorResumeServer(self):
    if self.connectorApp:
      if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
        serverInfo = (self.Host, self.Port)
      else:
        serverInfo = (self.IPaddress, self.Port)
    
      self.connectorController.resumeServer(serverInfo) 
      time.sleep(1)   
    
      
  def connectorTestAndResetServer(self):      
    if self.connectorApp:
      if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
        serverInfo = (self.Host, self.Port)
      else:
        serverInfo = (self.IPaddress, self.Port)
    
      self.connectorController.testAndResetServer(serverInfo) 
      time.sleep(1)   
   
  def removeConnector(self, backup = 0):
    if not self.connectorApp: return
    if self.connectorApp.type != CfgAppType.CFGConfigurationServer:
      clientConnectionList = self.connectorApp.DisconnectAllClientsListedInQaart(self.cfgServer.ignoreClientList)
      for client, conn in clientConnectionList:
        conn.appServerDBID = self.DBID
      self.connectorApp.ReconnectClients(clientConnectionList)   
      if not backup and self.backupApp:
        self.backupApp.removeConnector(backup = 1)
    else:
      pass
        
        
    
    
  def InsertConnector(self):
    """ Self is a Connector. Insert self between server and server clients."""
    
    objListCopy = copy.copy(self.cfgServer.ObjectList)
    srvName = self.getAddpTestOption("serverName") 
      
    srvCfgObj = CfgApplication(srvName, backup=1)           
    if srvCfgObj.type != CfgAppType.CFGConfigurationServer:
      self.ChangeHost(srvCfgObj.Host)
      if self.backupApp and srvCfgObj.backupApp:
          self.backupApp.ChangeHost(srvCfgObj.backupApp.Host)

      ignoreClientsNames = [] 
      ignoreClientsStr = self.getAddpTestOption("ignoreClients", exception=0)
      if ignoreClientsStr:
        for  each in ignoreClientsNames:
          ind = ignoreClientsNames.index(each)
          ignoreClientsNames[ind] = each.strip()
      clientConnectionList = srvCfgObj.DisconnectAllClients(ignoreClientsNames)
      for client, conn in clientConnectionList:
        conn.appServerDBID = self.DBID
      self.ReconnectClients(clientConnectionList)
    self.cfgServer.ObjectList = objListCopy                 

  def RemoveConnector(self):
    srvName = self.getAddpTestOption("serverName") 
    
    objListCopy = copy.copy(self.cfgServer.ObjectList)
    srvCfgObj = CfgApplication(srvName)
    self.cfgServer.ObjectList = objListCopy
    
    if srvCfgObj.type != CfgAppType.CFGConfigurationServer:
      clientConnectionList = self.DisconnectAllClients()
      for client, conn in clientConnectionList:
        conn.appServerDBID = srvCfgObj.DBID
      srvCfgObj.ReconnectClients(clientConnectionList)     
      
  def RestoreFromFile(self, saveConfFileName = None):
    """ Restore application from configuration file
    Parameters:
      saveConfFileName      - Char
    """
    if not saveConfFileName:
      saveConfFileName = GetOption("RestoreConfFileName")
    if not saveConfFileName: 
      mess = "Cannot restore application %s, DBID %s. File is not specified" %(self.name, self.DBID)
      self.printLog(mess)
    
      return 0
  
    try:
      saveConfFile = open(saveConfFileName, "r")
    except Exception, mess:
      self.printLog(mess)
      return 0
    try:  
      strCfgApps = saveConfFile.readlines()
    except Exception, mess:
      self.printLog(mess)
      saveConfFile.close()
      return 0
      
    loadedCfgApps = []
    try:
      for strCfgApp in strCfgApps:
        strCfgApp = eval(strCfgApp)
        cfgApp = CfgApplication(strObj = strCfgApp)
        del self.cfgServer.ObjectList[-1] #trick - remove appended object
        loadedCfgApps.append(cfgApp)
    except Exception, m:
      mess = "Cannot restore application %s, DBID %s from file %s.\n%s" %(self.name, self.DBID, saveConfFileName, m)
      self.printLog(mess)
      saveConfFile.close()
      return 0
      
    #try to compare by dbid

    foundInLoaded = 0
    for loadedCfgApp in loadedCfgApps:
      if loadedCfgApp.DBID == self.DBID:
        foundInLoaded = 1
        
        break
    if not foundInLoaded:
      mess = "Cannot find application %s, DBID %s in file %s" %(self.name, self.DBID, saveConfFileName)
      self.printLog(mess)
      saveConfFile.close()
      return 0

    self.BeginChange()
    self.options = loadedCfgApp.options
    self.userProperties = loadedCfgApp.userProperties
    self.appServerDBIDs = loadedCfgApp.appServerDBIDs
    self.serverInfo = loadedCfgApp.serverInfo
    changed = self.EndChange()
    if not changed:
      mess = "Cannot restore application %s, DBID %s from file %s" %(self.name, self.DBID, saveConfFileName)
      self.printLog(mess)
      saveConfFile.close()
      return 0
    mess = "Application %s, DBID %s successfully restored from file %s" %(self.name, self.DBID, saveConfFileName)
    self.printLog(mess)
      
    return 1
    
  def SetAccount(self, cfgObj):
    """Send request ConfSetAccount for this application"""
    self.cfgServer.SetAccount(self.DBID, cfgObj.cfgID.DBID, cfgObj.objType)
    self.cfgServer.GetUpdates()
    
#==================================================================================
#
#
#                  === CfgQAARTApplication model ===
#
#
if InFalse(GetOption("Java")) and InFalse((GetOption("DotNet"))):
  from pconflib import PrepareConnParams
  
class CfgQaartApplication(CfgApplication):

  def prepareClientConnectTo(self, cfgAppServer):
    found = 0
    connInfo = None
    if self.appServerDBIDs:
      for ci in self.appServerDBIDs:
        if ci.appServerDBID == cfgAppServer.DBID:
          found = 1
          thisCfgHost = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGHost, self.serverInfo.hostDBID)
          connDBID = ci.appServerDBID
          serverCfgHost = self.cfgServer.GetObjectByTypeAndDBID(CfgObjectType.CFGHost, cfgAppServer.serverInfo.hostDBID)
          return self.cfgServer.PrepareClient(self.DBID, thisCfgHost.DBID, connDBID, cfgAppServer.DBID, serverCfgHost.DBID) 
    if not found:
      return PrepareConnParams(cfgAppServer.Host, cfgAppServer.Port)  
            
#==================================================================================
#
#
#                  === CfgHost model ===
#
#
#==================================================================================
class CfgHost(CfgObject):
  """ CfgHost object
  Fields:
    DBID                - Int
    name                - Char
    HWID                - Char
    IPaddress           - Char
    OSinfo              - Struct_CfgOSinfo
    type                - Int
    address             - Struct_CfgAddress
    contactPersonDBID   - Int
    comment             - Char
    state               - Int
    userProperties      - KVList"),
    LCAPort             - Char
    SCSDBID             - Int
    resources           - ListOfStructs_CfgObjectResource
  """
  fields =       (("DBID",                "DBID"),
                 ("name",                "Char"),
                 ("HWID",                "Char"),
                 ("IPaddress",           "Char"),
                 ("OSinfo",              "Struct_CfgOSinfo"),
                 ("type",                "Int"),
                 ("address",             "Struct_CfgAddress"),
                 ("contactPersonDBID",   "Int"),
                 ("comment",             "Char"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
                 ("LCAPort",             "Char"),
                 ("SCSDBID",             "Int"),
                 ("resources",           "ListOfStructs_CfgObjectResource"))
                 
  toXmlTranslation = {"OSinfo": "CfgOSinfo", "address": "CfgAddress"}                 
  fromXmlTranslation = {"CfgOSinfo": "OSinfo", "CfgAddress": "address"}    
                 
  requiredFields = ["name", "OSinfo"]                  
  def __init__(self, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGHost
    filter = {}
    if name:
      filter = {"name" : name }
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgHost" 
    
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.type = 6
    self.LCAPort = "4999"

#==================================================================================
#
#
#                  === CfgAppPrototype model ===
#
#
#==================================================================================

class CfgAppPrototype(CfgObject):
  """ CfgAppPrototype object
  Fields:
    DBID                - Int
    name                - Char
    type                - Int
    version             - Char
    options             - KVList
    state               - Int
    userProperties      - KVList
  """
  
  fields =      (("DBID",                "DBID"),
                 ("name",                "Char"),
                 ("type",                "Int"),
                 ("version",             "Char"),
                 ("options",             "KVList"),
                 ("state",               "Int"),
                 ("userProperties",      "KVList"),
  )
  requiredFields = ["name", "type", "version"]
  translation = All([CfgObject.translation,  {"type":   "CfgAppType"}])
  
  def __init__(self, name = None, type = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGAppPrototype
    filter = {}
    if name:
      filter = {"name" : name }
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgAppPrototype" 
    

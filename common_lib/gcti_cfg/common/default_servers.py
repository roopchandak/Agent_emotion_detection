DefaultServers = {} 
def GetDefaultServer(type):
  if DefaultServers.has_key(type):
    return DefaultServers[type]
  
def SetDefaultServer(type, server):
  DefaultServers[type] = server 

def SetDefaultCommonContainer(container):
  SetDefaultServer("CommonContainer", container)
  
def GetDefaultCommonContainer():
  return GetDefaultServer("CommonContainer")
#==================================================================================

def SetDefaultTServer(tserver):
  SetDefaultServer("TServer", tserver)


def GetDefaultTServer():
  return GetDefaultServer("TServer")
  
#==================================================================================
def SetDefaultCServer(cserver):
  SetDefaultServer("ConfigServer", cserver)

def GetDefaultCServer():
  return GetDefaultServer("ConfigServer")
#==================================================================================

def SetDefaultOCServer(ocserver):
  SetDefaultServer("OCServer", ocserver)



def GetDefaultOCServer():
  return GetDefaultServer("OCServer")
  
#==================================================================================

def SetDefaultCPDServer(cpdserver):
  SetDefaultServer("CPDServer", cpdserver)

def GetDefaultCPDServer():
  return GetDefaultServer("CPDServer")
#==================================================================================

def SetDefaultDBServer(dbserver):
  SetDefaultServer("DBServer", dbserver)
  
def GetDefaultDBServer():
  return GetDefaultServer("DBServer")
#==================================================================================

def SetDefaultSCServer(scserver):
  SetDefaultServer("SolutionControlServer", scserver)

def GetDefaultSCServer():
  return GetDefaultServer("SolutionControlServer")

#==================================================================================

def SetDefaultStatServer(stServer):
  SetDefaultServer("StatServer", stServer)
  
def GetDefaultStatServer():
  return GetDefaultServer("StatServer")

#==================================================================================

def SetDefaultSiebelAdapter(adapter):
  SetDefaultServer("SiebelAdapter", adapter)

def GetDefaultSiebelAdapter():
  return GetDefaultServer("SiebelAdapter")
  
#==================================================================================  
def SetDefaultUCBServer(ucbserver):
  SetDefaultServer("UCBServer", ucbserver)

def GetDefaultUCBServer():
  return GetDefaultServer("UCBServer")
  
#==================================================================================  
def SetDefaultAilFactory(ailFactory):
  SetDefaultServer("AilFactory", ailFactory)

def GetDefaultAilFactory():
  return GetDefaultServer("AilFactory")
#==================================================================================

def SetDefaultITXServer(itxServer):
  SetDefaultServer("ITXServer", itxServer)
  
def GetDefaultITXServer():
  return GetDefaultServer("ITXServer")

#==================================================================================

def SetDefaultMessageServer(server):
  SetDefaultServer("MessageServer", server)
  
def GetDefaultMessageServer():
  return GetDefaultServer("MessageServer")
#==================================================================================
  

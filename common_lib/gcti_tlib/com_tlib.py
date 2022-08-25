import sys
if sys.copyright.lower().find("python") <> -1:
  import tlib
  #========== ConnID, TLibLog and Mask ==============
  
  NoConnID = tlib.T_NO_CONN_ID()
  EmptyConnID =  [255]*tlib.T_CONN_ID_SIZE()
  def ConnIDToStr(connID):
    if not connID or connID == NoConnID: return "None"
    else             : return tlib.TConnIDToStr(connID)
  NullMask = '\0' * tlib.T_MASK_LENGTH()
  StrToConnID = tlib.TStrToConnID
  def SetTlibraryDebug(debug = 2):
    tlib.SetTlibDebug(debug)
  
  def TLibSetupLog(fileName):
    tlib.TLibSetupLog(fileName)
  def ConnIDToStr(connID):
    if not connID or connID == NoConnID: return None
    else             : return tlib.TConnIDToStr(connID)    

elif sys.copyright.lower().find("jython") <> -1:
  from com.genesyslab.platform.voice.protocol import * #This package contains the Protocol classes that your applications can use to set up communication with T-Server, such as TServerProtocol. 

  
  
  def ConnIDToStr(val):
    return str(val)
    
  EmptyConnID = ConnectionId("FFFFFFFFFFFFFFFF")
  NoConnID    = ConnectionId("0000000000000000")
  
  def StrToConnID(st):
    return ConnectionId(st)
    
elif sys.copyright.lower().find("microsoft") <> -1:
 

  import clr
  clr.AddReferenceToFile(r"Genesyslab.Platform.Voice.Protocols.dll")
  from Genesyslab.Platform.Voice.Protocols import *
  
  def ConnIDToStr(val):
    return str(val)
    
  EmptyConnID = ConnectionId("FFFFFFFFFFFFFFFF")
  NoConnID    = ConnectionId("0000000000000000")
  
  def StrToConnID(st):
    return ConnectionId(st)
      

EmptyCallHistory = ((None,None),(None,None))



  




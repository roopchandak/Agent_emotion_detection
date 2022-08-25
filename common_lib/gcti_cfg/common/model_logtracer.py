class ServerLogTracer:

  def __init__(self, server):
    self.server = server
    self.logFileDir = server.logFileDir
    self.logFileName = server.logFileName   

  def isFunctional(self):
    return True
    
  def open(self):
    return None
   
  def Mark(self):
    return -1
    
  def CutAndSave(self,  marker, testName, path, save = 1):
    return None
       
  def Close(self):
    pass


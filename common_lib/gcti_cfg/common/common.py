#
#                  === Common service ===
#
#

import string
import sys
#import win32api
import time
from   enum         import Enum, NameToEnumElem, ValToEnumElem
import socket
import copy
import types
import traceback
import os
from threading import*

import StringIO
try:
  from test_view import *
  from pyasn1.type.univ import *
except:
  pass

globalOptions = {}  
global stopLock
stopLock = Lock()
  
def InTrue(val):
  return (val in ("true", "1", "on", "yes", "True",  "On", "Yes", 1))
  
def GetOption(optName, caseSensative = 0):
  stopLock.acquire()
  optValue = None
  try:
    if not caseSensative:
      for k_ in globalOptions.keys():
        if k_.upper() == optName.upper():
          optValue = globalOptions[k_]  
    else: 
      try:
        optValue = globalOptions[optName] 
      except KeyError, mess:
        pass
  finally:
    stopLock.release()
  if optValue == "false": return False  
  if optValue == "true": return True
  return optValue  

logger = None

try:
    if not InTrue(GetOption("NoStdout")):
        # Add path to GCTI-common package to Python search path
        gcti_commonDir = os.path.dirname(os.path.realpath(__file__))        
        gcti_commonDir = os.path.join(gcti_commonDir, "..", "..", "..", "common")
        sys.path.insert(0, gcti_commonDir)
        import util_logger
        fileName = sys.argv[0] + '_debug'
        logger = util_logger.CreateLoggerEx('cfg-common', fileName, fileNameTimestamp = 1, consoleOutput = 0)
        logger.info("\n\n\n\n\n\n**    THIS IS INTERNAL DEBUG TRACE ONLY                       **\n\n"
                    "**    ERRORS LOGGED IN THIS FILE DO NOT INDICATE A PROBLEM    **\n\n\n\n"
                    "--------------------------------------------------------------------\n"
                    "\n\n\n\n\n")    
except:
    pass

#========= Some globals ==================

global Normal
global Control
global Monitor
global Manager
global Executor
Normal   = 0
Control  = 1
Monitor  = 2
Passive  = 3
Manager  = 4
Executor = 5

global TServerWithCS
global TServerWithoutCS
global SolutionTesting
global AppTestingWithSCS
global AppTestingWithoutSCS
global AilTesting
global NetworkConnectionTesting

TServerWithoutCS = -1
TServerWithCS = 1
SolutionTesting = 2
AppTestingWithSCS = 3
AppTestingWithoutSCS = 4
AilTesting = 5
NetworkConnectionTesting = 6

global ToStart
global ToStop
global ToRestart
global NotDefined
ToStart   = 10
ToStop  = 11
ToRestart  = 12
NotDefined = 13


DefaultUserDataCPDServer  = {"Default userdata": ["cpdcpdcpdcpd etc",  "xxxcpdcpdcpdcpd etc"]}
_fatalErrorCnt = 0

def InFalse(val): 
  return (val in ("false", "0", "off", "no", "False", "Off", "No", 0, None))
#========= Errors and Exeptions ===========

TestResEnum   = Enum("""Successful, Skipped, ForceReset, Warning, MinorError, Error,
                        SeriousError,  ConnectionError, ProgrammError, UserError, FatalError""")
                                                # Test case results enumeration

                                                # Test case unsuccessfull 
UnsuccessSetAlways = (TestResEnum.FatalError, TestResEnum.ConnectionError, TestResEnum.UserError)                                                   
UnsuccessSetLevel1 = (TestResEnum.SeriousError, TestResEnum.FatalError, TestResEnum.ConnectionError, TestResEnum.UserError)   
UnsuccessSetLevel2 = (TestResEnum.Error,) + UnsuccessSetLevel1  
UnsuccessSetLevel3 = (TestResEnum.Warning, TestResEnum.MinorError) +  UnsuccessSetLevel2 

                                                # Make configuration reset after test case

class TesterExcept       (Exception):           pass
class SkipExcept         (TesterExcept):        pass
class ResetExcept        (TesterExcept):        pass
class ConnectionErrorExcept (TesterExcept):     pass
class FatalErrorExcept   (TesterExcept):        pass
class ProgrammErrorExcept(TesterExcept):        pass
class OpenErrorExcept(TesterExcept):            pass


#----------------------------------------------------

#================= Any ===================

class Any:
  # Accepts any fields and any methods with any parameters and makes nothing:
  #   a = Any()
  #   a.aaa("123", "456")             # Makes nothing
  #   a.bbb = 789                     # Makes nothing  
  #   b = a.ccc                       # a.ccc - return a.__a

  def __init__(self, *args, **keywords):  pass
  def __a(self, *args, **keywords):       pass
  def __getattr__(self, name):            return self.__a
  def __setattr__(self, name, val):       pass
  
def EmptyFunction(*args, **keywords): 
  pass  

#=========================================
def IncCnt(optName):
  optValue = GetOption(optName)
  if type(optValue) == type(0):
    optValue = optValue + 1
    SetOption(optName, optValue)
    
_curTest = None

def SetTestHandler(test):
  global _curTest
  _curTest = test  

def TestHandler():
  return _curTest
  
_result = TestResEnum.Successful
def ResetResult():
  _result = TestResEnum.Successful
  
def SetResult(res):
  global _result
  if res.val > _result.val:
    _result = res
  return _result
  
def GetResult():
  return _result

  

def In(setToCheck, setToCheckIn):
  if (type(setToCheckIn) is not types.TupleType):
    setToCheckIn = (setToCheckIn,)
  if (type(setToCheck) is not types.TupleType):
    setToCheck = (setToCheck,)    
  for res in setToCheck:
    if res in setToCheckIn:
      return 1
  return 0 

def ResetTestResult():
  if TestHandler():
    TestHandler().SetTestResult(None)

def ResetFatalErrorCnt():
  global _fatalErrorCnt
  _fatalErrorCnt = 0
  SetOption("FatalErrorString", "")
  if TestHandler():
    TestHandler().fatErrCnt = 0 

def ResetGlobalErrCnts():
  SetOption("GlobalWarCnt", 0)
  SetOption("GlobalMinErrCnt", 0)
  SetOption("GlobalErrCnt", 0)
  SetOption("GlobalSerErrCnt", 0)

def GetGlobalErrCnts():
  return (GetOption("GlobalWarCnt"), GetOption("GlobalErrCnt"), GetOption("GlobalSerErrCnt"))

# Several methods to print errors
def Message(str = "", str2 = "", str0 = "***", shift = 2, prtTm = 1, before = "\n" , after= "\n", prtStat = 1):   
  """Print message"""

  strErr, strExc = formatMsg("Message", str, str2, str0, shift, prtTm, before, after)
  PrintError(strErr, prtStack = 0, prtStat = prtStat)    


def Msg(str = "", str2 = "", str0 = "", shift = 2, prtTm = 1, before = "\n" , after= "\n"):   
  """Print message to commonlog only with time"""

  strErr, strExc = formatMsg("", str, str2, str0, shift, prtTm, before, after)
  PrintError(strErr, prtStack = 0, prtStat = 0) 

def Warning(str = "", str2 = "", str0 = "***", shift = 2, prtTm = 1, byServer = 0):             
  """Print warning message"""
  if not byServer:
    IncCnt("GlobalWarCnt")
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.Warning)  
  SetResult(TestResEnum.Warning)
  strErr, strExc = formatMsg("Warning", str, str2, str0, shift, prtTm)
  PrintError(strErr, prtStack = 0)
  

def MinorError(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm = 1, byServer = 0):             
  """Print warning message"""
  if not byServer:
    IncCnt("GlobalMinErrCnt")
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.MinorError)  
  SetResult(TestResEnum.MinorError)
  strErr, strExc = formatMsg("Minor Error", str(str1), str(str2), str0, shift, prtTm)
  strErrShort, strExc1 = formatMsg("Minor Error", str(str1), str(str2), "", 0, 0)
  SetOption("LastErrorMessage", strErrShort)
  PrintError(strErr, prtStack = 0)

def Error(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm = 1, byServer = 0):               
  """Print error message"""
  if not byServer:
    IncCnt("GlobalErrCnt")
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.Error)  
  SetResult(TestResEnum.Error)
  strErr, strExc = formatMsg("Error", str(str1), str(str2), str0, shift, prtTm)
  strErrShort, strExc1 = formatMsg("Error", str(str1), str(str2), "", 0, 0)
  SetOption("LastErrorMessage", strErrShort)
  PrintError(strErr, prtStack = 0) 


def SeriousError(reset = 0, str1 = "", str2 = "", str0 = "***", shift = 2, prtTm = 1, byServer = 0): 
  """if reset = 1: complete test case execution"""
  if not byServer:
    IncCnt("GlobalSerErrCnt")
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.SeriousError)  
  SetResult(TestResEnum.SeriousError)
  strErr, strExc = formatMsg("Serious Error", str(str1), str(str2), str0, shift, prtTm)
  strErrShort, strExc1 = formatMsg("Serious Error", str(str1), str(str2), "", 0, 0)
  SetOption("LastErrorMessage", strErrShort)
  PrintError(strErr, prtStack = 1)  

  if reset:
    raise ResetExcept, strExc

def Skip0(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1): 
  """Complete test case execution"""

  strErr, strExc = formatMsg("Skipped", str(str1), str(str2), str0, shift, prtTm)
  PrintError(strErr)
  raise SkipExcept, strExc

def UserErrorAfterException(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1):
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.UserError)    
  SetResult(TestResEnum.SeriousError)
  strErr, strExc = formatMsg("User Error ", str(str1), str(str2), str0, shift, prtTm)
  PrintError(strErr, prtStack = 1)  #always print stack

    
def SetFatalErrorCnt(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1):
  global _fatalErrorCnt
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.FatalError)    
  SetResult(TestResEnum.FatalError)
  strErr, strExc = formatMsg("Fatal Error ", str(str1), str(str2), str0, shift, prtTm)
  SetOption("FatalErrorString", strExc)
  PrintError(strErr, prtStack = 1)  #always print stack
  _fatalErrorCnt = 1
  if _printOn:
    try:
      import winsound
      for i in range(1):
        winsound.Beep(500, 100)
        time.sleep(0.5)
    except:
      print "\007"
      pass   
  

def FatalError(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1, beep = 1): 
  """Complete programm execution"""
  if InTrue(GetOption("IgnoreFatalError")): return
  global _fatalErrorCnt
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.FatalError)    
  SetResult(TestResEnum.FatalError)
  strErr, strExc = formatMsg("Fatal Error", str(str1), str(str2), str0, shift, prtTm)
  PrintError(strErr, prtStack = 1)  #always print stack
  _fatalErrorCnt = 1
  if _printOn:
    try:
      import winsound
      for i in range(1):
        winsound.Beep(500, 100)
        time.sleep(0.5)
    except:
      print "\007"
      pass
  SetOption("FatalErrorString", strExc)
  raise FatalErrorExcept, strExc
  
def FatalErrorCnt():
  if _fatalErrorCnt: return 1
  return 0

global _userErrorCnt
_userErrorCnt = 0
def UserErrorCnt():
  return _userErrorCnt

def IncUserError():
  global _userErrorCnt
  _userErrorCnt = _userErrorCnt + 1

def Unimplemented(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1):
  """Unimplemented feature, complete programm execution."""

  ProgrammError(str1, str2, str0, shift, prtTm)


def ProgrammError(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=0):
  """Error in code, complete programm execution."""
  IncUserError()
  strErr, strExc = formatMsg("Programm Error", str(str1), str(str2), str0, shift, prtTm)
  strErrShort, strExc1 = formatMsg("Programm Error", str(str1), str(str2), "", 0, 0)
  SetOption("LastErrorMessage", strErrShort)  
  PrintError(strErr, prtStack = 1)
  
  if TestHandler():
    TestHandler().SetTestResult(TestResEnum.UserError)    
 
  SetResult(TestResEnum.UserError)
  
  raise ProgrammErrorExcept, strExc


def ProgrammWarning(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1):
  """Error in programm code, continue programm execution."""
  if InTrue(GetOption("SuppressProgrammWarnings")): return
  strErr, strExc = formatMsg("Programm Warning", str(str1), str(str2), str0, shift, prtTm)
  PrintError(strErr) 
  pass #continue execution

def ConnectionError(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1): 
  strErr, strExc = formatMsg("Connection Error ", str(str1), str(str2), str0, shift, prtTm)
  PrintError(strErr, prtStack = 0)
  
  raise ConnectionErrorExcept, strExc
 
def OpenError(str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1): 
  strErr, strExc = formatMsg("Open Connection Error ", str(str1), str(str2), str0, shift, prtTm)
  PrintError(strErr, prtStack = 0)  
  raise OpenErrorExcept, strExc




def formatMsg(msgType, str1 = "", str2 = "", str0 = "***", shift = 2, prtTm=1, before="", after="\n"):
  if prtTm: tm = time.strftime("%m/%d/%y %H:%M:%S", time.localtime())     
  else:     tm = ""

  # Mesage for log
  _msgType = ""
  if msgType:
    _msgType = " %s:" % msgType

  s = "%s%s%s%s%s %s %s" % (before, " "*shift, str0, tm, _msgType, str1, str0)
  if str2:
    s += "\n%s" % str2
  if s[-1] <> "\n": s = s + "\n"
  # Mesage for exception
  s2 = str1.strip()
  if str2 and not str2.isspace():
    s2 += "\n"+str2.strip()

  return s, s2
#--------------------------------------
#Verifications
#--------------------------------------
def testValue(value = None, expectedValue = None,  description = "", error = 0,
              errCnt = None, forceReset = -1, exactMatch = 1, byServer = None):


  fldInf = ""
  if value == None and expectedValue == None: # just to produce error/warning and count it
    fldInf = ""
    bad = 1
  else:
    fldInf = ""
    fldInf = ("    expected value :%s\n" % str(expectedValue) + 
              "    received value :%s\n" % str(value))  
    bad = 0
    
    if type(expectedValue) == types.ListType:
      if not (value in expectedValue):  bad = 1
    else:
      if not fldInf or not ValueMatch(value, expectedValue, exactMatch): bad = 1
  
  if byServer:
    return bad, fldInf # leaving 
  
  if bad:
    if error == 1:
      Error(description, fldInf)
    elif error == 2:
      SeriousError(forceReset, description, fldInf)
    elif error == 0:
      Warning(description, fldInf)
    else:
      ProgramWarning("incorrect value of error parameter in TestValue")

def checkKVListValue(value = {}, expectedValue = {}, exactMatch = 1, res = ""):

  for key in expectedValue.keys():
    if type (value) <> type ({}):
      extExpected = "      %-27s: %s\n" %(key, expectedValue[key])
      extReceived = "      %-27s: %s\n" %(value, "WRONG TYPE")
      res = res + ("    expected value :\n%s\n" % str(extExpected) + 
                   "    received value :\n%s\n" % str(extReceived))        
    else:  
      if expectedValue[key] == "NO KEY":
        if  value.has_key(key):
          extExpected = "      %-27s: %s\n" %(key, expectedValue[key])
          extReceived = "      %-27s: %s\n" %(key, value[key])
          res = res + ("    expected value :\n%s\n" % str(extExpected) + 
                       "    received value :\n%s\n" % str(extReceived))          
      else:  
        if not value.has_key(key):
          extExpected = "      %-27s: %s\n" %(key, expectedValue[key])
          extReceived = "      %-27s: %s\n" %(key, "MISSING KEY")
          res = res + ("    expected value :\n%s\n" % str(extExpected) + 
                       "    received value :\n%s\n" % str(extReceived))
      
        else:
          if expectedValue[key] == "something": #ok
            pass
          else:
            
            expectedValueNext = expectedValue[key]
            valueNext = value[key]
            if type(expectedValueNext) == type({}):
              res = checkKVListValue(valueNext, expectedValueNext, exactMatch, res)
            else:
              if not ValueMatch(expectedValueNext, valueNext, exactMatch):
                extExpected = "      %-27s: %s\n" %(key, expectedValueNext)
                extReceived = "      %-27s: %s\n" %(key, valueNext)              
                res = res + ("    expected value :\n%s\n" % str(extExpected) + 
                             "    received value :\n%s\n" % str(extReceived))
  return res

   
def testKVListValue(value = {}, expectedValue = {},  description = "", error = False, errCnt = None,
                    forceReset = -1, exactMatch = 1, byServer = 0):
  
  fldInf = checkKVListValue(value, expectedValue, exactMatch)
  if byServer:
    return fldInf
  
  if fldInf:
    if error == 1:
      Error(description, fldInf)
    elif error == 2:
      SeriousError(forceReset, description, fldInf)
    elif error == 0:
      Warning(description, fldInf)
  return fldInf

def VerifyValue(receivedValue, expectedValue,  description = "", error = 0, errCnt = None,
                forceReset = -1, exactMatch = 1, byServer = 0):
  """Universal method to check value for server
     receivedValue - any type, received value
     expectedValue - any type, expected value
                     if expectedValue is dictionary type, values are verified per key, 
                     extra keys present in received value are ignored
     description - string, error/warning description
     error - 0, 1, 2, indicates if incorrect value is error (1),serious error (2) or warning (0)
     errCnt - specific error counter. If not specified, errBadOtherCnt/serErrOtherCnt/warBadOtherCnt is used
     exactMatch - boolean, defines if values should match exactly. exactMatch 0 is applicable for strings only.
  """
  if type(expectedValue) == type ({}):
    return testKVListValue(receivedValue, expectedValue,  description, error, errCnt, forceReset, exactMatch, byServer)
  else:
    return testValue(receivedValue, expectedValue,  description, error,  errCnt, forceReset, exactMatch, byServer)

def DetectError(description, errCnt = None, byServer = 0):
  """Universal method to indicate error for server
     description - string, error description
     errCnt - specific error counter. If not specified, errBadOtherCnt is used
  """
  testValue(description = description, error = 1, errCnt = errCnt, byServer = byServer)

def DetectSeriousError(description, errCnt = None, forceReset = -1, byServer = 0 ):
  """Universal method to indicate Serious error for server
     description - string, error description
     errCnt - specific error counter. If not specified, errBadOtherCnt is used
  """
  testValue(description = description, error = 2, errCnt = errCnt, forceReset = forceReset, byServer = byServer)
  
def DetectWarning(description, errCnt = None, byServer = 0 ):
  """Universal method to indicate error for server
     description - string, warning description
     errCnt - specific warning counter. If not specified, warBadOtherCnt is used
  """    
  testValue(description = description, error = 0, errCnt = errCnt, byServer = byServer)  
#--------------------------------------
  


#========== Log and Statistics ===========
# - During programm execution log file and statistics files are generated
# - Log is writen on terminal and in file if file for log is opened 
#   (OpenLogFile/CloseLogFile).
# - Statistic is writen in stat file if it is opened (OpenStatFile/CloseStatFile)


_printOn  = 1                 # On/Off log and statistics output
_logFile  = None              # File for log output                          
                              #
_statFile = None              # File for statistics output
                              # In statFile following is writen:
                              # - information about skiped test cases
                              # - information about unsuccessfull test cases
                              # - summary information
                              
_regrResFile = None           # File for test results    
_failedTestsFile = None       # File for failed tests    
_statErrHdr = None            # Header which must be writen in stat file before error 
                              # information output
                              # Usage:
                              # - Before test execution in _statErrHdr information about
                              #   test is set.
                              # - On output of error mesage _statErrHdr is first printed
                              #   and then erased, thus if we have several error
                              #   message during test execution _statErrHdr is printed
                              #   only one time.
                              # - _statErrHdr is not used on log output becouse test
                              #   information is printed before test execution
_addpLogFile = None   # Separate file for ADDP log   

def OpenFile(name):
  fileObject = open(name, "w")
  return fileObject

def WriteToFile(fileObject, obj, n = "\n"):
  fileObject.write(str(obj) + n)
  fileObject.flush()

def CloseFile(fileObject):  
  if fileObject:
    fileObject.close()
    fileObject = None
  return fileObject
  
def OpenLogFile(name, header = "\n================================= QAART ======================================\n"):
  global _logFile
  if _logFile: _logFile = CloseFile(_logFile)
  _logFile = OpenFile(name)
  if header:
    WriteToFile(_logFile, header)  
 
  
  
def GetLogFileObject():
  global _logFile
  return _logFile

  
def CloseLogFile():
  global _logFile
  if _logFile: _logFile = CloseFile(_logFile)
  
def OpenRegrResFile(name):
  global _regrResFile
  if _regrResFile: _regrResFile = CloseFile(_regrResFile)
  _regrResFile = OpenFile(name)


def CloseRegrResFile():
  global _regrResFile
  if _regrResFile: _regrResFile = CloseFile(_regrResFile)  

def OpenFailedTestsFile(name):
  global _failedTestsFile
  if _failedTestsFile: _failedTestsFile = CloseFile(_failedTestsFile)
  _failedTestsFile = OpenFile(name)


def CloseFailedTestsFile():
  global _failedTestsFile
  if _failedTestsFile: _failedTestsFile = CloseFile(_failedTestsFile)  



def OpenStatFile(name, header = "\n================================= QAART ======================================\n"):
  global _statFile
  if _statFile: _statFile = CloseFile(_statFile)
  _statFile = OpenFile(name)
  if header:
    WriteToFile(_statFile, header)

    
def CloseStatFile():
  global _statFile
  if _statFile: _statFile = CloseFile(_statFile)


def PrintStdout(objs = []):
  if InTrue(GetOption("NoStdoutCommon")) or InTrue(GetOption("NoStdout")): return
  if _printOn:
    if type(objs) <> type([]): #string
      objs = [objs]
    for obj in objs:
      print str(obj)
      
def DebugPrint(obj):
  if InTrue(GetOption("DebugLevel")):
    PrintLog(obj)
  
def PrintLog(obj):
  global _logFile
  if _printOn: 
    if _logFile: 
      WriteToFile(_logFile, obj)
    onScreen = 1
    if InTrue(GetOption("NoStdoutCommon")) or InTrue(GetOption("NoStdout")): onScreen = 0  
    if onScreen:
      print obj

    
def PrintStat(obj, onScreen = 0):
  """alwaysOnScreen - boolean, if 1 will print on screen no matter of StdoutOptions"""
  global _statFile
  if _printOn: 
    if _statFile: 
      WriteToFile(_statFile, obj)
    if onScreen: 
      print obj
    if TestHandler():
      TestHandler().addStatInfo(str(obj) + "\n")
      
def PrintRegrRes(obj):
  global _regrResFile
  if _regrResFile: 
    WriteToFile(_regrResFile, obj)
      
def PrintFailedTest(obj):
  global _failedTestsFile
  if _failedTestsFile: 
    WriteToFile(_failedTestsFile, obj)

def PrintLogStat(obj):
  PrintLog(obj)
  onScreen = 0
  if InTrue(GetOption("NoStdoutCommon")): onScreen = 1
  if InTrue(GetOption("NoStdoutStat")) or InTrue(GetOption("NoStdoutStat")): onScreen = 0  
  PrintStat(obj, onScreen = onScreen)



def RegrResultFile(name, allTests):
  ftl = OpenFile(name)
  for obj in allTests:
    WriteToFile(ftl, obj)
  CloseFile(ftl)

def SetStatErrHdr(hdr):
  global _statErrHdr
  _statErrHdr = hdr


def PrintError(obj, prtStack = 0, prtStat = 1):
  """ Print in log and stat """
  global _statErrHdr
  if logger:
    print time.strftime("[*] %m/%d/%y %H:%M:%S", time.localtime())
    logger.debug(str(obj))
  else:
    PrintLog(str(obj))
  if prtStat:
    if _statErrHdr :
      PrintStat(_statErrHdr)
      if _printOn:
        _statErrHdr = None
    onScreen = 0 # usually 
    if InTrue(GetOption("NoStdoutCommon")): onScreen = 1
    if InTrue(GetOption("NoStdoutStat")) or InTrue(GetOption("NoStdoutStat")): onScreen = 0
    PrintStat(str(obj), onScreen = onScreen)
  if prtStack and _printOn:
    try:
      if logger:
          logger.debug("************stack***********")
      else:          
          print "************stack***********"
      f = StringIO.StringIO()
      traceback.print_stack(limit = 50, file = f)
      stack = f.getvalue()
      if logger:
        logger.debug(stack)
      else:
        PrintLog(stack)
      if onScreen:
        print stack
      print "****************************"
    except: #IronPython does not support print_stack
      pass

def PrintTestResult(obj):
  global _statErrHdr
  if _statErrHdr:
    PrintStat(_statErrHdr)
    _statErrHdr = None
  PrintStat(obj)
  print obj


def PrintOn(val = 1):
  global _printOn
  old = _printOn
  _printOn = val
  return old


def PrintOff():
  global _printOn
  old = _printOn
  _printOn = 0
  return old
  
def GetPrintOn() :
  global _printOn
  return _printOn

def OpenAddpFile(name):
  global _addpLogFile
  if _addpLogFile:
    _addpLogFile.close()
  _addpLogFile = open(name, "w")


def CloseAddpFile():
  global _addpLogFile
  if _addpLogFile:
    _addpLogFile.close()
    _addpLogFile = None 

def PrintAddp(obj):
  global _addpLogFile
  if _printOn:
    if _addpLogFile: 
      _addpLogFile.write(str(obj)+"\n")    

def SetTestGetAccessNumber(val): #for compatablity
  if val not in (False, "local", "remote"):
    ProgrammError("Bad TestGetAccessNumber specified in options. Possible values: False, \"local\", \"remote\"")
  SetOption("TestGetAccessNumber", val)

def SetXRouteType(val): #for compatablity
  from common_enum    import XRouteType  
  xRouteType = NameToEnumElem(XRouteType, val)
  if xRouteType == None:
    ProgrammError("Bad XRouteType specified in options")
  SetOption("XRouteType", xRouteType)
 

def SetSaveConfigurationChanges(val):
  SetOption("SaveConfigurationChanges", val)
 

def SetDoNotTest(val):#for compatablity
  SetOption("DoNotTest", val)

  
def GetDoNotTest():
  return GetOption("DoNotTest")#for compatablity

# making it thread safe (??)
def SetOption(optName, optValue):  
  if optName == "XRouteType" and type(optValue) == types.StringType: 
    from common_enum import XRouteType
    optValue = NameToEnumElem(XRouteType, optValue)
    if optValue == None:
      ProgrammError("Bad XRouteType specified in options")
  elif optName == "AddTestInfo":
    PrintError("--<%s>--" %optValue)
  stopLock.acquire()  
  globalOptions[optName] = optValue
  stopLock.release()

def GetOptionInt(optName, caseSensative = 0):
  """Return integer option value (option may be set as integer or string)"""
  optValue = GetOption(optName, caseSensative)
  if optValue == None: #option is not defined
    return 0
  try:
    optValue = int(optValue)
  except:
    ProgrammError("Cannot covert to int value, option %s, set value %s" %(optName, optValue))
  return optValue  

def GetOptionMandatory(optName, caseSensative = 0):
  stopLock.acquire()
  optValue = None
  found = 0
  try:
    if not caseSensative:
      for k_ in globalOptions.keys():
        if k_.upper() == optName.upper():
          optValue = globalOptions[k_]  
          found = 1
    else: 
      try:
        optValue = globalOptions[optName] 
        found = 1
      except KeyError, mess:
        pass
  finally:
    stopLock.release()
  if optValue == "false": return False  
  if optValue == "true": return True
  if not found:
    FatalError("Option %s is not set" %optName)
  return optValue

def Similar(str1, str2):
  if str1 == str2 or (not str1 and not str2) or\
  (str1 and str2 and str1.find(str2) != -1) or \
    (str1 and str2 and str2.find(str1) !=-1):
    return 1
  return 0

def ValueMatch(val1, val2, exactMatch = 1):
  if exactMatch:
    return val1 == val2
  else:
    if type(val1) == type(""):
      return Similar(val1, val2)
    else:
      return val1 == val2


def All (DictList = []):

  sum = {}
  for dict in DictList:
    sum.update(dict)
  return sum
  
global _sync
_sync = Any()

def SetSynchronizer(sync):
  global _sync
  _sync = sync

    
def Synchronizer():
  return _sync

class Sync:
  def __init__(self, controlStatus, serverInfo = None):
    self.controlStatus = controlStatus
    self.NoCommandExchange = 1
    self.commonTServer = 0
    if controlStatus != Normal:
      self.NoCommandExchange = 0
      self.sock = 0
      self.port = 50007
      self.resetCommandReceived = 0
      self.serverInfo = serverInfo
      self.otherClientServerInfo = ""
      if self.controlStatus in (Control, Manager):
        self.openConnectionToMonitoring()
        if serverInfo:
          self.SetServerInfo(serverInfo)
      elif self.controlStatus in (Monitor, Passive, Executor):
        self.openConnectionToControling()
        if serverInfo:
          self.SetServerInfo(serverInfo)
  
  def SetServerInfo(self, serverInfo):
    self.serverInfo = serverInfo
    if self.controlStatus == Control:
      self.sendCommand(serverInfo)
      self.waitCommand("server info set")
    elif self.controlStatus in (Monitor, Passive):
      otherClientServerInfo = self.waitCommand()
      self.sendCommand("server info set")
      self.otherClientServerInfo = otherClientServerInfo    
      if serverInfo == otherClientServerInfo or otherClientServerInfo == "ail":
        self.commonTServer = 1    
  
  def GetControlStatus(self):
    return self.controlStatus
    
  def GetNoCommandExchange(self):
    return self.NoCommandExchange    
  
  def GetCommonTServer(self):
    return self.commonTServer
    
  def SetControlStatus(self, status = None, noCommandExchange = 1):
    if status != None:
      self.controlStatus = status
    if self.controlStatus != Normal:
      self.NoCommandExchange = noCommandExchange
  
  def ExchangeCommands(self, command, timeout = 180):
    if not self.NoCommandExchange:
      if self.controlStatus == Monitor:
        self.waitCommand(command, timeout)
        self.sendCommand(command)
      elif self.controlStatus == Control:
        self.sendCommand(command)
        self.waitCommand(command, timeout)  
  

  def openConnectionToMonitoring(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",self.port))
    print s.getsockname()
    s.listen(1) 
    print "Waiting for connection from monitoring site.."
    self.sock, addr = s.accept()
    
    print 'Connected by', addr
    print "received " + self.waitCommand("Hi! Monitoring client connected!")


  def openConnectionToControling(self, timeout = 30):

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    beg = time.time()
    tout = 0
    command = ""
    while tout < timeout:
      try:
        tout = int(time.time() - beg)
        self.sock.connect((socket.gethostname(), self.port))
        break
      except socket.error:
        pass
      
    if tout < timeout:    #connection was established before timeout expired
      self.sock.send("Hi! Monitoring client connected!")
    else:
      ProgrammError("No connection to Controlling Client")

  def waitCommand(self, cmd = "", timeout = 180) :
    if self.NoCommandExchange: return
    if cmd == "Any reset" and  self.resetCommandReceived:  # Monitor client is waiting for any reset command, but it already it happened
      self.resetCommandReceived = 0
      return "Let's do serious reset"
    beg = time.time()
    tout = 0
    command = ""
    print "Waiting for command " + cmd
    while tout < timeout:
      try:
        tout = int(time.time() - beg)
        command = self.sock.recv(1024)
        if command :
          print "Received command: " + command
          break
      except socket.error:
        pass  
    if cmd == "Any reset" and (command in ("Let's do serious reset", "Let's do usual reset")):
      return command
    if command == "Let's do serious reset" and cmd != "Any reset" and cmd != command:  # unexpected reset  .Only Control Client can initiate  reset
      self.resetCommandReceived = 1
      SeriousError(1, "Reset has been started on the other client") # should follow the other client
    if not cmd and command:    #command to expect is unknown 
      return command
    if not command or command != cmd:
      ProgrammError("Bad Synhronization")
    return command
    
  
  def sendCommand(self, command):
    if self.NoCommandExchange: return
    try:
      self.sock.send(command)
      print "Sending command " + command
    except socket.error:
      ProgrammError("Bad connection between clients")
      
  def Order(self, command):
    PrintLog("Sending command to Executor %s" %command)
    self.sendCommand(command)
    result = Synchronizer().waitCommand()
    PrintLog("Received result %s" %str(result))
    if result.find("Invalid command") <> -1:
      FatalError("Command sent to Executor is invalid: %s" %str(result))
    else:
      testResult = Synchronizer().waitCommand()
      PrintLog("Received test result %s" %str(testResult))
      if testResult not in (None, "Successful"):
        Message("Received result from Executor %s" %testResult)
      TestHandler().SetTestResult(testResult)
    return result
     
 
  def actionOnNoCommand(self):
    if self.NoCommandExchange: return
    ProgrammError("Bad synchronization")    



def CompareFloatPcnt(origRes, res2, compMethod = "percent", percent = 10):

  if compMethod == "percent":
    if origRes == "":
      if res2 <> "":
        return "Results are not equal"
    else:
      origRes = float(origRes)
      res2 = float(res2)

      allowedDelta = (float(percent)/100)* origRes
      if (res2 < origRes and res2 + allowedDelta < origRes) or \
        (res2 > origRes and res2 - allowedDelta > origRes):
        return "Result %s is not on allowable range %s - %s" %(res2, origRes - allowedDelta, origRes + allowedDelta)


#========== Reasons ======================
global lastReasons
global defaultReasons
lastReasons = None
defaultReasons = None
global lastActionTime
lastActionTime = None

def SetDefaultReasonsForThisTest(testName):
  global defaultReasons
  if testName:
    defaultReasons = {"DefaultReasons" : testName}
  else:
    defaultReasons = None
  
def Reasons(reasons = None):
  global lastReasons

  lastReasons = {}
  
  if reasons or reasons == {}:
    lastReasons = reasons
  else:
    if InTrue(GetOption("NoReasons")):
      lastReasons = None
    else:
      th = TestHandler()
      if th:
        lastReasons = {"DefaultReasons" : th.testName}
  SetLastActionTime()
  return copy.copy(lastReasons)
  
def GetReasons() :
  return copy.copy(lastReasons)

def GetLastActionTime():
  return lastActionTime

def SetLastActionTime():
  global lastActionTime
  lastActionTime = time.time()


global userDataForOrigCall
userDataForOrigCall = None
global userDataForConsCall
userDataForConsCall = None
global noUserData
noUserData = False

def SetNoUserData(val):
  global noUserData
  noUserData = val

def SetDefaultUserDataForThisTest(testName, testCnt = 0, testDoc = None):

  global userDataForOrigCall
  global userDataForConsCall

  if noUserData:
    userDataForOrigCall = None
    userDataForConsCall = None
    return
  if testName:
    if InTrue(GetOption("DocToUserData")) and testDoc:
      userDataForOrigCall = {"original *** %s"%testName:  "%s" %testDoc }
      userDataForConsCall = {"consult *** %s"%testName:  "%s" %testDoc }
    elif GetOption("TestCountToUserData"):
      userDataForOrigCall = {GetOption("DefaultUserDataKeyForOrigCall") :  "%s.%s" %(testCnt, testName) }
      userDataForConsCall = {GetOption("DefaultUserDataKeyForConsultCall") : "%s.%s" %(testCnt, testName)}
    else:
      userDataForOrigCall = {GetOption("DefaultUserDataKeyForOrigCall") :  "%s" %testName }
      userDataForConsCall = {GetOption("DefaultUserDataKeyForConsultCall") : "%s" %testName}
  else:
    userDataForOrigCall = None
    userDataForConsCall = None

def GetUserData(whatToGet = 1):
  if whatToGet:
    return copy.copy(userDataForOrigCall)
  else:
    return copy.copy(userDataForConsCall)
  
#======Wait events from any tserver=======
def Wait(ts = None, dnNum = None, event = None, timeout = None):
  if ts == None:
    if not timeout: timeout = 1
    time.sleep(timeout)
    return
  else:
    return ts.Wait(dnNum, event, timeout)

  
def GetAttribute(event, attrName):
  if not event:
    ProgrammError("Event passed to GetAttribute function is empty")
  if hasattr(event, attrName):
    return getattr(event, attrName)
  ProgrammError("Event does not have attribute %s" %attrName)

#==================================================================================
#Folder clearing
#==================================================================================
def ClearPath(folder):
  """Returns 0 if path succesfully cleaned, error string otherwise"""
  try:
    for f in os.listdir(folder): 
      PrintStdout(f)
      if os.path.isdir(os.path.join(folder, f)):
        ClearPath(os.path.join(folder, f))
      else:
        os.remove(os.path.join(folder, f))
    os.rmdir(folder)
    time.sleep(1)
  except os.error, err:
    Warning("Problem on folder clearing, check that no files are opened;  %s" % str(err))
    return "Problem on folder clearing, check that no files are opened;  %s" % str(err)
  return None 


#==================================================================================
def dataBaseTime():
    """Returns Greenwich time as string, example: '2002 Aug 06 22:04:13'
    """
    return time.strftime("%Y %b %d %X", time.gmtime())

def ctime_():
    """Returns local time as string, exapmle: '15:00:51'
    """
    return time.ctime().split()[3]

def ConvertTimeoutToSec(s):
  hr = 0
  min = 0
  sec = 0
  msec = 0
  i_hr = s.find("hr")
  if i_hr > -1:
    hr = int((s[0:i_hr]).strip())
    s = s[i_hr + 2:]
  elif s.count(":") == 2:
    i_hr = s.find(":")
    hr = int((s[0:i_hr]).strip())
    s = s[i_hr+1:]
  
  i_min = s.find("min")
  if i_min > -1:
    min = int((s[0:i_min]).strip())
    s = s[i_min + 3:]
  elif s.count(":") == 1:
    i_min = s.find(":")
    min = int(s[0:i_min].strip())
    s = s[i_min + 1:]
  
  i_sec = s.find("sec")
  if i_sec > -1:
    if s[i_sec - 1] != "m":# != msec
        sec = int((s[0:i_sec]).strip())
        s = s[i_sec + 3:]
  
  i_msec = s.find("msec")
  if i_msec > -1:
    msec = int((s[0:i_msec]).strip())
    s = s[i_msec + 4:]
  
  if s and len(s.strip()) > 0:
    sec = float(s.strip())
    
  if hr > 0: sec = sec + hr * 3600
  if min > 0: sec = sec + min * 60
  if msec > 0: sec = sec + float(msec)/1000
  return sec 


#==================================================================================
try:
  import inspect
except:
  pass
def whoami():
  return inspect.stack()[1][3]
#==================================================================================  
def dicGetKeyNoCase(dic, key):
  """Finds if key exists in case-insensitive dictionary.
    Raises KeyError if several keys with different case exist in dictionary
    Return - case-insensitive key or None if key not found
  """

  caseInsKey = None
  upk = key.upper()
  for k_ in dic.keys():
    if k_.upper() == upk:
      if caseInsKey:
        raise KeyError  # Several similar keys in the dictionary 
      caseInsKey = k_
  return caseInsKey

def dicGetValueByKeyNoCase(dic, key):
  """Returns value if key exists in case-insensitive dictionary or None otherwise
     
  """
  value = None
  key = dicGetKeyNoCase(dic, key)
  if key:
    value = dic[key]
  return value
#==================================================================================
def DictToString(aDict, br='\n', html=0,
            keyAlign='l',   sortKey=0,
            keyPrefix='',   keySuffix='',
            valuePrefix='', valueSuffix='',
            leftMargin=0,   indent=1 ):
    '''
return a string representive of aDict in the following format:
    {
     key1: value1,
     key2: value2,
     ...
     }

Spaces will be added to the keys to make them have same width.

sortKey: set to 1 if want keys sorted;
keyAlign: either 'l' or 'r', for left, right align, respectively.
keyPrefix, keySuffix, valuePrefix, valueSuffix: The prefix and
   suffix to wrap the keys or values. Good for formatting them
   for html document(for example, keyPrefix='<b>', keySuffix='</b>'). 
   Note: The keys will be padded with spaces to have them
         equally-wide. The pre- and suffix will be added OUTSIDE
         the entire width.
html: if set to 1, all spaces will be replaced with '&nbsp;', and
      the entire output will be wrapped with '<code>' and '</code>'.
br: determine the carriage return. If html, it is suggested to set
    br to '<br>'. If you want the html source code eazy to read,
    set br to '<br>\n'

version: 04b52
author : Runsun Pan
require: odict() # an ordered dict, if you want the keys sorted.
         Dave Benjamin 
         http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/161403
    '''
   
    if aDict:

        #------------------------------ sort key
        if sortKey:
            dic = aDict.copy()
            keys = dic.keys()
            keys.sort()
            aDict = odict()
            for k in keys:
                aDict[k] = dic[k]
            
        #------------------- wrap keys with ' ' (quotes) if str
        tmp = ['{']
        ks = [type(x)==str and "'%s'"%x or x for x in aDict.keys()]

        #------------------- wrap values with ' ' (quotes) if str
        vs = [type(x)==str and "'%s'"%x or x for x in aDict.values()] 

        maxKeyLen = max([len(str(x)) for x in ks])

        for i in range(len(ks)):

            #-------------------------- Adjust key width
            k = {1            : str(ks[i]).ljust(maxKeyLen),
                 keyAlign=='r': str(ks[i]).rjust(maxKeyLen) }[1]
            
            v = vs[i]        
            tmp.append(' '* indent+ '%s%s%s:%s%s%s,' %(
                        keyPrefix, k, keySuffix,
                        valuePrefix,v,valueSuffix))

        tmp[-1] = tmp[-1][:-1] # remove the ',' in the last item
        tmp.append('}')

        if leftMargin:
          tmp = [ ' '*leftMargin + x for x in tmp ]
          
        if html:
            return '<code>%s</code>' %br.join(tmp).replace(' ','&nbsp;')
        else:
            return br.join(tmp)     
    else:
        return '{}'
#========= Some system calls ==============
global SavedTime
global TimeStart 
SavedTime = 0  
TimeStart = 0

def SetDayOfWeek(day):
  # Sunday = 4 Jan 1998
  # Monday = 5 Jan 1998
  # Tuesday = 6 Jan 1998
  # Wednesday = 7 Jan 1998
  # Thursday = 8 Jan 1998
  # Friday = 9 Jan 1998
  # Saturday = 10 Jan 1998
  import win32api
  global TimeStart, SavedTime
  SavedTime = time.time()
  (y, m, dow, d, h, min, s, ms) = win32api.GetSystemTime() 
  #Set new system date with the same h, min, sec
  win32api.SetSystemTime(1998, 1, day.val, day.val + 4, h, min, s, ms)
  #start timer
  TimeStart = time.time()
  
def SetDateAndTime(year, month, day, hour, minute, sec = 0):
  import win32api
  global TimeStart, SavedTime
  SavedTime = time.time()
  win32api.SetSystemTime(year, month, 0, day, hour, minute, sec, 0)
  TimeStart = time.time()

def SetDate(year, month, day):
  import win32api
  global TimeStart, SavedTime
  SavedTime = time.time()
  (y, m, dow, d, h, min, s, ms) = win32api.GetSystemTime() 
  win32api.SetSystemTime(year, month, 0, day, h, min, s, ms)
  TimeStart = time.time()

def SetTime(hour = 0, minute = 0, sec = 0):
  import win32api
  global TimeStart, SavedTime
  SavedTime = time.time()
  (y, m, dow, d, h, min, s, ms) = win32api.GetSystemTime() 
  if not hour: hour = h
  if not minute: minute = min
  if not sec: sec = s
  win32api.SetSystemTime(y, m, dow, d, hour, minute, sec, ms)
  TimeStart = time.time()

def SetShiftTime(dhour = 0, dminute = 0, dsec = 0, saveTime = 1):
  import win32api
  global TimeStart, SavedTime
  if saveTime:
    SavedTime = time.time()
  (y, m, dow, d, h, min, s, ms) = win32api.GetSystemTime() 
  h = h + dhour
  min = min + dminute
  s = s + dsec
  win32api.SetSystemTime(y, m, dow, d, h, min, s, ms)
  TimeStart = time.time()  
  
def SetSystemTimeBack():
  import win32api
  global TimeStart, SavedTime
  if not TimeStart: return
  time.sleep(1)
  TimeStop = time.time()
  delta = TimeStop - TimeStart
  newTime = SavedTime + delta
  (y, m, d, h, min, sec, dow, jd, dsf) = time.gmtime(newTime)
  win32api.SetSystemTime(y, m, dow, d, h, min, sec, 0) 
  TimeStart = 0 
  
  
def IncorrectFunction():
  print hhh
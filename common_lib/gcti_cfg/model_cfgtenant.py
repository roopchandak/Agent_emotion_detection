#
#                  === CfgTenant model ===
#
#

from common               import *
from common_enum          import *
from enum                 import *
from model_cfgobject      import *
#==================================================================================
class CfgTenant(CfgObject):
  """ CfgTenant object
  Fields:
    DBID                    - Int
    isServiceProvider       - Int
    name                    - Char
    password                - Char
    address                 - Struct_CfgAddress
    chargeableNumber        - Char
    tenantPersonDBID        - Int
    providerPersonDBID      - Int
    serviceInfo             - Struct_CfgServiceInfo
    isSuperTenant           - Int
    tenantDBID              - Int
    state                   - Int
    userProperties          - KVList
    defaultCapacityRuleDBID - Int
    defaultContractDBID     - Int
    parentTenantDBID        - Int
  """
  fields =      (("DBID",                   "DBID"),
                 ("isServiceProvider",      "Int"),
                 ("name",                   "Char"),
                 ("password",               "Char"),
                 ("address",                "Struct_CfgAddress"),
                 ("chargeableNumber",       "Char"),                   
                 ("tenantPersonDBID",       "Int"),
                 ("providerPersonDBID",     "Int"),
                 ("serviceInfo",            "Struct_CfgServiceInfo"),
                 ("isSuperTenant",          "Int"),
                 ("tenantDBIDs",            "DBIDList"),
                 ("state",                  "Int"),
                 ("userProperties",         "KVList"),
                 ("defaultCapacityRuleDBID","Int"),
                 ("defaultContractDBID",    "Int"),
                 ("parentTenantDBID",    "Int"))             
  toXmlTranslation = {"address": "CfgAddress", "serviceInfo": "CfgServiceInfo"}                 
  fromXmlTranslation = {"CfgAddress": "address", "CfgServiceInfo": "serviceInfo"}
  
  translation = All([CfgObject.translation,  {"isServiceProvider": "CfgFlag",
                                              "isSuperTenant":     "CfgFlag"}])   
  requiredFields = ["name"]                                      
  def __init__(self, name = None, cfgServer = None, strObj = None):
    self.objType = CfgObjectType.CFGTenant
    filter = {}
    if name:
      if name == "Environment":
        filter = {"dbid": 1}
      else:
        filter = {"name" : name}
    CfgObject.__init__(self, self.objType, filter, cfgServer, strObj)
    self.title = "CfgTenant"
    
  def createEmptyObject(self):
    CfgObject.createEmptyObject(self)
    self.isServiceProvider = CfgFlag.False.val
    self.isSuperTenant = CfgFlag.False.val

   
  def getServiceInfoAttr(self, attr, obj):  
    #----serviceInfo------
    pattern = "\030serviceInfo=NIL"
    matchObj = re.search(pattern, obj)
    if matchObj: serviceInfo = None
    else:
      serviceInfo = {}
      pattern = "\035serviceDBID=([0-9]+)"
      matchObj = re.search(pattern, obj)
      serviceInfo["serviceDBID"] = int(matchObj.group(1))  
      pattern = "\030isChargeable=([0-9]+)"
      matchObj = re.search(pattern, obj)
      serviceInfo["isChargeable"] = int(matchObj.group(1))  
    return serviceInfo      
    
    
  def setServiceInfoAttr(self, attr, pyAttr):  
    #-----serviceInfo-----
    cfgString = ""
    if pyAttr == None:
      cfgString = cfgString + "\030serviceInfo=NIL"
    else:
      cfgString = cfgString + "\030serviceInfo="
      cfgString = cfgString + "\035serviceDBID=" + str(pyAttr["serviceDBID"])
      cfgString = cfgString + "\030isChargeable=" + str(pyAttr["isChargeable"])
      cfgString = cfgString + "\036"    
    return cfgString   
   
 
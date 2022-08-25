#
#                  === Common Enumerations ===
#
#

from enum   import Enum, ValToEnumElem, NameToEnumElem
#from common import NoConnID, NullMask

#==================================================================================
Bool = Enum("""
  Min = -1,
  False,
  True
 """)

PartyState = Enum("""
  Min = -1,
  NoPartyState,
  Dialing,
  Ringing,
  Established,
  Max = 100
""") 

ScanMode = Enum("""
  TSCAN_MODE_DEFAULT   = 0,
  TSCAN_MODE_WRITE     = 2, 
  TSCAN_MODE_WRITE_ALL = 512, 
  TSCAN_MODE_CONNECT   = 528
""")

ControlStatus = Enum("""
  Min = -1,
  Normal,
  Monitor,
  Control,
  Max = 100
""")



OpenMode = Enum("""
  Min = -1,
  Sync = 0,
  Async = 1,
  Max = 100
""")


AddressType = Enum("""
  Min = -1,
  Unknown,
  DN,
  Position,
  Queue,
  RouteDN,
  Trunk,
  VoiceChannel,
  DataChannel,
  Announcement,
  ASAI,
  ACDGroup,
  VSP,
  RouteQueue, 
  AgentID,    
  Other = 99, 
  Max = 100
""")


RegisterMode = Enum("""
  Min = -1,
  Share,
  Private,
  Monitor,
  Max = 100
""")


ControlMode = Enum("""
  Min = -1,
  Default = 0,
  Force = 1,
  Local = 2,
  Max = 100
""")


PartyRole = Enum("""
  Min = -1,
  Unknown,
  Origination,
  Destination,
  ConferenceMember,
  NewParty,
  AddedBy,
  DeletedBy,
  TransferedBy,
  DeletedParty,
  ConferencedBy,
  Observer,
  Max = 100
""")

                              
CallType = Enum("""
  Min = -1,
  Unknown,
  Internal,
  Inbound,
  Outbound,
  Consult,
  Max = 100
""")


CallScope = Enum("""
  Min = -1,
  Internal  = %s,
  Inbound = %s,
  Outbound  = %s
  """ % (`CallType.Internal.val`,
         `CallType.Inbound.val` ,
         `CallType.Outbound.val`
        )
)


CallState = Enum("""
  Min = -1,
  Ok,
  Transferred,
  Conferenced,
  GeneralError,
  SystemError,
  RemoteRelease,
  Busy,
  NoAnswer,
  SitDetected,
  AnsweringMachineDetected,
  AllTrunksBusy,
  SitInvalidnum,
  SitVacant,
  SitIntercept,
  SitUnknown,
  SitNocircuit,
  SitReorder,
  FaxDetected,
  QueueFull,
  Cleared,
  Overflowed,
  Abandoned,
  Redirected,
  Forwarded,
  Consult,
  Pickedup,
  Dropped,
  Droppednoanswer,
  Unknown,
  Covered, 
  ConverseOn,
  Bridged,
  Silence,        
  Answer,         
  NuTone,         
  NoDialTone,     
  NoProgress,     
  NoRingBack,     
  NoEstablished,  
  PagerDetected,  
  WrongParty,     
  DialErr,        
  DropErr,        
  SwitchErr,      
  NoFreePortErr,  
  TransferErr,    
  Stale,          
  AgentCallBackErr,
  GroupCallBackErr,
  Deafened, 
  Held,  
  DoNotCall,
  Cancel, 
  WrongNumber,
  Max = 100
""") 


AnswerType = Enum("""
  Min = -1,
  Unknown,
  Voice,
  Busy,
  NoAnswer,
  Sit,
  Fax,
  Modem,
  AnsweringMachine,
  Max = 100
""")

def AnswerTypeToCallResult(answerType):
  if answerType == AnswerType.Voice:
    return CallState.Answer
  return  NameToEnumElem(CallState, answerType)


PredictiveCallState = Enum("""
  Min = -1,
  CallToDest,
  DestAnswer,
  Divertied,
  Max = 100
""")


MakeCallType = Enum("""
  Min = -1,
  Regular,
  DirectAgent,
  SupervisorAssist,
  Priority,
  DirectPriority,
  Max = 100
""")


ConsultCallType = Enum("""
  Min = -1,
  Transfer,
  MuteTransfer,
  Conference,
  Max = 100
""")


MergeType = Enum("""
  Min = -1,
  Transfer,
  Conference,
  Max = 100
""")


RouteType = Enum("""
  Min = -1,
  Unknown,
  Default,
  Label,
  OverwriteDNIS,
  DDD,
  IDDD,
  Direct,
  Reject,
  Announcement,
  PostFeature,
  DirectAgent,
  Priority,
  DirectPriority,
  AgentID, 
  CallDisconnect,  
  IDMAX,
  Max = 100
""")

XRouteType = Enum("""
  XRouteTypeDefault       = -1,
  XRouteTypeMIN           =  0,
  XRouteTypeRoute         =  0,
  XRouteTypeDirect        =  1,
  XRouteTypeReroute       =  2,
  XRouteTypeDirectUUI     =  3,
  XRouteTypeDirectANI     =  4,
  XRouteTypeDirectNoToken =  5,
  XRouteTypeDNISPooling   =  6,
  XRouteTypeDirectDigits  =  7,
  XRouteTypePullBack      =  8, 
  XRouteTypeExtProtocol   =  9,
  XRouteTypeRouteUUI      = 10, 
  XRouteTypeDirectNetworkCallID = 11
""")

ForwardMode = Enum("""
  Min = -1,
  None,
  Unconditional,
  OnBusy,
  OnNoAnswer,
  OnBusyAndNoAnswer,
  SendAllCalls,
  Max = 100
""")


AgentType = Enum("""
  Min = -1,
  Agent,
  Supervisor,
  Max = 100
""")


AgentWorkMode = Enum("""
  Min = -1,
  Unknown,
  ManualIn,
  AutoIn,
  AfterCallWork,
  AuxWork,
  NoCallDisconnect,
  WalkAway,
  ReturnBack,
  Max = 100
""")


AgentState = Enum("""
  Unknown = -1,
  Login,
  Logout, 
  Ready, 
  NotReady,
  AfterCallWork,
  Max = 100
""")


AddressInfo = Enum("""
  Min = -1,
  AddressStatus,
  MessageWaitingStatus,
  AssociationStatus,
  CallForwardingStatus,
  AgentStatus,
  NumberOfAgentsInQueue,
  NumberOfAvailableAgentsInQueue,
  NumberOfCallsInQueue,
  AddressType,
  CallsQuery,
  SendAllCallsStatus,
  QueueLoginAudit,
  NumberOfIdleClassifiers,
  NumberOfClassifiersInUse,
  NumberOfIdleTrunks,
  NumberOfTrunksInUse,
  DatabaseValue,
  DNStatus,
  QueueStatus,
  Max = 100
""")


CallInfoType =  Enum ("""
  CallInfoPartiesQuery,
  CallInfoStatusQuery
""")


LocationInfo = Enum("""
  Min = -1,
  AllLocations,
  LocationData,
  MonitorLocation,
  CancelMonitorLocation,
  MonitorAllLocations,
  CancelMonitorAllLocations,
  LocationMonitorCanceled,
  AllLocationsMonitorCanceled,
  Max = 100
""")

AddressStatusInfoType = Enum("""
  Idle,
  Origination,
  Dialing,
  Talking,
  Ringing,
  Held,
  Treatment,
  LockedOut,
  Maintenance,
  Available,
  Vacant
""")

SwitchInfoType = Enum("""
  SwitchInfoDateTime       = 1,
  SwitchInfoClassifierStat = 2
""") 


TreatmentType  = Enum("""
  Min = -1,
  Unknown,
  IVR,
  Music,
  RingBack,
  Silence,
  Busy,
  CollectDigits,
  PlayAnnouncement,
  PlayAnnouncementAndDigits,
  VerifyDigits,
  RecordUserAnnouncement,
  DeleteUserAnnouncement,
  CancelCall,
  PlayApplication,
  SetDefaultRoute,
  TextToSpeech,
  TextToSpeechAndDigits,
  FastBusy, 
  RAN,
  IDMAX,
  Max = 100
""")



#Historically happened that prefix "Event" was removed form EventName. Sould be kept this way.
EventName = Enum("""
  RequestRegisterClient,
  RequestQueryServer,
  RequestQueryAddress,
  RequestRegisterAddress,
  RequestUnregisterAddress,
  RequestRegisterAll,
  RequestUnregisterAll,
  RequestSetInputMask,
  RequestAgentLogin,
  RequestAgentLogout,
  RequestAgentReady,
  RequestAgentNotReady,
  RequestSetDNDOn,
  RequestSetDNDOff,
  RequestMakeCall,
  RequestMakePredictiveCall,
  RequestAnswerCall,
  RequestReleaseCall,
  RequestHoldCall,
  RequestRetrieveCall,
  RequestInitiateConference,
  RequestCompleteConference,
  RequestDeleteFromConference,
  RequestInitiateTransfer,
  RequestMuteTransfer,
  RequestSingleStepTransfer,
  RequestCompleteTransfer,
  RequestMergeCalls,
  RequestAlternateCall,
  RequestReconnectCall,
  RequestAttachUserData,
  RequestUpdateUserData,
  RequestDeleteUserData,
  RequestDeletePair,
  RequestCallForwardSet,
  RequestCallForwardCancel,
  RequestRouteCall,
  RequestGiveMusicTreatment,
  RequestGiveSilenceTreatment,
  RequestGiveRingBackTreatment,
  RequestLoginMailBox,
  RequestLogoutMailBox,
  RequestOpenVoiceFile,
  RequestCloseVoiceFile,
  RequestPlayVoiceFile,
  RequestCollectDigits,
  RequestSetMessageWaitingOn,
  RequestSetMessageWaitingOff,
  RequestDistributeUserEvent,
  RequestDistributeEvent,

  ServerConnected,
  ServerDisconnected,
  Error,
  Registered,
  Unregistered,
  RegisteredAll,
  UnregisteredAll,
  Queued,
  Diverted,
  Abandoned,
  Ringing,
  Dialing,
  NetworkReached,
  DestinationBusy,
  Established,
  Released,
  Held,
  Retrieved,
  PartyChanged,
  PartyAdded,
  PartyDeleted,
  RouteRequest,
  RouteUsed,
  AgentLogin,
  AgentLogout,
  AgentReady,
  AgentNotReady,
  DNDOn,
  DNDOff,
  MailBoxLogin,
  MailBoxLogout,
  VoiceFileOpened,
  VoiceFileClosed,
  VoiceFileEndPlay,
  DigitsCollected,
  AttachedDataChanged,
  OffHook,
  OnHook,
  ForwardSet,
  ForwardCancel,
  MessageWaitingOn,
  MessageWaitingOff,
  AddressInfo,
  ServerInfo,
  LinkDisconnected,
  LinkConnected,
  UserEvent,

  RequestSendDTMF,
  DTMFSent,

  ResourceAllocated,
  ResourceFreed,

  RemoteConnectionSuccess,
  RemoteConnectionFailed,

  RequestRedirectCall,
  RequestListenDisconnect,
  RequestListenReconnect,
  ListenDisconnected,
  ListenReconnected,
  RequestQueryCall,
  PartyInfo,
  RequestClearCall,

  RequestSetCallInfo,
  CallInfoChanged,

  RequestApplyTreatment,
  TreatmentApplied,
  TreatmentNotApplied,
  TreatmentEnd,

  HardwareError,
  AgentAfterCallWork,
  TreatmentRequired,

  RequestSingleStepConference,
  RequestQuerySwitch,
  SwitchInfo,

  RequestGetAccessNumber,
  RequestCancelReqGetAccessNumber,
  AnswerAccessNumber,
  ReqGetAccessNumberCanceled,

  RequestReserveAgent,
  AgentReserved,
  RequestReserveAgentAndGetAccessNumber,

  RequestAgentSetIdleReason,
  AgentIdleReasonSet,

  RestoreConnection,
  PrimaryChanged,
  RequestLostBackupConnection,
  RequestSetDNInfo,

  RequestQueryLocation,
  LocationInfo,

  ACK,

  RequestMonitorNextCall,
  RequestCancelMonitoring,
  MonitoringNextCall,
  MonitoringCancelled,

  RequestSetMuteOn,
  RequestSetMuteOff,
  MuteOn,
  MuteOff,

  DNOutOfService,
  DNBackInService,

  RequestPrivateService,
  PrivateInfo,

  Bridged, 
  QueueLogout,          

  Reserved_1,           
  Reserved_2,
  Reserved_3,
  Reserved_4,
  Reserved_5,
  Reserved_6,
  Reserved_7,

  CallCreated,          
  CallDataChanged,
  CallDeleted,
  CallPartyAdded,
  CallPartyState,
  CallPartyMoved,
  CallPartyDeleted,

  RequestStartCallMonitoring,
  RequestStopCallMonitoring,

  RequestSendReturnReceipt,
  ReturnReceipt,


  RequestNetworkConsult,
  RequestNetworkAlternate,
  RequestNetworkTransfer,
  RequestNetworkMerge,
  RequestNetworkReconnect,
  RequestNetworkSingleStepTransfer,
  RequestNetworkPrivateService,
  NetworkCallStatus, 
  NetworkPrivateInfo,

  RequestTransactionMonitoring,
  TransactionStatus,
  
  MessageIDMAX
""")

CallMonitoringFields = Enum("""
  PartyState,          
  DN,
  CallUUID,
  NewCallUUID,
  RefCallUUID,
  PartyUUID,
  ISLinkList
""")  

CallMonitoringEvents = Enum("""
  CallCreated,          
  CallDataChanged,
  CallDeleted,
  CallPartyAdded,
  CallPartyState,
  CallPartyMoved,
  CallPartyDeleted
""")  


MediaType = Enum("""
  Voice      =   0,  
  VoIP       =   1,  
  EMail      =   2,
  VMail      =   3,  
  SMail      =   4,  
  Chat       =   5,
  Video      =   6,
  Cobrowsing =   7,
  Whiteboard =   8,
  AppSharing =   9,  
  WebForm    =  10,
  WorkItem   =  11,  

  Custom0    = 100   
""")



TMediaType = Enum("""
  TMediaVoice      =   0,  
  TMediaVoIP       =   1,  
  TMediaEMail      =   2,
  TMediaVMail      =   3,  
  TMediaSMail      =   4,  
  TMediaChat       =   5,
  TMediaVideo      =   6,
  TMediaCobrowsing =   7,
  TMediaWhiteboard =   8,
  TMediaAppSharing =   9,  
  TMediaWebForm    =  10,
  TMediaWorkItem   =  11,  

  TMediaCustom0    = 100   
""")



TPartyState = Enum("""
  PtState_NULL         =          0,

  PtState_Initiated    =     0x0001,
  PtState_Queued       =     0x0009,
  PtState_Alerting     =     0x000A,
  PtState_Busy         =     0x000B,
  PtState_Connected    =     0x000C,
  PtState_Held         =     0x000E,
  PtState_Failed       =     0x000F,

  PtState_NoListen     =     0x0010,
  PtState_NoTalk       =     0x0020,
  PtState_Bridged      =     0x0040,
  PtState_Audit        =     0x0080,
  PtState_SvcObserving =     0x00A0,

  PtState_TreatmentReq =     0x0100,
  PtState_Treatment    =     0x0200,
  PtState_Routing      =     0x0800,

  PtStateMod_Dialing   =    0x10000,
  PtStateMod_Uncertain =    0x20000
""")

def translatePartyStateToString(partyState):
  vals = [partyState & 0xF, partyState & 0xF0, partyState & 0xF00, partyState & 0xF0000]
  str = ""
  for v in vals:
    if v:
      val = ValToEnumElem(TPartyState, v)
      str = str + " + " + `val`
  if str: str = str [3:] 
  else: str = "PtState_NULL"
  return str

TDNState = Enum("""
  DNStateUnknown      = 0,
  DNStateOk           = 1,
  DNStateVirtual      = 2,
  DNStateOutOfService = 3
""")


TReliability = Enum("""
  TReliabilityOk        = 0,
  TReliabilityInPast    = 1,
  TReliabilityUncertain = 2
""")

Cause = Enum("""
  CauseEMPTY         =  0,
  CauseACD           =  1,
  CauseBusy          =  2,
  CauseNoAnswer      =  3,
  CauseReject        =  4,
  CauseRoute         =  5,
  CauseCoverage      =  6,
  CauseConverseOn    =  7,
  CauseForward       =  8,
  CauseRedirect      =  9,
  CauseTransfer      = 10,
  Cause1stepTransfer = 11,
  CauseConference    = 12,
  CauseAMdetected    = 13,
  CauseFaxDetected   = 14,
  CauseSITdetected   = 15
""")

MonitorNextCallType = Enum("""
  MonitorOneCall,
  MonitorAllCalls
""") 



NetworkCallState = Enum("""
  NetworkCallStateUnknown      = 0,
  NetworkCallStateConsulting   = 1,
  NetworkCallStateConsultHeld  = 2,
  NetworkCallStateTransferred  = 3,
  NetworkCallStateConferenced  = 4,
  NetworkCallStateReconnected  = 5,
  NetworkCallStateDisconnected = 6,
  NetworkCallStateNull         = 7
""")

NetworkDestState = Enum("""
  NetworkDestStateUnknown     = 0,
  NetworkDestStateRouting     = 1,
  NetworkDestStateDelivering  = 2,
  NetworkDestStateNoParty     = 3,
  NetworkDestStateOk          = 4
""")


SetOpType = Enum("""
  CreateCallInfo,
  SetCallInfo,
  DeleteCallInfo,
  AddParty,
  DeleteParty,
  CallInfoUpdate
""")

TRegMode = Enum("""
  RegModeDefault               = 0x01,
  RegModeMonitor               = 0x02,
  RegModeControl               = 0x04,
  RegModeNoSync                = 0x08,
  RegModeNoCallEvents          = 0x20, 
  RegModeNoPartyEvents         = 0x10, 
  RegModeNoInternalPartyEvents = 0x40 
""")

SubscriptionOperationType = Enum("""
  SubscriptionStart,
  SubscriptionStop,
  SubscriptionModify,
  SubscriptionOperationTypeIDMAX
""")

SipOperation = Enum("""
  Joined,
""")
# end tlib

#router lib
RouterEventName = Enum("""
  EventDebug, 
  EventError, 
  EventExecutionAck, 
  EventExecutionError, 
  EventExecutionInProgress ,
  EventInfo,
  EventShutdown
""")

RouterCdnStatus = Enum("""
  Released,
  Loaded
""")

RouterErrorCode = Enum("""
  NoError,
  SyntaxError,
  NotOwner,
  NotUser,
  NotAvailable,
  IOError,
  MaxClients,
  Rejected,
  DefaultRouting,
  NoCall,
  InterpError
""")

RouterStatisticUsage = Enum("""
  Any,
  Max,
  Min
""")
#end routerlib

#statlib
SObjectType = Enum("""
  Agent,
  AgentPlace,
  GroupAgents,
  GroupPlaces,
  RoutePoint,
  Queue,
  GroupQueues,
  Switch,
  RegDN,
  Campaign,
  CampaignGroup,
  CallingList,
  CampaignCallingList,
  Tenant,
  StagingArea,
  RoutingStrategy,
  Workbin
""")

SStatType = Enum("""
  Any,
  Current,
  Historical
           
""")

#Immediate
#Periodical
#NoNotification
#Reset
SNotificationMode = Enum("""
  SChangesBasedNotification,    
  STimeBasedNotification,
  SNoNotification,
  SResetBasedNotification 
""")

SStatisticProfile = Enum("""
  StatTypes,
  TimeProfiles,
  Filters,  
  TimeRanges
""")

SDataStreamType = Enum("""
  Broadcast,
  Unicast,
""")

SEventName = Enum("""

   SEventServerDisconnected,  
   SEventError,               
   SEventInfo,                
   SEventStatClosed,          
   SEventServerProfile,       
   SUserEvent,                
   SUserEventClosed,          
   SEventServerConnected,     
   SEventServerNotConnected,  
   SEventStatValid,
   SEventStatInvalid,
   SEventRegistered,  
   SEventServerStatistics,
   SEventDataStreamOpeningFailure,
   SEventDataStreamOpened,
   SEventDataStreamMessage,
   SEventDataStreamClosed,
   SEventCurrentTargetState_Snapshot,
   SEventCurrentTargetState_TargetAdded,
   SEventCurrentTargetState_TargetUpdated,
   SEventCurrentTargetState_TargetRemoved,
   SEventBatchCommands, 
   SEventStatOpened,
   SEventRunModeInfo,
   SEvent_SCA_ActionSpaceCreated,
   SEvent_SCA_ActionSpaceDestroyed,
   SEvent_SCA_ActionStarted,
   SEvent_SCA_ActionEnded,
   SEvent_SCA_ActionDataChanged,
   SEvent_SCA_ActionInstantDone,
   SEvent_SCA_Error   
""")

SStatisticSubject = Enum("""
   DNAction,
   DNStatus,
   AgentStatus,
   PlaceStatus,
   GroupStatus,
   CampaignAction
""")

   
SStatisticCategory = Enum("""
  TotalTime,
  TotalNumber,
  AverageTime,
  MaxTime,
  MinTime,
  ElapsedTimePercentage,
  RelativeTimePercentage,
  RelativeNumberPercentage,
  TotalNumberInTimeRange,
  TotalNumberInTimeRangePercentage,
  CurrentState,
  CurrentTime,
  CurrentNumber,
  CurrentMaxTime,
  CurrentMinTime,
  CurrentAverageTime,
  CurrentRelativeTimePercentage,
  CurrentRelativeNumberPercentage,
  CurrentNumberInTimeRange,
  CurrentNumberInTimeRangePercentage,
  TotalNumberPerSecond,
  EstimTimeToEndCurrentNumber,
  ServiceFactor1,
  LoadBalance1,
  TotalNumberErrors,
  TotalCustomValue,
  AverageCustomValue,
  MinCustomValue,
  MaxCustomValue,
  CurrentCustomValue,
  CurrentAverageCustomValue,
  CurrentMinCustomValue,
  CurrentMaxCustomValue,
  EstimWaitingTime,
  LoadBalance,
  RelativeNumber,
  EstimTimeToComplete,
  AverageOfCurrentNumber,
  AverageOfCurrentTime,
  TotalAdjustedTime,
  TotalAdjustedNumber,
  CurrentStateReasons,
  JavaCategory,
  AverageNumberPerRelativeHour,
  CurrentTargetState,
  TotalTimeInTimeRange,
  MinNumber,
  MaxNumber,
  CurrentDistinctNumber,
  CurrentContinuousTime,
  Formula,
  TotalDistinctTime
""")

SInterval = Enum("""
  SGrowingWindow    = 0,	
  SSinceLogin       = 1,  
  SSlidingWindow    = 2,	
  SSlidingSelection = 3   
""")

#end statlib
Days = Enum("""
  Sunday,
  Monday,
  Tuesday,
  Wednesday,
  Thursday,
  Friday,
  Saturday 
""")

Months = Enum("""
  January  = 1,
  February, 
  March, 
  April, 
  May, 
  June, 
  July, 
  August, 
  September, 
  October, 
  November, 
  December, 
""")
#-----------------------------
#Start SCS

SCSEventName = Enum("""
   StatusInfoMessage=1,
   AppWorkModeChanged,
   ActiveAlarm,
   ErrorMessage,
   ClientRegistered,
   ClientConnected,
   ClientDisconnected,
   KPLResponse,
   XResponse,
   AppCustomInfo,
   EnvironmentState   
   
""")   

AppLiveStatus =  Enum("""
  SCS_APP_STATUS_UNKNOWN = 0,
  SCS_APP_STATUS_STOPPED,
  SCS_APP_STATUS_STOP_TRANSITION,
  SCS_APP_STATUS_STOP_PENDING,
  SCS_APP_STATUS_START_TRANSITION,
  SCS_APP_STATUS_START_PENDING,
  SCS_APP_STATUS_RUNNING,
  SCS_APP_STATUS_INITIALIZING, 
  SCS_APP_STATUS_SERVICE_UNAVAILABLE 
""")

SolutionLiveStatus =  Enum("""
  SCS_SOL_STATUS_UNKNOWN = 0,
  SCS_SOL_STATUS_STOPPED,
  SCS_SOL_STATUS_STOP_PENDING,
  SCS_SOL_STATUS_START_PENDING,
  SCS_SOL_STATUS_STOP_TRANSITION,
  SCS_SOL_STATUS_START_TRANSITION,
  SCS_SOL_STATUS_RUN_PENDING,
  SCS_SOL_STATUS_RUNNING,
  SCS_SOL_STATUS_STARTED
""")

AppRunMode = Enum ("""
  UNKNOWN = -1,
  APP_RUNMODE_PRIMARY = 0,    
  APP_RUNMODE_BACKUP,     
  APP_RUNMODE_EXIT,       
  APP_RUNMODE_BACKUPHOT,  
  APP_RUNMODE_BACKUPWARM  
""")

AlarmStatus = Enum("""
  ACTIVE_ALARM_CREATED,
  ACTIVE_ALARM_DELETED
""")

DeamonLiveStatus = Enum("""
  SCS_HOST_STATUS_UNKNOWN = 0,
  SCS_HOST_STATUS_DISCONNECTED,
  SCS_HOST_STATUS_RUNNING
""")

SCSControlObjectType = Enum("""
  Unknown = 0,
  Solution = 8,
  Application = 9,
  Host = 10,
  AlarmCondition = 34
""")

ReactionType = Enum("""
  Reaction_NoReaction=0,
  Reaction_StartApp,
  Reaction_StopApp,
  Reaction_RestartApp,
  Reaction_StartService,
  Reaction_StopService,
  Reaction_ChangeLogLevel,
  Reaction_SendEmail,
  Reaction_SendSnmpTrap, 
  Reaction_SwitchToBackup, 
  Reaction_ExecuteOSCommamd 
""")

SCSErrorCode = Enum("""
  Undefined = 0,
  ApplicationNotStarted = 1,
  ApplicationNotStopped = 2,
  ApplicationNotReady = 3,
  ApplicationAlreadyExists = 4,
  ObjectNotFound = 5,
  DeamonNotStarted = 6,
  AlreadyInProgress = 7,
  OperatingSystemError = 8,
  UnableToExecute = 9,
  InternalError = 10,
  IncorrectClientCode = 11,
  NotImplemented = 12,
  HotBackupLimitations = 13,
  ApplicationHostConflict = 14
""")

LCAEventName = Enum("""
  EventChangeExecutionMode, 
  LcaEvent
""")

LogLevel = Enum("""
  LOG_LEVEL_ALL,      
  LOG_LEVEL_DEBUG,
  LOG_LEVEL_INFO,
  LOG_LEVEL_INTERACTION,
  LOG_LEVEL_ERROR,
  LOG_LEVEL_ALARM,    
  LOG_LEVEL_NONE  
""")



LogCategory = Enum("""
    LOG_CATEGORY_DEFAULT = 0,               
    LOG_CATEGORY_APP = 0,
    LOG_CATEGORY_ALARM, 
    LOG_CATEGORY_AUDIT  
""")



#End SCS
#--------------------------
#Start CFG
CfgObjectType  = Enum("""
  CFGNoObject,                 
  CFGSwitch,                   
  CFGDN,                       
  CFGPerson,                   
  CFGPlace,                    
  CFGAgentGroup,               
  CFGPlaceGroup,               
  CFGTenant,                   
  CFGService,                  
  CFGApplication,              
  CFGHost,                     
  CFGPhysicalSwitch,           
  CFGScript,                   
  CFGSkill,                    
  CFGActionCode,               
  CFGAgentLogin,               
  CFGTransaction,              
  CFGDNGroup,                  
  CFGStatDay,                  
  CFGStatTable,                
  CFGAppPrototype,             
  CFGAccessGroup,              
  CFGFolder,                   
  CFGField,                    
  CFGFormat,                   
  CFGTableAccess,              
  CFGCallingList,              
  CFGCampaign,                 
  CFGTreatment,                
  CFGFilter,                   
  CFGTimeZone,                 
  CFGVoicePrompt,              
  CFGIVRPort,                  
  CFGIVR,                      
  CFGAlarmCondition,   
  CFGEnumerator,
  CFGEnumeratorValue,
  CFGObjectiveTable,
  CFGCampaignGroup,
  CFGGVPReseller,
  CFGGVPCustomer,
  CFGGVPIVRProfile,
  CFGScheduledTask,
  CFGRole ,
  CFGPersonLastLogin    
  CFGMaxObjectType  = 1000     
""")

CfgTraceMode  = Enum("""
  CFGTMNoTraceMode,   
  CFGTMNone,          
  CFGTMLocal,         
  CFGTMRemote,        
  CFGTMBoth
""")

CfgOSType  = Enum("""  
  CFGNoOS,                 
  CFGSolaris,              
  CFGSolarisX86,           
  CFGDigitalUNIX,          
  CFGHPUX,                 
  CFGAIX,                  
  CFGSunOS,                
  CFGWinNT,                
  CFGWindows,              
  CFGOS2,                  
  CFGMacintosh,            
  CFGTandemUNIX,           
  CFGUnixWare,             
  CFGWindows2000,          
  CFGWindowsXP,
  CFGWindowsServer2003,
  CFGRedHatLinux,
  CFGWindowsServer2008,
  CFGWindowsVista,  
""")

CfgOperationMode  = Enum("""    
  CFGOMNoOperationMode,  
  CFGOMManual,           
  CFGOMSchedule
""")
  
CfgHAType  = Enum("""
  CFGHTNoHAType,   
  CFGHTColdStanby, 
  CFGHTWarmStanby, 
  CFGHTHotStanby  
""")

CfgFlag = Enum("""
  Unknown,
  False,
  True
""")

CfgDNRegisterFlag = Enum("""
  CFGDRUnknown,
  CFGDRFalse,
  CFGDRTrue,
  CFGDROnDemand
""")


CfgAppType = Enum("""
  CFGUnknown,              
  CFGTServer,              
  CFGStatServer,           
  CFGBillingServer,        
  CFGBillingClient,        
  CFGAgentView,            
  CFGVoiceTreatmentServer, 
  CFGVoiceTreatmentManager,
  CFGDBServer,             
  CFGCallConcentrator,     
  CFGSDialer,              
  CFGListManager,          
  CFGCMServer,             
  CFGCMClient,             
  CFGLME,                  
  CFGRouterServer,         
  CFGStrategyBuilder,      
  CFGStrategyLoader,       
  CFGAgentDesktop,         
  CFGSCE,                  
  CFGCCView,               
  CFGConfigurationServer,  
  CFGThirdPartyApp,        
  CFGThirdPartyServer,     
  CFGStrategySimulator,    
  CFGStrategyScheduler,    
  CFGDARTServer,           
  CFGDARTClient,           
  CFGCustomServer,         
  CFGExternalRouter,       
  CFGVirtual Interactive-T,
  CFGVirtualRP,            
  CFGDatabase,             
  CFGNetVector,            
  CFGDetailBiller,         
  CFGSummaryBiller,        
  CFGNACD,                 
  CFGBackUpControlClient,  
  CFGInfomartStatCollector,     
  CFGInfomartStatConfigurator,  
  CFGIVRInterfaceServer,        
  CFGIServer,                   
  CFGMessageServer,             
  CFGSCS,                       
  CFGSCI,                       
  CFGSNMPAgent,                 
  CFGRealDBServer,              
  CFGWFMClient,                 
  CFGWFMDataAggregator,         
  CFGWFMWebServices,            
  CFGWFMScheduleServer,         
  CFGInteractionRoutingDesigner,
  CFGETLProxy,                  
  CFGITCUtility,                
  CFGVSSServer,                 
  CFGVSSSystem,                 
  CFGVSSShared,                 
  CFGVSSConsoleCfg,             
  CFGCCAnalizerDataMart,        
  CFGChatServer,                
  CFGCallbackServer,            
  CFGCoBrowsingServer,          
  CFGISTransportServer,         
  CFGContactServer,             
  CFGEmailServer,               
  CFGMediaLink,                 
  CFGWebInteractionRequestsServer,
  CFGWebStatServer,             
  CFGWebInteractionServer,      
  CFGWebOptionRoutePoint,       
  CFGWebClient,                 
  CFGContactServerManager,      
  CFGContentAnalyzer,           
  CFGResponseManager,           
  CFGVoIPController,            
  CFGVoIPDevice,                
  CFGAutomatedWorkflowEngine,   
  CFGHAProxy,                   
  CFGVoIPStreamManager,         
  CFGVoIPDMXServer,
  CFGWebAPIServer,                 
  CFGLoadBalancer,                 
  CFGApplicationCluster,          
  CFGLoadDistributionServer,       
  CFGGProxy,                       
  CFGGIS,                          
  CFGAgentDesktopDeliveryServer,   
  CFGGCNClient,                    
  CFGIVRDT,                        
  CFGGCNThinServer,                
  CFGClassificationServer,         
  CFGTrainingServer,               
  CFGUniversalCallbackServer,      
  CFGCPDServerProxy,               
  CFGXLinkController,              
  CFGKWorkerPortal,                
  CFGWFMServer,                    
  CFGWFMBuilder,                   
  CFGWFMReports,                   
  CFGWFMWeb,                       
  CFGKnowledgeManager,
  CFGIVRDriver                          = 101,
  CFGIVRLibrary                         = 102,
  CFGLCSAdapter                         = 103,
  CFGDesktopNETServer                   = 104,
  CFGSiebel7ConfSynchComponent          = 105,
  CFGSiebel7CampSynchComponent          = 106,
  CFGGenericServer                      = 107,
  CFGGenericClient                      = 108,
  CFGCallDirector                       = 109,
  CFGSIPCommunicationServer             = 110,
  CFGInteractionServer                  = 111,
  CFGIntegrationServer                  = 112,
  CFGWFMDaemon                          = 113,
  CFGGVPPolicyManager                   = 114,
  CFGGVPCiscoQueueAdapter               = 115,
  CFGGVPTextToSpeechServer              = 116,
  CFGGVPASRLogManager                   = 117,
  CFGGVPBandwidthManager                = 118,
  CFGGVPEventsCollector                 = 119,
  CFGGVPCacheServer                     = 120,
  CFGGVPASRLogServer                    = 121,
  CFGGVPASRPackageLoader                = 122,
  CFGGVPIPCommunicationServer           = 123,
  CFGGVPResourceManager                 = 124,
  CFGGVPSIPSessionManager               = 125,
  CFGGVPMediaGateway                    = 126,
  CFGGVPSoftSwitch                      = 127,
  CFGGVPCoreService                     = 128,
  CFGGVPVoiceCommunicationServer        = 129,
  CFGGVPUnifiedLoginServer              = 130,
  CFGGVPCallStatusMonitor               = 131,
  CFGGVPReporter                        = 132,
  CFGGVPH323SessionManager              = 133,
  CFGGVPASRLogManagerAgent              = 134,
  CFGGVPGenesysQueueAdapter             = 135,
  CFGGVPIServer                         = 136,
  CFGGVPSCPGateway                      = 137,
  CFGGVPSRPServer                       = 138,
  CFGGVPMRCPTTSServer                   = 139,
  CFGGVPCCSServer                       = 140,
  CFGGVPMRCPASRServer                   = 141,
  CFGGVPNetworkMonitor                  = 142,
  CFGGVPOBNManager                      = 143,
  CFGGVPSelfServiceProvisioningServer   = 144,
  CFGGVPMCP                             = 145,
  CFGGVPFetchingModule                  = 146,
  CFGGVPMCPLegacyInterpreter            = 147,
  CFGGVPCCP                             = 148,
  CFGGVPResourceMgr                     = 149,
  CFGGVPClusterMgr                      = 150,
  CFGGVPMediaServer                     = 151,
  CFGGVPPSTNConnector                   = 152,
  CFGGVPReportingSever                  = 153,
  CFGGVPASG                             = 154,
  CFGGVPCTIConnector                    = 155,
  CFGResourceAccessPoint                = 156,
  CFGInteractionWorkspace               = 157,
  CFGAdvisors                           = 158,
  CFGESSExtensibleServices              = 159,
  CFGCustomerView                       = 160,
  CFGOrchestrationServer                = 161,
  CFGReserved                           = 162,
  CFGCapturePoint                       = 163,
  CFGRulesESPServer                     = 164,
  CFGGenesysAdministrator               = 165,
  CFGiWDManager                         = 166,
  CFGiWDRuntimeNode                     = 167,
  CFGBusinessRulesExecutionServer       = 168,
  CFGBusinessRulesGUI                   = 169,
  CFGVPPolicyServer                     = 170,
  CFGSocialMS                           = 171,
  CFGCSTAConnector                      = 172,
  CFGVPMRCPProxy                        = 173,  
""")


CfgRouteType = Enum("""
  CFGNoRoute,                  
  CFGDefault,                  
  CFGLabel,                    
  CFGOverwriteDNIS,            
  CFGDDD,                      
  CFGIDDD,                     
  CFGDirect,                   
  CFGReject,                   
  CFGAnnouncement,             
  CFGPostFeature,              
  CFGDirectAgent,              
  CFGUseExternalProtocol,      
  CFGGetFromDN,                
  CFGXRouteTypeDefault,        
  CFGXRouteTypeRoute,          
  CFGXRouteTypeDirect,         
  CFGXRouteTypeReroute,        
  CFGXRouteTypeDirectUUI,      
  CFGXRouteTypeDirectANI,      
  CFGXRouteTypeDirectNoToken,  
  CFGXRouteTypeDNISPooling,    
  CFGXRouteTypeDirectDNISnANI, 
  CFGXRouteTypeDirectDigits,   
  CFGXRouteTypeForbidden,
  CFGXRouteTypeISCCProtocol,
  CFGXRouteTypePullBack,
  CFGXRouteTypeDirectNetworkCallID
""")


CfgDialMode = Enum("""
  CFGDMNoDialMode,        
  CFGDMPredict,          
  CFGDMProgress,         
  CFGDMPreview,          
  CFGDMProgressAndSeize, 
  CFGDMPredictAndSeize,  
  CFGDMPower,            
  CFGDMPowerAndSeize,    
  CFGDMPushPreview,      
  CFGDMProgressGVP,      
  CFGDMPredictGVP,       
  CFGDMPowerGVP,         
""")


CfgOptimizationMethod = Enum("""
  CFGOMNoOptimizationMethod,  
  CFGOMBusyFactor,            
  CFGOMOverdialRate,          
  CFGOMWaitTime
""")

CfgRank= Enum(""" 
  CFGNoRank,                 
  CFGUser,                   
  CFGDesigner,               
  CFGTenantAdministrator,    
  CFGServiceAdministrator,   
  CFGSuperAdministrator
""")


GrpCampState = Enum("""
  Unknown = -1,
  CM_GCS_NotLoaded, 
  CM_GCS_WaitingUnload,
  CM_GCS_UnloadInProgress,
  CM_GCS_InActive,
  CM_GCS_Active,
  CM_GCS_Running
""")

CfgRecActionCode = Enum("""
  CFGRACNoRecActionCode,       
  CFGRACMarkDB,                
  CFGRACMarkAllChain,          
  CFGRACCycle,                 
  CFGRACRetryIn,               
  CFGRACRetryAtDate,           
  CFGRACNextInChain,           
  CFGRACNextInChainAfter,      
  CFGRACNextInChainAtDate,     
  CFGRACAssignToGroup,         
  CFGRACMarkAsAgentError,      
  CFGRACReschedule,            
  CFGRACMaxRecActionCode 
""")

CfgCallActionCode = Enum("""
  CFGCACNoCallActionCode,     
  CFGCACConnect,              
  CFGCACDrop,                 
  CFGCACMuteTransfer,         
  CFGCACTransfer,             
  CFGCACRoute,                
  CFGCACPlayMessage,          
  CFGCACSendFax,              
  CFGCACSendPage,             
  CFGCACSendEmail,            
  CFGCACMaxCallActionCode 
""") 

CfgObjectState = Enum("""
  CFGNoObjectState,   
  CFGEnabled,         
  CFGDisabled,        
  CFGDeleted,         
  CFGMaxObjectState       
""" )


CfgTargetType = Enum("""
  CFGNoTarget,
  CFGTargetAgent,
  CFGTargetPlace,
  CFGTargetAgentGroup,
  CFGTargetPlaceGroup,
  CFGTargetRoutingPoint,
  CFGTargetACDQueue,
  CFGTargetDestinationLabel,
  CFGTargetACDQueueGroup,
  CFGTargetExtRoutingPoint,
  CFGTargetISCC,
  CFGMaxTargetType
""")

CfgDNType = Enum("""
  CFGNoDN,                
  CFGExtension,           
  CFGACDPosition,         
  CFGACDQueue,            
  CFGRoutingPoint,        
  CFGVirtACDQueue,        
  CFGVirtRoutingPoint,    
  CFGEAPort,              
  CFGVoiceMail,           
  CFGCellular,            
  CFGCP,                  
  CFGFAX,                 
  CFGData,                
  CFGMusic,               
  CFGTrunk,               
  CFGTrunkGroup,          
  CFGTieLine,             
  CFGTieLineGroup,        
  CFGMixed,               
  CFGExtRoutingPoint,     
  CFGDestinationLabel,    
  CFGServiceNumber,       
  CFGRoutingQueue,        
  CFGCommDN,              
  CFGEmail,               
  CFGVoIP,                
  CFGVideo,               
  CFGChat,                
  CFGCoBrowse,            
  CFGVoIPService,         
  CFGWorkflow,
  CFGAccessResource,
  CFGGVPDID
""")
#BE CAREFUL about this enum, conflib contains 2 strings with value 7, I removed siemens
CfgSwitchType = Enum("""
  CFGNoSwitch,
  CFGNortelMeridian,
  CFGRockwellSpectrum,
  CFGRockwellGalaxy,
  CFGNortelDMS100,
  CFGLucentDefinityG3,
  CFGAspectCallCenter,
  CFGRolm9751CBX,
  CFGIntecomIBX80,
  CFGEricssonMD110,
  CFGLucent5ESS,
  CFGMadge,
  CFGNEC,
  CFGFujitsu,
  CFGHarrisVoiceFrame,
  CFGGateway01,
  CFGSiemensHicom150,
  CFGSiemensHicom300,
  CFGPhilipsSophoiS3000,
  CFGMatraMC6500,
  CFGSiemensHicom150H,
  CFGEricssonACP1000,
  CFGSiemensGECiSDX,
  CFGAlcatelA4400DHS3,
  CFGGenericSwitch,
  CFGDelcoACD,
  CFGHitachiCX8000,
  CFGLGStarex,
  CFGMitelSX2000,
  CFGNortelMeridianCallCenter,
  CFGSiemensHicom150E,
  CFGSiemensRealtisDX,
  CFGTadiranCoral,
  CFGVoIPSMCPSwitch,
  CFGVirtualSwitchIIF,
  CFGInternetGateway,
  CFGATT800ICPGateway,
  CFGSprintSiteRPGateway,
  CFGBellCanadaATFGateway,
  CFGAlcatelSCPGateway,
  CFGBellAtlanticISCPGateway,
  CFGConcert800Gateway,
  CFGAlcatelDTAGSCPGateway,
  CFGKPNNetworkGateway,
  CFGAlcatelTISCPGateway,
  CFGAlcatelBTSCPGateway,
  CFG3511ProtocolInterface,
  CFGDatavoiceDharma,
  CFGHuaweiCC08,
  CFGLucentIndexSDX,
  CFGSiemensHicom300H,
  CFGSiemensHiPath4000,
  CFGAlcatelA4200,
  CFGTenovisIntegral33,
  CFGTelera,
  CFGNGSN,
  CFGGenSpec,
  CFGVoicePortal,
  CFGKWGateway,
  CFGSiemensHicom300Real,
  CFGGenSpecXML,
  CFGOPSI,
  CFGCiscoCM,
  CFGMultimediaSwitch,
  CFGVerizonISCPGateway,
  CFGAlcatel5020OPSI,
  CFGAvayaIPOffice,
  CFGMitelMN3300,
  CFGSamsungIPPCXIAP,
  CFGSiemensHiPath3000,
  CFGEOneQueue,
  CFGTenovisI55,
  CFGSIPSwitch,
  CFGDigitroAXS20,
  CFGGVPDIDGroup,
  CFGSIPNetworkSwitch,
  CFGNECSV7000,
  CFGRadvisionIContact,
  CFGAvayaTSAPI,
  CFGHuaweiNGN,
  CFGCiscoUCCE,
  CFGBroadSoftBroadWorks
""")

CfgEventName = Enum("""
  CFGError, 
  CFGRegistered,
  CFGUnregistered,
  CFGObjectAdded, 
  CFGObjectDeleted,
  CFGObjectInfoChanged, 
  CFGObjectInfo,
  CFGObjectCount, 
  CFGEndObjectList,
  CFGDBDisconnected, 
  CFGDBConnected, 
  CFGServerDisconnected,
  CFGClientRegistered,
  CFGUnknownEvent,
  CFGAccessInfo,
  CFGAccessChanged,
  CFGBriefInfo,
  CFGAccountInfo, 
  CFGAccountChanged, 
  CFGACLBriefInfo,
  CFGEndHistoryLog,
  CFGOperationalModeSet,
  CFGOperationalMode,
  CFGObjectAddedToFolder,
  CFGObjectPermissions, 
  CFGExtObjectInfo,
  CFGReadConfigRegistered, 
  CFGReadConfigUnregistered,
  CFGReadConfig,
  CFGSchemaInfo,
  CFGFilterResult,
  CFGLocaleInfo,
  CFGALicense, 
  CFGReadAccessRegistered, 
  CFGReadAccessUnregistered,
  CFGAccessRead,
  CFGConfigServerInfo,
  CFGAuthenticated,
  CFGPasswordChanged,
  CFGLocaleChanged,           
  CFGReadLocaleRegistered,    
  CFGReadLocaleUnregistered,  
  CFGObjectsUpdated,          
  CFGSchemaChanged,           
  CFGUpdatePackagesInfo,      
  CFGLocaleSets,              
  CFGClientInfo,              
  CFGSchemaFile,              
  CFGServerProtocol,          
  CFGRouteTableInfo,          
  CFGRouteTableUpdated      
""")

CfgScriptType = Enum("""
  CFGNoScript,
  CFGDataCollection,
  CFGServiceSelection,
  CFGEnhancedQueuing,
  CFGScriptConfiguration,
  CFGSimpleRouting,
  CFGEnhancedRouting,
  CFGVoiceFile,
  CFGOutboundCampaign,
  CFGOutboundFormat,
  CFGOutboundList,
  CFGOutboundFilter,
  CFGOutboundTreatment,
  CFGOutboundAlert,
  CFGSchedule,
  CFGAlarmDetection,
  CFGAlarmReaction,
  CFGVssSystemSchema,
  CFGVssSharedSchema,
  CFGVssServerSchema,
  CFGVssObject,
  CFGEmailAckReceipt,
  CFGCapacityRule,
  CFGInteractionQueue,
  CFGInteractionQueueView,
  CFGInteractionWorkBin,
  CFGInteractionSubmitter,
  CFGInteractionSnapshot,
  CFGBusinessProcess,
  CFGSupervisorData,
  CFGInteractionWorkflowTrigger,
  CFGGVPReport,
  CFGOutboundSchedule,
  CFGESSDialPlan
""") 


CfgEnumeratorType = Enum("""
  CFGENTNoEnumeratorType,                
  CFGENTInteractionOperationalAttribute, 
  CFGENTRole,                            
  CFGENTContactAttribute,                
  CFGENTCustom,                          
""")

CfgIVRType = Enum("""
  CFGIVRTNoIVRType                      = 0,
  CFGIVRTConversant                     = 1,
  CFGIVRTWVRForAIX                      = 2,
  CFGIVRTDirectTalk6000                 = 2,
  CFGIVRTSyntellectVocalPoint           = 3,
  CFGIVRTSyntellectPremier              = 4,
  CFGIVRTSyntellectVista                = 5,
  CFGIVRTVoiceTek                       = 6,
  CFGIVRTAgility                        = 7,
  CFGIVRTMeridianIntegrated             = 8,
  CFGIVRTSymposiumOpen                  = 9,
  CFGIVRTEdify                          = 10,
  CFGIVRTBrite                          = 11,
  CFGIVRTShowNTel                       = 12,
  CFGIVRTIntervoiceBrite                = 13,
  CFGIVRTIntervoice                     = 13,
  CFGIVRTPeriphonics                    = 14,
  CFGIVRTAmerex                         = 15,
  CFGIVRTWVRForWindows                  = 16,
  CFGIVRTDirectTalkNT                   = 16,
  CFGIVRTGenesysVoicePlatform           = 17,
  CFGIVRTeleraGVP                       = 17,
  CFGIVRTMPS                            = 18,
  CFGIVRTAspectCSS                      = 19,
  CFGIVRTMSSpeechServer                 = 20,
  CFGIVRTOtherIVRType                   = 21,
  CFGIVRTEnvox                          = 22
""")

CfgAccessGroupType = Enum("""
  CFGNoAccessGroupType                  = 0,
  CFGDefaultGroup                       = 1,
  CFGUsersGroup                         = 2,
  CFGAdministratorsGroup                = 3,
  CFGSuperAdministratorsGroup           = 4,
  CFGSystemGroup                        = 5,
  CFGEveryoneGroup                      = 6
""")

CfgTransactionType  = Enum("""
  CFGTRTNoTransactionType               = 0,
  CFGTRTCallData                        = 1,
  CFGTRTBusinessAttribute               = 2,
  CFGTRTBusinessSituation               = 3,
  CFGTRTBusinessRule                    = 4,
  CFGTRTBusinessAction                  = 5,
  CFGTRTStatFilter                      = 16,
  CFGTRTStatTimeRange                   = 17,
  CFGTRTStatTimeProfile                 = 18,
  CFGTRTStatType                        = 19,
  CFGTRTStatMetric                      = 20,
  CFGTRTList                            = 21,
  CFGTRTMacro                           = 22
""")

CfgActionCodeType = Enum ("""
  CFGNoActionCode                       = 0,
  CFGInboundCall                        = 1,
  CFGOutboundCall                       = 2,
  CFGInternalCall                       = 3,
  CFGTransfer                           = 4,
  CFGConference                         = 5,
  CFGLogin                              = 6,
  CFGLogout                             = 7,
  CFGReady                              = 8,
  CFGNotReady                           = 9,
  CFGBusyOn                             = 10,
  CFGBusyOff                            = 11,
  CFGForwardOn                          = 12,
  CFGForwardOff                         = 13
""")

CfgDataType = Enum ("""
  CFGDTNoDataType                       = 0,
  CFGDTInt                              = 1,
  CFGDTFloat                            = 2,
  CFGDTChar                             = 3,
  CFGDTVarChar                          = 4,
  CFGDTDateTime                         = 5
""")

CfgFieldType = Enum ("""
  CFGFTNoFieldType                      = 0,
  CFGFTRecordID                         = 1,
  CFGFTPhone                            = 2,
  CFGFTRecordType                       = 3,
  CFGFTRecordStatus                     = 4,
  CFGFTDialResult                       = 5,
  CFGFTNumberOfAttempts                 = 6,
  CFGFTScheduledTime                    = 7,
  CFGFTCallTime                         = 8,
  CFGFTFrom                             = 9,
  CFGFTUntil                            = 10,
  CFGFTTimeZone                         = 11,
  CFGFTCampaignID                       = 12,
  CFGFTAgentID                          = 13,
  CFGFTChainID                          = 14,
  CFGFTNumberInChain                    = 15,
  CFGFTCustomField                      = 16,
  CFGFTANI                              = 17,
  CFGFTLATA                             = 18,
  CFGFTNPA                              = 19,
  CFGFTNPA_NXX                          = 20,
  CFGFTStateCode                        = 21,
  CFGFTInfoDigits                       = 22,
  CFGFTCountryCode                      = 23,
  CFGFTPhoneType                        = 24,
  CFGFTGroupDBID                        = 25,
  CFGFTAppDBID                          = 26,
  CFGFTTreatments                       = 27,
  CFGFTMediaRefference                  = 28,
  CFGFTEmailSubject                     = 29,
  CFGFTEmailTemplateID                  = 30,
  CFGFTSwitchID                         = 31
""")

CfgObjectiveTableType = Enum ("""
  CFGOTTNoType                          = 0,
  CFGOTTDefault                         = 1,
  CFGOTTCostContract                    = 2
""")

CfgTableType = Enum("""
  CFGTTNoTableType                      = 0,
  CFGTTCallingList                      = 1,
  CFGTTLogTable                         = 2,
  CFGTTANI                              = 3,
  CFGTTLATA                             = 4,
  CFGTTNPA                              = 5,
  CFGTTNPA_NXX                          = 6,
  CFGTTStateCode                        = 7,
  CFGTTInfoDigits                       = 8,
  CFGTTCountryCode                      = 9,
  CFGTTCustomType                       = 10,
  CFGTTDoNotCallList                    = 11,
  CFGTTEmailContactLists                = 12
""")

CfgDNGroupType = Enum("""
  CFGNoDNGroup                          = 0,
  CFGSinglePorts                        = 1,
  CFGACDQueues                          = 2,
  CFGRoutingPoints                      = 3,
  CFGNetworkPorts                       = 4,
  CFGServiceNumbers                     = 5
""")

CfgOperationalMode = Enum("""
  CFGOperationalNoMode                  = 0,
  CFGOperationalFullMode                = 1,
  CFGOperationalReadOnlyMode            = 2,
""")
#End CFG
#----------------------------
#Start Outbound

CMEventName = Enum("""
  MSGCFG_NONE,                   
  MSGCFG_UNKNOWN,                
  MSGCFG_ERROR,                  
  MSGCFG_CLIENTREGISTER,         
  MSGCFG_DISCONNECTED,           
  CM_UnknownMessage,             
  CM_ReqRegisterClient,          
  CM_ReqLoadCampaign,            
  CM_ReqUnloadCampaign,          
  CM_ReqStartDialing,            
  CM_ReqStopDialing,             
  CM_ReqSetDialingMode,          
  CM_ReqGetCampaignStatus,       
  CM_ReqCampaignRegistered,      
  CM_ReqCampaignUnregistered,    
  CM_EvServerConnected,          
  CM_EvServerDisconnected,       
  CM_EvClientDisconnected,       
  CM_EvClientReqistred,          
  CM_EvCampaignLoaded,           
  CM_EvCampaignUnloaded,         
  CM_EvDialingStarted,           
  CM_EvDialingStopped,           
  CM_EvDialingModeChanged,       
  CM_EvCampaignStatus,           
  CM_EvCampaignRegistered,       
  CM_EvCampaignUnregistered,     
  CM_EvError,   
  CM_ReqCommDNGetCampaignData,
  CM_ReqForceUnloadCampaign,
  CM_ReqCancelRecord,
  CM_EvRecordCanceled,
  CM_ReqDoNotCall,
  CM_EvDoNotCallProcessed,
  CM_MAX_MESSAGE                 
""")

CMStatEventName = Enum("""
  ST_EvCampaignActivated = 1,                   
  ST_EvCampaignDeactivated = 2,                
  ST_EvDialingStarted = 3,                  
  ST_EvDialModeChanged = 4,         
  ST_EvDialingStopped = 5,
  ST_EvWaitingAgentsStart = 6,
  ST_EvWaitingAgentsOver = 7,
  ST_EvWaitingPortsStart = 8,
  ST_EvWaitingPortsOver = 9,
  ST_EvWaitingRecordsStart = 10,
  ST_EvWaitingRecordsOver = 11,
  ST_EvSystemErrorStart = 12,
  ST_EvSystemErrorOver = 13,
  ST_EvCallCompleted = 14,
  ST_EvLeadProcessed = 15,
  ST_EvCallbackScheduled = 16,
  ST_EvCallbackCompleted = 17,
  ST_EvCallbackMissed = 18,
  ST_EvAgentError = 19,
  ST_EvRecordScheduled = 20
""")


DataSourcerEventType = Enum("""
  Activate = 1,
  Deactivate = 2
""")

SDEventType = Enum("""
  SDServerConnected,  
  SDServerDisconnected, 
  SDCallProgress,      
  SDRequestResponse,   
  SDEventError,
  SDHWDataEvent,
  SDChannelsUpdated,
  SDChannelsReleased,
  SDClientRegistered
""")

SDCallStatus = Enum("""
  SDCStNoStatus,    
  SDCStTransferred, 
  SDCStDropped,     
  SDCStAbandoned,   
  SDCStReleased,    
  SDCStDialError  
""")


SDLibError = Enum("""
  SDLibNoError ,          
  SDLibInvalidParameter,  
  SDLibFileReadError,     
  SDLibOptionNotFound,    
  SDLibConnectError,      
  SDLibServerNotFound,    
  SDLibMemAllocError,     
  SDLibPackMsgError,      
  SDLibWriteError,
  SDLibInternalError
""") 


 #treat all answers as a live voice  */
 #try to recognize all except AM */
 #recognize all */
 #recognize all, use for AM more precise method */
 #(default) - use Dialogic preset configuration */
 #Accuracy decision on PAMD */

SDialerAnswerTypeRecognition = Enum("""
  NoTypeRecognition,              
  NoAMRecognition,                
  PositiveAMRecognition,          
  FullPositiveAMRecognition,      
  TelephonyPreset,                
  AccuratePositiveAMRecognition   
""")

SDialerTransferType = Enum("""
  OneStepTransfer,
  TwoStepTransfer
""")
#End Outbound
#----------------------------
#Siebel

SiebelEventType = Enum("""
  TEvent,
  IEvent,
  CustomEvent,
  OutbEvent
""")

CustomEvents = Enum("""
  EventKwError,
  EventKwOnCallResponse,
  EventCurrentWorkItemChanged
 """)
OutbEvents = Enum(""" 
  EventCampaignLoaded,
  EventCampaignUnloaded,     
  EventCampaignStarted,        
  EventCampaignStopped,        
  EventCampaignModeChanged,      

  EventPreviewDialingModeStartAcknowledge, 
  EventPreviewDialingModeOverAcknowledge,  
  EventPreviewRecord,        
  EventPreviewRecordEmpty,     

  EventUpdateCallCompletionStatsAcknowledge,

  EventRecordProcessedAcknowledge,
  EventPreviewRecordProcessedAcknowledge,
  EventPredictRecordProcessedAcknowledge,

  EventRecordRejectAcknowledge,        
  EventPreviewRecordRejectAcknowledge,       
  EventPredictRecordRejectAcknowledge,       

  EventRecordCancelAcknowledge,        
  EventPreviewRecordCancelAcknowledge,       
  EventPredictRecordCancelAcknowledge,       

  EventRecordRescheduleAcknowledge,      

  EventScheduledRecordRescheduleAcknowledge,

  EventScheduledCal,        
  EventPreviewScheduledCall,       
  EventPredictScheduledCall,       

  EventDoNotCallAcknowledge,       
  EventPreviewDoNotCallAcknowledge,        
  EventPredictDoNotCallAcknowledge,        
  EventChainedRecord,        
  EventChainedRecordsDataEnd,    
  EventRecordCancel,       
  EventPreviewRecordCancel,        
  EventPredictRecordCancel,        
  EventAddRecordAcknowledge,       
  EventOCSError, 
  EventChainedWorkItemChanged,
  EventRecordRemove
""")  
SiebTEvents = Enum("""
  EventDialing,
  EventRinging,
  EventEstablished,
  EventReleased,
  EventAbandoned,
  EventDestinationBusy,
  EventHeld,
  EventRetrieved,
  EventUserDataChanged,
  EventRegistered,
  EventUnregistered,
  EventCallForwardSet,
  EventCallForwardCancel,
  EventAgentBusy,
  EventAgentNotBusy,
  EventAgentLogin,
  EventAgentLogout,
  EventAgentReady,
  EventAgentNotReady,
  EventServerConnected,
  EventServerDisconnected,
  EventError,
  EventACK,
  EventUserEvent,
  EventPartyChanged,
  EventPartyAdded,
  EventPartyDeleted,
  EventPartyInfo,
  EventDNOutOfService,
  EventDNBackInService,
  EventOnHook,
""")

def TranslateSiebelTEventNameToTEventName(eventName):
  if eventName[5:] in EventName.members:
    return eventName[5:]
  if eventName == "EventCallForwardSet": return "ForwardSet"
  if eventName == "EventCallForwardCancel": return "ForwardCancel"
  if eventName == "EventAgentBusy": return "DNDOn"
  if eventName == "EventAgentNotBusy": return "DNDOff"
  if eventName == "EventUserDataChanged": return "AttachedDataChanged"

def TranslateTEventNameToSiebelTEventName(eventName):
  if ("Event" + eventName) in SiebTEvents.members:
    return "Event" + eventName
  if eventName == "ForwardSet": return "EventCallForwardSet"
  if eventName == "ForwardCancel": return "EventCallForwardCancel"
  if eventName == "DNDOn": return "EventAgentBusy"
  if eventName == "DNDOff": return "EventAgentNotBusy"
  if eventName == "AttachedDataChanged": return "EventUserDataChanged"
  #EventAgentBusy -??  


SiebIEvents = Enum("""
  CacheCommandInformation,
  IndicateNewWorkItem,
  WorkItemReleased,
  WorkItemSuspended,
  WorkItemResumed,
  WorkItemStarted,
  ShowStatusText,
  UpdateObjectInformation
""")

SCCommandFlag =  Enum("""
  SC_CF_NOTSUPPORTED  = 1,
  SC_CF_DISABLED      = 2,
  SC_CF_CHECKED       = 4,
  SC_CF_BLINKING      = 8,
  SC_CF_NOPARAMSOK    = 16,
  SC_CF_STRPARAMSOK   = 32
""")

VCBType = Enum("""
  ASAP      = 1,
  Scheduled = 2
""")

VCBEventName = Enum("""
  RequestCallbackServiceStatus,
  RequestCallbackQuery,
  RequestCallbackQueryResult,
  RequestCallbackCancel,
  RequestCallbackReschedule,
  RequestCallbackAdd,
  RequestCallback,
  RequestCallbackProcessed,
  RequestCallbackReject,
  RequestCallbackSubmit,
  RequestCallbackPreview
""")
#-----------------------------------------------------
#ITX
ITXReason = Enum("""
  AutoResponded,
  Forwarded ,
  Normal,
  Redirected,
  Sent,
  Terminated,
  Abandoned
""")

ITXAgentState = Enum("""
  Unknown = -1,
  Login,
  Logout, 
  Available, 
  NotAvailable,
  Max = 100
""")

ITXVisibilityMode = Enum("""  
  unknown,  
  conference, 
  monitor,   
  coach
""")

ITXOperation = Enum("""
  op_unknown,   
  op_transfer,  
  op_conference,
  op_intrude,   
  op_route,   
  op_pull,    
  op_create,  
  op_reject,  
  op_timeout, 
  op_leave,   
  op_stop,    
  op_place_in_workbin, 
  op_place_in_queue, 
  op_party_disconnect 
""")

ITXWBContentOperation = Enum("""
  wb_content_op_unknown,
  wb_content_op_taken_out,
  wb_content_op_placed_in,
  wb_content_op_properties_changed,
""")

ITXActorType = Enum("""
  we_strategy = 1, 
  we_agent, 
  we_media_server
""")

ITXRouteType = Enum("""
  RouteTypeQueue = 1,
  RouteTypeAgent,
  RouteTypePlace,
  RouteTypeWorkbin,
  RouteTypeStop
""")

ITXEventName = Enum("""
  request_register_client                       = 100,
  request_submit                                = 101,
  request_stop_processing                       = 102,
  request_change_properties                     = 103,
  event_properties_changed                      = 104,
  request_place_in_queue                        = 105,
  request_place_in_workbin                      = 106,
  request_deliver                               = 107,
  request_pull                                  = 108,
  event_pulled_interactions                     = 109,
  request_transfer                              = 110,
  request_conference                            = 111,
  request_leave_interaction                     = 112,
  request_get_workbin_content                   = 113,
  request_workbin_notifications                 = 114,
  request_cancel_workbin_notifications          = 115,
  event_workbin_content                         = 116,
  event_workbin_content_changed                 = 117,
  request_take_snapshot                         = 118,
  event_snapshot_taken                          = 119,
  request_get_snapshot_interactions             = 120,
  event_snapshot_interactions                   = 121,
  request_lock_interaction                      = 122,
  request_unlock_interaction                    = 123,
  request_release_snapshot                      = 124,
  event_ack                                     = 125,
  event_error                                   = 126,
  event_invite                                  = 127,
  request_accept                                = 128,
  request_reject                                = 129,
  request_intrude                               = 130,
  event_activity_report                         = 131,
  event_party_added                             = 132,
  event_party_removed                           = 133,
  event_revoked                                 = 134,
  request_agent_login                           = 135,
  request_agent_logout                          = 136,
  event_agent_login                             = 137,
  event_agent_logout                            = 138,
  request_donot_disturb_on                      = 139,
  request_donot_disturb_off                     = 140,
  event_donot_disturb_on                        = 141,
  event_donot_disturb_off                       = 142,
  request_add_media                             = 143,
  request_remove_media                          = 144,
  event_media_added                             = 145,
  event_media_removed                           = 146,
  request_notready_for_media                    = 147,
  request_cancel_notready_for_media             = 148,
  event_notready_for_media                      = 149,
  event_ready_for_media                         = 150,
  request_change_agent_state_reason             = 151,
  event_agent_state_reason_changed              = 152,
  request_change_media_state_reason             = 153,
  event_media_state_reason_changed              = 154,
  event_current_agent_status                    = 155,
  request_agent_available                       = 156,
  request_agent_not_available                   = 157,
  event_agent_available                         = 158,
  event_agent_not_available                     = 159,
  event_interaction_submitted                   = 160,
  event_processing_stopped                      = 161,
  event_placed_in_queue                         = 162,
  event_placed_in_workbin                       = 163,
  event_locked                                  = 164,
  event_unlocked                                = 165,
  event_agent_invited                           = 166,
  event_accepted                                = 167,
  event_rejected                                = 168,
  request_start_place_agent_state_reporting     = 169,
  request_start_place_agent_state_reporting_all = 170,
  request_stop_place_agent_state_reporting      = 171,
  request_stop_place_agent_state_reporting_all  = 172,
  event_place_agent_state                       = 173,
  request_unregister_client                     = 174,
  msg_ping                                      = 175,
  event_custom                                  = 176,
  event_taken_from_queue                        = 177,
  request_workbin_types_info                    = 178,
  event_workbin_types_info                      = 179,
  request_workbin_statistic                     = 180,
  event_workbin_statistic                       = 181,
  event_taken_from_workbin                      = 182,
  request_subscribe                             = 183,
  request_unsubscribe                           = 184,
  request_publish                               = 185,
  event_user_event                              = 186,
  event_forced_disconnect                       = 187,
  request_get_interaction_properties            = 188,
  event_interaction_properties                  = 189,
  event_forced_agent_state_change               = 190,
  request_workflow_configuration                = 191,
  event_workflow_configuration                  = 192,
  event_external_service_requested              = 193,
  event_external_service_responded              = 194,
  event_agent_connection_closed                 = 195
""")


#contact server

UCSSortMode = Enum("""
  Ascending,
  Descending 
""")

UCSDataSourceType = Enum("""
  Archive,
  Main 
""")

UCSStatuses = Enum("""
  New = 0,
  Pending = 1,
  InProcess = 2,
  Stopped = 3,
""")

UCSEntityTypes = Enum("""
  EmailIn = 0,
  EmailOut = 1,
  Chat = 2,
  PhoneCall = 3,
  Callback = 5,
  CoBrowse = 6,
  Interaction = 7
""")

UCSCoBrowseAction = Enum("""
  Add = 0,
  Replace = 1,
  Remove = 2,
""")

UCSPrefixes = Enum("""
  Not = 0,
  And = 1,
  Or = 2,
""")

UCSOperators = Enum("""
  Equal = 0,
  NotEqual = 1,
  Greater = 2,
  GreaterOrEqual = 3,
  Lesser = 4,
  LesserOrEqual = 5,
  Like = 6,
""")  

UCSFaultCode = Enum("""
  InvalidServiceName = 0,
  InvalidMethodName = 1,
  StandardResponseNotFound = 2,
  StandardResponseNotFoundForCategory = 3,
  TextNotFound = 4,
  AddressNotFound = 5,
  TooManyAddresses = 6,
  InvalidAddressOrDomain = 7,
  StandardResponseTimeFrameError = 8,
  StandardResponseStatusError = 9,
  MissingParameter = 10,
  TwoIncopatibleParameters = 11,
  IncorrectParameterType = 12,
  IncorrectParameterValue = 13,
  RenderingError = 14,
  ParameterValueTooLong = 15,
  ParameterAndUserdataNotAllowed = 16,
  AttributeValueTooLong = 17,
  InvalidMediatypeValue = 18,
  Invalid3rdPartyMessageType = 19,
  ObjectNotFound = 20,
  InvalidInteractionType = 21,
  InvalidInteractionSubtype = 22,
  InvalidInteractionError = 23,
  InvalidFieldValue = 24,
  MaxAutoReplyCountReached = 25,
  ObjectAlreadyExist = 26,
  FatalError = 27,
  InvalidObjectId = 28,
  IncorrectConstraints = 29,
  InvalidAttributes = 30,
  ContactIdNotExist = 31,
  CanNotUpdateAttribute = 32,
  FromContactIdNotFound = 33,
  ToContactIdNotFound = 34,
  MergeIdNotFound = 35,
  MergeListNotExist = 36,
  MergeHistoryUnavailable = 37,
  UnexpectedError = 38,
  ConnectionToDbFailed = 39,
  NoEsjConfig = 40,
  SmtpAuthentificationError = 41,
  UnknownHost = 42,
  CantStopProcessing = 43,
  ConnectionClosed = 44,
  ServerOverloadedRequestRejected = 45,
  ConfigError = 46,
  FieldCodeKeyError = 47,
  TimeoutError = 48,
  NoSearchableAttribute = 49,
  NoCreationAttributeSet = 50,
  InvalidTenant = 51,
  NoTenant = 52,
  MoreThanOneTenant = 53,
  ContactMergeMultipleLevels = 54,
  InvalidMediaConfiguration = 55,
  NoValidSenderFound = 56,
  NoValidRecipientsFound = 57,
  BadAddress = 58,
  NoEmbeddedId = 59,
  NoParentFound = 60,
  NoReplyTextFound = 61,
  IdMismachError = 62,
  NotWellConstructed = 63,
  MimeMessageOpenError = 64,
  ManualIncorrectMime = 65
""")

UCSEventName = Enum("""
  EventAddAgentStdRespFavorite, 
  EventAddDocument, 
  EventAssignInteractionToContact, 
  EventBoostDocument, 
  EventCheckForUpdates, 
  EventContactListGet, 
  EventContactListGetNextPage, 
  EventContactListRelease, 
  EventCountInteractions, 
  EventDelete, 
  EventDeleteAgentStdRespFavorite, 
  EventDeleteInteraction, 
  EventError, 
  EventFindOrCreatePhoneCall, 
  EventGetAgentStdRespFavorites, 
  EventGetAllCategories, 
  EventGetAttributes, 
  EventGetContacts, 
  EventGetDocument, 
  EventGetIndexProperties, 
  EventGetInteractionContent, 
  EventGetInteractionsForContact, 
  EventGetInteractionsWithStatus, 
  EventGetVersion, 
  EventIdentifyContact, 
  EventInsert, 
  EventInsertInteraction, 
  EventInteractionListGet, 
  EventInteractionListGetNextPage, 
  EventInteractionListRelease, 
  EventMergeContacts, 
  EventMergeListGet, 
  EventMergeListGetNextPage, 
  EventMergeListRelease, 
  EventRemoveAllAttributes, 
  EventRemoveDocument, 
  EventRenderFieldCodes, 
  EventSearch, 
  EventSetInteractionStatus, 
  EventStopInteraction, 
  EventUnMergeContacts, 
  EventUpdateAttributes, 
  EventUpdateDocument, 
  EventUpdateInteraction,
  EventValidateFieldCodes                       
""")
#end contact server
 
#webmedia
FlexChatEventName = Enum("""
  EventStatus, 
""")

FlexChatRequestResult = Enum("""
  Success = 0,
  Error = 1,
""")


BasicChatEventName = Enum("""
  EventError, 
  EventRegistered, 
  EventSessionInfo,
""")

BasicChatSessionStatus = Enum("""
  Alive, 
  Over, 
""")


BasicChatUserType = Enum("""
  Client = 0,
  Agent = 1,
  Supervisor = 2,
  External = 3,
""")

BasicChatAction = Enum("""
  KeepAlive = 0,
  CloseIfNoAgents = 1,
  ForceClose = 2,
""")

BasicChatProtocolType = Enum("""
  Basic = 0,
  Flex = 1,
  Esp = 2,
""")

BasicChatVisibility = Enum("""
  All = 0,
  Int = 1,
  Vip = 2,
""")

BasicChatUserStatus = Enum("""
  On = 0,
  Off = 1,
  Keep = 2,
""")

WebEmailEventName = Enum("""
  EventAck, 
  EventError, 
""")

WebEmailErrors = Enum("""
  Success = 0,
  Timeout = 1,
  ConnectionClosed = 2,
  OperationFailure = 3,
  InternalFailure = 4,
  ConnectionFailure = 5,
""")



#end webmedia

PSDKProtocolType = Enum("""
  BasicChat,
  Callback,
  ConfServer,
  ConfServerDeprecated,
  ContactServer,
  Email,
  FlexChat,
  InteractionServer,
  LocalControlAgent,
  MessageServer,
  OutboundServer,
  RoutingServer,
  SolutionControlServer,
  StatServer,
  TServer,
""")
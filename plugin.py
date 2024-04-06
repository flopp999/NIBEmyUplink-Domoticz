# NIBEmyUplink Python Plugin
#
# Author: flopp999
#
"""
<plugin key="NIBEmyUplink" name="NIBE myUplink 0.1" author="flopp999" version="0.1" wikilink="https://github.com/flopp999/NIBEmyUplink-Domoticz" externallink="https://www.myuplink.com">
    <description>
        <h3>NIBE myUplink is used to read data from api.myuplink.com</h3><br/>
        <h3>Support me with a coffee &<a href="https://www.buymeacoffee.com/flopp999">https://www.buymeacoffee.com/flopp999</a></h3><br/>
        <h3>How to get your Identifier, Secret and URL?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEmyUplink-Domoticz#identifier-secret-and-callback-url">https://github.com/flopp999/NIBEmyUplink-Domoticz#identifier-secret-and-callback-url</a></h4>
        <br/>
        <h3>How to get your Access Code?</h3>
        <h4>&<a href="https://github.com/flopp999/NIBEmyUplink-Domoticz#access-code">https://github.com/flopp999/NIBEmyUplink-Domoticz#access-code</a></h4>
        <br/>
        <h3>Configuration</h3>
    </description>
    <params>
        <param field="Mode4" label="Uplink Identifier" width="350px" required="true" default="Identifier"/>
        <param field="Mode2" label="Uplink Secret" width="350px" required="true" default="Secret"/>
        <param field="Address" label="Callback URL" width="350px" required="true" default="URL"/>
        <param field="Mode1" label="Access Code" width="350px" required="true" default="Access Code"/>
        <param field="Mode3" label="Refresh Token" width="350px" default="Copy Refresh Token from Log to here" required="true"/>
        <param field="Port" label="Update every" width="100px">
            <options>
                <option label="1 minute" value=6 />
                <option label="5 minutes" value=30 />
                <option label="10 minutes" value=60 />
                <option label="15 minutes" value=90 />
            </options>
        </param>
        <param field="Mode6" label="Debug to file (Nibe.log)" width="50px">
            <options>
                <option label="Yes" value="Yes" />
                <option label="No" value="No" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz

Package = True
MissingPackage = []

try:
    import requests, json, os, logging
except ImportError as e:
    MissingPackage.append(e)
    Package = False

try:
    from logging.handlers import RotatingFileHandler
except ImportError as e:
    MissingPackage.append(e)
    Package = False

try:
    from datetime import datetime
except ImportError as e:
    MissingPackage.append(e)
    Package = False

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("NIBE")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(dir+'/NIBEmyUplink.log', maxBytes=1000000, backupCount=5)
logger.addHandler(handler)

class BasePlugin:
    enabled = False

    def __init__(self):
        self.token = ''
        self.loop = 0
        self.Count = 5
        return

    def onStart(self):
#        Domoticz.Debugging(1)
        WriteDebug("===onStart===")
        self.Ident = Parameters["Mode4"]
        self.ShowCategories = Parameters["Mode5"]
        self.URL = Parameters["Address"]
        self.Access = Parameters["Mode1"]
        self.Secret = Parameters["Mode2"]
        self.Refresh = Parameters["Mode3"]
        self.Update = Parameters["Port"]
        self.Categories = []
        self.SystemID = ""
        self.NoOfSystems = ""
        self.SystemUnitId = 0
        self.FirstRun = True
        self.AllSettings = True

        self.GetRefresh = Domoticz.Connection(Name="Get Refresh", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        if len(self.Refresh) < 50 and self.AllSettings == True:
            self.GetRefresh.Connect()
        self.GetToken = Domoticz.Connection(Name="Get Token", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        self.GetData = Domoticz.Connection(Name="Get Data 0", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        self.GetData1 = Domoticz.Connection(Name="Get Data 1", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        self.GetSystemID = Domoticz.Connection(Name="Get SystemID", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        self.GetNoOfSystems = Domoticz.Connection(Name="Get NoOfSystems", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        self.GetTarget = Domoticz.Connection(Name="Get Target", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
        self.GetCategories = Domoticz.Connection(Name="Get Categories", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")

    def onDisconnect(self, Connection):
        WriteDebug("Disconnect called for connection '"+Connection.Name+"'.")

    def onConnect(self, Connection, Status, Description):
        WriteDebug("Connect called for connection '"+Connection.Name+"'.")
        if CheckInternet() == True and self.AllSettings == True:
            if (Status == 0):
                headers = { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Host': 'api.myuplink.com'}
                data = "client_id="+self.Ident
                data += "&client_secret="+self.Secret

                if Connection.Name == ("Get Refresh"):
                    WriteDebug("Get Refresh")
                    data += "&grant_type=authorization_code"
                    data += "&code="+self.Access
                    data += "&redirect_uri="+self.URL
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                elif Connection.Name == ("Get Token"):
                    WriteDebug("Get Token")
                    Domoticz.Log(self.Refresh)
                    if len(self.Refresh) > 50:
                        WriteDebug("Using reftoken")
                        self.reftoken = self.Refresh
                    data += "&grant_type=refresh_token"
                    data += "&refresh_token="+self.reftoken
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                headers = { 'Host': 'api.myuplink.com', 'Authorization': 'Bearer '+self.token}

                if Connection.Name == ("Get Data 0"):
                    WriteDebug("Get Data 0")
                    self.loop = 0
                    self.SystemUnitId = 0
                    for category in categories:
                        Connection.Send({'Verb':'GET', 'URL': '/v2/devices/'+self.SystemID+'/points', 'Headers': headers})

                elif Connection.Name == ("Get SystemID"):
                        WriteDebug("Get SystemID")
                        Connection.Send({'Verb':'GET', 'URL': '/v2/systems/me', 'Headers': headers})

                elif Connection.Name == ("Get NoOfSystems"):
                        WriteDebug("Get NoOfSystems")
                        Connection.Send({'Verb':'GET', 'URL': '/v2/systems/'+self.SystemID+'/units', 'Headers': headers})

                elif Connection.Name == ("Get Target"):
                        WriteDebug("Get Target")
                        Connection.Send({'Verb':'GET', 'URL': '/v2/systems/'+self.SystemID+'/parameters?parameterIds=47398', 'Headers': headers})

                elif Connection.Name == ("Get Categories"):
                        WriteDebug("Get Categories")
                        self.SystemUnitId = 0
                        while self.SystemUnitId < int(self.NoOfSystems):
                            Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories?systemUnitId='+str(self.SystemUnitId), 'Headers': headers})
                            self.SystemUnitId += 1



    def onMessage(self, Connection, Data):
        Status = int(Data["Status"])

        if (Status == 200):
            Data = Data['Data'].decode('UTF-8')
            Data = json.loads(Data)

            if Connection.Name == ("Get Refresh"):
                WriteDebug("GetFre")
                self.reftoken = Data["refresh_token"]
                if len(self.Refresh) < 50:
                    Domoticz.Log("Copy token to Setup->Hardware->NibeUplink->Refresh Token:")
                    Domoticz.Log(str(self.reftoken))
                if self.GetRefresh.Connected() or self.GetRefresh.Connecting():
                    self.GetRefresh.Disconnect()
                self.GetToken.Connect()

            elif Connection.Name == ("Get SystemID"):
                self.SystemID = str(Data["systems"][0]["devices"][0]["id"])
                Domoticz.Log(self.SystemID)
                if self.GetSystemID.Connected() or self.GetSystemID.Connecting():
                    self.GetSystemID.Disconnect()
#                self.GetNoOfSystems.Connect()
                self.GetData.Connect()

#            elif Connection.Name == ("Get NoOfSystems"):
#                Domoticz.Log("Systems found:"+str(len(Data)))
#                self.NoOfSystems = len(Data) # will be 1 higher then SystemUnitId
#                if self.GetNoOfSystems.Connected() or self.GetNoOfSystems.Connecting():
#                    self.GetNoOfSystems.Disconnect()
#                if self.FirstRun == True and self.ShowCategories == "Yes":
#                    self.GetCategories.Connect()
#                self.GetData.Connect()

            elif Connection.Name == ("Get Target"):
                WriteDebug("inne i Message Target1")
                sValue = Data[0]["rawValue"]/10.0
                WriteDebug("inne i Message Target2")
                UpdateDevice(int(117), str(sValue), Data[0]["unit"], Data[0]["title"], Data[0]["parameterId"], Data[0]["designation"], 0)
                WriteDebug("inne i Message Target3")
                if self.GetTarget.Connected() or self.GetTarget.Connecting():
                    self.GetTarget.Disconnect()
                WriteDebug("inne i Message Target4")

            elif Connection.Name == ("Get Token"):
                self.token = Data["access_token"]
                if self.GetToken.Connected() or self.GetToken.Connecting():
                    self.GetToken.Disconnect()
                if self.SystemID == "":
                    self.GetSystemID.Connect()
                else:
                    self.GetData.Connect()

            elif Connection.Name == ("Get Categories"):
                for each in Data:
                    self.Categories.append(each["categoryId"])
                Domoticz.Log(str(self.Categories))
                if self.GetCategories.Connected() or self.GetCategories.Connecting():
                    self.GetCategories.Disconnect()

            elif Connection.Name == ("Get Data 0"):
                for each in Data:
                    UpdateDevice(str(each["value"]), each["parameterUnit"], each["parameterName"], int(each["parameterId"]))

        else:
            WriteDebug("Status = "+str(Status))
            Domoticz.Error(str("Status "+str(Status)))
            Domoticz.Error(str(Data))
            if _plugin.GetCategories.Connected() or _plugin.GetCategories.Connecting():
                _plugin.GetCategories.Disconnect()
            if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
                _plugin.GetRefresh.Disconnect()
            if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
                _plugin.GetToken.Disconnect()
            if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
                _plugin.GetData.Disconnect()
            if _plugin.GetData1.Connected() or _plugin.GetData1.Connecting():
                _plugin.GetData1.Disconnect()
            if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
                _plugin.GetSystemID.Disconnect()
            if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
                _plugin.GetNoOfSystems.Disconnect()
            if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
                _plugin.GetTarget.Disconnect()

    def onHeartbeat(self):
        WriteDebug("Heart")
        if _plugin.GetCategories.Connected() or _plugin.GetCategories.Connecting():
            _plugin.GetCategories.Disconnect()
        if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
            _plugin.GetData.Disconnect()
        if _plugin.GetData1.Connected() or _plugin.GetData1.Connecting():
            _plugin.GetData1.Disconnect()
        if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
            _plugin.GetSystemID.Disconnect()
        if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
            _plugin.GetNoOfSystems.Disconnect()
        if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
            _plugin.GetTarget.Disconnect()

        self.Count += 1
        if self.Count >= int(self.Update) and not self.GetToken.Connected() and not self.GetToken.Connecting():
            self.GetToken.Connect()
            WriteDebug("onHeartbeat")
            self.Count = 0

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def UpdateDevice(sValue, Unit, Name, PID):

    if PID == 40004:
        ID = 1
    elif PID == 40008:
        ID = 2
    elif PID == 40012:
        ID = 3
    elif PID == 40013:
        ID = 4
    elif PID == 40014:
        ID = 5
    elif PID == 40017:
        ID = 6
    elif PID == 40018:
        ID = 7
    elif PID == 40019:
        ID = 8
    elif PID == 40020:
        ID = 9
    elif PID == 40022:
        ID = 10
    elif PID == 40025:
        ID = 11
    elif PID == 40026:
        ID = 12
    elif PID == 40033:
        ID = 13
    elif PID == 40047:
        ID = 14
    elif PID == 40048:
        ID = 15
    elif PID == 40050:
        ID = 16
    elif PID == 40067:
        ID = 17
    elif PID == 40079:
        ID = 18
    elif PID == 40081:
        ID = 19
    elif PID == 40083:
        ID = 20
    elif PID == 40145:
        ID = 21
    elif PID == 40146:
        ID = 22
    elif PID == 40940:
        ID = 23
    elif PID == 40940:
        ID = 24
    elif PID == 40940:
        ID = 25
    elif PID == 40940:
        ID = 26
    elif PID == 40940:
        ID = 27
    elif PID == 40940:
        ID = 28
    elif PID == 40940:
        ID = 29
    elif PID == 40940:
        ID = 30
    elif PID == 41778:
        ID = 31
    elif PID == 42770:
        ID = 32
    elif PID == 43009:
        ID = 33
    elif PID == 43066:
        ID = 34
    elif PID == 43081:
        ID = 35
    elif PID == 43108:
        ID = 36
    elif PID == 43109:
        ID = 37
    elif PID == 43115:
        ID = 38
    elif PID == 43122:
        ID = 39
    elif PID == 43123:
        ID = 40
    elif PID == 43124:
        ID = 41
    elif PID == 43125:
        ID = 42
    elif PID == 43140:
        ID = 43
    elif PID == 43146:
        ID = 44
    elif PID == 43161:
        ID = 45
    elif PID == 43181:
        ID = 46
    elif PID == 43427:
        ID = 47
    elif PID == 49633:
        ID = 48
    elif PID == 49993:
        ID = 49
    elif PID == 49994:
        ID = 50
    elif PID == 49995:
        ID = 51
    elif PID == 50004:
        ID = 52
    elif PID == 50005:
        ID = 53

    if (ID not in Devices):
        if Unit == "°C":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Temperature", Used=1, Description="ParameterID="+str(PID)).Create()
        else:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Description="ParameterID="+str(PID)).Create()

    if (ID in Devices):
        if Devices[ID].sValue != sValue:
            Devices[ID].Update(0, str(sValue))

def CheckInternet():
    WriteDebug("Entered CheckInternet")
    try:
        WriteDebug("Ping")
        requests.get(url='https://api.myuplink.com/', timeout=2)
        WriteDebug("Internet is OK")
        return True
    except:
        if _plugin.GetCategories.Connected() or _plugin.GetCategories.Connecting():
            _plugin.GetCategories.Disconnect()
        if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
            _plugin.GetData.Disconnect()
        if _plugin.GetData1.Connected() or _plugin.GetData1.Connecting():
            _plugin.GetData1.Disconnect()
        if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
            _plugin.GetSystemID.Disconnect()
        if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
            _plugin.GetNoOfSystems.Disconnect()
        if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
            _plugin.GetTarget.Disconnect()

        WriteDebug("Internet is not available")
        return False

def WriteDebug(text):
    if Parameters["Mode6"] == "Yes":
        timenow = (datetime.now())
        logger.info(str(timenow)+" "+text)

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    _plugin.onMessage(Connection, Data)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

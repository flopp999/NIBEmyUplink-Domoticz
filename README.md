Support me with a coffee https://www.buymeacoffee.com/flopp999
---
Create a folder with name "NIBEmyUplink" in "domoticz/plugins"  
Put plugin.py, requirements.txt and NIBEmyUplink.zip in that folder

or

Run in domoticz/plugins "sudo git clone h<span>ttps://gith<span>ub.com/flopp999/NIBEmyUplink-Domoticz NIBEmyUplink"  

Run "pip3 install -r requirements.txt" to install all packages that this plugin needs

---
You need to have some information to be able to use this plugin:  
[Identifier](https://github.com/flopp999/NIBEmyUplink-Domoticz/blob/main/README.md#Identifier,-Secret-and-URL)  
[Secret](https://github.com/flopp999/NIBEmyUplink-Domoticz/blob/main/README.md#Identifier,-Secret-and-URL)  
[Callback URL](https://github.com/flopp999/NIBEmyUplink-Domoticz/blob/main/README.md#Identifier,-Secret-and-Callback-URL)  
[Access code](https://github.com/flopp999/NIBEmyUplink-Domoticz/blob/main/README.md#Access-code)

# Identifier, Secret and Callback URL
Login to [NIBE myUplink API](https://dev.myuplink.com/)  
Create an application under My Applications  
For Callback URL use "h<span>ttps://a<span>pi.nib<span>euplink.com/"  
Copy Identifier, Secret and Callback URL, paste to NIBEUplink hardware in Domoticz  

# Access code
You need to create an Access code before first use  
Click on the link below, you will get an error, that is OK  
[https://api.myuplink.com/oauth/authorize?response_type=code&client_id=yyyyyy&scope=READSYSTEM WRITESYSTEM offline_access&redirect_uri=http://validurl.local:1234&state=x]  
Once you clicked it, in the address bar change yyyyyy to your Identifier, NOT YOUR SYSTEM ID!!!  
Also change redirect_url to your own Callbrack URL  
Then it will ask you to login and accept.  
When this is done the address bar will look something like below  
"h<span>ttps://a<span>pi.my<span>uplink.com/?code=ndfhj3u38ufhswhnerjqa5zEyN-RmBgkTCc&state=x"  
Copy everything after "...code=" and before "&state...", the code above is just an example, normally the code is ~380 characters  
Above example have access code "ndfhj3u38ufhswhnerjqa5zEyN-RmBgkTCc"


Support me with a coffee https://www.buymeacoffee.com/flopp999

[comment]: # "Auto-generated SOAR connector documentation"
# QRadar

Publisher: Splunk  
Connector Version: 2\.1\.2  
Product Vendor: IBM  
Product Name: QRadar  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.9\.39220  

This app supports generic, investigative, and ingestion actions on an IBM QRadar device

### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a QRadar asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device** |  required  | string | Server IP/Hostname
**containers\_only** |  optional  | boolean | Ingest only offenses while polling
**has\_offense** |  optional  | boolean | Fetch only events and flows associated with the offense
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  optional  | string | Username
**password** |  optional  | password | Password
**authorization\_token** |  optional  | password | Auth Token for QRadar REST API calls
**timezone** |  required  | timezone | QRadar timezone
**add\_to\_resolved** |  optional  | boolean | Ingest artifacts into closed/resolved containers
**artifact\_max** |  optional  | numeric | Maximum event artifacts count per cycle \(excluding the default generated offense artifact\)
**ingest\_resolved** |  optional  | boolean | Ingest only open offenses
**cef\_event\_map** |  optional  | string | CEF event map
**cef\_value\_map** |  optional  | string | CEF value map
**delete\_empty\_cef\_fields** |  optional  | boolean | Delete the empty CEF fields
**event\_fields\_for\_query** |  optional  | string | Event fields to include while querying
**add\_offense\_id\_to\_name** |  optional  | boolean | Add offense ID to name of containers
**alternative\_ariel\_query** |  optional  | boolean | Alternative ariel query
**alternative\_ingest\_algorithm** |  optional  | boolean | Alternative ingest algorithm for offenses
**alt\_time\_field** |  optional  | string | Alternative ingestion time field
**alt\_initial\_ingest\_time** |  optional  | string | Alternative initial ingestion time
**alt\_ingestion\_order** |  optional  | string | Alternative ingestion order for offenses
**events\_ingest\_start\_time** |  optional  | numeric | Events ingestion initial time \(relative to offense start time, default is 60 min\)
**offense\_ingest\_start\_time** |  optional  | numeric | Offense ingestion initial time \(relative to offense start time, default is 0 min\)
**event\_ingest\_end\_time** |  optional  | numeric | Events ingestion end time \(relative to event ingestion start time, default is 0 min\)
**max\_events\_per\_offense** |  optional  | numeric | Maximum accumulated artifacts count per offense \(including the default generated offense artifact\)

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action runs a quick query on the device to check the connection and credentials  
[list offenses](#action-list-offenses) - Get a list of offenses  
[list closing reasons](#action-list-closing-reasons) - Get a list of offense closing reasons  
[get events](#action-get-events) - Get events belonging to an offense  
[get flows](#action-get-flows) - Get flows that make up an offense for a particular IP  
[offense details](#action-offense-details) - Get details about an offense  
[alt manage ingestion](#action-alt-manage-ingestion) - Manage ingestion details  
[run query](#action-run-query) - Execute an ariel query on the QRadar device  
[add listitem](#action-add-listitem) - Add an item to a reference set in QRadar  
[close offense](#action-close-offense) - Close an active offense, marking status=CLOSED  
[update offense](#action-update-offense) - Attach a note to an offense  
[assign user](#action-assign-user) - Assign the user to an offense  
[get rule info](#action-get-rule-info) - Retrieve QRadar rule information  
[list rules](#action-list-rules) - List all QRadar rules  
[on poll](#action-on-poll) - Callback action for the on\_poll ingest functionality  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action runs a quick query on the device to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'list offenses'
Get a list of offenses

Type: **investigate**  
Read only: **True**

The default start\_time is the past 5 days\. The default end\_time is now\. The default count is 100 offenses\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\) | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\) | numeric | 
**count** |  optional  | Number of offenses to retrieve | numeric | 
**offense\_id** |  optional  | Comma\-separated list of offense IDs to fetch | string |  `qradar offense id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.count | numeric |  |   100 
action\_result\.parameter\.end\_time | numeric |  |   1669900000000 
action\_result\.parameter\.offense\_id | string |  `qradar offense id`  |   44 
action\_result\.parameter\.start\_time | numeric |  |   1559900000000 
action\_result\.data\.\*\.assigned\_to | string |  |   admin 
action\_result\.data\.\*\.categories | string |  |   License Status 
action\_result\.data\.\*\.category\_count | numeric |  |   10 
action\_result\.data\.\*\.close\_time | string |  |  
action\_result\.data\.\*\.closing\_reason\_id | string |  `qradar offense closing reason id`  |  
action\_result\.data\.\*\.closing\_user | string |  |  
action\_result\.data\.\*\.credibility | numeric |  |   4 
action\_result\.data\.\*\.description | string |  |   Local Malware Events
 
action\_result\.data\.\*\.destination\_networks | string |  |   other 
action\_result\.data\.\*\.device\_count | numeric |  |   3 
action\_result\.data\.\*\.domain\_id | numeric |  |  
action\_result\.data\.\*\.event\_count | numeric |  |   28603163 
action\_result\.data\.\*\.flow\_count | numeric |  |   110 
action\_result\.data\.\*\.follow\_up | boolean |  |   False  True 
action\_result\.data\.\*\.id | numeric |  `qradar offense id`  |   44 
action\_result\.data\.\*\.inactive | boolean |  |   False  True 
action\_result\.data\.\*\.last\_updated\_time | numeric |  |   1559194600958 
action\_result\.data\.\*\.local\_destination\_count | numeric |  |   0 
action\_result\.data\.\*\.magnitude | numeric |  |   5 
action\_result\.data\.\*\.offense\_source | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.offense\_type | numeric |  |   0 
action\_result\.data\.\*\.policy\_category\_count | numeric |  |   0 
action\_result\.data\.\*\.protected | boolean |  |   False  True 
action\_result\.data\.\*\.relevance | numeric |  |   4 
action\_result\.data\.\*\.remote\_destination\_count | numeric |  |   1 
action\_result\.data\.\*\.rules\.\*\.id | numeric |  |  
action\_result\.data\.\*\.rules\.\*\.type | string |  |  
action\_result\.data\.\*\.security\_category\_count | numeric |  |   10 
action\_result\.data\.\*\.severity | numeric |  |   6 
action\_result\.data\.\*\.source\_count | numeric |  |   1 
action\_result\.data\.\*\.source\_network | string |  |   Net\-10\-172\-192\.Net\_10\_0\_0\_0 
action\_result\.data\.\*\.start\_time | numeric |  |   1558009780686 
action\_result\.data\.\*\.status | string |  |   OPEN 
action\_result\.data\.\*\.username\_count | numeric |  `user name`  |   0 
action\_result\.summary | string |  |  
action\_result\.summary\.total\_offenses | numeric |  |   1 
action\_result\.message | string |  |   Fetching all open offenses\. Total offenses\: 1  Total Offenses\: 1 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'list closing reasons'
Get a list of offense closing reasons

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**include\_reserved** |  optional  | Include reserved offense closing reasons | boolean | 
**include\_deleted** |  optional  | Include deleted offense closing reasons | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.include\_deleted | boolean |  |   True  False 
action\_result\.parameter\.include\_reserved | boolean |  |   True  False 
action\_result\.data\.\*\.id | numeric |  `qradar offense closing reason id`  |   2 
action\_result\.data\.\*\.is\_deleted | boolean |  |   True  False 
action\_result\.data\.\*\.is\_reserved | boolean |  |   True  False 
action\_result\.data\.\*\.text | string |  |   False\-Positive, Tuned 
action\_result\.summary\.total\_offense\_closing\_reasons | numeric |  |   5 
action\_result\.message | string |  |   Total offense closing reasons\: 5 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'get events'
Get events belonging to an offense

Type: **investigate**  
Read only: **True**

Use fields\_filter parameter to restrict the events returned that match the filter\. For e\.g\. destinationip='10\.10\.0\.52' and protocolid='6'\. For further details refer to the documentation section of the action in the README\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense\_id** |  optional  | Offense ID to get events of | numeric |  `qradar offense id` 
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\) | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\) | numeric | 
**count** |  optional  | Number of events to retrieve | numeric | 
**fields\_filter** |  optional  | Filter on event field values | string | 
**interval\_days** |  optional  | Interval days | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.count | numeric |  |   10 
action\_result\.parameter\.end\_time | numeric |  |   1669891174855 
action\_result\.parameter\.fields\_filter | string |  |   sourceip='122\.122\.122\.122' 
action\_result\.parameter\.interval\_days | numeric |  |   20 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   44 
action\_result\.parameter\.start\_time | numeric |  |   1559891174855 
action\_result\.data\.\*\.AccountDomain | string |  `domain`  `url`  |  
action\_result\.data\.\*\.Application | string |  |  
action\_result\.data\.\*\.Bytes | string |  |  
action\_result\.data\.\*\.BytesReceived | string |  |  
action\_result\.data\.\*\.BytesSent | string |  |  
action\_result\.data\.\*\.Destination Host Name | string |  `host name`  |  
action\_result\.data\.\*\.EventID | string |  |  
action\_result\.data\.\*\.File Hash | string |  |  
action\_result\.data\.\*\.File ID | string |  |  
action\_result\.data\.\*\.File Path | string |  |  
action\_result\.data\.\*\.Filename | string |  |  
action\_result\.data\.\*\.Hostname | string |  `host name`  |  
action\_result\.data\.\*\.Installer Filename | string |  |  
action\_result\.data\.\*\.Message | string |  |  
action\_result\.data\.\*\.Payload | string |  |   Communication with Known Watched Networks	There has been event communication with networks that appear on the systems watch and darknet lists\. 
action\_result\.data\.\*\.Source Host Name | string |  `host name`  |  
action\_result\.data\.\*\.categoryname\_category | string |  |   Suspicious Activity 
action\_result\.data\.\*\.destinationaddress | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.destinationip | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.destinationmac | string |  |   00\:00\:00\:00\:00\:00 
action\_result\.data\.\*\.destinationport | numeric |  `port`  |   0 
action\_result\.data\.\*\.endtime | numeric |  |  
action\_result\.data\.\*\.eventcount | numeric |  |  
action\_result\.data\.\*\.eventdirection | string |  |   L2R  R2R 
action\_result\.data\.\*\.hostname\_logsourceid | string |  `host name`  |   Unknown Host 63 
action\_result\.data\.\*\.identityip | string |  `ip`  |  
action\_result\.data\.\*\.logsourcegroupname\_logsourceid | string |  |   Other 
action\_result\.data\.\*\.logsourceid | numeric |  |   63 
action\_result\.data\.\*\.logsourcename\_logsourceid | string |  |   Custom Rule Engine\-8 \:\: qradar 
action\_result\.data\.\*\.protocolname\_protocolid | string |  |   Reserved 
action\_result\.data\.\*\.qid | numeric |  |   70750119 
action\_result\.data\.\*\.qidname\_qid | string |  |   Communication with Known Watched Networks 
action\_result\.data\.\*\.relevance | numeric |  |  
action\_result\.data\.\*\.severity | numeric |  |  
action\_result\.data\.\*\.sourceaddress | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.sourceip | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.sourcemac | string |  |   00\:00\:00\:00\:00\:00 
action\_result\.data\.\*\.sourceport | numeric |  `port`  |   0 
action\_result\.data\.\*\.sourcev6 | string |  `ipv6`  |  
action\_result\.data\.\*\.starttime | numeric |  |   1559194870184 
action\_result\.data\.\*\.username | string |  `user name`  |  
action\_result\.summary\.total\_events | numeric |  |   10 
action\_result\.message | string |  |   Total events\: 10 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'get flows'
Get flows that make up an offense for a particular IP

Type: **investigate**  
Read only: **True**

Use the <b>fields\_filter</b> parameter to restrict the flows returned\. For e\.g\. protocolid='6'\. For further details refer to the documentation section of the action in the README\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  optional  | IP to get all the flows of | string |  `ip` 
**offense\_id** |  optional  | Offense ID to get flows of | numeric |  `qradar offense id` 
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\) | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\) | numeric | 
**count** |  optional  | Number of flows to retrieve | numeric | 
**fields\_filter** |  optional  | Filter in AQL format on flow field values | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.count | numeric |  |   100 
action\_result\.parameter\.end\_time | numeric |  |   1559905203000 
action\_result\.parameter\.fields\_filter | string |  |   sourceip='127\.0\.0\.1' 
action\_result\.parameter\.ip | string |  `ip`  |   122\.122\.122\.122 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   41 
action\_result\.parameter\.start\_time | numeric |  |   1559905201000 
action\_result\.data\.\*\.Action | string |  |  
action\_result\.data\.\*\.Application Determination Algorithm | numeric |  |  
action\_result\.data\.\*\.Content Subject | string |  |  
action\_result\.data\.\*\.Content Type | string |  |  
action\_result\.data\.\*\.FTP Pass | string |  |  
action\_result\.data\.\*\.FTP RETR File | string |  |  
action\_result\.data\.\*\.FTP User | string |  |  
action\_result\.data\.\*\.File Entropy | string |  |  
action\_result\.data\.\*\.File Hash | string |  |  
action\_result\.data\.\*\.File Name | string |  |  
action\_result\.data\.\*\.File Size | string |  |  
action\_result\.data\.\*\.Flow Direction Algorithm | numeric |  |  
action\_result\.data\.\*\.Google Search Terms | string |  |  
action\_result\.data\.\*\.HTTP Content\-Type | string |  |  
action\_result\.data\.\*\.HTTP GET Request | string |  |  
action\_result\.data\.\*\.HTTP Host | string |  |  
action\_result\.data\.\*\.HTTP Referer | string |  |  
action\_result\.data\.\*\.HTTP Referrer | string |  |  
action\_result\.data\.\*\.HTTP Response Code | string |  |  
action\_result\.data\.\*\.HTTP Server | string |  |  
action\_result\.data\.\*\.HTTP User Agent | string |  |  
action\_result\.data\.\*\.HTTP User\-Agent | string |  |  
action\_result\.data\.\*\.HTTP Version | string |  |  
action\_result\.data\.\*\.Originating User | string |  |  
action\_result\.data\.\*\.Password | string |  |  
action\_result\.data\.\*\.Request URL | string |  |  
action\_result\.data\.\*\.SMTP From | string |  |  
action\_result\.data\.\*\.SMTP HELO | string |  |  
action\_result\.data\.\*\.SMTP Hello | string |  |  
action\_result\.data\.\*\.SMTP To | string |  |  
action\_result\.data\.\*\.Search Arguments | string |  |  
action\_result\.data\.\*\.VLAN Tag | string |  |  
action\_result\.data\.\*\.applicationid | numeric |  |   1011 
action\_result\.data\.\*\.applicationname\_applicationid | string |  |  
action\_result\.data\.\*\.category | numeric |  |   18448 
action\_result\.data\.\*\.categoryname\_category | string |  |  
action\_result\.data\.\*\.credibility | numeric |  |   10 
action\_result\.data\.\*\.destinationasn | string |  |  
action\_result\.data\.\*\.destinationbytes | numeric |  |   11567 
action\_result\.data\.\*\.destinationdscp | numeric |  |  
action\_result\.data\.\*\.destinationflags | string |  |  
action\_result\.data\.\*\.destinationifindex | string |  |  
action\_result\.data\.\*\.destinationip | string |  `ip`  |   10\.1\.16\.15 
action\_result\.data\.\*\.destinationpackets | numeric |  |   108 
action\_result\.data\.\*\.destinationpayload | string |  |  
action\_result\.data\.\*\.destinationport | numeric |  `port`  |   3365 
action\_result\.data\.\*\.destinationprecedence | numeric |  |  
action\_result\.data\.\*\.destinationv6 | string |  |   0\:0\:0\:0\:0\:0\:0\:0 
action\_result\.data\.\*\.domainid | numeric |  |  
action\_result\.data\.\*\.firstpackettime | numeric |  |   1559905202000 
action\_result\.data\.\*\.flowbias | string |  |  
action\_result\.data\.\*\.flowdirection | string |  |   L2R 
action\_result\.data\.\*\.flowid | numeric |  |  
action\_result\.data\.\*\.flowinterface | string |  |  
action\_result\.data\.\*\.flowinterfaceid | string |  |   5 
action\_result\.data\.\*\.flowsource | string |  |  
action\_result\.data\.\*\.flowtype | numeric |  |  
action\_result\.data\.\*\.fullmatchlist | string |  |  
action\_result\.data\.\*\.geographic | string |  |   NorthAmerica\.UnitedStates 
action\_result\.data\.\*\.hasdestinationpayload | boolean |  |  
action\_result\.data\.\*\.hasoffense | boolean |  |   True 
action\_result\.data\.\*\.hassourcepayload | boolean |  |   False 
action\_result\.data\.\*\.hastlv | boolean |  |  
action\_result\.data\.\*\.icmpcode | string |  |  
action\_result\.data\.\*\.icmptype | string |  |  
action\_result\.data\.\*\.intervalid | numeric |  |   1603463820 
action\_result\.data\.\*\.isduplicate | boolean |  |  
action\_result\.data\.\*\.lastpackettime | numeric |  |   1559905202999 
action\_result\.data\.\*\.partialmatchlist | string |  |  
action\_result\.data\.\*\.processorid | numeric |  |   8 
action\_result\.data\.\*\.protocolid | numeric |  |  
action\_result\.data\.\*\.protocolname\_protocolid | string |  |  
action\_result\.data\.\*\.qid | numeric |  |   53250087 
action\_result\.data\.\*\.qidname\_qid | string |  |   Test\.Securetest 
action\_result\.data\.\*\.relevance | numeric |  |  
action\_result\.data\.\*\.retentionbucket | string |  |  
action\_result\.data\.\*\.severity | numeric |  |   1 
action\_result\.data\.\*\.sourceasn | string |  |  
action\_result\.data\.\*\.sourcebytes | numeric |  |   1031681 
action\_result\.data\.\*\.sourcedscp | numeric |  |  
action\_result\.data\.\*\.sourceflags | string |  |  
action\_result\.data\.\*\.sourceifindex | string |  |  
action\_result\.data\.\*\.sourceip | string |  `ip`  |   127\.0\.0\.1 
action\_result\.data\.\*\.sourcepackets | numeric |  |   783 
action\_result\.data\.\*\.sourcepayload | string |  |  
action\_result\.data\.\*\.sourceport | numeric |  |   4806 
action\_result\.data\.\*\.sourceprecedence | numeric |  |  
action\_result\.data\.\*\.sourcev6 | string |  `ipv6`  |   0\:0\:0\:0\:0\:0\:0\:0 
action\_result\.data\.\*\.starttime | numeric |  |   1559905201000 
action\_result\.data\.\*\.viewobjectpair | string |  |  
action\_result\.summary\.total\_flows | numeric |  |   33 
action\_result\.message | string |  |   Total flows\: 33 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'offense details'
Get details about an offense

Type: **investigate**  
Read only: **True**

If the <b>ingest\_offense</b> parameter is checked, then, it will ingest the events within the last N days \(N \- value in the <b>interval\_days</b> parameter if given or value in the <b>interval\_days</b> parameter in the app config or default 5 days\) for the offense mentioned in the <b>offense\_id</b> parameter\. If the <b>ingest\_offense</b> parameter is unchecked, it will fetch only the details of the provided offense ID in the <b>offense\_id</b> parameter\. The parameter <b>tenant\_id</b> is used only when the <b>ingest\_offense</b> parameter is checked\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense\_id** |  required  | Offense ID to get the details of | numeric |  `qradar offense id` 
**tenant\_id** |  optional  | Tenant ID for saving container | numeric | 
**ingest\_offense** |  optional  | Ingest offense into Phantom | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.ingest\_offense | boolean |  |   True  False 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   43 
action\_result\.parameter\.tenant\_id | numeric |  |   123 
action\_result\.data\.\*\.assigned\_to | string |  |   admin 
action\_result\.data\.\*\.categories | string |  |   Error 
action\_result\.data\.\*\.category\_count | numeric |  |   4 
action\_result\.data\.\*\.close\_time | string |  |   1602888300000 
action\_result\.data\.\*\.closing\_reason\_id | string |  `qradar offense closing reason id`  |   3 
action\_result\.data\.\*\.closing\_user | string |  |   root 
action\_result\.data\.\*\.credibility | numeric |  |   4 
action\_result\.data\.\*\.description | string |  |   Anomaly\: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks
 
action\_result\.data\.\*\.destination\_networks | string |  |   other 
action\_result\.data\.\*\.device\_count | numeric |  |   3 
action\_result\.data\.\*\.domain\_id | numeric |  |  
action\_result\.data\.\*\.event\_count | numeric |  |   1035 
action\_result\.data\.\*\.flow\_count | numeric |  |   0 
action\_result\.data\.\*\.follow\_up | boolean |  |   False  True 
action\_result\.data\.\*\.id | numeric |  `qradar offense id`  |   43 
action\_result\.data\.\*\.inactive | boolean |  |   False  True 
action\_result\.data\.\*\.last\_updated\_time | numeric |  |   1559125383270 
action\_result\.data\.\*\.local\_destination\_count | numeric |  |   0 
action\_result\.data\.\*\.magnitude | numeric |  |   4 
action\_result\.data\.\*\.offense\_source | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.offense\_type | numeric |  |   0 
action\_result\.data\.\*\.policy\_category\_count | numeric |  |   0 
action\_result\.data\.\*\.protected | boolean |  |   False  True 
action\_result\.data\.\*\.relevance | numeric |  |   2 
action\_result\.data\.\*\.remote\_destination\_count | numeric |  |   1 
action\_result\.data\.\*\.rules\.\*\.id | numeric |  |  
action\_result\.data\.\*\.rules\.\*\.type | string |  |  
action\_result\.data\.\*\.security\_category\_count | numeric |  |   4 
action\_result\.data\.\*\.severity | numeric |  |   7 
action\_result\.data\.\*\.source\_count | numeric |  |   1 
action\_result\.data\.\*\.source\_network | string |  |   other 
action\_result\.data\.\*\.start\_time | numeric |  |   1558008289506 
action\_result\.data\.\*\.status | string |  |   OPEN 
action\_result\.data\.\*\.username\_count | numeric |  `user name`  |   0 
action\_result\.summary\.flow\_count | numeric |  |   0 
action\_result\.summary\.name | string |  |   Anomaly\: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks 
action\_result\.summary\.source | string |  `ip`  |   122\.122\.122\.122 
action\_result\.summary\.start\_time | string |  |   2019\-04\-04 21\:28\:47 UTC 
action\_result\.summary\.status | string |  |   OPEN 
action\_result\.summary\.total\_offenses | numeric |  |   1 
action\_result\.summary\.update\_time | string |  |   2019\-05\-14 10\:23\:03 UTC 
action\_result\.message | string |  |   Total offenses\: 1 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'alt manage ingestion'
Manage ingestion details

Type: **generic**  
Read only: **False**

The general structure of the state file is \{"app\_version"\:"app\_version", "last\_saved\_ingest\_time"\:"epoch\_time\_last\_fetched\_offense", "last\_ingested\_events\_data"\:\{"offense\_id"\:"epoch\_time\_last\_fetched\_event\_for\_offense\_id"\}\}\. <ul><li>There is no validation for values provided in the <b>offense\_id</b> action parameter because this action does not make any API calls to the QRadar instance and it merely provides a way of manipulating the state file\. It is requested to please confirm if the offense ID being provided as an input exists on the QRadar instance\. Any wrong value provided in the <b>offense\_id</b> parameter may corrupt the state file and the functionalities dependent on it\.</li><li>No comma\-separated values should be provided in any of the action input parameters or else it may corrupt the state file and the functionalities dependent on it\.</li><li>The <b>set last saved offense ingest time</b> operation sets the epoch time of the provided value in the <b>datetime</b> parameter against the <b>last\_saved\_ingest\_time</b> key in the state file\.</li><li>The <b>set last saved events ingest time</b> operation sets the epoch time of the provided value in the <b>datetime</b> parameter against the key corresponding to the offense ID value provided in the <b>offense\_id</b> in the dictionary structure against the key <b>last\_ingested\_events\_data</b> in the state file\. The format for the date string should match the formats 'YYYY\-MM\-DD HH\:MM\:SS\.Z', 'YYYY\-MM\-DDTHH\:MM\:SS\.Z', 'YYYY\-MM\-DD', or 'HH\:MM\:SS\.Z'\. Users can provide only date \(time will be 00\:00\:00\.000000\) or only time \(current date will be considered by default\)\. The action considers that the provided value in the <b>datestring</b> parameter represents the date string in the timezone selected in the asset configuration parameter <b>timezone</b> and accordingly stores the epoch time into the state file\.</li><li>The <b>delete last saved ingestion time data</b> operation deletes the entire last saved ingestion time data stored in the state file\.</li><li>The <b>get last saved ingestion time data</b> operation fetches the entire last saved ingestion time data stored in the state file\.</li><li>The parameter <b>offense\_id</b> does not support comma\-separated values\. The user has to provide a single non\-zero positive integer value of the corresponding Offense ID\.</li><li>The parameter <b>offense\_id</b> is mandatory for the operation <b>set last saved events ingest time</b>\.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**operation** |  required  | Operation to perform on the ingestion data stored in the state file | string | 
**datetime** |  optional  | Datetime string to be stored against the ingestion data in the state file | string | 
**offense\_id** |  optional  | Offense ID against which to store the 'datetime' parameter value | string |  `qradar offense id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.datetime | string |  |   2019\-12\-09 11\:11\:11\.0001 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   4 
action\_result\.parameter\.operation | string |  |   get last saved ingestion time data 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time | string |  |   Offense ID\_1=Fri Nov 29 10\:05\:25 2019 UTC \+0000, Offense ID\_3=Fri Nov 29 10\:01\:24 2019 UTC \+0000, Offense ID\_2=Fri Nov 29 10\:03\:18 2019 UTC \+0000 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.1 | numeric |  |   1575021925702 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.10 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.19 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.20 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.21 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.22 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.23 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.24 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.74 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.75 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.76 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.77 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.78 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.79 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.80 | numeric |  |  
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.82 | numeric |  |  
action\_result\.data\.\*\.last\_saved\_offense\_ingest\_time | string |  |   Mon Dec 09 11\:11\:11 2019 UTC \+0000 
action\_result\.data\.\*\.last\_saved\_offense\_ingest\_time\_as\_epoch | numeric |  |   1575889871000 
action\_result\.summary\.last\_ingested\_events\_ingest\_time | string |  |   Offense ID\_1=Fri Nov 29 10\:05\:25 2019 UTC \+0000, Offense ID\_3=Fri Nov 29 10\:01\:24 2019 UTC \+0000, Offense ID\_2=Fri Nov 29 10\:03\:18 2019 UTC \+0000 
action\_result\.summary\.last\_saved\_offense\_ingest\_time | string |  |   Mon Dec 09 11\:11\:11 2019 UTC \+0000 
action\_result\.message | string |  |   Last saved offense ingest time\: Mon Dec 09 11\:11\:11 2019 UTC \+0000, Last ingested events ingest time\: Offense ID\_1=Fri Nov 29 10\:05\:25 2019 UTC \+0000, Offense ID\_3=Fri Nov 29 10\:01\:24 2019 UTC \+0000, Offense ID\_2=Fri Nov 29 10\:03\:18 2019 UTC \+0000 
summary\.total\_objects | numeric |  |   2 
summary\.total\_objects\_successful | numeric |  |   2   

## action: 'run query'
Execute an ariel query on the QRadar device

Type: **investigate**  
Read only: **True**

Use this action to execute queries using AQL on the QRadar device\. AQL is a well documented \(on the IBM website\) query language with quite a few built\-in functions\.<br>Do note that this action could have a dynamic set of values returned in the data array since the query can specify the columns to return\. This is the main reason for not listing the data paths\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**query** |  required  | Ariel Query | string |  `qradar ariel query` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.query | string |  `qradar ariel query`  |   select qid from events 
action\_result\.data\.\*\.events\.\*\.AccountDomain | string |  |  
action\_result\.data\.\*\.events\.\*\.Application | string |  |  
action\_result\.data\.\*\.events\.\*\.Bytes | string |  |  
action\_result\.data\.\*\.events\.\*\.BytesReceived | string |  |  
action\_result\.data\.\*\.events\.\*\.BytesSent | string |  |  
action\_result\.data\.\*\.events\.\*\.Destination Host Name | string |  |  
action\_result\.data\.\*\.events\.\*\.EventID | string |  |  
action\_result\.data\.\*\.events\.\*\.File Hash | string |  |  
action\_result\.data\.\*\.events\.\*\.File ID | string |  |  
action\_result\.data\.\*\.events\.\*\.File Path | string |  |  
action\_result\.data\.\*\.events\.\*\.Filename | string |  |  
action\_result\.data\.\*\.events\.\*\.Installer Filename | string |  |  
action\_result\.data\.\*\.events\.\*\.Message | string |  |  
action\_result\.data\.\*\.events\.\*\.Payload | string |  |  
action\_result\.data\.\*\.events\.\*\.Source Host Name | string |  |  
action\_result\.data\.\*\.events\.\*\.category | numeric |  |   38750003 
action\_result\.data\.\*\.events\.\*\.categoryname\_category | string |  |  
action\_result\.data\.\*\.events\.\*\.destinationaddress | string |  |  
action\_result\.data\.\*\.events\.\*\.destinationip | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.events\.\*\.destinationmac | string |  |  
action\_result\.data\.\*\.events\.\*\.destinationport | numeric |  |   0 
action\_result\.data\.\*\.events\.\*\.endtime | numeric |  |  
action\_result\.data\.\*\.events\.\*\.eventcount | numeric |  |   1 
action\_result\.data\.\*\.events\.\*\.eventdirection | string |  |  
action\_result\.data\.\*\.events\.\*\.hostname\_logsourceid | string |  |  
action\_result\.data\.\*\.events\.\*\.identityip | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.events\.\*\.logsourcegroupname\_logsourceid | string |  |  
action\_result\.data\.\*\.events\.\*\.logsourceid | numeric |  |   65 
action\_result\.data\.\*\.events\.\*\.logsourcename\_logsourceid | string |  |  
action\_result\.data\.\*\.events\.\*\.magnitude | numeric |  |   5 
action\_result\.data\.\*\.events\.\*\.protocolid | numeric |  |   255 
action\_result\.data\.\*\.events\.\*\.protocolname\_protocolid | string |  |  
action\_result\.data\.\*\.events\.\*\.qid | numeric |  |   38750003 
action\_result\.data\.\*\.events\.\*\.qidname\_qid | string |  |  
action\_result\.data\.\*\.events\.\*\.queid | numeric |  |  
action\_result\.data\.\*\.events\.\*\.relevance | numeric |  |  
action\_result\.data\.\*\.events\.\*\.severity | numeric |  |  
action\_result\.data\.\*\.events\.\*\.sourceaddress | string |  |  
action\_result\.data\.\*\.events\.\*\.sourceip | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.events\.\*\.sourcemac | string |  |  
action\_result\.data\.\*\.events\.\*\.sourceport | numeric |  |   0 
action\_result\.data\.\*\.events\.\*\.starttime | numeric |  |   1559907060001 
action\_result\.data\.\*\.events\.\*\.username | string |  `user name`  |  
action\_result\.data\.\*\.flows\.\*\.category | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.destinationbytes | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.destinationflags | string |  |  
action\_result\.data\.\*\.flows\.\*\.destinationip | string |  |  
action\_result\.data\.\*\.flows\.\*\.destinationpackets | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.firstpackettime | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.flowtype | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.lastpackettime | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.protocolid | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.qid | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.sourcebytes | numeric |  |  
action\_result\.data\.\*\.flows\.\*\.sourceflags | string |  |  
action\_result\.data\.\*\.flows\.\*\.sourceip | string |  |  
action\_result\.data\.\*\.flows\.\*\.sourcepackets | numeric |  |  
action\_result\.summary | string |  |  
action\_result\.message | string |  |   Successfully ran query 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'add listitem'
Add an item to a reference set in QRadar

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**reference\_set\_name** |  required  | Name of reference set to add to | string | 
**reference\_set\_value** |  required  | Value to add to the reference set | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.reference\_set\_name | string |  |   Demo 
action\_result\.parameter\.reference\_set\_value | string |  |   122\.122\.122\.122 
action\_result\.data\.\*\.creation\_time | numeric |  |   1558518483009 
action\_result\.data\.\*\.element\_type | string |  |   IP 
action\_result\.data\.\*\.name | string |  |   Demo 
action\_result\.data\.\*\.number\_of\_elements | numeric |  |   3 
action\_result\.data\.\*\.timeout\_type | string |  |   FIRST\_SEEN 
action\_result\.summary\.element\_type | string |  |   IP 
action\_result\.summary\.name | string |  |   Demo 
action\_result\.summary\.number\_of\_elements | numeric |  |   3 
action\_result\.message | string |  |   Element type\: IP, Name\: Demo, Number of elements\: 3 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'close offense'
Close an active offense, marking status=CLOSED

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense\_id** |  required  | Offense ID to close | numeric |  `qradar offense id` 
**closing\_reason\_id** |  required  | Reason for closing offense | numeric |  `qradar offense closing reason id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.closing\_reason\_id | numeric |  `qradar offense closing reason id`  |   1 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   41 
action\_result\.data\.\*\.assigned\_to | string |  |   admin 
action\_result\.data\.\*\.categories | string |  |   Error 
action\_result\.data\.\*\.category\_count | numeric |  |   4 
action\_result\.data\.\*\.close\_time | numeric |  |   1559905203000 
action\_result\.data\.\*\.closing\_reason\_id | numeric |  `qradar offense closing reason id`  |   1 
action\_result\.data\.\*\.closing\_user | string |  |   API\_token\: Phantom 
action\_result\.data\.\*\.credibility | numeric |  |   4 
action\_result\.data\.\*\.description | string |  |   Anomaly\: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks
 
action\_result\.data\.\*\.destination\_networks | string |  |   other 
action\_result\.data\.\*\.device\_count | numeric |  |   3 
action\_result\.data\.\*\.domain\_id | numeric |  |  
action\_result\.data\.\*\.event\_count | numeric |  |   2660 
action\_result\.data\.\*\.flow\_count | numeric |  |   0 
action\_result\.data\.\*\.follow\_up | boolean |  |   False  True 
action\_result\.data\.\*\.id | numeric |  `qradar offense id`  |   41 
action\_result\.data\.\*\.inactive | boolean |  |   False  True 
action\_result\.data\.\*\.last\_updated\_time | numeric |  |   1557829383413 
action\_result\.data\.\*\.local\_destination\_count | numeric |  |   0 
action\_result\.data\.\*\.magnitude | numeric |  |   3 
action\_result\.data\.\*\.offense\_source | string |  `ip`  |   122\.122\.122\.122 
action\_result\.data\.\*\.offense\_type | numeric |  |   0 
action\_result\.data\.\*\.policy\_category\_count | numeric |  |   0 
action\_result\.data\.\*\.protected | boolean |  |   False  True 
action\_result\.data\.\*\.relevance | numeric |  |   2 
action\_result\.data\.\*\.remote\_destination\_count | numeric |  |   1 
action\_result\.data\.\*\.rules\.\*\.id | numeric |  |  
action\_result\.data\.\*\.rules\.\*\.type | string |  |  
action\_result\.data\.\*\.security\_category\_count | numeric |  |   4 
action\_result\.data\.\*\.severity | numeric |  |   7 
action\_result\.data\.\*\.source\_count | numeric |  |   1 
action\_result\.data\.\*\.source\_network | string |  |   other 
action\_result\.data\.\*\.start\_time | numeric |  |   1554413327061 
action\_result\.data\.\*\.status | string |  |   CLOSED 
action\_result\.data\.\*\.username\_count | numeric |  `user name`  |   0 
action\_result\.summary\.flow\_count | numeric |  |   0 
action\_result\.summary\.name | string |  |   Anomaly\: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks 
action\_result\.summary\.source | string |  `ip`  |   122\.122\.122\.122 
action\_result\.summary\.start\_time | string |  |   2019\-04\-04 21\:28\:47 UTC 
action\_result\.summary\.status | string |  |   CLOSED 
action\_result\.summary\.update\_time | string |  |   2019\-05\-14 10\:23\:03 UTC 
action\_result\.message | string |  |   Status\: CLOSED, Source\: 122\.122\.122\.122, Update time\: 2019\-05\-14 10\:23\:03 UTC, Name\: Anomaly\: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks, Flow count\: 0, Start time\: 2019\-04\-04 21\:28\:47 UTC 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'update offense'
Attach a note to an offense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense\_id** |  required  | Offense ID to attach note to | numeric |  `qradar offense id` 
**note\_text** |  required  | Text to put into note | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.note\_text | string |  |   Note Added By Phantom 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   41 
action\_result\.data | string |  |  
action\_result\.summary | string |  |  
action\_result\.message | string |  |   Successfully added note to offense 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'assign user'
Assign the user to an offense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense\_id** |  required  | Offense ID to assign the user to | numeric |  `qradar offense id` 
**assignee** |  required  | Name of the user | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.assignee | string |  |   admin 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id`  |   41 
action\_result\.data | string |  |  
action\_result\.summary | string |  |  
action\_result\.message | string |  |   Successfully assigned user to offense 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'get rule info'
Retrieve QRadar rule information

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**rule\_id** |  required  | Rule ID for which information needs to be extracted | numeric |  `qradar rule id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.rule\_id | numeric |  `qradar rule id`  |   1421 
action\_result\.data\.\*\.average\_capacity | numeric |  |   3541750 
action\_result\.data\.\*\.base\_capacity | numeric |  |   3541750 
action\_result\.data\.\*\.base\_host\_id | numeric |  |   384 
action\_result\.data\.\*\.capacity\_timestamp | numeric |  |   1566896735557 
action\_result\.data\.\*\.creation\_date | numeric |  |   1155662266056 
action\_result\.data\.\*\.enabled | boolean |  |   True  False 
action\_result\.data\.\*\.id | numeric |  |   1421 
action\_result\.data\.\*\.identifier | string |  |   SYSTEM\-1421 
action\_result\.data\.\*\.linked\_rule\_identifier | string |  |  
action\_result\.data\.\*\.modification\_date | numeric |  |   1267729985038 
action\_result\.data\.\*\.name | string |  |   User\:BB\:FalsePositives\: User Defined Server Type 2 False Positive Categories 
action\_result\.data\.\*\.origin | string |  |   SYSTEM 
action\_result\.data\.\*\.owner | string |  |   admin 
action\_result\.data\.\*\.type | string |  |   EVENT 
action\_result\.summary\.id | numeric |  |   1421 
action\_result\.summary\.name | string |  |   User\:BB\:FalsePositives\: User Defined Server Type 2 False Positive Categories 
action\_result\.message | string |  |   Id\: 1421, Name\: User\:BB\:FalsePositives\: User Defined Server Type 2 False Positive Categories 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'list rules'
List all QRadar rules

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**count** |  optional  | Number of rules to retrieve | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action\_result\.status | string |  |   success  failed 
action\_result\.parameter\.count | numeric |  |   31 
action\_result\.data\.\*\.average\_capacity | numeric |  |   3541750 
action\_result\.data\.\*\.base\_capacity | numeric |  |   3541750 
action\_result\.data\.\*\.base\_host\_id | numeric |  |   384 
action\_result\.data\.\*\.capacity\_timestamp | numeric |  |   1566896735557 
action\_result\.data\.\*\.creation\_date | numeric |  |   1155662266056 
action\_result\.data\.\*\.enabled | boolean |  |   True  False 
action\_result\.data\.\*\.id | numeric |  `qradar rule id`  |   1421 
action\_result\.data\.\*\.identifier | string |  |   SYSTEM\-1421 
action\_result\.data\.\*\.linked\_rule\_identifier | string |  |  
action\_result\.data\.\*\.modification\_date | numeric |  |   1267729985038 
action\_result\.data\.\*\.name | string |  |   User\:BB\:FalsePositives\: User Defined Server Type 2 False Positive Categories 
action\_result\.data\.\*\.origin | string |  |   SYSTEM 
action\_result\.data\.\*\.owner | string |  |   admin 
action\_result\.data\.\*\.type | string |  |   EVENT 
action\_result\.summary\.total\_rules | numeric |  |   135 
action\_result\.message | string |  |   Total rules\: 135 
summary\.total\_objects | numeric |  |   1 
summary\.total\_objects\_successful | numeric |  |   1   

## action: 'on poll'
Callback action for the on\_poll ingest functionality

Type: **ingest**  
Read only: **True**

The default start\_time is the past 5 days\. The default end\_time is now\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container\_id** |  optional  | Parameter ignored for this app | string | 
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\) | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\) | numeric | 
**container\_count** |  optional  | Maximum number of container records to query for | numeric | 
**artifact\_count** |  optional  | Parameter ignored for this app | numeric | 

#### Action Output
No Output
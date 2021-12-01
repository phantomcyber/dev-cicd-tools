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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.count | numeric | 
action\_result\.parameter\.end\_time | numeric | 
action\_result\.parameter\.offense\_id | string |  `qradar offense id` 
action\_result\.parameter\.start\_time | numeric | 
action\_result\.data\.\*\.assigned\_to | string | 
action\_result\.data\.\*\.categories | string | 
action\_result\.data\.\*\.category\_count | numeric | 
action\_result\.data\.\*\.close\_time | string | 
action\_result\.data\.\*\.closing\_reason\_id | string |  `qradar offense closing reason id` 
action\_result\.data\.\*\.closing\_user | string | 
action\_result\.data\.\*\.credibility | numeric | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.destination\_networks | string | 
action\_result\.data\.\*\.device\_count | numeric | 
action\_result\.data\.\*\.domain\_id | numeric | 
action\_result\.data\.\*\.event\_count | numeric | 
action\_result\.data\.\*\.flow\_count | numeric | 
action\_result\.data\.\*\.follow\_up | boolean | 
action\_result\.data\.\*\.id | numeric |  `qradar offense id` 
action\_result\.data\.\*\.inactive | boolean | 
action\_result\.data\.\*\.last\_updated\_time | numeric | 
action\_result\.data\.\*\.local\_destination\_count | numeric | 
action\_result\.data\.\*\.magnitude | numeric | 
action\_result\.data\.\*\.offense\_source | string |  `ip` 
action\_result\.data\.\*\.offense\_type | numeric | 
action\_result\.data\.\*\.policy\_category\_count | numeric | 
action\_result\.data\.\*\.protected | boolean | 
action\_result\.data\.\*\.relevance | numeric | 
action\_result\.data\.\*\.remote\_destination\_count | numeric | 
action\_result\.data\.\*\.rules\.\*\.id | numeric | 
action\_result\.data\.\*\.rules\.\*\.type | string | 
action\_result\.data\.\*\.security\_category\_count | numeric | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.data\.\*\.source\_count | numeric | 
action\_result\.data\.\*\.source\_network | string | 
action\_result\.data\.\*\.start\_time | numeric | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.username\_count | numeric |  `user name` 
action\_result\.summary | string | 
action\_result\.summary\.total\_offenses | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.include\_deleted | boolean | 
action\_result\.parameter\.include\_reserved | boolean | 
action\_result\.data\.\*\.id | numeric |  `qradar offense closing reason id` 
action\_result\.data\.\*\.is\_deleted | boolean | 
action\_result\.data\.\*\.is\_reserved | boolean | 
action\_result\.data\.\*\.text | string | 
action\_result\.summary\.total\_offense\_closing\_reasons | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.count | numeric | 
action\_result\.parameter\.end\_time | numeric | 
action\_result\.parameter\.fields\_filter | string | 
action\_result\.parameter\.interval\_days | numeric | 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.parameter\.start\_time | numeric | 
action\_result\.data\.\*\.AccountDomain | string |  `domain`  `url` 
action\_result\.data\.\*\.Application | string | 
action\_result\.data\.\*\.Bytes | string | 
action\_result\.data\.\*\.BytesReceived | string | 
action\_result\.data\.\*\.BytesSent | string | 
action\_result\.data\.\*\.Destination Host Name | string |  `host name` 
action\_result\.data\.\*\.EventID | string | 
action\_result\.data\.\*\.File Hash | string | 
action\_result\.data\.\*\.File ID | string | 
action\_result\.data\.\*\.File Path | string | 
action\_result\.data\.\*\.Filename | string | 
action\_result\.data\.\*\.Hostname | string |  `host name` 
action\_result\.data\.\*\.Installer Filename | string | 
action\_result\.data\.\*\.Message | string | 
action\_result\.data\.\*\.Payload | string | 
action\_result\.data\.\*\.Source Host Name | string |  `host name` 
action\_result\.data\.\*\.categoryname\_category | string | 
action\_result\.data\.\*\.destinationaddress | string |  `ip` 
action\_result\.data\.\*\.destinationip | string |  `ip` 
action\_result\.data\.\*\.destinationmac | string | 
action\_result\.data\.\*\.destinationport | numeric |  `port` 
action\_result\.data\.\*\.endtime | numeric | 
action\_result\.data\.\*\.eventcount | numeric | 
action\_result\.data\.\*\.eventdirection | string | 
action\_result\.data\.\*\.hostname\_logsourceid | string |  `host name` 
action\_result\.data\.\*\.identityip | string |  `ip` 
action\_result\.data\.\*\.logsourcegroupname\_logsourceid | string | 
action\_result\.data\.\*\.logsourceid | numeric | 
action\_result\.data\.\*\.logsourcename\_logsourceid | string | 
action\_result\.data\.\*\.protocolname\_protocolid | string | 
action\_result\.data\.\*\.qid | numeric | 
action\_result\.data\.\*\.qidname\_qid | string | 
action\_result\.data\.\*\.relevance | numeric | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.data\.\*\.sourceaddress | string |  `ip` 
action\_result\.data\.\*\.sourceip | string |  `ip` 
action\_result\.data\.\*\.sourcemac | string | 
action\_result\.data\.\*\.sourceport | numeric |  `port` 
action\_result\.data\.\*\.sourcev6 | string |  `ipv6` 
action\_result\.data\.\*\.starttime | numeric | 
action\_result\.data\.\*\.username | string |  `user name` 
action\_result\.summary\.total\_events | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.count | numeric | 
action\_result\.parameter\.end\_time | numeric | 
action\_result\.parameter\.fields\_filter | string | 
action\_result\.parameter\.ip | string |  `ip` 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.parameter\.start\_time | numeric | 
action\_result\.data\.\*\.Action | string | 
action\_result\.data\.\*\.Application Determination Algorithm | numeric | 
action\_result\.data\.\*\.Content Subject | string | 
action\_result\.data\.\*\.Content Type | string | 
action\_result\.data\.\*\.FTP Pass | string | 
action\_result\.data\.\*\.FTP RETR File | string | 
action\_result\.data\.\*\.FTP User | string | 
action\_result\.data\.\*\.File Entropy | string | 
action\_result\.data\.\*\.File Hash | string | 
action\_result\.data\.\*\.File Name | string | 
action\_result\.data\.\*\.File Size | string | 
action\_result\.data\.\*\.Flow Direction Algorithm | numeric | 
action\_result\.data\.\*\.Google Search Terms | string | 
action\_result\.data\.\*\.HTTP Content\-Type | string | 
action\_result\.data\.\*\.HTTP GET Request | string | 
action\_result\.data\.\*\.HTTP Host | string | 
action\_result\.data\.\*\.HTTP Referer | string | 
action\_result\.data\.\*\.HTTP Referrer | string | 
action\_result\.data\.\*\.HTTP Response Code | string | 
action\_result\.data\.\*\.HTTP Server | string | 
action\_result\.data\.\*\.HTTP User Agent | string | 
action\_result\.data\.\*\.HTTP User\-Agent | string | 
action\_result\.data\.\*\.HTTP Version | string | 
action\_result\.data\.\*\.Originating User | string | 
action\_result\.data\.\*\.Password | string | 
action\_result\.data\.\*\.Request URL | string | 
action\_result\.data\.\*\.SMTP From | string | 
action\_result\.data\.\*\.SMTP HELO | string | 
action\_result\.data\.\*\.SMTP Hello | string | 
action\_result\.data\.\*\.SMTP To | string | 
action\_result\.data\.\*\.Search Arguments | string | 
action\_result\.data\.\*\.VLAN Tag | string | 
action\_result\.data\.\*\.applicationid | numeric | 
action\_result\.data\.\*\.applicationname\_applicationid | string | 
action\_result\.data\.\*\.category | numeric | 
action\_result\.data\.\*\.categoryname\_category | string | 
action\_result\.data\.\*\.credibility | numeric | 
action\_result\.data\.\*\.destinationasn | string | 
action\_result\.data\.\*\.destinationbytes | numeric | 
action\_result\.data\.\*\.destinationdscp | numeric | 
action\_result\.data\.\*\.destinationflags | string | 
action\_result\.data\.\*\.destinationifindex | string | 
action\_result\.data\.\*\.destinationip | string |  `ip` 
action\_result\.data\.\*\.destinationpackets | numeric | 
action\_result\.data\.\*\.destinationpayload | string | 
action\_result\.data\.\*\.destinationport | numeric |  `port` 
action\_result\.data\.\*\.destinationprecedence | numeric | 
action\_result\.data\.\*\.destinationv6 | string | 
action\_result\.data\.\*\.domainid | numeric | 
action\_result\.data\.\*\.firstpackettime | numeric | 
action\_result\.data\.\*\.flowbias | string | 
action\_result\.data\.\*\.flowdirection | string | 
action\_result\.data\.\*\.flowid | numeric | 
action\_result\.data\.\*\.flowinterface | string | 
action\_result\.data\.\*\.flowinterfaceid | string | 
action\_result\.data\.\*\.flowsource | string | 
action\_result\.data\.\*\.flowtype | numeric | 
action\_result\.data\.\*\.fullmatchlist | string | 
action\_result\.data\.\*\.geographic | string | 
action\_result\.data\.\*\.hasdestinationpayload | boolean | 
action\_result\.data\.\*\.hasoffense | boolean | 
action\_result\.data\.\*\.hassourcepayload | boolean | 
action\_result\.data\.\*\.hastlv | boolean | 
action\_result\.data\.\*\.icmpcode | string | 
action\_result\.data\.\*\.icmptype | string | 
action\_result\.data\.\*\.intervalid | numeric | 
action\_result\.data\.\*\.isduplicate | boolean | 
action\_result\.data\.\*\.lastpackettime | numeric | 
action\_result\.data\.\*\.partialmatchlist | string | 
action\_result\.data\.\*\.processorid | numeric | 
action\_result\.data\.\*\.protocolid | numeric | 
action\_result\.data\.\*\.protocolname\_protocolid | string | 
action\_result\.data\.\*\.qid | numeric | 
action\_result\.data\.\*\.qidname\_qid | string | 
action\_result\.data\.\*\.relevance | numeric | 
action\_result\.data\.\*\.retentionbucket | string | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.data\.\*\.sourceasn | string | 
action\_result\.data\.\*\.sourcebytes | numeric | 
action\_result\.data\.\*\.sourcedscp | numeric | 
action\_result\.data\.\*\.sourceflags | string | 
action\_result\.data\.\*\.sourceifindex | string | 
action\_result\.data\.\*\.sourceip | string |  `ip` 
action\_result\.data\.\*\.sourcepackets | numeric | 
action\_result\.data\.\*\.sourcepayload | string | 
action\_result\.data\.\*\.sourceport | numeric | 
action\_result\.data\.\*\.sourceprecedence | numeric | 
action\_result\.data\.\*\.sourcev6 | string |  `ipv6` 
action\_result\.data\.\*\.starttime | numeric | 
action\_result\.data\.\*\.viewobjectpair | string | 
action\_result\.summary\.total\_flows | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.ingest\_offense | boolean | 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.parameter\.tenant\_id | numeric | 
action\_result\.data\.\*\.assigned\_to | string | 
action\_result\.data\.\*\.categories | string | 
action\_result\.data\.\*\.category\_count | numeric | 
action\_result\.data\.\*\.close\_time | string | 
action\_result\.data\.\*\.closing\_reason\_id | string |  `qradar offense closing reason id` 
action\_result\.data\.\*\.closing\_user | string | 
action\_result\.data\.\*\.credibility | numeric | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.destination\_networks | string | 
action\_result\.data\.\*\.device\_count | numeric | 
action\_result\.data\.\*\.domain\_id | numeric | 
action\_result\.data\.\*\.event\_count | numeric | 
action\_result\.data\.\*\.flow\_count | numeric | 
action\_result\.data\.\*\.follow\_up | boolean | 
action\_result\.data\.\*\.id | numeric |  `qradar offense id` 
action\_result\.data\.\*\.inactive | boolean | 
action\_result\.data\.\*\.last\_updated\_time | numeric | 
action\_result\.data\.\*\.local\_destination\_count | numeric | 
action\_result\.data\.\*\.magnitude | numeric | 
action\_result\.data\.\*\.offense\_source | string |  `ip` 
action\_result\.data\.\*\.offense\_type | numeric | 
action\_result\.data\.\*\.policy\_category\_count | numeric | 
action\_result\.data\.\*\.protected | boolean | 
action\_result\.data\.\*\.relevance | numeric | 
action\_result\.data\.\*\.remote\_destination\_count | numeric | 
action\_result\.data\.\*\.rules\.\*\.id | numeric | 
action\_result\.data\.\*\.rules\.\*\.type | string | 
action\_result\.data\.\*\.security\_category\_count | numeric | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.data\.\*\.source\_count | numeric | 
action\_result\.data\.\*\.source\_network | string | 
action\_result\.data\.\*\.start\_time | numeric | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.username\_count | numeric |  `user name` 
action\_result\.summary\.flow\_count | numeric | 
action\_result\.summary\.name | string | 
action\_result\.summary\.source | string |  `ip` 
action\_result\.summary\.start\_time | string | 
action\_result\.summary\.status | string | 
action\_result\.summary\.total\_offenses | numeric | 
action\_result\.summary\.update\_time | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.datetime | string | 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.parameter\.operation | string | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time | string | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.1 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.10 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.19 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.20 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.21 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.22 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.23 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.24 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.74 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.75 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.76 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.77 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.78 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.79 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.80 | numeric | 
action\_result\.data\.\*\.last\_ingested\_events\_ingest\_time\_as\_epoch\.82 | numeric | 
action\_result\.data\.\*\.last\_saved\_offense\_ingest\_time | string | 
action\_result\.data\.\*\.last\_saved\_offense\_ingest\_time\_as\_epoch | numeric | 
action\_result\.summary\.last\_ingested\_events\_ingest\_time | string | 
action\_result\.summary\.last\_saved\_offense\_ingest\_time | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.query | string |  `qradar ariel query` 
action\_result\.data\.\*\.events\.\*\.AccountDomain | string | 
action\_result\.data\.\*\.events\.\*\.Application | string | 
action\_result\.data\.\*\.events\.\*\.Bytes | string | 
action\_result\.data\.\*\.events\.\*\.BytesReceived | string | 
action\_result\.data\.\*\.events\.\*\.BytesSent | string | 
action\_result\.data\.\*\.events\.\*\.Destination Host Name | string | 
action\_result\.data\.\*\.events\.\*\.EventID | string | 
action\_result\.data\.\*\.events\.\*\.File Hash | string | 
action\_result\.data\.\*\.events\.\*\.File ID | string | 
action\_result\.data\.\*\.events\.\*\.File Path | string | 
action\_result\.data\.\*\.events\.\*\.Filename | string | 
action\_result\.data\.\*\.events\.\*\.Installer Filename | string | 
action\_result\.data\.\*\.events\.\*\.Message | string | 
action\_result\.data\.\*\.events\.\*\.Payload | string | 
action\_result\.data\.\*\.events\.\*\.Source Host Name | string | 
action\_result\.data\.\*\.events\.\*\.category | numeric | 
action\_result\.data\.\*\.events\.\*\.categoryname\_category | string | 
action\_result\.data\.\*\.events\.\*\.destinationaddress | string | 
action\_result\.data\.\*\.events\.\*\.destinationip | string |  `ip` 
action\_result\.data\.\*\.events\.\*\.destinationmac | string | 
action\_result\.data\.\*\.events\.\*\.destinationport | numeric | 
action\_result\.data\.\*\.events\.\*\.endtime | numeric | 
action\_result\.data\.\*\.events\.\*\.eventcount | numeric | 
action\_result\.data\.\*\.events\.\*\.eventdirection | string | 
action\_result\.data\.\*\.events\.\*\.hostname\_logsourceid | string | 
action\_result\.data\.\*\.events\.\*\.identityip | string |  `ip` 
action\_result\.data\.\*\.events\.\*\.logsourcegroupname\_logsourceid | string | 
action\_result\.data\.\*\.events\.\*\.logsourceid | numeric | 
action\_result\.data\.\*\.events\.\*\.logsourcename\_logsourceid | string | 
action\_result\.data\.\*\.events\.\*\.magnitude | numeric | 
action\_result\.data\.\*\.events\.\*\.protocolid | numeric | 
action\_result\.data\.\*\.events\.\*\.protocolname\_protocolid | string | 
action\_result\.data\.\*\.events\.\*\.qid | numeric | 
action\_result\.data\.\*\.events\.\*\.qidname\_qid | string | 
action\_result\.data\.\*\.events\.\*\.queid | numeric | 
action\_result\.data\.\*\.events\.\*\.relevance | numeric | 
action\_result\.data\.\*\.events\.\*\.severity | numeric | 
action\_result\.data\.\*\.events\.\*\.sourceaddress | string | 
action\_result\.data\.\*\.events\.\*\.sourceip | string |  `ip` 
action\_result\.data\.\*\.events\.\*\.sourcemac | string | 
action\_result\.data\.\*\.events\.\*\.sourceport | numeric | 
action\_result\.data\.\*\.events\.\*\.starttime | numeric | 
action\_result\.data\.\*\.events\.\*\.username | string |  `user name` 
action\_result\.data\.\*\.flows\.\*\.category | numeric | 
action\_result\.data\.\*\.flows\.\*\.destinationbytes | numeric | 
action\_result\.data\.\*\.flows\.\*\.destinationflags | string | 
action\_result\.data\.\*\.flows\.\*\.destinationip | string | 
action\_result\.data\.\*\.flows\.\*\.destinationpackets | numeric | 
action\_result\.data\.\*\.flows\.\*\.firstpackettime | numeric | 
action\_result\.data\.\*\.flows\.\*\.flowtype | numeric | 
action\_result\.data\.\*\.flows\.\*\.lastpackettime | numeric | 
action\_result\.data\.\*\.flows\.\*\.protocolid | numeric | 
action\_result\.data\.\*\.flows\.\*\.qid | numeric | 
action\_result\.data\.\*\.flows\.\*\.sourcebytes | numeric | 
action\_result\.data\.\*\.flows\.\*\.sourceflags | string | 
action\_result\.data\.\*\.flows\.\*\.sourceip | string | 
action\_result\.data\.\*\.flows\.\*\.sourcepackets | numeric | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.reference\_set\_name | string | 
action\_result\.parameter\.reference\_set\_value | string | 
action\_result\.data\.\*\.creation\_time | numeric | 
action\_result\.data\.\*\.element\_type | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.number\_of\_elements | numeric | 
action\_result\.data\.\*\.timeout\_type | string | 
action\_result\.summary\.element\_type | string | 
action\_result\.summary\.name | string | 
action\_result\.summary\.number\_of\_elements | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.closing\_reason\_id | numeric |  `qradar offense closing reason id` 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.data\.\*\.assigned\_to | string | 
action\_result\.data\.\*\.categories | string | 
action\_result\.data\.\*\.category\_count | numeric | 
action\_result\.data\.\*\.close\_time | numeric | 
action\_result\.data\.\*\.closing\_reason\_id | numeric |  `qradar offense closing reason id` 
action\_result\.data\.\*\.closing\_user | string | 
action\_result\.data\.\*\.credibility | numeric | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.destination\_networks | string | 
action\_result\.data\.\*\.device\_count | numeric | 
action\_result\.data\.\*\.domain\_id | numeric | 
action\_result\.data\.\*\.event\_count | numeric | 
action\_result\.data\.\*\.flow\_count | numeric | 
action\_result\.data\.\*\.follow\_up | boolean | 
action\_result\.data\.\*\.id | numeric |  `qradar offense id` 
action\_result\.data\.\*\.inactive | boolean | 
action\_result\.data\.\*\.last\_updated\_time | numeric | 
action\_result\.data\.\*\.local\_destination\_count | numeric | 
action\_result\.data\.\*\.magnitude | numeric | 
action\_result\.data\.\*\.offense\_source | string |  `ip` 
action\_result\.data\.\*\.offense\_type | numeric | 
action\_result\.data\.\*\.policy\_category\_count | numeric | 
action\_result\.data\.\*\.protected | boolean | 
action\_result\.data\.\*\.relevance | numeric | 
action\_result\.data\.\*\.remote\_destination\_count | numeric | 
action\_result\.data\.\*\.rules\.\*\.id | numeric | 
action\_result\.data\.\*\.rules\.\*\.type | string | 
action\_result\.data\.\*\.security\_category\_count | numeric | 
action\_result\.data\.\*\.severity | numeric | 
action\_result\.data\.\*\.source\_count | numeric | 
action\_result\.data\.\*\.source\_network | string | 
action\_result\.data\.\*\.start\_time | numeric | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.username\_count | numeric |  `user name` 
action\_result\.summary\.flow\_count | numeric | 
action\_result\.summary\.name | string | 
action\_result\.summary\.source | string |  `ip` 
action\_result\.summary\.start\_time | string | 
action\_result\.summary\.status | string | 
action\_result\.summary\.update\_time | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.note\_text | string | 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.assignee | string | 
action\_result\.parameter\.offense\_id | numeric |  `qradar offense id` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get rule info'
Retrieve QRadar rule information

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**rule\_id** |  required  | Rule ID for which information needs to be extracted | numeric |  `qradar rule id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.rule\_id | numeric |  `qradar rule id` 
action\_result\.data\.\*\.average\_capacity | numeric | 
action\_result\.data\.\*\.base\_capacity | numeric | 
action\_result\.data\.\*\.base\_host\_id | numeric | 
action\_result\.data\.\*\.capacity\_timestamp | numeric | 
action\_result\.data\.\*\.creation\_date | numeric | 
action\_result\.data\.\*\.enabled | boolean | 
action\_result\.data\.\*\.id | numeric | 
action\_result\.data\.\*\.identifier | string | 
action\_result\.data\.\*\.linked\_rule\_identifier | string | 
action\_result\.data\.\*\.modification\_date | numeric | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.origin | string | 
action\_result\.data\.\*\.owner | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.summary\.id | numeric | 
action\_result\.summary\.name | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list rules'
List all QRadar rules

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**count** |  optional  | Number of rules to retrieve | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.count | numeric | 
action\_result\.data\.\*\.average\_capacity | numeric | 
action\_result\.data\.\*\.base\_capacity | numeric | 
action\_result\.data\.\*\.base\_host\_id | numeric | 
action\_result\.data\.\*\.capacity\_timestamp | numeric | 
action\_result\.data\.\*\.creation\_date | numeric | 
action\_result\.data\.\*\.enabled | boolean | 
action\_result\.data\.\*\.id | numeric |  `qradar rule id` 
action\_result\.data\.\*\.identifier | string | 
action\_result\.data\.\*\.linked\_rule\_identifier | string | 
action\_result\.data\.\*\.modification\_date | numeric | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.origin | string | 
action\_result\.data\.\*\.owner | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.summary\.total\_rules | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

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
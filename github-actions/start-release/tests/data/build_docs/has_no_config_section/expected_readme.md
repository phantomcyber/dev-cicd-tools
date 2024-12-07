[comment]: # "Auto-generated SOAR connector documentation"
# QRadar

Publisher: Splunk  
Connector Version: 2.1.2  
Product Vendor: IBM  
Product Name: QRadar  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 4.9.39220  

This app supports generic, investigative, and ingestion actions on an IBM QRadar device

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity. This action runs a quick query on the device to check the connection and credentials  
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
[on poll](#action-on-poll) - Callback action for the on_poll ingest functionality  

## action: 'test connectivity'
Validate the asset configuration for connectivity. This action runs a quick query on the device to check the connection and credentials

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

The default start_time is the past 5 days. The default end_time is now. The default count is 100 offenses.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start_time** |  optional  | Start of time range, in epoch time (milliseconds) | numeric | 
**end_time** |  optional  | End of time range, in epoch time (milliseconds) | numeric | 
**count** |  optional  | Number of offenses to retrieve | numeric | 
**offense_id** |  optional  | Comma-separated list of offense IDs to fetch | string |  `qradar offense id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.count | numeric |  |   100 
action_result.parameter.end_time | numeric |  |   1669900000000 
action_result.parameter.offense_id | string |  `qradar offense id`  |   44 
action_result.parameter.start_time | numeric |  |   1559900000000 
action_result.data.\*.assigned_to | string |  |   admin 
action_result.data.\*.categories | string |  |   License Status 
action_result.data.\*.category_count | numeric |  |   10 
action_result.data.\*.close_time | string |  |  
action_result.data.\*.closing_reason_id | string |  `qradar offense closing reason id`  |  
action_result.data.\*.closing_user | string |  |  
action_result.data.\*.credibility | numeric |  |   4 
action_result.data.\*.description | string |  |   Local Malware Events
 
action_result.data.\*.destination_networks | string |  |   other 
action_result.data.\*.device_count | numeric |  |   3 
action_result.data.\*.domain_id | numeric |  |  
action_result.data.\*.event_count | numeric |  |   28603163 
action_result.data.\*.flow_count | numeric |  |   110 
action_result.data.\*.follow_up | boolean |  |   False  True 
action_result.data.\*.id | numeric |  `qradar offense id`  |   44 
action_result.data.\*.inactive | boolean |  |   False  True 
action_result.data.\*.last_updated_time | numeric |  |   1559194600958 
action_result.data.\*.local_destination_count | numeric |  |   0 
action_result.data.\*.magnitude | numeric |  |   5 
action_result.data.\*.offense_source | string |  `ip`  |   122.122.122.122 
action_result.data.\*.offense_type | numeric |  |   0 
action_result.data.\*.policy_category_count | numeric |  |   0 
action_result.data.\*.protected | boolean |  |   False  True 
action_result.data.\*.relevance | numeric |  |   4 
action_result.data.\*.remote_destination_count | numeric |  |   1 
action_result.data.\*.rules.\*.id | numeric |  |  
action_result.data.\*.rules.\*.type | string |  |  
action_result.data.\*.security_category_count | numeric |  |   10 
action_result.data.\*.severity | numeric |  |   6 
action_result.data.\*.source_count | numeric |  |   1 
action_result.data.\*.source_network | string |  |   Net-10-172-192.Net_10_0_0_0 
action_result.data.\*.start_time | numeric |  |   1558009780686 
action_result.data.\*.status | string |  |   OPEN 
action_result.data.\*.username_count | numeric |  `user name`  |   0 
action_result.summary | string |  |  
action_result.summary.total_offenses | numeric |  |   1 
action_result.message | string |  |   Fetching all open offenses. Total offenses: 1  Total Offenses: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list closing reasons'
Get a list of offense closing reasons

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**include_reserved** |  optional  | Include reserved offense closing reasons | boolean | 
**include_deleted** |  optional  | Include deleted offense closing reasons | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.include_deleted | boolean |  |   True  False 
action_result.parameter.include_reserved | boolean |  |   True  False 
action_result.data.\*.id | numeric |  `qradar offense closing reason id`  |   2 
action_result.data.\*.is_deleted | boolean |  |   True  False 
action_result.data.\*.is_reserved | boolean |  |   True  False 
action_result.data.\*.text | string |  |   False-Positive, Tuned 
action_result.summary.total_offense_closing_reasons | numeric |  |   5 
action_result.message | string |  |   Total offense closing reasons: 5 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get events'
Get events belonging to an offense

Type: **investigate**  
Read only: **True**

Use fields_filter parameter to restrict the events returned that match the filter. For e.g. destinationip='10.10.0.52' and protocolid='6'. For further details refer to the documentation section of the action in the README.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** |  optional  | Offense ID to get events of | numeric |  `qradar offense id` 
**start_time** |  optional  | Start of time range, in epoch time (milliseconds) | numeric | 
**end_time** |  optional  | End of time range, in epoch time (milliseconds) | numeric | 
**count** |  optional  | Number of events to retrieve | numeric | 
**fields_filter** |  optional  | Filter on event field values | string | 
**interval_days** |  optional  | Interval days | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.count | numeric |  |   10 
action_result.parameter.end_time | numeric |  |   1669891174855 
action_result.parameter.fields_filter | string |  |   sourceip='122.122.122.122' 
action_result.parameter.interval_days | numeric |  |   20 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   44 
action_result.parameter.start_time | numeric |  |   1559891174855 
action_result.data.\*.AccountDomain | string |  `domain`  `url`  |  
action_result.data.\*.Application | string |  |  
action_result.data.\*.Bytes | string |  |  
action_result.data.\*.BytesReceived | string |  |  
action_result.data.\*.BytesSent | string |  |  
action_result.data.\*.Destination Host Name | string |  `host name`  |  
action_result.data.\*.EventID | string |  |  
action_result.data.\*.File Hash | string |  |  
action_result.data.\*.File ID | string |  |  
action_result.data.\*.File Path | string |  |  
action_result.data.\*.Filename | string |  |  
action_result.data.\*.Hostname | string |  `host name`  |  
action_result.data.\*.Installer Filename | string |  |  
action_result.data.\*.Message | string |  |  
action_result.data.\*.Payload | string |  |   Communication with Known Watched Networks	There has been event communication with networks that appear on the systems watch and darknet lists. 
action_result.data.\*.Source Host Name | string |  `host name`  |  
action_result.data.\*.categoryname_category | string |  |   Suspicious Activity 
action_result.data.\*.destinationaddress | string |  `ip`  |   122.122.122.122 
action_result.data.\*.destinationip | string |  `ip`  |   122.122.122.122 
action_result.data.\*.destinationmac | string |  |   00:00:00:00:00:00 
action_result.data.\*.destinationport | numeric |  `port`  |   0 
action_result.data.\*.endtime | numeric |  |  
action_result.data.\*.eventcount | numeric |  |  
action_result.data.\*.eventdirection | string |  |   L2R  R2R 
action_result.data.\*.hostname_logsourceid | string |  `host name`  |   Unknown Host 63 
action_result.data.\*.identityip | string |  `ip`  |  
action_result.data.\*.logsourcegroupname_logsourceid | string |  |   Other 
action_result.data.\*.logsourceid | numeric |  |   63 
action_result.data.\*.logsourcename_logsourceid | string |  |   Custom Rule Engine-8 :: qradar 
action_result.data.\*.protocolname_protocolid | string |  |   Reserved 
action_result.data.\*.qid | numeric |  |   70750119 
action_result.data.\*.qidname_qid | string |  |   Communication with Known Watched Networks 
action_result.data.\*.relevance | numeric |  |  
action_result.data.\*.severity | numeric |  |  
action_result.data.\*.sourceaddress | string |  `ip`  |   122.122.122.122 
action_result.data.\*.sourceip | string |  `ip`  |   122.122.122.122 
action_result.data.\*.sourcemac | string |  |   00:00:00:00:00:00 
action_result.data.\*.sourceport | numeric |  `port`  |   0 
action_result.data.\*.sourcev6 | string |  `ipv6`  |  
action_result.data.\*.starttime | numeric |  |   1559194870184 
action_result.data.\*.username | string |  `user name`  |  
action_result.summary.total_events | numeric |  |   10 
action_result.message | string |  |   Total events: 10 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get flows'
Get flows that make up an offense for a particular IP

Type: **investigate**  
Read only: **True**

Use the <b>fields_filter</b> parameter to restrict the flows returned. For e.g. protocolid='6'. For further details refer to the documentation section of the action in the README.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  optional  | IP to get all the flows of | string |  `ip` 
**offense_id** |  optional  | Offense ID to get flows of | numeric |  `qradar offense id` 
**start_time** |  optional  | Start of time range, in epoch time (milliseconds) | numeric | 
**end_time** |  optional  | End of time range, in epoch time (milliseconds) | numeric | 
**count** |  optional  | Number of flows to retrieve | numeric | 
**fields_filter** |  optional  | Filter in AQL format on flow field values | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.count | numeric |  |   100 
action_result.parameter.end_time | numeric |  |   1559905203000 
action_result.parameter.fields_filter | string |  |   sourceip='127.0.0.1' 
action_result.parameter.ip | string |  `ip`  |   122.122.122.122 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   41 
action_result.parameter.start_time | numeric |  |   1559905201000 
action_result.data.\*.Action | string |  |  
action_result.data.\*.Application Determination Algorithm | numeric |  |  
action_result.data.\*.Content Subject | string |  |  
action_result.data.\*.Content Type | string |  |  
action_result.data.\*.FTP Pass | string |  |  
action_result.data.\*.FTP RETR File | string |  |  
action_result.data.\*.FTP User | string |  |  
action_result.data.\*.File Entropy | string |  |  
action_result.data.\*.File Hash | string |  |  
action_result.data.\*.File Name | string |  |  
action_result.data.\*.File Size | string |  |  
action_result.data.\*.Flow Direction Algorithm | numeric |  |  
action_result.data.\*.Google Search Terms | string |  |  
action_result.data.\*.HTTP Content-Type | string |  |  
action_result.data.\*.HTTP GET Request | string |  |  
action_result.data.\*.HTTP Host | string |  |  
action_result.data.\*.HTTP Referer | string |  |  
action_result.data.\*.HTTP Referrer | string |  |  
action_result.data.\*.HTTP Response Code | string |  |  
action_result.data.\*.HTTP Server | string |  |  
action_result.data.\*.HTTP User Agent | string |  |  
action_result.data.\*.HTTP User-Agent | string |  |  
action_result.data.\*.HTTP Version | string |  |  
action_result.data.\*.Originating User | string |  |  
action_result.data.\*.Password | string |  |  
action_result.data.\*.Request URL | string |  |  
action_result.data.\*.SMTP From | string |  |  
action_result.data.\*.SMTP HELO | string |  |  
action_result.data.\*.SMTP Hello | string |  |  
action_result.data.\*.SMTP To | string |  |  
action_result.data.\*.Search Arguments | string |  |  
action_result.data.\*.VLAN Tag | string |  |  
action_result.data.\*.applicationid | numeric |  |   1011 
action_result.data.\*.applicationname_applicationid | string |  |  
action_result.data.\*.category | numeric |  |   18448 
action_result.data.\*.categoryname_category | string |  |  
action_result.data.\*.credibility | numeric |  |   10 
action_result.data.\*.destinationasn | string |  |  
action_result.data.\*.destinationbytes | numeric |  |   11567 
action_result.data.\*.destinationdscp | numeric |  |  
action_result.data.\*.destinationflags | string |  |  
action_result.data.\*.destinationifindex | string |  |  
action_result.data.\*.destinationip | string |  `ip`  |   10.1.16.15 
action_result.data.\*.destinationpackets | numeric |  |   108 
action_result.data.\*.destinationpayload | string |  |  
action_result.data.\*.destinationport | numeric |  `port`  |   3365 
action_result.data.\*.destinationprecedence | numeric |  |  
action_result.data.\*.destinationv6 | string |  |   0:0:0:0:0:0:0:0 
action_result.data.\*.domainid | numeric |  |  
action_result.data.\*.firstpackettime | numeric |  |   1559905202000 
action_result.data.\*.flowbias | string |  |  
action_result.data.\*.flowdirection | string |  |   L2R 
action_result.data.\*.flowid | numeric |  |  
action_result.data.\*.flowinterface | string |  |  
action_result.data.\*.flowinterfaceid | string |  |   5 
action_result.data.\*.flowsource | string |  |  
action_result.data.\*.flowtype | numeric |  |  
action_result.data.\*.fullmatchlist | string |  |  
action_result.data.\*.geographic | string |  |   NorthAmerica.UnitedStates 
action_result.data.\*.hasdestinationpayload | boolean |  |  
action_result.data.\*.hasoffense | boolean |  |   True 
action_result.data.\*.hassourcepayload | boolean |  |   False 
action_result.data.\*.hastlv | boolean |  |  
action_result.data.\*.icmpcode | string |  |  
action_result.data.\*.icmptype | string |  |  
action_result.data.\*.intervalid | numeric |  |   1603463820 
action_result.data.\*.isduplicate | boolean |  |  
action_result.data.\*.lastpackettime | numeric |  |   1559905202999 
action_result.data.\*.partialmatchlist | string |  |  
action_result.data.\*.processorid | numeric |  |   8 
action_result.data.\*.protocolid | numeric |  |  
action_result.data.\*.protocolname_protocolid | string |  |  
action_result.data.\*.qid | numeric |  |   53250087 
action_result.data.\*.qidname_qid | string |  |   Test.Securetest 
action_result.data.\*.relevance | numeric |  |  
action_result.data.\*.retentionbucket | string |  |  
action_result.data.\*.severity | numeric |  |   1 
action_result.data.\*.sourceasn | string |  |  
action_result.data.\*.sourcebytes | numeric |  |   1031681 
action_result.data.\*.sourcedscp | numeric |  |  
action_result.data.\*.sourceflags | string |  |  
action_result.data.\*.sourceifindex | string |  |  
action_result.data.\*.sourceip | string |  `ip`  |   127.0.0.1 
action_result.data.\*.sourcepackets | numeric |  |   783 
action_result.data.\*.sourcepayload | string |  |  
action_result.data.\*.sourceport | numeric |  |   4806 
action_result.data.\*.sourceprecedence | numeric |  |  
action_result.data.\*.sourcev6 | string |  `ipv6`  |   0:0:0:0:0:0:0:0 
action_result.data.\*.starttime | numeric |  |   1559905201000 
action_result.data.\*.viewobjectpair | string |  |  
action_result.summary.total_flows | numeric |  |   33 
action_result.message | string |  |   Total flows: 33 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'offense details'
Get details about an offense

Type: **investigate**  
Read only: **True**

If the <b>ingest_offense</b> parameter is checked, then, it will ingest the events within the last N days (N - value in the <b>interval_days</b> parameter if given or value in the <b>interval_days</b> parameter in the app config or default 5 days) for the offense mentioned in the <b>offense_id</b> parameter. If the <b>ingest_offense</b> parameter is unchecked, it will fetch only the details of the provided offense ID in the <b>offense_id</b> parameter. The parameter <b>tenant_id</b> is used only when the <b>ingest_offense</b> parameter is checked.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** |  required  | Offense ID to get the details of | numeric |  `qradar offense id` 
**tenant_id** |  optional  | Tenant ID for saving container | numeric | 
**ingest_offense** |  optional  | Ingest offense into Phantom | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.ingest_offense | boolean |  |   True  False 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   43 
action_result.parameter.tenant_id | numeric |  |   123 
action_result.data.\*.assigned_to | string |  |   admin 
action_result.data.\*.categories | string |  |   Error 
action_result.data.\*.category_count | numeric |  |   4 
action_result.data.\*.close_time | string |  |   1602888300000 
action_result.data.\*.closing_reason_id | string |  `qradar offense closing reason id`  |   3 
action_result.data.\*.closing_user | string |  |   root 
action_result.data.\*.credibility | numeric |  |   4 
action_result.data.\*.description | string |  |   Anomaly: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks
 
action_result.data.\*.destination_networks | string |  |   other 
action_result.data.\*.device_count | numeric |  |   3 
action_result.data.\*.domain_id | numeric |  |  
action_result.data.\*.event_count | numeric |  |   1035 
action_result.data.\*.flow_count | numeric |  |   0 
action_result.data.\*.follow_up | boolean |  |   False  True 
action_result.data.\*.id | numeric |  `qradar offense id`  |   43 
action_result.data.\*.inactive | boolean |  |   False  True 
action_result.data.\*.last_updated_time | numeric |  |   1559125383270 
action_result.data.\*.local_destination_count | numeric |  |   0 
action_result.data.\*.magnitude | numeric |  |   4 
action_result.data.\*.offense_source | string |  `ip`  |   122.122.122.122 
action_result.data.\*.offense_type | numeric |  |   0 
action_result.data.\*.policy_category_count | numeric |  |   0 
action_result.data.\*.protected | boolean |  |   False  True 
action_result.data.\*.relevance | numeric |  |   2 
action_result.data.\*.remote_destination_count | numeric |  |   1 
action_result.data.\*.rules.\*.id | numeric |  |  
action_result.data.\*.rules.\*.type | string |  |  
action_result.data.\*.security_category_count | numeric |  |   4 
action_result.data.\*.severity | numeric |  |   7 
action_result.data.\*.source_count | numeric |  |   1 
action_result.data.\*.source_network | string |  |   other 
action_result.data.\*.start_time | numeric |  |   1558008289506 
action_result.data.\*.status | string |  |   OPEN 
action_result.data.\*.username_count | numeric |  `user name`  |   0 
action_result.summary.flow_count | numeric |  |   0 
action_result.summary.name | string |  |   Anomaly: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks 
action_result.summary.source | string |  `ip`  |   122.122.122.122 
action_result.summary.start_time | string |  |   2019-04-04 21:28:47 UTC 
action_result.summary.status | string |  |   OPEN 
action_result.summary.total_offenses | numeric |  |   1 
action_result.summary.update_time | string |  |   2019-05-14 10:23:03 UTC 
action_result.message | string |  |   Total offenses: 1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'alt manage ingestion'
Manage ingestion details

Type: **generic**  
Read only: **False**

The general structure of the state file is {"app_version":"app_version", "last_saved_ingest_time":"epoch_time_last_fetched_offense", "last_ingested_events_data":{"offense_id":"epoch_time_last_fetched_event_for_offense_id"}}. <ul><li>There is no validation for values provided in the <b>offense_id</b> action parameter because this action does not make any API calls to the QRadar instance and it merely provides a way of manipulating the state file. It is requested to please confirm if the offense ID being provided as an input exists on the QRadar instance. Any wrong value provided in the <b>offense_id</b> parameter may corrupt the state file and the functionalities dependent on it.</li><li>No comma-separated values should be provided in any of the action input parameters or else it may corrupt the state file and the functionalities dependent on it.</li><li>The <b>set last saved offense ingest time</b> operation sets the epoch time of the provided value in the <b>datetime</b> parameter against the <b>last_saved_ingest_time</b> key in the state file.</li><li>The <b>set last saved events ingest time</b> operation sets the epoch time of the provided value in the <b>datetime</b> parameter against the key corresponding to the offense ID value provided in the <b>offense_id</b> in the dictionary structure against the key <b>last_ingested_events_data</b> in the state file. The format for the date string should match the formats 'YYYY-MM-DD HH:MM:SS.Z', 'YYYY-MM-DDTHH:MM:SS.Z', 'YYYY-MM-DD', or 'HH:MM:SS.Z'. Users can provide only date (time will be 00:00:00.000000) or only time (current date will be considered by default). The action considers that the provided value in the <b>datestring</b> parameter represents the date string in the timezone selected in the asset configuration parameter <b>timezone</b> and accordingly stores the epoch time into the state file.</li><li>The <b>delete last saved ingestion time data</b> operation deletes the entire last saved ingestion time data stored in the state file.</li><li>The <b>get last saved ingestion time data</b> operation fetches the entire last saved ingestion time data stored in the state file.</li><li>The parameter <b>offense_id</b> does not support comma-separated values. The user has to provide a single non-zero positive integer value of the corresponding Offense ID.</li><li>The parameter <b>offense_id</b> is mandatory for the operation <b>set last saved events ingest time</b>.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**operation** |  required  | Operation to perform on the ingestion data stored in the state file | string | 
**datetime** |  optional  | Datetime string to be stored against the ingestion data in the state file | string | 
**offense_id** |  optional  | Offense ID against which to store the 'datetime' parameter value | string |  `qradar offense id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.datetime | string |  |   2019-12-09 11:11:11.0001 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   4 
action_result.parameter.operation | string |  |   get last saved ingestion time data 
action_result.data.\*.last_ingested_events_ingest_time | string |  |   Offense ID_1=Fri Nov 29 10:05:25 2019 UTC +0000, Offense ID_3=Fri Nov 29 10:01:24 2019 UTC +0000, Offense ID_2=Fri Nov 29 10:03:18 2019 UTC +0000 
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.1 | numeric |  |   1575021925702 
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.10 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.19 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.20 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.21 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.22 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.23 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.24 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.74 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.75 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.76 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.77 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.78 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.79 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.80 | numeric |  |  
action_result.data.\*.last_ingested_events_ingest_time_as_epoch.82 | numeric |  |  
action_result.data.\*.last_saved_offense_ingest_time | string |  |   Mon Dec 09 11:11:11 2019 UTC +0000 
action_result.data.\*.last_saved_offense_ingest_time_as_epoch | numeric |  |   1575889871000 
action_result.summary.last_ingested_events_ingest_time | string |  |   Offense ID_1=Fri Nov 29 10:05:25 2019 UTC +0000, Offense ID_3=Fri Nov 29 10:01:24 2019 UTC +0000, Offense ID_2=Fri Nov 29 10:03:18 2019 UTC +0000 
action_result.summary.last_saved_offense_ingest_time | string |  |   Mon Dec 09 11:11:11 2019 UTC +0000 
action_result.message | string |  |   Last saved offense ingest time: Mon Dec 09 11:11:11 2019 UTC +0000, Last ingested events ingest time: Offense ID_1=Fri Nov 29 10:05:25 2019 UTC +0000, Offense ID_3=Fri Nov 29 10:01:24 2019 UTC +0000, Offense ID_2=Fri Nov 29 10:03:18 2019 UTC +0000 
summary.total_objects | numeric |  |   2 
summary.total_objects_successful | numeric |  |   2   

## action: 'run query'
Execute an ariel query on the QRadar device

Type: **investigate**  
Read only: **True**

Use this action to execute queries using AQL on the QRadar device. AQL is a well documented (on the IBM website) query language with quite a few built-in functions.<br>Do note that this action could have a dynamic set of values returned in the data array since the query can specify the columns to return. This is the main reason for not listing the data paths.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**query** |  required  | Ariel Query | string |  `qradar ariel query` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.query | string |  `qradar ariel query`  |   select qid from events 
action_result.data.\*.events.\*.AccountDomain | string |  |  
action_result.data.\*.events.\*.Application | string |  |  
action_result.data.\*.events.\*.Bytes | string |  |  
action_result.data.\*.events.\*.BytesReceived | string |  |  
action_result.data.\*.events.\*.BytesSent | string |  |  
action_result.data.\*.events.\*.Destination Host Name | string |  |  
action_result.data.\*.events.\*.EventID | string |  |  
action_result.data.\*.events.\*.File Hash | string |  |  
action_result.data.\*.events.\*.File ID | string |  |  
action_result.data.\*.events.\*.File Path | string |  |  
action_result.data.\*.events.\*.Filename | string |  |  
action_result.data.\*.events.\*.Installer Filename | string |  |  
action_result.data.\*.events.\*.Message | string |  |  
action_result.data.\*.events.\*.Payload | string |  |  
action_result.data.\*.events.\*.Source Host Name | string |  |  
action_result.data.\*.events.\*.category | numeric |  |   38750003 
action_result.data.\*.events.\*.categoryname_category | string |  |  
action_result.data.\*.events.\*.destinationaddress | string |  |  
action_result.data.\*.events.\*.destinationip | string |  `ip`  |   122.122.122.122 
action_result.data.\*.events.\*.destinationmac | string |  |  
action_result.data.\*.events.\*.destinationport | numeric |  |   0 
action_result.data.\*.events.\*.endtime | numeric |  |  
action_result.data.\*.events.\*.eventcount | numeric |  |   1 
action_result.data.\*.events.\*.eventdirection | string |  |  
action_result.data.\*.events.\*.hostname_logsourceid | string |  |  
action_result.data.\*.events.\*.identityip | string |  `ip`  |   122.122.122.122 
action_result.data.\*.events.\*.logsourcegroupname_logsourceid | string |  |  
action_result.data.\*.events.\*.logsourceid | numeric |  |   65 
action_result.data.\*.events.\*.logsourcename_logsourceid | string |  |  
action_result.data.\*.events.\*.magnitude | numeric |  |   5 
action_result.data.\*.events.\*.protocolid | numeric |  |   255 
action_result.data.\*.events.\*.protocolname_protocolid | string |  |  
action_result.data.\*.events.\*.qid | numeric |  |   38750003 
action_result.data.\*.events.\*.qidname_qid | string |  |  
action_result.data.\*.events.\*.queid | numeric |  |  
action_result.data.\*.events.\*.relevance | numeric |  |  
action_result.data.\*.events.\*.severity | numeric |  |  
action_result.data.\*.events.\*.sourceaddress | string |  |  
action_result.data.\*.events.\*.sourceip | string |  `ip`  |   122.122.122.122 
action_result.data.\*.events.\*.sourcemac | string |  |  
action_result.data.\*.events.\*.sourceport | numeric |  |   0 
action_result.data.\*.events.\*.starttime | numeric |  |   1559907060001 
action_result.data.\*.events.\*.username | string |  `user name`  |  
action_result.data.\*.flows.\*.category | numeric |  |  
action_result.data.\*.flows.\*.destinationbytes | numeric |  |  
action_result.data.\*.flows.\*.destinationflags | string |  |  
action_result.data.\*.flows.\*.destinationip | string |  |  
action_result.data.\*.flows.\*.destinationpackets | numeric |  |  
action_result.data.\*.flows.\*.firstpackettime | numeric |  |  
action_result.data.\*.flows.\*.flowtype | numeric |  |  
action_result.data.\*.flows.\*.lastpackettime | numeric |  |  
action_result.data.\*.flows.\*.protocolid | numeric |  |  
action_result.data.\*.flows.\*.qid | numeric |  |  
action_result.data.\*.flows.\*.sourcebytes | numeric |  |  
action_result.data.\*.flows.\*.sourceflags | string |  |  
action_result.data.\*.flows.\*.sourceip | string |  |  
action_result.data.\*.flows.\*.sourcepackets | numeric |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully ran query 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'add listitem'
Add an item to a reference set in QRadar

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**reference_set_name** |  required  | Name of reference set to add to | string | 
**reference_set_value** |  required  | Value to add to the reference set | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.reference_set_name | string |  |   Demo 
action_result.parameter.reference_set_value | string |  |   122.122.122.122 
action_result.data.\*.creation_time | numeric |  |   1558518483009 
action_result.data.\*.element_type | string |  |   IP 
action_result.data.\*.name | string |  |   Demo 
action_result.data.\*.number_of_elements | numeric |  |   3 
action_result.data.\*.timeout_type | string |  |   FIRST_SEEN 
action_result.summary.element_type | string |  |   IP 
action_result.summary.name | string |  |   Demo 
action_result.summary.number_of_elements | numeric |  |   3 
action_result.message | string |  |   Element type: IP, Name: Demo, Number of elements: 3 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'close offense'
Close an active offense, marking status=CLOSED

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** |  required  | Offense ID to close | numeric |  `qradar offense id` 
**closing_reason_id** |  required  | Reason for closing offense | numeric |  `qradar offense closing reason id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.closing_reason_id | numeric |  `qradar offense closing reason id`  |   1 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   41 
action_result.data.\*.assigned_to | string |  |   admin 
action_result.data.\*.categories | string |  |   Error 
action_result.data.\*.category_count | numeric |  |   4 
action_result.data.\*.close_time | numeric |  |   1559905203000 
action_result.data.\*.closing_reason_id | numeric |  `qradar offense closing reason id`  |   1 
action_result.data.\*.closing_user | string |  |   API_token: Phantom 
action_result.data.\*.credibility | numeric |  |   4 
action_result.data.\*.description | string |  |   Anomaly: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks
 
action_result.data.\*.destination_networks | string |  |   other 
action_result.data.\*.device_count | numeric |  |   3 
action_result.data.\*.domain_id | numeric |  |  
action_result.data.\*.event_count | numeric |  |   2660 
action_result.data.\*.flow_count | numeric |  |   0 
action_result.data.\*.follow_up | boolean |  |   False  True 
action_result.data.\*.id | numeric |  `qradar offense id`  |   41 
action_result.data.\*.inactive | boolean |  |   False  True 
action_result.data.\*.last_updated_time | numeric |  |   1557829383413 
action_result.data.\*.local_destination_count | numeric |  |   0 
action_result.data.\*.magnitude | numeric |  |   3 
action_result.data.\*.offense_source | string |  `ip`  |   122.122.122.122 
action_result.data.\*.offense_type | numeric |  |   0 
action_result.data.\*.policy_category_count | numeric |  |   0 
action_result.data.\*.protected | boolean |  |   False  True 
action_result.data.\*.relevance | numeric |  |   2 
action_result.data.\*.remote_destination_count | numeric |  |   1 
action_result.data.\*.rules.\*.id | numeric |  |  
action_result.data.\*.rules.\*.type | string |  |  
action_result.data.\*.security_category_count | numeric |  |   4 
action_result.data.\*.severity | numeric |  |   7 
action_result.data.\*.source_count | numeric |  |   1 
action_result.data.\*.source_network | string |  |   other 
action_result.data.\*.start_time | numeric |  |   1554413327061 
action_result.data.\*.status | string |  |   CLOSED 
action_result.data.\*.username_count | numeric |  `user name`  |   0 
action_result.summary.flow_count | numeric |  |   0 
action_result.summary.name | string |  |   Anomaly: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks 
action_result.summary.source | string |  `ip`  |   122.122.122.122 
action_result.summary.start_time | string |  |   2019-04-04 21:28:47 UTC 
action_result.summary.status | string |  |   CLOSED 
action_result.summary.update_time | string |  |   2019-05-14 10:23:03 UTC 
action_result.message | string |  |   Status: CLOSED, Source: 122.122.122.122, Update time: 2019-05-14 10:23:03 UTC, Name: Anomaly: Access to Test or Test Defined Address
 preceded by Communication with Known Watched Networks, Flow count: 0, Start time: 2019-04-04 21:28:47 UTC 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'update offense'
Attach a note to an offense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** |  required  | Offense ID to attach note to | numeric |  `qradar offense id` 
**note_text** |  required  | Text to put into note | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.note_text | string |  |   Note Added By Phantom 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   41 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully added note to offense 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'assign user'
Assign the user to an offense

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** |  required  | Offense ID to assign the user to | numeric |  `qradar offense id` 
**assignee** |  required  | Name of the user | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.assignee | string |  |   admin 
action_result.parameter.offense_id | numeric |  `qradar offense id`  |   41 
action_result.data | string |  |  
action_result.summary | string |  |  
action_result.message | string |  |   Successfully assigned user to offense 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get rule info'
Retrieve QRadar rule information

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**rule_id** |  required  | Rule ID for which information needs to be extracted | numeric |  `qradar rule id` 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string |  |   success  failed 
action_result.parameter.rule_id | numeric |  `qradar rule id`  |   1421 
action_result.data.\*.average_capacity | numeric |  |   3541750 
action_result.data.\*.base_capacity | numeric |  |   3541750 
action_result.data.\*.base_host_id | numeric |  |   384 
action_result.data.\*.capacity_timestamp | numeric |  |   1566896735557 
action_result.data.\*.creation_date | numeric |  |   1155662266056 
action_result.data.\*.enabled | boolean |  |   True  False 
action_result.data.\*.id | numeric |  |   1421 
action_result.data.\*.identifier | string |  |   SYSTEM-1421 
action_result.data.\*.linked_rule_identifier | string |  |  
action_result.data.\*.modification_date | numeric |  |   1267729985038 
action_result.data.\*.name | string |  |   User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories 
action_result.data.\*.origin | string |  |   SYSTEM 
action_result.data.\*.owner | string |  |   admin 
action_result.data.\*.type | string |  |   EVENT 
action_result.summary.id | numeric |  |   1421 
action_result.summary.name | string |  |   User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories 
action_result.message | string |  |   Id: 1421, Name: User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

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
action_result.status | string |  |   success  failed 
action_result.parameter.count | numeric |  |   31 
action_result.data.\*.average_capacity | numeric |  |   3541750 
action_result.data.\*.base_capacity | numeric |  |   3541750 
action_result.data.\*.base_host_id | numeric |  |   384 
action_result.data.\*.capacity_timestamp | numeric |  |   1566896735557 
action_result.data.\*.creation_date | numeric |  |   1155662266056 
action_result.data.\*.enabled | boolean |  |   True  False 
action_result.data.\*.id | numeric |  `qradar rule id`  |   1421 
action_result.data.\*.identifier | string |  |   SYSTEM-1421 
action_result.data.\*.linked_rule_identifier | string |  |  
action_result.data.\*.modification_date | numeric |  |   1267729985038 
action_result.data.\*.name | string |  |   User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories 
action_result.data.\*.origin | string |  |   SYSTEM 
action_result.data.\*.owner | string |  |   admin 
action_result.data.\*.type | string |  |   EVENT 
action_result.summary.total_rules | numeric |  |   135 
action_result.message | string |  |   Total rules: 135 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'on poll'
Callback action for the on_poll ingest functionality

Type: **ingest**  
Read only: **True**

The default start_time is the past 5 days. The default end_time is now.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container_id** |  optional  | Parameter ignored for this app | string | 
**start_time** |  optional  | Start of time range, in epoch time (milliseconds) | numeric | 
**end_time** |  optional  | End of time range, in epoch time (milliseconds) | numeric | 
**container_count** |  optional  | Maximum number of container records to query for | numeric | 
**artifact_count** |  optional  | Parameter ignored for this app | numeric | 

#### Action Output
No Output
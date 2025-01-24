# QRadar

Publisher: Splunk
Connector Version: 2.1.2
Product Vendor: IBM
Product Name: QRadar
Minimum Product Version: 4.9.39220

This app supports generic, investigative, and ingestion actions on an IBM QRadar device

This App is an Ingestion source. In the Phantom documentation, in the [Administration
Manual](../admin/) under the [Data Sources](../admin/sources) section, you will find an explanation
of how Ingest Apps works and how information is extracted from the ingested data. There is a general
explanation in Overview, and some individuals Apps have their sections.

**QRadar Instance Minimum Version Compatibility**

- With this version of the QRadar app on Phantom, we declare support for the QRadar instances
  which are on and above the v7.3.1. This app has been tested and certified on the v7.3.1 version
  of the QRadar.
- The expectations of the actions with this version of the app have not been changed majorly. It
  is recommended to read the documentation for the app and each action first to understand the
  functioning of the actions of all the asset configuration and the action parameters.

**Playbook Backward Compatibility**

- The existing action parameters have been modified in the actions given below. Hence, it is
  requested to the end-user to please update their existing playbooks by re-inserting the
  corresponding action blocks or by providing appropriate values to these action parameters to
  ensure the correct functioning of the playbooks created on the earlier versions of the app.

  - Alt Manage Ingestion - The new drop-down values in the [operation] parameter have been
    added and the existing ones are modified.
  - Get Flows - This action was not working correctly and we have updated the logic for this
    action's functionality.
  - Offense Details - The action parameter for [interval_days] has been removed as it was not
    getting used in the action.

**Explanation of App Settings Parameter**

- **interval_days**
  - For List Offenses and Get Events action if the [start_time] is specified, it will be given
    priority, if not provided, this value is internally derived by subtracting the
    [interval_days] from the [end_time]. For the Get Events action, this field is having a
    higher preference over the [interval_days] action parameter if both are specified. If
    [interval_days] is not specified in the app settings it will take the default value which
    is 5.
  - If [Alternative ariel query] configuration parameter is checked, for On Poll and Get
    Events action to fetch the events, the time based filtering in this workflow is applied
    based on the granularity of days instead of applying it based on the granularity of epoch
    and Datetime formats.
  - For On Poll, to fetch the offenses, if there is time stored in the state file it will be
    given priority, if not provided, this value is internally derived by subtracting the
    [interval_days] from the [end_time]. If [interval_days] is not specified in the app
    settings it will take the default value which is 5.
  - For On Poll, to fetch the events, if there is time stored in the state file it will be given
    priority, if not provided, the [start_time] will be calculated by back-dating offense's
    [start_time] by the value of [events_ingest_start_time] configuration parameter.
  - [interval_days] parameter is not used in the alternative ingestion algorithm.

**Explanation of Asset Configuration Parameters**

- All the asset configuration parameters which are affecting the functioning of the On Poll action
  will also affect the functioning of the action [Offense Details] when the corresponding action
  parameter [ingest_offense] is checked

- **Asset Configuration Parameters**

  - **artifact_max -** Maximum number of event artifacts to ingest for the [On Poll] (both
    manual and scheduled) action and [Offense Details] action with [ingest_offense] action
    parameter set to TRUE. This count excludes the default generated offense artifact.

  - **cef_event_map -** JSON formatted string of key-value pairs for CEF mapping - use
    double-quotes. CEF values are the keys, QRadar fields are the values. QRadar fields are the
    internal names of the fields for the events data exported in the JSON format. These internal
    names can be obtained from the JSON data obtained by running the [Get Events] action. If
    the cef_event_map is provided by the user, the fields mentioned in this mapping and the
    default CEF mapping fields along with the extra fields provided in the \[Event fields to
    include while querying\] configuration parameter will be included in the CEF data of the
    artifact created for ingestion. If the cef_event_map is not provided by the user, then, the
    default event fields along with the extra fields provided in the \[Event fields to include
    while querying\] configuration parameter will be included in the CEF data of the artifacts
    created for ingestion. If the mapping provided in the [CEF event map] configuration field
    consists of the fields which are already covered by the default CEF mapping, then, the
    provided CEF mapping in the configuration parameter will also be created along with the
    default CEF mapping.

    **Sample [CEF Event Map] value**
    `         {"magnitudeValue":"magnitude","customAttributeValue1":"custom_attribute_1","customAttributeValue2":"Custom Attribute 2"}                          `
    **Important Point** - Internally the field UTF8(payload) is fetched by the name of Payload
    (i.e. UTF8(payload) as Payload). Hence, to map the UTF8(payload) field in the CEF event map,
    please provide the mapping as mentioned here {"[cef_name_for_payload_field]": "Payload"}.

    - The default CEF mapping is provided below (left-side is the display name of the event
      fields in the ingested artifacts data and right-side is the original internal name of
      the fields of an event)

      `            {                        "signature_id": "qid",                        "name": "qidname_qid",                        "severity": "severity",                        "applicationProtocol": "Application",                        "destinationMacAddress": "destinationmac",                        "destinationNtDomain": "AccountDomain",                        "destinationPort": "destinationport",                        "destinationAddress": "destinationaddress",                        "endTime": "endtime",                        "fileHash": "File Hash",                        "fileId": "File ID",                        "filePath": "File Path",                        "fileName": "Filename",                        "bytesIn": "BytesReceived",                        "message": "Message",                        "bytesOut": "BytesSent",                        "transportProtocol": "protocolname_protocolid",                        "sourceMacAddress": "sourcemac",                        "sourcePort": "sourceport",                        "sourceAddress": "sourceaddress",                        "startTime": "starttime",                        "payload": "Payload"                        }           `

  - **cef_value_map -** JSON formatted string representation of a dictionary used to map CEF
    field values to new values. Similar to cef_event_map, replace the value of any CEF field
    with another value. For example, to replace the value of cef.requestURL of \\"nourl\\", with
    null value, provide { \\"nourl\\": null }. If the user wants to replace a numeric
    (integer|float) value with some other value, due to the SDK issue, the user has to provide
    the key-value map in this format. e.g. if user wants to replace value 4 with 10 and 5.3 with
    6.7, provide this CEF value mapping {"numeric(4)": 10, "numeric(5.3)": 6.7}
    **Sample [CEF Value Map] values**

    - To replace integer|float values; value 4 with 10 and 5.3 with 6.7, provide below CEF
      value mapping

      `            {"numeric(4)": 10, "numeric(5.3)": 6.7}           `

    - To replace string values; Alert with Alert_Info

      `            {"Alert": "Alert_Info"}           `

  - **delete_empty_cef_fields -** Set true to delete CEF fields with empty values.

  - **event_fields_for_query -** Optionally define a new comma-separated list of fields (system
    or custom or both) for querying. A comma-separated list of field internal names as obtained
    in the JSON data while running the [Get Events] action. Use double-quotes if field names
    contain spaces.

  - **add_offense_id_to_name -** Optionally add the offense ID to the container name. If the
    user runs the On Poll action without this value being checked and then, stops the ingestion
    and again starts the ingestion after checking this parameter (to TRUE), new containers will
    not be created for the offenses which were already ingested and their names will also not be
    changed to have the offense ID prefixed. All the new event artifacts will continue getting
    created in the existing containers. Hence, it is recommended to delete the already ingested
    containers and artifacts if the user is changing the value of this parameter to ensure that
    all the containers and artifacts get created with the new expected names.

  - **alternative_ariel_query -** Alternative ariel query; considers Datetime specifications if
    provided or else retrieve events from the last [interval_days] (default=5) days; affects
    [On Poll], [Offense Details] and [Get Events] actions; [On Poll] will auto-extend
    the number of days to start on/before the day of the offense being retrieved.

  - **alt_initial_ingest_time -** This parameter is applicable only if
    [alternative_ingest_algorithm] parameter is checked. Set the [last_saved_ingest_time] to
    this. This is the initial lower limit to ingest offenses. This field accepts the values
    mentioned here; a string 'yesterday', a valid python parsable Datetime (dateutil module)
    (for the given date-time string, while parsing the date portion, higher preference is given
    to MM-DD-YYYY format and if the date-time string stands invalid in that date format, then,
    than it is considered to have the DD-MM-YYYY date format) or an epoch time in milliseconds;
    if no value is provided, then, the default value is 'yesterday'. Examples - yesterday,
    2020-02-25 12:00:00, 2020-12-01T05:00:00, 2019-04-30, 01-20-2020, 20-01-2020, 06:30:00, etc.

  - **alt_ingest_order -** This parameter is applicable only if [alternative_ingest_algorithm]
    parameter is checked. The parameter alt_ingest_order will decide the order in which the
    offense will be fetched (oldest first or latest first).

  - **alt_time_field -** This parameter is applicable only if [alternative_ingest_algorithm]
    parameter is checked. The parameter alt_time_field will decide the time on which the
    alt_ingest_order will be applied (start_time or last_updated_time or either)

  - **ingest_open -** This parameter is optional and if not set to true, it will fetch all the
    offenses (including the closed offenses). To fetch only open offenses ingest only open must
    be set to TRUE. This configuration parameter is used in List Offenses, Offense Details as
    well as in On Poll action.

  - **alternative_ingest_algorithm -** This parameter is optional and if not set to true then,
    the app will ignore the values kept in the [alt_ingest_order] and [alt_time_field]. If
    the parameter [alternative_ingest_algorithm] is set to true then, the offenses will be
    fetched according to [alt_ingest_order] and [alt_time_field] parameters. This
    configuration parameter is used in the List Offenses, Offense Details as well as in the On
    Poll action.

  - **events_ingest_start_time -** This parameter is optional and the default value is 60. This
    parameter defines the relative number of minutes (in milliseconds) to back-date the
    offense's 'start_time' to start fetching the events for that particular offense. e.g. if
    events_ingest_start_time = 25 and offense's start_time = 1582618635661, then, after
    back-date, the final timestamp from which we will start fetching the events for that
    particular offense is 1582618635661 - (25 * 60 * 1000) = 1582617135661. NOTE - This
    parameter is applicable only for the manual POLL NOW, the first run of the SCHEDULED |
    INTERVAL polling, and other actions like [Offense Details] which are involved in the
    events ingestion.

  - **containers_only -** This parameter is optional and if not set to true then, the offenses
    will be created as containers and the events of the offenses will be created as the
    artifacts. If this parameter is set to true then, the offenses will be created as containers
    and the details of the offenses will be created as the artifacts in those containers
    respectively. This configuration parameter is used in the Offense Details and On Poll
    actions.

  - **has_offense -** This parameter is optional and by default will be checked as true. This
    parameter describes whether the events and flows should be associated with the offense or
    not while fetching the events and flows. If this is set to true, then only the events and
    flows associated with the offense will be considered. This configuration parameter is used
    in the Get Events, Get Flows as well as in the On Poll action. For Get Events and Get Flows
    Action, 'has_offense' will only be considered if the user has passed the 'offense_id' while
    running these actions.

  - **offense_ingest_start_time -** This parameter is optional and the default will be 0. This
    parameter defines the relative number of minutes (in milliseconds) to back-date the
    offense's 'start_time' to start fetching the offenses. e.g. if offense_ingest_start_time =
    25 and the time to start fetching offenses is 1582618635661, then after back-date, the final
    timestamp from which we will start fetching the offenses would be 1582618635661 - (25 * 60
    \* 1000) = 1582617135661. This parameter is applicable for each type of polling.

  - **event_ingest_end_time -** This parameter is optional and the default will be 0. This
    parameter defines the relative number of minutes (in milliseconds) to modify the event
    ingestion 'end_time' by after-dating event ingestion 'start_time'. The 'start_time' will be
    [offense's start_time - events_ingest_start_time] for manual polling and the first run of
    scheduled | interval polling and for the next runs, it will take time stored in the state
    file against last_ingested_events_data for a particular offense. e.g. if
    event_ingest_end_time = 25 and the 'start_time' to fetch events is 1582618635661, then after
    modification, the final 'end_time' to stop fetching events would be 1582618635661 + (25 \*
    60 * 1000) = 1582620135661. If the modified 'end_time' exceeds the current time then it
    will consider the current time as 'end_time'. This parameter is applicable for each type of
    polling.

  - **max_events_per_offense -** This parameter is optional and the default will be None. This
    parameter defines the maximum accumulated artifacts to be ingested per offense, including
    the default generated offense artifact. e.g. if max_events_per_offense = 100, then maximum
    artifacts to be ingested in each container should not be greater than 100, considering all
    polling cycles. 'artifact_max' parameter can affect the functionality of the
    'max_events_per_offense' parameter based on its value as mentioned below.

    - If artifact_max is less than max_events_per_offense, then it will ingest artifact_max
      number of artifacts per cycle and once the total artifacts count in a container equals
      or exceeds the max_events_per_offense count it will not collect artifacts. e.g. If
      artifact_max = 20 and max_events_per_offense = 30, then in first polling cycle it will
      ingest 21 artifacts (one default generated offense artifact). In the next polling cycle,
      it will ingest 9 more artifacts. As the total artifacts in the container get equal to
      the max_events_per_offense it will not collect artifacts from the next cycle.
    - If max_events_per_offense is less than artifact_max, then it will ingest
      max_events_per_offense number of artifacts. e.g. if max_events_per_offense = 10 and
      artifact_max = 15, then it will ingest 10 artifacts.
    - If max_events_per_offense = 1, then irrespective of any value provided in
      'artifact_max', it will ingest only one artifact (default generated offense artifact).
    - NOTE - If offense will get updated while Qradar event creation, accordingly offense
      artifacts will also be ingested in phantom with updated parameters. This can affect the
      functionality of max_events_per_offense. e.g. if artifact_max = 5 and
      max_events_per_offense = 8, then in first cycle it will ingest 6 artifacts (one default
      generated offense artifact). In the next polling cycle, it will ingest 2 more event
      artifacts but if the offense is updated then it will also ingest one more offense
      artifact and the total artifact count will be one more than max_events_per_offense.

**Explanation of QRadar Actions' Parameters**

- **Test Connectivity (Authentication Details)**

  - This action provides 2 modes of providing the authentication: Basic Auth and Auth Token.
  - It expects the user to enter either a valid auth token or a valid pair of username and
    password both.
  - If none of the 3 configuration parameters for [Username], [Password], and \[Auth Token
    for QRadar REST API calls\] is provided, the action fails with an appropriate error.
  - If the user provides both the auth token and the pair of username and password, then, the
    [Test Connectivity] action will validate both the modes of authentication and will throw
    an appropriate error if any credentials are invalid.
  - If the user provides the auth token and any one of the username and password, the
    connectivity will fail and will throw an error to provide either both the username and
    password or none of them as in this case the auth token already exists and has a higher
    preference than the username and password. If the auth token is not provided, then, the user
    must provide both the username and password.
  - The connectivity gives a higher preference to the auth token than that using the pair of
    username and password.

- **List Offenses**

  - Default Offenses Ingestion Workflow

    - The offenses are fetched based on the logic that either their [start_time] or their
      [last_updated_time] is between the time range defined by [start_time] and
      [end_time].
    - **Start Time -** This field expects an epoch value in milliseconds. If not provided,
      this value is internally derived by subtracting the [interval_days] from the
      [end_time]. This field is having a higher preference over the [interval_days] action
      parameter if both are specified.
    - **End Time -** This field expects an epoch value in milliseconds. If not provided, this
      value is equal to the current epoch value in milliseconds.
    - **Count -** This field expects a valid non-zero integer value or empty value. If
      provided, offenses equal to the provided value are fetched. If left empty, the default
      100 offenses matching the filter criteria are fetched. If the user wants to fetch all
      the offenses, provide a value greater than the total offenses that exist on the QRadar
      server.
    - **Offense ID -** This field expects a comma-separated string containing valid offense
      IDs. If this is provided, irrespective of the start_time or end_time, the offenses
      corresponding to all the offense IDs provided here will be fetched based on the value
      provided in the [count] parameter.

  - Alternate Offenses Ingestion Workflow

    - This workflow has the functionalities similar to the default ingestion workflow with the
      below-mentioned points getting considered while ingestion.
    - This workflow considers the value stored against the key [last_saved_ingest_time] in
      the state file (only for On Poll and Ingest Offense action with ingest_offense set to
      TRUE) as the start time to fetch the offenses. If the key is not found in the state
      file, it considers the value mentioned in the [Alternative initial ingestion time]
      asset configuration parameter as the start time to fetch the offenses. If none of the
      above-mentioned values are found, it considers the default value as yesterday. It does
      not consider the [interval_days] parameter mentioned in the [app_config] settings.
    - This workflow is considered only if the [Alternative ingest algorithm for offenses]
      configuration parameter is checked.
    - The configuration parameters [Alternative ingestion time field] and \[Alternative
      ingestion order for offenses\] are applicable for this workflow only if the
      [Alternative ingest algorithm for offenses] config parameter is checked.
    - This workflow provides a provision to fetch the offenses in the [latest first] and the
      [oldest first] order.
    - This workflow provides a provision to fetch the offenses in the sorted order based on
      the QRadar offense time fields [starttime] and [last_updated_time]. Based on the
      above-mentioned time field selected, the offenses whose time field fall in the time
      range (inclusive of boundaries) defined by [start_time] and [end_time] action
      parameters are fetched. If the time field selected is [either], then, the offenses
      whose either [starttime] or [last_updated_time] falls in the time range (inclusive
      of boundaries) defined by [start_time] and [end_time] action parameters are fetched.
      For the time field [either], for the On Poll actions (scheduled | interval polling)
      the maximum of the [starttime] or [last_updated_time] for the last fetched offense
      is stored in the state file against the key [last_saved_ingest_time].

- **Get Events**

  - Default Ariel Query Events Ingestion Workflow

    - The events are fetched in the descending order of the values in the [starttime] field.
    - **Start Time -** This field expects an epoch value in milliseconds. If not provided,
      this value is internally derived by subtracting the [interval_days] from the
      [end_time]. This field is having a higher preference over the [interval_days] action
      parameter if both are specified.
    - **End Time -** This field expects an epoch value in milliseconds. If not provided, this
      value is equal to the current epoch value in milliseconds.
    - **Count -** This field expects a valid non-zero integer value or empty value. If
      provided, events equal to the provided value are fetched. If left empty, default 100
      events matching the filter criteria are fetched. If the user wants to fetch all the
      events, provide a value greater than the total events that exist on the QRadar server.
    - **Interval Days -** This field expects a valid non-zero integer value or empty value. If
      provided, events within the last n days (n is equal to the value provided in
      [interval_days] parameter) are fetched. If left empty, the value provided in the \[App
      Config Settings\] is considered in the [interval_days] parameter. If \[App Config
      Settings\] is also left empty, the default value of 5 days is considered in the
      [interval_days] parameter.
    - **Fields Filter -** This field expects a filter string in the valid AQL query syntax.
    - **Offense ID -** This field expects a unique offense ID to fetch the events for.

  - Alternate Ariel Query Events Ingestion Workflow

    - This workflow has the functionalities similar to the default ingestion workflow with the
      below-mentioned points getting considered while ingestion.
    - This workflow is considered only if the [Alternative ariel query] configuration
      parameter is checked.
    - The configuration parameter [Alternative initial ingestion time] is applicable for
      this workflow only if the [Alternative ariel query] config parameter is checked.
    - This workflow performs the same functionality as the default ingestion workflow, but
      with a different form of the Ariel query. The time based filtering in this workflow is
      applied based on the granularity of days instead of applying it based on the granularity
      of epoch and Datetime formats.
    - As the time based filtering in this workflow is applied based on the granularity of
      days, back-dating event fetching 'start_time' and after-dating event fetching 'end_time'
      does not work with this workflow.

- **Offense Details**

  - Default Offenses Ingestion Workflow

    - This action will behave similarly to a manual On Poll action run if the
      [ingest_offense] flag is checked and it will ingest all the events as artifacts for
      the provided offense ID.

    - **Tenant ID -** This field expects a valid tenant ID of the Phantom server for saving
      the container. If multi-tenancy is not enabled, then the events will be ingested with
      the default tenant. But if multi-tenancy is enabled and this field is left blank and no
      tenant is mapped with the asset then containers will not be created.

      - **To enable Multi-Tenancy**

        - Go to the Administration section and under Product settings, select
          Multi-tenancy and enable it.

      - **To map a tenant with asset**

        - After enabling Multi-tenancy, go to asset configurations, and select the Tenants
          tab. From the available list of tenants, select the tenant to map with the
          asset.

    - **Offense ID -** This field expects a unique offense ID whose details are to be fetched.
      If the value is provided, it will fetch the data for that offense ID irrespective of
      whether it falls in the range of days specified in the [interval_days] parameter of
      the app settings.

    - **Ingest Offense -** This flag if checked, the action ingests all the offense and events
      details. The parameters [interval_days] and [tenant_id] will be accounted for if the
      [ingest_offense] parameter is checked.

  - Alternate Offenses Ingestion Workflow

    - This workflow is considered only if the [Alternative ingest algorithm for offenses]
      configuration parameter is checked.
    - The behavior of this alternate workflow is the same as described in the alternate
      workflow section of the [List Offenses] action.

  - Alternate Ariel Query Events Ingestion Workflow

    - This workflow is considered only if the [Alternative ariel query] configuration
      parameter is checked.
    - The behavior of this alternate workflow is the same as described in the alternate
      workflow section of the [Get Events] action.

- **Get Flows**

  - **Start Time -** This field expects an epoch value in milliseconds. If not provided, this
    value is internally derived by subtracting the [interval_days] from the [end_time].
  - **End Time -** This field expects an epoch value in milliseconds. If not provided, this
    value is equal to the current epoch value in milliseconds.
  - **Count -** This field expects a valid non-zero integer value or empty value. If provided,
    flows equal to the provided value are fetched. If left empty, default 100 flows matching the
    filter criteria are fetched. If the user wants to fetch all the flows, provide a value
    greater than the total flows that exist on the QRadar server.
  - **IP -** IP to match against [Source Destination IP] and [Target Destination IP] for
    fetching all the flows.
  - **Fields Filter -** This field expects a filter string in the valid AQL query syntax.
  - **Offense ID -** This field expects a unique offense ID to fetch the flows for.

- **Alt Manage Ingestion**

  - This action provides a provision to alter the state file associated with the corresponding
    asset. For more details, please refer to the specific documentation for this action.
  - This action does not make any REST call to the QRadar instance. It simply fetches or
    manipulates the state file of the Phantom server for the corresponding asset.
  - Please change the state file with great care because if the standard format of the state
    file goes wrong, then, all the actions which are dependent on the state file e.g. On Poll,
    Offense Details with [ingest_offense] value True will start working incorrectly

- **On Poll**

  - The On Poll action works in 2 steps. In the first step, all the offenses in a defined time
    duration will be fetched. In the second step, all the events of the offenses (retrieved in
    the first step) will be fetched. A container will be created for each offense and for each
    offense all the events will be fetched as the respective artifacts.

  - The list of offenses will be fetched based on the asset configuration and the app
    configuration parameters configured with the asset. The first step simply calls \[List
    Offenses\] action. Based on the value of the flag \[Alternative ingest algorithm for
    offenses\], the offenses will be fetched either by the default ingestion workflow or by the
    alternative ingestion workflow.

  - The list of events will be fetched for each offense fetched in the earlier step based on the
    asset configuration and the app configuration parameters configured with the asset. This
    step simply calls [Get Events] action. Based on the value of the flag \[Alternative ariel
    query\], the offenses will be fetched either by the default ingestion workflow or by the
    alternative ingestion workflow. For manual polling and the first run of the scheduled |
    interval polling, the list of events for every offense will be fetched starting from the
    default time of 3600000 epoch milliseconds (1 hour past the 0 epoch) because if we start
    fetching it from 0 epoch, then, the QRadar API throws an error mentioning "Response Code:
    422 and Response Message: The request was well-formed but was unable to be followed due to
    semantic errors. Invalid query parameters: Start time(70-01-01,06:29:59) should be greater
    than one hour since the epoch.". NOTE - If the user's QRadar instance is in America/Los
    Angeles (-08:00 hrs) timezone and for the [QRadar timezone] asset configuration parameter,
    the user selects a timezone which is having an offset of \[-08:00 hrs (QRadar instance's
    timezone) + 1 = -07:00 hrs\] or greater, then, the date-time string that gets generated in
    the ariel query will represent a time which is earlier than the allowed time by the QRadar
    ariel query APIs (allowed time is 1 hour past the 0 epoch) for the configured timezone on
    the QRadar instance and it will throw the above-mentioned error. Hence, it is recommended
    that the end-user selects the same timezone in the asset as that configured in the QRadar
    instance to avoid any timezone related issues.

  - The general structure of the state file : {"app_version":"app_version",
    "last_saved_ingest_time":"epoch_time_last_fetched_offense",
    "last_ingested_events_data":{"offense_id":"epoch_time_last_fetched_event_for_offense_id"}}

  - **Two approaches for On Poll**

    - Manual polling

      - Manual polling fetches all the data every time based on the asset and app
        configurations. It is recommended to keep a very high value in [container_count]
        and [artifact_max] parameters to ensure all the required data gets ingested to
        avoid any data loss.

      - Fetch the offenses

        - The application will fetch the number of offenses controlled by the
          [container_count] parameter in [On Poll] action.
        - The application will fetch all the offenses governed by the behavior of the
          [List Offenses] action.
        - The state file is neither considered nor modified by the manual polling.

      - Fetch the events

        - This step will be executed only if the [containers_only] configuration
          parameter is not checked.
        - The application will fetch all events for each offense (retrieved in the
          previous step) controlled by the [artifact_max] configuration parameter and
          governed by the behavior of the [Get Events] action.

    - Scheduled polling

      - Scheduled polling fetches all the data every time (for the first run only) based on
        the asset and app configurations. It is recommended to keep a very high value in
        [container_count] and [artifact_max] parameters to ensure all the required data
        gets ingested (in the first run itself and gets in sync with the QRadar current
        state) and avoids any data loss.

      - It is recommended to keep scheduled polling interval of more than 30 minutes or an
        hour (for the first time so that all the initial offenses and events data get
        ingested quickly and correctly) if the number of events to be ingested is large in
        number (e.g. > 50,000 events collectively to be ingested for all offenses). The
        reason for doing this is due to the Phantom core's inherent behavior of killing the
        previous scheduled poll or interval poll run if it does not get completed within a
        definite time which is x times (x is internally defined specific to the Phantom
        server) multiple of the current polling interval. e.g. If there are 10 offenses with
        each offense having 5000 events (total 50,000 events), configure the scheduled
        polling for 30 minutes or an hour or more and wait until all the initial data gets
        ingested. Once it is completed, change the polling interval to the required time and
        then, the scheduled polling will work correctly, keeping the Phantom ingested data
        in sync with the QRadar data.

      - For the consecutive runs, the offenses are fetched starting from the epoch value in
        milliseconds stored in the [last_saved_ingest_time] key of the state file.

      - Fetch the offenses

        - The application will fetch all the offenses governed by the behavior of the
          [List Offenses] action.
        - The [starttime] or the [last_updated_time] of the last offense fetched is
          stored in the state file against the key [last_saved_ingest_time] based on the
          default or alternate ingestion workflow and the value selected in the
          [Alternative ingestion time field] configuration parameter. If the value
          selected in the [Alternative ingestion time field] configuration parameter is
          [either], then, the maximum of the [starttime] or the [last_updated_time]
          for the last fetched offense is stored in the state file.

      - Fetch the events

        - This step will be executed only if the [containers_only] configuration
          parameter is not checked.
        - The application will fetch all events for each offense (retrieved in the
          previous step) controlled by the [artifact_max] configuration parameter and
          governed by the behavior of the [Get Events] action.

**General Notes**

- Case-sensitive

  - For Assign User, Add Listitem

    - Parameters [reference_set_name] for 'add listitem' and [assignee] for 'assign user'
      are case sensitive.

### Configuration variables

This table lists the configuration variables required to operate QRadar. These variables are specified when configuring a QRadar asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device** | required | string | Server IP/Hostname
**containers_only** | optional | boolean | Ingest only offenses while polling
**has_offense** | optional | boolean | Fetch only events and flows associated with the offense
**verify_server_cert** | optional | boolean | Verify server certificate
**username** | optional | string | Username
**password** | optional | password | Password
**authorization_token** | optional | password | Auth Token for QRadar REST API calls
**timezone** | required | timezone | QRadar timezone
**add_to_resolved** | optional | boolean | Ingest artifacts into closed/resolved containers
**artifact_max** | optional | numeric | Maximum event artifacts count per cycle (excluding the default generated offense artifact)
**ingest_resolved** | optional | boolean | Ingest only open offenses
**cef_event_map** | optional | string | CEF event map
**cef_value_map** | optional | string | CEF value map
**delete_empty_cef_fields** | optional | boolean | Delete the empty CEF fields
**event_fields_for_query** | optional | string | Event fields to include while querying
**add_offense_id_to_name** | optional | boolean | Add offense ID to name of containers
**alternative_ariel_query** | optional | boolean | Alternative ariel query
**alternative_ingest_algorithm** | optional | boolean | Alternative ingest algorithm for offenses
**alt_time_field** | optional | string | Alternative ingestion time field
**alt_initial_ingest_time** | optional | string | Alternative initial ingestion time
**alt_ingestion_order** | optional | string | Alternative ingestion order for offenses
**events_ingest_start_time** | optional | numeric | Events ingestion initial time (relative to offense start time, default is 60 min)
**offense_ingest_start_time** | optional | numeric | Offense ingestion initial time (relative to offense start time, default is 0 min)
**event_ingest_end_time** | optional | numeric | Events ingestion end time (relative to event ingestion start time, default is 0 min)
**max_events_per_offense** | optional | numeric | Maximum accumulated artifacts count per offense (including the default generated offense artifact)

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
**start_time** | optional | Start of time range, in epoch time (milliseconds) | numeric | **end_time** | optional | End of time range, in epoch time (milliseconds) | numeric | **count** | optional | Number of offenses to retrieve | numeric | **offense_id** | optional | Comma-separated list of offense IDs to fetch | string | `qradar offense id`

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.count | numeric | | 100 action_result.parameter.end_time | numeric | | 1669900000000 action_result.parameter.offense_id | string | `qradar offense id` | 44 action_result.parameter.start_time | numeric | | 1559900000000 action_result.data.\*.assigned_to | string | | admin action_result.data.\*.categories | string | | License Status action_result.data.\*.category_count | numeric | | 10 action_result.data.\*.close_time | string | | action_result.data.\*.closing_reason_id | string | `qradar offense closing reason id` | action_result.data.\*.closing_user | string | | action_result.data.\*.credibility | numeric | | 4 action_result.data.\*.description | string | | Local Malware Events
action_result.data.\*.destination_networks | string | | other action_result.data.\*.device_count | numeric | | 3 action_result.data.\*.domain_id | numeric | | action_result.data.\*.event_count | numeric | | 28603163 action_result.data.\*.flow_count | numeric | | 110 action_result.data.\*.follow_up | boolean | | False True action_result.data.\*.id | numeric | `qradar offense id` | 44 action_result.data.\*.inactive | boolean | | False True action_result.data.\*.last_updated_time | numeric | | 1559194600958 action_result.data.\*.local_destination_count | numeric | | 0 action_result.data.\*.magnitude | numeric | | 5 action_result.data.\*.offense_source | string | `ip` | 122.122.122.122 action_result.data.\*.offense_type | numeric | | 0 action_result.data.\*.policy_category_count | numeric | | 0 action_result.data.\*.protected | boolean | | False True action_result.data.\*.relevance | numeric | | 4 action_result.data.\*.remote_destination_count | numeric | | 1 action_result.data.\*.rules.\*.id | numeric | | action_result.data.\*.rules.\*.type | string | | action_result.data.\*.security_category_count | numeric | | 10 action_result.data.\*.severity | numeric | | 6 action_result.data.\*.source_count | numeric | | 1 action_result.data.\*.source_network | string | | Net-10-172-192.Net_10_0_0_0 action_result.data.\*.start_time | numeric | | 1558009780686 action_result.data.\*.status | string | | OPEN action_result.data.\*.username_count | numeric | `user name` | 0 action_result.summary | string | | action_result.summary.total_offenses | numeric | | 1 action_result.message | string | | Fetching all open offenses. Total offenses: 1 Total Offenses: 1 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'list closing reasons'
Get a list of offense closing reasons

Type: **investigate**
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**include_reserved** | optional | Include reserved offense closing reasons | boolean | **include_deleted** | optional | Include deleted offense closing reasons | boolean |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.include_deleted | boolean | | True False action_result.parameter.include_reserved | boolean | | True False action_result.data.\*.id | numeric | `qradar offense closing reason id` | 2 action_result.data.\*.is_deleted | boolean | | True False action_result.data.\*.is_reserved | boolean | | True False action_result.data.\*.text | string | | False-Positive, Tuned action_result.summary.total_offense_closing_reasons | numeric | | 5 action_result.message | string | | Total offense closing reasons: 5 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'get events'
Get events belonging to an offense

Type: **investigate**
Read only: **True**

Use fields_filter parameter to restrict the events returned that match the filter. For e.g. destinationip='10.10.0.52' and protocolid='6'. For further details refer to the documentation section of the action in the README.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** | optional | Offense ID to get events of | numeric | `qradar offense id` **start_time** | optional | Start of time range, in epoch time (milliseconds) | numeric | **end_time** | optional | End of time range, in epoch time (milliseconds) | numeric | **count** | optional | Number of events to retrieve | numeric | **fields_filter** | optional | Filter on event field values | string | **interval_days** | optional | Interval days | numeric |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.count | numeric | | 10 action_result.parameter.end_time | numeric | | 1669891174855 action_result.parameter.fields_filter | string | | sourceip='122.122.122.122' action_result.parameter.interval_days | numeric | | 20 action_result.parameter.offense_id | numeric | `qradar offense id` | 44 action_result.parameter.start_time | numeric | | 1559891174855 action_result.data.\*.AccountDomain | string | `domain` `url` | action_result.data.\*.Application | string | | action_result.data.\*.Bytes | string | | action_result.data.\*.BytesReceived | string | | action_result.data.\*.BytesSent | string | | action_result.data.\*.Destination Host Name | string | `host name` | action_result.data.\*.EventID | string | | action_result.data.\*.File Hash | string | | action_result.data.\*.File ID | string | | action_result.data.\*.File Path | string | | action_result.data.\*.Filename | string | | action_result.data.\*.Hostname | string | `host name` | action_result.data.\*.Installer Filename | string | | action_result.data.\*.Message | string | | action_result.data.\*.Payload | string | | Communication with Known Watched Networks There has been event communication with networks that appear on the systems watch and darknet lists. action_result.data.\*.Source Host Name | string | `host name` | action_result.data.\*.categoryname_category | string | | Suspicious Activity action_result.data.\*.destinationaddress | string | `ip` | 122.122.122.122 action_result.data.\*.destinationip | string | `ip` | 122.122.122.122 action_result.data.\*.destinationmac | string | | 00:00:00:00:00:00 action_result.data.\*.destinationport | numeric | `port` | 0 action_result.data.\*.endtime | numeric | | action_result.data.\*.eventcount | numeric | | action_result.data.\*.eventdirection | string | | L2R R2R action_result.data.\*.hostname_logsourceid | string | `host name` | Unknown Host 63 action_result.data.\*.identityip | string | `ip` | action_result.data.\*.logsourcegroupname_logsourceid | string | | Other action_result.data.\*.logsourceid | numeric | | 63 action_result.data.\*.logsourcename_logsourceid | string | | Custom Rule Engine-8 :: qradar action_result.data.\*.protocolname_protocolid | string | | Reserved action_result.data.\*.qid | numeric | | 70750119 action_result.data.\*.qidname_qid | string | | Communication with Known Watched Networks action_result.data.\*.relevance | numeric | | action_result.data.\*.severity | numeric | | action_result.data.\*.sourceaddress | string | `ip` | 122.122.122.122 action_result.data.\*.sourceip | string | `ip` | 122.122.122.122 action_result.data.\*.sourcemac | string | | 00:00:00:00:00:00 action_result.data.\*.sourceport | numeric | `port` | 0 action_result.data.\*.sourcev6 | string | `ipv6` | action_result.data.\*.starttime | numeric | | 1559194870184 action_result.data.\*.username | string | `user name` | action_result.summary.total_events | numeric | | 10 action_result.message | string | | Total events: 10 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'get flows'
Get flows that make up an offense for a particular IP

Type: **investigate**
Read only: **True**

Use the <b>fields_filter</b> parameter to restrict the flows returned. For e.g. protocolid='6'. For further details refer to the documentation section of the action in the README.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** | optional | IP to get all the flows of | string | `ip` **offense_id** | optional | Offense ID to get flows of | numeric | `qradar offense id` **start_time** | optional | Start of time range, in epoch time (milliseconds) | numeric | **end_time** | optional | End of time range, in epoch time (milliseconds) | numeric | **count** | optional | Number of flows to retrieve | numeric | **fields_filter** | optional | Filter in AQL format on flow field values | string |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.count | numeric | | 100 action_result.parameter.end_time | numeric | | 1559905203000 action_result.parameter.fields_filter | string | | sourceip='127.0.0.1' action_result.parameter.ip | string | `ip` | 122.122.122.122 action_result.parameter.offense_id | numeric | `qradar offense id` | 41 action_result.parameter.start_time | numeric | | 1559905201000 action_result.data.\*.Action | string | | action_result.data.\*.Application Determination Algorithm | numeric | | action_result.data.\*.Content Subject | string | | action_result.data.\*.Content Type | string | | action_result.data.\*.FTP Pass | string | | action_result.data.\*.FTP RETR File | string | | action_result.data.\*.FTP User | string | | action_result.data.\*.File Entropy | string | | action_result.data.\*.File Hash | string | | action_result.data.\*.File Name | string | | action_result.data.\*.File Size | string | | action_result.data.\*.Flow Direction Algorithm | numeric | | action_result.data.\*.Google Search Terms | string | | action_result.data.\*.HTTP Content-Type | string | | action_result.data.\*.HTTP GET Request | string | | action_result.data.\*.HTTP Host | string | | action_result.data.\*.HTTP Referer | string | | action_result.data.\*.HTTP Referrer | string | | action_result.data.\*.HTTP Response Code | string | | action_result.data.\*.HTTP Server | string | | action_result.data.\*.HTTP User Agent | string | | action_result.data.\*.HTTP User-Agent | string | | action_result.data.\*.HTTP Version | string | | action_result.data.\*.Originating User | string | | action_result.data.\*.Password | string | | action_result.data.\*.Request URL | string | | action_result.data.\*.SMTP From | string | | action_result.data.\*.SMTP HELO | string | | action_result.data.\*.SMTP Hello | string | | action_result.data.\*.SMTP To | string | | action_result.data.\*.Search Arguments | string | | action_result.data.\*.VLAN Tag | string | | action_result.data.\*.applicationid | numeric | | 1011 action_result.data.\*.applicationname_applicationid | string | | action_result.data.\*.category | numeric | | 18448 action_result.data.\*.categoryname_category | string | | action_result.data.\*.credibility | numeric | | 10 action_result.data.\*.destinationasn | string | | action_result.data.\*.destinationbytes | numeric | | 11567 action_result.data.\*.destinationdscp | numeric | | action_result.data.\*.destinationflags | string | | action_result.data.\*.destinationifindex | string | | action_result.data.\*.destinationip | string | `ip` | 10.1.16.15 action_result.data.\*.destinationpackets | numeric | | 108 action_result.data.\*.destinationpayload | string | | action_result.data.\*.destinationport | numeric | `port` | 3365 action_result.data.\*.destinationprecedence | numeric | | action_result.data.\*.destinationv6 | string | | 0:0:0:0:0:0:0:0 action_result.data.\*.domainid | numeric | | action_result.data.\*.firstpackettime | numeric | | 1559905202000 action_result.data.\*.flowbias | string | | action_result.data.\*.flowdirection | string | | L2R action_result.data.\*.flowid | numeric | | action_result.data.\*.flowinterface | string | | action_result.data.\*.flowinterfaceid | string | | 5 action_result.data.\*.flowsource | string | | action_result.data.\*.flowtype | numeric | | action_result.data.\*.fullmatchlist | string | | action_result.data.\*.geographic | string | | NorthAmerica.UnitedStates action_result.data.\*.hasdestinationpayload | boolean | | action_result.data.\*.hasoffense | boolean | | True action_result.data.\*.hassourcepayload | boolean | | False action_result.data.\*.hastlv | boolean | | action_result.data.\*.icmpcode | string | | action_result.data.\*.icmptype | string | | action_result.data.\*.intervalid | numeric | | 1603463820 action_result.data.\*.isduplicate | boolean | | action_result.data.\*.lastpackettime | numeric | | 1559905202999 action_result.data.\*.partialmatchlist | string | | action_result.data.\*.processorid | numeric | | 8 action_result.data.\*.protocolid | numeric | | action_result.data.\*.protocolname_protocolid | string | | action_result.data.\*.qid | numeric | | 53250087 action_result.data.\*.qidname_qid | string | | Test.Securetest action_result.data.\*.relevance | numeric | | action_result.data.\*.retentionbucket | string | | action_result.data.\*.severity | numeric | | 1 action_result.data.\*.sourceasn | string | | action_result.data.\*.sourcebytes | numeric | | 1031681 action_result.data.\*.sourcedscp | numeric | | action_result.data.\*.sourceflags | string | | action_result.data.\*.sourceifindex | string | | action_result.data.\*.sourceip | string | `ip` | 127.0.0.1 action_result.data.\*.sourcepackets | numeric | | 783 action_result.data.\*.sourcepayload | string | | action_result.data.\*.sourceport | numeric | | 4806 action_result.data.\*.sourceprecedence | numeric | | action_result.data.\*.sourcev6 | string | `ipv6` | 0:0:0:0:0:0:0:0 action_result.data.\*.starttime | numeric | | 1559905201000 action_result.data.\*.viewobjectpair | string | | action_result.summary.total_flows | numeric | | 33 action_result.message | string | | Total flows: 33 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'offense details'
Get details about an offense

Type: **investigate**
Read only: **True**

If the <b>ingest_offense</b> parameter is checked, then, it will ingest the events within the last N days (N - value in the <b>interval_days</b> parameter if given or value in the <b>interval_days</b> parameter in the app config or default 5 days) for the offense mentioned in the <b>offense_id</b> parameter. If the <b>ingest_offense</b> parameter is unchecked, it will fetch only the details of the provided offense ID in the <b>offense_id</b> parameter. The parameter <b>tenant_id</b> is used only when the <b>ingest_offense</b> parameter is checked.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** | required | Offense ID to get the details of | numeric | `qradar offense id` **tenant_id** | optional | Tenant ID for saving container | numeric | **ingest_offense** | optional | Ingest offense into Phantom | boolean |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.ingest_offense | boolean | | True False action_result.parameter.offense_id | numeric | `qradar offense id` | 43 action_result.parameter.tenant_id | numeric | | 123 action_result.data.\*.assigned_to | string | | admin action_result.data.\*.categories | string | | Error action_result.data.\*.category_count | numeric | | 4 action_result.data.\*.close_time | string | | 1602888300000 action_result.data.\*.closing_reason_id | string | `qradar offense closing reason id` | 3 action_result.data.\*.closing_user | string | | root action_result.data.\*.credibility | numeric | | 4 action_result.data.\*.description | string | | Anomaly: Access to Test or Test Defined Address
preceded by Communication with Known Watched Networks
action_result.data.\*.destination_networks | string | | other action_result.data.\*.device_count | numeric | | 3 action_result.data.\*.domain_id | numeric | | action_result.data.\*.event_count | numeric | | 1035 action_result.data.\*.flow_count | numeric | | 0 action_result.data.\*.follow_up | boolean | | False True action_result.data.\*.id | numeric | `qradar offense id` | 43 action_result.data.\*.inactive | boolean | | False True action_result.data.\*.last_updated_time | numeric | | 1559125383270 action_result.data.\*.local_destination_count | numeric | | 0 action_result.data.\*.magnitude | numeric | | 4 action_result.data.\*.offense_source | string | `ip` | 122.122.122.122 action_result.data.\*.offense_type | numeric | | 0 action_result.data.\*.policy_category_count | numeric | | 0 action_result.data.\*.protected | boolean | | False True action_result.data.\*.relevance | numeric | | 2 action_result.data.\*.remote_destination_count | numeric | | 1 action_result.data.\*.rules.\*.id | numeric | | action_result.data.\*.rules.\*.type | string | | action_result.data.\*.security_category_count | numeric | | 4 action_result.data.\*.severity | numeric | | 7 action_result.data.\*.source_count | numeric | | 1 action_result.data.\*.source_network | string | | other action_result.data.\*.start_time | numeric | | 1558008289506 action_result.data.\*.status | string | | OPEN action_result.data.\*.username_count | numeric | `user name` | 0 action_result.summary.flow_count | numeric | | 0 action_result.summary.name | string | | Anomaly: Access to Test or Test Defined Address
preceded by Communication with Known Watched Networks action_result.summary.source | string | `ip` | 122.122.122.122 action_result.summary.start_time | string | | 2019-04-04 21:28:47 UTC action_result.summary.status | string | | OPEN action_result.summary.total_offenses | numeric | | 1 action_result.summary.update_time | string | | 2019-05-14 10:23:03 UTC action_result.message | string | | Total offenses: 1 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'alt manage ingestion'
Manage ingestion details

Type: **generic**
Read only: **False**

The general structure of the state file is {"app_version":"app_version", "last_saved_ingest_time":"epoch_time_last_fetched_offense", "last_ingested_events_data":{"offense_id":"epoch_time_last_fetched_event_for_offense_id"}}. <ul><li>There is no validation for values provided in the <b>offense_id</b> action parameter because this action does not make any API calls to the QRadar instance and it merely provides a way of manipulating the state file. It is requested to please confirm if the offense ID being provided as an input exists on the QRadar instance. Any wrong value provided in the <b>offense_id</b> parameter may corrupt the state file and the functionalities dependent on it.</li><li>No comma-separated values should be provided in any of the action input parameters or else it may corrupt the state file and the functionalities dependent on it.</li><li>The <b>set last saved offense ingest time</b> operation sets the epoch time of the provided value in the <b>datetime</b> parameter against the <b>last_saved_ingest_time</b> key in the state file.</li><li>The <b>set last saved events ingest time</b> operation sets the epoch time of the provided value in the <b>datetime</b> parameter against the key corresponding to the offense ID value provided in the <b>offense_id</b> in the dictionary structure against the key <b>last_ingested_events_data</b> in the state file. The format for the date string should match the formats 'YYYY-MM-DD HH:MM:SS.Z', 'YYYY-MM-DDTHH:MM:SS.Z', 'YYYY-MM-DD', or 'HH:MM:SS.Z'. Users can provide only date (time will be 00:00:00.000000) or only time (current date will be considered by default). The action considers that the provided value in the <b>datestring</b> parameter represents the date string in the timezone selected in the asset configuration parameter <b>timezone</b> and accordingly stores the epoch time into the state file.</li><li>The <b>delete last saved ingestion time data</b> operation deletes the entire last saved ingestion time data stored in the state file.</li><li>The <b>get last saved ingestion time data</b> operation fetches the entire last saved ingestion time data stored in the state file.</li><li>The parameter <b>offense_id</b> does not support comma-separated values. The user has to provide a single non-zero positive integer value of the corresponding Offense ID.</li><li>The parameter <b>offense_id</b> is mandatory for the operation <b>set last saved events ingest time</b>.</li></ul>

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**operation** | required | Operation to perform on the ingestion data stored in the state file | string | **datetime** | optional | Datetime string to be stored against the ingestion data in the state file | string | **offense_id** | optional | Offense ID against which to store the 'datetime' parameter value | string | `qradar offense id`

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.datetime | string | | 2019-12-09 11:11:11.0001 action_result.parameter.offense_id | numeric | `qradar offense id` | 4 action_result.parameter.operation | string | | get last saved ingestion time data action_result.data.\*.last_ingested_events_ingest_time | string | | Offense ID_1=Fri Nov 29 10:05:25 2019 UTC +0000, Offense ID_3=Fri Nov 29 10:01:24 2019 UTC +0000, Offense ID_2=Fri Nov 29 10:03:18 2019 UTC +0000 action_result.data.\*.last_ingested_events_ingest_time_as_epoch.1 | numeric | | 1575021925702 action_result.data.\*.last_ingested_events_ingest_time_as_epoch.10 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.19 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.20 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.21 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.22 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.23 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.24 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.74 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.75 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.76 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.77 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.78 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.79 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.80 | numeric | | action_result.data.\*.last_ingested_events_ingest_time_as_epoch.82 | numeric | | action_result.data.\*.last_saved_offense_ingest_time | string | | Mon Dec 09 11:11:11 2019 UTC +0000 action_result.data.\*.last_saved_offense_ingest_time_as_epoch | numeric | | 1575889871000 action_result.summary.last_ingested_events_ingest_time | string | | Offense ID_1=Fri Nov 29 10:05:25 2019 UTC +0000, Offense ID_3=Fri Nov 29 10:01:24 2019 UTC +0000, Offense ID_2=Fri Nov 29 10:03:18 2019 UTC +0000 action_result.summary.last_saved_offense_ingest_time | string | | Mon Dec 09 11:11:11 2019 UTC +0000 action_result.message | string | | Last saved offense ingest time: Mon Dec 09 11:11:11 2019 UTC +0000, Last ingested events ingest time: Offense ID_1=Fri Nov 29 10:05:25 2019 UTC +0000, Offense ID_3=Fri Nov 29 10:01:24 2019 UTC +0000, Offense ID_2=Fri Nov 29 10:03:18 2019 UTC +0000 summary.total_objects | numeric | | 2 summary.total_objects_successful | numeric | | 2 ## action: 'run query'
Execute an ariel query on the QRadar device

Type: **investigate**
Read only: **True**

Use this action to execute queries using AQL on the QRadar device. AQL is a well documented (on the IBM website) query language with quite a few built-in functions.<br>Do note that this action could have a dynamic set of values returned in the data array since the query can specify the columns to return. This is the main reason for not listing the data paths.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**query** | required | Ariel Query | string | `qradar ariel query`

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.query | string | `qradar ariel query` | select qid from events action_result.data.\*.events.\*.AccountDomain | string | | action_result.data.\*.events.\*.Application | string | | action_result.data.\*.events.\*.Bytes | string | | action_result.data.\*.events.\*.BytesReceived | string | | action_result.data.\*.events.\*.BytesSent | string | | action_result.data.\*.events.\*.Destination Host Name | string | | action_result.data.\*.events.\*.EventID | string | | action_result.data.\*.events.\*.File Hash | string | | action_result.data.\*.events.\*.File ID | string | | action_result.data.\*.events.\*.File Path | string | | action_result.data.\*.events.\*.Filename | string | | action_result.data.\*.events.\*.Installer Filename | string | | action_result.data.\*.events.\*.Message | string | | action_result.data.\*.events.\*.Payload | string | | action_result.data.\*.events.\*.Source Host Name | string | | action_result.data.\*.events.\*.category | numeric | | 38750003 action_result.data.\*.events.\*.categoryname_category | string | | action_result.data.\*.events.\*.destinationaddress | string | | action_result.data.\*.events.\*.destinationip | string | `ip` | 122.122.122.122 action_result.data.\*.events.\*.destinationmac | string | | action_result.data.\*.events.\*.destinationport | numeric | | 0 action_result.data.\*.events.\*.endtime | numeric | | action_result.data.\*.events.\*.eventcount | numeric | | 1 action_result.data.\*.events.\*.eventdirection | string | | action_result.data.\*.events.\*.hostname_logsourceid | string | | action_result.data.\*.events.\*.identityip | string | `ip` | 122.122.122.122 action_result.data.\*.events.\*.logsourcegroupname_logsourceid | string | | action_result.data.\*.events.\*.logsourceid | numeric | | 65 action_result.data.\*.events.\*.logsourcename_logsourceid | string | | action_result.data.\*.events.\*.magnitude | numeric | | 5 action_result.data.\*.events.\*.protocolid | numeric | | 255 action_result.data.\*.events.\*.protocolname_protocolid | string | | action_result.data.\*.events.\*.qid | numeric | | 38750003 action_result.data.\*.events.\*.qidname_qid | string | | action_result.data.\*.events.\*.queid | numeric | | action_result.data.\*.events.\*.relevance | numeric | | action_result.data.\*.events.\*.severity | numeric | | action_result.data.\*.events.\*.sourceaddress | string | | action_result.data.\*.events.\*.sourceip | string | `ip` | 122.122.122.122 action_result.data.\*.events.\*.sourcemac | string | | action_result.data.\*.events.\*.sourceport | numeric | | 0 action_result.data.\*.events.\*.starttime | numeric | | 1559907060001 action_result.data.\*.events.\*.username | string | `user name` | action_result.data.\*.flows.\*.category | numeric | | action_result.data.\*.flows.\*.destinationbytes | numeric | | action_result.data.\*.flows.\*.destinationflags | string | | action_result.data.\*.flows.\*.destinationip | string | | action_result.data.\*.flows.\*.destinationpackets | numeric | | action_result.data.\*.flows.\*.firstpackettime | numeric | | action_result.data.\*.flows.\*.flowtype | numeric | | action_result.data.\*.flows.\*.lastpackettime | numeric | | action_result.data.\*.flows.\*.protocolid | numeric | | action_result.data.\*.flows.\*.qid | numeric | | action_result.data.\*.flows.\*.sourcebytes | numeric | | action_result.data.\*.flows.\*.sourceflags | string | | action_result.data.\*.flows.\*.sourceip | string | | action_result.data.\*.flows.\*.sourcepackets | numeric | | action_result.summary | string | | action_result.message | string | | Successfully ran query summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'add listitem'
Add an item to a reference set in QRadar

Type: **generic**
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**reference_set_name** | required | Name of reference set to add to | string | **reference_set_value** | required | Value to add to the reference set | string |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.reference_set_name | string | | Demo action_result.parameter.reference_set_value | string | | 122.122.122.122 action_result.data.\*.creation_time | numeric | | 1558518483009 action_result.data.\*.element_type | string | | IP action_result.data.\*.name | string | | Demo action_result.data.\*.number_of_elements | numeric | | 3 action_result.data.\*.timeout_type | string | | FIRST_SEEN action_result.summary.element_type | string | | IP action_result.summary.name | string | | Demo action_result.summary.number_of_elements | numeric | | 3 action_result.message | string | | Element type: IP, Name: Demo, Number of elements: 3 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'close offense'
Close an active offense, marking status=CLOSED

Type: **generic**
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** | required | Offense ID to close | numeric | `qradar offense id` **closing_reason_id** | required | Reason for closing offense | numeric | `qradar offense closing reason id`

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.closing_reason_id | numeric | `qradar offense closing reason id` | 1 action_result.parameter.offense_id | numeric | `qradar offense id` | 41 action_result.data.\*.assigned_to | string | | admin action_result.data.\*.categories | string | | Error action_result.data.\*.category_count | numeric | | 4 action_result.data.\*.close_time | numeric | | 1559905203000 action_result.data.\*.closing_reason_id | numeric | `qradar offense closing reason id` | 1 action_result.data.\*.closing_user | string | | API_token: Phantom action_result.data.\*.credibility | numeric | | 4 action_result.data.\*.description | string | | Anomaly: Access to Test or Test Defined Address
preceded by Communication with Known Watched Networks
action_result.data.\*.destination_networks | string | | other action_result.data.\*.device_count | numeric | | 3 action_result.data.\*.domain_id | numeric | | action_result.data.\*.event_count | numeric | | 2660 action_result.data.\*.flow_count | numeric | | 0 action_result.data.\*.follow_up | boolean | | False True action_result.data.\*.id | numeric | `qradar offense id` | 41 action_result.data.\*.inactive | boolean | | False True action_result.data.\*.last_updated_time | numeric | | 1557829383413 action_result.data.\*.local_destination_count | numeric | | 0 action_result.data.\*.magnitude | numeric | | 3 action_result.data.\*.offense_source | string | `ip` | 122.122.122.122 action_result.data.\*.offense_type | numeric | | 0 action_result.data.\*.policy_category_count | numeric | | 0 action_result.data.\*.protected | boolean | | False True action_result.data.\*.relevance | numeric | | 2 action_result.data.\*.remote_destination_count | numeric | | 1 action_result.data.\*.rules.\*.id | numeric | | action_result.data.\*.rules.\*.type | string | | action_result.data.\*.security_category_count | numeric | | 4 action_result.data.\*.severity | numeric | | 7 action_result.data.\*.source_count | numeric | | 1 action_result.data.\*.source_network | string | | other action_result.data.\*.start_time | numeric | | 1554413327061 action_result.data.\*.status | string | | CLOSED action_result.data.\*.username_count | numeric | `user name` | 0 action_result.summary.flow_count | numeric | | 0 action_result.summary.name | string | | Anomaly: Access to Test or Test Defined Address
preceded by Communication with Known Watched Networks action_result.summary.source | string | `ip` | 122.122.122.122 action_result.summary.start_time | string | | 2019-04-04 21:28:47 UTC action_result.summary.status | string | | CLOSED action_result.summary.update_time | string | | 2019-05-14 10:23:03 UTC action_result.message | string | | Status: CLOSED, Source: 122.122.122.122, Update time: 2019-05-14 10:23:03 UTC, Name: Anomaly: Access to Test or Test Defined Address
preceded by Communication with Known Watched Networks, Flow count: 0, Start time: 2019-04-04 21:28:47 UTC summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'update offense'
Attach a note to an offense

Type: **generic**
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** | required | Offense ID to attach note to | numeric | `qradar offense id` **note_text** | required | Text to put into note | string |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.note_text | string | | Note Added By Phantom action_result.parameter.offense_id | numeric | `qradar offense id` | 41 action_result.data | string | | action_result.summary | string | | action_result.message | string | | Successfully added note to offense summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'assign user'
Assign the user to an offense

Type: **generic**
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**offense_id** | required | Offense ID to assign the user to | numeric | `qradar offense id` **assignee** | required | Name of the user | string |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.assignee | string | | admin action_result.parameter.offense_id | numeric | `qradar offense id` | 41 action_result.data | string | | action_result.summary | string | | action_result.message | string | | Successfully assigned user to offense summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'get rule info'
Retrieve QRadar rule information

Type: **investigate**
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**rule_id** | required | Rule ID for which information needs to be extracted | numeric | `qradar rule id`

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.rule_id | numeric | `qradar rule id` | 1421 action_result.data.\*.average_capacity | numeric | | 3541750 action_result.data.\*.base_capacity | numeric | | 3541750 action_result.data.\*.base_host_id | numeric | | 384 action_result.data.\*.capacity_timestamp | numeric | | 1566896735557 action_result.data.\*.creation_date | numeric | | 1155662266056 action_result.data.\*.enabled | boolean | | True False action_result.data.\*.id | numeric | | 1421 action_result.data.\*.identifier | string | | SYSTEM-1421 action_result.data.\*.linked_rule_identifier | string | | action_result.data.\*.modification_date | numeric | | 1267729985038 action_result.data.\*.name | string | | User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories action_result.data.\*.origin | string | | SYSTEM action_result.data.\*.owner | string | | admin action_result.data.\*.type | string | | EVENT action_result.summary.id | numeric | | 1421 action_result.summary.name | string | | User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories action_result.message | string | | Id: 1421, Name: User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'list rules'
List all QRadar rules

Type: **investigate**
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**count** | optional | Number of rules to retrieve | numeric |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed action_result.parameter.count | numeric | | 31 action_result.data.\*.average_capacity | numeric | | 3541750 action_result.data.\*.base_capacity | numeric | | 3541750 action_result.data.\*.base_host_id | numeric | | 384 action_result.data.\*.capacity_timestamp | numeric | | 1566896735557 action_result.data.\*.creation_date | numeric | | 1155662266056 action_result.data.\*.enabled | boolean | | True False action_result.data.\*.id | numeric | `qradar rule id` | 1421 action_result.data.\*.identifier | string | | SYSTEM-1421 action_result.data.\*.linked_rule_identifier | string | | action_result.data.\*.modification_date | numeric | | 1267729985038 action_result.data.\*.name | string | | User:BB:FalsePositives: User Defined Server Type 2 False Positive Categories action_result.data.\*.origin | string | | SYSTEM action_result.data.\*.owner | string | | admin action_result.data.\*.type | string | | EVENT action_result.summary.total_rules | numeric | | 135 action_result.message | string | | Total rules: 135 summary.total_objects | numeric | | 1 summary.total_objects_successful | numeric | | 1 ## action: 'on poll'
Callback action for the on_poll ingest functionality

Type: **ingest**
Read only: **True**

The default start_time is the past 5 days. The default end_time is now.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container_id** | optional | Parameter ignored for this app | string | **start_time** | optional | Start of time range, in epoch time (milliseconds) | numeric | **end_time** | optional | End of time range, in epoch time (milliseconds) | numeric | **container_count** | optional | Maximum number of container records to query for | numeric | **artifact_count** | optional | Parameter ignored for this app | numeric |

#### Action Output

No Output

______________________________________________________________________

This file contains auto-generated SOAR connector documentation.

Copyright {{year}} Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

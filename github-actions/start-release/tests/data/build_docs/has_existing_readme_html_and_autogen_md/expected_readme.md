[comment]: # "Auto-generated SOAR connector documentation"
# QRadar

Publisher: Splunk  
Connector Version: 2\.1\.2  
Product Vendor: IBM  
Product Name: QRadar  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.9\.39220  

This app supports generic, investigative, and ingestion actions on an IBM QRadar device

[comment]: # " File: README.md"
[comment]: # " Copyright (c) 2016-2021 Splunk Inc."
[comment]: # ""
[comment]: # " SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part"
[comment]: # " without a valid written license from Splunk Inc. is PROHIBITED."
[comment]: # ""
This App is an Ingestion source. In the Phantom documentation, in the [Administration
Manual](../admin/) under the [Data Sources](../admin/sources) section, you will find an explanation
of how Ingest Apps works and how information is extracted from the ingested data. There is a general
explanation in Overview, and some individuals Apps have their sections.

**QRadar Instance Minimum Version Compatibility**

-   With this version of the QRadar app on Phantom, we declare support for the QRadar instances
    which are on and above the v7.3.1. This app has been tested and certified on the v7.3.1 version
    of the QRadar.
-   The expectations of the actions with this version of the app have not been changed majorly. It
    is recommended to read the documentation for the app and each action first to understand the
    functioning of the actions of all the asset configuration and the action parameters.

**Playbook Backward Compatibility**

-   The existing action parameters have been modified in the actions given below. Hence, it is
    requested to the end-user to please update their existing playbooks by re-inserting the
    corresponding action blocks or by providing appropriate values to these action parameters to
    ensure the correct functioning of the playbooks created on the earlier versions of the app.

      

    -   Alt Manage Ingestion - The new drop-down values in the \[operation\] parameter have been
        added and the existing ones are modified.
    -   Get Flows - This action was not working correctly and we have updated the logic for this
        action's functionality.
    -   Offense Details - The action parameter for \[interval_days\] has been removed as it was not
        getting used in the action.

**Explanation of App Settings Parameter**

-   **interval_days**
    -   For List Offenses and Get Events action if the \[start_time\] is specified, it will be given
        priority, if not provided, this value is internally derived by subtracting the
        \[interval_days\] from the \[end_time\]. For the Get Events action, this field is having a
        higher preference over the \[interval_days\] action parameter if both are specified. If
        \[interval_days\] is not specified in the app settings it will take the default value which
        is 5.
    -   If \[Alternative ariel query\] configuration parameter is checked, for On Poll and Get
        Events action to fetch the events, the time based filtering in this workflow is applied
        based on the granularity of days instead of applying it based on the granularity of epoch
        and Datetime formats.
    -   For On Poll, to fetch the offenses, if there is time stored in the state file it will be
        given priority, if not provided, this value is internally derived by subtracting the
        \[interval_days\] from the \[end_time\]. If \[interval_days\] is not specified in the app
        settings it will take the default value which is 5.
    -   For On Poll, to fetch the events, if there is time stored in the state file it will be given
        priority, if not provided, the \[start_time\] will be calculated by back-dating offense's
        \[start_time\] by the value of \[events_ingest_start_time\] configuration parameter.
    -   \[interval_days\] parameter is not used in the alternative ingestion algorithm.

**Explanation of Asset Configuration Parameters**

-   All the asset configuration parameters which are affecting the functioning of the On Poll action
    will also affect the functioning of the action \[Offense Details\] when the corresponding action
    parameter \[ingest_offense\] is checked

-   **Asset Configuration Parameters**

      

    -   **artifact_max -** Maximum number of event artifacts to ingest for the \[On Poll\] (both
        manual and scheduled) action and \[Offense Details\] action with \[ingest_offense\] action
        parameter set to TRUE. This count excludes the default generated offense artifact.
    -   **cef_event_map -** JSON formatted string of key-value pairs for CEF mapping - use
        double-quotes. CEF values are the keys, QRadar fields are the values. QRadar fields are the
        internal names of the fields for the events data exported in the JSON format. These internal
        names can be obtained from the JSON data obtained by running the \[Get Events\] action. If
        the cef_event_map is provided by the user, the fields mentioned in this mapping and the
        default CEF mapping fields along with the extra fields provided in the \[Event fields to
        include while querying\] configuration parameter will be included in the CEF data of the
        artifact created for ingestion. If the cef_event_map is not provided by the user, then, the
        default event fields along with the extra fields provided in the \[Event fields to include
        while querying\] configuration parameter will be included in the CEF data of the artifacts
        created for ingestion. If the mapping provided in the \[CEF event map\] configuration field
        consists of the fields which are already covered by the default CEF mapping, then, the
        provided CEF mapping in the configuration parameter will also be created along with the
        default CEF mapping.  
          
        **Sample \[CEF Event Map\] value**  
        `         {"magnitudeValue":"magnitude","customAttributeValue1":"custom_attribute_1","customAttributeValue2":"Custom Attribute 2"}                          `
        **Important Point** - Internally the field UTF8(payload) is fetched by the name of Payload
        (i.e. UTF8(payload) as Payload). Hence, to map the UTF8(payload) field in the CEF event map,
        please provide the mapping as mentioned here {"\[cef_name_for_payload_field\]": "Payload"}.
        -   The default CEF mapping is provided below (left-side is the display name of the event
            fields in the ingested artifacts data and right-side is the original internal name of
            the fields of an event)

              
            `            {                        "signature_id": "qid",                        "name": "qidname_qid",                        "severity": "severity",                        "applicationProtocol": "Application",                        "destinationMacAddress": "destinationmac",                        "destinationNtDomain": "AccountDomain",                        "destinationPort": "destinationport",                        "destinationAddress": "destinationaddress",                        "endTime": "endtime",                        "fileHash": "File Hash",                        "fileId": "File ID",                        "filePath": "File Path",                        "fileName": "Filename",                        "bytesIn": "BytesReceived",                        "message": "Message",                        "bytesOut": "BytesSent",                        "transportProtocol": "protocolname_protocolid",                        "sourceMacAddress": "sourcemac",                        "sourcePort": "sourceport",                        "sourceAddress": "sourceaddress",                        "startTime": "starttime",                        "payload": "Payload"                        }           `
    -   **cef_value_map -** JSON formatted string representation of a dictionary used to map CEF
        field values to new values. Similar to cef_event_map, replace the value of any CEF field
        with another value. For example, to replace the value of cef.requestURL of \\"nourl\\", with
        null value, provide { \\"nourl\\": null }. If the user wants to replace a numeric
        (integer\|float) value with some other value, due to the SDK issue, the user has to provide
        the key-value map in this format. e.g. if user wants to replace value 4 with 10 and 5.3 with
        6.7, provide this CEF value mapping {"numeric(4)": 10, "numeric(5.3)": 6.7}  
        **Sample \[CEF Value Map\] values**  
        -   To replace integer\|float values; value 4 with 10 and 5.3 with 6.7, provide below CEF
            value mapping

              
            `            {"numeric(4)": 10, "numeric(5.3)": 6.7}           `

        -   To replace string values; Alert with Alert_Info

              
            `            {"Alert": "Alert_Info"}           `
    -   **delete_empty_cef_fields -** Set true to delete CEF fields with empty values.
    -   **event_fields_for_query -** Optionally define a new comma-separated list of fields (system
        or custom or both) for querying. A comma-separated list of field internal names as obtained
        in the JSON data while running the \[Get Events\] action. Use double-quotes if field names
        contain spaces.
    -   **add_offense_id_to_name -** Optionally add the offense ID to the container name. If the
        user runs the On Poll action without this value being checked and then, stops the ingestion
        and again starts the ingestion after checking this parameter (to TRUE), new containers will
        not be created for the offenses which were already ingested and their names will also not be
        changed to have the offense ID prefixed. All the new event artifacts will continue getting
        created in the existing containers. Hence, it is recommended to delete the already ingested
        containers and artifacts if the user is changing the value of this parameter to ensure that
        all the containers and artifacts get created with the new expected names.
    -   **alternative_ariel_query -** Alternative ariel query; considers Datetime specifications if
        provided or else retrieve events from the last \[interval_days\] (default=5) days; affects
        \[On Poll\], \[Offense Details\] and \[Get Events\] actions; \[On Poll\] will auto-extend
        the number of days to start on/before the day of the offense being retrieved.
    -   **alt_initial_ingest_time -** This parameter is applicable only if
        \[alternative_ingest_algorithm\] parameter is checked. Set the \[last_saved_ingest_time\] to
        this. This is the initial lower limit to ingest offenses. This field accepts the values
        mentioned here; a string 'yesterday', a valid python parsable Datetime (dateutil module)
        (for the given date-time string, while parsing the date portion, higher preference is given
        to MM-DD-YYYY format and if the date-time string stands invalid in that date format, then,
        than it is considered to have the DD-MM-YYYY date format) or an epoch time in milliseconds;
        if no value is provided, then, the default value is 'yesterday'. Examples - yesterday,
        2020-02-25 12:00:00, 2020-12-01T05:00:00, 2019-04-30, 01-20-2020, 20-01-2020, 06:30:00, etc.
    -   **alt_ingest_order -** This parameter is applicable only if \[alternative_ingest_algorithm\]
        parameter is checked. The parameter alt_ingest_order will decide the order in which the
        offense will be fetched (oldest first or latest first).
    -   **alt_time_field -** This parameter is applicable only if \[alternative_ingest_algorithm\]
        parameter is checked. The parameter alt_time_field will decide the time on which the
        alt_ingest_order will be applied (start_time or last_updated_time or either)
    -   **ingest_open -** This parameter is optional and if not set to true, it will fetch all the
        offenses (including the closed offenses). To fetch only open offenses ingest only open must
        be set to TRUE. This configuration parameter is used in List Offenses, Offense Details as
        well as in On Poll action.
    -   **alternative_ingest_algorithm -** This parameter is optional and if not set to true then,
        the app will ignore the values kept in the \[alt_ingest_order\] and \[alt_time_field\]. If
        the parameter \[alternative_ingest_algorithm\] is set to true then, the offenses will be
        fetched according to \[alt_ingest_order\] and \[alt_time_field\] parameters. This
        configuration parameter is used in the List Offenses, Offense Details as well as in the On
        Poll action.
    -   **events_ingest_start_time -** This parameter is optional and the default value is 60. This
        parameter defines the relative number of minutes (in milliseconds) to back-date the
        offense's 'start_time' to start fetching the events for that particular offense. e.g. if
        events_ingest_start_time = 25 and offense's start_time = 1582618635661, then, after
        back-date, the final timestamp from which we will start fetching the events for that
        particular offense is 1582618635661 - (25 \* 60 \* 1000) = 1582617135661. NOTE - This
        parameter is applicable only for the manual POLL NOW, the first run of the SCHEDULED \|
        INTERVAL polling, and other actions like \[Offense Details\] which are involved in the
        events ingestion.
    -   **containers_only -** This parameter is optional and if not set to true then, the offenses
        will be created as containers and the events of the offenses will be created as the
        artifacts. If this parameter is set to true then, the offenses will be created as containers
        and the details of the offenses will be created as the artifacts in those containers
        respectively. This configuration parameter is used in the Offense Details and On Poll
        actions.
    -   **has_offense -** This parameter is optional and by default will be checked as true. This
        parameter describes whether the events and flows should be associated with the offense or
        not while fetching the events and flows. If this is set to true, then only the events and
        flows associated with the offense will be considered. This configuration parameter is used
        in the Get Events, Get Flows as well as in the On Poll action. For Get Events and Get Flows
        Action, 'has_offense' will only be considered if the user has passed the 'offense_id' while
        running these actions.
    -   **offense_ingest_start_time -** This parameter is optional and the default will be 0. This
        parameter defines the relative number of minutes (in milliseconds) to back-date the
        offense's 'start_time' to start fetching the offenses. e.g. if offense_ingest_start_time =
        25 and the time to start fetching offenses is 1582618635661, then after back-date, the final
        timestamp from which we will start fetching the offenses would be 1582618635661 - (25 \* 60
        \* 1000) = 1582617135661. This parameter is applicable for each type of polling.
    -   **event_ingest_end_time -** This parameter is optional and the default will be 0. This
        parameter defines the relative number of minutes (in milliseconds) to modify the event
        ingestion 'end_time' by after-dating event ingestion 'start_time'. The 'start_time' will be
        \[offense's start_time - events_ingest_start_time\] for manual polling and the first run of
        scheduled \| interval polling and for the next runs, it will take time stored in the state
        file against last_ingested_events_data for a particular offense. e.g. if
        event_ingest_end_time = 25 and the 'start_time' to fetch events is 1582618635661, then after
        modification, the final 'end_time' to stop fetching events would be 1582618635661 + (25 \*
        60 \* 1000) = 1582620135661. If the modified 'end_time' exceeds the current time then it
        will consider the current time as 'end_time'. This parameter is applicable for each type of
        polling.
    -   **max_events_per_offense -** This parameter is optional and the default will be None. This
        parameter defines the maximum accumulated artifacts to be ingested per offense, including
        the default generated offense artifact. e.g. if max_events_per_offense = 100, then maximum
        artifacts to be ingested in each container should not be greater than 100, considering all
        polling cycles. 'artifact_max' parameter can affect the functionality of the
        'max_events_per_offense' parameter based on its value as mentioned below.
        -   If artifact_max is less than max_events_per_offense, then it will ingest artifact_max
            number of artifacts per cycle and once the total artifacts count in a container equals
            or exceeds the max_events_per_offense count it will not collect artifacts. e.g. If
            artifact_max = 20 and max_events_per_offense = 30, then in first polling cycle it will
            ingest 21 artifacts (one default generated offense artifact). In the next polling cycle,
            it will ingest 9 more artifacts. As the total artifacts in the container get equal to
            the max_events_per_offense it will not collect artifacts from the next cycle.
        -   If max_events_per_offense is less than artifact_max, then it will ingest
            max_events_per_offense number of artifacts. e.g. if max_events_per_offense = 10 and
            artifact_max = 15, then it will ingest 10 artifacts.
        -   If max_events_per_offense = 1, then irrespective of any value provided in
            'artifact_max', it will ingest only one artifact (default generated offense artifact).
        -   NOTE - If offense will get updated while Qradar event creation, accordingly offense
            artifacts will also be ingested in phantom with updated parameters. This can affect the
            functionality of max_events_per_offense. e.g. if artifact_max = 5 and
            max_events_per_offense = 8, then in first cycle it will ingest 6 artifacts (one default
            generated offense artifact). In the next polling cycle, it will ingest 2 more event
            artifacts but if the offense is updated then it will also ingest one more offense
            artifact and the total artifact count will be one more than max_events_per_offense.

**Explanation of QRadar Actions' Parameters**

-   **Test Connectivity (Authentication Details)**

      

    -   This action provides 2 modes of providing the authentication: Basic Auth and Auth Token.
    -   It expects the user to enter either a valid auth token or a valid pair of username and
        password both.
    -   If none of the 3 configuration parameters for \[Username\], \[Password\], and \[Auth Token
        for QRadar REST API calls\] is provided, the action fails with an appropriate error.
    -   If the user provides both the auth token and the pair of username and password, then, the
        \[Test Connectivity\] action will validate both the modes of authentication and will throw
        an appropriate error if any credentials are invalid.
    -   If the user provides the auth token and any one of the username and password, the
        connectivity will fail and will throw an error to provide either both the username and
        password or none of them as in this case the auth token already exists and has a higher
        preference than the username and password. If the auth token is not provided, then, the user
        must provide both the username and password.
    -   The connectivity gives a higher preference to the auth token than that using the pair of
        username and password.

      

-   **List Offenses**

      

    -   Default Offenses Ingestion Workflow

          

        -   The offenses are fetched based on the logic that either their \[start_time\] or their
            \[last_updated_time\] is between the time range defined by \[start_time\] and
            \[end_time\].
        -   **Start Time -** This field expects an epoch value in milliseconds. If not provided,
            this value is internally derived by subtracting the \[interval_days\] from the
            \[end_time\]. This field is having a higher preference over the \[interval_days\] action
            parameter if both are specified.
        -   **End Time -** This field expects an epoch value in milliseconds. If not provided, this
            value is equal to the current epoch value in milliseconds.
        -   **Count -** This field expects a valid non-zero integer value or empty value. If
            provided, offenses equal to the provided value are fetched. If left empty, the default
            100 offenses matching the filter criteria are fetched. If the user wants to fetch all
            the offenses, provide a value greater than the total offenses that exist on the QRadar
            server.
        -   **Offense ID -** This field expects a comma-separated string containing valid offense
            IDs. If this is provided, irrespective of the start_time or end_time, the offenses
            corresponding to all the offense IDs provided here will be fetched based on the value
            provided in the \[count\] parameter.

          

    -   Alternate Offenses Ingestion Workflow

          

        -   This workflow has the functionalities similar to the default ingestion workflow with the
            below-mentioned points getting considered while ingestion.
        -   This workflow considers the value stored against the key \[last_saved_ingest_time\] in
            the state file (only for On Poll and Ingest Offense action with ingest_offense set to
            TRUE) as the start time to fetch the offenses. If the key is not found in the state
            file, it considers the value mentioned in the \[Alternative initial ingestion time\]
            asset configuration parameter as the start time to fetch the offenses. If none of the
            above-mentioned values are found, it considers the default value as yesterday. It does
            not consider the \[interval_days\] parameter mentioned in the \[app_config\] settings.
        -   This workflow is considered only if the \[Alternative ingest algorithm for offenses\]
            configuration parameter is checked.
        -   The configuration parameters \[Alternative ingestion time field\] and \[Alternative
            ingestion order for offenses\] are applicable for this workflow only if the
            \[Alternative ingest algorithm for offenses\] config parameter is checked.
        -   This workflow provides a provision to fetch the offenses in the \[latest first\] and the
            \[oldest first\] order.
        -   This workflow provides a provision to fetch the offenses in the sorted order based on
            the QRadar offense time fields \[starttime\] and \[last_updated_time\]. Based on the
            above-mentioned time field selected, the offenses whose time field fall in the time
            range (inclusive of boundaries) defined by \[start_time\] and \[end_time\] action
            parameters are fetched. If the time field selected is \[either\], then, the offenses
            whose either \[starttime\] or \[last_updated_time\] falls in the time range (inclusive
            of boundaries) defined by \[start_time\] and \[end_time\] action parameters are fetched.
            For the time field \[either\], for the On Poll actions (scheduled \| interval polling)
            the maximum of the \[starttime\] or \[last_updated_time\] for the last fetched offense
            is stored in the state file against the key \[last_saved_ingest_time\].

      

-   **Get Events**

      

    -   Default Ariel Query Events Ingestion Workflow

          

        -   The events are fetched in the descending order of the values in the \[starttime\] field.
        -   **Start Time -** This field expects an epoch value in milliseconds. If not provided,
            this value is internally derived by subtracting the \[interval_days\] from the
            \[end_time\]. This field is having a higher preference over the \[interval_days\] action
            parameter if both are specified.
        -   **End Time -** This field expects an epoch value in milliseconds. If not provided, this
            value is equal to the current epoch value in milliseconds.
        -   **Count -** This field expects a valid non-zero integer value or empty value. If
            provided, events equal to the provided value are fetched. If left empty, default 100
            events matching the filter criteria are fetched. If the user wants to fetch all the
            events, provide a value greater than the total events that exist on the QRadar server.
        -   **Interval Days -** This field expects a valid non-zero integer value or empty value. If
            provided, events within the last n days (n is equal to the value provided in
            \[interval_days\] parameter) are fetched. If left empty, the value provided in the \[App
            Config Settings\] is considered in the \[interval_days\] parameter. If \[App Config
            Settings\] is also left empty, the default value of 5 days is considered in the
            \[interval_days\] parameter.
        -   **Fields Filter -** This field expects a filter string in the valid AQL query syntax.
        -   **Offense ID -** This field expects a unique offense ID to fetch the events for.

          

    -   Alternate Ariel Query Events Ingestion Workflow

          

        -   This workflow has the functionalities similar to the default ingestion workflow with the
            below-mentioned points getting considered while ingestion.
        -   This workflow is considered only if the \[Alternative ariel query\] configuration
            parameter is checked.
        -   The configuration parameter \[Alternative initial ingestion time\] is applicable for
            this workflow only if the \[Alternative ariel query\] config parameter is checked.
        -   This workflow performs the same functionality as the default ingestion workflow, but
            with a different form of the Ariel query. The time based filtering in this workflow is
            applied based on the granularity of days instead of applying it based on the granularity
            of epoch and Datetime formats.
        -   As the time based filtering in this workflow is applied based on the granularity of
            days, back-dating event fetching 'start_time' and after-dating event fetching 'end_time'
            does not work with this workflow.

      

-   **Offense Details**

      

    -   Default Offenses Ingestion Workflow

          

        -   This action will behave similarly to a manual On Poll action run if the
            \[ingest_offense\] flag is checked and it will ingest all the events as artifacts for
            the provided offense ID.

        -   **Tenant ID -** This field expects a valid tenant ID of the Phantom server for saving
            the container. If multi-tenancy is not enabled, then the events will be ingested with
            the default tenant. But if multi-tenancy is enabled and this field is left blank and no
            tenant is mapped with the asset then containers will not be created.

              

            -   **To enable Multi-Tenancy**

                  

                -   Go to the Administration section and under Product settings, select
                    Multi-tenancy and enable it.

            -   **To map a tenant with asset**

                  

                -   After enabling Multi-tenancy, go to asset configurations, and select the Tenants
                    tab. From the available list of tenants, select the tenant to map with the
                    asset.

        -   **Offense ID -** This field expects a unique offense ID whose details are to be fetched.
            If the value is provided, it will fetch the data for that offense ID irrespective of
            whether it falls in the range of days specified in the \[interval_days\] parameter of
            the app settings.

        -   **Ingest Offense -** This flag if checked, the action ingests all the offense and events
            details. The parameters \[interval_days\] and \[tenant_id\] will be accounted for if the
            \[ingest_offense\] parameter is checked.

          

    -   Alternate Offenses Ingestion Workflow

          

        -   This workflow is considered only if the \[Alternative ingest algorithm for offenses\]
            configuration parameter is checked.
        -   The behavior of this alternate workflow is the same as described in the alternate
            workflow section of the \[List Offenses\] action.

          

    -   Alternate Ariel Query Events Ingestion Workflow

          

        -   This workflow is considered only if the \[Alternative ariel query\] configuration
            parameter is checked.
        -   The behavior of this alternate workflow is the same as described in the alternate
            workflow section of the \[Get Events\] action.

      

-   **Get Flows**

      

    -   **Start Time -** This field expects an epoch value in milliseconds. If not provided, this
        value is internally derived by subtracting the \[interval_days\] from the \[end_time\].
    -   **End Time -** This field expects an epoch value in milliseconds. If not provided, this
        value is equal to the current epoch value in milliseconds.
    -   **Count -** This field expects a valid non-zero integer value or empty value. If provided,
        flows equal to the provided value are fetched. If left empty, default 100 flows matching the
        filter criteria are fetched. If the user wants to fetch all the flows, provide a value
        greater than the total flows that exist on the QRadar server.
    -   **IP -** IP to match against \[Source Destination IP\] and \[Target Destination IP\] for
        fetching all the flows.
    -   **Fields Filter -** This field expects a filter string in the valid AQL query syntax.
    -   **Offense ID -** This field expects a unique offense ID to fetch the flows for.

      

-   **Alt Manage Ingestion**

      

    -   This action provides a provision to alter the state file associated with the corresponding
        asset. For more details, please refer to the specific documentation for this action.
    -   This action does not make any REST call to the QRadar instance. It simply fetches or
        manipulates the state file of the Phantom server for the corresponding asset.
    -   Please change the state file with great care because if the standard format of the state
        file goes wrong, then, all the actions which are dependent on the state file e.g. On Poll,
        Offense Details with \[ingest_offense\] value True will start working incorrectly

      

-   **On Poll**

      

    -   The On Poll action works in 2 steps. In the first step, all the offenses in a defined time
        duration will be fetched. In the second step, all the events of the offenses (retrieved in
        the first step) will be fetched. A container will be created for each offense and for each
        offense all the events will be fetched as the respective artifacts.

    -   The list of offenses will be fetched based on the asset configuration and the app
        configuration parameters configured with the asset. The first step simply calls \[List
        Offenses\] action. Based on the value of the flag \[Alternative ingest algorithm for
        offenses\], the offenses will be fetched either by the default ingestion workflow or by the
        alternative ingestion workflow.

    -   The list of events will be fetched for each offense fetched in the earlier step based on the
        asset configuration and the app configuration parameters configured with the asset. This
        step simply calls \[Get Events\] action. Based on the value of the flag \[Alternative ariel
        query\], the offenses will be fetched either by the default ingestion workflow or by the
        alternative ingestion workflow. For manual polling and the first run of the scheduled \|
        interval polling, the list of events for every offense will be fetched starting from the
        default time of 3600000 epoch milliseconds (1 hour past the 0 epoch) because if we start
        fetching it from 0 epoch, then, the QRadar API throws an error mentioning "Response Code:
        422 and Response Message: The request was well-formed but was unable to be followed due to
        semantic errors. Invalid query parameters: Start time(70-01-01,06:29:59) should be greater
        than one hour since the epoch.". NOTE - If the user's QRadar instance is in America/Los
        Angeles (-08:00 hrs) timezone and for the \[QRadar timezone\] asset configuration parameter,
        the user selects a timezone which is having an offset of \[-08:00 hrs (QRadar instance's
        timezone) + 1 = -07:00 hrs\] or greater, then, the date-time string that gets generated in
        the ariel query will represent a time which is earlier than the allowed time by the QRadar
        ariel query APIs (allowed time is 1 hour past the 0 epoch) for the configured timezone on
        the QRadar instance and it will throw the above-mentioned error. Hence, it is recommended
        that the end-user selects the same timezone in the asset as that configured in the QRadar
        instance to avoid any timezone related issues.

    -   The general structure of the state file : {"app_version":"app_version",
        "last_saved_ingest_time":"epoch_time_last_fetched_offense",
        "last_ingested_events_data":{"offense_id":"epoch_time_last_fetched_event_for_offense_id"}}

          
          

    -   **Two approaches for On Poll**

          

        -   Manual polling

              

            -   Manual polling fetches all the data every time based on the asset and app
                configurations. It is recommended to keep a very high value in \[container_count\]
                and \[artifact_max\] parameters to ensure all the required data gets ingested to
                avoid any data loss.

            -   Fetch the offenses

                  

                -   The application will fetch the number of offenses controlled by the
                    \[container_count\] parameter in \[On Poll\] action.
                -   The application will fetch all the offenses governed by the behavior of the
                    \[List Offenses\] action.
                -   The state file is neither considered nor modified by the manual polling.

            -   Fetch the events

                  

                -   This step will be executed only if the \[containers_only\] configuration
                    parameter is not checked.
                -   The application will fetch all events for each offense (retrieved in the
                    previous step) controlled by the \[artifact_max\] configuration parameter and
                    governed by the behavior of the \[Get Events\] action.

              

        -   Scheduled polling

              

            -   Scheduled polling fetches all the data every time (for the first run only) based on
                the asset and app configurations. It is recommended to keep a very high value in
                \[container_count\] and \[artifact_max\] parameters to ensure all the required data
                gets ingested (in the first run itself and gets in sync with the QRadar current
                state) and avoids any data loss.

            -   It is recommended to keep scheduled polling interval of more than 30 minutes or an
                hour (for the first time so that all the initial offenses and events data get
                ingested quickly and correctly) if the number of events to be ingested is large in
                number (e.g. \> 50,000 events collectively to be ingested for all offenses). The
                reason for doing this is due to the Phantom core's inherent behavior of killing the
                previous scheduled poll or interval poll run if it does not get completed within a
                definite time which is x times (x is internally defined specific to the Phantom
                server) multiple of the current polling interval. e.g. If there are 10 offenses with
                each offense having 5000 events (total 50,000 events), configure the scheduled
                polling for 30 minutes or an hour or more and wait until all the initial data gets
                ingested. Once it is completed, change the polling interval to the required time and
                then, the scheduled polling will work correctly, keeping the Phantom ingested data
                in sync with the QRadar data.

            -   For the consecutive runs, the offenses are fetched starting from the epoch value in
                milliseconds stored in the \[last_saved_ingest_time\] key of the state file.

            -   Fetch the offenses

                  

                -   The application will fetch all the offenses governed by the behavior of the
                    \[List Offenses\] action.
                -   The \[starttime\] or the \[last_updated_time\] of the last offense fetched is
                    stored in the state file against the key \[last_saved_ingest_time\] based on the
                    default or alternate ingestion workflow and the value selected in the
                    \[Alternative ingestion time field\] configuration parameter. If the value
                    selected in the \[Alternative ingestion time field\] configuration parameter is
                    \[either\], then, the maximum of the \[starttime\] or the \[last_updated_time\]
                    for the last fetched offense is stored in the state file.

            -   Fetch the events

                  

                -   This step will be executed only if the \[containers_only\] configuration
                    parameter is not checked.
                -   The application will fetch all events for each offense (retrieved in the
                    previous step) controlled by the \[artifact_max\] configuration parameter and
                    governed by the behavior of the \[Get Events\] action.

**General Notes**

-   Case-sensitive

      

    -   For Assign User, Add Listitem

          

        -   Parameters \[reference_set_name\] for 'add listitem' and \[assignee\] for 'assign user'
            are case sensitive.

      


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
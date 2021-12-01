[comment]: # " File: readme.md"
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

      

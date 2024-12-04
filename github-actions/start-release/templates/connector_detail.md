[comment]: # "Auto-generated SOAR connector documentation"
# {{connector.name}}

Publisher: {{connector.publisher}}  
Connector Version: {{connector.app_version}}  
Product Vendor: {{connector.product_vendor}}  
Product Name: {{connector.product_name}}  
Product Version Supported (regex): "{{connector.product_version_regex}}"  
Minimum Product Version: {{connector.min_phantom_version}}  

{{connector.description}}

{%- if connector.md_content %}

{{connector.md_content | string}}

{%- endif %}

{%- if connector.configuration %}

### Configuration Variables
This table lists the configuration variables required to operare {{connector.name}}. These variables are specified when configuring a {{connector.product_name}} asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
{%- for name, parameters in connector.configuration.items() %}
{%- if name != "ph" and ("visibility" not in parameters or parameters.visibility|length > 0) %}
**{{name}}** | {% if parameters.required == True %} required {% else %} optional {% endif %} | {{ parameters.data_type }} | {{ parameters.description }}
{%- endif %}
{%- endfor %}
{%- endif %}

{%- if connector.actions %}

### Supported Actions
{%- for action in connector.actions %}  
[{{action.action}}](#{{action.action | generate_action_heading_text | generate_gh_fragment}}) - {{action.description}}  
{%- endfor %}

{%- for action in connector.actions %}  

## {{action.action | generate_action_heading_text}}
{{action.description}}

Type: **{{action.type}}**  
Read only: **{{action.read_only}}**  

{%- if action.verbose %}

{{action.verbose}}

{%- endif %}

#### Action Parameters
{%- if action.parameters %}
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
{%- for name, parameters in action.parameters.items() %}
{%- if parameters.data_type != "ph" %}
**{{name}}** | {% if parameters.required == True %} required {% else %} optional {% endif %} | {{parameters.description}} | {{parameters.data_type}} | {% for contain in parameters.contains %} `{{contain}}` {% endfor %}
{%- endif %}
{%- endfor %}
{%- else %}
No parameters are required for this action
{%- endif %}

#### Action Output
{%- if action.output %}
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
{%- for output in action.output %}
{{output.data_path}} | {{output.data_type}} | {% for contain in output.contains %} `{{contain}}` {% endfor %} |  {% for example in output.example_values %} {{example}} {% endfor %}
{%- endfor %}
{%- else %}
No Output
{%- endif %}
{%- endfor %}
{%- endif %}

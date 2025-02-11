# Welcome
This folder contains private semgrep rules defined for connectors in https://github.com/splunk-soar-connectors.
Before updating or adding a rule, make sure to install semgrep:
```
pip install semgrep
```

# Writing Rules
See the Semgrep [getting started](https://semgrep.dev/docs/writing-rules/overview/) and
[pattern syntax](https://semgrep.dev/docs/writing-rules/pattern-syntax/) pages.

# Directory Structure
When writing a new rule, please place its configuration and test file under
`rules/python/category/<rule-file>.yaml` and `rules/python/category/<rule-file>.py` respectively.
Note that the test for a given rule needs to have the same name as the rule's configuration file minus
the file extension (eg, `my-rule.yaml`, `my-rule.py`) for the test to be picked up by Semgrep.

# Running Tests
To test a specific set of rules, run:
```
semgrep --test semgrep/rules/python/category
```

To test all the rules, run:
```
semgrep --test semgrep/rules
```

## Test Annotations
Semgrep provides annotations we can use in our test code to indicate where we are or aren't expecting findings. See https://semgrep.dev/docs/writing-rules/testing-rules/ for more details.

# Running Rules
Semgrep rules are automatically run as part of the pre-commit hooks. The rules will be checked against any modified files in your commits.

To manually run the rules against a connector repo:
```
cd <path_to_connector_repo>
semgrep --config <path_to_dev_cicd_tools>/semgrep/rules
```

# Uploading Private Rules
`upload_private_rules.sh` will upload the rules from every `yaml` file under the `rules` folder
to the Semgrep registry. Note that the rules will only be visible to members of `splunk-soar-connectors`.

To upload a specific ruleset under the path `rules/python/category/ruleset.yaml`:
```
docker pull returntocorp/semgrep-upload:latest
docker run -v "$(pwd)":/temp \
    -e SEMGREP_UPLOAD_DEPLOYMENT="$SEMGREP_DEPLOYMENT_ID" \
    -e SEMGREP_TOKEN="$SEMGREP_TOKEN" \
    returntocorp/semgrep-upload:latest "/temp/rules/python/category/ruleset.yaml"
```

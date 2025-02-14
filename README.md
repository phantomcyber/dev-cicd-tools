# dev-cicd-tools

This repo contains tools and scripts to standardize and simplify CI/CD pipelines and developer experience.

# Note on Usage
The recommended way to use pre-commit is to run `pre-commit install` within your app directory and use `pre-commit run`,
as apps should already include their own pre-commit configuration. However, if you want to use these tools locally you can use as below.

# Local setup
It might be beneficial to clone this repo to be adjacent to your apps folders, though not strictly required:
```
.
├── app1
├── app2
└── dev-cicd-tools
```

To setup your local environment, you need:
- [pre-commit](https://pre-commit.com/)

# Running checks
Most commands expect the path to the app folder you want to check. Take a look at the available hooks in `.pre-commit-hooks.yaml` for the complete list. Some useful commands:
```bash
pre-commit run --config dev-cicd-tools/.pre-commit-hooks.yaml --source /path/to/app1 --all-files
```

# pre-commit
The pre-commit folder contains [pre-commit](https://pre-commit.com/) hooks for SOAR Connector
repos in https://github.com/splunk-soar-connectors. Please refer to https://pre-commit.com/ for
details on authoring and installing hooks.

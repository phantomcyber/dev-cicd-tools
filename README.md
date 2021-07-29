# dev-cicd-tools

This repo contains tools and scripts to standardize and simplify CI/CD pipelines and developer experience.


# Local developer tools setup
Clone this repo to be adjacent to your apps folders:
```
.
├── app1
├── app2
└── dev-cicd-tools
```

To setup your local dev environment, first you need the following pre-requisites:
- [make](https://www.gnu.org/software/make/)
- [python3](https://www.python.org/downloads/)

Once you've installed the pre-requisites, you can run
```
make install
```

# Running developer tools
Most of the targets in the Makefile expect the name of the app folder to operate on, specified with `APP_FOLDER`.

Take a look in the Makefile for the complete list of targets. Some useful commands:
```
make lint APP_FOLDER=app1
make lint-fix APP_FOLDER=app1
```
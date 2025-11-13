<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella Model Explorer

![image](https://github.com/dbinfrago/capella-model-explorer/actions/workflows/build-test-publish.yml/badge.svg)
![image](https://github.com/dbinfrago/capella-model-explorer/actions/workflows/lint.yml/badge.svg)

A webapp for exploring Capella models through simple "auto-generated" textual
and graphical views.

## Longer story

We see a larger non-MBSE crowd struggling with the things hidden in the model.
With this app we expose model contents in an easy to review readable form with
basic graphical annotations. Under the hood it uses Jinja templates enabling
the tooling teams to support their users with model-derived documents of any
shape and form.

## Use cases

- Provide insights into / "spell-out" the model for non-MBSE stakeholders via
  document-a-like dynamic views that describe model elements in a
  human-readable form.

- Provide meaningful default views (that can be further customized) for the key
  elements to kickstart the model exploration.

There are a few more use cases but we will reveal them a bit later.

# Installation

You can install the latest released version directly from PyPI.

```sh
pip install capella-model-explorer
```

## Run the app

The app comes with a command line interface (CLI). Run `cme --help` to get help
or `cme SUBCOMMAND --help` to get help for any subcommand.

```sh
cme run --help
```

When running the app, the used IP address and port are printed to the console.

### Run the app locally

```sh
cme run
```

### Build a Docker image and run the app in a container

```sh
docker build -t capella-model-explorer .
cme run --container --image capella-model-explorer
```

Above will start the app with a sample model which can be found here:
[In-Flight Entertainment System](https://github.com/dbinfrago/Capella-IFE-sample)

Stop the app via CTRL+C.

### Run the app in a container with a custom remote model

```sh
export CME_MODEL='git+https://github.com/dbinfrago/Capella-IFE-sample.git'
export CME_PORT=5000  # optional, default is 8000
cme run --container
```

More information describing what kinds of values can be specified via the
environment variable `CME_MODEL` can be found in [the capellambse
documentation](https://dbinfrago.github.io/py-capellambse/start/specifying-models.html).

### Run the app in a container with a custom local model

If you want to be able to explore a local Capella model, you can mount a local
model into the container.

```bash
export CME_MODEL=/path/on/host/to/model
cme run --container
```

### Run the app in a container and enable live report template editing

If you want to be able to live edit and test local templates, you can mount a
local model and a templates folder into the container. Live template reloading
and rendering will be enabled.

```bash
export CME_TEMPLATES_DIR=$(realpath ./templates)
cme run --container
```

# Integration in the Capella Collaboration Manager

The Capella Model Explorer can be integrated into the [Capella Collaboration
Manager](https://github.com/dbinfrago/capella-collab-manager). Navigate to
`Settings` > `Tools`, then `Add a new tool` with the following configuration:

```yaml
name: Capella model explorer
integrations:
  t4c: false
  pure_variants: false
config:
  resources:
    cpu:
      requests: 0.4
      limits: 2
    memory:
      requests: 1.6Gi
      limits: 6Gi
  environment:
    CME_MODEL:
      stage: before
      value:
        path: "{CAPELLACOLLAB_SESSION_PROVISIONING[0][path]}"
        diagram_cache:
          path: "{CAPELLACOLLAB_SESSION_PROVISIONING[0][diagram_cache]}"
          password: "{CAPELLACOLLAB_SESSION_API_TOKEN}"
          username: "{CAPELLACOLLAB_SESSION_REQUESTER_USERNAME}"
        fallback_render_aird: "true"
    CME_LOG_FILE: /var/log/session/model-explorer.log
    CME_LIVE_MODE: "0"
    CME_ROUTE_PREFIX: "{CAPELLACOLLAB_SESSIONS_BASE_PATH}"
  connection:
    methods:
      - id: f51872a8-1a4f-4a4d-b4f4-b39cbd31a75b
        type: http
        name: Browser connection
        ports:
          metrics: 8000
          http: 8000
        sharing:
          enabled: true
        redirect_url: "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
  monitoring:
    prometheus:
      path: /metrics
    logging:
      enabled: true
  provisioning:
    directory: /models
    max_number_of_models: 1
    required: true
    provide_diagram_cache: true
  persistent_workspaces:
    mounting_enabled: false
  supported_project_types:
    - general
```

You can tune the resources according to your needs.

After saving the configuration, you have to add a version for the new tool.
Since the Capella Model Explorer can load different Capella versions, we can
use one generic version:

```yaml
name: "Generic"
config:
  is_recommended: true
  is_deprecated: false
  sessions:
    persistent:
      image: ghcr.io/dbinfrago/capella-model-explorer/model-explorer:latest
  backups:
    image: null
  compatible_versions: [1, 2, 3, 4]
```

Replace the numbers in `compatible_versions` with the version IDs for the
versions you want to support.

When configured properly, users will be able to start read-only sessions for
the Capella Model Explorer. More information about read-only sessions is
available in the [Capella Collaboration Manager
documentation](https://dbinfrago.github.io/capella-collab-manager/user/sessions/types/read-only/).

# Theme

The app comes with a default light and dark theme and the hue value for the
primary color can be customized via the environment variable
`CME_PRIMARY_COLOR_HUE`. The default hue value is 231 which corresponds to the
purple/blue color used as primary color in the [Capella Collaboration Manager
documentation](https://dbinfrago.github.io/capella-collab-manager).

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a
look at our [guidelines for contributors](CONTRIBUTING.md) for details. It also
contains a short guide on how to set up a local development environment.

# Licenses

This project is compliant with the
[REUSE Specification Version 3.0](https://git.fsfe.org/reuse/docs/src/commit/d173a27231a36e1a2a3af07421f5e557ae0fec46/spec.md).

Copyright DB InfraGO AG, licensed under Apache 2.0 (see full text in
[LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt))

Dot-files are licensed under CC0-1.0 (see full text in
[LICENSES/CC0-1.0.txt](LICENSES/CC0-1.0.txt))

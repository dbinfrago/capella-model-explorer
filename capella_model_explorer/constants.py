# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import importlib.resources as imr
import pathlib
import sys
import typing as t
import uuid

import fasthtml.starlette
from fasthtml import common as fh
from fasthtml import ft

from capella_model_explorer import core

LAUNCH_ID = str(uuid.uuid4())
"""A unique ID that identifies this launch of the model explorer.

This ID is used to invalidate client-side caches when re-launching the
server, in cases where we can't reliably ensure that the model hasn't
changed between launches. Examples include models loaded from local
files (not backed by a Git repository) or remote plain HTTP servers.
"""

CACHE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year

CONFIG = fasthtml.starlette.Config(env_prefix="CME_")


@dataclasses.dataclass
class Defaults:
    docker_image_name: t.Final[str] = "capella-model-explorer:latest"
    host: t.Final[str] = "0.0.0.0"
    live_mode: bool = True
    model: t.Final[str] = (
        "git+https://github.com/DSD-DBS/Capella-IFE-sample.git"
    )
    port: t.Final[int] = 8000
    primary_color_hue: t.Final[int] = 231
    route_prefix: t.Final[str] = ""
    templates_dir: t.Final[pathlib.Path] = pathlib.Path("templates")


DEBUG_SPINNER = CONFIG("DEBUG_SPINNER", cast=bool, default=False)

DOCKER_IMAGE_NAME: str = CONFIG(
    "DOCKER_IMAGE_NAME", default=Defaults.docker_image_name
)
HOST: str = CONFIG("HOST", default=Defaults.host)
MODEL: str = CONFIG("MODEL", default=Defaults.model)
PORT: int = CONFIG("PORT", cast=int, default=Defaults.port)
PRIMARY_COLOR_HUE: int = CONFIG(
    "PRIMARY_COLOR_HUE", cast=int, default=Defaults.primary_color_hue
)
LIVE_MODE: t.Final[bool] = CONFIG(
    "LIVE_MODE", cast=bool, default=Defaults.live_mode
)

ROUTE_PREFIX: t.Final[str] = CONFIG(
    "ROUTE_PREFIX", default=Defaults.route_prefix
).rstrip("/")
TEMPLATES_DIR: t.Final[pathlib.Path] = CONFIG(
    "TEMPLATES_DIR",
    cast=pathlib.Path,
    default=Defaults.templates_dir.resolve(),
).resolve()

css_bundle_path = "static/bundle/app.css"
css_bundle_hash = core.compute_file_hash(css_bundle_path)

favicon_path = "static/favicon.svg"
favicon_hash = core.compute_file_hash(favicon_path)

js_bundle_path = "static/bundle/app.js"
js_bundle_hash = core.compute_file_hash(js_bundle_path)

HEADERS: t.Final[list[fh.Link | ft.Script]] = [
    fh.Link(
        rel="stylesheet",
        href=f"{ROUTE_PREFIX}/{css_bundle_path}?v={css_bundle_hash}",
        type="text/css",
    ),
    fh.Link(
        rel="icon",
        href=f"{ROUTE_PREFIX}/{favicon_path}?v={favicon_hash}",
        type="image/x-icon",
    ),
    ft.Script(
        charset="utf-8",
        src=f"{ROUTE_PREFIX}/{js_bundle_path}?v={js_bundle_hash}",
    ),
    fh.HighlightJS(langs=["python"]),
    ft.Script(
        imr.read_text(__name__.rsplit(".", 1)[0], "inline-dark-mode.js")
    ),
    ft.Style(
        f":root {{ --primary-color-hue: {PRIMARY_COLOR_HUE}; }}\n"
        ":not(:defined) { visibility: hidden; }"
    ),
]
if sys.stderr.isatty():
    LOGGING_COLORS = {
        "CRITICAL": "\x1b[1;31m",  # Bold and red
        "ERROR": "\x1b[31m",  # red
        "WARNING": "\x1b[33m",  # yellow
        "INFO": "\x1b[32m",  # green
        "DEBUG": "\x1b[3;90m",  # Italic and dark gray
        "RESET": "\x1b[m",
    }
else:
    LOGGING_COLORS = {
        "CRITICAL": "",
        "ERROR": "",
        "WARNING": "",
        "INFO": "",
        "DEBUG": "",
        "RESET": "",
    }

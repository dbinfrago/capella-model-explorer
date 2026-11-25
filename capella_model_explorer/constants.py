# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import importlib.resources as imr
import os
import pathlib
import sys
import typing as t
import uuid

import htpy as h

from capella_model_explorer import core

LAUNCH_ID = str(uuid.uuid4())
"A unique ID that identifies this launch of the model explorer.\n\nThis ID is used to invalidate client-side caches when re-launching the\nserver, in cases where we can't reliably ensure that the model hasn't\nchanged between launches. Examples include models loaded from local\nfiles (not backed by a Git repository) or remote plain HTTP servers.\n"
CACHE_MAX_AGE = 365 * 24 * 60 * 60
_T = t.TypeVar("_T")


def _config(name: str, default: _T, cast: t.Callable[[str], _T]) -> _T:
    value = os.getenv(f"CME_{name}")
    if value is None:
        return default
    if cast is bool:
        return t.cast(_T, value.lower() in {"1", "true", "yes", "on"})
    return cast(value)


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


DEBUG_SPINNER: bool = _config("DEBUG_SPINNER", default=False, cast=bool)
DOCKER_IMAGE_NAME: str = _config(
    "DOCKER_IMAGE_NAME", Defaults.docker_image_name, str
)
HOST: str = _config("HOST", Defaults.host, str)
MODEL: str = _config("MODEL", Defaults.model, str)
PORT: int = _config("PORT", Defaults.port, int)
PRIMARY_COLOR_HUE: int = _config(
    "PRIMARY_COLOR_HUE", Defaults.primary_color_hue, int
)
LIVE_MODE: t.Final[bool] = _config("LIVE_MODE", Defaults.live_mode, bool)
ROUTE_PREFIX: t.Final[str] = _config(
    "ROUTE_PREFIX", Defaults.route_prefix, str
).rstrip("/")
TEMPLATES_DIR: t.Final[pathlib.Path] = _config(
    "TEMPLATES_DIR", Defaults.templates_dir.resolve(), pathlib.Path
).resolve()
css_bundle_path = "static/bundle/app.css"
css_bundle_hash = core.compute_file_hash(css_bundle_path)
favicon_path = "static/favicon.svg"
favicon_hash = core.compute_file_hash(favicon_path)
js_bundle_path = "static/bundle/app.js"
js_bundle_hash = core.compute_file_hash(js_bundle_path)
HEADERS: t.Final[list[h.Node]] = [
    h.link(
        rel="stylesheet",
        href=f"{ROUTE_PREFIX}/{css_bundle_path}?v={css_bundle_hash}",
        type="text/css",
    ),
    h.link(
        rel="icon",
        href=f"{ROUTE_PREFIX}/{favicon_path}?v={favicon_hash}",
        type="image/x-icon",
    ),
    h.script(
        charset="utf-8",
        src=f"{ROUTE_PREFIX}/{js_bundle_path}?v={js_bundle_hash}",
    ),
    h.link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css",
    ),
    h.script(
        src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"
    ),
    h.script[imr.read_text(__name__.rsplit(".", 1)[0], "inline-dark-mode.js")],
    h.style[
        f":root {{ --primary-color-hue: {PRIMARY_COLOR_HUE}; }}\n:not(:defined) {{ visibility: hidden; }}"
    ],
]
if sys.stderr.isatty():
    LOGGING_COLORS = {
        "CRITICAL": "\x1b[1;31m",
        "ERROR": "\x1b[31m",
        "WARNING": "\x1b[33m",
        "INFO": "\x1b[32m",
        "DEBUG": "\x1b[3;90m",
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

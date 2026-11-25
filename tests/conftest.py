# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import pathlib
import types
import typing as t

import pytest
from starlette import testclient

from capella_model_explorer import app as app_module
from capella_model_explorer import constants, state


@pytest.fixture
def server(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    tmp_path: pathlib.Path,
) -> t.Iterator[testclient.TestClient]:
    """Run the application with a model stub and no external resources."""
    route_prefix = getattr(request, "param", "")
    templates_dir = tmp_path / "Test"
    templates_dir.mkdir()
    (templates_dir / "index.yaml").write_text(
        "- id: test-report\n"
        "  name: Test report\n"
        "  description: A self-contained test report\n"
        "  template: report.html\n"
        "  single: true\n",
        encoding="utf-8",
    )
    (templates_dir / "report.html").write_text(
        "<h1>{{ model.name }}</h1>", encoding="utf-8"
    )
    model_path = tmp_path / "model.aird"
    model = types.SimpleNamespace(
        name="Test model",
        description_badge='<svg xmlns="http://www.w3.org/2000/svg"/>',
        info=types.SimpleNamespace(capella_version="7.0.0"),
    )
    monkeypatch.setattr(constants, "MODEL", str(model_path))
    monkeypatch.setattr(constants, "ROUTE_PREFIX", route_prefix)
    monkeypatch.setattr(constants, "TEMPLATES_DIR", tmp_path)
    monkeypatch.setattr(
        app_module.capellambse, "loadinfo", lambda _: {"path": model_path}
    )
    monkeypatch.setattr(
        app_module.capellambse, "MelodyModel", lambda **_: model
    )
    monkeypatch.setattr(state, "model", model, raising=False)

    original_templates = state.templates[:]
    original_categories = state.template_categories[:]
    state.templates.clear()
    state.template_categories.clear()

    importlib.reload(app_module)
    try:
        with testclient.TestClient(app_module.app) as client:
            yield client
    finally:
        state.templates[:] = original_templates
        state.template_categories[:] = original_categories
        monkeypatch.undo()
        importlib.reload(app_module)

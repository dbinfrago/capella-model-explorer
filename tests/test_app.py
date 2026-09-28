# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capella_model_explorer import app, constants, state


@pytest.mark.anyio
async def test_router_lifespan(monkeypatch, tmp_path):
    model = object()
    monkeypatch.setattr(constants, "MODEL", str(tmp_path / "model.aird"))
    monkeypatch.setattr(constants, "TEMPLATES_DIR", tmp_path)
    monkeypatch.setattr(
        app.capellambse,
        "loadinfo",
        lambda _: {"path": tmp_path / "model.aird"},
    )
    monkeypatch.setattr(app.capellambse, "MelodyModel", lambda **_: model)
    monkeypatch.setattr(app.reports, "load_templates", lambda: None)

    async with app.app.router.lifespan_context(app.app):
        assert state.model is model


def test_server_starts(server):
    response = server.get("/")

    assert response.status_code == 200


@pytest.mark.parametrize("server", ["/explorer"], indirect=True)
def test_route_prefix_redirects_to_prefixed_home(server):
    response = server.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/explorer/"


@pytest.mark.parametrize("server", ["/explorer"], indirect=True)
def test_route_prefix_is_accepted(server):
    response = server.get("/explorer/")

    assert response.status_code == 200


def test_home_page_renders_basic_content(server):
    response = server.get("/")

    assert response.status_code == 200
    assert "Model Explorer" in response.text
    assert "Reports" in response.text
    assert "Test model" in response.text
    assert "Capella version: 7.0.0" in response.text
    assert "Test report" in response.text


def test_unknown_template_renders_error_content(server):
    response = server.get("/report/does-not-exist")

    assert response.status_code == 200
    assert "Template not found:" in response.text

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

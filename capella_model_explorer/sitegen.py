# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Script to generate static sites based on the model-explorer templates."""

import functools
import importlib
import logging
import os
import pathlib

import asyncclick as click
import capellambse
import capellambse.model as m
import lxml.html as lhtml
import markupsafe
from lxml import etree
from lxml.builder import E

from . import __version__, app, reports, state
from . import constants as c

LOGGER = logging.getLogger(__name__)

GENERIC_TEMPLATE = "__generic__"


@click.command()
@click.version_option(version=__version__)
@click.option(
    "-m",
    "--model",
    envvar="CME_MODEL",
    default=c.Defaults.model,
    show_default=True,
    help="The Capella model to load (file, URL or JSON string).",
)
@click.option(
    "-t",
    "--templates-dir",
    envvar="CME_TEMPLATES_DIR",
    default=str(c.Defaults.templates_dir.resolve()),
    show_default=True,
    help="The directory containing the templates.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    default="./pages",
    show_default=True,
)
@click.argument("template_ids", nargs=-1)
async def main(
    *,
    model: str,
    template_ids: tuple[str, ...],
    templates_dir: str,
    output: pathlib.Path,
) -> None:
    """Statically render a set of templates as standalone HTML pages."""
    logging.basicConfig(level="INFO")

    os.environ["CME_MODEL"] = model
    os.environ["CME_TEMPLATES_DIR"] = templates_dir
    importlib.reload(c)

    async with app.lifespan(...):
        reports.SVG_WRAP_MARKUP = markupsafe.Markup("{svg_data}")
        _render_templates(set(template_ids) - {GENERIC_TEMPLATE}, output)


def _render_templates(tids: set[str], output: pathlib.Path):
    has_generic = any(i.id == GENERIC_TEMPLATE for i in state.templates)
    needed_generic: set[capellambse.helpers.UUIDString] = set()

    def _generate_link(
        obj: m.ModelElement | m.AbstractDiagram, prefix: str = "../"
    ) -> str | None:
        for t in state.templates:
            if t.scope is not None and t.scope.applies_to(obj):
                return f"{prefix}{t.id}/{obj.uuid}"

        assert capellambse.helpers.is_uuid_string(obj.uuid)
        needed_generic.add(obj.uuid)
        if has_generic:
            return f"{prefix}{GENERIC_TEMPLATE}/{obj.uuid}"
        return None

    index_body = E.body(E.h1("List of objects"))
    templates_to_render = [i for i in state.templates if i.id in tids]
    num_templates = len(templates_to_render)
    num_padlen = len(str(num_templates))
    idx_padlen = max(len(i.id) for i in templates_to_render)
    LOGGER.info("Rendering %d templates", num_templates)
    for template_number, template in enumerate(templates_to_render, 1):
        assert template.id != GENERIC_TEMPLATE

        template_path = c.TEMPLATES_DIR.joinpath(template.path)
        j2template = state.jinja_env.from_string(
            template_path.read_text("utf-8")
        )
        tout = output.joinpath(template.id)
        tout.mkdir(parents=True, exist_ok=True)

        index_body.append(E.h2(template.name, E.small(f" ({template.id})")))
        pbar_label = f"[{template_number:{num_padlen}d}/{num_templates:{num_padlen}d}]: {template.id:{idx_padlen}s}"

        if template.single:
            with click.progressbar(length=100, label=pbar_label) as dummybar:
                rendered = j2template.render(
                    object=None,
                    model=state.model,
                    diff_data={},
                    object_diff={},
                )
                rendered = capellambse.helpers.replace_hlinks(
                    rendered, state.model, _generate_link
                )
                tout.joinpath("render.html").write_text(rendered, "utf-8")
                dummybar.update(100)
            index_body.append(
                E.p(
                    E.a(
                        f"View the {template.name!r} template",
                        href=f"{template.id}/render.html",
                    )
                )
            )
            continue

        if not template.instances:
            with click.progressbar(length=100, label=pbar_label) as dummybar:
                dummybar.update(100)
            index_body.append(E.p("No objects use this template."))
            continue

        objs = sorted(
            template.instances,
            key=lambda o: (o["name"], o["uuid"]),
        )
        index_list = E.ul()
        index_body.append(index_list)

        with click.progressbar(
            objs,
            label=pbar_label,
            item_show_func=lambda o: str(getattr(o, "name", "")),
        ) as pbar:
            for objdict in pbar:
                try:
                    obj = state.model.by_uuid(objdict["uuid"])
                    rendered = j2template.render(
                        object=obj,
                        model=state.model,
                        diff_data={},
                        object_diff={},
                    )
                    rendered = capellambse.helpers.replace_hlinks(
                        rendered, state.model, _generate_link
                    )
                    tout.joinpath(f"{obj.uuid}.html").write_text(
                        rendered, "utf-8"
                    )
                except Exception:
                    LOGGER.exception(
                        "Error rendering template %s for %r (%s)",
                        template.id,
                        objdict["name"],
                        objdict["uuid"],
                    )
                else:
                    index_list.append(
                        E.li(*lhtml.fragments_fromstring(obj._short_html_()))
                    )

    del template
    LOGGER.info("Rendering loose objects using generic template")
    idx = GENERIC_TEMPLATE
    generic_template = reports.template_by_id(idx)
    if generic_template is None:
        LOGGER.error("Template %r not found, cannot render loose objects", idx)
    else:
        template_path = c.TEMPLATES_DIR.joinpath(generic_template.path)
        j2template = state.jinja_env.from_string(
            template_path.read_text("utf-8")
        )
        tout = output.joinpath(idx)
        tout.mkdir(parents=True, exist_ok=True)
        rendered_generic: set[capellambse.helpers.UUIDString] = set()

        while needed_generic:
            obj_id = needed_generic.pop()
            if obj_id in rendered_generic:
                continue
            rendered_generic.add(obj_id)

            try:
                rendered = j2template.render(
                    object=state.model.by_uuid(obj_id),
                    model=state.model,
                    diff_data={},
                    object_diff={},
                )
                rendered = capellambse.helpers.replace_hlinks(
                    rendered, state.model, _generate_link
                )
                tout.joinpath(f"{obj_id}.html").write_text(rendered, "utf-8")
            except Exception:
                LOGGER.exception("Error in generic template for %s", obj_id)

    rendered = etree.tostring(E.html(index_body), encoding=str)
    rendered = capellambse.helpers.replace_hlinks(
        rendered, state.model, functools.partial(_generate_link, prefix="")
    )
    output.joinpath("index.html").write_text(rendered, "utf-8")


if __name__ == "__main__":
    main()

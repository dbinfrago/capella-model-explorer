# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import json
import logging
import operator
import pathlib
import re
import traceback
import typing as t

import capellambse
import capellambse.model as m
import capellambse_context_diagrams
import jinja2
import markupsafe
import pydantic as p
import yaml
from lxml import etree
from lxml import html as lxml_html

import capella_model_explorer
import capella_model_explorer.constants as c
from capella_model_explorer import app, core, state

SVG_PLACEHOLDER_MARKUP = markupsafe.Markup(
    '<div class="svg-container relative inline-block cursor-wait px-6 py-4 animate-pulse'
    ' rounded-full bg-primary-500 text-neutral-300 dark:bg-primary-700 dark:text-neutral-400"'
    ' hx-trigger="load" hx-get="{url}" hx-swap="outerHTML" hx-headers="{headers}">'
    "Loading diagram..."
    "</div>"
)

SVG_ERROR_MARKUP = markupsafe.Markup(
    '<div class="svg-container relative inline-block px-6 py-4 w-full rounded-3xl bg-red-500'
    ' text-neutral-300 dark:bg-red-700 dark:text-neutral-400">'
    '<span class="cursor-pointer w-full"'
    " hx-on:click=\"this.nextElementSibling.classList.toggle('hidden')\">"
    "Error rendering diagram (click for details)"
    "</span>"
    '<div class="overflow-auto w-full hidden">'
    '<pre class="mt-2 p-2 text-xs bg-red-800 text-white rounded-md overflow-auto w-full">{traceback}</pre>'
    "</div></div>"
)

SVG_WRAP_MARKUP = markupsafe.Markup(
    '<div class="svg-container relative inline-block cursor-pointer"'
    ' onclick="openDiagramViewer(this)" data-img="{svg_data}">'
    '<img src="{svg_data}" alt="{title}"'
    ' class="transition hover:scale-105 hover:shadow-lg hover:shadow-normal-500/50">'
    "</div>"
)

logger = logging.getLogger(__name__)


class Template(p.BaseModel):
    id: str = p.Field(title="Template identifier")
    name: str = p.Field(title="Template name")
    category: str = p.Field(title="Template category")
    description: str = p.Field(title="Template description")

    scope: TemplateScope | None = p.Field(default=None, title="Template scope")
    single: bool | None = p.Field(None, title="Single instance flag")
    isStable: bool | None = p.Field(None, title="Stable template flag")
    isDocument: bool | None = p.Field(None, title="Document template flag")
    isExperimental: bool | None = p.Field(
        None, title="Experimental template flag"
    )
    path: pathlib.Path = p.Field(title="Absolute file path to template")
    error: str | None = p.Field(None, title="Broken template flag")
    traceback: str | None = p.Field(None, title="Template error traceback")
    instance_count: int = p.Field(0, title="Number of instances")
    instances: list[dict] = p.Field([], title="List of instances")

    def model_post_init(self, _):
        self._compute_instances()

    def _compute_instances(self) -> None:
        if self.single:
            self.instance_count = 1
            return
        try:
            if self.scope is not None:
                self.instances = [
                    self._simple_object(obj)
                    for obj in self._find_objects(
                        obj_type=self.scope.type,
                        below=self.scope.below,
                        attr=None,
                        filters=self.scope.filters,
                    )
                ]
            self.instance_count = len(self.instances)
        except Exception as e:
            self.error = f"Template scope error: {e}"
            self.traceback = traceback.format_exc()

    def _find_objects(
        self, obj_type=None, below=None, attr=None, filters=None
    ):
        if attr:
            getter = operator.attrgetter(attr)
            objects = getter(state.model)
            if hasattr(objects, "_element"):
                objects = [objects]
            elif not isinstance(objects, m.ElementList):
                raise ValueError(
                    f"Expected a list of model objects or a single model object"
                    f" for {attr!r} of the model, got {objects!r}"
                )
        elif below and obj_type:
            getter = operator.attrgetter(below)
            objects = state.model.search(obj_type, below=getter(state.model))
        elif obj_type:
            objects = state.model.search(obj_type)
        else:
            raise ValueError("No search criteria provided")

        if filters:
            filtered = []
            for object in objects:
                for attr_key, filter in filters.items():
                    attr = getattr(object, attr_key)
                    if filter == "not_empty":
                        if attr:
                            filtered.append(object)
                    elif attr == filter:
                        filtered.append(object)
            objects = filtered
        return objects

    def _simple_object(self, obj) -> dict[str, t.Any]:
        if not obj:
            return {}
        if obj.name:
            name = obj.name
        else:
            name = obj.long_name if hasattr(obj, "long_name") else "undefined"

        return {"uuid": obj.uuid, "name": str(name)}


class TemplateScope(p.BaseModel):
    type: str | None = p.Field(None, title="Model Element Type")
    below: t.Literal["oa", "sa", "la", "pa"] | None = p.Field(
        None, title="Model element to search below, scope limiter"
    )
    filters: dict[str, t.Any] | None = p.Field(
        {}, title="Filters to apply to the search"
    )

    def applies_to(self, obj: m.ModelElement | m.AbstractDiagram) -> bool:
        if type(obj).__name__ != self.type:
            return False

        if (
            (self.below == "oa" and obj.layer != obj._model.oa)
            or (self.below == "sa" and obj.layer != obj._model.sa)
            or (self.below == "la" and obj.layer != obj._model.la)
            or (self.below == "pa" and obj.layer != obj._model.pa)
        ):
            return False

        for key, value in (self.filters or {}).items():
            try:
                actual = getattr(obj, key)
            except AttributeError:
                return False
            if actual != value:
                return False

        return True


class TemplateCategory(p.BaseModel):
    idx: str = p.Field(title="Category Identifier")
    templates: list[Template] = p.Field(
        default_factory=list, title="Templates in this category"
    )


def template_by_id(id_: str) -> Template | None:
    for template in state.templates:
        if template.id == id_:
            return template
    return None


def _register_template_category(category: str) -> None:
    state.template_categories.append(
        TemplateCategory(
            idx=category,
            templates=[t for t in state.templates if t.category == category],
        )
    )


def _make_href(
    obj: m.ModelElement | m.AbstractDiagram,
) -> str | None:
    generic_template: Template | None = None
    for template in state.templates:
        if template.path.name.startswith("__generic__"):
            generic_template = template
            continue

        if template.single:
            continue

        if template.scope and not template.scope.applies_to(obj):
            continue

        return app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=obj.uuid,
        )

    if generic_template is None:
        return None
    return app.app.url_path_for(
        "template_page",
        template_id=generic_template.id,
        model_element_uuid=obj.uuid,
    )


def finalize(markup: t.Any) -> object:
    if markup is None:
        return ""

    if isinstance(markup, m.AbstractDiagram):
        logger.warning(
            (
                "Synchronously rendering diagram inline, which is slow"
                " - please update the template to use 'render_diagram()' instead:"
                " %r (%s)"
            ),
            markup.name,
            markup.uuid,
        )
        return render_diagram(markup.render("svg"), markup.name)

    if isinstance(markup, capellambse.diagram.Diagram):
        logger.warning(
            (
                "Placing synchronously rendered diagram inline, which is slow"
                " - please update the template to use 'render_diagram()' instead:"
                " %r (%s)"
            ),
            markup.name,
            markup.uuid,
        )
        svg = m.diagram.convert_format(None, "svg", markup)
        return render_diagram(svg, markup.name)

    markup = markupsafe.escape(markup)
    return capellambse.helpers.replace_hlinks(markup, state.model, _make_href)


def make_href_filter(obj: object) -> str | None:
    if jinja2.is_undefined(obj) or obj is None:
        return "#"

    if isinstance(obj, m.ElementList):
        raise TypeError("Cannot make an href to a list of elements")
    if not isinstance(obj, m.ModelElement | m.AbstractDiagram):
        raise TypeError(f"Expected a model object, got {obj!r}")
    try:
        state.model.by_uuid(obj.uuid)
    except KeyError:
        return "#"
    return _make_href(obj)


def diagram_placeholder(
    parent: capellambse.model.ModelElement,
    attr: str,
    /,
    **kw: t.Any,
) -> t.Any:
    logger.info(
        "Generating diagram placeholder for %r on %r", attr, parent.uuid
    )
    if not isinstance(parent, capellambse.model.ModelElement):
        raise TypeError("Parent object must be a model element")
    if not isinstance(attr, str) or not attr.isidentifier():
        raise TypeError("Attribute must be a Python identifier string")
    try:
        can_find = state.model.by_uuid(parent.uuid) == parent
    except KeyError:
        can_find = False
    if not can_find:
        raise TypeError(f"Cannot find object by its UUID: {parent!r}")

    try:
        diag = getattr(parent, attr)
    except AttributeError:
        raise TypeError(
            f"Parent object ({type(parent).__name__})"
            f" does not have an attribute {attr!r}"
        ) from None
    if not isinstance(diag, capellambse.model.AbstractDiagram):
        raise TypeError(
            f"Expected a diagram at {type(parent).__name__}.{attr},"
            f" got {type(diag).__name__}"
        )

    url = app.app.url_path_for("render_diagram", parent=parent.uuid, attr=attr)
    if kw:
        try:
            params = json.dumps(kw)
        except Exception:
            raise TypeError(
                f"Render parameters must be JSON serializable: {kw!r}"
            ) from None
        url = f"{url}?params={params}"

    render_environment = compute_cache_key(None)
    headers = json.dumps({"Render-Environment": render_environment})

    return SVG_PLACEHOLDER_MARKUP.format(url=url, headers=headers)


def render_diagram(svg: str, title: str, /) -> markupsafe.Markup:
    svg = markupsafe.Markup(
        "data:image/svg+xml;base64,"
        + base64.standard_b64encode(svg.encode("utf-8")).decode("ascii")
    )
    return SVG_WRAP_MARKUP.format(svg_data=svg, title=title)


def load_templates() -> None:
    for idx_path in sorted(c.TEMPLATES_DIR.glob("**/*.yaml")):
        category = re.sub(r"^[A-Za-z0-9]{2}-", "", idx_path.parent.name)
        template_defs = yaml.safe_load(idx_path.read_text(encoding="utf8"))
        for template_def in template_defs:
            template_def["category"] = category
            template_def["path"] = str(
                idx_path.parent / template_def["template"]
            )
            template = Template(**template_def)
            state.templates.append(template)
        _register_template_category(category)


def compute_cache_key(template: Template | None, /) -> str:
    data = {
        "model-explorer-version": capella_model_explorer.__version__,
        "capellambse-version": capellambse.__version__,
        "ctx-diags-version": capellambse_context_diagrams.__version__,
    }
    if template is not None:
        data["template-hash"] = core.compute_file_hash(str(template.path))
    if model_revision := state.model.info.resources["\x00"].rev_hash:
        data["model-revision"] = model_revision
    else:
        data["launch-id"] = c.LAUNCH_ID
    return json.dumps(data)


def process_html_with_toc(html_content: str) -> tuple[str, list[dict]]:
    """Process HTML to extract TOC and inject IDs in a single pass."""
    if not html_content.strip():
        return html_content, []

    try:
        doc = lxml_html.fromstring(html_content)
    except etree.XMLSyntaxError:
        try:
            doc = lxml_html.fragment_fromstring(
                html_content, create_parent=True
            )
        except Exception:
            logger.warning("Cannot parse template result for TOC processing")
            return html_content, []

    toc_items: list[dict[str, t.Any]] = []
    heading_counter: dict[str, int] = {}

    headings = doc.xpath(".//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6")
    assert isinstance(headings, list)

    for heading in headings:
        if not isinstance(heading, lxml_html.HtmlElement):
            continue
        text = heading.text_content().strip()
        if not text:
            continue

        existing_id = heading.get("id", "")

        if not existing_id:
            slug = re.sub(r"[^\w\s-]", "", text.lower())
            slug = re.sub(r"[-\s]+", "-", slug).strip("-")

            if not slug:
                slug = f"heading-{len(toc_items)}"

            count = heading_counter.get(slug, 0)
            heading_counter[slug] = count + 1

            if count > 0:
                slug = f"{slug}-{count}"

            existing_id = slug
            heading.set("id", existing_id)

        assert isinstance(heading.tag, str)
        toc_items.append(
            {
                "level": int(heading.tag[1:]),
                "text": text,
                "id": existing_id,
            }
        )

    processed_html = lxml_html.tostring(doc, encoding="unicode", method="html")
    return processed_html, toc_items

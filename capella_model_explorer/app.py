# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import contextlib
import json
import logging
import pathlib
import tempfile
import time
import traceback
import typing as t

import capellambse
import jinja2
import prometheus_client
import starlette
import starlette.middleware
from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer.constants as c
from capella_model_explorer import components, reports, state

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(_):
    logger.info("Configuration:")
    logger.info("\tRoute prefix: '%s'", c.ROUTE_PREFIX)
    logger.info("\tLive mode: %s", c.LIVE_MODE)
    logger.info("\tHost: '%s'", c.HOST)
    logger.info("\tCapella model: '%s'", c.MODEL)
    logger.info("\tTemplates directory: '%s'", c.TEMPLATES_DIR)

    model_spec = capellambse.loadinfo(c.MODEL)
    logger.info("Loading model from: %s", model_spec["path"])
    state.model = capellambse.MelodyModel(**model_spec)
    logger.info("Loading templates from: %s", c.TEMPLATES_DIR)
    reports.load_templates()
    state.jinja_env = jinja2.Environment(
        autoescape=True,
        loader=jinja2.FileSystemLoader(c.TEMPLATES_DIR),
        lstrip_blocks=True,
        trim_blocks=True,
    )
    state.jinja_env.finalize = reports.finalize
    state.jinja_env.filters["make_href"] = reports.make_href_filter
    state.jinja_env.globals["render_diagram"] = reports.diagram_placeholder
    state.jinja_env.tests["diagram"] = lambda obj: isinstance(
        obj, capellambse.model.AbstractDiagram | capellambse.diagram.Diagram
    )
    state.jinja_env.tests["modelelement"] = lambda obj: isinstance(
        obj, capellambse.model.ModelElement
    )
    yield


class UpdateLastInteractionTimeMiddleware(
    starlette.middleware.base.BaseHTTPMiddleware
):
    async def dispatch(self, request, call_next):
        if request.url.path not in ("/metrics", "/favicon.ico"):
            state.last_interaction = time.time()
        return await call_next(request)


if c.LIVE_MODE:
    _app_cls = fh.FastHTMLWithLiveReload
else:
    _app_cls = fh.FastHTML


app = _app_cls(
    htmx=False,
    hdrs=c.HEADERS,
    key_fname=pathlib.Path(tempfile.gettempdir()) / ".sesskey",
    live=c.LIVE_MODE,
    lifespan=lifespan,
    middleware=[
        starlette.middleware.Middleware(UpdateLastInteractionTimeMiddleware),
    ],
    pico=False,
)
ar = fh.APIRouter(prefix=c.ROUTE_PREFIX)
app.static_route_exts(f"{c.ROUTE_PREFIX}/static", "./static")


@app.get("/metrics")
def metrics() -> t.Any:
    idle_time_minutes = (time.time() - state.last_interaction) / 60
    state.idle_time_gauge.set(idle_time_minutes)
    return fh.Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )


@app.get("/")
def prefix_redirect(request) -> t.Any:
    if c.ROUTE_PREFIX:
        return fh.RedirectResponse(url=app.url_path_for("main_home"))
    return home(request)


@ar.get("/", name="main_home")
def home(request) -> t.Any:
    """Show home/ landing page with all reports in categories."""
    page_content = (
        ft.Div(
            components.model_information(),
            components.reports_page(),
            cls="flex flex-col space-y-4 place-items-center mx-auto mb-4",
        ),
        components.bottom_bar(),
    )
    return _maybe_wrap_content(request, None, None, page_content)


@ar.get("/model-object-list")
def model_object_list(
    template_id: str, selected_model_element_uuid: str = "", search: str = ""
) -> t.Any:
    """Return (filtered) list of model elements for active template."""
    template = reports.template_by_id(template_id)
    assert template is not None
    return components.model_elements_list(
        template=template,
        selected_id=selected_model_element_uuid,
        search=search,
    )


@ar.get("/rendered-report")
def rendered_report(template_id: str, model_element_uuid: str = "") -> t.Any:
    """Render and return report.

    Takes the template and model element from the application state and
    returns the rendered template.
    """
    template = reports.template_by_id(template_id)
    assert template is not None
    model_element = (
        state.model.by_uuid(model_element_uuid) if model_element_uuid else None
    )
    template_content = template.path.read_text(encoding="utf8")
    jinja_template = state.jinja_env.from_string(template_content)
    try:
        rendered_template = jinja_template.render(
            object=model_element,
            model=state.model,
            diff_data={},
            object_diff={},
        )
        processed_html, toc_items = reports.process_html_with_toc(
            rendered_template
        )
    except Exception:
        elem_repr = ""
        try:
            if model_element is not None:
                elem_repr = model_element._short_repr_()
        except Exception:
            pass
        logger.exception(
            "Error rendering template %r with object %s",
            template_id,
            elem_repr or repr(model_element_uuid),
        )

        full_traceback = traceback.format_exc()
        return ft.Div(
            ft.Div("Error rendering template:", cls="text-xl"),
            fh.Pre(
                full_traceback,
                cls="text-xs prose dark:prose-invert",
            ),
            cls="dark:text-neutral-100 grow content-center",
        )

    toc_button_script = "document.getElementById('toc-toggle-button').classList.remove('hidden');"
    content = ft.Div(
        ft.Div(
            fh.NotStr(processed_html),
            cls="prose svg-display dark:prose-invert max-w-4xl w-full",
        ),
        components.table_of_contents(toc_items) if toc_items else None,
        ft.Script(
            "document.getElementById('root').classList.remove('h-screen');"
            "document.getElementById('print-button').classList.remove('hidden');"
            + (toc_button_script * bool(toc_items))
        ),
        cls="flex flex-row w-full",
    )
    return (
        content,
        fh.HttpHeader("Cache-Control", f"max-age={c.CACHE_MAX_AGE}"),
        fh.HttpHeader("Vary", "Render-Environment"),
    )


@ar.get("/report/{template_id}")
@ar.get("/report/{template_id}/{model_element_uuid}")
def template_page(
    request: starlette.requests.Request,
    template_id: str,
    model_element_uuid: str | None = None,
    search: str = "",
) -> t.Any:
    template = reports.template_by_id(template_id)
    if template is None:
        template_path = pathlib.Path(template_id.replace("|", "/"))
        content = ft.Div(
            ft.Div("Template not found:", cls="text-xl"),
            fh.Code(template_path),
            cls="dark:text-neutral-100 grow content-center",
        )
        return _maybe_wrap_content(request, None, None, content)

    if template.single:
        placeholder = components.report_placeholder(template, None)
    elif model_element_uuid:
        placeholder = components.report_placeholder(
            template, model_element_uuid
        )
    elif len(template.instances) == 1:
        return fh.RedirectResponse(
            app.url_path_for(
                "template_page",
                template_id=template.id,
                model_element_uuid=template.instances[0]["uuid"],
            )
        )
    else:
        placeholder = components.report_placeholder(None, None)

    if (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-Target") != "root"
    ):
        return (
            components.template_container(placeholder),
            components.template_sidebar(
                template=template,
                selected_model_element_uuid=model_element_uuid,
                search=search,
                oob=True,
            ),
            components.breadcrumbs(template, model_element_uuid, oob=True),
        )

    page_content = ft.Div(
        components.template_sidebar(
            template=template,
            selected_model_element_uuid=model_element_uuid,
            search=search,
        ),
        components.template_container(placeholder),
        id="template-page-content",
        cls=(
            "flex",
            "flex-col-reverse",
            "justify-between",
            "lg:flex-row",
            "min-h-full",
            "print:bg-white",
            "print:min-h-auto",
            "w-full",
        ),
    )

    if request.headers.get("HX-Request") == "true":
        return (
            page_content,
            components.breadcrumbs(template, model_element_uuid, oob=True),
        )

    return components.application_shell(
        page_content,
        template=template,
        element=model_element_uuid,
    )


def _maybe_wrap_content(
    request: starlette.requests.Request,
    template: reports.Template | None,
    element: str | None,
    content: t.Any,
) -> t.Any:
    if request.headers.get("HX-Request") == "true":
        return content, components.breadcrumbs(template, element, oob=True)
    return components.application_shell(
        content, template=template, element=element
    )


@ar.get("/render")
def render_template(
    template_id: str,
    model_element_uuid: str | None = None,
) -> t.Any:
    """Request the rendering of a template.

    Returns a template container with loading spinner that itself (htmx)
    requests the rendered template and replaces itself with the rendered
    template.
    """
    template = reports.template_by_id(template_id)
    return (
        components.report_placeholder(template, model_element_uuid),
        components.breadcrumbs(template, model_element_uuid, oob=True),
    )


@ar.get("/diagram/{parent}/{attr}")
def render_diagram(
    parent: str,
    attr: str,
    params: str = "",
) -> t.Any:
    """Request the rendering of a diagram."""
    if params:
        dec_params = json.loads(params)
    else:
        dec_params = {}
    del params

    try:
        parent_obj = state.model.by_uuid(parent)
    except KeyError:
        return ft.Div(f"Model element not found: {parent}")
    try:
        diag = getattr(parent_obj, attr)
    except AttributeError:
        return ft.Div(f"Model element does not have attribute {attr!r}")
    if not isinstance(diag, capellambse.model.AbstractDiagram):
        return ft.Div(f"Attribute {attr!r} is not a diagram")

    try:
        rendered = reports.render_diagram(
            diag.render("svg", **dec_params), diag.name
        )
    except Exception:
        logger.exception("Error rendering diagram %r on %r", attr, parent)
        full_traceback = traceback.format_exc()
        rendered = reports.SVG_ERROR_MARKUP.format(traceback=full_traceback)

    return (
        fh.NotStr(rendered),
        fh.HttpHeader("Cache-Control", f"max-age={c.CACHE_MAX_AGE}"),
        fh.HttpHeader("Vary", "Render-Environment"),
    )


ar.to_app(app)

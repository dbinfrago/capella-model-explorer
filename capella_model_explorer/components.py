# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import importlib.resources as imr
import json
import logging
import typing as t

from fasthtml import common as fh
from fasthtml import ft

import capella_model_explorer
from capella_model_explorer import app, icons, reports, state
from capella_model_explorer import constants as c

logger = logging.getLogger(__name__)

GITHUB_URL = "https://github.com/DSD-DBS/capella-model-explorer"


def application_shell(
    *content: t.Any,
    template: reports.Template | None,
    element: str | None,
) -> tuple[ft.Title, ft.Main]:
    return (
        ft.Title(f"{state.model.name} - Model Explorer"),
        ft.Body(
            navbar(template, element),
            ft.Main(
                *content,
                id="root",
                cls="responsive",
            ),
            # placeholder for script injection per outerHTML swap
            ft.Script(id="script"),
            hx_ext="morph",
        ),
    )


def breadcrumbs(
    template: reports.Template | None = None,
    element_id: str | None = None,
    /,
    *,
    oob: bool = False,
) -> ft.Nav:
    components = []

    if template is not None:
        components.append(
            ft.A(
                ft.I("home"),
                cls="button circle transparent",
                href=app.app.url_path_for("main_home"),
                hx_get=app.app.url_path_for("main_home"),
                hx_target="#root",
                hx_push_url="true",
            )
        )

        url = app.app.url_path_for("template_page", template_id=template.id)
        components.append(ft.I("chevron_forward"))
        components.append(
            ft.A(template.name, href=url, cls="button transparent")
        )

    if element_id is not None:
        assert template is not None, "Model element passed without template"
        element = state.model.by_uuid(element_id)
        url = app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=element_id,
        )
        components.append(ft.I("chevron_forward"))
        components.append(
            ft.A(element.name, href=url, cls="button transparent")
        )

    return ft.Nav(
        *components,
        id="breadcrumbs",
        cls="row",
        aria_label="Breadcrumb",
        **({"hx_swap_oob": "true"} if oob else {}),
    )


def model_information() -> ft.Article:
    """Render the model information including the badge."""
    badge = "data:image/svg+xml;base64," + base64.standard_b64encode(
        state.model.description_badge.encode("utf-8")
    ).decode("ascii")
    return ft.Article(
        ft.H4(state.model.name),
        ft.P(f"Capella version: {state.model.info.capella_version}"),
        ft.Img(
            src=badge,
            alt="Model description badge",
            cls="object-scale-down",
        ),
        cls="no-elevate center-align",
    )


def model_object_button(
    *, template: reports.Template, model_element: dict, selected: bool = False
) -> ft.A:
    if state.show_uuids:
        label = ft.Div(
            ft.H6(model_element["name"], cls="small"),
            ft.Div(model_element["uuid"]),
            cls="max",
        )
    else:
        label = ft.H6(model_element["name"], cls="small max")

    url = app.app.url_path_for(
        "template_page",
        template_id=template.id,
        model_element_uuid=model_element["uuid"],
    )

    return ft.A(
        label,
        id=f"model-element-{model_element['uuid']}",
        aria_selected=("false", "true")[selected],
        cls="primary-container" if selected else None,
        href=url,
        hx_get=url,
        hx_push_url="true",
        hx_include='[name="search"]',
        hx_target="#template_container",
    )


def model_elements_list(
    *,
    template: reports.Template,
    selected_id: str | None,
    search: str = "",
) -> ft.Div:
    search_words = search.lower().split()
    model_elements = [
        obj
        for obj in sorted(template.instances, key=lambda x: x["name"])
        if (n := obj["name"].lower()) and all(w in n for w in search_words)
    ]
    return ft.Ul(
        *(
            ft.Li(
                model_object_button(
                    template=template,
                    model_element=model_element,
                    selected=model_element["uuid"] == selected_id,
                )
            )
            for model_element in model_elements
        ),
        id="model_object_list",
        cls="list border scroll",
    )


def navbar(template: reports.Template | None, element: str | None) -> ft.Nav:
    return ft.Header(
        ft.Nav(
            *breadcrumbs(template, element),
            ft.Div(cls="max"),
            ft.Button(
                ft.I("print"),
                onclick="window.print();",
                id="print-button",
                title="Print report",
                cls="hidden border circle",
            ),
            ft.Button(
                ft.I("toc"),
                id="toc-toggle-button",
                title="Toggle table of contents",
                onclick="toggleToc()",
                cls="hidden xl:hidden border circle",
            ),
            ft.Button(
                ft.I("night_sight_auto", id="dark-mode-icon-system"),
                ft.I("dark_mode", id="dark-mode-icon-dark", cls=("hidden",)),
                ft.I("light_mode", id="dark-mode-icon-light", cls=("hidden",)),
                id="dark-mode-button",
                title="Toggle dark mode",
                cls="border circle",
            ),
            id="page-header",
            cls="print:hidden",
        ),
        cls="primary-container",
    )


def report_placeholder(
    template: reports.Template | None,
    model_element_uuid: str | None,
) -> t.Any:
    if template is None:
        ph_content = ft.Div(
            ft.Span(
                "Select a model element.",
                cls="text-slate-600 dark:text-slate-500 p-4 italic m-auto",
            ),
            cls="flex justify-center place-items-center h-full w-full",
        )

    else:
        render_environment = reports.compute_cache_key(template)
        headers = json.dumps({"Render-Environment": render_environment})

        ph_content = ft.Div(
            ft.Div(cls="shape loading-indicator extra"),
            hx_trigger="click" if c.DEBUG_SPINNER else "load",
            hx_get=app.rendered_report.to(
                template_id=template.id,
                model_element_uuid=model_element_uuid,
            ),
            hx_headers=headers,
            hx_target="#template_container",
            cls="flex justify-center place-items-center h-full w-full",
        )

    return ph_content


def reports_page() -> tuple[ft.Article, ...]:
    return tuple(template_category(t) for t in state.template_categories)


def search_field(template: reports.Template, search: str) -> ft.Div:
    search_field_threshold = 3
    return ft.Div(
        ft.Input(
            icons.magnifying_glass(),
            type="search",
            id="instance-search",
            name="search",
            placeholder="Search",
            value=search,
            cls=(
                "-outline-offset-1",
                "bg-white",
                "block",
                "col-start-1",
                "dark:bg-neutral-800",
                "dark:focus:outline-white",
                "dark:text-neutral-400",
                "focus:-outline-offset-2",
                "focus:outline-2",
                "focus:outline-primary-500",
                "grow",
                "outline",
                "outline-1",
                "outline-neutral-300",
                "pl-8",
                "placeholder:text-neutral-400",
                "pr-3",
                "py-1.5",
                "rounded-md",
                "row-start-1",
                "text-neutral-900",
            ),
            hx_trigger="input changed delay:20ms, search",
            hx_get=app.model_object_list.to(
                template_id=template.id,
                selected_model_element_uuid="",
            ),
            hx_swap="outerHTML",
            hx_target="#model_object_list",
            hx_preserve="true",
            autofocus="true",
        ),
        cls=(
            "hidden"
            if template.instance_count <= search_field_threshold
            else "",
            "grid",
            "grid-cols-1",
            "pl-2",
            "pr-4",
        ),
    )


def template_card(
    template: reports.Template,
    *,
    base_color: str = "",
) -> ft.Article:
    url = app.app.url_path_for("template_page", template_id=template.id)

    chips = []
    if reports.TemplateFlags.EXPERIMENTAL in template.flags:
        c = ft.Button(
            ft.I("experiment"),
            ft.Span("Experimental"),
            cls="chip yellow5 black-text no-margin",
        )
        chips.append(c)

    if reports.TemplateFlags.STABLE in template.flags:
        c = ft.Button(
            ft.I("verified_user"),
            ft.Span("Stable"),
            cls=("chip green5 white-text", None if chips else "no-margin"),
        )
        chips.append(c)

    if reports.TemplateFlags.DOCUMENT in template.flags:
        header_icon = ft.Span(
            ft.I("description", cls="white-text"),
            ft.Div("Document", cls="tooltip left"),
        )
    else:
        header_icon = ft.Span(
            ft.I("file_copy", cls="white-text"),
            ft.Div("Multi-element template", cls="tooltip left"),
            ft.Div(template.instance_count, cls="badge tertiary"),
        )

    if base_color:
        bg_color = f"{base_color}2"
        header_color = f"{base_color}9"
    else:
        bg_color = "primary-container"
        header_color = "primary"

    if chips:
        chips_container = ft.Div(
            *chips,
            cls="scroll no-margin medium-padding",
            style="padding-bottom: 0!important",
        )
    else:
        chips_container = None

    return ft.A(
        ft.Article(
            ft.Nav(
                ft.H6(template.name, cls="white-text max"),
                header_icon,
                cls=f"{header_color} no-margin medium-padding small-round",
            ),
            chips_container,
            ft.P(template.description, cls="max no-margin medium-padding"),
            cls=f"{bg_color}",
            style="height: 100%; width: 100%",
        ),
        cls="s12 m6 l4 wave",
        href=url,
        hx_get=url,
        hx_target="#root",
        hx_push_url="true",
    )


def template_category(
    template_category: reports.TemplateCategory,
) -> ft.Article:
    logger.debug(
        "Rendering template category %r (color: %s)",
        template_category.idx,
        template_category.color,
    )
    return ft.Article(
        ft.H5(f"{template_category.idx} Reports", cls="center-align"),
        ft.Div(
            *[
                template_card(template, base_color=template_category.color)
                for template in template_category.templates
            ],
            cls="grid",
        ),
        cls=f"{template_category.color}1" if template_category.color else "",
    )


def template_container(content: t.Any) -> ft.Div:
    return ft.Div(
        content,
        id="template_container",
        cls=(
            "bg-white",
            "dark:bg-neutral-800",
            "dark:border-b",
            "dark:lg:border-l",
            "dark:border-neutral-700",
            "dark:shadow-neutral-700",
            "min-h-full",
            "html-content",
            "flex",
            "items-start",
            "justify-center",
            "p-4",
            "print:bg-white",
            "print:m-0",
            "print:ml-6",
            "print:p-0",
            "svg-display",
            "template-container",
            "w-full",
        ),
    )


def template_sidebar(
    *,
    template: reports.Template,
    selected_model_element_uuid: str | None,
    search: str = "",
    oob: bool = False,
) -> ft.Div:
    sidebar_caption = (
        ft.Div(
            ft.H1(
                template.name,
                cls="text-xl text-neutral-700 dark:text-neutral-400",
            ),
            ft.H2(
                template.description,
                cls="text-sm text-neutral-900 dark:text-neutral-400",
            ),
            cls="mx-2",
        ),
    )
    return ft.Div(
        sidebar_caption,
        search_field(template, search=search),
        model_elements_list(
            template=template,
            selected_id=selected_model_element_uuid,
            search=search,
        ),
        id="template-sidebar",
        cls=(
            "dark:bg-neutral-900",
            "flex",
            "flex-col",
            "h-full",
            "lg:max-h-[calc(100vh-12*var(--spacing))]",
            "lg:w-96",
            "max-h-[calc(0.85*(100vh-12*var(--spacing)))]",
            "pl-4",
            "print:hidden",
            "py-4",
            "rounded-lg",
            "space-y-4",
            "sticky",
            "top-0",
        ),
        hx_swap_oob=oob and "morph",
    )


def table_of_contents(toc_items: list[dict]) -> ft.Div:
    if not toc_items:
        return ft.Div()

    return ft.Div(
        ft.Div(
            ft.H3(
                "Table of Contents",
                cls=(
                    "text-lg",
                    "font-semibold",
                    "text-neutral-800",
                    "dark:text-neutral-300",
                    "mb-3",
                    "px-3",
                    "pt-4",
                    "xl:pt-0",
                ),
            ),
            ft.Nav(
                ft.Ul(
                    *(toc_item(item) for item in toc_items),
                    cls="space-y-1",
                ),
                cls="overflow-y-auto xl:max-h-[calc(100vh-16rem)]",
            ),
            cls="xl:sticky xl:top-4 h-full xl:h-auto",
        ),
        ft.Script(
            imr.read_text(__name__.rsplit(".", 1)[0], "table-of-contents.js")
        ),
        id="table-of-contents",
        cls=(
            "fixed",
            "top-12",
            "right-0",
            "bottom-0",
            "w-80",
            "bg-white",
            "dark:bg-neutral-900",
            "border-l",
            "border-neutral-300",
            "dark:border-neutral-700",
            "shadow-lg",
            "transform",
            "translate-x-full",
            "xl:translate-x-0",
            "transition-transform",
            "duration-300",
            "z-40",
            "overflow-y-auto",
            "pl-4",
            "xl:relative",
            "xl:transform-none",
            "xl:shadow-none",
            "xl:border-none",
            "xl:bg-transparent",
            "xl:dark:bg-transparent",
            "xl:w-80",
            "xl:top-0",
            "xl:overflow-visible",
            "xl:pl-6",
            "shrink-0",
            "print:hidden",
        ),
    )


def toc_item(item: dict) -> ft.Li:
    indent_map = {
        1: "ml-0",
        2: "ml-3",
        3: "ml-6",
        4: "ml-9",
        5: "ml-12",
        6: "ml-15",
    }
    return ft.Li(
        ft.A(
            item["text"],
            href=f"#{item['id']}",
            cls=(
                "block",
                "text-sm",
                "text-neutral-700",
                "dark:text-neutral-400",
                "hover:text-primary-600",
                "dark:hover:text-primary-400",
                "py-1.5",
                "rounded",
                "transition-colors",
                "duration-300",
                "toc-link",
                indent_map[item["level"]],
            ),
            data_target=item["id"],
        ),
    )


def bottom_bar() -> ft.Div:
    """Return container for bottom bar."""
    version = capella_model_explorer.__version__
    if "dev" in version:
        version_element = ft.Span(
            f"Capella-Model-Explorer: v{version}", cls="dark:text-gray-300"
        )
    else:
        version_element = ft.A(
            ft.Span(f"Capella-Model-Explorer: v{version}"),
            href=f"{GITHUB_URL}/releases/v{version}",
            target="_blank",
            cls="hover:underline dark:text-gray-300",
        )

    return ft.Div(
        ft.Span(version_element),
        ft.Div(cls="max"),
        ft.Span(
            ft.A(
                "Contribute on GitHub",
                fh.NotStr("&nbsp;"),
                ft.I(icons.github_logo()),
                href=GITHUB_URL,
                target="_blank",
            ),
        ),
        cls="row",
    )

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import importlib.resources as imr
import json
import typing as t

from fasthtml import ft, svg

import capella_model_explorer
from capella_model_explorer import app, icons, reports, state
from capella_model_explorer import constants as c

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
                cls=(
                    "grow",
                    "w-full",
                    "overflow-y-auto",
                ),
            ),
            # placeholder for script injection per outerHTML swap
            ft.Script(id="script"),
            cls=(
                "bg-neutral-100",
                "dark:bg-neutral-900",
                "flex",
                "flex-col",
                "h-screen",
                "min-h-screen",
                "print:h-auto",
                "print:min-h-auto",
            ),
            hx_ext="morph",
        ),
    )


def breadcrumb(*, label: str, url: str) -> ft.Li:
    return (
        ft.Li(
            ft.Div(
                svg.Svg(
                    svg.Path(d="M.293 0l22 22-22 22h1.414l22-22-22-22H.293z"),
                    viewbox="0 0 24 44",
                    preserveaspectratio="none",
                    aria_hidden="true",
                    cls="h-full w-6 stroke-1 stroke-primary-400 dark:stroke-neutral-700",
                ),
                ft.A(
                    label,
                    href=url,
                    cls=(
                        "dark:hover:text-neutral-100",
                        "dark:text-neutral-400",
                        "font-medium",
                        "ml-4",
                        "hover:text-neutral-50",
                        "text-neutral-300",
                        "text-sm",
                    ),
                ),
                cls="flex items-center",
            ),
            cls="flex",
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
            ft.Li(
                ft.Div(
                    ft.A(
                        icons.home(),
                        ft.Span("Home", cls="sr-only"),
                        href=app.app.url_path_for("main_home"),
                        hx_get=app.app.url_path_for("main_home"),
                        hx_target="#root",
                        hx_push_url="true",
                    ),
                    cls="flex items-center",
                ),
                cls="flex",
            )
        )

        url = app.app.url_path_for("template_page", template_id=template.id)
        components.append(breadcrumb(label=template.name, url=url))

    if element_id is not None:
        assert template is not None, "Model element passed without template"
        element = state.model.by_uuid(element_id)
        url = app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=element_id,
        )
        components.append(breadcrumb(label=element.name, url=url))

    return ft.Nav(
        ft.Ol(
            *components,
            role="list",
            cls="flex space-x-4 rounded-md px-6",
        ),
        id="breadcrumbs",
        aria_label="Breadcrumb",
        cls="flex grow",
        **({"hx_swap_oob": "true"} if oob else {}),
    )


def model_information() -> ft.Div:
    """Render the model information including the badge."""
    badge = "data:image/svg+xml;base64," + base64.standard_b64encode(
        state.model.description_badge.encode("utf-8")
    ).decode("ascii")
    return ft.Div(
        ft.H1(state.model.name, cls="text-xl"),
        ft.P(
            f"Capella version: {state.model.info.capella_version}",
        ),
        ft.Img(
            src=badge,
            alt="Model description badge",
            cls="object-scale-down",
        ),
        cls=(
            "bg-white",
            "dark:bg-neutral-800/50",
            "dark:shadow-none",
            "dark:text-neutral-400",
            "flex",
            "flex-col",
            "max-w-full",
            "m-2",
            "mt-4",
            "p-4",
            "place-items-center",
            "rounded-lg",
            "shadow-primary-500",
            "shadow-xs",
            "svg-display",
            "text-center",
            "text-neutral-700",
        ),
    )


def model_object_button(
    *, template: reports.Template, model_element: dict, selected: bool = False
) -> ft.A:
    return ft.A(
        ft.Div(model_element["name"]),
        ft.Div(model_element["uuid"], cls="text-xs text-sky-700")
        if state.show_uuids
        else None,
        id=f"model-element-{model_element['uuid']}",
        aria_selected="true" if selected else "false",
        cls=(
            "aria-selected:bg-primary-500",
            "aria-selected:dark:hover:bg-primary-500",
            "aria-selected:dark:text-white",
            "aria-selected:text-white",
            "bg-neutral-200",
            "break-words",
            "cursor-pointer",
            "dark:bg-neutral-800",
            "dark:hover:bg-neutral-700",
            "dark:text-neutral-400",
            "duration-300",
            "flex",
            "flex-col",
            "hover:bg-primary-50",
            "hover:scale-[1.02]",
            "model_object_btn",
            "p-4",
            "place-items-left",
            "rounded-md",
            "shadow-sm",
            "text-left",
            "transition",
            "w-full",
        ),
        hx_trigger="click",
        hx_get=app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=model_element["uuid"],
        ),
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
    return ft.Div(
        ft.Div(
            *(
                model_object_button(
                    template=template,
                    model_element=model_element,
                    selected=model_element["uuid"] == selected_id,
                )
                for model_element in model_elements
            ),
            cls="flex flex-col space-y-4 pl-2 pr-4 my-2",
        ),
        id="model_object_list",
        cls="overflow-auto grow",
    )


def navbar(template: reports.Template | None, element: str | None) -> ft.Nav:
    return ft.Nav(
        breadcrumbs(template, element),
        ft.Button(
            icons.printer(),
            onclick="window.print();",
            id="print-button",
            title="Print report",
            cls="hidden cursor-pointer",
        ),
        ft.Button(
            icons.toc_icon(),
            id="toc-toggle-button",
            title="Toggle table of contents",
            onclick="toggleToc()",
            cls="hidden xl:hidden cursor-pointer",
        ),
        ft.Button(
            icons.theme_system(id="dark-mode-icon-system"),
            icons.theme_dark(id="dark-mode-icon-dark", cls=("hidden",)),
            icons.theme_light(id="dark-mode-icon-light", cls=("hidden",)),
            id="dark-mode-button",
            title="Toggle dark mode",
            cls="cursor-pointer",
        ),
        id="page-header",
        cls=(
            "bg-primary-500",
            "dark:bg-neutral-800",
            "dark:border-b",
            "dark:border-neutral-700",
            "flex",
            "gap-2",
            "h-12",
            "min-h-12",
            "max-h-12",
            "px-4",
            "py-0",
            "print:hidden",
            "sticky",
            "top-0",
            "w-full",
            "z-50",
        ),
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
            icons.spinner(),
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


def reports_page() -> ft.Div:
    return ft.Div(
        *(template_category(t) for t in state.template_categories),
        id="reports-index",
        cls=(
            "bg-white",
            "dark:bg-neutral-800/50",
            "dark:shadow-none",
            "flex",
            "flex-col",
            "m-2",
            "p-4",
            "place-items-center",
            "rounded-lg",
            "shadow-primary-500",
            "shadow-xs",
            "space-y-16",
        ),
    )


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


def template_card(template: reports.Template) -> ft.A:
    url = app.app.url_path_for("template_page", template_id=template.id)

    chips = []
    if template.isExperimental:
        c = ft.Div(
            icons.badge_experimental(),
            ft.P("Experimental"),
            cls=(
                "bg-yellow-100",
                "border",
                "border-yellow-800",
                "dark:border-yellow-600",
                "dark:bg-yellow-900",
                "dark:text-yellow-300",
                "flex",
                "flex-row",
                "font-medium",
                "max-h-7",
                "me-2",
                "px-2.5",
                "py-1",
                "rounded-full",
                "space-x-2",
                "text-xs",
                "text-yellow-800",
            ),
        )
        chips.append(c)

    if template.isStable:
        c = ft.Div(
            icons.badge_stable(),
            ft.P("Stable"),
            cls=(
                "bg-green-100",
                "border",
                "border-green-800",
                "dark:bg-green-700",
                "dark:border-green-500",
                "dark:text-green-200",
                "flex",
                "flex-row",
                "font-medium",
                "max-h-7",
                "me-2",
                "px-2.5",
                "py-1",
                "rounded-full",
                "space-x-2",
                "text-green-800",
                "text-xs",
            ),
        )
        chips.append(c)

    if template.isDocument:
        c = ft.Div(
            icons.badge_document(),
            ft.P("Document"),
            cls=(
                "bg-blue-200",
                "border",
                "border-blue-800",
                "dark:bg-blue-700",
                "dark:border-blue-400",
                "dark:text-blue-200",
                "flex",
                "flex-row",
                "font-medium",
                "max-h-7",
                "me-2",
                "px-2.5",
                "py-1",
                "rounded-full",
                "space-x-2",
                "text-blue-800",
                "text-xs",
            ),
        )
        chips.append(c)

    if chips:
        chip_container = ft.Div(
            *chips, cls="flex flex-row grow place-items-end p-4"
        )
    else:
        chip_container = None

    return ft.A(
        ft.Div(
            ft.Div(
                template.name,
                cls="text-neutral-100 dark:text-neutral-400 text-2xl",
            ),
            ft.Div(
                icons.file_stack()
                if template.instance_count > 1
                else icons.report(),
                ft.Span(
                    template.instance_count,
                    cls="hidden" if template.instance_count <= 1 else "block",
                ),
                cls=(
                    "dark:text-neutral-400",
                    "flex",
                    "flex-row",
                    "items-top",
                    "pt-2",
                    "space-x-2",
                    "text-primary-50",
                ),
            ),
            cls=(
                "_template-card-header",
                "bg-primary-500",
                "dark:bg-neutral-900",
                "flex",
                "flex-row",
                "justify-between",
                "p-4",
                "rounded-t-lg",
            ),
        ),
        ft.P(
            template.description,
            cls=(
                "_template-card-description",
                "dark:text-neutral-300",
                "p-4",
                "text-left",
                "text-neutral-800",
            ),
        ),
        chip_container,
        cls=(
            "_template-card",
            "active:border-blue-600",
            "bg-white",
            "dark:bg-neutral-800",
            "dark:hover:bg-neutral-700",
            "dark:shadow-neutral-900",
            "dark:shadow-xs",
            "duration-300",
            "flex",
            "flex-col",
            "hover:bg-primary-50",
            "hover:cursor-pointer",
            "hover:scale-105",
            "m-4",
            "rounded-lg",
            "shadow-lg",
            "transition",
            "w-80",
        ),
        href=url,
        hx_get=url,
        hx_target="#root",
        hx_push_url="true",
    )


def template_category(
    template_category: reports.TemplateCategory,
) -> ft.Div:
    return ft.Div(
        ft.P(
            f"{template_category.idx} Reports",
            cls=(
                "border-b",
                "border-neutral-900",
                "dark:border-neutral-700",
                "dark:text-neutral-400",
                "font-semibold",
                "pb-2",
                "text-2xl",
                "text-center",
                "text-neutral-800",
            ),
        ),
        ft.Div(
            *[
                template_card(template)
                for template in template_category.templates
            ],
            cls=(
                "2xl:grid-cols-4",
                "auto-rows-auto",
                "content-around",
                "grid",
                "grid-flow-row",
                "pt-4",
                (
                    " sm:grid-cols-1"
                    " md:grid-cols-1"
                    " lg:grid-cols-2"
                    " xl:grid-cols-3"
                ),
            ),
        ),
        id="template-category",
        cls="rounded-lg w-full my-2 mx-auto justify-center",
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
        ft.Div(version_element),
        ft.Div(
            ft.A(
                ft.Span("Contribute on GitHub"),
                icons.github_logo(),
                href=GITHUB_URL,
                target="_blank",
                cls="flex items-center gap-2 hover:underline dark:text-gray-300",
            ),
            cls="md:w-fit md:mx-auto",
        ),
        cls="md:grid md:grid-cols-3 w-full px-2 pb-2",
    )

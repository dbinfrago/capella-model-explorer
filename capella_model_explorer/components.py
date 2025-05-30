# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import json
import typing as t

from fasthtml import components as fc
from fasthtml import ft, svg

import capella_model_explorer
from capella_model_explorer import app, icons, reports, state
from capella_model_explorer import constants as c

GITHUB_URL = "https://github.com/DSD-DBS/capella-model-explorer"


def main_layout(
    *content: t.Any,
    sidebar: t.Any,
    template: reports.Template | None,
    element: str | None,
) -> tuple[ft.Title, ft.Main]:
    if sidebar is None:
        sidebar = ft.Div(id="sidebar_container")
    return (
        ft.Title(f"{state.model.name} - Model Explorer"),
        ft.Body(
            fc.Mdui_layout(
                navbar(template, element),
                fc.Mdui_navigation_drawer(
                    sidebar,
                    id="navdrawer",
                    cls="screen:[position:fixed!important] print:hidden",
                    close_on_esc=True,
                    close_on_overlay_click=True,
                ),
                fc.Mdui_layout_main(
                    *content,
                    id="root",
                    cls=("colors-surface-container", "grow", "w-full"),
                ),
                cls="screen:min-h-screen",
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
            "colors-surface",
            "max-w-full",
            "m-2",
            "mt-4",
            "p-4",
            "rounded-lg",
            "text-center",
        ),
    )


def model_elements_list(
    *,
    template: reports.Template,
    selected_id: str | None,
    search: str = "",
):
    search_words = search.lower().split()

    buttons = []
    for obj in sorted(template.instances, key=lambda x: x["name"]):
        n = obj["name"].lower()
        if not all(w in n for w in search_words):
            continue
        button = fc.Mdui_list_item(
            obj["name"],
            (
                ft.Span(obj["uuid"], slot="description")
                if state.show_uuids
                else None
            ),
            id=f"model-element-{obj['uuid']}",
            rounded=True,
            active=obj["uuid"] == selected_id,
            hx_trigger="click",
            hx_get=app.app.url_path_for(
                "template_page",
                template_id=template.id,
                model_element_uuid=obj["uuid"],
            ),
            hx_push_url="true",
            hx_include='[name="search"]',
            hx_target="#template_container",
        )
        buttons.append(button)

    return fc.Mdui_list(*buttons, cls=("overflow-auto", "grow"))


def navbar(template: reports.Template | None, element: str | None) -> ft.Nav:
    if element is not None:
        assert template is not None, "Model element passed without template"
        obj = state.model.by_uuid(element)
        title = fc.Mdui_top_app_bar_title(obj.name)
    elif template is not None:
        title = fc.Mdui_top_app_bar_title(template.name)
    else:
        title = fc.Mdui_top_app_bar_title(state.model.name)

    return fc.Mdui_top_app_bar(
        fc.Mdui_button_icon(
            icon="menu",
            onclick="navdrawer.open = !navdrawer.open",
        ),
        title,
        ft.Div(cls="grow"),
        ft.Div(
            fc.Mdui_button_icon(
                icon="print--outlined",
                onclick="window.print();",
                title="Print report",
            ),
            fc.Mdui_button_icon(
                icon="brightness_auto--outlined",
                id="dark-mode-button",
                title="Toggle dark mode",
            ),
        ),
        id="page-header",
        cls=("[position:fixed!important]", "print:hidden"),
        variant="medium",
        scroll_behavior="shrink elevate",
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
            fc.Mdui_circular_progress(),
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
    categories = []
    for i, cat in enumerate(state.template_categories):
        if i > 0:
            categories.append(fc.Mdui_divider(middle=True))
        categories.append(template_category(cat))
    return ft.Div(
        *categories,
        id="reports-index",
        cls=("colors-surface", "m-2", "p-4", "rounded-lg"),
    )


def search_field(template: reports.Template, search: str) -> ft.Div | None:
    search_field_threshold = 3
    if template.instance_count <= search_field_threshold:
        return None
    return ft.Div(
        fc.Mdui_text_field(
            variant="outlined",
            label="Search",
            id="instance-search",
            name="search",
            value=search,
            icon="search",
            clearable=True,
            hx_trigger="input changed delay:300ms, search",
            hx_get=app.model_object_list.to(
                template_id=template.id,
                selected_model_element_uuid="",
            ),
            hx_swap="outerHTML",
            hx_target="#model_object_list",
            hx_preserve="true",
        ),
        cls=("grid", "grid-cols-1", "pl-2", "pr-4"),
    )


def template_card(template: reports.Template) -> ft.A:
    url = app.app.url_path_for("template_page", template_id=template.id)

    # https://tailwindcss.com/docs/detecting-classes-in-source-files#dynamic-class-names
    colors = ("colors-primary-container", "colors-primary")
    if template.scope:
        if template.scope.below == "oa":
            colors = ("colors-layer-oa-container", "colors-layer-oa")
        elif template.scope.below == "sa":
            colors = ("colors-layer-sa-container", "colors-layer-sa")
        elif template.scope.below == "la":
            colors = ("colors-layer-la-container", "colors-layer-la")
        elif template.scope.below == "pa":
            colors = ("colors-layer-pa-container", "colors-layer-pa")

    chips = []
    if template.isExperimental:
        c = fc.Mdui_chip(
            "Experimental", icon="science", cls="chip-experimental"
        )
        chips.append(c)

    if template.isStable:
        c = fc.Mdui_chip("Stable", icon="gpp_good", cls="chip-stable")
        chips.append(c)

    if template.isDocument:
        c = fc.Mdui_chip("Document", icon="description", cls="chip-document")
        chips.append(c)

    if chips:
        chip_container = ft.Div(
            *chips, cls=("flex", "flex-row", "grow", "place-items-end", "p-4")
        )
    else:
        chip_container = None

    return fc.Mdui_card(
        ft.Div(
            ft.Div(
                ft.Div(template.name, cls=("text-2xl", "grow")),
                fc.Mdui_icon(
                    name="file_copy"
                    if template.instance_count > 1
                    else "description"
                ),
                (
                    ft.Span(template.instance_count, cls="block")
                    if template.instance_count > 1
                    else None
                ),
                cls=("flex", "flex-row", "justify-between", "p-4", colors[1]),
            ),
            ft.P(
                template.description,
                cls=("p-4", "text-left", "grow"),
            ),
            chip_container,
            cls=("h-full", "w-full", "flex", "flex-col"),
        ),
        cls=("m-4", "w-80", colors[0]),
        href=url,
        hx_get=url,
        hx_target="#root",
        hx_push_url="true",
    )


def template_category(category: reports.TemplateCategory) -> ft.Div:
    cards = [template_card(t) for t in category.templates]
    return ft.Div(
        ft.H2(f"{category.idx} Reports"),
        ft.Div(
            *cards,
            cls=(
                "auto-rows-auto",
                "content-around",
                "grid",
                "grid-flow-row",
                "sm:grid-cols-1",
                "md:grid-cols-1",
                "lg:grid-cols-2",
                "xl:grid-cols-3",
                "2xl:grid-cols-4",
                "pt-4",
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
            "html-content",  # copied from v0.2.3
            "items-center",
            "justify-center",
            "p-4",
            "print:bg-white",
            "print:m-0",
            "print:ml-6",
            "print:p-0",
            "svg-display",  # copied from v0.2.3
            "template-container",
            "w-full",
        ),
    )


def template_sidebar(
    *,
    template: reports.Template,
    element_id: str | None,
    search: str = "",
    oob: bool = False,
) -> ft.Div:
    return ft.Div(
        ft.Div(
            ft.H1(template.name, cls="text-xl"),
            ft.P(template.description, cls="text-sm"),
            cls="mx-2",
        ),
        search_field(template, search=search),
        model_elements_list(
            template=template,
            selected_id=element_id,
            search=search,
        ),
        id="sidebar_container",
        cls="relative max-h-screen",
        hx_swap_oob=oob and "morph",
    )


def bottom_bar() -> ft.Div:
    """Return container for bottom bar."""
    version = capella_model_explorer.__version__
    if "dev" in version:
        version_element = ft.Span(f"Capella-Model-Explorer: v{version}")
    else:
        version_element = ft.A(
            ft.Span(f"Capella-Model-Explorer: v{version}"),
            href=f"{GITHUB_URL}/releases/v{version}",
            target="_blank",
            cls="hover:underline",
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
        cls="md:grid md:grid-cols-3 px-2 pb-2",
    )

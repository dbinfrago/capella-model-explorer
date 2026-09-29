# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import importlib.resources as imr
import json
import typing as t

import htpy as h

import capella_model_explorer
from capella_model_explorer import app, icons, reports, state
from capella_model_explorer import constants as c

Node = h.Node
path = h.Element("path")
GITHUB_URL = "https://github.com/DSD-DBS/capella-model-explorer"


def application_shell(
    *content: t.Any, template: reports.Template | None, element: str | None
) -> tuple[Node, Node]:
    return (
        h.title[f"{state.model.name} - Model Explorer"],
        h.body(
            ".bg-neutral-100.dark:bg-neutral-900.flex.flex-col.h-screen.min-h-screen.print:h-auto.print:min-h-auto",
            hx_ext="morph",
        )[
            navbar(template, element),
            h.main("#root.grow.w-full.overflow-y-auto")[*content],
            h.script("#script"),
        ],
    )


def breadcrumb(*, label: str, url: str) -> Node:
    return (
        h.li(".flex")[
            h.div(".flex.items-center")[
                h.svg(
                    ".h-full.w-6.stroke-1.stroke-primary-400.dark:stroke-neutral-700",
                    viewbox="0 0 24 44",
                    preserveaspectratio="none",
                    aria_hidden="true",
                )[path(d="M.293 0l22 22-22 22h1.414l22-22-22-22H.293z")],
                h.a(
                    ".dark:hover:text-neutral-100.dark:text-neutral-400.font-medium.ml-4.hover:text-neutral-50.text-neutral-300.text-sm",
                    href=url,
                )[label],
            ],
        ],
    )


def breadcrumbs(
    template: reports.Template | None = None,
    element_id: str | None = None,
    /,
    *,
    oob: bool = False,
) -> Node:
    components: list[Node] = []
    if template is not None:
        components.append(
            h.li(".flex")[
                h.div(".flex.items-center")[
                    h.a(
                        href=app.app.url_path_for("main_home"),
                        hx_get=app.app.url_path_for("main_home"),
                        hx_target="#root",
                        hx_push_url="true",
                    )[icons.home(), h.span(".sr-only")["Home"]],
                ],
            ]
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
    return h.nav(
        "#breadcrumbs.flex.grow",
        aria_label="Breadcrumb",
        **({"hx_swap_oob": "true"} if oob else {}),
    )[h.ol(".flex.space-x-4.rounded-md.px-6", role="list")[*components]]


def model_information() -> Node:
    """Render the model information including the badge."""
    badge = "data:image/svg+xml;base64," + base64.standard_b64encode(
        state.model.description_badge.encode("utf-8")
    ).decode("ascii")
    return h.div(
        ".bg-white.dark:bg-neutral-800/50.dark:shadow-none.dark:text-neutral-400.flex.flex-col.max-w-full.m-2.mt-4.p-4.place-items-center.rounded-lg.shadow-primary-500.shadow-xs.svg-display.text-center.text-neutral-700"
    )[
        h.h1(".text-xl")[state.model.name],
        h.p[f"Capella version: {state.model.info.capella_version}"],
        h.img(".object-scale-down", src=badge, alt="Model description badge"),
    ]


def model_object_button(
    *, template: reports.Template, model_element: dict, selected: bool = False
) -> Node:
    return h.a(
        ".aria-selected:bg-primary-500.aria-selected:dark:hover:bg-primary-500.aria-selected:dark:text-white.aria-selected:text-white.bg-neutral-200.break-words.cursor-pointer.dark:bg-neutral-800.dark:hover:bg-neutral-700.dark:text-neutral-400.duration-300.flex.flex-col.hover:bg-primary-50.hover:scale-[1.02].model_object_btn.p-4.place-items-left.rounded-md.shadow-sm.text-left.transition.w-full",
        id=f"model-element-{model_element['uuid']}",
        aria_selected="true" if selected else "false",
        hx_trigger="click",
        hx_get=app.app.url_path_for(
            "template_page",
            template_id=template.id,
            model_element_uuid=model_element["uuid"],
        ),
        hx_push_url="true",
        hx_include='[name="search"]',
        hx_target="#template_container",
    )[
        h.div[model_element["name"]],
        h.div(".text-xs.text-sky-700")[model_element["uuid"]]
        if state.show_uuids
        else None,
    ]


def model_elements_list(
    *, template: reports.Template, selected_id: str | None, search: str = ""
) -> Node:
    search_words = search.lower().split()
    model_elements = [
        obj
        for obj in sorted(template.instances, key=lambda x: x["name"])
        if (n := obj["name"].lower()) and all(w in n for w in search_words)
    ]
    return h.div("#model_object_list.overflow-auto.grow")[
        h.div(".flex.flex-col.space-y-4.pl-2.pr-4.my-2")[
            *(
                model_object_button(
                    template=template,
                    model_element=model_element,
                    selected=model_element["uuid"] == selected_id,
                )
                for model_element in model_elements
            ),
        ],
    ]


def navbar(template: reports.Template | None, element: str | None) -> Node:
    return h.nav(
        "#page-header.bg-primary-500.dark:bg-neutral-800.dark:border-b.dark:border-neutral-700.flex.gap-2.h-12.min-h-12.max-h-12.px-4.py-0.print:hidden.sticky.top-0.w-full.z-50"
    )[
        breadcrumbs(template, element),
        h.button(
            "#print-button.hidden.cursor-pointer",
            onclick="window.print();",
            title="Print report",
        )[icons.printer()],
        h.button(
            "#toc-toggle-button.hidden.xl:hidden.cursor-pointer",
            title="Toggle table of contents",
            onclick="toggleToc()",
        )[icons.toc_icon()],
        h.button("#dark-mode-button.cursor-pointer", title="Toggle dark mode")[
            icons.theme_system(id="dark-mode-icon-system"),
            icons.theme_dark(id="dark-mode-icon-dark", cls=("hidden",)),
            icons.theme_light(id="dark-mode-icon-light", cls=("hidden",)),
        ],
    ]


def report_placeholder(
    template: reports.Template | None, model_element_uuid: str | None
) -> Node:
    if template is None:
        ph_content = h.div(
            ".flex.justify-center.place-items-center.h-full.w-full"
        )[
            h.span(".text-slate-600.dark:text-slate-500.p-4.italic.m-auto")[
                "Select a model element.",
            ],
        ]
    else:
        render_environment = reports.compute_cache_key(template)
        headers = json.dumps({"Render-Environment": render_environment})
        ph_content = h.div(
            ".flex.justify-center.place-items-center.h-full.w-full",
            hx_trigger="click" if c.DEBUG_SPINNER else "load",
            hx_get=app.url_for(
                "rendered_report",
                template_id=template.id,
                model_element_uuid=model_element_uuid or "",
            ),
            hx_headers=headers,
            hx_target="#template_container",
        )[icons.spinner()]
    return ph_content


def reports_page() -> Node:
    return h.div(
        "#reports-index.bg-white.dark:bg-neutral-800/50.dark:shadow-none.flex.flex-col.m-2.p-4.place-items-center.rounded-lg.shadow-primary-500.shadow-xs.space-y-16"
    )[*(template_category(t) for t in state.template_categories)]


def search_field(template: reports.Template, search: str) -> Node:
    search_field_threshold = 3
    return h.div(
        class_=(
            "hidden"
            if template.instance_count <= search_field_threshold
            else "",
            "grid",
            "grid-cols-1",
            "pl-2",
            "pr-4",
        )
    )[
        h.input(
            "#instance-search.-outline-offset-1.bg-white.block.col-start-1.dark:bg-neutral-800.dark:focus:outline-white.dark:text-neutral-400.focus:-outline-offset-2.focus:outline-2.focus:outline-primary-500.grow.outline.outline-1.outline-neutral-300.pl-8.placeholder:text-neutral-400.pr-3.py-1.5.rounded-md.row-start-1.text-neutral-900",
            type="search",
            name="search",
            placeholder="Search",
            value=search,
            hx_trigger="input changed delay:20ms, search",
            hx_get=app.url_for(
                "model_object_list",
                template_id=template.id,
                selected_model_element_uuid="",
            ),
            hx_swap="outerHTML",
            hx_target="#model_object_list",
            hx_preserve="true",
            autofocus="true",
        ),
    ]


def template_card(template: reports.Template) -> Node:
    url = app.app.url_path_for("template_page", template_id=template.id)
    chips = []
    if template.isExperimental:
        c = h.div(
            ".bg-yellow-100.border.border-yellow-800.dark:border-yellow-600.dark:bg-yellow-900.dark:text-yellow-300.flex.flex-row.font-medium.max-h-7.me-2.px-2.5.py-1.rounded-full.space-x-2.text-xs.text-yellow-800"
        )[icons.badge_experimental(), h.p["Experimental"]]
        chips.append(c)
    if template.isStable:
        c = h.div(
            ".bg-green-100.border.border-green-800.dark:bg-green-700.dark:border-green-500.dark:text-green-200.flex.flex-row.font-medium.max-h-7.me-2.px-2.5.py-1.rounded-full.space-x-2.text-green-800.text-xs"
        )[icons.badge_stable(), h.p["Stable"]]
        chips.append(c)
    if template.isDocument:
        c = h.div(
            ".bg-blue-200.border.border-blue-800.dark:bg-blue-700.dark:border-blue-400.dark:text-blue-200.flex.flex-row.font-medium.max-h-7.me-2.px-2.5.py-1.rounded-full.space-x-2.text-blue-800.text-xs"
        )[icons.badge_document(), h.p["Document"]]
        chips.append(c)
    if chips:
        chip_container = h.div(".flex.flex-row.grow.place-items-end.p-4")[
            *chips,
        ]
    else:
        chip_container = None
    return h.a(
        "._template-card.active:border-blue-600.bg-white.dark:bg-neutral-800.dark:hover:bg-neutral-700.dark:shadow-neutral-900.dark:shadow-xs.duration-300.flex.flex-col.hover:bg-primary-50.hover:cursor-pointer.hover:scale-105.m-4.rounded-lg.shadow-lg.transition.w-80",
        href=url,
        hx_get=url,
        hx_target="#root",
        hx_push_url="true",
    )[
        h.div(
            "._template-card-header.bg-primary-500.dark:bg-neutral-900.flex.flex-row.justify-between.p-4.rounded-t-lg"
        )[
            h.div(".text-neutral-100.dark:text-neutral-400.text-2xl")[
                template.name,
            ],
            h.div(
                ".dark:text-neutral-400.flex.flex-row.items-top.pt-2.space-x-2.text-primary-50"
            )[
                icons.file_stack()
                if template.instance_count > 1
                else icons.report(),
                h.span(
                    class_="hidden"
                    if template.instance_count <= 1
                    else "block"
                )[template.instance_count],
            ],
        ],
        h.p(
            "._template-card-description.dark:text-neutral-300.p-4.text-left.text-neutral-800"
        )[template.description],
        chip_container,
    ]


def template_category(template_category: reports.TemplateCategory) -> Node:
    return h.div(
        "#template-category.rounded-lg.w-full.my-2.mx-auto.justify-center"
    )[
        h.p(
            ".border-b.border-neutral-900.dark:border-neutral-700.dark:text-neutral-400.font-semibold.pb-2.text-2xl.text-center.text-neutral-800"
        )[f"{template_category.idx} Reports"],
        h.div(
            ".2xl:grid-cols-4.auto-rows-auto.content-around.grid.grid-cols-1.lg:grid-cols-2.xl:grid-cols-3.grid-flow-row.pt-4"
        )[
            *[
                template_card(template)
                for template in template_category.templates
            ],
        ],
    ]


def template_container(content: Node) -> Node:
    return h.div(
        "#template_container.bg-white.dark:bg-neutral-800.dark:border-b.dark:lg:border-l.dark:border-neutral-700.dark:shadow-neutral-700.min-h-full.html-content.flex.items-start.justify-center.p-4.print:bg-white.print:m-0.print:ml-6.print:p-0.svg-display.template-container.w-full"
    )[content]


def template_sidebar(
    *,
    template: reports.Template,
    selected_model_element_uuid: str | None,
    search: str = "",
    oob: bool = False,
) -> Node:
    sidebar_caption = (
        h.div(".mx-2")[
            h.h1(".text-xl.text-neutral-700.dark:text-neutral-400")[
                template.name,
            ],
            h.h2(".text-sm.text-neutral-900.dark:text-neutral-400")[
                template.description,
            ],
        ],
    )
    return h.div(
        "#template-sidebar.dark:bg-neutral-900.flex.flex-col.h-full.lg:max-h-[calc(100vh-12*var(--spacing))].lg:w-96.max-h-[calc(0.85*(100vh-12*var(--spacing)))].pl-4.print:hidden.py-4.rounded-lg.space-y-4.sticky.top-0",
        hx_swap_oob=oob and "morph",
    )[
        sidebar_caption,
        search_field(template, search=search),
        model_elements_list(
            template=template,
            selected_id=selected_model_element_uuid,
            search=search,
        ),
    ]


def table_of_contents(toc_items: list[dict[str, t.Any]]) -> Node:
    if not toc_items:
        return h.div
    return h.div(
        "#table-of-contents.fixed.top-12.right-0.bottom-0.w-80.bg-white.dark:bg-neutral-900.border-l.border-neutral-300.dark:border-neutral-700.shadow-lg.transform.translate-x-full.xl:translate-x-0.transition-transform.duration-300.z-40.overflow-y-auto.pl-4.xl:relative.xl:transform-none.xl:shadow-none.xl:border-none.xl:bg-transparent.xl:dark:bg-transparent.xl:w-80.xl:top-0.xl:overflow-visible.xl:pl-6.shrink-0.print:hidden"
    )[
        h.div(".xl:sticky.xl:top-4.h-full.xl:h-auto")[
            h.h3(
                ".text-lg.font-semibold.text-neutral-800.dark:text-neutral-300.mb-3.px-3.pt-4.xl:pt-0"
            )["Table of Contents"],
            h.nav(".overflow-y-auto.xl:max-h-[calc(100vh-16rem)]")[
                h.ul(".space-y-1")[*(toc_item(item) for item in toc_items)],
            ],
        ],
        h.script[
            imr.read_text(__name__.rsplit(".", 1)[0], "table-of-contents.js"),
        ],
    ]


def toc_item(item: dict[str, t.Any]) -> Node:
    indent_map = {
        1: "ml-0",
        2: "ml-3",
        3: "ml-6",
        4: "ml-9",
        5: "ml-12",
        6: "ml-15",
    }
    return h.li[
        h.a(
            href=f"#{item['id']}",
            class_=(
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
        )[item["text"]],
    ]


def bottom_bar() -> Node:
    """Return container for bottom bar."""
    version = capella_model_explorer.__version__
    if "dev" in version:
        version_element = h.span(".dark:text-gray-300")[
            f"Capella-Model-Explorer: v{version}",
        ]
    else:
        version_element = h.a(
            ".hover:underline.dark:text-gray-300",
            href=f"{GITHUB_URL}/releases/v{version}",
            target="_blank",
        )[h.span[f"Capella-Model-Explorer: v{version}"]]
    return h.div(".md:grid.md:grid-cols-3.w-full.px-2.pb-2")[
        h.div[version_element],
        h.div(".md:w-fit.md:mx-auto")[
            h.a(
                ".flex.items-center.gap-2.hover:underline.dark:text-gray-300",
                href=GITHUB_URL,
                target="_blank",
            )[h.span["Contribute on GitHub"], icons.github_logo()],
        ],
    ]

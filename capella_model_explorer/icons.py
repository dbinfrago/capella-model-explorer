# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fasthtml import svg


def github_logo() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d=(
                "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 "
                "11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04 "
                "-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 "
                "3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 "
                "1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108 "
                "-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 "
                "0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 "
                "0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 "
                "1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285 "
                "-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 "
                "3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 "
                "2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825 "
                ".57C20.565 22.092 24 17.592 24 12.297c0-6.627 "
                "-5.373-12-12-12"
            ),
        ),
        viewBox="0 0 24 24",
        cls="hover:animate-spin",
    )


def home() -> svg.Svg:
    return svg.Svg(
        svg.Path(d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"),
        svg.Path(
            d=(
                "M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 "
                "5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
            )
        ),
        width="24",
        height="24",
        viewbox="0 0 24 24",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
        cls=(
            "dark:hover:stroke-neutral-100",
            "dark:stroke-neutral-400",
            "fill-none",
            "hover:stroke-neutral-50",
            "stroke-neutral-300",
        ),
    )


def magnifying_glass() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            fill_rule="evenodd",
            d=(
                "M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7 "
                "7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06 "
                "1.06l-3.329-3.328A7 7 0 0 1 2 9Z"
            ),
            clip_rule="evenodd",
        ),
        viewBox="0 0 20 20",
        fill="currentColor",
        aria_hidden="true",
        data_slot="icon",
        cls=(
            "pointer-events-none col-start-1 row-start-1 ml-3 size-5 "
            "self-center text-neutral-400"
        ),
    )


def spinner() -> svg.Svg:
    return svg.Svg(
        svg.Circle(
            cx="12",
            cy="12",
            r="10",
            stroke_width="4",
            cls=("opacity-25", "stroke-primary-500"),
        ),
        svg.Path(
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z",
            cls=("opacity-100", "fill-primary-500"),
        ),
        xmlns="http://www.w3.org/2000/svg",
        fill="none",
        viewbox="0 0 24 24",
        cls=(
            "animate-spin",
            "size-15",
        ),
    )

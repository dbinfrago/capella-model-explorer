# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fasthtml import svg


def github_logo() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d=(
                "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205"
                " 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04"
                "-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7"
                " 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838"
                " 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108"
                "-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93"
                " 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176"
                " 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405"
                " 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285"
                "-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23"
                " 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81"
                " 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825"
                ".57C20.565 22.092 24 17.592 24 12.297c0-6.627"
                "-5.373-12-12-12"
            ),
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        fill="currentColor",
        cls="hover:animate-spin",
    )


def home() -> svg.Svg:
    return svg.Svg(
        svg.Path(d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"),
        svg.Path(
            d=(
                "M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7"
                " 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
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


def badge_document() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def badge_experimental() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2",
        ),
        svg.Path(
            d="M8.5 2h7",
        ),
        svg.Path(
            d="M7 16h10",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def badge_stable() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",
        ),
        svg.Path(
            d="m9 12 2 2 4-4",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def file_stack() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M21 7h-3a2 2 0 0 1-2-2V2",
        ),
        svg.Path(
            d="M21 6v6.5c0 .8-.7 1.5-1.5 1.5h-7c-.8 0-1.5-.7-1.5-1.5v-9c0-.8.7-1.5 1.5-1.5H17Z",
        ),
        svg.Path(
            d="M7 8v8.8c0 .3.2.6.4.8.2.2.5.4.8.4H15",
        ),
        svg.Path(
            d="M3 12v8.8c0 .3.2.6.4.8.2.2.5.4.8.4H11",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def theme_system(
    *,
    id: str | None = None,
    cls: tuple[str, ...] = (),
) -> svg.Svg:
    """Return the 'theme-light-dark' Material Design Icon."""
    return svg.Svg(
        svg.Path(
            d="M7.5,2C5.71,3.15 4.5,5.18 4.5,7.5C4.5,9.82 5.71,11.85 7.53,13C4.46,13 2,10.54 2,7.5A5.5,5.5 0 0,1 7.5,2M19.07,3.5L20.5,4.93L4.93,20.5L3.5,19.07L19.07,3.5M12.89,5.93L11.41,5L9.97,6L10.39,4.3L9,3.24L10.75,3.12L11.33,1.47L12,3.1L13.73,3.13L12.38,4.26L12.89,5.93M9.59,9.54L8.43,8.81L7.31,9.59L7.65,8.27L6.56,7.44L7.92,7.35L8.37,6.06L8.88,7.33L10.24,7.36L9.19,8.23L9.59,9.54M19,13.5A5.5,5.5 0 0,1 13.5,19C12.28,19 11.15,18.6 10.24,17.93L17.93,10.24C18.6,11.15 19,12.28 19,13.5M14.6,20.08L17.37,18.93L17.13,22.28L14.6,20.08M18.93,17.38L20.08,14.61L22.28,17.15L18.93,17.38M20.08,12.42L18.94,9.64L22.28,9.88L20.08,12.42M9.63,18.93L12.4,20.08L9.87,22.27L9.63,18.93Z"
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        cls=(
            "dark:hover:fill-neutral-100",
            "dark:fill-neutral-400",
            "hover:fill-neutral-50",
            "fill-neutral-300",
            *cls,
        ),
        id=id,
    )


def theme_dark(
    *,
    id: str | None = None,
    cls: tuple[str, ...] = (),
) -> svg.Svg:
    """Return the 'weather-night' Material Design Icon."""
    return svg.Svg(
        svg.Path(
            d="M17.75,4.09L15.22,6.03L16.13,9.09L13.5,7.28L10.87,9.09L11.78,6.03L9.25,4.09L12.44,4L13.5,1L14.56,4L17.75,4.09M21.25,11L19.61,12.25L20.2,14.23L18.5,13.06L16.8,14.23L17.39,12.25L15.75,11L17.81,10.95L18.5,9L19.19,10.95L21.25,11M18.97,15.95C19.8,15.87 20.69,17.05 20.16,17.8C19.84,18.25 19.5,18.67 19.08,19.07C15.17,23 8.84,23 4.94,19.07C1.03,15.17 1.03,8.83 4.94,4.93C5.34,4.53 5.76,4.17 6.21,3.85C6.96,3.32 8.14,4.21 8.06,5.04C7.79,7.9 8.75,10.87 10.95,13.06C13.14,15.26 16.1,16.22 18.97,15.95M17.33,17.97C14.5,17.81 11.7,16.64 9.53,14.5C7.36,12.31 6.2,9.5 6.04,6.68C3.23,9.82 3.34,14.64 6.35,17.66C9.37,20.67 14.19,20.78 17.33,17.97Z",
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        cls=(
            "dark:hover:fill-neutral-100",
            "dark:fill-neutral-400",
            "hover:fill-neutral-50",
            "fill-neutral-300",
            *cls,
        ),
        id=id,
    )


def theme_light(
    *,
    id: str | None = None,
    cls: tuple[str, ...] = (),
) -> svg.Svg:
    """Return the 'weather-sunny' Material Design Icon."""
    return svg.Svg(
        svg.Path(
            d="M12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,2L14.39,5.42C13.65,5.15 12.84,5 12,5C11.16,5 10.35,5.15 9.61,5.42L12,2M3.34,7L7.5,6.65C6.9,7.16 6.36,7.78 5.94,8.5C5.5,9.24 5.25,10 5.11,10.79L3.34,7M3.36,17L5.12,13.23C5.26,14 5.53,14.78 5.95,15.5C6.37,16.24 6.91,16.86 7.5,17.37L3.36,17M20.65,7L18.88,10.79C18.74,10 18.47,9.23 18.05,8.5C17.63,7.78 17.1,7.15 16.5,6.64L20.65,7M20.64,17L16.5,17.36C17.09,16.85 17.62,16.22 18.04,15.5C18.46,14.77 18.73,14 18.87,13.21L20.64,17M12,22L9.59,18.56C10.33,18.83 11.14,19 12,19C12.82,19 13.63,18.83 14.37,18.56L12,22Z"
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        cls=(
            "dark:hover:fill-neutral-100",
            "dark:fill-neutral-400",
            "hover:fill-neutral-50",
            "fill-neutral-300",
            *cls,
        ),
        id=id,
    )


def magnifying_glass() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            fill_rule="evenodd",
            d=(
                "M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7"
                " 7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06"
                " 1.06l-3.329-3.328A7 7 0 0 1 2 9Z"
            ),
            clip_rule="evenodd",
        ),
        viewBox="0 0 20 20",
        fill="currentColor",
        aria_hidden="true",
        data_slot="icon",
        cls=(
            "pointer-events-none col-start-1 row-start-1 ml-3 size-5"
            " self-center text-neutral-400"
        ),
    )


def printer() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2",
        ),
        svg.Path(
            d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6",
        ),
        svg.Rect(x="6", y="14", width="12", height="8", rx="1"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
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


def report() -> svg.Svg:
    return svg.Svg(
        svg.Path(
            d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",
        ),
        svg.Path(
            d="M14 2v4a2 2 0 0 0 2 2h4",
        ),
        svg.Path(
            d="M10 9H8",
        ),
        svg.Path(
            d="M16 13H8",
        ),
        svg.Path(
            d="M16 17H8",
        ),
        width="16",
        height="16",
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        stroke_width="2",
        stroke_linecap="round",
        stroke_linejoin="round",
    )


def toc_icon() -> svg.Svg:
    return svg.Svg(
        svg.Text(
            "TOC",
            x="50%",
            y="50%",
            dominant_baseline="middle",
            text_anchor="middle",
            font_size="10",
            font_weight="bold",
            fill="currentColor",
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
        cls=(
            "dark:hover:text-neutral-100",
            "dark:text-neutral-400",
            "hover:text-neutral-50",
            "text-neutral-300",
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

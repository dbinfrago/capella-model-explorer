/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import "bigger-picture/dist/bigger-picture.css";
import BiggerPicture from "bigger-picture/dist/bigger-picture.mjs";

import "htmx.org";
import "./htmx.js";
import "idiomorph/dist/idiomorph.js";
import "idiomorph/dist/idiomorph-ext.js";

import "./compiled.css";

window.openDiagramViewer = function (svgContainer) {
  if (typeof window.lightbox === "undefined") {
    window.lightbox = BiggerPicture({ target: document.body });
  }
  lightbox.open({ items: [svgContainer], el: svgContainer });
};

window.toggleToc = function () {
  const toc = document.getElementById("table-of-contents");
  if (!toc) return;

  const isOpen = !toc.classList.contains("translate-x-full");
  toc.classList.toggle("translate-x-full", isOpen);
  toc.classList.toggle("translate-x-0", !isOpen);
};

const xlMediaQuery = window.matchMedia("(min-width: 1280px)");
function resetTocOnResize() {
  const toc = document.getElementById("table-of-contents");
  if (!toc) return;

  toc.classList.toggle("translate-x-full", !xlMediaQuery.matches);
  toc.classList.toggle("translate-x-0", xlMediaQuery.matches);
}

window.addEventListener("resize", resetTocOnResize);
document.addEventListener("DOMContentLoaded", resetTocOnResize);

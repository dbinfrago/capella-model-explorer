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

import * as mdui from "mdui";

import "./compiled.css";

window.mdui = mdui;

window.openDiagramViewer = function (svgContainer) {
  if (typeof window.lightbox === "undefined") {
    window.lightbox = BiggerPicture({ target: document.body });
  }
  lightbox.open({ items: [svgContainer], el: svgContainer });
};

/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

(function () {
  const query = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(...args) {
    document.body.classList.toggle(
      "dark",
      localStorage.theme === "dark" ||
        (!("theme" in localStorage) && query.matches),
    );
    document
      .getElementById("dark-mode-icon-system")
      .classList.toggle("hidden", "theme" in localStorage);
    document
      .getElementById("dark-mode-icon-dark")
      .classList.toggle("hidden", localStorage.theme !== "dark");
    document
      .getElementById("dark-mode-icon-light")
      .classList.toggle("hidden", localStorage.theme !== "light");
  }

  query.addEventListener("change", applyTheme);
  window.addEventListener("DOMContentLoaded", function () {
    document
      .getElementById("dark-mode-button")
      .addEventListener("click", function (event) {
        if (!("theme" in localStorage)) {
          localStorage.theme = "dark";
        } else if (localStorage.theme === "dark") {
          localStorage.theme = "light";
        } else if (localStorage.theme === "light") {
          localStorage.removeItem("theme");
        }
        applyTheme();
      });
    applyTheme();
  });
})();

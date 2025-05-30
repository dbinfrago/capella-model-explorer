/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

(function () {
  const query = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(...args) {
    const is_dark =
      localStorage.theme === "dark" ||
      (!("theme" in localStorage) && query.matches);
    document.documentElement.classList.toggle("mdui-theme-dark", is_dark);
    document.documentElement.classList.toggle("mdui-theme-light", !is_dark);

    let button = document.getElementById("dark-mode-button");
    button.icon =
      localStorage.theme === "light"
        ? "light_mode--outlined"
        : localStorage.theme === "dark"
          ? "dark_mode--outlined"
          : "brightness_auto--outlined";
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

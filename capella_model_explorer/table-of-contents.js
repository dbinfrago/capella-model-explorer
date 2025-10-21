/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

(function () {
  const toc = document.currentScript.parentElement;
  if (!toc) return;

  let observer = null;
  let activeLink = null;

  function setActiveLink(link) {
    if (activeLink) {
      activeLink.classList.remove("active");
    }
    if (link) {
      link.classList.add("active");
      activeLink = link;

      const tocNav = toc.querySelector("nav");
      if (tocNav) {
        const linkTop = link.offsetTop;
        const navHeight = tocNav.getBoundingClientRect().height;
        const scrollTarget = linkTop - navHeight / 2;

        tocNav.scrollTo({
          top: scrollTarget,
          behavior: "smooth",
        });
      }
    }
  }

  function setupObserver() {
    if (observer) {
      observer.disconnect();
    }

    const links = toc.querySelectorAll(".toc-link");
    const headings = Array.from(links)
      .map((link) => {
        const id = link.getAttribute("data-target");
        return document.getElementById(id);
      })
      .filter(Boolean);

    const scrollContainer = document.getElementById("root");
    if (!scrollContainer || headings.length === 0) return;

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            const correspondingLink = toc.querySelector(
              `[data-target="${id}"]`,
            );
            if (correspondingLink) {
              setActiveLink(correspondingLink);
            }
          }
        });
      },
      {
        root: scrollContainer,
        rootMargin: "-75px 0px -80% 0px",
        threshold: 0,
      },
    );

    headings.forEach((heading) => {
      if (heading) observer.observe(heading);
    });

    if (links.length > 0) {
      setActiveLink(links[0]);
    }
  }

  toc.addEventListener("click", (e) => {
    if (e.target.matches(".toc-link")) {
      e.preventDefault();
      const targetId = e.target.getAttribute("data-target");
      const target = document.getElementById(targetId);
      const scrollContainer = document.getElementById("root");

      if (target && scrollContainer) {
        const offset = 80;
        const containerRect = scrollContainer.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        const scrollTop = scrollContainer.scrollTop;
        const targetPosition =
          targetRect.top - containerRect.top + scrollTop - offset;

        scrollContainer.scrollTo({
          top: targetPosition,
          behavior: "smooth",
        });
        setActiveLink(e.target);
      }
    }
  });

  document.addEventListener("click", (e) => {
    const tocButton = document.getElementById("toc-toggle-button");
    if (!tocButton) return;

    const isXlScreen = window.matchMedia("(min-width: 1280px)").matches;
    if (isXlScreen) return;

    const isTocOpen = !toc.classList.contains("translate-x-full");
    if (!isTocOpen) return;

    const clickedInsideToc = toc.contains(e.target);
    const clickedTocButton = tocButton.contains(e.target);

    if (!clickedInsideToc && !clickedTocButton) {
      toc.classList.add("translate-x-full");
      toc.classList.remove("translate-x-0");
      tocButton.setAttribute("aria-expanded", "false");
    }
  });

  setupObserver();
})();

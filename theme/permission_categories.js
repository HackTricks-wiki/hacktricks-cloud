/* Display the canonical YAML on its book page without adding it to the search index. */
(() => {
  "use strict";

  function init() {
    for (const viewer of document.querySelectorAll("[data-permission-yaml]")) {
      const status = viewer.querySelector("[data-yaml-status]");
      const code = viewer.querySelector("[data-yaml-content]");
      const retry = viewer.querySelector("[data-yaml-retry]");

      async function load() {
        retry.hidden = true;
        status.textContent = "Loading permission categories…";
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 30000);
        try {
          const response = await fetch(viewer.dataset.permissionYaml, {
            signal: controller.signal,
            credentials: "same-origin",
          });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const yaml = await response.text();
          // Use textContent so strings inside the YAML cannot become HTML.
          code.textContent = yaml;
          status.textContent = "Canonical permission categories (YAML)";
        } catch (error) {
          status.textContent = "Permission categories could not be loaded. Please retry or open the source link above.";
          retry.hidden = false;
        } finally {
          clearTimeout(timeout);
        }
      }

      retry.addEventListener("click", load);
      load();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

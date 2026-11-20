(() => {
  "use strict";

  const groups = document.querySelectorAll(".navigation .resources-group");
  const dropdowns = Array.from(document.querySelectorAll(".navigation .w-dropdown"));
  const mobile = window.matchMedia("(max-width: 991px)");

  function dropdownParts(dropdown) {
    return {
      toggle: dropdown.querySelector(".w-dropdown-toggle"),
      panel: dropdown.querySelector(".w-dropdown-list"),
    };
  }

  function setDropdownOpen(dropdown, open) {
    const { toggle, panel } = dropdownParts(dropdown);
    if (!toggle || !panel) return;

    dropdown.classList.toggle("w--open", open);
    toggle.classList.toggle("w--open", open);
    panel.classList.toggle("w--open", open);
    toggle.setAttribute("aria-expanded", String(open));
    panel.setAttribute("aria-hidden", String(!open));
  }

  function closeDropdowns(except) {
    dropdowns.forEach((dropdown) => {
      if (dropdown !== except) setDropdownOpen(dropdown, false);
    });
  }

  dropdowns.forEach((dropdown) => {
    const { toggle, panel } = dropdownParts(dropdown);
    if (!toggle || !panel) return;

    if (!toggle.hasAttribute("tabindex")) toggle.tabIndex = 0;
    toggle.setAttribute("role", "button");
    toggle.setAttribute("aria-haspopup", "true");
    setDropdownOpen(dropdown, false);

    function toggleDropdown(event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      const shouldOpen = !dropdown.classList.contains("w--open");
      closeDropdowns(dropdown);
      setDropdownOpen(dropdown, shouldOpen);
    }

    // Capture the event before Webflow's dropdown handler so a click cannot
    // be handled twice and immediately close the menu again.
    toggle.addEventListener("click", toggleDropdown, true);
    toggle.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        toggleDropdown(event);
      } else if (event.key === "Escape") {
        event.preventDefault();
        event.stopImmediatePropagation();
        setDropdownOpen(dropdown, false);
      }
    }, true);

    panel.addEventListener("click", (event) => {
      if (event.target.closest("a")) setDropdownOpen(dropdown, false);
    });
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".navigation .w-dropdown")) closeDropdowns();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const openDropdown = document.querySelector(".navigation .w-dropdown.w--open");
    if (!openDropdown) return;
    const { toggle } = dropdownParts(openDropdown);
    closeDropdowns();
    if (toggle) toggle.focus();
  });

  function updateGroups() {
    groups.forEach((group) => {
      group.open = !mobile.matches;
      group.querySelector("summary").tabIndex = mobile.matches ? 0 : -1;
    });
  }

  groups.forEach((group) => {
    group.querySelector("summary").addEventListener("click", (event) => {
      if (!mobile.matches) event.preventDefault();
    });
  });

  updateGroups();
  mobile.addEventListener("change", () => {
    updateGroups();
    closeDropdowns();
  });
})();

(() => {
  "use strict";

  const groups = document.querySelectorAll(".navigation .resources-group");
  const mobile = window.matchMedia("(max-width: 991px)");

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
  mobile.addEventListener("change", updateGroups);
})();

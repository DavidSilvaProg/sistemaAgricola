const selectAll = document.getElementById("select-all");
    const checkboxes = document.querySelectorAll(".item-checkbox");
    const bulkActions = document.getElementById("bulk-actions");

    function toggleBulkActions() {
      const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
      bulkActions.classList.toggle("hidden", !anyChecked);
    }

    selectAll.addEventListener("change", () => {
      checkboxes.forEach(checkbox => checkbox.checked = selectAll.checked);
      toggleBulkActions();
    });

    checkboxes.forEach(checkbox => {
      checkbox.addEventListener("change", toggleBulkActions);
    });
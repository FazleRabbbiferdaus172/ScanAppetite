document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('selectAll');

    // Ensure the checkbox exists before adding an event listener
    if (selectAllCheckbox) {
        selectAllCheckbox.onclick = function() {
            const checkboxes = document.getElementsByName('item_ids');
            for (const checkbox of checkboxes) {
                checkbox.checked = this.checked;
            }
        }
    }
});
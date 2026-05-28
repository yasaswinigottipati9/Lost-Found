/*
 * Lost & Found Smart Platform - Main JavaScript
 * Student Note: This file contains client-side JavaScript for
 * interactive features like auto-dismiss alerts, chat AJAX, etc.
 */

// Wait for DOM to be fully loaded before running scripts
document.addEventListener('DOMContentLoaded', function () {

    // ============================================================
    // AUTO-DISMISS ALERTS after 5 seconds
    // ============================================================
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5000ms = 5 seconds
    });


    // ============================================================
    // ITEM CARD HOVER EFFECT - highlight on hover
    // ============================================================
    const itemCards = document.querySelectorAll('.item-card');
    itemCards.forEach(function (card) {
        card.addEventListener('mouseenter', function () {
            this.style.zIndex = '10';
        });
        card.addEventListener('mouseleave', function () {
            this.style.zIndex = '1';
        });
    });


    // ============================================================
    // POST ITEM FORM - Item Type Selector
    // Highlight selected type (Lost/Found) card
    // ============================================================
    const lostSelector = document.getElementById('lostSelector');
    const foundSelector = document.getElementById('foundSelector');
    const itemTypeSelect = document.getElementById('id_item_type');

    if (lostSelector && foundSelector && itemTypeSelect) {
        // Set initial state based on select value
        function updateTypeSelector() {
            const val = itemTypeSelect.value;
            lostSelector.classList.remove('selected-lost');
            foundSelector.classList.remove('selected-found');
            if (val === 'lost') {
                lostSelector.classList.add('selected-lost');
            } else if (val === 'found') {
                foundSelector.classList.add('selected-found');
            }
        }
        updateTypeSelector();
        itemTypeSelect.addEventListener('change', updateTypeSelector);
    }


    // ============================================================
    // CHAT - Scroll to bottom of messages
    // ============================================================
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }


    // ============================================================
    // DASHBOARD TABS - Remember active tab in localStorage
    // So when user navigates back, same tab is active
    // ============================================================
    const tabLinks = document.querySelectorAll('[data-bs-toggle="pill"]');
    tabLinks.forEach(function (link) {
        link.addEventListener('shown.bs.tab', function (e) {
            localStorage.setItem('activeTab', e.target.getAttribute('href'));
        });
    });

    // Restore active tab
    const savedTab = localStorage.getItem('activeTab');
    if (savedTab) {
        const tabEl = document.querySelector('[href="' + savedTab + '"]');
        if (tabEl) {
            const tab = new bootstrap.Tab(tabEl);
            tab.show();
        }
    }


    // ============================================================
    // SEARCH FORM - Submit on select change (for category/type filters)
    // ============================================================
    const filterSelects = document.querySelectorAll('#filterForm select');
    filterSelects.forEach(function (select) {
        select.addEventListener('change', function () {
            // Optional: auto-submit form on change
            // document.getElementById('filterForm').submit();
        });
    });


    // ============================================================
    // CONFIRM DELETE - Extra confirmation dialog
    // ============================================================
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to delete this item? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });


    // ============================================================
    // IMAGE UPLOAD - Preview image before submitting
    // ============================================================
    const imageInput = document.getElementById('id_image');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');

    if (imageInput && imagePreview && previewImg) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('File is too large! Maximum size is 5MB.');
                    imageInput.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (evt) {
                    previewImg.src = evt.target.result;
                    imagePreview.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }


    // ============================================================
    // BACK TO TOP BUTTON (if exists in page)
    // ============================================================
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                backToTopBtn.classList.remove('d-none');
            } else {
                backToTopBtn.classList.add('d-none');
            }
        });

        backToTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }


    // ============================================================
    // TOOLTIP INITIALIZATION (Bootstrap tooltips)
    // ============================================================
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

});


// ============================================================
// GLOBAL FUNCTION: Select item type on post form
// Called from HTML onclick handlers
// ============================================================
function selectType(type) {
    const lostSelector = document.getElementById('lostSelector');
    const foundSelector = document.getElementById('foundSelector');
    const itemTypeSelect = document.getElementById('id_item_type');

    if (!lostSelector || !foundSelector || !itemTypeSelect) return;

    lostSelector.classList.remove('selected-lost', 'bg-danger', 'bg-opacity-10');
    foundSelector.classList.remove('selected-found', 'bg-success', 'bg-opacity-10');

    if (type === 'lost') {
        lostSelector.classList.add('selected-lost', 'bg-danger', 'bg-opacity-10');
    } else if (type === 'found') {
        foundSelector.classList.add('selected-found', 'bg-success', 'bg-opacity-10');
    }

    itemTypeSelect.value = type;
}

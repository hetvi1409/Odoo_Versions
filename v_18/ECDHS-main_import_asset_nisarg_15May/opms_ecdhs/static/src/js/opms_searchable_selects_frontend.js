/**
 * OPMS Searchable Select Integration
 * Uses a custom searchable combobox pattern (similar to Odoo many2one fields)
 * No external dependencies - works directly with form-select elements
 */
(function () {
    "use strict";

    var ENHANCED_ATTR = "data-opms-searchable";

    function createCombobox(select) {
        // Skip if already enhanced
        if (select[ENHANCED_ATTR]) {
            return false;
        }

        // Create wrapper container
        var wrapper = document.createElement("div");
        wrapper.className = "opms-searchable-combobox";

        // Create the input (replaces the visual select)
        var input = document.createElement("input");
        input.type = "text";
        input.className = "form-control opms-combobox-input";
        input.setAttribute("autocomplete", "off");
        input.setAttribute("placeholder", "Type to search or click to see all...");
        input.setAttribute("data-opms-no-auto-submit", "1");

        // Create dropdown list container
        var dropdown = document.createElement("div");
        dropdown.className = "opms-combobox-dropdown";

        // Build options list from select element
        var options = [];
        var cachedBroadOptions = [];
        var selectedText = "";
        var placeholderText = "Type to search or click to see all...";
        var searchQuery = "";
        var dropdownOpen = false;

        Array.prototype.forEach.call(select.options, function (option) {
            options.push({
                value: option.value,
                text: option.textContent || option.innerText,
                selected: option.selected
            });

            if (!option.value && option.selected) {
                placeholderText = option.textContent || option.innerText || placeholderText;
            }

            if (option.selected && option.value) {
                selectedText = option.textContent || option.innerText;
            }
        });

        input.setAttribute("placeholder", placeholderText);

        function syncDisplayFromSelect() {
            var selectedOption = null;

            Array.prototype.forEach.call(select.options, function (option) {
                if (option.selected) {
                    selectedOption = option;
                }
            });

            if (selectedOption && selectedOption.value) {
                selectedText = selectedOption.textContent || selectedOption.innerText || "";
                input.value = selectedText;
            } else {
                selectedText = "";
                input.value = "";
            }

            searchQuery = "";
        }

        syncDisplayFromSelect();

        function cloneOptions(optionList) {
            return optionList.map(function (opt) {
                return {
                    value: opt.value,
                    text: opt.text,
                    selected: !!opt.selected
                };
            });
        }

        function shouldUseBroadCache() {
            var currentValuedCount = options.filter(function (opt) { return !!opt.value; }).length;
            var cachedValuedCount = cachedBroadOptions.filter(function (opt) { return !!opt.value; }).length;
            return currentValuedCount <= 1 && cachedValuedCount > 1;
        }

        function getRenderableOptions() {
            if (shouldUseBroadCache()) {
                var activeValue = String(select.value || "");
                return cachedBroadOptions.map(function (opt) {
                    return {
                        value: opt.value,
                        text: opt.text,
                        selected: !!opt.value && String(opt.value) === activeValue
                    };
                });
            }
            return options;
        }

        function refreshBroadCache() {
            var valuedCount = options.filter(function (opt) { return !!opt.value; }).length;
            if (valuedCount > 1) {
                cachedBroadOptions = cloneOptions(options);
            }
        }

        // Build and insert dropdown options
        function renderDropdown(filterText) {
            dropdown.innerHTML = "";
            var query = (filterText || "").toLowerCase().trim();
            var matchCount = 0;
            var renderableOptions = getRenderableOptions();

            renderableOptions.forEach(function (opt) {
                // Always show first empty option
                if (!opt.value) {
                    var optEl = document.createElement("div");
                    optEl.className = "opms-combobox-option opms-combobox-empty";
                    optEl.textContent = opt.text || "-- None --";
                    optEl.dataset.value = opt.value;
                    dropdown.appendChild(optEl);
                    return;
                }

                var text = opt.text.toLowerCase();
                var matches = !query || text.indexOf(query) !== -1;

                if (matches) {
                    matchCount++;
                    var optEl = document.createElement("div");
                    optEl.className = "opms-combobox-option";
                    if (opt.selected) {
                        optEl.classList.add("selected");
                    }
                    optEl.textContent = opt.text;
                    optEl.dataset.value = opt.value;

                    optEl.addEventListener("click", function (e) {
                        e.stopPropagation();
                        selectOption(opt.value, opt.text);
                    });

                    dropdown.appendChild(optEl);
                }
            });

            // Show "No Match" message if search yielded nothing
            if (query && matchCount === 0) {
                var noMatch = document.createElement("div");
                noMatch.className = "opms-combobox-no-match";
                noMatch.textContent = "- No Match -";
                dropdown.appendChild(noMatch);
            }

        }

        function positionDropdown() {
            var rect = input.getBoundingClientRect();
            dropdown.style.position = "fixed";
            dropdown.style.left = rect.left + "px";
            dropdown.style.top = rect.bottom + "px";
            dropdown.style.width = rect.width + "px";
            dropdown.style.zIndex = "1085";
            dropdown.style.display = "block";
        }

        function openDropdown() {
            if (!dropdownOpen) {
                document.body.appendChild(dropdown);
                dropdownOpen = true;
            }
            positionDropdown();
            dropdown.classList.add("show");
        }

        function closeDropdown() {
            dropdown.classList.remove("show");
            dropdownOpen = false;
            if (dropdown.parentNode === document.body) {
                dropdown.parentNode.removeChild(dropdown);
            }
        }

        function selectOption(value, text) {
            var hasOption = Array.prototype.some.call(select.options, function (option) {
                return String(option.value || "") === String(value || "");
            });
            if (value && !hasOption) {
                var injectedOption = document.createElement("option");
                injectedOption.value = value;
                injectedOption.textContent = text;
                select.appendChild(injectedOption);
            }

            select.value = value;
            input.value = value ? text : "";
            searchQuery = "";
            closeDropdown();

            // Trigger change event
            var event = new Event("change", { bubbles: true });
            select.dispatchEvent(event);
        }

        // Event listeners
        input.addEventListener("focus", function () {
            renderDropdown(searchQuery);
            openDropdown();
        });

        input.addEventListener("click", function () {
            renderDropdown(searchQuery);
            openDropdown();
        });

        input.addEventListener("input", function () {
            searchQuery = input.value;
            if (!String(searchQuery || "").trim()) {
                selectedText = "";
                if (select.value) {
                    select.value = "";
                    var clearEvent = new Event("change", { bubbles: true });
                    select.dispatchEvent(clearEvent);
                }
            }
            renderDropdown(searchQuery);
            openDropdown();
        });

        input.addEventListener("keydown", function (e) {
            // Escape key - close dropdown and restore selected value
            if (e.key === "Escape") {
                input.value = selectedText || "";
                searchQuery = "";
                closeDropdown();
            }
            if (e.key === "ArrowDown") {
                e.preventDefault();
                renderDropdown(searchQuery);
                openDropdown();
            }
        });

        // Close dropdown when clicking elsewhere
        document.addEventListener("click", function (e) {
            if (!wrapper.contains(e.target)) {
                closeDropdown();
            }
        });

        window.addEventListener("scroll", function () {
            if (dropdownOpen) {
                positionDropdown();
            }
        }, true);

        window.addEventListener("resize", function () {
            if (dropdownOpen) {
                positionDropdown();
            }
        });

        // Append to DOM
        wrapper.appendChild(input);
        select.parentNode.insertBefore(wrapper, select);
        select.style.display = "none";

        // Mark as enhanced
        select[ENHANCED_ATTR] = true;
        select._opmsComboboxSyncDisplay = syncDisplayFromSelect;

        // Rerender if select options change dynamically
        var observer = new MutationObserver(function () {
            options = [];
            placeholderText = "Type to search or click to see all...";

            Array.prototype.forEach.call(select.options, function (option) {
                options.push({
                    value: option.value,
                    text: option.textContent || option.innerText,
                    selected: option.selected
                });

                if (!option.value && option.selected) {
                    placeholderText = option.textContent || option.innerText || placeholderText;
                }

            });

            input.setAttribute("placeholder", placeholderText);

            syncDisplayFromSelect();
            refreshBroadCache();
            refreshBroadCache();

            if (dropdownOpen) {
                renderDropdown(searchQuery);
                positionDropdown();
            }
        });
        observer.observe(select, { childList: true });

        return true;
    }

    function enhanceSelects() {
        var selects = document.querySelectorAll("select.opms-searchable-select");
        var enhanced = 0;
        Array.prototype.forEach.call(selects, function (select) {
            if (createCombobox(select)) {
                enhanced++;
            }
        });
        return enhanced;
    }

    function setupAutoSubmitForms() {
        var forms = document.querySelectorAll('form[data-opms-auto-submit="1"]');

        Array.prototype.forEach.call(forms, function (form) {
            if (form.dataset.opmsAutoSubmitBound === "1") {
                return;
            }
            form.dataset.opmsAutoSubmitBound = "1";

            var pendingTimer = null;
            var delay = Number(form.dataset.opmsAutoSubmitDelay || 250);

            function shouldIgnoreTarget(target) {
                if (!target || !form.contains(target)) {
                    return true;
                }
                if (target.closest(".opms-searchable-combobox")) {
                    return true;
                }
                if (target.matches("[data-opms-no-auto-submit='1']")) {
                    return true;
                }
                return false;
            }

            function submitForm() {
                if (typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                } else {
                    form.submit();
                }
            }

            function queueSubmit(wait) {
                window.clearTimeout(pendingTimer);
                pendingTimer = window.setTimeout(submitForm, typeof wait === "number" ? wait : delay);
            }

            form.addEventListener("change", function (event) {
                var target = event.target;
                if (shouldIgnoreTarget(target)) {
                    return;
                }
                if (target.matches("select, input[type='checkbox'], input[type='radio']")) {
                    queueSubmit(0);
                }
            });

            form.addEventListener("input", function (event) {
                var target = event.target;
                if (shouldIgnoreTarget(target)) {
                    return;
                }
                if (target.matches("input[type='search'], input[type='text'], input[type='number'], textarea")) {
                    queueSubmit();
                }
            });
        });
    }

    // Run on DOM ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", enhanceSelects);
        document.addEventListener("DOMContentLoaded", setupAutoSubmitForms);
    } else {
        enhanceSelects();
        setupAutoSubmitForms();
    }

    // Re-scan periodically for dynamically added selects
    setInterval(enhanceSelects, 500);
    setInterval(setupAutoSubmitForms, 500);

    // Expose global method
    window.opmsRehashSearchableSelects = enhanceSelects;
})();

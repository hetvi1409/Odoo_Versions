/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

export const Timer = publicWidget.Widget.extend({
    selector: '.tender_timer_id',

    start: function () {
        this._super.apply(this, arguments);
        const timerEl = this.el.querySelector('#tender_timer_count');
        const tender = $('input[name="tender_id"]').val();
        const token = $('input[name="tender_timer_token"]').val();
        if (!timerEl || !tender) {
            return;
        }

        const parseOdooDatetime = (value) => {
            if (!value) {
                return null;
            }
            const normalized = String(value).replace(' ', 'T');
            const parsed = new Date(normalized);
            return Number.isNaN(parsed.getTime()) ? null : parsed;
        };

        jsonrpc('/tender/timer', { tender: tender, token: token }).then((timerData) => {
            const endValue = timerData && timerData.end_time ? timerData.end_time : null;
            const endDate = parseOdooDatetime(endValue);

            if (!endDate) {
                timerEl.textContent = 'N/A';
                return;
            }

            const timerIdCount = setInterval(() => {
                const timeRemaining = endDate.getTime() - Date.now();
                if (timeRemaining <= 0) {
                    timerEl.textContent = '0d. 0h. 0m. 0s.';
                    clearInterval(timerIdCount);
                    return;
                }

                const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeRemaining / (1000 * 60 * 60)) % 24);
                const minutes = Math.floor((timeRemaining / (1000 * 60)) % 60);
                const seconds = Math.floor((timeRemaining / 1000) % 60);
                timerEl.textContent = `${days}d. ${hours}h. ${minutes}m. ${seconds}s.`;
            }, 1000);
        }).catch(() => {
            timerEl.textContent = 'N/A';
        });
    }

});

publicWidget.registry.Timer = Timer;

export const ArchiveDropdown = publicWidget.Widget.extend({
    selector: '.tm-archive-dropdown',

    start: function () {
        this._super.apply(this, arguments);

        this._onDocumentClick = this._onDocumentClick.bind(this);

        const submenu = this.el.querySelector('.tm-archive-submenu');
        if (!submenu) {
            return this._bindMobileToggle();
        }

        this._bindMobileToggle();
    },

    destroy: function () {
        document.removeEventListener('click', this._onDocumentClick);
        return this._super.apply(this, arguments);
    },

    _bindMobileToggle: function () {
        const toggle = this.el.querySelector('.nav-link');
        if (!toggle) {
            return;
        }

        toggle.addEventListener('click', (ev) => {
            if (window.matchMedia('(max-width: 991px)').matches) {
                ev.preventDefault();
                this.el.classList.toggle('tm-archive-open');
            }
        });

        document.addEventListener('click', this._onDocumentClick);
    },

    _onDocumentClick: function (ev) {
        if (!this.el.contains(ev.target)) {
            this.el.classList.remove('tm-archive-open');
        }
    },
});

publicWidget.registry.ArchiveDropdown = ArchiveDropdown;

export const ProcurementNav = publicWidget.Widget.extend({
    selector: '.tm-procurement-nav',

    start: function () {
        this._super.apply(this, arguments);

        this.collapseEl = this.el.querySelector('#tmProcurementNav');
        this.togglerEl = this.el.querySelector('.navbar-toggler');
        if (!this.collapseEl || !this.togglerEl) {
            return;
        }

        this._onScroll = this._onScroll.bind(this);
        this._onLinkClick = this._onLinkClick.bind(this);

        this.el.querySelectorAll('.nav-link').forEach((link) => {
            link.addEventListener('click', this._onLinkClick);
        });
        window.addEventListener('scroll', this._onScroll, { passive: true });
    },

    destroy: function () {
        if (this.el) {
            this.el.querySelectorAll('.nav-link').forEach((link) => {
                link.removeEventListener('click', this._onLinkClick);
            });
        }
        window.removeEventListener('scroll', this._onScroll);
        return this._super.apply(this, arguments);
    },

    _closeMobileNav: function () {
        if (!window.matchMedia('(max-width: 991px)').matches) {
            return;
        }
        this.collapseEl.classList.remove('show');
        this.togglerEl.classList.add('collapsed');
        this.togglerEl.setAttribute('aria-expanded', 'false');
    },

    _onLinkClick: function () {
        this._closeMobileNav();
    },

    _onScroll: function () {
        if (this.collapseEl.classList.contains('show')) {
            this._closeMobileNav();
        }
    },
});

publicWidget.registry.ProcurementNav = ProcurementNav;

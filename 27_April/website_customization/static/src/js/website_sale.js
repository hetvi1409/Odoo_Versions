/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.StockWarning = publicWidget.Widget.extend({
    selector: '.o_wsale_product_page, #product_detail',
    events: {
        'click .js_add_cart_json': '_onAddCartJsonClick',
        'change input.js_quantity, input[name="add_qty"]': '_onInputChange',
        'input input.js_quantity, input[name="add_qty"]': '_onInputChange',
    },

    /**
     * @override
     */
    start() {
        this._super(...arguments);
        this._stockQty = null;
        this._stockExceeded = false;
        this._fetchStock().then(() => {
            this._checkAndWarn();
        });
        return Promise.resolve();
    },

    /**
     * Fetch available stock from the server for the current product.
     */
    async _fetchStock() {
        const productId = this._getProductId();
        console.log('productId>>>',productId)
        if (!productId) return;
        try {
            const result = await rpc('/shop/product/stock', { product_id: productId });
            console.log('Stock result>>>', result);
            if (result && result.manage_stock !== false) {
                this._stockQty = (result.qty !== undefined) ? result.qty : null;
            } else {
                this._stockQty = null;
            }
        } catch (e) {
            this._stockQty = null;
        }
    },

    /**
     * Get the current product_id from the page.
     */
    _getProductId() {
        const variantInput = this.el.querySelector('input.product_id, input[name="product_id"]');
        if (variantInput && variantInput.value) return parseInt(variantInput.value, 10);
        const form = this.el.querySelector('form[action="/shop/cart/update"]');
        if (form) {
            const input = form.querySelector('input[name="product_id"]');
            if (input && input.value) return parseInt(input.value, 10);
        }
        return null;
    },


    _getQtyInput() {
        return this.el.querySelector('input.js_quantity, input[name="add_qty"]');
    },

    _getPlusBtn() {
        return this.el.querySelector(
            '.js_add_cart_json[data-dir="add"], ' +
            'a.js_add_cart_json[href*="add"], ' +
            '.css_quantity a.btn:last-of-type, ' +
            '.css_quantity button:last-of-type, ' +
            'a.btn.btn-link.float_right.js_add_cart_json, ' +
            'a.btn-link.js_add_cart_json.float_right'
        ) || this._findPlusBtnByFaIcon();
    },

    /**
     * Fallback: find + button by looking for fa-plus inside .js_add_cart_json links.
     */
    _findPlusBtnByFaIcon() {
        const allCartJsonBtns = this.el.querySelectorAll('a.js_add_cart_json, button.js_add_cart_json');
        console.log('All cart JSON buttons>>>', allCartJsonBtns);
        for (const btn of allCartJsonBtns) {
            if (btn.querySelector('.fa-plus') || btn.classList.contains('fa-plus')) {
                return btn;
            }
        }
        return null;
    },

    /**
     * Get the Add to Cart submit button.
     */
    _getAddToCartBtn() {
        return this.el.querySelector(
            'a#add_to_cart, button#add_to_cart, ' +
            '.a-submit#add_to_cart, ' +
            'a.a-submit[id="add_to_cart"], ' +
            'button[id="add_to_cart"]'
        );
    },

    /**
     * Intercept clicks on .js_add_cart_json (both + and -).
     * Block + if stock exceeded; allow - always.
     */
    _onAddCartJsonClick(ev) {
        const btn = ev.currentTarget;
        const isPlus = btn.querySelector('.fa-plus') !== null ||
                       btn.textContent.trim() === '+' ||
                       btn.getAttribute('data-dir') === 'add';

        if (isPlus && this._stockQty !== null) {
            const qtyInput = this._getQtyInput();
            const currentQty = qtyInput ? (parseInt(qtyInput.value, 10) || 1) : 1;

            if (currentQty >= this._stockQty) {
                // Block the + click entirely
                ev.preventDefault();
                ev.stopImmediatePropagation();
                this._stockExceeded = true;
                this._applyState();
                return false;
            }
        }

        // It's a - click or qty is within limit — let Odoo handle it, then re-check
        setTimeout(() => this._checkAndWarn(), 120);
    },

    /**
     * Called when the user types in the qty input.
     */
    _onInputChange() {
        if (this._stockQty === null) return;
        this._checkAndWarn();
    },

    /**
     * Core logic: compare qty vs stock and update state.
     */
    _checkAndWarn() {
        if (this._stockQty === null) return;
        const qtyInput = this._getQtyInput();
        if (!qtyInput) return;
        const currentQty = parseInt(qtyInput.value, 10) || 1;
        console.log('currentQty>>>', currentQty);
        this._stockExceeded = currentQty >= this._stockQty +1;
        console.log('stockExceeded>>>', this._stockExceeded);
        this._applyState();
    },

    /**
     * Apply visual state: warning banner + button states.
     */
    _applyState() {
        if (this._stockExceeded) {
            this._renderWarning(this._stockQty);
            this._setAddToCartDisabled(true);
            this._setPlusBtnDisabled(true);
        } else {
            this._clearWarning();
            this._setAddToCartDisabled(false);
            this._setPlusBtnDisabled(false);
        }
    },

    /**
     * Render the warning banner below the qty block (idempotent).
     */
    _renderWarning(maxQty) {
        if (this.el.querySelector('.stock_limit_warning')) return;

        // Find the qty block — try multiple selectors
        const qtyBlock = this.el.querySelector(
            '.css_quantity, .input-group.js_add_cart_json, .js_quantity_wrapper, ' +
            '.product_quantity_block, div.input-group'
        );
        if (!qtyBlock) return;

        const warning = document.createElement('div');
        warning.className = 'stock_limit_warning';

        if (!maxQty || maxQty <= 0) {
            warning.innerHTML = `
                <span class="stock_warning_icon">⚠</span>
                <span><strong>Out of Stock!</strong> This product is currently unavailable.</span>
            `;
        } else {
            warning.innerHTML = `
                <span class="stock_warning_icon">⚠</span>
                <span>
                    <strong>Stock Limit Reached!</strong>
                    Only <strong>${maxQty}</strong> unit${maxQty > 1 ? 's' : ''} available in stock.
                </span>
            `;
        }

        // Insert directly after the qty block
        qtyBlock.insertAdjacentElement('afterend', warning);
    },

    /**
     * Remove the warning banner.
     */
    _clearWarning() {
        this.el.querySelectorAll('.stock_limit_warning').forEach(el => el.remove());
    },

    /**
     * Disable/enable the + (add one) button.
     */
    _setPlusBtnDisabled(disable) {
        // Target all .js_add_cart_json buttons that have fa-plus
        const allCartJsonBtns = this.el.querySelectorAll('a.js_add_cart_json, button.js_add_cart_json');
        for (const btn of allCartJsonBtns) {
            const isPlus = btn.querySelector('.fa-plus') !== null ||
                           btn.getAttribute('data-dir') === 'add';
            if (isPlus) {
                if (disable) {
                    btn.classList.add('stock_plus_disabled');
                    btn.setAttribute('data-stock-blocked', '1');
                } else {
                    btn.classList.remove('stock_plus_disabled');
                    btn.removeAttribute('data-stock-blocked');
                }
            }
        }
    },

    /**
     * Disable/enable the Add to Cart button.
     */
    _setAddToCartDisabled(disable) {
        const btn = this._getAddToCartBtn();
        if (!btn) return;
        if (disable) {
            btn.classList.add('stock_cart_disabled');
            btn.setAttribute('data-stock-blocked', '1');
        } else {
            btn.classList.remove('stock_cart_disabled');
            btn.removeAttribute('data-stock-blocked');
        }
    },

    /**
     * @override
     */
    destroy() {
        this._clearWarning();
        this._setAddToCartDisabled(false);
        this._setPlusBtnDisabled(false);
        this._super(...arguments);
    },
});

// ─── Styles ────────────────────────────────────────────────────────────────────
const style = document.createElement('style');
style.textContent = `

/* ── Warning banner ── */
.stock_limit_warning {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.875rem;
    background: #fff8e1;
    color: #b45309;
    border: 1px solid #fcd34d;
    border-left: 4px solid #f59e0b;
    padding: 10px 14px;
    border-radius: 6px;
    margin-top: 10px;
    animation: stockFadeIn 0.25s ease;
    line-height: 1.4;
}

.stock_warning_icon {
    font-size: 1.1rem;
    flex-shrink: 0;
    color: #f59e0b;
}

@keyframes stockFadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Disabled + button ── */
.stock_plus_disabled {
    pointer-events: none !important;
    opacity: 0.35 !important;
    cursor: not-allowed !important;
}

/* ── Disabled Add to Cart button ── */
.stock_cart_disabled {
    pointer-events: none !important;
    opacity: 0.45 !important;
    cursor: not-allowed !important;
    filter: grayscale(60%) !important;
    position: relative;
}

/* Tooltip on hover for disabled Add to Cart */
.stock_cart_disabled::after {
    content: "Quantity exceeds available stock";
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    color: #fff;
    font-size: 0.75rem;
    padding: 4px 8px;
    border-radius: 4px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s ease;
    z-index: 10;
}

/* Show tooltip on hover (pointer-events still blocked, but CSS hover works on parent) */
.stock_cart_disabled:hover::after {
    opacity: 1;
}

`;
document.head.appendChild(style);
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { StyleManager } from "./style_manager";

export class SettingsModal extends Component {
    setup() {
        this.orm = useService("orm");

        this.defaultSettings = {
            home_icon_count: 6,
            home_icon_size: 70,
            home_font_size_multiplier: 100,
            home_icon_spacing: 10,
            home_icon_margin: 16,
            home_icon_radius: 17.1428571,
            home_top_margin: 48,
            home_fit_to_screen_width: false,
        };

        this.settings = [
            { id: 'iconCountSlider', key: 'home_icon_count', label: _t('Column count'), type: 'range', min: 4, max: 15, step: 1, unit: '' },
            { id: 'iconSizeSlider', key: 'home_icon_size', label: _t('Icon size'), type: 'range', min: 60, max: 128, step: 1, unit: 'px' },
            { id: 'fontSizeSlider', key: 'home_font_size_multiplier', label: _t('Text size'), type: 'range', min: 50, max: 250, step: 1, unit: '%' },
            { id: 'iconSpacingSlider', key: 'home_icon_spacing', label: _t('Icon inner spacing'), type: 'range', min: 5, max: 20, step: 1, unit: 'px' },
            { id: 'iconMarginSlider', key: 'home_icon_margin', label: _t('Icon margin'), type: 'range', min: 0, max: 64, step: 1, unit: 'px' },
            { id: 'iconRadiusSlider', key: 'home_icon_radius', label: _t('Corner radius'), type: 'range', min: 0, max: 100, step: 'any', unit: '%', decimal: 0 },
            { id: 'topMarginSlider', key: 'home_top_margin', label: _t('Top margin'), type: 'range', min: 0, max: 96, step: 1, unit: 'px' },
            { id: 'fitToScreenWidthCheckbox', key: 'home_fit_to_screen_width', label: _t('Fit to screen width'), type: 'boolean' },
        ];

        this.state = useState({ ...this.defaultSettings });
        this.initialSettings = {};
        this.isSaved = false;

        onWillStart(async () => {
            await this.loadSettings();
        });

        onMounted(() => {
            this.applyPreview();
            this.resizeListener = () => {
                this.applyPreview();
            };
            browser.addEventListener("resize", this.resizeListener);
        });

        onWillUnmount(() => {
            browser.removeEventListener("resize", this.resizeListener);
            if (!this.isSaved) {
                StyleManager.applyStyles(this.initialSettings);
            }
        });
    }

    async loadSettings() {
        try {
            const data = await this.orm.call("res.users", "get_home_customizer_settings");
            if (data) {
                Object.assign(this.state, data);
                this.initialSettings = { ...this.state };
            }
        } catch (e) {
        }
    }

    applyPreview() {
        StyleManager.applyStyles(this.state);
    }

    onInput() {
        this.applyPreview();
    }

    formatValue(setting) {
        let val = this.state[setting.key];
        if (setting.decimal !== undefined) {
            val = parseFloat(val).toFixed(setting.decimal);
        } else if (typeof val === 'number') {
            val = Math.round(val);
        }
        return val + (setting.unit || '');
    }

    isChanged(key) {
        const current = this.state[key];
        const initial = this.initialSettings[key];
        if (typeof current === 'number') return Math.abs(current - initial) > 0.01;
        return current !== initial;
    }

    isDifferentFromDefault(key) {
        const current = this.state[key];
        const def = this.defaultSettings[key];
        if (typeof current === 'number') return Math.abs(current - def) > 0.01;
        return current !== def;
    }

    hasChanges() {
        return Object.keys(this.state).some(key => this.isChanged(key));
    }

    hasDiffFromDefaults() {
        return Object.keys(this.state).some(key => this.isDifferentFromDefault(key));
    }

    undoSetting(key) {
        this.state[key] = this.initialSettings[key];
        this.applyPreview();
    }

    resetSetting(key) {
        this.state[key] = this.defaultSettings[key];
        this.applyPreview();
    }

    undoAll() {
        Object.assign(this.state, this.initialSettings);
        this.applyPreview();
    }

    resetAll() {
        Object.assign(this.state, this.defaultSettings);
        this.applyPreview();
    }

    async save() {
        this.isSaved = true;
        try {
            await this.orm.call("res.users", "update_home_customizer_settings", [this.state]);
            this.props.close();
        } catch (e) {
            this.isSaved = false;
        }
    }

    close() {
        this.props.close();
    }
}

SettingsModal.components = { Dialog };
SettingsModal.template = "home_customizer.SettingsModal";
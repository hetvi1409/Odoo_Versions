/** @odoo-module **/

import { registry } from "@web/core/registry";

const styleElementId = 'odoo-app-drawer-style';

export const StyleManager = {
    applyStyles(settings) {
        const {
            home_icon_count: iconCount,
            home_icon_size: iconSize,
            home_icon_radius: iconRadius,
            home_top_margin: topMargin,
            home_icon_spacing: iconSpacing,
            home_fit_to_screen_width: fitToScreenWidth,
            home_icon_margin: iconMargin,
            home_font_size_multiplier: fontSizeMultiplier
        } = settings;

        if (iconCount === undefined) {
            return;
        }

        let style = document.getElementById(styleElementId);

        const widthPercent = (100 / iconCount).toFixed(8) + '%';
        
        const borderRadiusInPx = (iconSize / 2) * (iconRadius / 100);
        
        const baseFontSize = (iconSize * (0.875 / 70));
        const finalFontSize = baseFontSize * (fontSizeMultiplier / 100);

        let maxWidthCss = '';
        if (fitToScreenWidth) {
            maxWidthCss = `max-width: ${window.innerWidth - 40}px !important;`;
        } else {
            const spacingCount = iconCount - 1;
            const baseMaxWidthPx = iconCount * 75 + spacingCount * 80;
            const sizeAdjustment = (iconSize - 70) * 8; 
            const maxWidthPx = baseMaxWidthPx + sizeAdjustment;
            maxWidthCss = `max-width: ${maxWidthPx}px !important;`;
        }

        const css = `
            @media (min-width: 768px) {
                .o_home_menu { font-size: ${finalFontSize}rem !important; }
                .o_home_menu .row-cols-6 > *, .o_home_menu .row-cols-sm-6 > *, .o_home_menu .row-cols-md-6 > *, .o_home_menu .row-cols-lg-6 > *, .o_home_menu .row-cols-xl-6 > *, .o_home_menu .row-cols-xxl-6 > *, .o_home_menu .col-2, .o_home_menu .col-sm-2, .o_home_menu .col-md-2, .o_home_menu .col-lg-2, .o_home_menu .col-xl-2, .o_home_menu .col-xxl-2 { width: ${widthPercent} !important; flex: 0 0 auto !important; }
                .o_home_menu .offset-2, .o_home_menu .offset-sm-2, .o_home_menu .offset-md-2, .o_home_menu .offset-lg-2, .o_home_menu .offset-xl-2, .o_home_menu .offset-xxl-2 { margin-left: ${widthPercent} !important; }
                .o_home_menu .container, .o_home_menu .o_container_small { ${maxWidthCss} }
                .o_home_menu .o_app .o_app_icon { width: ${iconSize}px !important; height: ${iconSize}px !important; border-radius: ${borderRadiusInPx}px !important; padding: ${iconSpacing}px !important; }
                .o_home_menu .mb-3 { margin-bottom: ${iconMargin}px !important; }
            }
            .mt-5 { margin-top: ${topMargin}px !important; }
        `;

        if (style) {
            style.textContent = css;
        } else {
            style = document.createElement('style');
            style.id = styleElementId;
            style.textContent = css;
            document.head.appendChild(style);
        }
    }
};

export const styleService = {
    dependencies: ["orm"],
    async start(env, { orm }) {
        try {
            const settings = await orm.call("res.users", "get_home_customizer_settings");
            if (settings) {
                StyleManager.applyStyles(settings);
            }
        } catch (error) {
        }
    }
};

registry.category("services").add("home_customizer_style", styleService);
{
    "name": "Login Page Customizer | Custom Background, Style & Branding",

    "description": """
Login Page Customizer by Zehntech Technologies is a powerful module designed to 
enhance and personalize the Odoo login experience by enabling complete control 
over layout, styling, and branding of the login screen.

Key Features - Login Page Customizer
    Custom Background - Set custom background images for a visually appealing login screen
    Layout Alignment - Choose center, left, or right aligned login form
    UI Customization - Modify colors, fonts, and overall appearance
    Password Security - Enforce strong password rules and validation
    Enhanced UX - Improve usability and user-friendly interaction
    Responsive Design - Optimized for desktop and mobile devices
    Flexible Styling - Easily adaptable UI with SCSS support
    Easy Configuration - Manage settings from backend configuration panel

Tags: Odoo Login Customization, Odoo UI Enhancement, Login Branding,
    Odoo Authentication, Login Page Design, Odoo UX Improvement,
    Odoo Security Features, Web Customization, Odoo Frontend,
    Odoo Login Personalization, Odoo login page customization,
    Odoo custom login page, Odoo login background image,
    Odoo login page branding, Odoo login security
""",

    "summary": """
Login Page Customizer for advanced Odoo login customization - background, layout,
branding, security, and UI enhancements with improved user experience.
Powered by Zehntech Technologies.Odoo login page customization, Odoo custom login page, Odoo login background image, Odoo login page branding, Odoo login security
""",

    "category": "Website",
    "sequence": 30,
    "version": "19.0.1.0.0",

    "author": "Zehntech Technologies Inc.",
    "company": "Zehntech Technologies Inc.",
    "maintainer": "Zehntech Technologies Inc.",
    "contributor": "Zehntech Technologies Inc.",

    "website": "https://www.zehntech.com/",
    "support": "odoo-support@zehntech.com",

    "depends": [
        "website",
        "auth_signup", 
    ],

    "assets": {
        "web.assets_frontend": [
            "advance_login_form/static/src/scss/login_form.scss",
            "advance_login_form/static/src/scss/custom.scss",
        ],
    },

    "data": [
        "static/src/xml/login.xml",
        "views/templates.xml",
        "views/res_config_settings_views.xml",
    ],

    "i18n": [
        "i18n/es.po",   
        "i18n/de.po",   
        "i18n/fr.po",   
        "i18n/ja_JP.po" 
    ],

    "images": ["static/description/banner.gif"],

    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,

    "price": 0.00,
    "currency": "USD",
}

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR UAE Backend Theme",
    "version": "18.0.1.0.8",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "First-party backend theme studio and UI refresh for the HR UAE suite.",
    "author": "HrProject Team",
    "website": "https://example.com/hr-uae",
    "depends": [
        "web",
        "hr_uae_base",
    ],
    "data": [
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_uae_backend_theme/static/src/js/apps_menu_glass.esm.js",
            "hr_uae_backend_theme/static/src/js/theme_service.esm.js",
            "hr_uae_backend_theme/static/src/js/theme_switcher.esm.js",
            "hr_uae_backend_theme/static/src/xml/theme_switcher.xml",
            "hr_uae_backend_theme/static/src/scss/backend_theme.scss",
        ],
    },
    "installable": True,
    "application": False,
}

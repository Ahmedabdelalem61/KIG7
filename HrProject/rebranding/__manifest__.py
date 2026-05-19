# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Rebranding",
    "version": "18.0.1.0.4",
    "license": "LGPL-3",
    "category": "Hidden",
    "summary": "Hide Odoo branding in the user menu and align custom dashboard spacing.",
    "author": "HrProject Team",
    "depends": [
        "web",
        "web_tour",
    ],
    "assets": {
        "web.assets_backend": [
            "rebranding/static/src/js/user_menu_hide.esm.js",
            "rebranding/static/src/js/tour_service_patch.esm.js",
            "rebranding/static/src/scss/dashboard_padding.scss",
        ],
    },
    "installable": True,
    "application": False,
}

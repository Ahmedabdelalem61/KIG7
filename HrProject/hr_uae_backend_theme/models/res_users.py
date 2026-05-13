# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

HR_THEME_PRESET_SELECTION = [
    ("oasis", "Oasis"),
    ("lagoon", "Lagoon"),
    ("ember", "Ember"),
]
HR_THEME_DENSITY_SELECTION = [
    ("comfortable", "Comfortable"),
    ("compact", "Compact"),
]
HR_THEME_CHROME_SELECTION = [
    ("floating", "Floating"),
    ("flat", "Flat"),
]
HR_THEME_FONT_SCALE_SELECTION = [
    ("default", "Default"),
    ("large", "Large"),
]
HR_THEME_MENU_STYLE_SELECTION = [
    ("spotlight", "Spotlight"),
    ("compact", "Compact"),
]
HR_THEME_NAV_MENU_STYLE_SELECTION = [
    ("minimal", "Minimal"),
    ("chip", "Chip"),
    ("classic", "Classic"),
]
HR_THEME_NAV_ICON_TONE_SELECTION = [
    ("preset", "Match preset"),
    ("accent", "Accent"),
    ("neutral", "Neutral"),
]
HR_THEME_APPS_MENU_GLASS_TINT_SELECTION = [
    ("frost", "Frost"),
    ("pearl", "Pearl"),
    ("accent", "Accent"),
    ("mist", "Mist"),
    ("depth", "Depth"),
    ("glow", "Glow"),
]

HR_THEME_PREFERENCE_MAP = {
    "preset": (
        "hr_theme_preset",
        "hr_uae_backend_theme.default_preset",
        "oasis",
        HR_THEME_PRESET_SELECTION,
    ),
    "density": (
        "hr_theme_density",
        "hr_uae_backend_theme.default_density",
        "comfortable",
        HR_THEME_DENSITY_SELECTION,
    ),
    "chrome": (
        "hr_theme_chrome",
        "hr_uae_backend_theme.default_chrome",
        "floating",
        HR_THEME_CHROME_SELECTION,
    ),
    "font_scale": (
        "hr_theme_font_scale",
        "hr_uae_backend_theme.default_font_scale",
        "default",
        HR_THEME_FONT_SCALE_SELECTION,
    ),
    "menu_style": (
        "hr_theme_menu_style",
        "hr_uae_backend_theme.default_menu_style",
        "spotlight",
        HR_THEME_MENU_STYLE_SELECTION,
    ),
    "nav_menu_style": (
        "hr_theme_nav_menu_style",
        "hr_uae_backend_theme.default_nav_menu_style",
        "minimal",
        HR_THEME_NAV_MENU_STYLE_SELECTION,
    ),
    "nav_icon_tone": (
        "hr_theme_nav_icon_tone",
        "hr_uae_backend_theme.default_nav_icon_tone",
        "preset",
        HR_THEME_NAV_ICON_TONE_SELECTION,
    ),
}
HR_THEME_BRAND_NAME_PARAM = "hr_uae_backend_theme.brand_name"
HR_THEME_GLASS_BLUR_PARAM = "hr_uae_backend_theme.default_apps_menu_glass_blur"
HR_THEME_GLASS_TINT_PARAM = "hr_uae_backend_theme.default_apps_menu_glass_tint"


class ResUsers(models.Model):
    _inherit = "res.users"

    hr_theme_preset = fields.Selection(
        selection=HR_THEME_PRESET_SELECTION,
        string="Theme Preset",
        default=lambda self: self._get_hr_theme_default_value("preset"),
        required=True,
    )
    hr_theme_density = fields.Selection(
        selection=HR_THEME_DENSITY_SELECTION,
        string="Density",
        default=lambda self: self._get_hr_theme_default_value("density"),
        required=True,
    )
    hr_theme_chrome = fields.Selection(
        selection=HR_THEME_CHROME_SELECTION,
        string="Shell Style",
        default=lambda self: self._get_hr_theme_default_value("chrome"),
        required=True,
    )
    hr_theme_font_scale = fields.Selection(
        selection=HR_THEME_FONT_SCALE_SELECTION,
        string="Font Scale",
        default=lambda self: self._get_hr_theme_default_value("font_scale"),
        required=True,
    )
    hr_theme_menu_style = fields.Selection(
        selection=HR_THEME_MENU_STYLE_SELECTION,
        string="App Menu Style",
        default=lambda self: self._get_hr_theme_default_value("menu_style"),
        required=True,
    )
    hr_theme_nav_menu_style = fields.Selection(
        selection=HR_THEME_NAV_MENU_STYLE_SELECTION,
        string="Top Menu Style",
        default=lambda self: self._get_hr_theme_default_value("nav_menu_style"),
        required=True,
    )
    hr_theme_nav_icon_tone = fields.Selection(
        selection=HR_THEME_NAV_ICON_TONE_SELECTION,
        string="Navbar Icon Tone",
        default=lambda self: self._get_hr_theme_default_value("nav_icon_tone"),
        required=True,
    )
    hr_theme_apps_menu_glass_blur = fields.Integer(
        string="Apps Grid Glass Blur %",
        default=lambda self: self._get_hr_theme_glass_blur_default(),
        required=True,
    )
    hr_theme_apps_menu_glass_tint = fields.Selection(
        selection=HR_THEME_APPS_MENU_GLASS_TINT_SELECTION,
        string="Apps Grid Glass Tint",
        default=lambda self: self._get_hr_theme_glass_tint_default(),
        required=True,
    )

    @api.model
    def _get_hr_theme_glass_blur_default(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(HR_THEME_GLASS_BLUR_PARAM, "72")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = 72
        return max(0, min(100, value))

    @api.model
    def _get_hr_theme_glass_tint_default(self):
        allowed = {value for value, _label in HR_THEME_APPS_MENU_GLASS_TINT_SELECTION}
        raw = self.env["ir.config_parameter"].sudo().get_param(HR_THEME_GLASS_TINT_PARAM, "frost")
        return raw if raw in allowed else "frost"

    @api.model
    def _get_hr_theme_default_value(self, preference_key):
        field_name, param_key, fallback, selection = HR_THEME_PREFERENCE_MAP[preference_key]
        del field_name
        allowed_values = {value for value, _label in selection}
        param_value = self.env["ir.config_parameter"].sudo().get_param(param_key, fallback)
        return param_value if param_value in allowed_values else fallback

    @api.model
    def _get_hr_theme_defaults(self):
        base = {
            key: self._get_hr_theme_default_value(key)
            for key in HR_THEME_PREFERENCE_MAP
        }
        base["apps_menu_glass_blur"] = self._get_hr_theme_glass_blur_default()
        base["apps_menu_glass_tint"] = self._get_hr_theme_glass_tint_default()
        return base

    @api.model
    def _get_hr_theme_default_field_values(self):
        defaults = self._get_hr_theme_defaults()
        out = {
            field_name: defaults[key]
            for key, (field_name, _param_key, _fallback, _selection) in HR_THEME_PREFERENCE_MAP.items()
        }
        out["hr_theme_apps_menu_glass_blur"] = defaults["apps_menu_glass_blur"]
        out["hr_theme_apps_menu_glass_tint"] = defaults["apps_menu_glass_tint"]
        return out

    @api.model
    def _normalize_hr_theme_glass_blur(self, raw_value, fallback):
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            value = int(fallback)
        return max(0, min(100, value))

    @api.model
    def _normalize_hr_theme_glass_tint(self, raw_value, fallback):
        allowed = {value for value, _label in HR_THEME_APPS_MENU_GLASS_TINT_SELECTION}
        if raw_value in allowed:
            return raw_value
        if fallback in allowed:
            return fallback
        return "frost"

    @api.model
    def _normalize_hr_theme_preferences(self, preferences=None):
        preferences = preferences if isinstance(preferences, dict) else {}
        defaults = self._get_hr_theme_defaults()
        normalized = {}
        field_values = {}
        for key, (field_name, _param_key, _fallback, selection) in HR_THEME_PREFERENCE_MAP.items():
            allowed_values = {value for value, _label in selection}
            value = preferences.get(key, defaults[key])
            if value not in allowed_values:
                value = defaults[key]
            normalized[key] = value
            field_values[field_name] = value

        blur = self._normalize_hr_theme_glass_blur(
            preferences.get("apps_menu_glass_blur", defaults["apps_menu_glass_blur"]),
            defaults["apps_menu_glass_blur"],
        )
        tint = self._normalize_hr_theme_glass_tint(
            preferences.get("apps_menu_glass_tint", defaults["apps_menu_glass_tint"]),
            defaults["apps_menu_glass_tint"],
        )
        normalized["apps_menu_glass_blur"] = blur
        normalized["apps_menu_glass_tint"] = tint
        field_values["hr_theme_apps_menu_glass_blur"] = blur
        field_values["hr_theme_apps_menu_glass_tint"] = tint
        return normalized, field_values

    def _get_hr_theme_payload(self):
        self.ensure_one()
        defaults = self._get_hr_theme_defaults()
        preferences = {}
        for key, (field_name, _param_key, _fallback, selection) in HR_THEME_PREFERENCE_MAP.items():
            allowed_values = {value for value, _label in selection}
            field_value = getattr(self, field_name)
            preferences[key] = field_value if field_value in allowed_values else defaults[key]

        preferences["apps_menu_glass_blur"] = self._normalize_hr_theme_glass_blur(
            getattr(self, "hr_theme_apps_menu_glass_blur"),
            defaults["apps_menu_glass_blur"],
        )
        preferences["apps_menu_glass_tint"] = self._normalize_hr_theme_glass_tint(
            getattr(self, "hr_theme_apps_menu_glass_tint"),
            defaults["apps_menu_glass_tint"],
        )
        brand_name = (
            self.env["ir.config_parameter"].sudo().get_param(
                HR_THEME_BRAND_NAME_PARAM,
                "HR UAE Admin",
            )
            or "HR UAE Admin"
        )
        return {
            "brand_name": brand_name,
            "defaults": defaults,
            "preferences": preferences,
        }

    @api.model
    def get_hr_theme_payload(self):
        return self.env.user._get_hr_theme_payload()

    @api.model
    def set_hr_theme_preferences(self, preferences):
        _normalized, field_values = self._normalize_hr_theme_preferences(preferences)
        self.env.user.sudo().write(field_values)
        return self.env.user._get_hr_theme_payload()

    @api.model
    def reset_hr_theme_preferences(self):
        self.env.user.sudo().write(self._get_hr_theme_default_field_values())
        return self.env.user._get_hr_theme_payload()

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .res_users import (
    HR_THEME_APPS_MENU_GLASS_TINT_SELECTION,
    HR_THEME_BRAND_NAME_PARAM,
    HR_THEME_CHROME_SELECTION,
    HR_THEME_DENSITY_SELECTION,
    HR_THEME_FONT_SCALE_SELECTION,
    HR_THEME_MENU_STYLE_SELECTION,
    HR_THEME_NAV_ICON_TONE_SELECTION,
    HR_THEME_NAV_MENU_STYLE_SELECTION,
    HR_THEME_PRESET_SELECTION,
)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_theme_brand_name = fields.Char(
        string="Brand Name",
        config_parameter=HR_THEME_BRAND_NAME_PARAM,
        default="HR UAE Admin",
    )
    hr_theme_default_preset = fields.Selection(
        selection=HR_THEME_PRESET_SELECTION,
        string="Default Preset",
        config_parameter="hr_uae_backend_theme.default_preset",
        default="oasis",
    )
    hr_theme_default_density = fields.Selection(
        selection=HR_THEME_DENSITY_SELECTION,
        string="Default Density",
        config_parameter="hr_uae_backend_theme.default_density",
        default="comfortable",
    )
    hr_theme_default_chrome = fields.Selection(
        selection=HR_THEME_CHROME_SELECTION,
        string="Default Shell Style",
        config_parameter="hr_uae_backend_theme.default_chrome",
        default="floating",
    )
    hr_theme_default_font_scale = fields.Selection(
        selection=HR_THEME_FONT_SCALE_SELECTION,
        string="Default Font Scale",
        config_parameter="hr_uae_backend_theme.default_font_scale",
        default="default",
    )
    hr_theme_default_menu_style = fields.Selection(
        selection=HR_THEME_MENU_STYLE_SELECTION,
        string="Default App Menu Style",
        config_parameter="hr_uae_backend_theme.default_menu_style",
        default="spotlight",
    )
    hr_theme_default_nav_menu_style = fields.Selection(
        selection=HR_THEME_NAV_MENU_STYLE_SELECTION,
        string="Default Top Menu Style",
        config_parameter="hr_uae_backend_theme.default_nav_menu_style",
        default="minimal",
    )
    hr_theme_default_nav_icon_tone = fields.Selection(
        selection=HR_THEME_NAV_ICON_TONE_SELECTION,
        string="Default Navbar Icon Tone",
        config_parameter="hr_uae_backend_theme.default_nav_icon_tone",
        default="preset",
    )
    hr_theme_default_apps_menu_glass_blur = fields.Integer(
        string="Default Apps Grid Glass Blur %",
        config_parameter="hr_uae_backend_theme.default_apps_menu_glass_blur",
        default=72,
    )
    hr_theme_default_apps_menu_glass_tint = fields.Selection(
        selection=HR_THEME_APPS_MENU_GLASS_TINT_SELECTION,
        string="Default Apps Grid Glass Tint",
        config_parameter="hr_uae_backend_theme.default_apps_menu_glass_tint",
        default="frost",
    )

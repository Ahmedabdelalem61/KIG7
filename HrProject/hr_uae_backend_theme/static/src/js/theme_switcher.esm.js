import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownGroup } from "@web/core/dropdown/dropdown_group";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { Component, useState } from "@odoo/owl";

export class HrUaeThemeSwitcher extends Component {
    static template = "hr_uae_backend_theme.ThemeSwitcher";
    static components = { Dropdown, DropdownGroup };
    static props = {};

    setup() {
        this.notification = useService("notification");
        this.themeService = useService("hr_uae_backend_theme");
        this.options = this.themeService.getOptions();
        this.state = useState({
            ...this.themeService.getPreferences(),
            brandName: this.themeService.getBrandName(),
            isSaving: false,
        });
    }

    get presetOptions() {
        return this.options.preset;
    }

    get densityOptions() {
        return this.options.density;
    }

    get chromeOptions() {
        return this.options.chrome;
    }

    get fontScaleOptions() {
        return this.options.font_scale;
    }

    get menuStyleOptions() {
        return this.options.menu_style;
    }

    get navMenuStyleOptions() {
        return this.options.nav_menu_style;
    }

    get navIconToneOptions() {
        return this.options.nav_icon_tone;
    }

    get glassTintSwatches() {
        return this.themeService.getGlassTintSwatches(this.state.preset);
    }

    basePreferences() {
        return {
            preset: this.state.preset,
            density: this.state.density,
            chrome: this.state.chrome,
            font_scale: this.state.font_scale,
            menu_style: this.state.menu_style,
            nav_menu_style: this.state.nav_menu_style,
            nav_icon_tone: this.state.nav_icon_tone,
            apps_menu_glass_blur: this.state.apps_menu_glass_blur,
            apps_menu_glass_tint: this.state.apps_menu_glass_tint,
        };
    }

    isSelected(key, value) {
        return this.state[key] === value;
    }

    chipClass(key, value) {
        return this.isSelected(key, value)
            ? "o_hr_theme_chip is-selected"
            : "o_hr_theme_chip";
    }

    presetClass(value) {
        return this.isSelected("preset", value)
            ? "o_hr_theme_preset is-selected"
            : "o_hr_theme_preset";
    }

    async updateTheme(key, value) {
        if (this.state[key] === value || this.state.isSaving) {
            return;
        }
        const nextPreferences = {
            ...this.basePreferences(),
            [key]: value,
        };
        this.state.isSaving = true;
        this.themeService.apply(nextPreferences);
        Object.assign(this.state, nextPreferences);
        try {
            const payload = await this.themeService.save(nextPreferences);
            Object.assign(this.state, payload.preferences);
        } catch (_error) {
            Object.assign(this.state, this.themeService.getPreferences());
            this.themeService.apply(this.themeService.getPreferences());
            this.notification.add(_t("Theme update failed."), { type: "danger" });
        } finally {
            this.state.isSaving = false;
        }
    }

    onGlassBlurInput(ev) {
        const value = Number.parseInt(ev.target.value, 10);
        if (Number.isNaN(value)) {
            return;
        }
        this.state.apps_menu_glass_blur = value;
        this.themeService.apply({
            ...this.basePreferences(),
            apps_menu_glass_blur: value,
        });
    }

    async onGlassBlurCommit(ev) {
        const value = Number.parseInt(ev.target.value, 10);
        if (Number.isNaN(value) || this.state.isSaving) {
            return;
        }
        const nextPreferences = {
            ...this.basePreferences(),
            apps_menu_glass_blur: value,
        };
        this.state.isSaving = true;
        try {
            const payload = await this.themeService.save(nextPreferences);
            Object.assign(this.state, payload.preferences);
        } catch (_error) {
            Object.assign(this.state, this.themeService.getPreferences());
            this.themeService.apply(this.themeService.getPreferences());
            this.notification.add(_t("Theme update failed."), { type: "danger" });
        } finally {
            this.state.isSaving = false;
        }
    }

    async resetTheme() {
        if (this.state.isSaving) {
            return;
        }
        this.state.isSaving = true;
        try {
            const payload = await this.themeService.reset();
            Object.assign(this.state, payload.preferences);
        } catch (_error) {
            this.notification.add(_t("Theme reset failed."), { type: "danger" });
        } finally {
            this.state.isSaving = false;
        }
    }
}

const systrayItem = {
    Component: HrUaeThemeSwitcher,
};

registry.category("systray").add(
    "hr_uae_backend_theme.switcher",
    systrayItem,
    { sequence: 8 }
);

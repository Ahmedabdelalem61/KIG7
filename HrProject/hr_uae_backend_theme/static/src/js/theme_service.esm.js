import { registry } from "@web/core/registry";
import { session } from "@web/session";

import { getGlassTintSwatches } from "./apps_menu_glass.esm.js";

const FALLBACKS = {
    preset: "oasis",
    density: "comfortable",
    chrome: "floating",
    font_scale: "default",
    menu_style: "spotlight",
    nav_menu_style: "minimal",
    nav_icon_tone: "preset",
    apps_menu_glass_blur: 72,
    apps_menu_glass_tint: "frost",
};

export const THEME_OPTIONS = {
    preset: [
        {
            value: "oasis",
            label: "Oasis",
            caption: "Warm surfaces with a calm teal accent.",
            preview: ["#0f766e", "#e8bb86"],
        },
        {
            value: "lagoon",
            label: "Lagoon",
            caption: "Cool glassy blues for a cleaner operational feel.",
            preview: ["#0284c7", "#34d399"],
        },
        {
            value: "ember",
            label: "Ember",
            caption: "Ivory and terracotta for a stronger executive tone.",
            preview: ["#c2410c", "#f59e0b"],
        },
    ],
    density: [
        { value: "comfortable", label: "Comfortable" },
        { value: "compact", label: "Compact" },
    ],
    chrome: [
        { value: "floating", label: "Floating" },
        { value: "flat", label: "Flat" },
    ],
    font_scale: [
        { value: "default", label: "Default" },
        { value: "large", label: "Large" },
    ],
    menu_style: [
        { value: "spotlight", label: "Spotlight" },
        { value: "compact", label: "Compact" },
    ],
    nav_menu_style: [
        { value: "minimal", label: "Minimal" },
        { value: "chip", label: "Chip" },
        { value: "classic", label: "Classic" },
    ],
    nav_icon_tone: [
        { value: "preset", label: "Match preset" },
        { value: "accent", label: "Accent" },
        { value: "neutral", label: "Neutral" },
    ],
};

const DATASET_MAP = {
    preset: "hrThemePreset",
    density: "hrThemeDensity",
    chrome: "hrThemeChrome",
    font_scale: "hrThemeFontScale",
    menu_style: "hrThemeMenuStyle",
    nav_menu_style: "hrThemeNavMenuStyle",
    nav_icon_tone: "hrThemeNavIconTone",
};

const GLASS_TINT_OPTIONS = [
    { value: "frost", label: "Frost" },
    { value: "pearl", label: "Pearl" },
    { value: "accent", label: "Accent" },
    { value: "mist", label: "Mist" },
    { value: "depth", label: "Depth" },
    { value: "glow", label: "Glow" },
];

function clampBlur(value, fallback) {
    const n = Number.parseInt(String(value), 10);
    if (Number.isNaN(n)) {
        return Number.parseInt(String(fallback), 10) || 72;
    }
    return Math.min(100, Math.max(0, n));
}

function normalizeGlassTint(value, fallback) {
    const allowed = new Set(GLASS_TINT_OPTIONS.map((o) => o.value));
    const v = typeof value === "string" ? value : "";
    if (allowed.has(v)) {
        return v;
    }
    return allowed.has(fallback) ? fallback : "frost";
}

function clonePayload(payload) {
    return {
        brand_name: payload.brand_name,
        defaults: { ...payload.defaults },
        preferences: { ...payload.preferences },
    };
}

function normalizePreferences(preferences = {}, defaults = FALLBACKS) {
    const normalized = {};
    for (const [key, options] of Object.entries(THEME_OPTIONS)) {
        const allowedValues = new Set(options.map((option) => option.value));
        const fallback = defaults[key] ?? FALLBACKS[key];
        const value = preferences[key];
        normalized[key] = allowedValues.has(value) ? value : fallback;
    }
    normalized.apps_menu_glass_blur = clampBlur(
        preferences.apps_menu_glass_blur,
        defaults.apps_menu_glass_blur ?? FALLBACKS.apps_menu_glass_blur
    );
    normalized.apps_menu_glass_tint = normalizeGlassTint(
        preferences.apps_menu_glass_tint,
        defaults.apps_menu_glass_tint ?? FALLBACKS.apps_menu_glass_tint
    );
    return normalized;
}

function normalizePayload(payload = {}) {
    const defaults = normalizePreferences(payload.defaults || {}, FALLBACKS);
    return {
        brand_name: payload.brand_name || "HR UAE Admin",
        defaults,
        preferences: normalizePreferences(payload.preferences || {}, defaults),
    };
}

function applyTheme(preferences) {
    const root = document.documentElement;
    root.classList.add("o_hr_uae_backend_theme");
    if (document.body) {
        document.body.classList.add("o_hr_uae_backend_theme");
    } else {
        document.addEventListener(
            "DOMContentLoaded",
            () => document.body?.classList.add("o_hr_uae_backend_theme"),
            { once: true }
        );
    }
    for (const [key, dataKey] of Object.entries(DATASET_MAP)) {
        root.dataset[dataKey] = preferences[key];
    }
    root.dataset.hrThemeAppsMenuGlassBlur = String(preferences.apps_menu_glass_blur);
    root.dataset.hrThemeAppsMenuGlassTint = preferences.apps_menu_glass_tint;
    root.style.setProperty("--hr-apps-menu-glass-blur-pct", String(preferences.apps_menu_glass_blur));
}

export const hrUaeBackendThemeService = {
    dependencies: ["orm"],
    start(_env, { orm }) {
        let payload = normalizePayload(session.hr_uae_backend_theme || {});
        applyTheme(payload.preferences);

        const updatePayload = (nextPayload) => {
            payload = normalizePayload(nextPayload);
            session.hr_uae_backend_theme = clonePayload(payload);
            applyTheme(payload.preferences);
            return clonePayload(payload);
        };

        return {
            getBrandName() {
                return payload.brand_name;
            },
            getOptions() {
                return THEME_OPTIONS;
            },
            getGlassTintSwatches(preset) {
                return getGlassTintSwatches(preset);
            },
            getPayload() {
                return clonePayload(payload);
            },
            getPreferences() {
                return { ...payload.preferences };
            },
            apply(preferences) {
                payload.preferences = normalizePreferences(preferences, payload.defaults);
                session.hr_uae_backend_theme = clonePayload(payload);
                applyTheme(payload.preferences);
                return { ...payload.preferences };
            },
            async save(preferences) {
                const nextPayload = await orm.call(
                    "res.users",
                    "set_hr_theme_preferences",
                    [preferences]
                );
                return updatePayload(nextPayload);
            },
            async reset() {
                const nextPayload = await orm.call(
                    "res.users",
                    "reset_hr_theme_preferences",
                    []
                );
                return updatePayload(nextPayload);
            },
        };
    },
};

registry.category("services").add("hr_uae_backend_theme", hrUaeBackendThemeService);

/** Swatch previews for Theme Studio (stronger contrast so chips read clearly in the menu). */
const TINT_KEYS = ["frost", "pearl", "accent", "mist", "depth", "glow"];

const SWATCH_BY_PRESET = {
    oasis: {
        frost: "linear-gradient(135deg, #fffdf5 0%, #f0e6d8 55%, #e8d4bc 100%)",
        pearl: "linear-gradient(135deg, #fde8d4 0%, #f5cfa8 50%, #e8bb86 100%)",
        accent: "linear-gradient(135deg, #0f766e 0%, #14b8a6 45%, #5eead4 100%)",
        mist: "linear-gradient(135deg, #ccfbf1 0%, #5eead4 40%, #0d9488 100%)",
        depth: "linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%)",
        glow: "linear-gradient(135deg, #fcd34d 0%, #f59e0b 50%, #d97706 100%)",
    },
    lagoon: {
        frost: "linear-gradient(135deg, #f8fafc 0%, #e0f2fe 55%, #bae6fd 100%)",
        pearl: "linear-gradient(135deg, #dbeafe 0%, #93c5fd 50%, #3b82f6 100%)",
        accent: "linear-gradient(135deg, #0369a1 0%, #0ea5e9 50%, #38bdf8 100%)",
        mist: "linear-gradient(135deg, #d1fae5 0%, #34d399 45%, #059669 100%)",
        depth: "linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #334155 100%)",
        glow: "linear-gradient(135deg, #a7f3d0 0%, #2dd4bf 50%, #0d9488 100%)",
    },
    ember: {
        frost: "linear-gradient(135deg, #fffbeb 0%, #fde68a 35%, #fcd34d 100%)",
        pearl: "linear-gradient(135deg, #ffedd5 0%, #fdba74 45%, #ea580c 100%)",
        accent: "linear-gradient(135deg, #9a3412 0%, #ea580c 50%, #fb923c 100%)",
        mist: "linear-gradient(135deg, #fef3c7 0%, #fbbf24 50%, #d97706 100%)",
        depth: "linear-gradient(135deg, #431407 0%, #7c2d12 50%, #9a3412 100%)",
        glow: "linear-gradient(135deg, #fef08a 0%, #f59e0b 50%, #b45309 100%)",
    },
};

export function getGlassTintSwatches(preset) {
    const key = SWATCH_BY_PRESET[preset] ? preset : "oasis";
    const row = SWATCH_BY_PRESET[key];
    return TINT_KEYS.map((value) => ({
        value,
        /** Full CSS for `t-att-style` (string form — reliable on `<button>`). */
        styleAttr: `background-image: ${row[value]}; background-size: cover; background-repeat: no-repeat; background-color: #e2e8f0;`,
    }));
}

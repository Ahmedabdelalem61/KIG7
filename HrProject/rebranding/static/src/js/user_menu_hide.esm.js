/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { UserMenu } from "@web/webclient/user_menu/user_menu";

/** Registry keys to drop when modules register menu items. */
const HIDDEN_USER_MENU_KEYS = new Set([
    "documentation",
    "support",
    "odoo_account",
    "web_tour.tour_enabled",
]);

/** `id` field on rendered menu element objects (see web user_menu_items.js). */
const HIDDEN_USER_MENU_IDS = new Set([
    "documentation",
    "support",
    "account",
    "web_tour.tour_enabled",
]);

const userMenuRegistry = registry.category("user_menuitems");

function stripHiddenUserMenuItems() {
    for (const key of HIDDEN_USER_MENU_KEYS) {
        if (userMenuRegistry.contains(key)) {
            userMenuRegistry.remove(key);
        }
    }
}

function isHiddenMenuElement(element) {
    return Boolean(element?.id && HIDDEN_USER_MENU_IDS.has(element.id));
}

stripHiddenUserMenuItems();

userMenuRegistry.addEventListener("UPDATE", () => {
    stripHiddenUserMenuItems();
});

patch(UserMenu.prototype, {
    getElements() {
        return super.getElements(...arguments).filter((element) => !isHiddenMenuElement(element));
    },
});

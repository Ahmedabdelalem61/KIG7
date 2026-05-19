/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { menuService } from "@web/webclient/menus/menu_service";
import { patch } from "@web/core/utils/patch";

patch(menuService, {
    async start(env) {
        const menus = await super.start(env);
        const originalSetCurrentMenu = menus.setCurrentMenu.bind(menus);
        menus.setCurrentMenu = (menu) => {
            originalSetCurrentMenu(menu);
            const $ = window.jQuery;
            if (!$) {
                return;
            }
            $("body").removeClass("sh_sidebar_background_enterprise");
            $(".sh_search_container").css("display", "none");
            $(".sh_entmate_theme_appmenu_div").removeClass("show");
            $(".o_action_manager").removeClass("d-none");
            $(".o_menu_brand").css("display", "block");
            $(".full").removeClass("sidebar_arrow");
            $(".o_menu_sections").css("display", "flex");
            browser.dispatchEvent(new CustomEvent("sh-close-apps-menu"));
        };
        return menus;
    },
});

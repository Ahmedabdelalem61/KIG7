/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { tourService } from "@web_tour/tour_service/tour_service";

/**
 * web_tour registers the "Onboarding" switch in tourService.start() (async),
 * after all modules are loaded — a registry.add monkey-patch is not reliable.
 */
patch(tourService, {
    async start(env, deps) {
        const result = await super.start(env, deps);
        const userMenuRegistry = registry.category("user_menuitems");
        if (userMenuRegistry.contains("web_tour.tour_enabled")) {
            userMenuRegistry.remove("web_tour.tour_enabled");
        }
        return result;
    },
});

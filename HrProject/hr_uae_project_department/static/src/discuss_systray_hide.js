/** @odoo-module **/

import { registry } from "@web/core/registry";

const systray = registry.category("systray");

for (const key of ["mail.messaging_menu", "mail.activity_menu", "discuss.CallMenu"]) {
    if (systray.contains(key)) {
        systray.remove(key);
    }
}

/** @odoo-module **/

import { registry } from "@web/core/registry";

const resetStateStep = {
    trigger: ".o_main_navbar",
    run() {
        window.__shThemeTour.reset();
    },
};

registry.category("web_tour.tours").add("sh_entmate_theme_login_frontend", {
    url: "/web/login",
    steps: () => [
        {
            trigger: "body.bg-100",
        },
        {
            trigger: "body .o_database_list",
        },
        {
            trigger: 'input[name="login"]',
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_navigation", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: "#app_toggle",
            run: "click",
        },
        {
            trigger: ".sh_entmate_theme_appmenu_div.show",
        },
        {
            trigger: '.sh_app_name:contains("Sh Theme Tour Partners")',
            run: "click",
        },
        {
            trigger: ".o_list_renderer .o_data_row",
            timeout: 30000,
        },
        {
            trigger: '.o_data_row:contains("Sh Theme Tour Search Partner")',
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_view_refresh", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: "#app_toggle",
            run: "click",
        },
        {
            trigger: ".sh_entmate_theme_appmenu_div.show",
        },
        {
            trigger: '.sh_app_name:contains("Sh Theme Tour Partners")',
            run: "click",
        },
        {
            trigger: ".o_list_renderer .o_data_row",
            timeout: 30000,
        },
        {
            trigger: "button.sh_refresh",
            run: "click",
        },
        {
            trigger: ".o_list_renderer .o_data_row",
        },
        {
            trigger: ".o_switch_view.o_kanban",
            run: "click",
        },
        {
            trigger: ".o_kanban_renderer",
            timeout: 30000,
        },
        {
            trigger: ".o_control_panel button.sh_refresh",
            run: "click",
        },
        {
            trigger: ".o_kanban_renderer",
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_list_group_expand", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: "#app_toggle",
            run: "click",
        },
        {
            trigger: ".sh_entmate_theme_appmenu_div.show",
        },
        {
            trigger: '.sh_app_name:contains("Sh Theme Tour Partners")',
            run: "click",
        },
        {
            trigger: ".o_list_renderer .o_data_row",
            timeout: 30000,
        },
        {
            trigger: '.o_control_panel .o_list_buttons button.fa-expand[title="Expand groups"]',
            timeout: 30000,
        },
        {
            trigger: '.o_control_panel .o_list_buttons button.fa-expand[title="Expand groups"]',
            run: "click",
        },
        {
            trigger: '.o_control_panel .o_list_buttons button.fa-compress[title="Collapse groups"]',
            run: "click",
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_theme_backend", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: ".theme_configuration",
            run: "click",
        },
        {
            trigger: ".backmate_theme_layout.sh_theme_model",
        },
        {
            trigger: ".backmate_theme_layout .theme_color_box",
            run() {
                const options = [
                    ...document.querySelectorAll(".backmate_theme_layout .theme_color_box"),
                ];
                const target = options.find(
                    (option) => !option.querySelector('input[name="themeColor"]')?.checked
                );
                target?.click();
                window.__shThemeTour.markReload();
            },
        },
        {
            trigger: 'body[data-sh-theme-reload-count="1"]',
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_announcement_popup", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: ".o_main_navbar",
            run() {
                return window.__shThemeTour.triggerPopupAnnouncement(
                    "Sh Theme Tour Popup Announcement"
                );
            },
        },
        {
            trigger: ".o_notification_manager .o_notification",
            timeout: 30000,
        },
        {
            trigger: '.o_notification_content:contains("Sh Theme Tour Popup Announcement")',
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_discuss_chatter", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: "#app_toggle",
            run: "click",
        },
        {
            trigger: ".sh_entmate_theme_appmenu_div.show",
            run() {
                window.__shThemeTour.triggerBodySearch();
            },
        },
        {
            trigger: "body.sh_sidebar_background_enterprise .usermenu_search_input:visible",
            run() {
                return window.__shThemeTour.runGlobalSearch("Sh Theme Tour Search Partner");
            },
        },
        {
            trigger:
                '.sh_search_results .dropdown-item:contains("Sh Theme Tour Search Partner")',
            run: "click",
        },
        {
            trigger: '.o_content:contains("Sh Theme Tour Search Partner")',
            timeout: 30000,
        },
        {
            trigger: ".o-mail-Chatter, .o_Chatter",
        },
        {
            trigger: ".o-mail-Message.sh_right_chat, .o-mail-Message.sh_left_chat",
            timeout: 30000,
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_language_switch", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: ".sh_language_selector .fa-language",
            run: "click",
        },
        {
            trigger: ".o-dropdown--menu .o-mail-ActivityGroup",
            timeout: 30000,
            run() {
                return window.__shThemeTour
                    .clickLanguageOption((label) => /french|français/i.test(label))
                    .catch(() => window.__shThemeTour.switchUserLanguage("fr_FR"));
            },
        },
        {
            trigger: ".o_main_navbar",
            run() {
                return window.__shThemeTour.verifySessionLanguage("fr_FR");
            },
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_multitab_persist", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: ".o_main_navbar",
            run() {
                window.__shThemeTour.closeAppDrawer();
                const actionMatch = window.location.pathname.match(/action-(\d+)/);
                const actionId = actionMatch ? parseInt(actionMatch[1], 10) : 0;
                return window.__shThemeTour.addMultiTab({
                    name: "Sh Theme Tour Partners App",
                    url: `#action=${actionId}`,
                    actionId,
                    menuId: actionId,
                    menu_xmlid: "",
                });
            },
        },
        {
            trigger: 'body.multi_tab_enabled .multi_tab_div:contains("Sh Theme Tour Partners")',
        },
        {
            trigger: ".o_main_navbar",
            run() {
                window.__shThemeTour.markReload();
                return window.__shThemeTour.jsonRpcRoute("/get/mutli/tab", {}).then(
                    (records) => {
                        window.__shThemeTour.renderMultiTabs(records);
                    }
                );
            },
        },
        {
            trigger: 'body.multi_tab_enabled .multi_tab_div:contains("Sh Theme Tour Partners")',
        },
    ],
});

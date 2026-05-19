/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc as jsonrpc } from "@web/core/network/rpc";

const resetStateStep = {
    trigger: ".o_main_navbar",
    run() {
        window.__shThemeTour.reset();
    },
};

registry.category("web_tour.tours").add("sh_entmate_theme_smoke_shell", {
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
        },
        {
            trigger: '#object1:contains("Sh Theme Tour Announcement")',
        },
        {
            trigger: "#moon_button:visible",
            run: "click",
        },
        {
            trigger: "#sun_button:visible",
            run: "click",
        },
        {
            trigger: ".open_calc",
            run: "click",
        },
        {
            trigger: ".calculator #display",
        },
        {
            trigger: "#seven",
            run: "click",
        },
        {
            trigger: ".calculator #display",
            run() {
                const display = document.querySelector(".calculator #display");
                if (!display || !display.textContent.includes("7")) {
                    throw new Error("Calculator display did not show 7");
                }
            },
        },
        {
            trigger: ".o_main_navbar",
            run() {
                const layout = window.__shThemeTour.ensureZoomControl();
                const toggle = layout?.querySelector(".sh_zoom");
                if (!toggle) {
                    throw new Error("Zoom toggle not available in systray");
                }
                toggle.click();
                window.__shThemeTour.applyZoomLevel(110);
                const label = layout.querySelector(".sh_full");
                if (!label?.textContent.includes("110")) {
                    throw new Error("Zoom label did not increase to 110%");
                }
                const contentDiv = document.querySelector(".o_content > div");
                if (contentDiv && !contentDiv.classList.contains("sh_zoom_110")) {
                    throw new Error("Zoom class sh_zoom_110 was not applied to content");
                }
                window.__shThemeTour.applyZoomLevel(100);
                if (!label.textContent.includes("100")) {
                    throw new Error("Zoom reset did not return to 100%");
                }
                if (contentDiv?.classList.contains("sh_zoom_110")) {
                    throw new Error("Zoom reset did not remove sh_zoom_110 class");
                }
            },
        },
        {
            trigger: ".sh_language_selector .fa-language",
            run: "click",
        },
        {
            trigger: ".o-dropdown--menu .o-mail-ActivityGroup",
            timeout: 30000,
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_quick_menu_and_todo", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: ".o_action_manager",
        },
        {
            trigger: ".sh_bookmark",
            run() {
                window.__shThemeTour.pinBookmarkFromUrl();
            },
        },
        {
            trigger: ".sh_bookmark.active",
        },
        {
            trigger: ".sh_bookmark.active .sh_bookmark_icon, .sh_bookmark.active .sh_bookmarked_icon",
            run: "click",
        },
        {
            trigger: ".sh_wqm_quick_menu_submenu_list_cls:visible",
        },
        {
            trigger: ".sh_bookmark_search",
        },
        {
            trigger: ".sh_bookmark_search",
            run: "edit Quick Seed 01",
        },
        {
            trigger: '.sh_search_result .sh_quick_menu_item:contains("Quick Seed 01")',
        },
        {
            trigger: '.sh_search_result .sh_quick_menu_item:contains("Quick Seed 01")',
            run() {
                const row = this.anchor;
                row.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
                const removeBtn = row.querySelector(
                    ".sh_wqm_remove_quick_menu_cls i, .sh_wqm_remove_quick_menu_cls"
                );
                removeBtn?.click();
            },
        },
        {
            trigger: "#todo_icon",
            run: "click",
        },
        {
            trigger: ".todo_layout.sh_theme_model",
        },
        {
            trigger: ".sh_add_todo_input",
            run() {
                return window.__shThemeTour.createTodo("Tour Added Todo");
            },
        },
        {
            trigger: '.sh_main_card:contains("Tour Added Todo") .sh_todo_checklist',
            run() {
                return window.__shThemeTour.markTodoDone("Tour Added Todo", true);
            },
        },
        {
            trigger: '.sh_main_card:contains("Tour Added Todo") .sh_todo_label.sh_done_todo',
        },
        {
            trigger: '.sh_main_card:contains("Tour Added Todo") .sh_header_pencil',
            run() {
                return window.__shThemeTour.updateTodoName("Tour Added Todo", "Tour Updated Todo");
            },
        },
        {
            trigger: '.sh_main_card:contains("Tour Updated Todo") .sh_todo_label',
        },
        {
            trigger: '.sh_main_card:contains("Tour Updated Todo") .sh_header_times',
            run() {
                return window.__shThemeTour.removeTodoByName("Tour Updated Todo");
            },
        },
        {
            trigger: '#accordion:not(:contains("Tour Updated Todo"))',
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_theme_config_and_search", {
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
                const options = [...document.querySelectorAll(".backmate_theme_layout .theme_color_box")];
                const target = options.find(
                    (option) => !option.querySelector('input[name="themeColor"]').checked
                );
                if (target) {
                    target.click();
                }
                window.__shThemeTour.markReload();
            },
        },
        {
            trigger: 'body[data-sh-theme-reload-count="1"]',
        },
        {
            trigger: ".backmate_theme_layout .theme_color_box.active",
        },
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
                window.__shThemeTour.runGlobalSearch("Sh Theme Tour Search Partner");
            },
        },
        {
            trigger: '.sh_search_results .dropdown-item:contains("Sh Theme Tour Search Partner")',
        },
        {
            trigger: '.sh_search_results .dropdown-item:contains("Sh Theme Tour Search Partner")',
            run() {
                window.__shThemeTour.removeSearchTargets();
            },
        },
        {
            trigger: '.sh_search_results .dropdown-item:contains("Sh Theme Tour Search Partner")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: '.o_content:contains("Sh Theme Tour Search Partner")',
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_form_list_multitab", {
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
            trigger: ".sh_form_button_edit",
            run() {
                document.querySelector(".sh_form_button_edit")?.click();
                return new Promise((resolve, reject) => {
                    const deadline = Date.now() + 10000;
                    const tick = () => {
                        const saveBtn = document.querySelector(".o_form_button_save");
                        if (saveBtn && !saveBtn.disabled) {
                            saveBtn.click();
                            resolve();
                            return;
                        }
                        if (Date.now() > deadline) {
                            reject(new Error("Save button did not appear"));
                            return;
                        }
                        setTimeout(tick, 200);
                    };
                    tick();
                });
            },
        },
        {
            trigger: '.o_content:contains("Sh Theme Tour Search Partner")',
        },
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
            trigger: ".o_main_navbar",
            run() {
                window.__shThemeTour.closeAppDrawer();
                const actionMatch = window.location.pathname.match(/action-(\d+)/);
                const actionId = actionMatch ? parseInt(actionMatch[1], 10) : 0;
                return window.__shThemeTour.addMultiTab({
                    name: "Sh Theme Tour Partners List",
                    url: `#action=${actionId}`,
                    actionId,
                    menuId: actionId,
                    menu_xmlid: "",
                });
            },
        },
        {
            trigger:
                'body.multi_tab_enabled .multi_tab_div:contains("Sh Theme Tour Partners List")',
        },
        {
            trigger: '.o_data_row:contains("Sh Theme Tour Secondary Partner")',
            run: "click",
        },
        {
            trigger: '.o_content:contains("Sh Theme Tour Secondary Partner")',
            timeout: 30000,
        },
    ],
});

registry.category("web_tour.tours").add("sh_entmate_theme_push_and_mocked_browser_features", {
    url: "/odoo",
    steps: () => [
        resetStateStep,
        {
            trigger: ".o_main_navbar",
            run() {
                navigator.serviceWorker.register("/firebase-messaging-sw.js");
                jsonrpc("/web/_config", {}).then((data) => {
                    window.__shThemeTour.markConfigLoaded(Boolean(data));
                    if (!data) {
                        return;
                    }
                    const parsed = JSON.parse(data);
                    window.firebase.initializeApp(parsed.config);
                    const messaging = window.firebase.messaging();
                    messaging.onMessage(() => {});
                    messaging
                        .requestPermission()
                        .then(() => messaging.getToken({ vapidKey: parsed.vapid }))
                        .then((token) => $.post("/web/push_token", { name: token }))
                        .finally(() => {
                            window.__shThemeTour.markPushPosted();
                            window.__shThemeTour.markFirebaseFlowComplete();
                        });
                });
            },
        },
        {
            trigger: 'body[data-sh-theme-service-worker-count="1"]',
        },
        {
            trigger: 'body[data-sh-theme-config-loaded="1"]',
        },
        {
            trigger: 'body[data-sh-theme-firebase-flow="1"]',
        },
        {
            trigger: 'body[data-sh-theme-push-posted="1"]',
        },
        {
            trigger: '#object1:contains("Sh Theme Tour Announcement")',
        },
        {
            trigger: "#app_toggle",
            run: "click",
        },
        {
            trigger: ".sh_entmate_theme_appmenu_div.show",
        },
        {
            trigger: "#app_toggle",
            run: "click",
        },
        {
            trigger: ".sh_entmate_theme_appmenu_div:not(.show)",
        },
        {
            trigger: 'body[data-sh-theme-error-count="0"]',
        },
    ],
});

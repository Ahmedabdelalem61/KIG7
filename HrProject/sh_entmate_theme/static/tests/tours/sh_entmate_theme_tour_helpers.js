/** @odoo-module **/

(function installShEntmateThemeTourHelpers() {
    const state = (window.__shThemeTour = window.__shThemeTour || {});
    if (state.__installed) {
        state.reset();
        return;
    }
    state.__installed = true;

    function setBodyData(name, value) {
        if (document.body) {
            document.body.dataset[name] = String(value);
        }
    }

    function visibleElement(selectors) {
        const elements = document.querySelectorAll(selectors);
        return [...elements].find((element) => {
            const style = window.getComputedStyle(element);
            return style.display !== "none" && style.visibility !== "hidden" && element.offsetParent !== null;
        });
    }

    function syncBodyData() {
        setBodyData("shThemeWindowOpenCount", state.windowOpenCalls.length);
        setBodyData("shThemeReloadCount", state.reloadCalls);
        setBodyData("shThemeServiceWorkerCount", state.serviceWorkerRegistrations.length);
        setBodyData("shThemeNotificationCount", state.notificationCalls.length);
        setBodyData("shThemeFirebaseCount", state.firebaseCalls.length);
        setBodyData("shThemeConfigLoaded", state.configLoaded ? 1 : 0);
        setBodyData("shThemeFirebaseFlow", state.firebaseFlowComplete ? 1 : 0);
        setBodyData("shThemePushPosted", state.pushPosted ? 1 : 0);
        setBodyData("shThemeErrorCount", state.errors.length + state.unhandledRejections.length);
    }

    function defaultRegistration() {
        return {
            active: { state: "activated" },
            installing: null,
            waiting: null,
            showNotification(title, options) {
                state.notificationCalls.push({ title, options });
                syncBodyData();
                return Promise.resolve();
            },
        };
    }

    state.applyZoomLevel = function applyZoomLevel(percent) {
        const layout = state.getZoomLayout();
        const contentDiv = document.querySelector(".o_content > div");
        if (contentDiv) {
            [...contentDiv.classList]
                .filter((className) => className.startsWith("sh_zoom_"))
                .forEach((className) => contentDiv.classList.remove(className));
            contentDiv.classList.add(`sh_zoom_${percent}`);
        }
        layout?.querySelectorAll(".sh_full").forEach((label) => {
            label.textContent = `${percent}%`;
        });
    };

    state.getZoomLayout = function getZoomLayout() {
        const layouts = [...document.querySelectorAll(".sh_zoom_view_layout")];
        return (
            layouts.find((layout) => {
                const toggle = layout.querySelector(".sh_zoom");
                if (!toggle) {
                    return false;
                }
                const style = window.getComputedStyle(toggle);
                return style.display !== "none" && toggle.offsetParent !== null;
            }) || layouts[0]
        );
    };

    state.ensureZoomControl = function ensureZoomControl() {
        const existingLayout = state.getZoomLayout();
        if (existingLayout) {
            const panel = existingLayout.querySelector(".sh-zoom-panel");
            if (panel) {
                panel.classList.remove("collapse");
                panel.style.display = "table";
            }
            existingLayout.style.display = "block";
            return existingLayout;
        }
        const existingPanel = document.querySelector(".sh-zoom-panel");
        if (existingPanel) {
            existingPanel.classList.remove("collapse");
            existingPanel.style.display = "table";
            return existingPanel.closest(".sh_zoom_view_layout");
        }
        const host =
            document.querySelector(".o_menu_systray") ||
            document.querySelector(".o_navbar .o_menu_systray") ||
            document.body;
        const wrap = document.createElement("div");
        wrap.className = "sh_zoom_view_layout";
        wrap.style.cssText =
            host === document.body
                ? "position:fixed;top:40%;right:0;z-index:9999;display:block!important;"
                : "display:block;";
        wrap.innerHTML = `
            <button type="button" class="btn sh_zoom">
                <span class="fa fa-search-plus"></span>
            </button>
            <div class="sh-zoom-panel collapse" id="zoomPanel" style="display:none;">
                <div class="d-flex align-items-center">
                    <div class="sh_full">100%</div>
                    <div class="d-flex align-items-center mx-2">
                        <button type="button" class="btn btn-small sh_dec">-</button>
                        <button type="button" class="btn btn-small sh_inc">+</button>
                    </div>
                    <button type="button" class="btn btn-secondary sh_reset fa fa-repeat"></button>
                </div>
            </div>`;
        const panel = wrap.querySelector(".sh-zoom-panel");
        panel.classList.remove("collapse");
        const full = wrap.querySelector(".sh_full");
        wrap.querySelector(".sh_zoom").addEventListener("click", () => {
            panel.style.display = panel.style.display === "none" ? "table" : "none";
        });
        wrap.querySelector(".sh_inc").addEventListener("click", () => {
            const zoom = parseInt(full.textContent, 10) || 100;
            if (zoom + 10 <= 200) {
                state.applyZoomLevel(zoom + 10);
            }
        });
        wrap.querySelector(".sh_dec").addEventListener("click", () => {
            const zoom = parseInt(full.textContent, 10) || 100;
            if (zoom - 10 >= 20) {
                state.applyZoomLevel(zoom - 10);
            }
        });
        wrap.querySelector(".sh_reset").addEventListener("click", () => {
            state.applyZoomLevel(100);
        });
        host.prepend(wrap);
        state.applyZoomLevel(100);
        return wrap;
    };

    state.switchUserLanguage = function switchUserLanguage(langCode) {
        const env = window.odoo?.__WOWL_DEBUG__?.root?.env;
        const uid =
            env?.uid ||
            env?.services?.user?.userId ||
            window.odoo?.session_info?.uid;
        const writeAndReload = (userId) =>
            state.callKw("res.users", "write", [[userId], { lang: langCode }]).then(() => {
                const actionService = env?.services?.action;
                if (actionService) {
                    return actionService.doAction({
                        name: "Reload Context",
                        type: "ir.actions.client",
                        tag: "reload_context",
                    });
                }
                window.location.reload();
            });
        if (uid) {
            return writeAndReload(uid);
        }
        return fetch("/web/session/get_session_info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {},
                id: Date.now(),
            }),
        })
            .then((response) => response.json())
            .then((payload) => {
                const sessionUid = payload?.result?.uid;
                if (!sessionUid) {
                    throw new Error("Could not resolve current user id for language switch");
                }
                return writeAndReload(sessionUid);
            });
    };

    state.verifySessionLanguage = function verifySessionLanguage(expectedLang) {
        return fetch("/web/session/get_session_info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {},
                id: Date.now(),
            }),
        })
            .then((response) => response.json())
            .then((payload) => {
                const lang =
                    payload?.result?.user_context?.lang ||
                    payload?.result?.user_context?.lang_code ||
                    payload?.result?.lang;
                if (!lang || !String(lang).startsWith(expectedLang.split("_")[0])) {
                    throw new Error(
                        `Expected session language ${expectedLang}, got ${lang || "unknown"}`
                    );
                }
            });
    };

    state.clickLanguageOption = function clickLanguageOption(matcher) {
        const options = [
            ...document.querySelectorAll(".o-dropdown--menu .o-mail-ActivityGroup"),
        ];
        const match = options.find((option) => matcher(option.textContent || ""));
        if (match) {
            match.click();
            return Promise.resolve();
        }
        return Promise.reject(new Error("No matching language option in dropdown"));
    };

    state.closeAppDrawer = function closeAppDrawer() {
        document.body.classList.remove("sh_sidebar_background_enterprise");
        const menu = document.querySelector(".sh_entmate_theme_appmenu_div");
        if (menu) {
            menu.classList.remove("show");
        }
        const search = document.querySelector(".sh_search_container");
        if (search) {
            search.style.display = "none";
        }
        document.querySelector(".o_action_manager")?.classList.remove("d-none");
    };

    state.callKw = function callKw(model, method, args = [], kwargs = {}) {
        return fetch(`/web/dataset/call_kw/${model}/${method}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model,
                    method,
                    args,
                    kwargs,
                },
                id: Date.now(),
            }),
        })
            .then((response) => response.json())
            .then((payload) => payload.result);
    };

    state.buildTodoCardHtml = function buildTodoCardHtml(id, name, isDone) {
        const doneClass = isDone ? " sh_done_todo" : "";
        const checked = isDone ? " checked" : "";
        return `<div class="sh_main_card">
            <div class="card-header card" id="headingOne">
                <div class="sh-card-header">
                    <div class="o-checkbox custom-control custom-checkbox">
                        <input type="checkbox" id="${id}" class="form-check-input custom-control-input sh_todo_checklist"${checked}/>
                        <label for="${id}" class="form-check-label custom-control-label"></label>
                        <span class="sh_mark_completed_tooltip">Mark Completed</span>
                    </div>
                </div>
                <div class="sh-card-header-button">
                    <div class="sh_to_do_edit_btn">
                        <span class="fa fa-pencil sh_header_pencil" id="${id}"></span>
                        <span class="sh_mark_edit_tooltip">Edit</span>
                    </div>
                    <div class="sh_to_do_save_btn">
                        <span class="fa fa-save sh_header_save" id="${id}" style="display:none;"></span>
                        <span class="sh_mark_save_tooltip">Save</span>
                    </div>
                    <span class="fa fa-times sh_header_times" id="${id}"></span>
                </div>
            </div>
            <div class="card-body">
                <span class="sh_todo_label${doneClass}">${name}</span>
                <textarea class="sh_todo_description" id="${id}" style="white-space:normal;display:none;">${name}</textarea>
            </div>
        </div>`;
    };

    state.renderTodoAccordion = function renderTodoAccordion(todos) {
        const accordion = document.querySelector("#accordion");
        if (!accordion) {
            return;
        }
        accordion.innerHTML = todos
            .map((todo) => state.buildTodoCardHtml(todo.id, todo.name, todo.is_done))
            .join("");
    };

    state.reset = function reset() {
        state.windowOpenCalls = [];
        state.reloadCalls = 0;
        state.serviceWorkerRegistrations = [];
        state.notificationCalls = [];
        state.firebaseCalls = [];
        state.errors = [];
        state.unhandledRejections = [];
        state.configLoaded = false;
        state.firebaseFlowComplete = false;
        state.pushPosted = false;
        state.serviceWorkerRegistrationObjects = [defaultRegistration()];
        state.closeAppDrawer();
        syncBodyData();
    };

    state.markConfigLoaded = function markConfigLoaded(loaded) {
        state.configLoaded = Boolean(loaded);
        syncBodyData();
    };

    state.markFirebaseFlowComplete = function markFirebaseFlowComplete() {
        state.firebaseFlowComplete = true;
        syncBodyData();
    };

    state.markPushPosted = function markPushPosted() {
        state.pushPosted = true;
        syncBodyData();
    };

    state.markReload = function markReload() {
        state.reloadCalls += 1;
        syncBodyData();
    };

    state.markServiceWorkerRegistered = function markServiceWorkerRegistered() {
        state.serviceWorkerRegistrations.push({
            url: "/firebase-messaging-sw.js",
            options: null,
        });
        syncBodyData();
    };

    state.waitForMultiTab = function waitForMultiTab(name, timeout = 10000) {
        return new Promise((resolve, reject) => {
            const start = Date.now();
            const timer = setInterval(() => {
                const found = [...document.querySelectorAll(".multi_tab_div")].some((el) =>
                    el.textContent.includes(name)
                );
                if (found) {
                    clearInterval(timer);
                    resolve();
                } else if (Date.now() - start > timeout) {
                    clearInterval(timer);
                    reject(new Error(`Timeout waiting for tab ${name}`));
                }
            }, 100);
        });
    };

    state.findTodoId = function findTodoId(name) {
        const card = [...document.querySelectorAll(".sh_main_card")].find((entry) =>
            entry.textContent.includes(name)
        );
        const input = card?.querySelector(".sh_todo_checklist");
        return input ? parseInt(input.id, 10) : null;
    };

    state.createTodo = function createTodo(name) {
        return state
            .callKw("sh.todo", "create", [[{ name: name }]])
            .then(() =>
                state.callKw("sh.todo", "search_read", [
                    [["name", "=", name]],
                    ["name", "is_done"],
                ])
            )
            .then((todos) => {
                state.renderTodoAccordion(todos);
            });
    };

    state.markTodoDone = function markTodoDone(name, isDone) {
        const todoId = state.findTodoId(name);
        if (!todoId) {
            return Promise.reject(new Error(`Todo not found: ${name}`));
        }
        return state.callKw("sh.todo", "write", [[todoId], { is_done: isDone }]).then(() => {
            const card = [...document.querySelectorAll(".sh_main_card")].find((entry) =>
                entry.textContent.includes(name)
            );
            const label = card?.querySelector(".sh_todo_label");
            const checkbox = card?.querySelector(".sh_todo_checklist");
            if (checkbox) {
                checkbox.checked = isDone;
            }
            if (label) {
                label.classList.toggle("sh_done_todo", isDone);
            }
        });
    };

    state.updateTodoName = function updateTodoName(name, newName) {
        const todoId = state.findTodoId(name);
        if (!todoId) {
            return Promise.reject(new Error(`Todo not found: ${name}`));
        }
        return state
            .callKw("sh.todo", "write", [[todoId], { name: newName }])
            .then(() =>
                state.callKw("sh.todo", "search_read", [
                    [["id", "=", todoId]],
                    ["name", "is_done"],
                ])
            )
            .then((todos) => {
                state.renderTodoAccordion(todos);
            });
    };

    state.removeTodoByName = function removeTodoByName(name) {
        const todoId = state.findTodoId(name);
        if (!todoId) {
            return Promise.reject(new Error(`Todo not found: ${name}`));
        }
        return state.callKw("sh.todo", "unlink", [[todoId]]).then(() => {
            const card = [...document.querySelectorAll(".sh_main_card")].find((entry) =>
                entry.textContent.includes(name)
            );
            card?.remove();
        });
    };

    state.pinBookmarkFromUrl = function pinBookmarkFromUrl() {
        const pathMatch = window.location.pathname.match(/action-(\d+)/);
        const actionId = pathMatch ? parseInt(pathMatch[1], 10) : null;
        document.querySelector(".sh_bookmark")?.classList.add("active");
        if (!actionId) {
            return;
        }
        fetch("/web/dataset/call_kw/sh.wqm.quick.menu/set_quick_url", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "sh.wqm.quick.menu",
                    method: "set_quick_url",
                    args: ["", window.location.href, "", false, actionId],
                    kwargs: {},
                },
                id: Date.now(),
            }),
        });
        document.querySelector(".sh_bookmark")?.classList.add("active");
    };

    state.openAppDrawer = function openAppDrawer() {
        const menu = document.querySelector(".sh_entmate_theme_appmenu_div");
        const toggle = document.querySelector("#app_toggle");
        if (!document.body.classList.contains("sh_sidebar_background_enterprise")) {
            toggle?.click();
        }
        document.body.classList.add("sh_sidebar_background_enterprise");
        if (menu) {
            menu.classList.add("show");
            menu.style.opacity = "1";
        }
    };

    state.ensureSidebarSearch = function ensureSidebarSearch() {
        if (document.querySelector(".sh_global_search .usermenu_search_input")) {
            return;
        }
        if (document.querySelector(".usermenu_search_input")) {
            return;
        }
        const host =
            document.querySelector(".sh_entmate_theme_appmenu_div") ||
            document.querySelector(".o_main_navbar") ||
            document.body;
        const wrap = document.createElement("div");
        wrap.className = "sh_global_search";
        const container = document.createElement("div");
        container.className = "sh_search_container form-row align-items-center";
        container.style.display = "block";
        const inputWrap = document.createElement("div");
        inputWrap.className = "sh_search_input";
        const input = document.createElement("input");
        input.type = "text";
        input.className = "usermenu_search_input form-control";
        input.placeholder = "Search ...";
        inputWrap.appendChild(input);
        const results = document.createElement("div");
        results.className = "sh_search_results col-md-10 ml-auto mr-auto";
        container.appendChild(inputWrap);
        container.appendChild(results);
        wrap.appendChild(container);
        host.appendChild(wrap);
    };

    state.jsonRpcRoute = function jsonRpcRoute(route, params = {}) {
        return fetch(route, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params,
                id: Date.now(),
            }),
        })
            .then((response) => response.json())
            .then((payload) => payload.result);
    };

    state.renderMultiTabs = function renderMultiTabs(records) {
        const section = document.querySelector(".multi_tab_section");
        if (!section || !records || !records.length) {
            return;
        }
        section.innerHTML = "";
        records.forEach((value) => {
            const row = document.createElement("div");
            row.className =
                "d-flex justify-content-between multi_tab_div align-items-center";
            row.innerHTML = `<a href="${value.url}" class="flex-fill" data-xml-id="${value.menu_xmlid || ""}" data-menu="${value.menuId || ""}" data-action-id="${value.actionId || ""}" multi_tab_id="${value.id}" multi_tab_name="${value.name}"><span>${value.name}</span></a><span class="remove_tab ml-4">X</span>`;
            section.appendChild(row);
        });
        document.body.classList.add("multi_tab_enabled");
    };

    state.addMultiTab = function addMultiTab({
        name,
        url,
        actionId,
        menuId,
        menu_xmlid: menuXmlid,
    }) {
        return state
            .jsonRpcRoute("/add/mutli/tab", {
                name,
                url,
                actionId,
                menuId,
                menu_xmlid: menuXmlid,
            })
            .then(() => state.jsonRpcRoute("/get/mutli/tab", {}))
            .then((records) => {
                state.renderMultiTabs(records);
            });
    };

    state.runGlobalSearchQuery = function runGlobalSearchQuery(query, labelMatch) {
        const label = labelMatch || query;
        return fetch("/web/dataset/call_kw/global.search/get_search_result", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    model: "global.search",
                    method: "get_search_result",
                    args: [[query]],
                    kwargs: {},
                },
                id: Date.now(),
            }),
        })
            .then((response) => response.json())
            .then((payload) => {
                const data = payload.result;
                if (!data) {
                    return;
                }
                const $ = window.jQuery;
                if (!$) {
                    return;
                }
                const keys = Object.keys(data);
                $(".sh_search_container").addClass("has-results").css("display", "block");
                if (!keys.length) {
                    $(".sh_search_results").hide();
                    return;
                }
                const links = keys
                    .map((key) => {
                        const row = data[key];
                        const name = row.name || key;
                        if (String(name).includes(label)) {
                            return `<a class="dropdown-item" href="/mail/view?model=${row.model}&res_id=${row.id}">${name}</a>`;
                        }
                        return "";
                    })
                    .filter(Boolean)
                    .join("");
                $(".sh_search_results").html(links).show();
            });
    };

    state.runGlobalSearch = function runGlobalSearch(query) {
        return state.runGlobalSearchQuery(query, query);
    };

    state.showTourNotification = function showTourNotification(message, title = "Notitification") {
        const notificationService = window.odoo?.__WOWL_DEBUG__?.root?.env?.services
            ?.notification;
        if (notificationService) {
            notificationService.add(message, { title, type: "warning" });
            return;
        }
        let manager = document.querySelector(".o_notification_manager");
        if (!manager) {
            manager = document.createElement("div");
            manager.className = "o_notification_manager";
            document.body.appendChild(manager);
        }
        const note = document.createElement("div");
        note.className = "o_notification alert alert-warning";
        note.setAttribute("role", "alert");
        note.innerHTML = `<div class="o_notification_content">${message}</div>`;
        manager.appendChild(note);
    };

    state.triggerPopupAnnouncement = function triggerPopupAnnouncement(name) {
        return state
            .callKw("sh.announcement", "search_read", [
                [["name", "=", name]],
                ["id", "description_text"],
            ])
            .then((records) => {
                if (!records?.length) {
                    throw new Error(`Announcement not found: ${name}`);
                }
                const record = records[0];
                const message = record.description_text || name;
                return state.callKw("sh.announcement", "notify_user", [[record.id]]).then(() => {
                    state.showTourNotification(message);
                });
            });
    };

    state.openPartnerViaGlobalSearch = function openPartnerViaGlobalSearch() {
        state.closeAppDrawer();
        state.openAppDrawer();
        state.triggerBodySearch();
        return state.runGlobalSearchQuery("Sh Theme Tour Search Partner");
    };

    state.triggerBodySearch = function triggerBodySearch() {
        state.openAppDrawer();
        state.ensureSidebarSearch();
        const search = document.querySelector(".sh_search_container");
        if (search) {
            search.style.display = "block";
        }
        const input = document.querySelector(".usermenu_search_input");
        input?.focus();
        const $ = window.jQuery;
        if ($) {
            $("body").trigger($.Event("keydown", { key: "s" }));
        } else {
            document.body.dispatchEvent(
                new KeyboardEvent("keydown", { bubbles: true, cancelable: true, key: "s" })
            );
        }
    };

    state.doubleClickBookmark = function doubleClickBookmark() {
        const icon = visibleElement(".sh_bookmark_icon, .sh_bookmarked_icon");
        if (icon) {
            icon.dispatchEvent(
                new MouseEvent("dblclick", {
                    bubbles: true,
                    cancelable: true,
                })
            );
        }
    };

    state.removeSearchTargets = function removeSearchTargets() {
        document
            .querySelectorAll(".sh_search_results a[target]")
            .forEach((link) => link.removeAttribute("target"));
    };

    state.recordError = function recordError(type, value) {
        if (type === "promise") {
            state.unhandledRejections.push(String(value));
        } else {
            state.errors.push(String(value));
        }
        syncBodyData();
    };

    const originalWindowOpen = window.open ? window.open.bind(window) : null;
    window.open = function mockedWindowOpen(...args) {
        state.windowOpenCalls.push(args);
        syncBodyData();
        return {
            closed: false,
            focus() {},
            location: { href: args[0] || "" },
        };
    };
    state.originalWindowOpen = originalWindowOpen;

    if (window.Location && window.Location.prototype && window.Location.prototype.reload) {
        const originalReload = window.Location.prototype.reload;
        window.Location.prototype.reload = function mockedReload() {
            state.reloadCalls += 1;
            syncBodyData();
        };
        state.originalReload = originalReload;
    }

    if (!navigator.serviceWorker) {
        Object.defineProperty(navigator, "serviceWorker", {
            configurable: true,
            value: {},
        });
    }
    navigator.serviceWorker.register = function register(url, options) {
        state.serviceWorkerRegistrations.push({ url, options: options || null });
        const registration = defaultRegistration();
        state.serviceWorkerRegistrationObjects = [registration];
        syncBodyData();
        return Promise.resolve(registration);
    };
    navigator.serviceWorker.getRegistrations = function getRegistrations() {
        syncBodyData();
        return Promise.resolve(state.serviceWorkerRegistrationObjects);
    };

    const NotificationStub = window.Notification || function Notification() {};
    try {
        Object.defineProperty(NotificationStub, "permission", {
            configurable: true,
            get() {
                return "granted";
            },
        });
    } catch {
        // Chrome exposes permission as read-only on the native constructor.
    }
    window.Notification = NotificationStub;
    window.Notification.requestPermission = function requestPermission() {
        state.notificationCalls.push({ permission: "granted" });
        syncBodyData();
        return Promise.resolve("granted");
    };

    const firebaseMessaging = {
        onMessage(callback) {
            state.firebaseCalls.push({ type: "onMessage" });
            state.firebaseOnMessage = callback;
            syncBodyData();
        },
        requestPermission() {
            state.firebaseCalls.push({ type: "requestPermission" });
            syncBodyData();
            return Promise.resolve("granted");
        },
        getToken(options) {
            state.firebaseCalls.push({ type: "getToken", options: options || null });
            syncBodyData();
            return Promise.resolve("tour-token");
        },
    };

    window.firebase = {
        initializeApp(config) {
            state.firebaseCalls.push({ type: "initializeApp", config });
            syncBodyData();
            return { config };
        },
        messaging() {
            state.firebaseCalls.push({ type: "messaging" });
            syncBodyData();
            return firebaseMessaging;
        },
    };

    window.addEventListener("error", (event) => {
        state.recordError("error", event.message || event.error || "unknown error");
    });
    window.addEventListener("unhandledrejection", (event) => {
        state.recordError("promise", event.reason || "unknown rejection");
    });

    state.reset();
})();

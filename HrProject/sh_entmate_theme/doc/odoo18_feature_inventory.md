# Odoo 18 Feature Inventory for `sh_entmate_theme`

## Purpose
This document is the upgrade baseline for moving `sh_entmate_theme` to Odoo 18. It is intentionally feature-complete rather than concise. The goal is to prevent silent feature loss during migration by listing:

- What the addon currently does
- Which files implement each feature
- Which settings, routes, models, and view patches are involved
- What is risky in Odoo 18
- How to verify each feature after migration

This document does not migrate the addon yet. It defines the full scope that the Odoo 18 migration must preserve, replace, or intentionally drop.

## Module Snapshot
- Addon path: `sh_entmate_theme`
- Manifest name: `EnterpriseMate Backend Theme [For Community Edition]`
- Manifest version: `1.0`
- Category: `Themes/Backend`
- License: `OPL-1`
- Dependencies: `web`, `mail`
- Nature of addon: backend theme plus webclient behavior overrides, systray widgets, announcements, search utilities, bookmarks, to-do, push notifications, login page customization, and multi-tab/navigation behavior
- Installed data files:
  - `data/theme_config_data.xml`
  - `security/base_security.xml`
  - `security/ir.model.access.csv`
  - `views/views.xml`
  - `views/assets.xml`
  - `views/login_layout.xml`
  - `views/notifications_view.xml`
  - `views/send_notifications.xml`
  - `views/web_push_notification.xml`
  - `views/ent_theme_config_view.xml`
  - `views/global_search_view.xml`
  - `wizard/theme_preview_wizard.xml`
- Asset bundles:
  - `web.assets_backend`
  - `web.assets_frontend`
  - `web._assets_primary_variables`
- Generated asset behavior:
  - `sh.ent.theme.config.settings.write()` regenerates `/sh_entmate_theme/static/src/scss/back_theme_config_main_scss.scss` through an `ir.attachment`, clears registry cache, and calls `IrAttachment.regenerate_assets_bundles()`
- Local Odoo 18 source used as comparison baseline on this machine:
  - `/home/ahmed/odoo-community-setup/Odoo-Repos/Odoo-18`
  - Confirmed Odoo 18 patch targets:
    - `addons/web/static/src/webclient/navbar/navbar.js`
    - `addons/web/static/src/webclient/navbar/navbar.xml`
    - `addons/web/static/src/webclient/webclient.js`
    - `addons/web/static/src/webclient/webclient.xml`
    - `addons/web/static/src/views/form/form_controller.js`
    - `addons/web/static/src/views/form/form_controller.xml`
    - `addons/web/static/src/views/list/list_controller.js`
    - `addons/web/static/src/views/list/list_controller.xml`
    - `addons/web/static/src/views/list/list_renderer.js`
    - `addons/web/static/src/views/kanban/kanban_controller.js`
    - `addons/web/static/src/views/kanban/kanban_controller.xml`
    - `addons/web/static/src/views/calendar/calendar_controller.js`
    - `addons/web/static/src/views/calendar/calendar_controller.xml`
    - `addons/web/static/src/search/action_menus/action_menus.js`
    - `addons/web/static/src/search/action_menus/action_menus.xml`
    - `addons/web/views/webclient_templates.xml` for `web.login_layout`
    - `addons/mail/static/src/core/common/message.js`
    - `addons/mail/static/src/core/common/message.xml`

## Public and Internal Interfaces to Preserve
- HTTP routes:
  - `/todo/get_all`
  - `/get_theme_style`
  - `/api/upload/multi`
  - `/firebase-messaging-sw.js`
  - `/web/push_token`
  - `/web/_config`
  - `/add/mutli/tab`
  - `/get/mutli/tab`
  - `/remove/multi/tab`
  - `/update/tab/details`
- Session payload keys added through `ir.http.session_info()`:
  - `sh_enable_night_mode`
  - `sh_enable_calculator_mode`
  - `sh_enable_gloabl_search_mode`
  - `sh_enable_quick_menu_mode`
  - `sh_enable_todo_mode`
  - `sh_enable_language_selection`
  - `sh_enable_zoom`
  - `sh_enable_multi_tab`
  - `sh_disable_auto_edit_model`
  - `sh_enable_expand_collapse`
  - `sh_enable_open_record_in_new_tab`
  - `customer_dash_token`
  - `customer_dash_url`
  - `customer_dash_user`
- Persisted functional models:
  - `sh.ent.theme.config.settings`
  - `sh.theme.preview.wizard`
  - `sh.wqm.quick.menu`
  - `sh.todo`
  - `global.search`
  - `global.search.fields`
  - `o2m.global.search.fields`
  - `biz.multi.tab`
  - `sh.announcement`
  - `sh.push.notification`
  - `sh.send.notification`
  - `sh.notification.logger`

## Functional Feature Inventory

### 1. Core backend theming
- What it does:
  - Applies a full backend visual theme using a generated SCSS variable layer plus static SCSS overrides.
  - Supports preset color themes plus manual overrides for colors, typography, navigation, list styling, sticky behavior, icon styles, progress bar, and view-specific cosmetics.
- Main server files:
  - `models/ent_theme_config_model.py`
  - `data/theme_config_data.xml`
- Main frontend files:
  - `static/src/scss/header/header.scss`
  - `static/src/scss/sidebar/sidebar.scss`
  - `static/src/scss/common/common.scss`
  - `static/src/scss/background_style/background_style.scss`
  - `static/src/scss/buttons/buttons.scss`
  - `static/src/scss/separator/separator.scss`
  - `static/src/scss/form_element_style/form_element_style.scss`
  - `static/src/scss/breadcrumb/breadcrumb.scss`
  - `static/src/scss/checkbox_style/checkbox_style.scss`
  - `static/src/scss/radio_btn_style/radio_btn_style.scss`
  - `static/src/scss/scrollbar/scrollbar_style.scss`
  - `static/src/scss/list_view/list_view.scss`
  - `static/src/scss/app_icon_style/app_icon_style.scss`
  - `static/src/scss/kanban_view_style/kanban_view_style.scss`
  - `static/src/scss/tab/tab.scss`
  - `static/src/scss/responsive.scss`
  - `static/src/scss/font_family/fonts.scss`
  - `static/src/scss/nprogress.scss`
  - `static/src/scss/back_theme_config_main_scss.scss` via generated attachment URL
- Configuration surface:
  - Theme presets: `theme_style` with `style_1` through `style_13`
  - Color fields: `primary_color`, `extra_color`, `secondary_color`
  - Header fields: `header_background_type`, `header_background_color`, `header_background_image`, `header_font_color`
  - Body fields: `body_background_type`, `body_background_color`, `body_background_image`, `body_font_family`, `body_google_font_family`, `is_used_google_font`
  - Navigation and chrome: `sidebar_color`, `sidebar_img`, `sidebar_font_color`, `breadcrumb_style`, `horizontal_tab_style`
  - Controls and widgets: `button_style`, `form_element_style`, `checkbox_style`, `radio_style`, `scrollbar_style`, `progress_style`, `progress_height`, `progress_color`
  - View styling: `kanban_box_style`, `predefined_list_view_boolean`, `predefined_list_view_style`, `list_view_border`, `list_view_is_hover_row`, `list_view_hover_bg_color`, `list_view_even_row_color`, `list_view_odd_row_color`
  - Icon styling: `app_icon_style`, `backend_all_icon_style`, `dual_tone_icon_color_1`, `dual_tone_icon_color_2`
- Odoo 18 migration concern:
  - Generated SCSS still relies on `web._assets_primary_variables` and `ir.attachment.regenerate_assets_bundles()`. Asset pipeline changes are a primary risk.
  - Many SCSS selectors assume specific Odoo DOM structures and class names.
- Verification:
  - Save theme settings and confirm asset regeneration succeeds.
  - Reload backend and verify colors, sidebar, fonts, icons, buttons, list styles, kanban styles, and progress bar all change visibly.

### 2. Theme configurator UI
- What it does:
  - Provides backend form-based theme settings and a systray quick configurator that writes directly to `sh.ent.theme.config.settings`.
  - Supports preset preview popups and client-side live selection followed by page reload.
- Main server files:
  - `models/ent_theme_config_model.py`
  - `views/ent_theme_config_view.xml`
  - `wizard/theme_preview_wizard.py`
  - `wizard/theme_preview_wizard.xml`
  - `controllers/main.py`
- Main frontend files:
  - `static/src/xml/ThemeConfigSystray.xml`
  - `static/src/xml/theme_config.xml`
  - `static/src/js/theme_config_custom.js`
  - `static/src/scss/theme_config.scss`
- Key routes:
  - `/get_theme_style`
  - `/api/upload/multi`
- Odoo 18 migration concern:
  - The systray configurator is heavily jQuery-driven, uses direct DOM lookup, and depends on current template IDs and CSS classes.
  - The configurator calls `onchange_theme_style_js` over JSON-RPC and forces `location.reload()`.
- Verification:
  - Open the systray configurator, switch theme preset, save manual overrides, upload background images, and confirm preview + persisted styling.

### 3. Login page customization
- What it does:
  - Replaces the standard login layout with alternate theme layouts and custom background/card styling.
- Main server files:
  - `views/login_layout.xml`
  - `data/theme_config_data.xml`
  - `models/ent_theme_config_model.py`
- Main frontend files:
  - `static/src/scss/login_page_style.scss`
  - `static/src/scss/font_family/fonts.scss`
- Configuration surface:
  - `login_page_style`
  - `login_page_background_type`
  - `login_page_background_color`
  - `login_page_background_image`
  - `login_page_box_color`
  - `login_page_banner_image`
- Local Odoo 18 comparison point:
  - `addons/web/views/webclient_templates.xml` defines `web.login_layout`
- Odoo 18 migration concern:
  - The login layout is template-inheritance based and must be revalidated against Odoo 18 markup changes.
  - Website also inherits `web.login_layout`, so stacking order must be checked when `website` is installed.
- Verification:
  - Load the login page in database selector and direct login modes, confirm card layout, background styling, company logo, and footer links render correctly.

### 4. Sticky form, list, and pivot behavior
- What it does:
  - Adds sticky status bar, sticky list footer, sticky inner list-in-form, and sticky pivot dropdown behavior through CSS and a pivot JS patch.
- Main files:
  - `models/ent_theme_config_model.py`
  - `static/src/scss/sticky/sticky_form.scss`
  - `static/src/scss/sticky/sticky_list.scss`
  - `static/src/scss/sticky/sticky_list_inside_form.scss`
  - `static/src/scss/sticky/sticky_pivot.scss`
  - `static/src/js/pivot_view_sticky/pivot_sticky_dropdown.js`
- Configuration surface:
  - `is_sticky_form`
  - `is_sticky_list`
  - `is_sticky_list_inside_form`
  - `is_sticky_pivot`
- Odoo 18 migration concern:
  - These features depend on stable DOM structure and scroll container behavior in form/list/pivot views.
- Verification:
  - Scroll long forms, grouped lists, one2many lists in forms, and pivot screens; confirm sticky elements remain positioned correctly.

### 5. View refresh controls and grouped-list expand/collapse
- What it does:
  - Adds refresh buttons to kanban, list, and calendar control panels.
  - Adds expand/collapse buttons for grouped list views when enabled per user.
- Main frontend files:
  - `static/src/xml/refresh.xml`
  - `static/src/js/list_controller.js`
  - `static/src/js/kanban_controller.js`
  - `static/src/js/calendar_controller.js`
- Configuration surface:
  - `res.users.sh_enable_expand_collapse`
- Odoo 18 migration concern:
  - Patches depend on `web.ListView.Buttons`, `web.KanbanView.Buttons`, and `web.CalendarController.controlButtons`.
  - Grouped list expand/collapse uses jQuery selectors against `.o_group_header` and `.o_group_name`.
- Verification:
  - Open list/kanban/calendar views and confirm refresh buttons appear and reload the current view.
  - Open grouped list view and confirm expand/collapse buttons work.

### 6. Navigation, app drawer, and custom menu service
- What it does:
  - Replaces the top navbar layout, app drawer behavior, menu service, and related menu rendering.
  - Adds multi-tab container slot below the navbar.
  - Modifies viewport meta via `web.layout`.
- Main server files:
  - `views/assets.xml`
- Main frontend files:
  - `static/src/xml/menu.xml`
  - `static/src/xml/navbar.xml`
  - `static/src/js/navbar.js`
  - `static/src/js/menu_service.js`
  - `static/src/js/dropdown.js`
  - `static/src/js/On_refresh.js`
- Local Odoo 18 comparison points:
  - `addons/web/static/src/webclient/navbar/navbar.js`
  - `addons/web/static/src/webclient/navbar/navbar.xml`
- Odoo 18 migration concern:
  - `menu_service.js` removes and re-registers the core `menu` service. This is one of the highest-risk customizations.
  - `menu.xml` replaces most of `web.NavBar`.
  - App drawer behavior uses direct CSS class toggling and assumes current navbar DOM.
- Verification:
  - Open app drawer, switch apps, close drawer, use mobile nav behavior, and confirm menu selection still updates router state correctly.

### 7. Quick menu / bookmarks
- What it does:
  - Lets users bookmark actions or direct URLs, search bookmarks, remove bookmarks, and reopen them from a systray icon.
- Main server files:
  - `models/web_quick_menu.py`
- Main frontend files:
  - `static/src/js/quick_menu_custom.js`
  - `static/src/xml/web_quick_menu.xml`
  - `static/src/scss/quick_menu/quick_menu.scss`
- Persisted model:
  - `sh.wqm.quick.menu`
- Configuration surface:
  - `res.users.sh_enable_quick_menu_mode`
- Odoo 18 migration concern:
  - Depends on current action service controller structure and current URL format.
  - Uses direct `window.location.href` bookmarking, so router format changes can break reopen behavior.
- Verification:
  - Add bookmark from list/form/action, search inside bookmark popup, remove bookmark, and reopen bookmarked items.

### 8. Global search
- What it does:
  - Provides systray search for:
    - menus
    - records across configured models
    - primitive fields, many2one display names, and configured one2many child fields
  - Supports company-aware search logic
- Main server files:
  - `models/global_search.py`
  - `views/global_search_view.xml`
- Main frontend files:
  - `static/src/js/global_search_fronted.js`
  - `static/src/xml/global_search.xml`
  - `static/src/scss/global_search/global_search.scss`
- Config and security:
  - `res.company.enable_menu_search`
  - `res.users.sh_enable_gloabl_search_mode`
  - `group_global_search`
  - models `global.search`, `global.search.fields`, `o2m.global.search.fields`
- Odoo 18 migration concern:
  - Search execution is implemented with broad `search_read()` loops and dynamic field traversal, not indexed backend search.
  - Frontend opens record results through `/mail/view?model=...&res_id=...`.
  - Multi-company label display is effectively disabled in frontend because `show_company` is hardcoded false.
- Verification:
  - Search menu labels, search configured records, search many2one-related data, search one2many child data, and verify navigation to results.

### 9. To-do widget
- What it does:
  - Provides a per-user systray to-do panel with add, edit, complete, and remove actions.
- Main server files:
  - `models/todo.py`
  - `controllers/main.py`
  - `views/todo_card.xml`
- Main frontend files:
  - `static/src/js/todo_custom.js`
  - `static/src/js/todo_widget_custom.js`
  - `static/src/xml/todo.xml`
  - `static/src/xml/todo_card.xml`
  - `static/src/scss/todo/todo.scss`
- Persisted model:
  - `sh.todo`
- Configuration surface:
  - `res.users.sh_enable_todo_mode`
- Odoo 18 migration concern:
  - The widget mixes OWL component registration with direct jQuery DOM mutation and manual render injection.
  - Re-render logic currently rebuilds the accordion from scratch.
- Verification:
  - Add todo, edit title, mark complete, remove item, reload page, and confirm records are user-specific and persisted.

### 10. Language selector
- What it does:
  - Adds a systray language switcher with installed languages and flag images.
- Main server files:
  - `models/web_quick_menu.py` on `res.lang.sh_get_installed_lang`
- Main frontend files:
  - `static/src/js/language_selector_custom.js`
  - `static/src/xml/Language.xml`
  - `static/src/scss/language_selector/language_selector.scss`
- Configuration surface:
  - `res.users.sh_enable_language_selection`
- Odoo 18 migration concern:
  - Directly writes `res.users.lang` and triggers `reload_context`.
  - Relies on current systray component registry and dropdown component APIs.
- Verification:
  - Open selector, switch to another installed language, and confirm interface reloads with new language.

### 11. Calculator systray tool
- What it does:
  - Adds a frontend-only calculator popup in the systray.
- Main frontend files:
  - `static/src/js/calculator_custom.js`
  - `static/src/js/calculate.js`
  - `static/src/xml/Calculator.xml`
  - `static/src/scss/calculator/calculator.scss`
- Configuration surface:
  - `res.users.sh_enable_calculator_mode`
- Odoo 18 migration concern:
  - Uses inline HTML string injection instead of a normal OWL render path.
- Verification:
  - Open calculator, perform arithmetic, and confirm enable/disable toggle hides the systray entry.

### 12. Night mode
- What it does:
  - Adds a systray day/night toggle and persists mode in `localStorage`.
- Main frontend files:
  - `static/src/js/night_mode_custom.js`
  - `static/src/xml/NightMode.xml`
  - `static/src/scss/entmate_night_mode/entmate_night_mode.scss`
  - `static/src/js/On_refresh.js`
- Configuration surface:
  - `res.users.sh_enable_night_mode`
- Important note:
  - The user preference field is commented out in `views/views.xml`, so the feature exists but is not currently exposed in the standard preference view.
- Odoo 18 migration concern:
  - Depends on `.o_web_client` and custom class `sh_night_mode`.
- Verification:
  - Toggle night mode, reload browser, and confirm mode persists.

### 13. Zoom widget
- What it does:
  - Injects a zoom control panel into `web.WebClient` and applies zoom classes to `.o_content`.
- Main frontend files:
  - `static/src/webclient/web_client.js`
  - `static/src/webclient/zoomwidget/zoomwidget_custom.js`
  - `static/src/xml/Zoom.xml`
  - `static/src/scss/zoom_in_out/zoom_in_out.scss`
- Configuration surface:
  - `res.users.sh_enable_zoom`
- Odoo 18 migration concern:
  - Custom component injection depends on `WebClient.components` mutation and template extension.
  - Existing user preferences already warn that sticky features do not work smoothly with zoom.
- Verification:
  - Zoom in, zoom out, reset, then test forms/lists/kanban to ensure layout is still usable.

### 14. Multi-tab navigation
- What it does:
  - Lets users create persistent tabs from menus, stores them on the user, renders a tab strip below the navbar, and supports remove/update flows.
- Main server files:
  - `models/multi_tab.py`
  - `controllers/main.py`
  - `models/web_quick_menu.py` for user relation and session flag
- Main frontend files:
  - `static/src/js/navbar.js`
  - `static/src/webclient/navtab/navtab.js`
  - `static/src/webclient/action_container.js`
  - `static/src/xml/navbar.xml`
  - `static/src/scss/multi_tab_at_control_panel/multi_tab.scss`
- Configuration surface:
  - `res.users.sh_enable_multi_tab`
- Persisted model:
  - `biz.multi.tab`
- Route surface:
  - `/add/mutli/tab`
  - `/get/mutli/tab`
  - `/remove/multi/tab`
  - `/update/tab/details`
- Odoo 18 migration concern:
  - Relies on current action metadata (`actionID`, `xmlid`, URL hash structure).
  - Route names are misspelled as `mutli` and should be preserved unless deliberately migrated with compatibility handling.
  - `ActionContainer` is effectively replaced, which is high risk.
- Verification:
  - Shift-open app/menu to create tab, reload session, switch tabs, remove tabs, and confirm persistence.

### 15. Disable auto-edit mode
- What it does:
  - Forces forms into readonly mode and adds a manual `Edit` button when enabled for the user.
- Main frontend files:
  - `static/src/js/form_controller_custom.js`
  - `static/src/xml/form_controller.xml`
  - `static/src/scss/form_controller/form_controller.scss`
- Configuration surface:
  - `res.users.sh_disable_auto_edit_model`
- Local Odoo 18 comparison points:
  - `addons/web/static/src/views/form/form_controller.js`
  - `addons/web/static/src/views/form/form_controller.xml`
- Odoo 18 migration concern:
  - Patches `FormController` methods and internal mode switching behavior directly.
  - Dialog form handling is special-cased.
- Verification:
  - Open existing record, confirm readonly default, click `Edit`, save, discard, and reopen.

### 16. Open record in new tab
- What it does:
  - Adds:
    - a list-row button to open records in a new browser tab
    - an action menu item to open selected records in new tabs
- Main frontend files:
  - `static/src/js/open_record.js`
  - `static/src/xml/open_record_in_new_tab/action_menus.xml`
  - `static/src/xml/open_record_in_new_tab/list_rendered.xml`
- Configuration surface:
  - `res.users.sh_enable_open_record_in_new_tab`
- Local Odoo 18 comparison points:
  - `addons/web/static/src/views/list/list_renderer.js`
  - `addons/web/static/src/search/action_menus/action_menus.js`
- Odoo 18 migration concern:
  - The list-row column is inserted with jQuery after mount.
  - URL transformation assumes `view_type=list` and swaps to `view_type=form`.
- Verification:
  - Open records from a list row and from the action menu, including grouped lists and multi-select.

### 17. Announcements and bus popup notifications
- What it does:
  - Stores announcement records for selected users and renders top-navbar banner notifications.
  - Supports simple text, styled text, animation, and popup notifications through `bus.bus`.
- Main server files:
  - `models/notifications.py`
  - `views/notifications_view.xml`
- Main frontend files:
  - `static/src/webclient/action_container.js`
  - `static/src/xml/notification.xml`
  - `static/src/scss/notification/notification.scss`
- Persisted model:
  - `sh.announcement`
- Security:
  - menu guarded by `group_web_notification`
- Odoo 18 migration concern:
  - Navbar banner rendering depends on custom `ActionContainer` patch and manual DOM append to `.o_navbar`.
  - Popup notifications use `bus.bus._sendmany`.
  - HTML description exists in model, but the frontend template uses escaped output; intended rich HTML should be revalidated.
- Verification:
  - Create animated banner, non-animated banner, and popup notification; confirm targeted users receive the correct behavior.

### 18. Firebase web push notifications
- What it does:
  - Registers browser push tokens, stores registered users/devices, exposes Firebase config, serves a service worker, and allows manual or scheduled push notifications to user segments.
- Main server files:
  - `models/push_notification.py`
  - `models/send_notification.py`
  - `models/notification_logger.py`
  - `controllers/main.py`
  - `views/views.xml`
  - `views/send_notifications.xml`
  - `views/web_push_notification.xml`
  - `security/base_security.xml`
- Main frontend files:
  - `static/src/js/firebase.js`
  - `static/src/WebPushNotificationFirebaseSetup.pdf`
- Company configuration:
  - `enable_web_push_notification`
  - `api_key`
  - `vapid`
  - `config_details`
- Persisted models:
  - `sh.push.notification`
  - `sh.send.notification`
  - `sh.notification.logger`
- Security and cron:
  - `sh_push_notification_user`
  - cron `Firebase Push Notification` calling `model._push_notification_cron()`
- External dependencies:
  - Firebase CDN scripts `8.4.3` in assets
  - Firebase scripts `8.4.2` in service worker route
  - Python library `pyfcm`
- Odoo 18 migration concern:
  - Service worker registration, Firebase v8 API usage, and permission flow are all legacy.
  - `config_details` is parsed with `safe_eval`.
  - `send_message()` logs success/failure but ignores response details.
- Verification:
  - Configure Firebase, register token from browser, confirm registered users appear, send manual notification, schedule notification, and inspect log history.

### 19. Attachment preview in list view
- What it does:
  - Server side provides attachment metadata per record and frontend code exists to render attachment chips and an inline viewer for image/pdf/text/video content.
- Main server files:
  - `models/web_quick_menu.py` on `res.users.get_attachment_data()`
- Present frontend files:
  - `static/src/js/attachment/attachment.js`
  - `static/src/js/attachment/document_viewer.js`
  - `static/src/js/attachment/pdf.js`
  - `static/src/js/attachment/pdf_worker.js`
  - `static/src/js/attachment/viewer.js`
  - `static/src/xml/attachment.xml`
  - `static/src/xml/document_viewer.xml`
  - `static/src/scss/attachment/attachment.scss`
- Configuration surface:
  - `res.users.show_attachment_in_list_view`
- Important status note:
  - The SCSS is in the manifest.
  - The attachment JS and XML are present in the codebase but are not included in `web.assets_backend`.
  - The user preference field is commented out in `views/views.xml`.
  - Treat this feature as present-in-code but not clearly active in the shipped asset bundle.
- Odoo 18 migration concern:
  - Decide explicitly whether to:
    - reactivate and migrate it
    - keep it dormant
    - remove it
- Verification:
  - If reactivated, verify list-row attachments, viewer open/close, and image/pdf/text/video behavior.

### 20. Discuss / chatter message styling
- What it does:
  - Patches mail message rendering to apply custom left/right chat classes depending on author.
- Main frontend files:
  - `static/src/components/message/message.js`
  - `static/src/xml/message.xml`
- Local Odoo 18 comparison point:
  - `addons/mail/static/src/core/common/message.js`
- Odoo 18 migration concern:
  - Mail is often refactored between Odoo versions; message component APIs are sensitive.
- Verification:
  - Open Discuss or chatter thread and confirm self-authored vs other-authored messages receive correct styling.

### 21. Miscellaneous runtime behavior
- What it does:
  - Adds viewport meta to `web.layout`
  - Registers service worker on document ready
  - Closes overlapping popups on action-area clicks
  - Persists night mode in browser storage
- Main files:
  - `views/assets.xml`
  - `static/src/js/On_refresh.js`
- Odoo 18 migration concern:
  - These behaviors are global and can have side effects outside the intended widgets.
- Verification:
  - Confirm no JS errors on backend load and no unexpected interference with core navigation.

## Configuration Inventory

### `sh.ent.theme.config.settings`
- Identity:
  - `name`
- Theme preset:
  - `theme_style`
- Colors:
  - `primary_color`
  - `extra_color`
  - `secondary_color`
- Header:
  - `header_background_type`
  - `header_background_color`
  - `header_background_image`
  - `header_font_color`
- Body:
  - `body_background_type`
  - `body_background_color`
  - `body_background_image`
  - `body_font_family`
  - `body_google_font_family`
  - `is_used_google_font`
- General style presets:
  - `button_style`
  - `separator_style`
  - `separator_color`
  - `kanban_box_style`
  - `horizontal_tab_style`
  - `form_element_style`
  - `breadcrumb_style`
- Sidebar:
  - `sidebar_color`
  - `sidebar_img`
  - `sidebar_font_color`
- Progress:
  - `progress_style`
  - `progress_height`
  - `progress_color`
- List view:
  - `predefined_list_view_boolean`
  - `predefined_list_view_style`
  - `list_view_border`
  - `list_view_is_hover_row`
  - `list_view_hover_bg_color`
  - `list_view_even_row_color`
  - `list_view_odd_row_color`
- Login page:
  - `login_page_style`
  - `login_page_background_type`
  - `login_page_background_color`
  - `login_page_background_image`
  - `login_page_box_color`
  - `login_page_banner_image`
- Sticky behavior:
  - `is_sticky_form`
  - `is_sticky_list`
  - `is_sticky_list_inside_form`
  - `is_sticky_pivot`
- Icon and input styling:
  - `checkbox_style`
  - `radio_style`
  - `scrollbar_style`
  - `app_icon_style`
  - `dual_tone_icon_color_1`
  - `dual_tone_icon_color_2`
  - `backend_all_icon_style`
- Misc:
  - `is_navbar_style`
- Write-time behavior:
  - Generates SCSS content and writes it into `ir.attachment`
  - Clears registry cache
  - Regenerates asset bundles

### `res.company`
- `enable_menu_search`
- `enable_web_push_notification`
- `api_key`
- `vapid`
- `config_details`

### `res.config.settings`
- Related to `res.company`:
  - `enable_menu_search`
  - `enable_web_push_notification`
  - `api_key`
  - `vapid`
  - `config_details`

### `res.users`
- Functional toggles:
  - `sh_enable_night_mode`
  - `sh_enable_calculator_mode`
  - `sh_enable_gloabl_search_mode`
  - `sh_enable_quick_menu_mode`
  - `sh_enable_todo_mode`
  - `sh_enable_language_selection`
  - `sh_enable_zoom`
  - `sh_enable_multi_tab`
  - `sh_disable_auto_edit_model`
  - `sh_enable_expand_collapse`
  - `show_attachment_in_list_view`
  - `sh_enable_open_record_in_new_tab`
- Relations:
  - `sh_wqm_web_quick_menu_line`
  - `multi_tab_ids`
- Session exposure:
  - Most toggles are injected into `ir.http.session_info()`

### Supporting functional models
- `sh.wqm.quick.menu`
  - `menu_id`, `user_id`, `parent_menu_id`, `sh_url`, `name`
- `sh.todo`
  - `name`, `is_done`, `sequence`, `user_id`
- `global.search`
  - `model_id`, `field_ids`, `main_field_id`, `global_field_ids`
- `global.search.fields`
  - `global_search_id`, `sequence`, `field_id`, `name`, `model_id`, `related_model_id`, `ttype`, `field_ids`
- `o2m.global.search.fields`
  - `sequence`, `name`, `field_id`, `global_o2m_search_id`, `model_id`, `related_model_id`, `ttype`
- `biz.multi.tab`
  - `name`, `url`, `actionId`, `menuId`, `user_id`, `menu_xmlid`
- `sh.announcement`
  - `name`, `description`, `active`, `user_ids`, `font_color`, `background_color`, `date`, `is_animation`, `direction`, `simple_text`, `description_text`, `font_size`, `padding`, `font_family`, `google_font_family`, `is_popup_notification`, `notification_type`
- `sh.push.notification`
  - `user_id`, `user_type`, `datetime`, `register_id`
- `sh.send.notification`
  - `name`, `title`, `message`, `redirect_url`, `logo`, `state`, `message_to`, `specific_ids`, `log_historys`
- `sh.notification.logger`
  - `name`, `error`, `datetime`, `base_config_id`, `status`

## Security and Access Inventory
- Groups from `security/base_security.xml`:
  - `group_global_search`
  - `group_web_notification`
  - `sh_push_notification_user`
- Cron from `security/base_security.xml`:
  - `Firebase Push Notification`
- Access rules from `security/ir.model.access.csv`:
  - full access: `sh.wqm.quick.menu`
  - notification admin access: `sh.announcement` for `group_web_notification`
  - read-only general user access: `sh.announcement`
  - full user access: `sh.push.notification`
  - full user access: `sh.send.notification`
  - full user access: `sh.notification.logger`
  - full user access: `sh.todo`
  - full access: `sh.ent.theme.config.settings`
  - full user access: `global.search`
  - full user access: `global.search.fields`
  - full user access: `o2m.global.search.fields`
  - read/write wizard access: `sh.theme.preview.wizard`
- Menus/actions guarded by group:
  - Global Search configuration menu: `group_global_search`
  - Notification admin menu: `group_web_notification`
  - Push notification menu root and registered-user list: `sh_push_notification_user`

## Technical Extension Points

### Active webclient patches and replacements
- `views/assets.xml`
  - inherits `web.layout` to inject viewport meta
- `views/login_layout.xml`
  - inherits `web.login_layout`
- `static/src/xml/menu.xml`
  - extends and largely replaces `web.NavBar`
- `static/src/js/navbar.js`
  - patches `NavBar.prototype`
- `static/src/js/menu_service.js`
  - removes core `menu` service and adds a custom replacement
- `static/src/webclient/web_client.js`
  - mutates `WebClient.components` and `WebClient.template`
- `static/src/xml/Zoom.xml`
  - extends `web.WebClient`
- `static/src/webclient/action_container.js`
  - patches `ActionContainer.prototype`
  - reassigns `ActionContainer.components`
  - replaces `ActionContainer.template` with inline XML
- `static/src/js/form_controller_custom.js`
  - patches `FormController.prototype`
- `static/src/xml/form_controller.xml`
  - extends `web.FormView`
- `static/src/js/open_record.js`
  - patches `ListRenderer.prototype`
  - patches `ActionMenus.prototype`
- `static/src/xml/open_record_in_new_tab/action_menus.xml`
  - extends `web.ActionMenus`
- `static/src/xml/open_record_in_new_tab/list_rendered.xml`
  - extends `web.ListRenderer.RecordRow`
- `static/src/js/list_controller.js`
  - patches `ListController.prototype`
- `static/src/js/kanban_controller.js`
  - patches `KanbanController.prototype`
- `static/src/js/calendar_controller.js`
  - patches `CalendarController.prototype`
- `static/src/components/message/message.js`
  - patches `mail.core.common.Message.prototype`

### Session and backend integration hooks
- `models/web_quick_menu.py`
  - extends `ir.http.session_info()`
  - generates a `res.users.apikeys` token during session info creation
  - injects external dashboard values from `floor_api.hig_base_url`
- `models/ent_theme_config_model.py`
  - mutates asset attachment and regenerates bundles on settings write

### Inactive or dormant code paths that still matter
- Present but not bundled in manifest:
  - `static/src/js/attachment/*.js`
  - `static/src/xml/attachment.xml`
  - `static/src/xml/document_viewer.xml`
  - `static/src/js/notebook.js`
  - `static/src/webclient/systray_mail_preview.js`
- Present but commented out in manifest:
  - `static/src/js/route_service.js`
  - `static/src/js/action_service.js`
  - `static/src/js/owl.carousel.js`
- Present but not exposed in user preferences:
  - `sh_enable_night_mode`
  - `show_attachment_in_list_view`

## External Dependencies and Integration Risks
- Firebase web SDK from Google CDN:
  - asset bundle loads `8.4.3`
  - service worker route embeds `8.4.2`
- Python dependency:
  - `pyfcm`
- Browser storage:
  - `localStorage` for night mode and tab hints
  - `sessionStorage` for tab highlight state
- JSON-RPC and jQuery:
  - many widgets mix OWL, jQuery, and direct DOM mutation
- Raw SQL:
  - `res.users.get_attachment_data()` queries `ir_attachment` directly
- `safe_eval`:
  - Firebase config parsing in `/web/_config`
- API key generation side effect:
  - `session_info()` generates a `res.users.apikeys` token if needed
- External integration leakage:
  - `customer_dash_token`, `customer_dash_url`, and `customer_dash_user` are added to session info even though they are not theme-specific

## Odoo 18 Upgrade Checklist by Feature
- Core theming:
  - Confirm generated SCSS still loads through `web._assets_primary_variables`
  - Confirm `ir.attachment.regenerate_assets_bundles()` remains valid or replace with Odoo 18 asset invalidation pattern
- Theme configurator:
  - Revalidate systray component registration and DOM IDs used by `theme_config_custom.js`
- Login customization:
  - Revalidate `web.login_layout` inheritance against `addons/web/views/webclient_templates.xml`
- Sticky features:
  - Recheck selectors and scroll containers in form/list/pivot layouts
- Refresh and expand/collapse:
  - Recheck control panel template names and grouped row selectors
- Navbar and menu service:
  - Reconcile custom menu service with Odoo 18 router/menu lifecycle
  - Rebase custom navbar replacement on Odoo 18 `web.NavBar`
- Quick menu:
  - Revalidate current action metadata and URL format
- Global search:
  - Revalidate `/mail/view` record opening pattern
  - Review performance and multi-company behavior
- To-do:
  - Replace brittle jQuery/DOM flows if Odoo 18 rendering breaks current approach
- Language selector:
  - Revalidate systray dropdown API and user language reload flow
- Calculator:
  - Revalidate systray mount and inline HTML injection
- Night mode:
  - Revalidate top-level client class selectors
- Zoom:
  - Revalidate `WebClient` injection and `.o_content` zoom class target
- Multi-tab:
  - Revalidate route hash format, action metadata, and `ActionContainer` replacement
- Disable auto-edit:
  - Revalidate form controller internals
- Open in new tab:
  - Revalidate list renderer hooks and action menu template extension
- Announcements:
  - Revalidate custom `ActionContainer` append point and bus notification compatibility
- Firebase push:
  - Replace or confirm Firebase v8 compatibility on Odoo 18
  - Revalidate service worker registration and browser permission flow
- Attachment preview:
  - Decide explicit status: migrate, keep dormant, or remove
- Discuss styling:
  - Revalidate mail message component patch

## Regression Test Matrix
1. Install the addon cleanly on Odoo 18 and confirm no manifest or asset errors.
2. Open backend as admin and confirm navbar, app drawer, and systray render without JS tracebacks.
3. Open Theme Configuration form and save a theme preset.
4. Change manual colors and confirm they persist after reload.
5. Upload body/header/login images and confirm they apply.
6. Open login page and confirm custom layout renders.
7. Toggle app drawer and switch between apps.
8. Add, search, reopen, and remove a quick menu bookmark.
9. Configure `global.search` for at least one model and confirm menu + record search work.
10. Add, edit, complete, and remove to-do entries.
11. Change user language from systray and confirm reload.
12. Enable calculator and verify calculator opens and computes.
13. Enable night mode manually in data and confirm toggle works and persists.
14. Enable zoom and verify increase, decrease, and reset work.
15. Enable multi-tab, create tabs, reload browser, and confirm persistence.
16. Enable disable-auto-edit and confirm readonly default plus explicit edit flow.
17. Enable open-record-in-new-tab and verify both list button and action menu path.
18. Open list, kanban, and calendar views and confirm refresh button behavior.
19. Open grouped list view and confirm expand/collapse behavior.
20. Create banner announcement and confirm it appears for target user.
21. Create popup announcement and confirm bus notification is received.
22. Configure Firebase, register browser token, and confirm `sh.push.notification` records appear.
23. Send a push notification manually and confirm log entry is created.
24. Schedule a push notification and confirm cron processing.
25. Open Discuss/chatter and confirm self/other message styling.
26. If attachment preview is reactivated, verify attachment chips and viewer behavior.

## Open Risks and Likely Breakpoints
- Highest risk:
  - full custom `menu` service replacement
  - `ActionContainer` template replacement
  - `WebClient.components` mutation
  - heavy jQuery DOM manipulation against Odoo internals
- Asset pipeline risk:
  - generated SCSS attachment and bundle regeneration strategy may differ in Odoo 18
- Legacy integration risk:
  - Firebase v8 APIs, service worker flow, and `pyfcm`
- Hidden/dormant feature risk:
  - attachment preview code exists but is not clearly active
  - night mode exists but its user toggle is hidden
- Security/side-effect risk:
  - `session_info()` generates API keys and exposes unrelated dashboard fields
- Performance risk:
  - `global.search` loops all configured models/records with broad `search_read()`
- Functional correctness risk:
  - open-record-in-new-tab and bookmarks depend on current URL structure
  - multi-tab depends on action metadata and hash routes

## Assumptions and Defaults Used for This Inventory
- The current codebase is the source of truth, not marketplace screenshots or sales text.
- The local Odoo 18 source at `/home/ahmed/odoo-community-setup/Odoo-Repos/Odoo-18` is the comparison baseline for upgrade touchpoints.
- Features present in code but not clearly wired into assets are still in scope and must be consciously migrated, kept dormant, or removed.
- No feature has been intentionally dropped yet.
- No runtime API changes are proposed in this documentation step.

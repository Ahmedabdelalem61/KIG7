# Odoo 18 Tour Coverage Matrix — `sh_entmate_theme`

Maps the [regression test matrix](odoo18_feature_inventory.md#regression-test-matrix) and functional inventory items to automated web tours in `TestShEntmateThemeTours`.

**Run all tours:**

```bash
/home/ahmed/odoo-18.0-community/.venv/bin/python /home/ahmed/odoo-18.0-community/odoo-bin \
  -c /home/ahmed/Downloads/odoo18_sh_entmate_test.conf \
  -d sh_entmate_test \
  --test-enable --stop-after-init \
  --test-tags=/sh_entmate_theme:TestShEntmateThemeTours
```

**Last verified:** 14/14 tours green (Phase A + B + follow-ups).

---

## Summary

| Status | Count | Meaning |
|--------|------:|---------|
| Automated | 18 | Covered by at least one tour (UI and/or RPC mock) |
| Partial | 5 | Tour touches feature but not full inventory checklist |
| Deferred | 3 | Requires manual QA, cron, or assets not loaded in tests |
| N/A | 2 | Install/manifest or dormant code paths |

---

## Tour catalog

| Tour | Test method | Primary features |
|------|-------------|------------------|
| `sh_entmate_theme_smoke_shell` | `test_sh_entmate_theme_smoke_shell` | App drawer, banner announcement, night mode, calculator, zoom, language dropdown |
| `sh_entmate_theme_quick_menu_and_todo` | `test_sh_entmate_theme_quick_menu_and_todo` | Bookmarks, quick menu search/remove, todo CRUD |
| `sh_entmate_theme_theme_config_and_search` | `test_sh_entmate_theme_theme_config_and_search` | Systray theme config, global search → record |
| `sh_entmate_theme_form_list_multitab` | `test_sh_entmate_theme_form_list_multitab` | Global search, disable-auto-edit form, list, multi-tab + list row |
| `sh_entmate_theme_push_and_mocked_browser_features` | `test_sh_entmate_theme_push_and_mocked_browser_features` | Firebase/SW mocks, push token RPC, app drawer |
| `sh_entmate_theme_login_frontend` | `test_sh_entmate_theme_login_frontend` | Custom login layout |
| `sh_entmate_theme_navigation` | `test_sh_entmate_theme_navigation` | App drawer → custom menu action |
| `sh_entmate_theme_view_refresh` | `test_sh_entmate_theme_view_refresh` | List + kanban refresh buttons |
| `sh_entmate_theme_list_group_expand` | `test_sh_entmate_theme_list_group_expand` | Grouped list expand/collapse buttons |
| `sh_entmate_theme_theme_backend` | `test_sh_entmate_theme_theme_backend` | Systray theme preset + reload marker |
| `sh_entmate_theme_announcement_popup` | `test_sh_entmate_theme_announcement_popup` | `notify_user` RPC + notification UI |
| `sh_entmate_theme_discuss_chatter` | `test_sh_entmate_theme_discuss_chatter` | Chatter + left/right message classes |
| `sh_entmate_theme_multitab_persist` | `test_sh_entmate_theme_multitab_persist` | Multi-tab add + `/get/mutli/tab` restore |
| `sh_entmate_theme_language_switch` | `test_sh_entmate_theme_language_switch` | `fr_FR` write + `reload_context` + `html[lang]` |

**Helpers:** `static/tests/tours/sh_entmate_theme_tour_helpers.js` (`window.__shThemeTour`).

---

## Regression matrix (26 items) → coverage

| # | Inventory item | Status | Tour(s) | Notes |
|---|----------------|--------|---------|-------|
| 1 | Clean install / no asset errors | N/A | — | Module load implied by `post_install` test class |
| 2 | Navbar, app drawer, systray without JS errors | **Automated** | `smoke_shell`, `navigation`, `push_and_mocked_browser_features` | `body[data-sh-theme-error-count="0"]` on push tour |
| 3 | Theme Configuration form save | **Partial** | `theme_backend`, `theme_config_and_search` | Systray configurator only; not backend form view |
| 4 | Manual colors persist after reload | **Partial** | `theme_config_and_search` | Preset click + reload count; not every color field |
| 5 | Upload body/header/login images | **Deferred** | — | Manual / file upload |
| 6 | Login page custom layout | **Automated** | `login_frontend` | DB selector + login field |
| 7 | App drawer + switch apps | **Automated** | `navigation`, `smoke_shell`, `view_refresh`, `list_group_expand` | Custom partners menu |
| 8 | Quick menu bookmark lifecycle | **Automated** | `quick_menu_and_todo` | Pin, search, remove |
| 9 | Global search (menu + records) | **Automated** | `theme_config_and_search`, `discuss_chatter`, `form_list_multitab` | Partner model configured in `setUpClass` |
| 10 | To-do add/edit/complete/remove | **Automated** | `quick_menu_and_todo` | RPC + DOM helpers |
| 11 | Language switch + reload | **Automated** | `language_switch`, `smoke_shell` | Dropdown click + `reload_context`; session verified via `/web/session/get_session_info` |
| 12 | Calculator open + compute | **Automated** | `smoke_shell` | Delegated handlers in `calculate.js` |
| 13 | Night mode toggle + persist | **Partial** | `smoke_shell` | Toggle only; `localStorage` persist not asserted |
| 14 | Zoom in/out/reset | **Automated** | `smoke_shell` | Systray or `ensureZoomControl()` fallback |
| 15 | Multi-tab create + persist | **Automated** | `multitab_persist`, `form_list_multitab` | RPC routes; list row open in combined tour |
| 16 | Disable auto-edit + Edit button | **Automated** | `form_list_multitab` | `.sh_form_button_edit` → save |
| 17 | Open record in new tab | **Deferred** | — | Needs `sh_enable_open_record_in_new_tab` UI tour |
| 18 | List/kanban/calendar refresh | **Partial** | `view_refresh` | List + kanban; calendar not in tour |
| 19 | Grouped list expand/collapse | **Automated** | `list_group_expand` | Buttons on partners list |
| 20 | Banner announcement | **Automated** | `smoke_shell`, `push_and_mocked_browser_features` | `#object1` banner text |
| 21 | Popup announcement / bus | **Automated** | `announcement_popup` | RPC + notification service (websocket 503 in headless) |
| 22 | Firebase token registration | **Automated** | `push_and_mocked_browser_features` | Mocked SW/Firebase; asserts `sh.push.notification` |
| 23 | Manual push send + log | **Deferred** | — | `sh.send.notification` wizard / FCM |
| 24 | Scheduled push + cron | **Deferred** | — | Cron `Firebase Push Notification` |
| 25 | Discuss/chatter message styling | **Automated** | `discuss_chatter` | `.sh_left_chat` / `.sh_right_chat` |
| 26 | Attachment preview in list | **Deferred** | — | JS not in `web.assets_backend`; feature dormant |

---

## Functional inventory (§1–21) → coverage

| § | Feature | Status | Tour(s) |
|---|---------|--------|---------|
| 1 | Core backend theming | **Partial** | `theme_config_and_search`, `theme_backend` | Visual SCSS not pixel-tested |
| 2 | Theme configurator UI | **Automated** | `theme_config_and_search`, `theme_backend` | Systray panel |
| 3 | Login customization | **Automated** | `login_frontend` |
| 4 | Sticky form/list/pivot | **Deferred** | — | CSS-only; scroll QA manual |
| 5 | Refresh + expand/collapse | **Automated** | `view_refresh`, `list_group_expand` |
| 6 | Navigation / app drawer / menu | **Automated** | `navigation`, `smoke_shell`, others |
| 7 | Quick menu / bookmarks | **Automated** | `quick_menu_and_todo` |
| 8 | Global search | **Automated** | `theme_config_and_search`, `form_list_multitab`, `discuss_chatter` |
| 9 | To-do widget | **Automated** | `quick_menu_and_todo` |
| 10 | Language selector | **Automated** | `language_switch`, `smoke_shell` |
| 11 | Calculator | **Automated** | `smoke_shell` |
| 12 | Night mode | **Partial** | `smoke_shell` |
| 13 | Zoom widget | **Automated** | `smoke_shell` |
| 14 | Multi-tab navigation | **Automated** | `multitab_persist`, `form_list_multitab` |
| 15 | Disable auto-edit | **Automated** | `form_list_multitab` |
| 16 | Open record in new tab | **Deferred** | — |
| 17 | Announcements + popup | **Automated** | `smoke_shell`, `announcement_popup` |
| 18 | Firebase web push | **Partial** | `push_and_mocked_browser_features` | Registration only |
| 19 | Attachment preview | **Deferred** | — | Not in assets bundle |
| 20 | Discuss/chatter styling | **Automated** | `discuss_chatter` |
| 21 | Miscellaneous runtime | **Partial** | `push_and_mocked_browser_features` | Error count guard |

---

## Deferred / manual follow-ups

1. **Open in new tab** — tour with `sh_enable_open_record_in_new_tab` on list + action menu.
2. **Calendar refresh** — extend `view_refresh` with calendar action or sample event.
3. **Push send + cron** — server tests on `sh.send.notification` / cron, not browser tour.
4. **Theme backend form** — `sh.ent.theme.config.settings` form save (separate from systray).
5. **Sticky views** — visual/scroll tests or screenshot tour.
6. **Attachment preview** — only after assets wired in `__manifest__.py`.

---

## Test data (Python)

Defined in `tests/test_web_tours.py` `setUpClass`:

- Admin user flags (calculator, zoom, multi-tab, expand/collapse, etc.)
- `global.search` on `res.partner`
- Partners tree + `partners_action` / `grouped_partners_action`
- Banner + popup `sh.announcement`
- `fr_FR` language for language tours
- Chatter seed message on search partner

---

## Known test environment limits

| Limit | Impact | Mitigation in tours |
|-------|--------|---------------------|
| WebSocket `/websocket` → 503 | Bus popup may not arrive live | `triggerPopupAnnouncement` → `notification.add()` |
| Headless layout | Zoom systray sometimes hidden | `ensureZoomControl()` fallback |
| External Firebase CDN 404 | Expected in tests | Mocked `window.firebase` + SW |
| Odoo 18 tour schema | No `timeout` on passive-only steps | `timeout` only with `run` or long triggers |

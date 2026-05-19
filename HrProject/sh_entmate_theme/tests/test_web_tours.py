from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestShEntmateThemeTours(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.admin = env.ref("base.user_admin").sudo()
        cls.company = cls.admin.company_id.sudo()
        cls.global_search_group = env.ref("sh_entmate_theme.group_global_search")
        cls.global_search_group.sudo().write({"users": [(4, cls.admin.id)]})

        cls.user_feature_flags = {
            "sh_enable_quick_menu_mode": True,
            "sh_enable_todo_mode": True,
            "sh_enable_language_selection": True,
            "sh_enable_zoom": True,
            "sh_enable_multi_tab": True,
            "sh_enable_open_record_in_new_tab": True,
            "sh_enable_gloabl_search_mode": True,
            "sh_disable_auto_edit_model": True,
            "sh_enable_calculator_mode": True,
            "sh_enable_night_mode": True,
            "sh_enable_expand_collapse": True,
            "show_attachment_in_list_view": True,
        }
        cls.admin.write({**cls.user_feature_flags, "lang": "en_US"})
        cls.company.write({"enable_menu_search": True})
        cls._admin_lang_baseline = cls.admin.lang

        partner_model = env["ir.model"].sudo()._get("res.partner")
        partner_name_field = env["ir.model.fields"].sudo().search(
            [("model", "=", "res.partner"), ("name", "=", "name")],
            limit=1,
        )
        cls.global_search_config = env["global.search"].sudo().create(
            {
                "model_id": partner_model.id,
                "main_field_id": partner_name_field.id,
                "field_ids": [(6, 0, [partner_name_field.id])],
            }
        )
        env["global.search.fields"].sudo().create(
            {
                "global_search_id": cls.global_search_config.id,
                "field_id": partner_name_field.id,
                "model_id": partner_model.id,
            }
        )

        cls.partner_parent = env["res.partner"].sudo().create(
            {
                "name": "Sh Theme Tour Parent Company",
                "is_company": True,
            }
        )
        cls.search_partner = env["res.partner"].sudo().create(
            {
                "name": "Sh Theme Tour Search Partner",
                "parent_id": cls.partner_parent.id,
            }
        )
        cls.partner_parent_b = env["res.partner"].sudo().create(
            {
                "name": "Sh Theme Tour Parent Company B",
                "is_company": True,
            }
        )
        cls.extra_partner = env["res.partner"].sudo().create(
            {
                "name": "Sh Theme Tour Secondary Partner",
                "parent_id": cls.partner_parent_b.id,
            }
        )
        cls.tour_user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .sudo()
            .create(
                {
                    "name": "Sh Theme Tour User",
                    "login": "sh_theme_tour_user",
                    "email": "sh_theme_tour_user@example.com",
                    "groups_id": [(6, 0, [env.ref("base.group_user").id])],
                    "company_id": cls.company.id,
                    "company_ids": [(6, 0, [cls.company.id])],
                }
            )
        )

        cls.announcement = env["sh.announcement"].sudo().create(
            {
                "name": "Sh Theme Tour Announcement",
                "active": True,
                "user_ids": [(6, 0, [cls.admin.id])],
                "simple_text": True,
                "description_text": "Sh Theme Tour Announcement",
                "font_color": "#ffffff",
                "background_color": "#111111",
                "font_size": 12,
                "padding": 6,
                "font_family": "Roboto",
                "is_popup_notification": False,
            }
        )

        cls.theme_settings = env["sh.ent.theme.config.settings"].sudo().browse(1)
        cls.theme_baseline = {
            "theme_style": cls.theme_settings.theme_style,
            "sidebar_img": cls.theme_settings.sidebar_img,
        }

        cls.partners_action = env["ir.actions.act_window"].sudo().create(
            {
                "name": "Sh Theme Tour Partners Action",
                "res_model": "res.partner",
                "view_mode": "list,kanban,form",
                "domain": [("name", "ilike", "Sh Theme Tour")],
            }
        )
        cls.grouped_partners_action = env["ir.actions.act_window"].sudo().create(
            {
                "name": "Sh Theme Tour Grouped Partners",
                "res_model": "res.partner",
                "view_mode": "list,form",
                "domain": [
                    ("name", "ilike", "Sh Theme Tour"),
                    ("parent_id", "!=", False),
                ],
                "context": {"group_by": "parent_id"},
            }
        )
        cls.theme_settings_action = env["ir.actions.act_window"].sudo().create(
            {
                "name": "Sh Theme Tour Theme Settings",
                "res_model": "sh.ent.theme.config.settings",
                "view_mode": "form",
                "res_id": cls.theme_settings.id,
                "target": "current",
            }
        )
        cls.users_action = env["ir.actions.act_window"].sudo().create(
            {
                "name": "Sh Theme Tour Users Action",
                "res_model": "res.users",
                "view_mode": "list,form",
            }
        )
        cls.partners_menu = env["ir.ui.menu"].sudo().create(
            {
                "name": "Sh Theme Tour Partners App",
                "parent_id": False,
                "sequence": 9990,
                "action": f"ir.actions.act_window,{cls.partners_action.id}",
            }
        )
        cls.users_menu = env["ir.ui.menu"].sudo().create(
            {
                "name": "Sh Theme Tour Users App",
                "parent_id": False,
                "sequence": 9991,
                "action": f"ir.actions.act_window,{cls.users_action.id}",
            }
        )

        cls.search_partner.message_post(body="Sh Theme Tour Chatter Message")

        cls.popup_announcement = env["sh.announcement"].sudo().create(
            {
                "name": "Sh Theme Tour Popup Announcement",
                "active": True,
                "user_ids": [(6, 0, [cls.admin.id])],
                "simple_text": True,
                "description_text": "Sh Theme Tour Popup Announcement",
                "is_popup_notification": True,
                "notification_type": "warning",
            }
        )

        cls.extra_lang = env["res.lang"].with_context(active_test=False).sudo().search(
            [("code", "=", "fr_FR")], limit=1
        )
        if not cls.extra_lang:
            cls.extra_lang = env["res.lang"].sudo().create(
                {
                    "name": "French",
                    "code": "fr_FR",
                    "iso_code": "fr",
                    "url_code": "fr",
                }
            )
        cls.extra_lang.sudo().write({"active": True})

    @classmethod
    def tearDownClass(cls):
        cls.theme_settings.sudo().write(cls.theme_baseline)
        cls.company.sudo().write(
            {
                "enable_menu_search": True,
                "enable_web_push_notification": False,
                "api_key": False,
                "vapid": False,
                "config_details": False,
            }
        )
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self._reset_tour_state()

    def _reset_tour_state(self):
        self.admin.sudo().write({**self.user_feature_flags, "lang": self._admin_lang_baseline})
        self.company.sudo().write(
            {
                "enable_menu_search": True,
                "enable_web_push_notification": False,
                "api_key": False,
                "vapid": False,
                "config_details": False,
            }
        )
        self.theme_settings.sudo().write(self.theme_baseline)
        self.env["biz.multi.tab"].sudo().search([("user_id", "=", self.admin.id)]).unlink()
        self.env["sh.wqm.quick.menu"].sudo().search([("user_id", "=", self.admin.id)]).unlink()
        self.env["sh.todo"].sudo().search([("user_id", "=", self.admin.id)]).unlink()
        self.env["sh.push.notification"].sudo().search(
            [("register_id", "=", "tour-token")]
        ).unlink()
        self.env["sh.todo"].sudo().create(
            {
                "name": "Sh Theme Tour Seed Todo",
                "user_id": self.admin.id,
            }
        )
        self._seed_quick_menus()

    def _seed_quick_menus(self):
        quick_menu_model = self.env["sh.wqm.quick.menu"].sudo()
        for index in range(1, 15):
            quick_menu_model.create(
                {
                    "user_id": self.admin.id,
                    "name": f"Quick Seed {index:02d}",
                    "sh_url": (
                        f"#menu_id={self.partners_menu.id}"
                        f"&action={self.partners_action.id}"
                        f"&model=res.partner&view_type=list&seed={index}"
                    ),
                }
            )

    def _enable_push_config(self):
        self.company.sudo().write(
            {
                "enable_web_push_notification": True,
                "api_key": "tour-api-key",
                "vapid": "tour-vapid-key",
                "config_details": """
{
  apiKey: "tour-api-key",
  authDomain: "tour.example.com",
  projectId: "tour-project",
  storageBucket: "tour-project.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abcdef123456",
  measurementId: "G-TOUR1234"
}
                """.strip(),
            }
        )

    def test_sh_entmate_theme_smoke_shell(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_smoke_shell",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_quick_menu_and_todo(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_quick_menu_and_todo",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_theme_config_and_search(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_theme_config_and_search",
            login="admin",
            timeout=240,
        )

    def test_sh_entmate_theme_form_list_multitab(self):
        self.start_tour(
            "/odoo",
            "sh_entmate_theme_form_list_multitab",
            login="admin",
            timeout=240,
        )

    def test_sh_entmate_theme_push_and_mocked_browser_features(self):
        self._enable_push_config()
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_push_and_mocked_browser_features",
            login="admin",
            timeout=180,
        )
        self.assertTrue(
            self.env["sh.push.notification"]
            .sudo()
            .search_count([("register_id", "=", "tour-token")]),
            "Expected the mocked push flow to register the test token.",
        )

    def test_sh_entmate_theme_login_frontend(self):
        self.start_tour(
            "/web/login?db=sh_entmate_test",
            "sh_entmate_theme_login_frontend",
            login=None,
            timeout=120,
        )

    def test_sh_entmate_theme_navigation(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_navigation",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_view_refresh(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_view_refresh",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_list_group_expand(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_list_group_expand",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_theme_backend(self):
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_theme_backend",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_announcement_popup(self):
        self.start_tour(
            "/odoo",
            "sh_entmate_theme_announcement_popup",
            login="admin",
            timeout=120,
        )

    def test_sh_entmate_theme_discuss_chatter(self):
        self.start_tour(
            "/odoo",
            "sh_entmate_theme_discuss_chatter",
            login="admin",
            timeout=240,
        )

    def test_sh_entmate_theme_multitab_persist(self):
        self.env["biz.multi.tab"].sudo().search([("user_id", "=", self.admin.id)]).unlink()
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_multitab_persist",
            login="admin",
            timeout=180,
        )

    def test_sh_entmate_theme_language_switch(self):
        self.admin.sudo().write({"lang": "en_US"})
        self.start_tour(
            f"/odoo/action-{self.partners_action.id}",
            "sh_entmate_theme_language_switch",
            login="admin",
            timeout=240,
        )

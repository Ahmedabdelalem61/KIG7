/* @odoo-module */

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { user } from "@web/core/user";
import { rpc as jsonrpc } from "@web/core/network/rpc";
import { Dropdown } from "@web/core/dropdown/dropdown";

export class LanguageTemplate extends Component {
       static components = { Dropdown };
       static template = "LanguageTemplate";

       setup() {
            this.languages_list = [];
            this.selected_lang = user.lang;
            this.show_language_selector = session.sh_enable_language_selection;
            this.actionService = useService("action");
            this.orm = useService("orm");
            onWillStart(() => this.fetch_sh_get_installed_lang());
       }

       async fetch_sh_get_installed_lang() {
            var self = this;
            jsonrpc("/web/dataset/call_kw/res.lang/sh_get_installed_lang", {
                    model: 'res.lang',
                    method: 'sh_get_installed_lang',
                    args: [],
                    kwargs: {},
                }).then(function (languages) {
                    self.languages_list = languages
                    self.selected_lang = user.lang
                    self.render();
                    });
       }

       onBeforeOpen() {
        this.fetch_sh_get_installed_lang();
        }

       change_sh_user_lang(e){
            var self = this;
            var lang = e[0]
            var self = this;

            this.orm.write("res.users", [user.userId], { lang: lang }).then(function () {
            self.actionService.doAction({
                        name: 'Reload Context',
                        type: 'ir.actions.client',
                        tag: 'reload_context',
                    });
        });
        }
}

registry.category("systray").add("sh_entmate_theme.language_template", { Component: LanguageTemplate });

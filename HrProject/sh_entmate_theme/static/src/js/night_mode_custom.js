/* @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export class NightMode extends Component {
       static template = "NightModeTemplate";

       setup() {
            this.show_night_mode = session.sh_enable_night_mode;
        if ($('.o_web_client').hasClass('sh_night_mode')) {
            this.day_mode = false;
        } else {
            this.day_mode = true;
        }
       }

        _click_moon_button() {
			localStorage.setItem("is_night_mode", "t");
			$('.o_web_client').addClass('sh_night_mode');
			$('#moon_button').css("display", "none");
			$('#sun_button').css("display", "inline-flex");
		}

		_click_sun_button() {
			localStorage.setItem("is_night_mode", "f");
			$('.o_web_client').removeClass('sh_night_mode');
			$('#moon_button').css("display", "inline-flex");
			$('#sun_button').css("display", "none");
		}

}

registry.category("systray").add("NightModeTemplate", { Component: NightMode });

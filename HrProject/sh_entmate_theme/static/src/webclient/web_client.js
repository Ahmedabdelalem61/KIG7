/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { ActionContainer } from "@web/webclient/actions/action_container";
import { NavBar } from "@web/webclient/navbar/navbar";
import { MainComponentsContainer } from "@web/core/main_components_container";
import { patch } from "@web/core/utils/patch";


patch(WebClient.prototype, {
    // _loadDefaultApp() {
    //     if($(".sh_entmate_theme_appmenu_div").hasClass("sh_first_load")){
    //         $(".sh_entmate_theme_appmenu_div").removeClass("show")
    //         $(".sh_entmate_theme_appmenu_div").removeClass("sh_first_load")
    //         // return this._super();
    //     }
       
    //     $(".sh_entmate_theme_appmenu_div").addClass("show")
    //     $("body").addClass("sh_sidebar_background_enterprise");
    //     $(".sh_entmate_theme_appmenu_div").css("opacity", "1");
    //     $(".o_action_manager").addClass("d-none");
    //     $(".full").addClass("sidebar_arrow");
    //     $(".o_menu_brand").css("display", "none");
    //     $(".o_menu_sections").css("display", "none");
    //     // Standard code commnet
    //     // const root = this.menuService.getMenu("root");
    //     // const firstApp = root.children[0];
    //     // if (firstApp) {
    //     //     return this.menuService.selectMenu(firstApp);
    //     // }
    //     // return this._super();

        
    // }

});
	WebClient.components = {
		ActionContainer,
        NavBar,
        MainComponentsContainer,
	};

WebClient.template = "web.WebClient";


	



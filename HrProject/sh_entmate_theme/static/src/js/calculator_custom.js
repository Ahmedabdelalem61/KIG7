/* @odoo-module */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { renderToElement } from "@web/core/utils/render";

export class CalculaterSh extends Component {
       static template = "CalculatorTemplate";

       setup() {
            this.show_calculator = session.sh_enable_calculator_mode;
       }


       onClickCalculator() {
          const $ = window.jQuery;
          if (!$) {
              return;
          }
          if($('.calculator').length > 0){
        	  $(".sh_calc_results").html("");
          }else{
        	  $(".sh_calc_results").empty().append(renderToElement("sh_entmate_theme.CalcResults"));
          }

          if($('.sh_calc_util').hasClass('active')){
        	  $('.sh_calc_util').removeClass('active')
          }else{
        	  $('.sh_calc_util').addClass('active')
          }

          // close other popup
          $('.sh_user_language_list_cls').css("display","none")
          $('.sh_wqm_quick_menu_submenu_list_cls').css("display","none")
          $('.todo_layout').removeClass("sh_theme_model");
       }

}

registry.category("systray").add("sh_entmate_theme.calculater_sh", { Component: CalculaterSh }, { sequence: 25 });

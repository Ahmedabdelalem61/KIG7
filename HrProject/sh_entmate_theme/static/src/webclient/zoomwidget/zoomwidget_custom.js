/** @odoo-module **/

import { Component } from "@odoo/owl";
import { session } from "@web/session";
import { registry } from "@web/core/registry";

export class ZoomWidget extends Component {
    static template = "ZoomSystrayTemplate";

    setup() {
        this.show_zoom = !!session.sh_enable_zoom;
    }

    setResetZoom(){
        var zoom = $('.sh_full').text().split('%')
        if($('.o_content').find('div')[0]){
            $($('.o_content').find('div')[0]).removeClass("sh_zoom_"+zoom[0])
            zoom = 100
            $('.sh_full').text(zoom.toString()+'%');
            $($('.o_content').find('div')[0]).addClass("sh_zoom_"+zoom)
        }
    }
    zoomDropdown(ev){
            if ($('.sh-zoom-panel').css('display') == 'none')
            {                   
                $('.sh-zoom-panel').css('display','table')
            }else{
                $('.sh-zoom-panel').css('display','none')
            }
    }
    setDecZoom(){
        var zoom = $('.sh_full').text().split('%')
        if(parseInt(zoom[0])-10 >= 20 && parseInt(zoom[0])-10 <= 200){
            if($('.o_content').find('div')[0]){
                $($('.o_content').find('div')[0]).removeClass("sh_zoom_"+zoom[0])
                zoom = parseInt(zoom[0])-10
                $('.sh_full').text(zoom.toString()+'%');
                $($('.o_content').find('div')[0]).addClass("sh_zoom_"+zoom)
            }
        }
    }
    setIncZoom(){
        var zoom = $('.sh_full').text().split('%')
        if(parseInt(zoom[0])+10 >= 20 && parseInt(zoom[0])+10 <= 200){
            if($('.o_content').find('div')[0]){
                $($('.o_content').find('div')[0]).removeClass("sh_zoom_"+zoom[0])
                zoom = parseInt(zoom[0])+10
                $('.sh_full').text(zoom.toString()+'%');
                $($('.o_content').find('div')[0]).addClass("sh_zoom_"+zoom)
            }
        }
    }
}

registry.category("systray").add(
    "sh_entmate_theme.ZoomWidget",
    {
        Component: ZoomWidget,
        isDisplayed: () => Boolean(session.sh_enable_zoom),
    },
    { sequence: 24 }
);

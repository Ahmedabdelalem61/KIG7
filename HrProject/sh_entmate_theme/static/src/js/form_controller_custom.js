/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(FormController.prototype, {

     async setup() {
        await super.setup();
        if (this.footerArchInfo) {
            // If dialogue box then need to give edit permission
            this.props.preventEdit = false;
        }
        else if (session.sh_disable_auto_edit_model){
            this.model.config.mode = 'readonly';
        }
    },

    disableEditButton() {
        return session.sh_disable_auto_edit_model;
    },

    _onClickEditView() {
        this.model.root.switchMode("edit");
    },

    async saveButtonClicked(params = {}) {
        await super.saveButtonClicked(params);
        if (session.sh_disable_auto_edit_model) {
            await this.model.root.switchMode("readonly");
        }
    },

    async discard() {
        await super.discard();
        if (session.sh_disable_auto_edit_model) {
            await this.model.root.switchMode("readonly");
        }
    },
});

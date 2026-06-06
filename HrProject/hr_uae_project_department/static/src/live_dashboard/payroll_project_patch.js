/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { HrUaePayrollLiveDashboard } from "@hr_uae_payroll/live_dashboard/payroll_live_dashboard";

patch(HrUaePayrollLiveDashboard.prototype, {
    openProject(projectId) {
        if (!projectId) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.uae.payroll.dashboard",
            domain: [["department_id", "=", projectId]],
            views: [[false, "list"]],
            target: "current",
        });
    },
});

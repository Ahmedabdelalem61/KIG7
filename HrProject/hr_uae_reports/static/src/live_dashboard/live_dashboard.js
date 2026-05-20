/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatFloat } from "@web/core/utils/numbers";

export class HrUaeLiveDashboard extends Component {
    static template = "hr_uae_reports.HrUaeLiveDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            data: null,
            lastRefresh: null,
            error: null,
        });

        onWillStart(async () => {
            await this.fetch();
        });
    }

    async fetch() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const data = await this.orm.call(
                "hr.uae.dashboard",
                "fetch_dashboard_data",
                []
            );
            this.state.data = data;
            this.state.lastRefresh = new Date();
        } catch (err) {
            this.state.error = err.message || String(err);
            this.notification.add(this.state.error, { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    formatCurrency(amount) {
        const cur = this.state.data?.currency || { symbol: "AED", position: "after" };
        const value = formatFloat(amount || 0, { digits: [69, 2] });
        return cur.position === "before" ? `${cur.symbol} ${value}` : `${value} ${cur.symbol}`;
    }

    pieSegments(items) {
        const total = items.reduce((s, x) => s + (x.value || 0), 0) || 1;
        let cumulative = 0;
        const radius = 90;
        const cx = 100;
        const cy = 100;
        return items.map((item, idx) => {
            const start = (cumulative / total) * Math.PI * 2 - Math.PI / 2;
            cumulative += item.value;
            const end = (cumulative / total) * Math.PI * 2 - Math.PI / 2;
            const large = end - start > Math.PI ? 1 : 0;
            const x1 = cx + radius * Math.cos(start);
            const y1 = cy + radius * Math.sin(start);
            const x2 = cx + radius * Math.cos(end);
            const y2 = cy + radius * Math.sin(end);
            const path = `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${large} 1 ${x2} ${y2} Z`;
            return {
                path,
                color: PALETTE[idx % PALETTE.length],
                label: item.label,
                value: item.value,
                percent: ((item.value / total) * 100).toFixed(1),
            };
        });
    }

    barRows(items, valueFormatter) {
        const max = Math.max(1, ...items.map((x) => x.value || 0));
        return items.map((item, idx) => ({
            label: item.label,
            value: item.value,
            valueLabel: valueFormatter ? valueFormatter(item.value) : item.value,
            widthPct: Math.max(2, Math.round((item.value / max) * 100)),
            color: PALETTE[idx % PALETTE.length],
        }));
    }

    refreshNow() {
        this.fetch();
    }

    openEmployees(domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Employees",
            res_model: "hr.employee",
            domain: domain || [],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openHeldPayslips() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Held Payslips",
            res_model: "hr.payslip",
            domain: [["hr_uae_hold_active", "=", true]],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openOpenFlights() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Open Flights",
            res_model: "hr.uae.flight",
            domain: [["booking_state", "in", ["draft", "booked"]]],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openPendingAdjustments() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Adjustments to Approve",
            res_model: "hr.uae.salary.adjustment",
            domain: [["state", "=", "to_approve"]],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openDocsAlerts() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Document Alerts",
            res_model: "hr.uae.document",
            domain: [["expiry_state", "in", ["warning", "expired"]]],
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openEmployee(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.employee",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openLeave(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.leave",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openTermination(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.uae.termination",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

const PALETTE = [
    "var(--hud-chart-1)",
    "var(--hud-chart-2)",
    "var(--hud-chart-3)",
    "var(--hud-chart-4)",
    "var(--hud-chart-5)",
    "var(--hud-chart-6)",
    "var(--hud-chart-7)",
    "var(--hud-chart-8)",
    "var(--hud-chart-9)",
    "var(--hud-chart-10)",
];

registry.category("actions").add("hr_uae_live_dashboard", HrUaeLiveDashboard);

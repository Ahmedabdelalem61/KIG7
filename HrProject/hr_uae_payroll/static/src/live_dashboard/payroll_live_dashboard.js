/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatFloat } from "@web/core/utils/numbers";

const PALETTE = [
    "#0ea5e9",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#ec4899",
    "#14b8a6",
    "#f97316",
    "#22c55e",
    "#6366f1",
    "#06b6d4",
    "#a855f7",
];

export class HrUaePayrollLiveDashboard extends Component {
    static template = "hr_uae_payroll.HrUaePayrollLiveDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            data: null,
            lastRefresh: null,
            error: null,
            monthsBack: 6,
        });

        onWillStart(async () => {
            await this.fetch();
        });
    }

    async fetch() {
        this.state.loading = true;
        this.state.error = null;
        try {
            this.state.data = await this.orm.call(
                "hr.uae.payroll.live.dashboard",
                "fetch_data",
                [{ months_back: this.state.monthsBack }]
            );
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

    refreshNow() {
        this.fetch();
    }

    setRange(months) {
        this.state.monthsBack = months;
        this.fetch();
    }

    // ---------- Chart helpers (pure SVG, no external libs) ----------

    netTrendSvg(items) {
        // Line + area chart of net pay across months
        if (!items.length) {
            return null;
        }
        const W = 640;
        const H = 200;
        const padL = 50;
        const padR = 12;
        const padT = 16;
        const padB = 28;
        const max = Math.max(1, ...items.map((x) => x.net));
        const stepX = (W - padL - padR) / Math.max(1, items.length - 1);
        const points = items.map((it, i) => ({
            x: padL + i * stepX,
            y: padT + (1 - it.net / max) * (H - padT - padB),
            label: it.label,
            net: it.net,
            slips: it.slips,
        }));
        const pathD = points
            .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
            .join(" ");
        const areaD =
            `M ${points[0].x.toFixed(1)} ${(H - padB).toFixed(1)} ` +
            points
                .map((p) => `L ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
                .join(" ") +
            ` L ${points[points.length - 1].x.toFixed(1)} ${(H - padB).toFixed(1)} Z`;

        // Y-axis ticks
        const ticks = [0, 0.5, 1].map((f) => ({
            y: padT + f * (H - padT - padB),
            value: max * (1 - f),
        }));

        return { W, H, padL, padR, padT, padB, points, pathD, areaD, ticks, max };
    }

    barRows(items, valueKey = "value", formatter) {
        const max = Math.max(1, ...items.map((x) => x[valueKey] || 0));
        return items.map((item, idx) => ({
            ...item,
            valueLabel: formatter
                ? formatter(item[valueKey])
                : (item[valueKey] || 0).toLocaleString(),
            widthPct: Math.max(2, Math.round((item[valueKey] / max) * 100)),
            color: PALETTE[idx % PALETTE.length],
        }));
    }

    diverging(items) {
        // For salary rule breakdown: positive earnings vs negative deductions
        const max = Math.max(1, ...items.map((x) => Math.abs(x.value)));
        return items.map((item, idx) => {
            const widthPct = Math.max(2, Math.round((Math.abs(item.value) / max) * 50));
            return {
                ...item,
                widthPct,
                isNeg: item.value < 0,
                valueLabel: this.formatCurrency(item.value),
                color: item.value < 0 ? "#ef4444" : "#10b981",
            };
        });
    }

    // ---------- Drill-down handlers ----------

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

    openAllPayslips() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Payslips",
            res_model: "hr.payslip",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            target: "current",
        });
    }

    openDashboardList() {
        this.action.doAction("hr_uae_payroll.action_hr_uae_payroll_dashboard");
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

    openPayslip(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.payslip",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openAdjustment(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.uae.salary.adjustment",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openProject(projectId) {
        if (!projectId) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.uae.payroll.dashboard",
            domain: [["project_allocation_id", "=", projectId]],
            views: [[false, "list"]],
            target: "current",
        });
    }
}

registry
    .category("actions")
    .add("hr_uae_payroll_live_dashboard", HrUaePayrollLiveDashboard);

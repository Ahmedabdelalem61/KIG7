# Multi-currency contracts — manual test guide (staging server)

A short, click-by-click checklist to confirm the feature works on the live
staging server. No coding needed. Do it as an **HR Manager** user.

- Site: open the staging URL in your browser (e.g. `http://185.196.21.19:8073`)
  and log in.
- Time needed: ~10 minutes.

> The numbers below assume a test rate of **1 USD = 4 AED**. Use any rate you
> like — just keep the “× rate” math in mind when checking results.

---

## Step 0 — Add an exchange rate (required once)

The system has **no exchange rates yet**, so payroll will (correctly) refuse to
convert until you add one.

1. Turn on developer tools: **Settings** → scroll to the bottom → **Activate the
   developer mode**.
2. Go to **Settings → Technical → Currencies** (under the “Currencies” section).
3. Search **USD**, open it, and tick **Active** if it isn’t.
4. Open the **Rates** tab → **Add a line**:
   - **Date:** today.
   - Set the rate so **1 USD = 4 AED**. Odoo shows two helper columns — set
     **“AED per Unit” = 4** (if instead you see **“Unit per AED”**, put **0.25**).
5. Save.

✅ You now have a USD rate. (Repeat later with a different date/rate to test
period changes — Step 4.)

---

## Step 1 — Put a contract in USD

1. Go to **Employees → Contracts** (or open an employee → their contract).
2. Pick a test contract (or create one). On the **Salary Information** tab:
   - Change **Contract Currency** from AED to **USD**.
   - The **Wage** field (and the allowances) are now entered **in USD** — type
     e.g. **1000**. Do the same for any allowance you want to test.
3. Save.

✅ **Expected:** a new **“Converted (AED)”** tab appears showing the company-currency
values **read-only** — Wage ≈ **4,000 AED** (1000 × 4). Only the USD amounts on
Salary Information are editable.

---

## Step 2 — Check the payslip converts the salary

1. Go to **Payroll → Payslips → New**.
2. Pick the **employee** from Step 1, set a **period** (e.g. this month), make sure
   the **Salary Structure** is *UAE Standard*.
3. Click **Compute Sheet**.
4. Look at the **Salary Computation** lines.

✅ **Expected:** **BASIC = 4,000 AED** (1000 USD × 4). Housing/Transport/Other
lines are likewise the USD amount × 4. **Net** adds up in AED.

---

## Step 3 — Confirm it uses the rate of the pay period (the key behaviour)

This proves the rate is taken **fresh at payroll time**, not frozen on the contract.

1. Back in **Currencies → USD → Rates**, add a **second** rate line with a date in
   **next month** and a **different** value — e.g. **1 USD = 5 AED**
   (“AED per Unit” = 5).
2. Create a **new payslip** for the **next month** period and **Compute Sheet**.

✅ **Expected:** the new payslip’s **BASIC = 5,000 AED** (1000 × 5), while last
month’s payslip still shows **4,000 AED**. Each period uses its own rate.

---

## Step 4 — Fail-safe when a rate is missing

1. Create a contract in a currency that has **no rate** (e.g. **EUR**, if you
   haven’t added one).
2. Try to **Compute Sheet** on a payslip for that employee.

✅ **Expected:** a clear pop-up error like *“No exchange rate is defined for EUR
on or before …”*. Nothing is paid at a wrong 1:1 rate.

---

## Step 5 — Flight ticket in another currency

1. Open the employee’s record → make sure **“Deduct Employee-Paid Flight Tickets”**
   is ticked.
2. **Flight Tickets → New:** same employee, **Currency = USD**, **Ticket Price =
   1000**, **Paid By = Paid by Employee**, a **Departure Date** inside the pay
   period, then **Book** it.
3. Re-open that period’s payslip and **Compute Sheet**.

✅ **Expected:** the **Flight deduction** line is about **−4,000 AED** (1000 USD × 4),
not −1000.

---

## Step 6 — Salary adjustment in another currency

1. **Payroll → Salary Adjustments → New:** same employee, **Allowance**, **Amount =
   1000**, **Currency = USD**, **One-shot**, target the period’s payslip.
2. **Submit** → **Approve**.
3. Open the payslip → check the input / recompute.

✅ **Expected:** the adjustment reaches payroll as **4,000 AED** (1000 × 4).

---

## Step 7 — Normal AED contracts are unchanged

1. Open any contract still in **AED** (the default).

✅ **Expected:** it looks and behaves exactly as before — you type the wage in AED,
no extra fields, payslips compute the same numbers as always.

---

## If something looks off

- BASIC is 0 or wrong on a foreign contract → the currency has **no rate for that
  date**. Add it (Step 0) and recompute.
- AED value on the contract shows 0 after picking USD → same cause: add the rate,
  then re-save the contract (or wait for the nightly refresh).
- Need to revert a test contract → set **Contract Currency** back to **AED**.

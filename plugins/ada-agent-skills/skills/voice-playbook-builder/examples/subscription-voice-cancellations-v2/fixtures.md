# Worklist schema and real-shape fixtures

Row: `sid~route~eligibility~pausable~ispaused~name~price~renewaldate~kind~fee`, rows joined by `;`.
- route: OK | GIFT | NORENEW | APP · eligibility (discount): ELIGIBLE | INELIGIBLE · pausable: PAUSABLE | NOPAUSE · ispaused: NOTPAUSED | PAUSED
- kind: BASE | ADDON (the tools add-on is the only add-on) · fee: FEE (billed-monthly installment plans) | NOFEE (never for free trials)
- name fallback: renewalName || orderTitle || orderDescription || 'membership' · price/date 'NA' when blank (common on international plans)
- Menu (for the selection ask): `name: sid (base|add-on); …`
- Built by the lookup action's JMESPath (kept under 1024 chars); includes type Subscription and FreeTrial; NOPAUSE for pay-in-full, free trials, billed-monthly and household plans.

## Fixtures (ids masked)
| name | rows |
|---|---|
| single | `2001~OK~ELIGIBLE~PAUSABLE~NOTPAUSED~Premium Membership~$299.00~2027-03-15~BASE~NOFEE` |
| multi | Premium 2101 · Regional 2102 · Global 2103 (all OK ELIGIBLE PAUSABLE BASE) |
| addon | `2201 Premium BASE` + `2202 Tools Add-on ADDON INELIGIBLE NOPAUSE` |
| multi_addon | Premium 2301 · Global 2302 · Tools Add-on 2303 (ADDON) — the partial-selection handoff case |
| offers_fee | Global 4001 PAUSABLE NOFEE · Regional 4002 NOPAUSE FEE |
| gift_fee_norenew | Premium 9104 OK · Global (Gift) 9101 GIFT · Regional 6 Months 9102 NOPAUSE FEE · Canada Regional 9103 NORENEW |
| mixed_types | Premium · gift · norenew · APP · Tools Add-on |
| real_household_addon | `9617 Tools Add-on 6 Months ADDON PAUSABLE` + `9967 Premium Household Plan 12 Months BASE NOPAUSE FEE` — pause must NOT be offered |
| real_nodate_pausable | Premium Plus, price/date NA |
| real_dup_addon | two identical "Tools Add-on" rows + a Heritage Plus plan — duplicate names |
| real_app_blankname | APP row with blank title → 'membership' fallback |
| already_cancelled | worklist NONE; portfolio pending_cancel_only; pending list `Global Membership ~ 2027-03-03; Tools Add-on ~ 2026-10-04` |
| zombie (found live) | `1001~OK~ELIGIBLE~PAUSABLE~NOTPAUSED~Global Membership 6 Months~$149.00~2015-01-01~BASE~NOFEE` — the billing API says active; preparecancel returns 422 |

Inject in sims through a meta variable; the TEST section copies it into `test_scenario`.

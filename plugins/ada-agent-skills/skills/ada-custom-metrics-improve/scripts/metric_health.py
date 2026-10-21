"""Per-metric health table for one Ada instance's active custom metrics.

Counts pass, fail and null verdicts over a window and flags metrics that cannot be trusted yet.
Read-only. Needs a logged-in adacli session for the instance.

    python3 metric_health.py <instance> --start 2026-10-07 --end 2026-10-21 [--json] [--fails-out DIR]
"""
import argparse, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

ROW_CAP = 10000
MIN_SCORED = 30
RESULTS = ("pass", "fail", "null")


def adacli(inst, *args, tries=4):

    # Parallel reads hit transient ECONNRESET, so retry with backoff.

    for i in range(tries):
        out = subprocess.run(["adacli", inst, *args], capture_output=True, text=True)
        if not out.returncode:
            return out.stdout
        if i < tries - 1:
            time.sleep(2 ** i)
    raise RuntimeError(f"adacli {' '.join(args)} failed: {out.stderr.strip() or out.stdout.strip()}")


def rows_of(payload):
    if isinstance(payload, list):
        return payload
    for k in ("items", "data", "metrics", "results", "custom_metrics"):
        if isinstance(payload.get(k), list):
            return payload[k]
    return []


def active_metrics(inst, run=adacli):
    metrics = rows_of(json.loads(run(inst, "custom-metrics", "list", "--json") or "[]"))
    return [m for m in metrics if str(m.get("state", "active")).lower() == "active"]


def flags(name, counts):
    out = []
    scored = counts["pass"] + counts["fail"]
    total = scored + counts["null"]
    if scored < MIN_SCORED:
        out.append("few scored")
    if total and counts["null"] / total > 0.5:
        out.append("mostly null")
    if scored >= MIN_SCORED and counts["fail"] in (0, scored):
        out.append("no signal")
    if any(counts[r] >= ROW_CAP for r in RESULTS):
        out.append("at row cap")
    if re.match(r"^\s*\d+\s*[.)]", name or ""):
        out.append("numbered name")
    return out


def health(inst, start, end, run=adacli, fails_out=None):
    metrics = active_metrics(inst, run)
    jobs = [(m, r) for m in metrics for r in RESULTS]

    def one(job):
        m, r = job
        mid = m.get("id") or m.get("_id")
        return job, json.loads(run(inst, "custom-metrics", "conversations", mid, "--result", r,
                                   "--start", start, "--end", end, "--json") or "[]")

    counts = {(m.get("id") or m.get("_id")): dict.fromkeys(RESULTS, 0) for m in metrics}
    fails = {}
    with ThreadPoolExecutor(6) as ex:
        for (m, r), payload in ex.map(one, jobs):
            mid = m.get("id") or m.get("_id")
            rows = rows_of(payload)
            counts[mid][r] = len(rows)
            if r == "fail":
                fails[mid] = [x["key"] for x in rows if "key" in x]

    table = []
    for m in metrics:
        mid = m.get("id") or m.get("_id")
        c = counts[mid]
        scored = c["pass"] + c["fail"]
        table.append({"id": mid, "name": m.get("name"), **c, "scored": scored,
                      "fail_rate": round(c["fail"] / scored, 3) if scored else None,
                      "flags": flags(m.get("name"), c)})
    table.sort(key=lambda t: t["fail"], reverse=True)

    if fails_out:
        os.makedirs(fails_out, exist_ok=True)
        for t in table:
            with open(os.path.join(fails_out, f"{t['id']}.json"), "w") as f:
                json.dump({"name": t["name"], "fail_conversation_ids": fails.get(t["id"], [])}, f, indent=1)
    return table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fails-out", help="directory to write one file of failing conversation IDs per metric")
    a = ap.parse_args()
    try:
        table = health(a.instance, a.start, a.end, fails_out=a.fails_out)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        print("A 403 means custom-metrics-mvp is off. An auth error means log in first "
              "(docs/guides/adacli-operational-notes.md).", file=sys.stderr)
        sys.exit(1)
    if a.json:
        print(json.dumps(table, indent=1))
        return
    print(f"{a.instance}  {a.start} to {a.end}  ({len(table)} active metrics)\n")
    print(f"{'metric':40} {'pass':>6} {'fail':>6} {'null':>6} {'fail%':>6}  flags")
    for t in table:
        pct = "-" if t["fail_rate"] is None else f"{t['fail_rate'] * 100:.0f}%"
        print(f"{(t['name'] or t['id'])[:40]:40} {t['pass']:>6} {t['fail']:>6} {t['null']:>6} {pct:>6}  {', '.join(t['flags'])}")


if __name__ == "__main__":
    main()

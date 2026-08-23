"""STX-002 runner: 7 treatments x 15 hard worlds. Reproducible. Logged."""
import json, os, re, time, sys
sys.path.insert(0, "/root/cogym/evolution_lab")
os.environ["OPENCODE_GO_API_KEY"] = "sk-fv9GAkxq7nRiVTX0l8gLEUoPc79spJGqU9HkSjswVLnoQfTuWz5HY1R8hA44g8ZU"

from cogym.hermes_adapter import make_treatments, run_subject

EXDIR = "/root/cogym/experiments/stx-002"
worlds = json.load(open(f"{EXDIR}/worlds.json"))
materials = f"{EXDIR}/materials"
probe_template = open("/root/cogym/experiments/stx-001/probe.md").read()  # format reference only

treatments = make_treatments("stx002", materials)
log_dir = "/root/cogym/logs/stx-002"
os.makedirs(log_dir, exist_ok=True)

results = {}
start = time.time()

for ti, spec in enumerate(treatments):
    tr_results = []
    print(f"\n[{spec.treatment}] ({ti+1}/7)", flush=True)
    for wi, w in enumerate(worlds):
        task = w["prompt"] + '\n\nAnswer with JSON only: {"choice":"A or B","confidence":0.X}'
        r = run_subject(spec, task, timeout=300, log_dir=log_dir)
        
        chosen, conf = "?", None
        try:
            m = re.search(r'\{[^}]+\}', r["output"])
            j = json.loads(m.group(0))
            chosen = j.get("choice", "?")
            conf = j.get("confidence")
        except: pass
        
        correct = (chosen == w["oracle"])
        tr_results.append({
            "world_family": w["family"], "world_seed": w["seed"],
            "oracle": w["oracle"], "chosen": chosen,
            "correct": correct, "confidence": conf,
            "exit_code": r["exit"], "duration_s": r["duration_s"],
        })
        status = "✓" if correct else "✗"
        print(f"  w{wi+1} [{w['family'][:12]}] {status} chose={chosen} oracle={w['oracle']}", flush=True)
    
    acc = sum(1 for x in tr_results if x["correct"]) / len(tr_results)
    results[spec.treatment] = {"accuracy": round(acc, 3), "runs": tr_results}
    print(f"  accuracy: {acc:.1%}", flush=True)

# Summary
elapsed = time.time() - start
print(f"\n{'='*50}")
print(f"STX-002 COMPLETE | {elapsed:.0f}s | {len(treatments)} treatments x {len(worlds)} worlds")
print(f"{'Treatment':<12} {'Accuracy':>8} {'vs Control':>10}")
control_acc = results.get("control", {}).get("accuracy", 0)
for t in ["live","checkpoint","pack","teaching","primer","summary","control"]:
    if t in results:
        a = results[t]["accuracy"]
        delta = a - control_acc
        marker = " ←" if delta > 0 and t != "control" else ""
        print(f"{t:<12} {a:>7.1%} {delta:>+9.1%}{marker}")

json.dump(results, open(f"{EXDIR}/outputs/results.json","w"), indent=1)

# Per-family breakdown
print("\nPer-family accuracy:")
families = sorted(set(w["family"] for w in worlds))
header = f"{'Treatment':<12}" + "".join(f" {f[:12]:>13}" for f in families)
print(header)
for t in ["live","checkpoint","pack","teaching","primer","summary","control"]:
    if t not in results: continue
    row = f"{t:<12}"
    for fam in families:
        fam_runs = [r for r in results[t]["runs"] if r["world_family"]==fam]
        acc = sum(1 for r in fam_runs if r["correct"])/len(fam_runs) if fam_runs else 0
        row += f" {acc:>12.0%}"
    print(row)

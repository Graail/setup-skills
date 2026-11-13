#!/usr/bin/env python3
"""Helper for the local model served by Strata (OpenAI-compatible API). Stdlib only.

Env: LOCAL_URL (default http://127.0.0.1:8080), LOCAL_MODEL (Strata ignores the name),
LOCAL_API_KEY (only if Strata has an api_key), LOCAL_CONTEXT (fallback context size).

Commands
  probe                      context length, load state, measured speed
  estimate FILES... [--out N] [--per-item]
                             token projection: fits? how many calls? how long?
  run --prompt P [--input F...] [--out O] [--check CMD] [--json]
                             one stateless call; optional check; retries once
  map --template T --items ITEMS.jsonl --out OUT.jsonl [--check-key K...]
                             one call per item (best for bulk work: no context growth)
  chat --session S --prompt P
                             multi-turn session with auto-compaction near the limit

Auto-compaction (chat): before each call the session's token count is
estimated. Over COMPACT_AT (default 60% of num_ctx) the oldest turns are
summarized by the model into one short "state" message and dropped; the last
KEEP_TURNS turns stay verbatim. The summary is saved in the session file.
"""
import argparse, json, os, subprocess, sys, time, urllib.request

HOST = os.environ.get("LOCAL_URL", "http://127.0.0.1:8080").rstrip("/")
MODEL = os.environ.get("LOCAL_MODEL", "strata")
API_KEY = os.environ.get("LOCAL_API_KEY", "")
CHARS_PER_TOKEN = 3.5          # conservative for code/JSON
COMPACT_AT = float(os.environ.get("LOCAL_COMPACT_AT", "0.60"))  # share of num_ctx that triggers compaction
KEEP_TURNS = 4
SESS_DIR = os.path.join(os.environ.get("TEMP", "/tmp"), "local-sessions")


def http(path, body=None, timeout=1800):
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = "Bearer " + API_KEY
    req = urllib.request.Request(HOST + path, data=None if body is None else json.dumps(body).encode(),
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _find_ctx(obj):
    """First context-size field found in a /props or /v1/models answer."""
    if isinstance(obj, dict):
        for k in ("n_ctx", "context_length", "max_context", "context_window", "max_model_len"):
            if isinstance(obj.get(k), int) and obj[k] > 0:
                return obj[k]
        for v in obj.values():
            n = _find_ctx(v)
            if n:
                return n
    elif isinstance(obj, list):
        for v in obj:
            n = _find_ctx(v)
            if n:
                return n
    return 0


def num_ctx():
    for path in ("/props", "/v1/models"):
        try:
            n = _find_ctx(http(path, timeout=10))
            if n:
                return n
        except Exception:
            pass
    return int(os.environ.get("LOCAL_CONTEXT", "65536"))


def toks(text):
    return int(len(text) / CHARS_PER_TOKEN) + 1


def chat_call(messages, think="low", fmt=None):
    body = {"model": MODEL, "messages": messages, "stream": False, "temperature": 0.2,
            "reasoning_effort": think}
    if fmt == "json":
        body["response_format"] = {"type": "json_object"}
    t = time.time()
    r = http("/v1/chat/completions", body)
    # same shape the rest of the script reads: d["message"]["content"]
    return {"message": {"content": r["choices"][0]["message"].get("content") or ""},
            "usage": r.get("usage", {}), "_wall": time.time() - t}


def stats(d):
    u = d.get("usage", {})
    pe, ev = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
    return f"in={pe} out={ev} ~{ev/max(d['_wall'], 0.001):.0f} tok/s (wall, incl. prompt) wall={d['_wall']:.1f}s"


def run_check(cmd, path):
    if not cmd:
        return True, ""
    p = subprocess.run(cmd.replace("{out}", path), shell=True, capture_output=True, text=True)
    return p.returncode == 0, (p.stdout + p.stderr)[-1500:]


# ---------------------------------------------------------------- commands
def cmd_probe(a):
    n = num_ctx()
    d = chat_call([{"role": "user", "content": "Count from 1 to 40, comma separated."}])
    print(f"model={MODEL} num_ctx={n}  {stats(d)}")


def cmd_estimate(a):
    n = num_ctx()
    sizes = [(f, toks(open(f, encoding="utf-8", errors="replace").read())) for f in a.files]
    total = sum(s for _, s in sizes)
    overhead = 600 + a.out
    budget = int(n * COMPACT_AT)
    print(f"num_ctx={n}  safe budget per call={budget}")
    for f, s in sizes:
        print(f"  {s:>7} tok  {f}")
    if a.per_item:
        worst = max(s for _, s in sizes) + overhead
        print(f"per-item calls={len(sizes)}  worst call={worst} tok  fits={worst <= budget}")
        calls = len(sizes)
    else:
        calls = max(1, -(-(total + overhead) // budget))
        print(f"total={total + overhead} tok  calls needed={calls}")
    # speed is left out on purpose: the decision is Claude's token cost only (SKILL.md, section 1)
    print(f"Claude cost if done directly: read ~{total} + write ~{a.out * calls} tokens")


def one(prompt, inputs, think, fmt):
    content = prompt
    for f in inputs or []:
        content += f"\n\n=== FILE {f} ===\n" + open(f, encoding="utf-8", errors="replace").read()
    n = num_ctx()
    if toks(content) > n * COMPACT_AT:
        sys.exit(f"ERROR: input ~{toks(content)} tok > safe budget {int(n*COMPACT_AT)}. Split the task.")
    return chat_call([{"role": "user", "content": content}], think, fmt)


def cmd_run(a):
    prompt = open(a.prompt, encoding="utf-8").read() if os.path.exists(a.prompt) else a.prompt
    for attempt in (1, 2):
        d = one(prompt, a.input, a.think, "json" if a.json else None)
        out = d["message"]["content"]
        if a.out:
            open(a.out, "w", encoding="utf-8").write(out)
        ok, log = run_check(a.check, a.out or "")
        print(f"attempt {attempt}: {stats(d)} check={'OK' if ok else 'FAIL'}", file=sys.stderr)
        if ok:
            if not a.out:
                print(out)
            return
        prompt += f"\n\nYour previous answer failed this check:\n{log}\nFix it."
    sys.exit("FAILED twice: do it yourself (protocol rule).")


def cmd_map(a):
    tpl = open(a.template, encoding="utf-8").read()
    items = [json.loads(l) for l in open(a.items, encoding="utf-8") if l.strip()]
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["_id"] for l in open(a.out, encoding="utf-8") if l.strip()}
    fails = []
    with open(a.out, "a", encoding="utf-8") as fo:
        for i, it in enumerate(items):
            iid = it.get("_id", str(i))
            if iid in done:
                continue
            res = None
            for attempt in (1, 2):
                d = one(tpl.replace("{item}", json.dumps(it, ensure_ascii=False)), [], a.think, "json")
                try:
                    res = json.loads(d["message"]["content"])
                    missing = [k for k in a.check_key or [] if k not in res]
                    if missing:
                        raise ValueError(f"missing {missing}")
                    break
                except Exception as e:
                    res = None
                    err = str(e)
            if res is None:
                fails.append((iid, err))
                continue
            res["_id"] = iid
            fo.write(json.dumps(res, ensure_ascii=False) + "\n")
            fo.flush()
            print(f"[{i+1}/{len(items)}] {iid}: {stats(d)}", file=sys.stderr)
    print(f"done; failed={len(fails)}")
    for f in fails:
        print("FAIL", *f)


def compact(sess, n):
    msgs = sess["messages"]
    size = sum(toks(m["content"]) for m in msgs) + toks(sess.get("summary", ""))
    if size < n * COMPACT_AT or len(msgs) <= KEEP_TURNS * 2:
        return
    old, keep = msgs[:-KEEP_TURNS * 2], msgs[-KEEP_TURNS * 2:]
    text = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    d = chat_call([{"role": "user", "content":
                    "Summarize this conversation as a compact state for continuing the work. Keep: decisions, "
                    "exact names/ids/paths, open items, results. Drop chit-chat. Max 400 words.\n\n"
                    f"Previous summary:\n{sess.get('summary','')}\n\nConversation:\n{text}"}])
    sess["summary"] = d["message"]["content"]
    sess["messages"] = keep
    print(f"[compacted {len(old)} messages, ~{size} tok -> ~{toks(sess['summary']) + sum(toks(m['content']) for m in keep)}]",
          file=sys.stderr)


def cmd_chat(a):
    os.makedirs(SESS_DIR, exist_ok=True)
    path = os.path.join(SESS_DIR, a.session + ".json")
    sess = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"summary": "", "messages": []}
    prompt = open(a.prompt, encoding="utf-8").read() if os.path.exists(a.prompt) else a.prompt
    sess["messages"].append({"role": "user", "content": prompt})
    compact(sess, num_ctx())
    msgs = ([{"role": "system", "content": "State so far:\n" + sess["summary"]}] if sess["summary"] else []) + sess["messages"]
    d = chat_call(msgs, a.think)
    sess["messages"].append({"role": "assistant", "content": d["message"]["content"]})
    json.dump(sess, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(d["message"]["content"])
    print(f"[{stats(d)}  session={path}]", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("probe")
    e = s.add_parser("estimate"); e.add_argument("files", nargs="+"); e.add_argument("--out", type=int, default=1000)
    e.add_argument("--per-item", action="store_true")
    r = s.add_parser("run"); r.add_argument("--prompt", required=True); r.add_argument("--input", nargs="*")
    r.add_argument("--out"); r.add_argument("--check"); r.add_argument("--json", action="store_true")
    r.add_argument("--think", default="low")
    m = s.add_parser("map"); m.add_argument("--template", required=True); m.add_argument("--items", required=True)
    m.add_argument("--out", required=True); m.add_argument("--check-key", nargs="*"); m.add_argument("--think", default="low")
    c = s.add_parser("chat"); c.add_argument("--session", required=True); c.add_argument("--prompt", required=True)
    c.add_argument("--think", default="low")
    a = p.parse_args()
    {"probe": cmd_probe, "estimate": cmd_estimate, "run": cmd_run, "map": cmd_map, "chat": cmd_chat}[a.cmd](a)


if __name__ == "__main__":
    main()

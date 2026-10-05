#!/usr/bin/env python3
"""醒脑选主题：确定性实现轮换/mute/去重逻辑。

TOPICS.md -> 按模块 1>2>3>4>5>6>1 轮换，从 sent_log 最后一个主题的下一个模块起，
取第一个"未发送（30 天内）且不在 muted 列表"的主题。mute 优先级高于轮换。
第二轮（30 天内全发过）放宽日期限制，标记 second_round=true（由模型换切入角度）。

用法:
  next-topic.py --topics PATH --sent-log PATH --prefs PATH [--date YYYY-MM-DD]
输出 JSON 到 stdout，exit 0=选中，1=无可用主题。
"""
import argparse, json, re, sys
from datetime import date, timedelta

def canon_module(s):
    """模块名归一化 -> (num or None, key)。"""
    s = (s or "").strip()
    m = re.search(r"(\d+)", s)
    num = int(m.group(1)) if m else None
    key = re.sub(r"^模块?\d*\s*[:：]?\s*", "", s)
    key = re.sub(r"\s*\(.*$", "", key).strip()
    return num, key

def topic_key(title):
    return re.split(r"[:：]", title, 1)[0].strip()

def parse_topics(path):
    mods = []  # [(num, name, [(title, source)])]
    cur = None
    for raw in open(path, encoding="utf-8").read().splitlines():
        line = raw.strip().strip("\\")
        mh = re.match(r"##\s*模块\s*(\d+)\s*[:：]\s*(.+)", line)
        if mh:
            cur = (int(mh.group(1)), mh.group(2).strip(), [])
            mods.append(cur)
            continue
        mt = re.match(r"(\d+)\.\s*(.+)", line)
        if mt and cur is not None:
            body = mt.group(2).strip().strip("\\").strip('"')
            if "｜" in body:
                title, source = body.rsplit("｜", 1)
            elif "|" in body:
                title, source = body.rsplit("|", 1)
            else:
                title, source = body, ""
            cur[2].append((title.strip(), source.strip()))
    return sorted(mods, key=lambda m: m[0])

def load_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except OSError:
        return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics", required=True)
    ap.add_argument("--sent-log", required=True)
    ap.add_argument("--prefs", required=True)
    ap.add_argument("--date", default=None)
    a = ap.parse_args()
    today = date.fromisoformat(a.date) if a.date else date.today()

    mods = parse_topics(a.topics)
    if not mods:
        print(json.dumps({"error": "TOPICS.md 解析为空"}, ensure_ascii=False)); return 1
    mod_by_num = {m[0]: m for m in mods}
    name2num = {}
    for num, name, _ in mods:
        _, key = canon_module(name)
        name2num[key] = num
        name2num[str(num)] = num

    sent = load_json(a.sent_log, [])
    prefs = load_json(a.prefs, {})
    muted_mods = set()
    for m in prefs.get("muted_modules", []):
        num, key = canon_module(m)
        muted_mods.add(num if num else key)
    muted_topics = set(prefs.get("muted_topics", []))

    # 近 30 天发过的主题 key
    cutoff = today - timedelta(days=30)
    recent_topics = set()
    dated = []
    for e in sent:
        try:
            d = date.fromisoformat(e.get("date", ""))
            dated.append(d)
        except ValueError:
            continue
        if d >= cutoff and e.get("topic"):
            recent_topics.add(topic_key(e["topic"]))
    if not dated and sent:  # 无合法日期时退化为近 30 条
        for e in sent[-30:]:
            if e.get("topic"):
                recent_topics.add(topic_key(e["topic"]))

    # 起始模块：最后一个已发送主题的下一个
    start = 1
    if sent:
        last = sent[-1].get("module", "")
        num, key = canon_module(last)
        if num in mod_by_num:
            start = num % 6 + 1
        elif key in name2num:
            start = name2num[key] % 6 + 1

    def muted(mod_num, mod_name, title):
        _, key = canon_module(mod_name)
        if mod_num in muted_mods or key in muted_mods or mod_name in muted_mods:
            return True
        tk = topic_key(title)
        return any(mt == tk or mt in title for mt in muted_topics)

    order = [(start + i - 1) % 6 + 1 for i in range(6)]
    # 第一遍：严格（30 天去重）；第二遍：放宽日期（mute 仍生效）
    for strict in (True, False):
        for mn in order:
            if mn not in mod_by_num:
                continue
            _, mname, topics = mod_by_num[mn]
            for idx, (title, source) in enumerate(topics, 1):
                if muted(mn, mname, title):
                    continue
                if strict and topic_key(title) in recent_topics:
                    continue
                print(json.dumps({
                    "module_num": mn, "module": canon_module(mname)[1],
                    "topic": topic_key(title), "topic_full": title,
                    "source": source, "topic_index": idx,
                    "second_round": not strict,
                }, ensure_ascii=False))
                return 0
    print(json.dumps({"error": "无可用主题（可能全被 mute）"}, ensure_ascii=False))
    return 1

if __name__ == "__main__":
    sys.exit(main())

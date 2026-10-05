#!/usr/bin/env python3
"""醒脑北极星仪表：从 sent_log + reply_log 计算回复率 / 回来率。

回复率 = 有实质回复的推送日 / 推送日（窗口内）
回来率 = 昨日回复者今日又回复的比例（昨日有回复的日子中，今日也有回复的占比）

用法: metrics.py --sent-log PATH --reply-log PATH [--days N]
输出 JSON + 一行人话摘要。
"""
import argparse, json, sys
from datetime import date, timedelta

def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except OSError:
        return []

def dates(entries):
    out = set()
    for e in entries:
        try:
            out.add(date.fromisoformat(e.get("date", "")))
        except ValueError:
            pass
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sent-log", required=True)
    ap.add_argument("--reply-log", required=True)
    ap.add_argument("--days", type=int, default=30)
    a = ap.parse_args()
    today = date.today()
    start = today - timedelta(days=a.days - 1)

    sent = {d for d in dates(load(a.sent_log)) if start <= d <= today}
    repl = {d for d in dates(load(a.reply_log)) if start <= d <= today}

    replied_sent_days = sent & repl
    reply_rate = len(replied_sent_days) / len(sent) if sent else None

    eligible = sorted(d for d in repl if d < today)
    returned = sum(1 for d in eligible if d + timedelta(days=1) in repl)
    return_rate = returned / len(eligible) if eligible else None

    # 当前连击（截至昨天或今天）
    streak = 0
    d = today if today in repl else today - timedelta(days=1)
    while d in repl:
        streak += 1
        d -= timedelta(days=1)

    res = {
        "window_days": a.days, "push_days": len(sent),
        "reply_days": len(replied_sent_days),
        "reply_rate": round(reply_rate, 3) if reply_rate is not None else None,
        "return_rate": round(return_rate, 3) if return_rate is not None else None,
        "current_streak_days": streak,
    }
    print(json.dumps(res, ensure_ascii=False))
    rr = "n/a" if res["reply_rate"] is None else f"{res['reply_rate']*100:.1f}%"
    rt = "n/a" if res["return_rate"] is None else f"{res['return_rate']*100:.1f}%"
    print(f"近{a.days}天：推送{len(sent)}天，有回复{len(replied_sent_days)}天，回复率{rr}，回来率{rt}，当前连击{streak}天。")

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""醒脑 Beat 1（小叙事＋钩子）确定性校验。

把能变成代码的约束变成代码，prompt 只管变不成代码的东西。
变不成代码的（机制未剧透、叙事质量、不说教）仍由模型按 SKILL.md 四检自查。

用法:
  qc-beat1.py --text-file PATH --topic TOPIC --module MODULE --scene SCENE_ID \
               --prefs ~/.xingnao/user_prefs.json --sent-log ~/.xingnao/sent_log.json

检查项（全部确定性）:
  1. 字数：正文（去署名行、去空白）120-180 字
  2. 署名行存在："——醒脑" 必须出现
  3. 钩子启发式：正文含 回/想知道/为什么/?/？ 之一（启发式，钩子质量仍由模型把关）
  4. mute：topic 不在 muted_topics，module 不在 muted_modules
  5. 去重：scene 不在 sent_log 近 30 条的 scene 中

输出 JSON 到 stdout，exit 0=通过，1=不通过。
"""
import argparse
import json
import re
import sys

SIG_MARK = "——醒脑"
HOOK_HINTS = ("回我", "想知道", "为什么", "?", "？")
MIN_CHARS, MAX_CHARS = 120, 180


def body_text(text):
    lines = [ln for ln in text.splitlines() if SIG_MARK not in ln]
    return re.sub(r"\s+", "", "".join(lines))


def finish(ok, failures, details):
    print(json.dumps({"pass": ok, "failures": failures, "details": details},
                     ensure_ascii=False))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--prefs", required=True)
    ap.add_argument("--sent-log", required=True)
    a = ap.parse_args()

    failures, details = [], {}
    try:
        text = open(a.text_file, encoding="utf-8").read()
    except OSError as e:
        return finish(False, ["读文本失败: %s" % e], {})

    n = len(body_text(text))
    details["chars"] = n
    if not (MIN_CHARS <= n <= MAX_CHARS):
        failures.append("字数 %d 超出 %d-%d" % (n, MIN_CHARS, MAX_CHARS))

    details["has_signature"] = SIG_MARK in text
    if not details["has_signature"]:
        failures.append("缺少署名行")

    details["hook_hint"] = any(h in body_text(text) for h in HOOK_HINTS)
    if not details["hook_hint"]:
        failures.append("未检测到钩子痕迹")

    try:
        prefs = json.load(open(a.prefs, encoding="utf-8"))
    except OSError:
        prefs = {}
    if a.topic in set(prefs.get("muted_topics", [])):
        failures.append("主题被 mute: %s" % a.topic)
    if a.module in set(prefs.get("muted_modules", [])):
        failures.append("模块被 mute: %s" % a.module)

    try:
        log = json.load(open(a.sent_log, encoding="utf-8"))
    except OSError:
        log = []
    recent = {e.get("scene") for e in log[-30:] if e.get("scene")}
    details["recent_scenes"] = len(recent)
    if a.scene in recent:
        failures.append("场景 30 天内重复: %s" % a.scene)

    return finish(not failures, failures, details)


if __name__ == "__main__":
    sys.exit(main())

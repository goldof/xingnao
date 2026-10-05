#!/usr/bin/env python3
"""醒脑 Beat 2（科学解释）确定性校验。

硬门槛（fail）: 字数 200-300（去署名行、去空白）、署名行存在。
软提醒（warning，不判 fail）: 未检测到年份（出处弱）、未检测到边界条件词。
变不成代码的（讲透、案例真实、不说教）仍由模型自查。

用法: qc-beat2.py --text-file PATH
"""
import argparse, json, re, sys

SIG_MARK = "——醒脑"
MIN_CHARS, MAX_CHARS = 200, 300
BOUNDARY_HINTS = ("不适用", "避免", "注意", "边界", "别", "不要", "仅当", "如果")

def body(t):
    return re.sub(r"\s+", "", "".join(
        ln for ln in t.splitlines() if SIG_MARK not in ln))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", required=True)
    a = ap.parse_args()
    try:
        text = open(a.text_file, encoding="utf-8").read()
    except OSError as e:
        print(json.dumps({"pass": False, "failures": ["读文本失败: %s" % e],
                          "warnings": []}, ensure_ascii=False))
        return 1
    b, failures, warnings = body(text), [], []
    n = len(b)
    if not (MIN_CHARS <= n <= MAX_CHARS):
        failures.append("字数 %d 超出 %d-%d" % (n, MIN_CHARS, MAX_CHARS))
    if SIG_MARK not in text:
        failures.append("缺少署名行")
    if not re.search(r"(19|20)\d{2}", b):
        warnings.append("未检测到年份，出处可能弱")
    if not any(w in b for w in BOUNDARY_HINTS):
        warnings.append("未检测到边界条件词，行动点可能缺边界")
    print(json.dumps({"pass": not failures, "failures": failures,
                      "warnings": warnings,
                      "details": {"chars": n}}, ensure_ascii=False))
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())

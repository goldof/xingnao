#!/usr/bin/env python3
"""醒脑环境探针：只探测可验证的，诚实声明探测不到的。

可验证:
  persistence: 尝试写 ~/.xingnao/ -> local；写失败 -> ephemeral
  svg_renderer: 检查 chromium / rsvg-convert 二进制是否存在
不可验证（由调用方声明）:
  image: native 需宿主声明（--image native），否则沿用旧档案，无旧档案时按
         renderer 推断（有 renderer -> svg，否则 none）

用法: env-probe.py [--profile PATH] [--image {native,svg,none}] [--home PATH]
"""
import argparse, json, os, shutil, sys
from datetime import datetime, timezone

RENDERERS = [
    ("chromium", ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]),
    ("rsvg", ["rsvg-convert"]),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=os.path.expanduser("~/.xingnao/env_profile.json"))
    ap.add_argument("--image", choices=["native", "svg", "none"], default=None)
    ap.add_argument("--home", default=os.path.expanduser("~/.xingnao"))
    a = ap.parse_args()

    try:
        old = json.load(open(a.profile, encoding="utf-8"))
    except OSError:
        old = {}

    # persistence：真写测试
    persistence = "ephemeral"
    try:
        os.makedirs(a.home, exist_ok=True)
        tp = os.path.join(a.home, ".probe_write_test")
        open(tp, "w").write("ok")
        os.remove(tp)
        persistence = "local"
    except OSError:
        pass

    # svg_renderer：真查二进制
    renderer = "none"
    for name, bins in RENDERERS:
        if any(shutil.which(b) for b in bins):
            renderer = name
            break

    # image：声明优先，其次沿用旧值，最后按 renderer 推断
    if a.image:
        image = a.image
    elif old.get("image") in ("native", "svg", "none"):
        image = old["image"]
    else:
        image = "svg" if renderer != "none" else "none"

    prof = {
        "_note": "宿主能力档案：每次晨间任务开始时由探针重写。image 由宿主声明（native 需 --image 显式传入），renderer/persistence 为实测。",
        "image": image, "svg_renderer": renderer, "persistence": persistence,
        "probed_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        json.dump(prof, open(a.profile, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    except OSError as e:
        print(json.dumps({"error": "写档案失败: %s" % e}, ensure_ascii=False))
        return 1
    print(json.dumps(prof, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())

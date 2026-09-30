#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用：提交 API 工作流到 ComfyUI 桥接（8199），等待完成并收图。
用法: python3 submit_prompt.py <workflow.json> <output_png_dst>
"""
import json
import os
import shutil
import sys
import time
import urllib.request

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

BRIDGE = "http://127.0.0.1:8199"
COMFY_OUT = "/mnt/d/minimax-h3-demo/ComfyUI/output"


def main():
    wf_path, dst = sys.argv[1], sys.argv[2]
    wf = json.load(open(wf_path))
    body = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(BRIDGE + "/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]
    print("submitted:", pid, flush=True)

    t0 = time.time()
    while time.time() - t0 < 600:
        with urllib.request.urlopen(f"{BRIDGE}/history/{pid}", timeout=30) as r:
            h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                print(f"done in {time.time()-t0:.1f}s  status_str={st.get('status_str')}", flush=True)
                if st.get("status_str") == "error":
                    print(json.dumps(h[pid].get("status"), ensure_ascii=False)[:800], flush=True)
                for node_out in h[pid].get("outputs", {}).values():
                    for img in node_out.get("images", []):
                        src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
                        shutil.copy(src, dst)
                        print("saved ->", dst, flush=True)
                return
        time.sleep(3)
    print("TIMEOUT", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()

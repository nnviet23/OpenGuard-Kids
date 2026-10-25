"""Đo độ trễ lan truyền chính sách và lệnh khẩn (M4/F4) trên server đang chạy.

    python measure_propagation.py --server http://127.0.0.1:8000/api/v1 --email parent@example.com --password OpenGuard@2026 --n 30

Mỗi lượt: (a) phụ huynh đổi hạn mức → đo thời gian tới khi heartbeat của thiết bị mô phỏng thấy phiên bản mới;
(b) phụ huynh bấm “Khóa ngay” → đo thời gian lệnh tới được thiết bị qua WebSocket. Mục tiêu đề bài: (a) ≤ 60 s, (b) ≤ 5 s.
Thiết bị mô phỏng được ghép cặp thật bằng mã 8 ký tự (không phải máy Windows – để đo máy thật hãy chạy agent thật
và ghi thời điểm khóa bằng đồng hồ/quay màn hình).
"""
import argparse
import asyncio
import json
import statistics as st
import time

import httpx
import websockets


def stats(label, xs):
    xs = sorted(xs)
    p95 = xs[min(len(xs) - 1, int(round(0.95 * (len(xs) - 1))))]
    print(f"{label}: n={len(xs)} min={xs[0]:.3f}s mean={st.mean(xs):.3f}s median={st.median(xs):.3f}s p95={p95:.3f}s max={xs[-1]:.3f}s")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8000/api/v1")
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--n", type=int, default=30)
    a = ap.parse_args()
    http = httpx.Client(base_url=a.server, timeout=10)
    r = http.post("/auth/login", json={"email": a.email, "password": a.password})
    r.raise_for_status()
    hdr = {"X-CSRF-Token": r.json()["csrf_token"]}
    child = http.post("/children", json={"name": "Đo độ trễ", "age_group": "6-11"}, headers=hdr).json()["id"]
    code = http.post(f"/children/{child}/enroll-code", json={"parent_consent": True, "child_informed": True}, headers=hdr).json()["code"]
    dev = httpx.Client(base_url=a.server, timeout=10)
    e = dev.post("/agent/enroll", json={"code": code, "device_name": "Máy đo độ trễ"}).json()
    dh = {"Authorization": f"Bearer {e['access_token']}"}
    policy_lat, ws_lat = [], []
    try:
        for i in range(a.n):
            v0 = dev.post("/agent/heartbeat", json={}, headers=dh).json()["policy"]["policy_version"]
            t0 = time.perf_counter()
            http.put(f"/children/{child}/policy", json={"weekday_limit_minutes": 60 + i}, headers=hdr).raise_for_status()
            while dev.post("/agent/heartbeat", json={}, headers=dh).json()["policy"]["policy_version"] == v0:
                await asyncio.sleep(0.2)
            policy_lat.append(time.perf_counter() - t0)
        wsurl = a.server.replace("http", "ws", 1) + "/agent/ws"
        async with websockets.connect(wsurl) as ws:
            await ws.send(json.dumps({"token": e["access_token"]}))
            await ws.recv()  # hello
            for i in range(a.n):
                t0 = time.perf_counter()
                http.post(f"/children/{child}/lock", json={"lock": i % 2 == 0}, headers=hdr).raise_for_status()
                while True:
                    m = json.loads(await asyncio.wait_for(ws.recv(), 10))
                    if m.get("type") == "command":
                        break
                ws_lat.append(time.perf_counter() - t0)
                await ws.send(json.dumps({"ack": m["id"]}))
    finally:
        http.delete(f"/devices/{e['device_id']}", headers=hdr)
        http.delete(f"/children/{child}", headers=hdr)
    stats("Lan truyền chính sách qua heartbeat (poll 0.2 s; thực tế agent poll mỗi 60 s ⇒ trần ≈ 60 s + giá trị này)", policy_lat)
    stats("Lệnh khóa khẩn qua WebSocket (từ lúc bấm đến lúc agent nhận)", ws_lat)


asyncio.run(main())

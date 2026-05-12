#!/usr/bin/env python3
import argparse
import csv
import json
import re
import subprocess
import sys
from typing import Any, Dict, List, Tuple

def run_curl(ip: str, user: str, password: str, payload: str) -> Dict[str, Any]:
    url = f"http://{ip}/ISAPI/AccessControl/AcsEvent?format=json"
    cmd = [
        "curl", "-sS", "--digest",
        "-u", f"{user}:{password}",
        "-H", "Content-Type: application/json",
        "-X", "POST", url,
        "--data-binary", payload,
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed ({p.returncode}): {p.stderr.strip()}")
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Response is not valid JSON: {e}\nRaw:\n{p.stdout[:5000]}")

def extract_info_list(resp: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
    # Ошибки устройства часто приходят в корне (statusString/errMsg)
    if resp.get("statusString") and resp.get("statusString") not in ("OK", "Success"):
        raise RuntimeError(f'Device error: {resp.get("statusString")} / {resp.get("subStatusCode")} / {resp.get("errorMsg")}')

    acs = resp.get("AcsEvent") or resp.get("AcsEventRsp") or resp.get("AcsEventResp") or {}
    info = acs.get("InfoList") or []
    status = acs.get("responseStatusStrg") or ""
    return info, status

def pick(ev: Dict[str, Any], keys: List[str]) -> str:
    for k in keys:
        v = ev.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s != "":
            return s
    return ""

def is_card_event(ev: Dict[str, Any]) -> bool:
    verify = pick(ev, ["currentVerifyMode", "verifyMode", "authMode", "authenticationMode"])
    cardno = pick(ev, ["cardNo", "cardNumber", "cardNoString"])
    reader = pick(ev, ["cardReaderNo", "readerNo"])
    # Эвристика: либо явно "card" в способе верификации, либо есть cardNo/readerNo
    if re.search(r"card", verify, re.IGNORECASE):
        return True
    if cardno or reader:
        return True
    return False

def event_to_row(ev: Dict[str, Any]) -> Dict[str, str]:
    return {
        "time": pick(ev, ["time", "dateTime", "createTime", "occurTime"]),
        "employeeNo": pick(ev, ["employeeNoString", "employeeNo", "personId", "personID"]),
        "name": pick(ev, ["name", "personName", "employeeName"]),
        "cardNo": pick(ev, ["cardNo", "cardNumber", "cardNoString"]),
        "verifyMode": pick(ev, ["currentVerifyMode", "verifyMode", "authMode", "authenticationMode"]),
        "doorNo": pick(ev, ["doorNo", "doorNumber"]),
        "readerNo": pick(ev, ["cardReaderNo", "readerNo"]),
        "major": pick(ev, ["major"]),
        "minor": pick(ev, ["minor"]),
        "result": pick(ev, ["status", "accessResult", "authResult", "attendanceStatus"]),
    }

def csv_to_xlsx(csv_path: str, xlsx_path: str) -> None:
    try:
        from openpyxl import Workbook
    except Exception as e:
        raise RuntimeError("openpyxl not installed. Install: pip install openpyxl") from e

    wb = Workbook()
    ws = wb.active
    ws.title = "events"

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)

    wb.save(xlsx_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", required=True, help="Device IP, e.g. 192.168.1.50")
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", required=True, help='Password or "-" to prompt from stdin')
    ap.add_argument("--start", required=True, help='Start time, e.g. 2025-12-01T00:00:00+03:00')
    ap.add_argument("--end", required=True, help='End time, e.g. 2026-01-30T23:59:59+03:00')
    ap.add_argument("--max", type=int, default=200, help="Page size (maxResults)")
    ap.add_argument("--minor", type=int, default=0, help="minor=0 for all, try 75 if empty")
    ap.add_argument("--out", required=True, help="Output CSV path")
    ap.add_argument("--xlsx", default="", help="Optional output XLSX path")
    ap.add_argument("--only-card", action="store_true", help="Filter only card verification events")
    args = ap.parse_args()

    password = args.password
    if password == "-":
        import getpass
        password = getpass.getpass("Password: ")

    fieldnames = ["time","employeeNo","name","cardNo","verifyMode","doorNo","readerNo","major","minor","result"]

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        pos = 0
        total_written = 0

        while True:
            payload = json.dumps({
                "AcsEventCond": {
                    "searchID": "log_20251201_20260130",
                    "searchResultPosition": pos,
                    "maxResults": args.max,
                    "major": 5,
                    "minor": args.minor,
                    "startTime": args.start,
                    "endTime": args.end,
                }
            }, ensure_ascii=False)

            resp = run_curl(args.ip, args.user, password, payload)
            info, status = extract_info_list(resp)

            if not info:
                break

            written_this_page = 0
            for ev in info:
                if args.only_card and not is_card_event(ev):
                    continue
                w.writerow(event_to_row(ev))
                written_this_page += 1

            total_written += written_this_page
            # Переходим дальше по "сырым" позициям; чаще всего корректно += len(info)
            pos += len(info)

            # Если устройство явно говорит, что больше нет — можно остановиться
            if status and status.upper() not in ("MORE", "OK"):
                break

        print(f"Done. Rows written: {total_written}", file=sys.stderr)

    if args.xlsx:
        csv_to_xlsx(args.out, args.xlsx)
        print(f"XLSX saved: {args.xlsx}", file=sys.stderr)

if __name__ == "__main__":
    main()

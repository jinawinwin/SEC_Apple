#!/usr/bin/env python3
"""Fetch Apple facts from SEC and publish annual, half-year and quarter data."""
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json
import os

CIK = "0000320193"
URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"
OUT = Path(__file__).resolve().parents[1] / "data" / "financials.json"
TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"],
    "gross_profit": ["GrossProfit"], "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"], "eps_diluted": ["EarningsPerShareDiluted"],
    "eps_basic": ["EarningsPerShareBasic"], "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "assets": ["Assets"], "liabilities": ["Liabilities"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
}
INSTANT = {"cash", "assets", "liabilities"}

def get_facts(payload):
    facts = payload.get("facts", {}).get("us-gaap", {})
    return {name: next((facts[tag] for tag in tags if tag in facts), None) for name, tags in TAGS.items()}

def unit_rows(fact, key):
    if not fact:
        return []
    units = fact.get("units", {})
    unit = "USD/shares" if key.startswith("eps_") else "USD"
    return units.get(unit, [])

def main():
    contact = os.environ.get("SEC_CONTACT_EMAIL", "").strip()
    if not contact:
        raise RuntimeError("Set the SEC_CONTACT_EMAIL Actions secret to a monitored contact email before running the SEC refresh.")
    req = Request(URL, headers={
        "User-Agent": f"Apple SEC Dashboard/1.0 {contact}",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov",
    })
    try:
        with urlopen(req, timeout=45) as response:
            raw = response.read()
            if response.info().get("Content-Encoding") == "gzip":
                import gzip
                raw = gzip.decompress(raw)
            facts = get_facts(json.loads(raw.decode("utf-8")))
    except HTTPError as error:
        body = error.read()
        if error.headers.get("Content-Encoding") == "gzip":
            import gzip
            body = gzip.decompress(body)
        detail = body.decode("utf-8", errors="replace")
        raise RuntimeError(f"SEC Company Facts returned HTTP {error.code}: {detail}") from error
    result = {"annual": {}, "half_year": {}, "quarterly": {}}
    instant = {}
    for metric, fact in facts.items():
        for row in unit_rows(fact, metric):
            if row.get("form") not in ("10-K", "10-Q") or not row.get("end"):
                continue
            end = date.fromisoformat(row["end"])
            start = date.fromisoformat(row["start"]) if row.get("start") else None
            filed = row.get("filed", "")
            if metric in INSTANT:
                prev = instant.get(end.isoformat(), {}).get("_filed", "")
                if filed >= prev:
                    instant.setdefault(end.isoformat(), {})[metric] = row["val"]
                    instant[end.isoformat()]["_filed"] = filed
                continue
            if not start:
                continue
            days = (end - start).days + 1
            if row["form"] == "10-K" and 330 <= days <= 380:
                kind = "annual"
            elif row["form"] == "10-Q" and 150 <= days <= 200:
                kind = "half_year"
            elif row["form"] == "10-Q" and 70 <= days <= 110:
                kind = "quarterly"
            else:
                continue
            key = (end.isoformat(), start.isoformat())
            current = result[kind].setdefault(key, {"end": end.isoformat(), "period": f"{row.get('fy', '')} {row.get('fp', '')}".strip(), "_filed": ""})
            if filed >= current["_filed"]:
                current[metric] = row["val"]
                current["_filed"] = filed
    for kind, periods in result.items():
        cleaned = []
        for item in periods.values():
            item.pop("_filed", None)
            item.pop("start", None)
            item.update({k: v for k, v in instant.get(item["end"], {}).items() if k != "_filed"})
            if item.get("capex") is not None:
                item["capex"] = abs(item["capex"])
            if item.get("operating_cash_flow") is not None and item.get("capex") is not None:
                item["free_cash_flow"] = item["operating_cash_flow"] - item["capex"]
            cleaned.append(item)
        result[kind] = sorted(cleaned, key=lambda x: x["end"], reverse=True)
    result["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    result["source"] = URL
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated SEC financial dataset")

if __name__ == "__main__":
    main()


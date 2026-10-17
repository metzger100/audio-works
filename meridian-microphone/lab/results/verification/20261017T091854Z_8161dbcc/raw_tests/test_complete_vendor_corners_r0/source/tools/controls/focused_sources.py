# SPDX-License-Identifier: GPL-3.0-or-later
"""Retain public documentary bytes in private, unique retrieval directories."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]
URLS = {
    "keithley": "https://download.tek.com/document/LowLevelHandbook_7Ed.pdf",
    "wima": "https://www.wima.de/wp-content/uploads/media/e_WIMA_MKP_2.pdf",
    "wima_current": "https://www.wima.de/en/our-product-range/metallized-capacitors/mkp-2/",
    "middlebrook": "https://iic-jku.github.io/analog-circuit-design/slides/middlebrook_method.html",
    "adi_injection": "https://www.analog.com/jp/lp/003/jp-web-lab/tnj-055.html",
    "that_receiver": "https://thatcorp.com/datashts/1200data.pdf",
    "that_driver": "https://www.thatcorp.com/datashts/1600data.pdf",
    "jfe150": "https://www.ti.com/lit/ds/symlink/jfe150.pdf",
    "jfe_application": "https://www.ti.com/lit/an/slpa018/slpa018.pdf",
    "bc850c": "https://assets.nexperia.com/documents/data-sheet/BC850C.pdf",
    "pmbt5551": "https://assets.nexperia.com/documents/data-sheet/PMBT5551.pdf",
    "ep1585365": "https://data.epo.org/publication-server/rest/v1.2/patents/EP1585365NWB1/document.pdf",
    "ep2590434": "https://data.epo.org/publication-server/rest/v1.2/publication-dates/20160127/patents/EP2590434NWB1/document.pdf",
    "epo_register": "https://register.epo.org/smartSearch?query=pn%3DEP1585365",
    "audiotube": "https://www.audiotube24.de/product_id-00015999",
}


def main():
    folder = (
        ROOT
        / "research/device_sources/local"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_focused_"
            + uuid.uuid4().hex[:8]
        )
    )
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    for key, url in URLS.items():
        dest = folder / key
        dest.mkdir()
        row = dict(
            id=key,
            url=url,
            utc=datetime.now(timezone.utc).isoformat(),
            terms="Original notices; redistribution unresolved; private documentary research",
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Meridian research audit"})
            with urllib.request.urlopen(req, timeout=20) as response:
                data = response.read()
                row.update(
                    final_url=response.url,
                    http_status=response.status,
                    mime=response.headers.get("Content-Type"),
                    bytes=len(data),
                    sha256=hashlib.sha256(data).hexdigest(),
                )
            (dest / "response.bin").write_bytes(data)
            row["kind"] = "pdf" if data.startswith(b"%PDF") else "html_or_other"
            row["status"] = "acquired_response_requires_content_review"
        except (OSError, ValueError) as exc:
            row.update(status="failed", reason=str(exc))
        (dest / "receipt.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append(row)
        print(key, row["status"], flush=True)
    (folder / "receipts.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(folder.relative_to(ROOT))


if __name__ == "__main__":
    main()

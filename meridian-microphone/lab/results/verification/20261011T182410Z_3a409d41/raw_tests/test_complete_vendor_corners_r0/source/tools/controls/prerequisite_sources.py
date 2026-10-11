# SPDX-License-Identifier: GPL-3.0-or-later
"""Public primary-source retrieval; unique receipts, no licence acceptance."""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
URLS = {
    "slpm366": "https://www.ti.com/lit/zip/slpm366",
    "slpm349i": "https://www.ti.com/lit/zip/slpm349i",
    "slpm358": "https://www.ti.com/lit/zip/slpm358",
    "slpm350b": "https://www.ti.com/lit/zip/slpm350b",
    "slpm351b": "https://www.ti.com/lit/zip/slpm351b",
    "slpu009": "https://www.ti.com/lit/ug/slpu009/slpu009.pdf",
    "ngspice47": "https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf",
    "nexperia_models": "https://assets.nexperia.com/documents/application-note/AN10462.pdf",
    "ti_noise": "https://www.ti.com/lit/an/slva043b/slva043b.pdf",
    "jfe150_sheet": "https://www.ti.com/lit/ds/symlink/jfe150.pdf",
}


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = (
        ROOT / "research/device_sources/local" / (stamp + "_prerequisites_" + uuid.uuid4().hex[:8])
    )
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, url in URLS.items():
        dest = folder / name
        dest.mkdir()
        row = dict(
            id=name,
            url=url,
            utc=datetime.now(timezone.utc).isoformat(),
            terms="Original notices apply; redistribution unresolved; private research only",
        )
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "Meridian research source audit"}
            )
            with urllib.request.urlopen(request, timeout=25) as response:
                data = response.read()
                row.update(
                    final_url=response.url,
                    status_code=response.status,
                    headers=dict(response.headers),
                    bytes=len(data),
                    sha256=hashlib.sha256(data).hexdigest(),
                )
            (dest / "response.bin").write_bytes(data)
            row["kind"] = "zip" if data[:2] == b"PK" else "pdf" if data[:4] == b"%PDF" else "other"
            if row["kind"] == "zip":
                with zipfile.ZipFile(dest / "response.bin") as archive:
                    row["members"] = []
                    for member in archive.infolist():
                        if member.is_dir():
                            continue
                        body = archive.read(member)
                        row["members"].append(
                            dict(
                                name=member.filename,
                                bytes=len(body),
                                sha256=hashlib.sha256(body).hexdigest(),
                            )
                        )
                        # Flat numbered files avoid trusting archive paths.
                        (dest / ("member_%03d" % len(row["members"]))).write_bytes(body)
            row["status"] = "acquired" if row["kind"] in {"zip", "pdf"} else "non_document_response"
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            row.update(status="failed", reason=str(exc))
        (dest / "receipt.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append(row)
        print(name, row["status"], flush=True)
    (folder / "receipts.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(folder)


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: GPL-3.0-or-later
"""Dated private primary-source receipts; no agreements or overwritten originals."""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]
URLS = {
    "charge": "https://www.ti.com/lit/an/sloa033a/sloa033a.pdf",
    "electrometer": "https://www.analog.com/media/en/technical-documentation/data-sheets/ADA4530-1.pdf",
    "guard_methods": "https://www.analog.com/media/en/technical-documentation/application-notes/AN-1373.pdf",
    "opa197": "https://www.ti.com/lit/ds/symlink/opa197.pdf",
    "opa928": "https://www.ti.com/lit/ds/symlink/opa928.pdf",
    "opa928_fixture": "https://www.ti.com/lit/ug/sbou282a/sbou282a.pdf",
    "stm": "https://arxiv.org/pdf/2007.00615",
    "cyclo": "https://designers-guide.org/theory/cyclo-paper.pdf",
    "mance": "https://spaceserv1.ethz.ch/aeil/download/Davor_Mance_Thesis_text.pdf",
    "gefro": "https://arxiv.org/pdf/1307.5233",
    "photo_servo": "https://arxiv.org/pdf/2604.18969",
    "ngspice47": "https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf",
    "xyce": "https://xyce.sandia.gov/files/xyce/Xyce_Users_Guide_7.10.pdf",
    "ep_charge": "https://data.epo.org/publication-server/rest/v1.2/publication-dates/20131218/patents/EP2675188NWA1/document.pdf",
    "ep_guard": "https://data.epo.org/publication-server/rest/v1.2/patents/EP2002273NWB1/document.pdf",
}
FOLLOWUP = {
    "jiang": "https://repository.tudelft.nl/file/File_b234e936-4b3b-4450-a0e2-d767806b3343",
    "masalov": "https://arxiv.org/pdf/1709.05213",
    "electrometer_lowercase": "https://www.analog.com/media/en/technical-documentation/data-sheets/ada4530-1.pdf",
    "guard_methods_html": "https://www.analog.com/en/resources/app-notes/an-1373.html",
    "ngspice47_followup": "https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf",
    "ep_charge_followup": "https://data.epo.org/publication-server/rest/v1.2/publication-dates/20131218/patents/EP2675188NWA1/document.pdf",
    "ep_guard_followup": "https://data.epo.org/publication-server/rest/v1.2/patents/EP2002273NWB1/document.pdf",
}
LEADS = {
    "jefferts_1987": "https://tf.nist.gov/general/pdf/655.pdf",
    "hamamatsu_s5973": "https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/s5971_etc_kpin1025e.pdf",
}


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = (
        ROOT / "research/architecture_sources/local" / (stamp + "_diverse_" + uuid.uuid4().hex[:8])
    )
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    selected = LEADS if "--leads" in sys.argv else FOLLOWUP if "--followup" in sys.argv else URLS
    for name, url in selected.items():
        row = dict(
            id=name,
            url=url,
            utc=datetime.now(timezone.utc).isoformat(),
            terms="Original notices apply; redistribution unresolved; private research",
        )
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Meridian research audit"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
                row.update(
                    final_url=response.url,
                    mime=response.headers.get("Content-Type"),
                    status_code=response.status,
                    bytes=len(data),
                )
            dest = folder / (name + ".bin")
            dest.write_bytes(data)
            row.update(
                path=str(dest.relative_to(ROOT)),
                sha256=hashlib.sha256(data).hexdigest(),
                status="pdf" if data.startswith(b"%PDF") else "non_pdf_retained",
            )
        except (OSError, ValueError) as exc:
            row.update(status="failed", reason=str(exc))
            if isinstance(exc, urllib.error.HTTPError):
                data = exc.read()
                dest = folder / (name + "_failure.bin")
                dest.write_bytes(data)
                row.update(
                    path=str(dest.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest()
                )
        rows.append(row)
        (folder / (name + ".json")).write_text(json.dumps(row, indent=2) + "\n")
        print(name, row["status"], flush=True)
    (folder / "receipts.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(folder)


if __name__ == "__main__":
    main()

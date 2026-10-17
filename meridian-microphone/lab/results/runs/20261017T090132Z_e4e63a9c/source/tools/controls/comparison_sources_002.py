# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite primary-source refresh; retain failures and exact private response bytes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import read_yaml
from meridian_lab.bounded import write_data

URLS = {
    "jfe150": "https://www.ti.com/lit/ds/symlink/jfe150.pdf",
    "jfe150_exact": "https://www.ti.com/product/JFE150/part-details/JFE150DBVR",
    "opa197": "https://www.ti.com/lit/ds/symlink/opa197.pdf",
    "opa197_exact": "https://www.ti.com/product/OPA197/part-details/OPA197IDBVR",
    "opa928": "https://www.ti.com/lit/ds/symlink/opa928.pdf",
    "opa928_fixture": "https://www.ti.com/lit/ug/sbou282a/sbou282a.pdf",
    "bipolar": "https://assets.nexperia.com/documents/data-sheet/BC846_SER.pdf",
    "bipolar_lifecycle": "https://www.nexperia.com/product/BC846",
    "pmbt5551": "https://assets.nexperia.com/documents/data-sheet/PMBT5551.pdf",
    "bc850c": "https://assets.nexperia.com/documents/data-sheet/BC850C.pdf",
    "wima": "https://www.wima.de/wp-content/uploads/media/e_WIMA_MKP_2.pdf",
    "hva": "https://www.seielect.com/catalog/sei-hva.pdf",
    "charge": "https://www.ti.com/lit/an/sloa033a/sloa033a.pdf",
    "guard": "https://www.analog.com/en/resources/app-notes/an-1373.html",
    "electrometer": "https://www.analog.com/media/en/technical-documentation/data-sheets/ada4530-1.pdf",
    "periodic_noise": "https://designers-guide.org/theory/cyclo-paper.pdf",
    "ngspice47": "https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf",
    "ngspice_news": "https://ngspice.sourceforge.io/news.html",
    "capsule": "https://store.arienneaudio.com/microphone-capsules/20-arienne-audio-flat-k47-microphone-capsule.html",
    "jfe_retail": "https://www.digikey.de/de/products/detail/texas-instruments/JFE150DBVR/18185049",
    "film_retail": "https://www.audiotube24.de/product_id-00015999",
    "fr_retail": "https://www.digikey.de/en/products/detail/panasonic-industry/EEU-FR1J470/3072280",
    "dpma_charge": "https://register.dpma.de/DPMAregister/pat/register?AKZ=E121716344",
    "dpma_expired": "https://register.dpma.de/DPMAregister/pat/register?AKZ=E044500734",
    "dpma_reset": "https://register.dpma.de/DPMAregister/pat/register?AKZ=E147210710",
    "epo_charge": "https://data.epo.org/publication-server/rest/v1.2/patents/EP2675188NWB1/document.pdf",
    "epo_guard": "https://data.epo.org/publication-server/rest/v1.2/patents/EP2002273NWB1/document.pdf",
    "epo_register": "https://register.epo.org/application?number=EP12171634",
}


def main():
    suffix = "-followup" if "--followup" in sys.argv else ""
    target = ROOT / f"research/architectures/comparison-sources-002{suffix}.json"
    if target.exists():
        raise ValueError("Source receipt already exists; preserve and inspect it")
    folder = ROOT / "research/architecture_sources/local" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_comparison002_" + uuid.uuid4().hex[:8]
    )
    folder.mkdir(parents=True, exist_ok=False)

    def fetch(item):
        name, url = item
        row = dict(id=name, url=url, retrieved_utc=datetime.now(timezone.utc).isoformat(),
                   terms="Original notices retained; private research; redistribution unresolved")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Meridian research audit"})
            with urllib.request.urlopen(req, timeout=20) as response:
                data = response.read()
                row.update(final_url=response.url, mime=response.headers.get("Content-Type"),
                           http_status=response.status, bytes=len(data))
            row["state"] = "pdf" if data.startswith(b"%PDF") else "html_or_other_requires_inspection"
        except (OSError, ValueError) as exc:
            row.update(state="failed", reason=str(exc))
            data = exc.read() if isinstance(exc, urllib.error.HTTPError) else None
        if data is not None:
            path = folder / (name + ".bin")
            path.write_bytes(data)
            row.update(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest())
        (folder / (name + ".json")).write_text(json.dumps(row, indent=2) + "\n")
        return row

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(fetch, URLS.items()))
    # Preserve source/query/file ledgers as inputs, never replace the earlier cohorts.
    inherited = ["research/architectures/focused-sources-001.json",
                 "research/architectures/diverse-sources-001.json",
                 "research/architectures/diverse-audit-sources-001.json",
                 "research/capsules/queries-001.json", "research/capsules/sources-001.yaml",
                 "research/devices/simulation-prerequisites-queries-001.json",
                 "research/patents/sources-screening-001.json",
                 "research/patents/queries-official-001.json", "research/patents/queries-web-001.json"]
    prior = []
    for name in inherited:
        p = ROOT / name
        value = read_yaml(p)
        prior.append(dict(path=name, sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                          resolved_entries=len(value) if isinstance(value, (list, dict)) else None))
    write_data(target, dict(date="2026-10-17", sources=rows, inherited=prior,
                           directory=str(folder.relative_to(ROOT)), status="retrieval_only_not_validation"))
    print(json.dumps(dict(sources=len(rows), states={k:sum(r["state"]==k for r in rows)
          for k in sorted({r["state"] for r in rows})}, directory=str(folder.relative_to(ROOT)))))


if __name__ == "__main__":
    main()

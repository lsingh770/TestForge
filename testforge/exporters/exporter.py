from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def export_results(results: list[dict[str, Any]], output_dir: str | Path) -> dict[str, str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    json_path = target / "results.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    csv_path = target / "results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        fields = [
            "id",
            "name",
            "category",
            "priority",
            "passed",
            "status_code",
            "summary",
            "error",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow({
                "id": result.get("id", ""),
                "name": result.get("name", ""),
                "category": result.get("category", ""),
                "priority": result.get("priority", ""),
                "passed": result.get("passed", False),
                "status_code": result.get("status_code", ""),
                "summary": result.get("summary", ""),
                "error": result.get("error", ""),
            })

    junit_path = target / "results.xml"
    junit_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<testsuite name=\"testforge\" tests=\"{total}\" failures=\"{failures}\">
{cases}
</testsuite>
""".format(
        total=len(results),
        failures=sum(1 for r in results if not r.get("passed", False)),
        cases="\n".join(
            f"<testcase classname=\"{r.get('category','unknown')}\" name=\"{r.get('name','unnamed')}\" time=\"0\">"
            + (f"<failure message=\"{r.get('error','failure')}\">{r.get('summary','Failed')}</failure>" if not r.get("passed", False) else "")
            + "</testcase>"
            for r in results
        ),
    )
    junit_path.write_text(junit_xml, encoding="utf-8")

    return {
        "json": str(json_path),
        "csv": str(csv_path),
        "junit": str(junit_path),
    }

"""Hand-review fixes applied on top of the Bama bootstrap. Re-run after re-bootstrapping:
    uv run python -m catalog.review_fixes
"""

import copy
import re
import json
from pathlib import Path

SEED = Path(__file__).parent / "data" / "vehicles.seed.json"


def fix(rows):
    for r in rows:
        # Some spec URLs carry a second numeric page ID ("pars-specs-1463-471-elx"); Bama ads use
        # the bare trim slug ("peugeot-pars-elx"), so drop it from the trim, ID and alias.
        m = re.match(r"^\d+-(.+)$", r["trim"])
        if m:
            r["trim"] = m.group(1)
            r["id"] = f"{r['make']}-{r['model']}-{r['trim']}"
            r["aliases"] = {"bama": [r["id"]]}
        # Bama sometimes leaves the gearbox as just "N سرعته"; the trim name tells manual from automatic.
        if not r["gearbox"]:
            name = f"{r['trim']} {r['trim_fa']} {r['model_fa']}".lower()
            r["gearbox"] = "automatic" if ("اتوماتیک" in name or "at" in r["trim"].split("-") or "automatic" in name or r["trim"].endswith("at")) else "manual"
    ids = {r["id"] for r in rows}
    # Pride 132 is missing from Bama's review index; it is the hatchback of the 131 with the same drivetrain.
    for r131 in [r for r in rows if r["id"].startswith("pride-131-")]:
        r132 = copy.deepcopy(r131)
        trim = r131["trim"]
        r132.update(id=f"pride-132-{trim}", model="132", model_fa="پراید 132", family="pride-132",
                    body_type="hatchback", bama_url="", aliases={"bama": [f"pride-132-{trim}"]},
                    note="copied from Pride 131 specs (hand review)")
        if r132["id"] not in ids:
            rows.append(r132)
    # Peugeot 405 GLX bi-fuel is common on Divar and Bama but missing from Bama's review index.
    glx = next((r for r in rows if r["id"] == "peugeot-405-glx"), None)
    if glx and "peugeot-405-glxcng" not in ids:
        cng = copy.deepcopy(glx)
        cng.update(id="peugeot-405-glxcng", trim="glxcng", trim_fa="GLX دوگانه سوز", fuel_type="dual", bama_url="",
                   aliases={"bama": ["peugeot-405-glxcng"]}, note="copied from 405 GLX specs, dual fuel (hand review)")
        rows.append(cng)
    return rows


if __name__ == "__main__":
    rows = fix(json.loads(SEED.read_text()))
    SEED.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(len(rows), "rows")

"""Render the four-page design source to self-contained HTML using the stdlib."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)


def render_section(source: str) -> str:
    lines = source.strip().splitlines()
    result: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == "<!-- architecture -->":
            svg = (DOCS / "architecture.svg").read_text(encoding="utf-8")
            result.append(f'<figure>{svg}<figcaption>One platform, two paths: verified publication and controlled execution.</figcaption></figure>')
        elif line.startswith("# "):
            result.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            result.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("| "):
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            header = "".join(f"<th>{inline(cell)}</th>" for cell in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows[2:])
            result.append(f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>")
            continue
        elif line.startswith("- ") or re.match(r"\d+\. ", line):
            ordered = bool(re.match(r"\d+\. ", line))
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            pattern = r"^\d+\. " if ordered else r"^- "
            while index < len(lines) and re.match(pattern, lines[index].strip()):
                text = re.sub(pattern, "", lines[index].strip())
                items.append(f"<li>{inline(text)}</li>")
                index += 1
            result.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        else:
            result.append(f"<p>{inline(line)}</p>")
        index += 1
    return "\n".join(result)


def main() -> None:
    sections = (DOCS / "design.md").read_text(encoding="utf-8").split("<!-- pagebreak -->")
    if len(sections) != 4:
        raise ValueError("The design must have exactly four page sections")
    pages = "\n".join(
        f'<article class="page"><main>{render_section(section)}</main><footer><span>Engineering AI Marketplace · Design proposal</span><span>{number} / 4</span></footer></article>'
        for number, section in enumerate(sections, start=1)
    )
    document = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Engineering AI Marketplace — Design</title><style>
@page { size: A4; margin: 13mm 15mm; }
* { box-sizing: border-box; }
body { margin: 0; color: #1d2c3b; background: #e7ecf1; font: 10.3pt/1.3 Arial, sans-serif; }
.page { width: 180mm; min-height: 271mm; display: flex; flex-direction: column; background: white; margin: 8mm auto; padding: 0; break-after: page; }
.page:last-child { break-after: auto; }
main { flex-shrink: 0; padding-bottom: 3mm; }
h1 { margin: 0 0 4mm; color: #173f65; font-size: 22pt; line-height: 1.12; }
h2 { margin: 4mm 0 2.5mm; color: #173f65; font-size: 13pt; line-height: 1.18; }
main > h2:first-child { margin-top: 0; }
p { margin: 0 0 2.8mm; }
strong { color: #142d45; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 3mm; font-size: 9.3pt; line-height: 1.29; }
th { text-align: left; color: #173f65; background: #eaf1f7; }
th, td { padding: 2.1mm 2.3mm; vertical-align: top; border-bottom: .25mm solid #d6e0e9; }
td:first-child { width: 29%; }
tr { break-inside: avoid; }
code { font: 8.6pt/1.3 monospace; overflow-wrap: anywhere; }
ul, ol { padding-left: 5mm; margin: 0 0 3mm; }
li { margin: 0 0 2mm; break-inside: avoid; }
figure { margin: 0 0 3mm; }
figure svg { display: block; width: 100%; height: auto; }
figcaption { color: #617080; font-size: 8.1pt; margin-top: 1mm; }
footer { flex-shrink: 0; margin-top: auto; padding-top: 3mm; border-top: .25mm solid #d6e0e9; display: flex; justify-content: space-between; color: #617080; font-size: 8pt; }
@media screen { .page { padding: 10mm; width: 200mm; min-height: 291mm; box-shadow: 0 2px 12px #bcc6d0; } }
@media print { body { background: white; } .page { margin: 0; } }
</style></head><body>""" + pages + "</body></html>\n"
    destination = DOCS / "design.html"
    destination.write_text(document, encoding="utf-8")
    print(f"Rendered {len(sections)} page sections to {destination}")


if __name__ == "__main__":
    main()

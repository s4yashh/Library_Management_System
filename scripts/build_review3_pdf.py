"""Build the self-contained Review III submission PDF from the Markdown report.

Requires pandoc and PyMuPDF in the invoking Python environment.
"""

from pathlib import Path
import subprocess
import tempfile

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "review-3-report.md"
EVIDENCE = ROOT / "docs" / "live-verification.md"
OUTPUT = ROOT / "review3.pdf"

CSS = """
body { font-family: sans-serif; font-size: 10.1pt; line-height: 1.3; color: #17253b; }
h1 { font-size: 21pt; color: #112c50; margin-top: 0; margin-bottom: 13pt; }
h2 { font-size: 14pt; color: #134879; margin-top: 17pt; margin-bottom: 7pt;
     border-bottom: 1px solid #bed0df; padding-bottom: 4pt; }
h3 { font-size: 11.5pt; color: #174e79; margin-top: 12pt; margin-bottom: 5pt; }
p { margin-top: 0; margin-bottom: 8pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.1pt; margin: 7pt 0 12pt; }
th { background-color: #e8f1f8; color: #163958; font-weight: bold; }
th, td { border: 0.5pt solid #c5d4df; padding: 4pt 5pt; vertical-align: top; }
tr:nth-child(even) { background-color: #f7fafc; }
pre { background-color: #f1f5f8; border-left: 3pt solid #4787b4; padding: 7pt;
      font-family: monospace; font-size: 8pt; white-space: pre-wrap; }
code { font-family: monospace; font-size: 8.5pt; }
img { max-width: 100%; max-height: 340pt; }
a { color: #176399; text-decoration: none; }
"""


def html_from_markdown(markdown: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html"],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def main() -> None:
    report = REPORT.read_text(encoding="utf-8")
    evidence = EVIDENCE.read_text(encoding="utf-8")
    evidence = evidence.replace("# Live Oracle Verification — 26 October 2026", "# Appendix A — Live Oracle Verification", 1)
    html = html_from_markdown(report + "\n\n" + evidence)
    html = html.replace('src="er-diagram.png"', 'src="docs/er-diagram.png"')
    story = pymupdf.Story(html, user_css=CSS, archive=pymupdf.Archive(str(ROOT)))
    page = pymupdf.Rect(0, 0, 595, 842)  # A4 portrait, points
    content = pymupdf.Rect(48, 48, 547, 790)

    with tempfile.TemporaryDirectory() as temp_dir:
        draft = Path(temp_dir) / "draft.pdf"
        writer = pymupdf.DocumentWriter(str(draft))
        story.write(writer, lambda page_no, filled: (page, content, None))
        writer.close()

        document = pymupdf.open(draft)
        for index, pdf_page in enumerate(document):
            if index > 0:
                pdf_page.insert_text(
                    (48, 30), "LIBRARY MANAGEMENT SYSTEM  |  REVIEW III",
                    fontsize=8, fontname="helv", color=(0.24, 0.39, 0.52),
                )
            pdf_page.draw_line((48, 806), (547, 806), color=(0.73, 0.81, 0.87), width=0.5)
            pdf_page.insert_text(
                (48, 820), "Suyash Singh  •  24BYB0078",
                fontsize=8, fontname="helv", color=(0.32, 0.40, 0.48),
            )
            pdf_page.insert_text(
                (513, 820), f"{index + 1} / {len(document)}",
                fontsize=8, fontname="helv", color=(0.32, 0.40, 0.48),
            )
        document.set_metadata({
            "title": "Library Management System — Review III",
            "author": "Suyash Singh",
            "subject": "Integrated System and Final Demonstration",
        })
        document.save(OUTPUT, garbage=4, deflate=True)
        print(f"Created {OUTPUT} ({len(document)} pages)")


if __name__ == "__main__":
    main()

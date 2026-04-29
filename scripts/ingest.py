"""Split an HTML file into chunks (one per line) using the HTML section splitter."""

import argparse
from pathlib import Path

from compass.infrastructure.html_splitter import split_html


def main(html_path: str, output_path: str) -> None:
    html = Path(html_path).read_text(encoding="utf-8")
    sections = split_html(html)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for section in sections:
            line = section["content"].replace("\n", " ").strip()
            if line:
                f.write(line + "\n")

    print(f"Done – {sum(1 for _ in out.open())} chunks written to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split HTML into chunks (one per line).")
    parser.add_argument("html", help="Path to the HTML file")
    parser.add_argument("-o", "--output", default="data/chunks.txt", help="Output txt file (default: data/chunks.txt)")
    args = parser.parse_args()

    main(args.html, args.output)

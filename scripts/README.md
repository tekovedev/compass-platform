# Scripts

## Ingest

Split an HTML file into chunks (one per line) using the HTML section splitter.

```bash
python scripts/ingest.py data/BO-COD-DL10135.html                      # outputs to data/chunks.txt
python scripts/ingest.py data/BO-COD-DL10135.html -o output/chunks.txt  # custom output
```

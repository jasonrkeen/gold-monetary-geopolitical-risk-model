# Contributing

Contributions should preserve the project's distinction between gold-supportive
conditions and market risk, as well as its explicit live/demo labeling.

## Local validation

Create a virtual environment, install `requirements.txt`, and run:

```bash
python -m unittest discover -s tests -v
python main.py --mode demo
```

Before changing a connector, also run `python main.py --mode live` and confirm
that the output manifest records the expected provider, coverage, and dates.

Before changing report code, render every PDF page to images and inspect it for
clipping, overlaps, broken glyphs, and unreadable charts. PDF text extraction
alone is not a layout test.

## Pull requests

- Keep changes focused and explain any methodological effect.
- Add or update tests for analytical logic and failure behavior.
- Update `docs/METHODOLOGY.md` when factors, weights, transformations, or
  scenario assumptions change.
- Never present deterministic demo output as current market analysis.

# EFM Council Lite

A small, shareable ethical deliberation program inspired by the Ethical Field Method.

This version is intentionally lightweight:
- no API keys
- no external model SDKs
- no FastAPI
- no dependency-heavy setup
- pure Python standard library

It does **not** pretend to solve ethics. It gives a structured multi-lens evaluation map for a decision prompt.

## What it does

Given a decision, it runs several evaluative lenses:
- Kantian constraint
- Consequentialist outcomes
- Virtue trajectory
- Confucian role obligations
- Trustee stewardship
- Stoic reality alignment
- Institutional red flags
- Genealogical adversarial critique

Then it synthesizes:
- convergences
- fault lines
- suspension triggers
- unresolved questions

## Usage

```bash
python cli.py "Should we deploy this system before the safety audit is complete?"
```

From file:

```bash
python cli.py --file decision.txt
```

Save JSON and Markdown outputs:

```bash
python cli.py "Your decision" --output output/my_decision
```

## Design

This is a deterministic local scaffold, not an LLM product. Each lens uses rule-guided promptless heuristics and question generation so the system is:
- runnable anywhere Python runs
- easy to inspect
- easy to extend
- safe to publish as a starting point

## Files

- `cli.py` — command line entry point
- `efm_council.py` — core evaluation engine
- `report.py` — markdown formatter
- `sample_decision.txt` — example input

## Next steps

Natural extensions:
- replace heuristic lenses with pluggable model backends
- add richer scoring rules
- add YAML-configurable lenses
- add a web UI or API wrapper

## License

MIT

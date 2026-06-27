# Demo Data

This directory holds generated demo data files. **These files are not committed to git** (see root `.gitignore`).

## Files (generated, not committed)

| File | Description |
|------|-------------|
| `positions_in.parquet` | ~500 synthetic loan positions for the India demo tenant |
| `positions_us.parquet` | ~500 synthetic loan positions for the US demo tenant |
| `reference_data_in.json` | Risk weights, LCR haircuts, run-off rates for IN jurisdiction |
| `reference_data_us.json` | Risk weights, LCR haircuts, run-off rates for US jurisdiction |

## Generating Demo Data

```bash
uv run python tools/generate_demo_data.py
```

This script creates all files above. Run it once after cloning if you need demo mode.

## Why Not Committed?

- Parquet files are binary — diffs are unreadable in code review
- Data changes independently of code; committing it creates noise
- Different developers may need different volumes for their testing needs

The generation script is the source of truth for demo data shape.

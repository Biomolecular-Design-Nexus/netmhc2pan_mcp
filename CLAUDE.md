# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server wrapping NetMHCIIpan-4.3 for MHC Class II peptide binding prediction. Built with FastMCP, it exposes 17 tools for epitope analysis, immunogenicity assessment, and population-level HLA screening. Requires Linux x86_64 (NetMHCIIpan binary dependency).

## Setup & Environment

```bash
# Quick setup (creates conda env, installs deps)
bash quick_setup.sh

# Manual activation
mamba activate ./env   # or: conda activate ./env

# Register with Claude Code
claude mcp add netmhc2pan -- ./env/bin/python ./src/server.py
```

Dependencies: `fastmcp loguru click pandas numpy tqdm openpyxl` (Python 3.10, installed into local `./env/`).

## Common Commands

```bash
# Run MCP server
./env/bin/python src/server.py

# Dev mode (FastMCP inspector)
fastmcp dev src/server.py

# Run server validation tests
./env/bin/python test_server.py

# Test individual scripts with sample data
python scripts/peptide_prediction.py --input examples/data/peptides.txt --allele DRB1_0101 --summary
python scripts/protein_analysis.py --input examples/data/protein.fsa --allele DRB1_0101 --context --summary
python scripts/custom_allele_prediction.py --input examples/data/peptides.txt --beta-seq examples/data/beta_chain.fsa --summary
python scripts/batch_multi_allele.py --input examples/data/peptides.txt --alleles DRB1_0101,DRB1_1501 --summary
```

## Architecture

### Two-Layer Design

1. **MCP Server Layer** (`src/server.py`): FastMCP server defining all 17 tools. Thin wrappers that delegate to the scripts layer. Tools are organized into:
   - **Synchronous tools** (4): `predict_peptide_binding`, `analyze_protein_sequence`, `predict_custom_mhc_binding`, `predict_binding_affinity` — import and call script functions directly
   - **Submit/async tools** (6): `submit_*` variants — use `JobManager` to run scripts as background subprocesses
   - **Job management tools** (5): `get_job_status`, `get_job_result`, `get_job_log`, `cancel_job`, `list_jobs`
   - **Utility tools** (2): `export_predictions_to_excel`, `analyze_netmhcpan_output`, `get_server_info`

2. **Scripts Layer** (`scripts/`): Standalone CLI scripts (Click-based) that can run independently of MCP. Each script imports from `scripts/lib/`.

### Shared Library (`scripts/lib/`)

- `netmhciipan.py`: Locates and invokes the NetMHCIIpan binary (`repo/netMHCIIpan-4.3/netMHCIIpan`). All prediction calls go through `run_netmhciipan()`.
- `parsers.py`: Parses raw NetMHCIIpan text output into structured data (predictions, strong/weak binders).
- `utils.py`: Shared utilities.

### Job System (`src/jobs/manager.py`)

`JobManager` (singleton: `job_manager`) runs scripts as background subprocesses via `mamba run -p ./env python <script>`. Jobs are tracked on disk under `jobs/<job_id>/` with `metadata.json`, `output.txt`, and `job.log`. Jobs execute in daemon threads.

### Path Resolution

`src/server.py` adds both `src/` and `scripts/` to `sys.path` so that sync tools can `from peptide_prediction import run_peptide_prediction` directly. The NetMHCIIpan binary is located by `scripts/lib/netmhciipan.py` searching `repo/netMHCIIpan-4.3/netMHCIIpan` first.

## Key Conventions

- Allele format uses underscores: `DRB1_0101`, not `DRB1*01:01`
- Peptide inputs accept either a file path (`--input`) or comma-separated strings (`--peptides`)
- Binding thresholds: strong binder <= 1.0 %Rank, weak binder <= 5.0 %Rank
- Sample data for testing lives in `examples/data/`
- Config templates in `configs/` (JSON format)

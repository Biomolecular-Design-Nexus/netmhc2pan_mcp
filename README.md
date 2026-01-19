# netMHCIIpan-4.3 MCP

> MCP Server for NetMHCIIpan-4.3 - MHC Class II binding prediction tools for epitope analysis and immunogenicity assessment

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

This MCP server provides access to NetMHCIIpan-4.3, a state-of-the-art tool for predicting binding affinity between peptides and MHC class II molecules. It enables epitope mapping, immunogenicity assessment, and population-level HLA analysis for vaccine development, immunotherapy, and basic immunology research.

### Features
- **MHC II Binding Prediction**: Accurate binding affinity prediction for HLA-DR, HLA-DQ, HLA-DP, H-2, and BoLA molecules
- **Protein Epitope Mapping**: Analyze full protein sequences to identify immunogenic regions
- **Custom Allele Support**: Use custom alpha/beta chain sequences for novel MHC variants
- **Population Analysis**: Batch prediction across multiple alleles for HLA diversity studies
- **Context-Aware Prediction**: Enhanced prediction considering flanking sequence context
- **Async Job Management**: Handle large-scale analyses with job tracking and monitoring

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment (Python 3.10)
├── src/
│   ├── server.py           # MCP server with 17 tools
│   └── jobs/               # Job management system
├── scripts/
│   ├── peptide_prediction.py      # Basic peptide binding prediction
│   ├── protein_analysis.py        # Protein sequence epitope mapping
│   ├── custom_allele_prediction.py # Custom MHC sequence analysis
│   ├── batch_multi_allele.py      # Multi-allele population screening
│   └── lib/                       # Shared utilities (275 LOC)
├── examples/
│   └── data/                      # Demo data (8 sample files)
├── configs/                       # Configuration files (5 configs)
└── repo/                          # NetMHCIIpan-4.3 binary distribution
```

---

## Installation

### Quick Setup (Recommended)

Run the automated setup script:

```bash
cd netmhc2pan_mcp
bash quick_setup.sh
```

The script will create the conda environment, install all dependencies, and display the Claude Code configuration. See `quick_setup.sh --help` for options like `--skip-env`.

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- Linux x86_64 system (for NetMHCIIpan binary)

### Manual Installation (Alternative)

If you prefer manual installation or need to customize the setup:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/netmhc2pan_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.10 -y
# or: conda create -p ./env python=3.10 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install core dependencies
pip install fastmcp loguru click pandas numpy tqdm --no-cache-dir

# Optional: For Excel export functionality
pip install openpyxl
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Runtime | Example |
|--------|-------------|---------|---------|
| `scripts/peptide_prediction.py` | Predict MHC II binding for individual peptides | <1s | Vaccine candidate screening |
| `scripts/protein_analysis.py` | Analyze protein sequences for binding regions | 1-2s | Epitope mapping |
| `scripts/custom_allele_prediction.py` | Use custom MHC sequences for novel alleles | ~1s | Novel allele analysis |
| `scripts/batch_multi_allele.py` | Batch prediction across multiple alleles | 3-5s | Population coverage |

### Script Examples

#### Peptide Binding Prediction

```bash
# Activate environment
mamba activate ./env

# Predict binding from peptide file
python scripts/peptide_prediction.py \
  --input examples/data/peptides.txt \
  --allele DRB1_0101 \
  --output results/peptide_predictions.txt \
  --summary

# Predict specific peptides directly
python scripts/peptide_prediction.py \
  --peptides AAAGAEAGKATTE,AALAAAAGVPPADKY \
  --allele DRB1_0101 \
  --summary
```

**Parameters:**
- `--input, -i`: Text file with peptides (one per line, optional scores) (required if no --peptides)
- `--peptides, -p`: Comma-separated peptides (alternative to --input)
- `--allele, -a`: MHC II allele (default: DRB1_0101)
- `--output, -o`: Output file path (optional)
- `--summary`: Include summary statistics

#### Protein Sequence Analysis

```bash
# Analyze protein for epitopes with context awareness
python scripts/protein_analysis.py \
  --input examples/data/protein.fsa \
  --allele DRB1_0101 \
  --context \
  --summary \
  --output results/protein_analysis.txt

# Direct protein sequence analysis
python scripts/protein_analysis.py \
  --sequence ASQKRPSQRHGSKYLATASTMDHARHGFLPRHRDTGILD \
  --allele DRB1_0101 \
  --sorted
```

**Parameters:**
- `--input, -i`: FASTA file with protein sequences (required if no --sequence)
- `--sequence, -s`: Single protein sequence (alternative to --input)
- `--allele, -a`: MHC II allele (default: DRB1_0101)
- `--context, -c`: Enable context-aware prediction
- `--terminal-anchor, -t`: Consider terminal anchors
- `--sorted`: Sort results by binding affinity

#### Custom Allele Prediction

```bash
# Use custom beta chain with peptides
python scripts/custom_allele_prediction.py \
  --input examples/data/peptides.txt \
  --beta-seq examples/data/beta_chain.fsa \
  --summary \
  --output results/custom_allele.txt

# Use both alpha and beta chains
python scripts/custom_allele_prediction.py \
  --peptides AAAGAEAGKATTE \
  --alpha-seq examples/data/alpha_chain.fsa \
  --beta-seq examples/data/beta_chain.fsa
```

**Parameters:**
- `--input, -i`: Input file with peptides or proteins
- `--peptides, -p`: Comma-separated peptides
- `--alpha-seq`: FASTA file with alpha chain sequence
- `--beta-seq`: FASTA file with beta chain sequence
- `--input-type`: "peptide" or "protein" (default: peptide)

#### Batch Multi-Allele Analysis

```bash
# Screen peptides across multiple alleles
python scripts/batch_multi_allele.py \
  --input examples/data/peptides.txt \
  --alleles DRB1_0101,DRB1_1501,DQB1_0602 \
  --output results/multi_allele.csv \
  --summary

# Generate Excel report
python scripts/batch_multi_allele.py \
  --input examples/data/peptides.txt \
  --alleles DRB1_0101,DRB1_0301,DRB1_1501 \
  --excel \
  --output results/population_analysis.xlsx
```

**Parameters:**
- `--input, -i`: Input file with peptides (required)
- `--alleles, -a`: Comma-separated MHC II alleles (required)
- `--output, -o`: Output CSV or XLSX file path
- `--excel`: Generate Excel format output
- `--context, -c`: Use context-aware prediction

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Activate environment first
mamba activate ./env

# Install MCP server for Claude Code
fastmcp install src/server.py --name netmhc2pan_mcp
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add netmhc2pan_mcp -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "netmhc2pan_mcp": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/netmhc2pan_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/netmhc2pan_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from netmhc2pan_mcp?
```

#### Basic Peptide Prediction
```
Use predict_peptide_binding with peptides "AAAGAEAGKATTE,AALAAAAGVPPADKY" and allele "DRB1_0101"
```

#### Protein Analysis with Context
```
Run analyze_protein_sequence on @examples/data/protein.fsa using allele DRB1_0101 with context enabled
```

#### Custom Allele Analysis
```
Use predict_custom_mhc_binding with input file @examples/data/peptides.txt and beta_seq @examples/data/beta_chain.fsa
```

#### Multi-Allele Population Screening
```
Run predict_binding_affinity on @examples/data/peptides.txt across alleles "DRB1_0101,DRB1_1501,DQB1_0602"
```

#### Long-Running Async Jobs
```
Submit submit_batch_multi_allele_screening for @examples/data/peptides.txt with alleles "DRB1_0101,DRB1_0301,DRB1_1501"
Then check the job status
```

#### Job Management
```
List all current jobs and their status
Check status of job "abc123"
Get results for completed job "def456"
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/peptides.txt` | Reference peptide input file |
| `@examples/data/protein.fsa` | Reference FASTA protein file |
| `@examples/data/beta_chain.fsa` | Reference custom beta chain |
| `@configs/default_config.json` | Reference configuration file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "netmhc2pan_mcp": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/netmhc2pan_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/netmhc2pan_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code but without @ references)
> What tools are available from netmhc2pan_mcp?
> Use predict_peptide_binding with peptides "AAAGAEAGKATTE" and allele "DRB1_0101"
> Run analyze_protein_sequence on examples/data/protein.fsa with context enabled
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 seconds):

| Tool | Description | Best For | Runtime |
|------|-------------|----------|---------|
| `predict_peptide_binding` | Predict MHC II binding for peptides | Vaccine screening, quick checks | <1s |
| `analyze_protein_sequence` | Analyze protein for epitope regions | Immunogenicity mapping | 1-2s |
| `predict_custom_mhc_binding` | Binding prediction with custom MHC | Novel allele analysis | ~1s |
| `predict_binding_affinity` | Multi-allele binding screening | Population coverage | 3-5s |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking:

| Tool | Description | Best For | Parameters |
|------|-------------|----------|------------|
| `submit_peptide_prediction` | Async peptide binding analysis | Large peptide sets | `input_file`, `peptides`, `allele`, `job_name` |
| `submit_protein_analysis` | Async protein sequence analysis | Multiple proteins | `input_file`, `allele`, `context`, `job_name` |
| `submit_custom_mhc_prediction` | Async custom allele prediction | Multiple custom alleles | `input_file`, `alpha_seq`, `beta_seq`, `job_name` |
| `submit_batch_multi_allele_screening` | Async multi-allele screening | Large population studies | `input_file`, `alleles`, `job_name` |
| `submit_large_peptide_screening` | High-throughput peptide screening | Multiple datasets | `input_files`, `allele`, `job_name` |
| `submit_multi_allele_screening` | Comprehensive allele screening | HLA diversity analysis | `input_file`, `alleles`, `job_name` |

### Job Management Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_job_status` | Check job progress and status | `job_id` |
| `get_job_result` | Get completed job results | `job_id` |
| `get_job_log` | View execution logs (last 50 lines) | `job_id`, `tail` (default: 50) |
| `cancel_job` | Cancel running job | `job_id` |
| `list_jobs` | List all jobs with optional status filter | `status` ("pending", "running", "completed", "failed") |

### Utility Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `export_predictions_to_excel` | Export job results to Excel | `job_id`, `output_file` |
| `analyze_netmhcpan_output` | Analyze raw NetMHCIIpan output | `output_file` |
| `get_server_info` | Get server and tool information | None |

---

## Examples

### Example 1: Single Peptide Screening

**Goal:** Quickly check if specific peptides bind to a particular MHC II allele

**Using Script:**
```bash
python scripts/peptide_prediction.py \
  --input examples/data/peptides.txt \
  --allele DRB1_0101 \
  --summary \
  --output results/peptide_screen.txt
```

**Using MCP (in Claude Code):**
```
Use predict_peptide_binding to process @examples/data/peptides.txt with allele DRB1_0101 and include summary statistics
```

**Expected Output:**
- Strong binders: Peptides with IC50 ≤ 50 nM
- Weak binders: Peptides with 50 nM < IC50 ≤ 500 nM
- Summary statistics: Total predictions, binder counts, score distributions

### Example 2: Protein Epitope Mapping

**Goal:** Map immunogenic regions in a target protein sequence

**Using Script:**
```bash
python scripts/protein_analysis.py \
  --input examples/data/protein.fsa \
  --allele DRB1_0101 \
  --context \
  --summary \
  --output results/epitope_map.txt
```

**Using MCP (in Claude Code):**
```
Run analyze_protein_sequence on @examples/data/protein.fsa with allele DRB1_0101, enable context-aware prediction, and include summary
```

**Expected Output:**
- All 15-mer peptide predictions from protein sequence
- Context-aware binding scores
- Summary of binding regions and immunogenic hotspots

### Example 3: Custom Allele Analysis

**Goal:** Analyze binding to a novel MHC variant using custom beta chain

**Using Script:**
```bash
python scripts/custom_allele_prediction.py \
  --input examples/data/peptides.txt \
  --beta-seq examples/data/beta_chain.fsa \
  --summary \
  --output results/custom_analysis.txt
```

**Using MCP (in Claude Code):**
```
Use predict_custom_mhc_binding with input @examples/data/peptides.txt and beta_seq @examples/data/beta_chain.fsa with summary enabled
```

**Expected Output:**
- Predictions using USER_DEF allele from custom beta chain
- Comparison with standard allele predictions
- Custom allele sequence information

### Example 4: Population Coverage Analysis

**Goal:** Assess HLA population coverage across multiple common alleles

**Using Script:**
```bash
python scripts/batch_multi_allele.py \
  --input examples/data/peptides.txt \
  --alleles DRB1_0101,DRB1_0301,DRB1_1501 \
  --excel \
  --output results/population_coverage.xlsx \
  --summary
```

**Using MCP (in Claude Code):**
```
Run predict_binding_affinity on @examples/data/peptides.txt with alleles "DRB1_0101,DRB1_0301,DRB1_1501" and generate Excel output
```

**Expected Output:**
- Cross-allele binding matrix
- Population coverage statistics
- Excel report with multiple sheets per allele

### Example 5: Large-Scale Async Processing

**Goal:** Submit large dataset for background processing with job tracking

**Using MCP (in Claude Code):**
```
Submit submit_large_peptide_screening with input_files ["file1.txt", "file2.txt"] and allele "DRB1_0101" with job_name "large_screen"
```

**Workflow:**
1. **Submit**: Returns job_id for tracking
2. **Monitor**: Use `get_job_status` to check progress
3. **Results**: Use `get_job_result` when completed
4. **Export**: Use `export_predictions_to_excel` for reporting

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With | Format |
|------|-------------|----------|--------|
| `peptides.txt` | 9 sample peptides with scores | Peptide prediction tools | Text (peptide per line) |
| `protein.fsa` | 138-amino acid protein sequence | Protein analysis tools | FASTA format |
| `peptides_context.txt` | Peptides with flanking regions | Context-aware prediction | Text with context |
| `alpha_chain.fsa` | DQA1_0101 alpha chain sequence | Custom allele tools | FASTA format |
| `beta_chain.fsa` | DQB1_0201 beta chain sequence | Custom allele tools | FASTA format |
| `peptides_binding_both.txt` | Peptides binding multiple alleles | Multi-allele analysis | Text format |
| `protein_protein_pred_9mer.txt` | Reference 9-mer predictions | Validation | NetMHCIIpan output |
| `peptides_predictions.txt` | Expected prediction results | Validation | NetMHCIIpan output |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Key Parameters |
|--------|-------------|----------------|
| `default_config.json` | Global default settings | `default_allele`, `timeout_seconds`, `strong_binder_threshold` |
| `peptide_prediction_config.json` | Peptide prediction defaults | `allele`, `output_format`, `include_summary` |
| `protein_analysis_config.json` | Protein analysis settings | `context_aware`, `terminal_anchor`, `sorted_output` |
| `custom_allele_config.json` | Custom allele parameters | `input_type`, `validation_settings` |
| `batch_multi_allele_config.json` | Batch processing options | `max_parallel_jobs`, `continue_on_error`, `output_format` |

### Config Example

```json
{
  "netmhciipan": {
    "default_allele": "DRB1_0101",
    "timeout_seconds": 300
  },
  "prediction": {
    "context_aware": false,
    "strong_binder_threshold": 1.0,
    "weak_binder_threshold": 5.0
  },
  "output": {
    "format": "text",
    "include_summary": true
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install fastmcp loguru click pandas numpy tqdm --no-cache-dir
```

**Problem:** Import errors
```bash
# Verify installation
python -c "from src.server import mcp; print('MCP server OK')"
python -c "from scripts.peptide_prediction import run_peptide_prediction; print('Scripts OK')"
```

**Problem:** NetMHCIIpan binary not found
```bash
# Check binary location
ls -la repo/netMHCIIpan-4.3/netMHCIIpan
# Should be executable and point to correct NMHOME

# Test binary directly
cd repo/netMHCIIpan-4.3/test
../netMHCIIpan -f example.pep
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove netmhc2pan_mcp
fastmcp install src/server.py --name netmhc2pan_mcp
```

**Problem:** Tools not working
```bash
# Test server directly
python -c "
from src.server import mcp
tools = [name for name, _ in mcp.list_tools()]
print(f'Available tools: {len(tools)}')
print(tools[:5])  # Show first 5 tools
"
```

**Problem:** Missing demo data
```bash
# Verify demo files exist
ls -la examples/data/
# Should show: peptides.txt, protein.fsa, alpha_chain.fsa, beta_chain.fsa, etc.

# Test with sample data
python scripts/peptide_prediction.py --input examples/data/peptides.txt --allele DRB1_0101 --summary
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory permissions
ls -la jobs/
# Should be writable

# Check job details
python -c "
from src.jobs.manager import job_manager
jobs = job_manager.list_jobs()
print(f'Active jobs: {len(jobs.get(\"jobs\", []))}')
"
```

**Problem:** Job failed
```
Use get_job_log with job_id "abc123" and tail 100 to see error details
```

Common causes:
- Input file not found or inaccessible
- Malformed peptide sequences
- NetMHCIIpan binary path issues
- Disk space or permission problems

**Problem:** Job results not found
```bash
# Check job output directory
ls -la jobs/abc123/
# Should contain: metadata.json, output.txt, job.log

# Verify job completion
python -c "
from src.jobs.manager import job_manager
status = job_manager.get_job_status('abc123')
print(f'Status: {status.get(\"status\")}')
"
```

### Data Issues

**Problem:** Invalid input format
```bash
# Check peptide file format (should be one peptide per line)
head -5 examples/data/peptides.txt

# Check FASTA format
head -5 examples/data/protein.fsa
# Should start with >sequence_name

# Validate peptide sequences (amino acids only)
python -c "
import re
with open('examples/data/peptides.txt') as f:
    for i, line in enumerate(f, 1):
        peptide = line.strip().split()[0]
        if not re.match('^[ACDEFGHIKLMNPQRSTVWY]+$', peptide):
            print(f'Invalid peptide on line {i}: {peptide}')
"
```

**Problem:** Allele not recognized
```bash
# List available alleles
cd repo/netMHCIIpan-4.3
./netMHCIIpan -list

# Common alleles:
# HLA-DR: DRB1_0101, DRB1_0301, DRB1_0401, DRB1_0701, DRB1_1501
# HLA-DQ: DQA1_0101-DQB1_0501, DQA1_0301-DQB1_0302
# HLA-DP: DPA1_0103-DPB1_0201, DPA1_0201-DPB1_0101
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Test all scripts with sample data
python scripts/peptide_prediction.py --input examples/data/peptides.txt --allele DRB1_0101 --summary
python scripts/protein_analysis.py --input examples/data/protein.fsa --allele DRB1_0101 --context --summary
python scripts/custom_allele_prediction.py --input examples/data/peptides.txt --beta-seq examples/data/beta_chain.fsa --summary
python scripts/batch_multi_allele.py --input examples/data/peptides.txt --alleles DRB1_0101,DRB1_1501 --summary

# Test MCP server
python test_server.py
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py

# Test individual tools
python -c "
from src.server import mcp
result = mcp.call_tool('predict_peptide_binding', {
    'peptides': 'AAAGAEAGKATTE',
    'allele': 'DRB1_0101',
    'summary': True
})
print(result)
"
```

### Performance Monitoring

```bash
# Monitor job execution
tail -f jobs/*/job.log

# Check server resource usage
ps aux | grep "server.py"

# Monitor temp directory
du -sh /tmp/netmhc*
```

---

## License

Based on NetMHCIIpan-4.3 (Academic License). For commercial use, obtain NetMHCIIpan license from DTU Bioinformatics.

## Credits

- **NetMHCIIpan-4.3**: [DTU Bioinformatics](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
- **Original Repository**: [netMHCIIpan-4.3 Distribution](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
- **MCP Framework**: [Anthropic MCP](https://github.com/modelcontextprotocol)
- **FastMCP**: [FastMCP](https://github.com/jlowin/fastmcp)

## Support

For issues with this MCP implementation, please check:
1. [Troubleshooting section](#troubleshooting) above
2. Verify all file paths and permissions
3. Test with provided example data
4. Check job logs for detailed error information

For NetMHCIIpan-specific questions, refer to the [official documentation](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/).
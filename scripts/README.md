# MCP Scripts - NetMHCIIpan Tools

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Overview

This directory contains four clean scripts extracted from the verified use cases in Step 4. These scripts have been optimized for MCP wrapping with minimal dependencies, consistent interfaces, and proper error handling.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (standard library + optional pandas for Excel)
2. **Self-Contained**: Utility functions inlined in `scripts/lib/` to reduce external dependencies
3. **Configurable**: Parameters externalized to `configs/` directory, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping
5. **Consistent Interface**: All scripts follow the same pattern for arguments and return values

## Scripts

| Script | Description | Repo Dependent | Config | MCP Function |
|--------|-------------|----------------|--------|--------------|
| `peptide_prediction.py` | Predict MHC II binding for peptides | Yes (binary) | `configs/peptide_prediction_config.json` | `run_peptide_prediction()` |
| `protein_analysis.py` | Analyze protein sequences for binding regions | Yes (binary) | `configs/protein_analysis_config.json` | `run_protein_analysis()` |
| `custom_allele_prediction.py` | Predict binding using custom MHC sequences | Yes (binary) | `configs/custom_allele_config.json` | `run_custom_allele_prediction()` |
| `batch_multi_allele.py` | Batch predictions across multiple alleles | Yes (binary) + pandas (optional) | `configs/batch_multi_allele_config.json` | `run_batch_multi_allele()` |

## Dependencies Summary

### Essential Dependencies (All Scripts)
- Standard library: `argparse`, `subprocess`, `sys`, `os`, `pathlib`, `tempfile`, `json`
- No external Python packages required for core functionality

### Optional Dependencies
- `pandas` + `openpyxl`: Required only for Excel output in `batch_multi_allele.py`

### Repo Dependencies
- **NetMHCIIpan Binary**: All scripts require the `repo/netMHCIIpan-4.3/netMHCIIpan` executable
- **Auto-detection**: Scripts automatically locate the binary in common paths

## Shared Library (`scripts/lib/`)

Common functions are organized in the `scripts/lib/` directory:

- **`utils.py`**: File I/O utilities (temp files, validation, cleanup)
- **`netmhciipan.py`**: NetMHCIIpan tool wrapper with unified interface
- **`parsers.py`**: Output parsing and summary report generation

**Total Functions**: 12 shared functions to minimize code duplication

## Usage Examples

### Basic Peptide Prediction
```bash
# Activate environment
mamba activate ./env  # or: conda activate ./env

# Predict from file
python scripts/peptide_prediction.py --input examples/data/peptides.txt --allele DRB1_0101

# Predict from command line
python scripts/peptide_prediction.py --peptides AAAGAEAGKATTE,AALAAAAGVPPADKY --allele DRB1_0101

# With custom config and summary
python scripts/peptide_prediction.py --input examples/data/peptides.txt --config configs/peptide_prediction_config.json --summary
```

### Protein Sequence Analysis
```bash
# Context-aware analysis
python scripts/protein_analysis.py --input examples/data/protein.fsa --allele DRB1_0101 --context

# With summary and sorted output
python scripts/protein_analysis.py --input examples/data/protein.fsa --allele DRB1_0101 --summary --sorted
```

### Custom MHC Allele Prediction
```bash
# Using alpha and beta chains
python scripts/custom_allele_prediction.py --input examples/data/peptides.txt --alpha-seq examples/data/alpha_chain.fsa --beta-seq examples/data/beta_chain.fsa

# Beta chain only
python scripts/custom_allele_prediction.py --peptides AAAGAEAGKATTE --beta-seq examples/data/beta_chain.fsa
```

### Batch Multi-Allele Processing
```bash
# CSV output
python scripts/batch_multi_allele.py --input examples/data/peptides.txt --alleles DRB1_0101,DRB1_1501 --output results/batch.csv

# Excel output (requires pandas)
python scripts/batch_multi_allele.py --input examples/data/peptides.txt --alleles DRB1_0101,DRB1_1501 --output results/batch.xlsx --excel
```

## Configuration Files

Each script supports external configuration via JSON files in `configs/`:

```bash
# Using custom configuration
python scripts/peptide_prediction.py --input FILE --config configs/my_custom_config.json
```

See `configs/README.md` for configuration file formats and options.

## For MCP Wrapping (Step 6)

Each script exports a main function that can be directly wrapped as MCP tools:

```python
from scripts.peptide_prediction import run_peptide_prediction

# In MCP tool:
@mcp.tool()
def predict_peptide_binding(input_file: str, allele: str = "DRB1_0101", output_file: str = None):
    """Predict MHC II binding for peptides."""
    return run_peptide_prediction(input_file, allele=allele, output_file=output_file)
```

## Return Value Format

All main functions return a consistent dictionary format:

```python
{
    "result": {
        "strong_binders": [...],      # List of strong binders
        "weak_binders": [...],        # List of weak binders
        "all_predictions": [...],     # All predictions
        "summary": {...}              # Summary statistics
    },
    "raw_output": "...",             # Raw NetMHCIIpan output
    "output_file": "/path/to/file",  # Saved output file (if any)
    "metadata": {...}                # Execution metadata
}
```

## Environment Setup

```bash
# Ensure mamba/conda environment is activated
mamba activate ./env  # or: conda activate ./env

# Verify NetMHCIIpan is accessible
ls repo/netMHCIIpan-4.3/netMHCIIpan

# Test scripts
python scripts/peptide_prediction.py --help
```

## Testing

All scripts have been tested with the example data:

```bash
# Test all scripts
python scripts/peptide_prediction.py --input examples/data/peptides.txt --allele DRB1_0101 --summary
python scripts/protein_analysis.py --input examples/data/protein.fsa --allele DRB1_0101 --context --summary
python scripts/custom_allele_prediction.py --input examples/data/peptides.txt --beta-seq examples/data/beta_chain.fsa --summary
python scripts/batch_multi_allele.py --input examples/data/peptides.txt --alleles DRB1_0101,DRB1_1501 --output results/test.csv --summary
```

## Error Handling

- **File validation**: Input files are validated before processing
- **Graceful failures**: Missing tools or files produce helpful error messages
- **Cleanup**: Temporary files are automatically cleaned up
- **Consistent errors**: All scripts use consistent error reporting

## Performance Notes

- **Binary dependency**: All scripts require the NetMHCIIpan binary from `repo/`
- **Memory usage**: Minimal memory footprint, suitable for server deployment
- **Execution time**: Depends on NetMHCIIpan tool performance
- **Batch processing**: Multi-allele script processes alleles sequentially (can be parallelized)
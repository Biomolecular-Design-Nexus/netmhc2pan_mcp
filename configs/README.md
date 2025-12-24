# Configuration Files for NetMHCIIpan Scripts

This directory contains JSON configuration files for customizing the behavior of NetMHCIIpan MCP scripts.

## Configuration Files

| File | Script | Description |
|------|--------|-------------|
| `default_config.json` | All scripts | Global defaults and common settings |
| `peptide_prediction_config.json` | `peptide_prediction.py` | Peptide binding prediction settings |
| `protein_analysis_config.json` | `protein_analysis.py` | Protein analysis parameters |
| `custom_allele_config.json` | `custom_allele_prediction.py` | Custom MHC allele settings |
| `batch_multi_allele_config.json` | `batch_multi_allele.py` | Batch processing configuration |

## Usage

### Using Configuration Files

```bash
# Use specific config file
python scripts/peptide_prediction.py --input FILE --config configs/peptide_prediction_config.json

# Override specific parameters (config file + command line)
python scripts/peptide_prediction.py --input FILE --config configs/my_config.json --allele DRB1_1501
```

### Configuration Hierarchy

1. **Default values**: Built into each script
2. **Config file**: JSON configuration file (if specified)
3. **Command line**: Command line arguments override config file values

## Configuration Format

All configuration files use JSON format with the following structure:

```json
{
  "_description": "Description of this configuration",
  "_source": "Original source or use case",
  "_use_case": "Related use case identifier",

  "parameter_name": "value",
  "nested_object": {
    "sub_parameter": "value"
  }
}
```

### Meta Fields

- `_description`: Human-readable description
- `_source`: Original source file or use case
- `_use_case`: Related use case identifier
- `_created`: Creation date
- `_version`: Configuration version

These meta fields are ignored by scripts and are for documentation purposes only.

## Common Parameters

### NetMHCIIpan Settings

```json
{
  "allele": "DRB1_0101",           // Default MHC allele
  "input_type": "peptide",         // "peptide" or "protein"
  "context": false,                // Context-aware prediction
  "terminal_anchor": false,        // Terminal anchor consideration
  "sorted_output": false           // Sort by binding affinity
}
```

### Output Settings

```json
{
  "output_format": "text",         // "text", "csv", "excel"
  "verbose": true,                 // Show detailed output
  "include_summary": true,         // Include summary statistics
  "save_raw_output": true          // Save raw NetMHCIIpan output
}
```

### Validation Settings

```json
{
  "min_peptide_length": 9,         // Minimum peptide length
  "max_peptide_length": 30,        // Maximum peptide length
  "validate_sequences": true,      // Validate amino acid sequences
  "allowed_amino_acids": "ACDEFGHIKLMNPQRSTVWY"
}
```

## Script-Specific Configurations

### Peptide Prediction (`peptide_prediction_config.json`)

Focus on peptide-specific parameters:

```json
{
  "allele": "DRB1_0101",
  "input_type": "peptide",
  "output_format": "text",
  "validation": {
    "min_peptide_length": 9,
    "max_peptide_length": 30
  },
  "netmhciipan_options": {
    "input_type_flag": "1"
  }
}
```

### Protein Analysis (`protein_analysis_config.json`)

Protein-specific analysis options:

```json
{
  "allele": "DRB1_0101",
  "input_type": "protein",
  "context": false,
  "terminal_anchor": false,
  "sorted_output": false,
  "analysis_options": {
    "context_aware": {
      "enabled": false,
      "window_size": 15
    }
  },
  "summary": {
    "show_strong_binders": true,
    "max_displayed_binders": 10
  }
}
```

### Custom Allele (`custom_allele_config.json`)

Custom MHC sequence settings:

```json
{
  "input_type": "peptide",
  "use_alpha_chain": true,
  "use_beta_chain": true,
  "custom_allele_options": {
    "alpha_chain": {
      "required": false,
      "format": "fasta"
    },
    "beta_chain": {
      "required": true,
      "format": "fasta"
    }
  },
  "validation": {
    "min_chain_length": 100,
    "max_chain_length": 500
  }
}
```

### Batch Multi-Allele (`batch_multi_allele_config.json`)

Batch processing and multi-allele settings:

```json
{
  "input_type": "peptide",
  "output_format": "csv",
  "batch_processing": {
    "continue_on_error": true,
    "max_retries_per_allele": 2,
    "timeout_per_allele": 300
  },
  "allele_sets": {
    "common_hla_dr": ["DRB1_0101", "DRB1_0301", "DRB1_0401"],
    "test_set": ["DRB1_0101", "DRB1_1501"]
  },
  "output_formats": {
    "csv": {
      "enabled": true,
      "include_header": true
    },
    "excel": {
      "enabled": false,
      "requires_pandas": true
    }
  }
}
```

## Creating Custom Configurations

### Basic Custom Config

Create a new JSON file with your desired settings:

```json
{
  "_description": "My custom configuration",
  "_created": "2025-12-21",

  "allele": "DQB1_0602",
  "context": true,
  "output_format": "csv",
  "verbose": false
}
```

### Extending Default Config

Start with an existing config file and modify as needed:

1. Copy an existing config file
2. Modify the parameters you want to change
3. Update the `_description` field
4. Use with `--config` parameter

### Parameter Override

You can override any config parameter via command line:

```bash
# Config file sets allele to DRB1_0101, but override to DRB1_1501
python scripts/peptide_prediction.py --config my_config.json --allele DRB1_1501
```

## Validation

Configuration files are validated when loaded:

- Required parameters must be present
- Parameter types must match expected types
- File paths are validated for existence
- Invalid configurations produce helpful error messages

## Default Values

If no configuration file is specified, scripts use built-in defaults:

- **Allele**: DRB1_0101
- **Input Type**: peptide
- **Context**: false
- **Output Format**: text
- **Verbose**: true

See `default_config.json` for complete default values.

## Examples

### Research Configuration

For systematic research with multiple alleles:

```json
{
  "_description": "Research configuration for systematic MHC analysis",

  "batch_processing": {
    "continue_on_error": true,
    "max_retries_per_allele": 3
  },
  "output_format": "excel",
  "include_summary": true,
  "verbose": false
}
```

### Production Configuration

For production/service use:

```json
{
  "_description": "Production configuration for MCP service",

  "verbose": false,
  "output_format": "json",
  "timeout_seconds": 60,
  "validation": {
    "strict": true
  }
}
```

### Debug Configuration

For debugging and development:

```json
{
  "_description": "Debug configuration with verbose output",

  "verbose": true,
  "save_intermediate_files": true,
  "include_raw_output": true,
  "output_format": "text"
}
```
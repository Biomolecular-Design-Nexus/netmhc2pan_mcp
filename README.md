# NetMHCIIpan MCP

**MHC Class II binding prediction using NetMHCIIpan-4.3 via Docker**

An MCP (Model Context Protocol) server for MHC Class II peptide binding prediction and immunogenicity assessment with 18 tools:
- **predict_peptide_binding** -- Predict MHC II binding for peptides
- **analyze_protein_sequence** -- Map immunogenic epitope regions in proteins
- **predict_custom_mhc_binding** -- Binding prediction with custom alpha/beta chains
- **predict_binding_affinity** -- Multi-allele binding screening
- **submit_peptide_prediction / submit_protein_analysis / submit_custom_mhc_prediction** -- Async job submission
- **submit_batch_multi_allele_screening / submit_large_peptide_screening / submit_multi_allele_screening** -- Batch processing
- **get_job_status / get_job_result / get_job_log / cancel_job / list_jobs** -- Job management
- **export_predictions_to_excel** -- Export results to Excel format
- **analyze_netmhcpan_output** -- Parse raw NetMHCIIpan output
- **get_server_info** -- Server capabilities and supported alleles

## Quick Start with Docker

### Approach 1: Pull Pre-built Image from GitHub

The fastest way to get started. A pre-built Docker image is automatically published to GitHub Container Registry on every release.

```bash
# Pull the latest image
docker pull ghcr.io/macromnex/netmhc2pan_mcp:latest

# Register with Claude Code (runs as current user to avoid permission issues)
claude mcp add netmhc2pan_mcp -- docker run -i --rm --user `id -u`:`id -g` -v `pwd`:`pwd` ghcr.io/macromnex/netmhc2pan_mcp:latest
```

**Note:** Run from your project directory. `` `pwd` `` expands to the current working directory.

**Requirements:**
- Docker
- Claude Code installed

That's it! The NetMHCIIpan MCP server is now available in Claude Code.

---

### Approach 2: Build Docker Image Locally

Build the image yourself and install it into Claude Code. Useful for customization or offline environments.

```bash
# Clone the repository
git clone https://github.com/MacromNex/netmhc2pan_mcp.git
cd netmhc2pan_mcp

# Build the Docker image
docker build -t netmhc2pan_mcp:latest .

# Register with Claude Code (runs as current user to avoid permission issues)
claude mcp add netmhc2pan_mcp -- docker run -i --rm --user `id -u`:`id -g` -v `pwd`:`pwd` netmhc2pan_mcp:latest
```

**About the Docker Flags:**
- `-i` -- Interactive mode for Claude Code
- `--rm` -- Automatically remove container after exit
- `` --user `id -u`:`id -g` `` -- Runs the container as your current user
- `-v` -- Mounts your project directory

---

## Verify Installation

```bash
claude mcp list
# You should see 'netmhc2pan_mcp' in the output
```

In Claude Code, you can now use all 18 tools:
- `predict_peptide_binding`, `analyze_protein_sequence`, `predict_custom_mhc_binding`, `predict_binding_affinity`
- `submit_peptide_prediction`, `submit_protein_analysis`, `submit_custom_mhc_prediction`
- `submit_batch_multi_allele_screening`, `submit_large_peptide_screening`, `submit_multi_allele_screening`
- `get_job_status`, `get_job_result`, `get_job_log`, `cancel_job`, `list_jobs`
- `export_predictions_to_excel`, `analyze_netmhcpan_output`, `get_server_info`

---

## Next Steps

- **Detailed documentation**: See [detail.md](detail.md) for comprehensive guides including local installation, script usage, configuration files, demo data, allele lists, and troubleshooting

---

## Usage Examples

### Predict Peptide Binding to MHC II

```
Use predict_peptide_binding with peptides "AAAGAEAGKATTE,AALAAAAGVPPADKY" for allele DRB1_0101 and include summary statistics
```

### Map Protein Epitopes

```
Run analyze_protein_sequence on @my_protein.fasta using allele DRB1_0101 with context-aware prediction enabled
```

### Population Coverage Screening

```
Run predict_binding_affinity on @peptides.txt across alleles "DRB1_0101,DRB1_0301,DRB1_1501" and generate Excel output
```

---

## Troubleshooting

### Docker Issues

**Problem:** Container not found or pull fails
```bash
# Verify Docker is running
docker info

# Pull with explicit tag
docker pull ghcr.io/macromnex/netmhc2pan_mcp:latest
```

**Problem:** Permission denied on output files
```bash
# Ensure you're using the --user flag
docker run -i --rm --user `id -u`:`id -g` -v `pwd`:`pwd` ghcr.io/macromnex/netmhc2pan_mcp:latest
```

**Problem:** MCP server not responding
```bash
# Re-register with Claude Code
claude mcp remove netmhc2pan_mcp
claude mcp add netmhc2pan_mcp -- docker run -i --rm --user `id -u`:`id -g` -v `pwd`:`pwd` ghcr.io/macromnex/netmhc2pan_mcp:latest
```

**Problem:** File paths not found inside container
```bash
# Make sure to run Claude Code from the directory containing your files
# The -v `pwd`:`pwd` flag mounts only the current directory
cd /path/to/your/project
claude
```

**Problem:** NetMHCIIpan binary errors inside container
```bash
# Test the container directly
docker run --rm ghcr.io/macromnex/netmhc2pan_mcp:latest --help

# If the binary fails, rebuild the image
docker build --no-cache -t netmhc2pan_mcp:latest .
```

---

## License

Academic License -- Based on NetMHCIIpan-4.3 by DTU Bioinformatics. For commercial use, obtain a license from [DTU Health Tech](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/).

## Credits

- **NetMHCIIpan-4.3**: Original software by [DTU Bioinformatics](https://services.healthtech.dtu.dk/services/NetMHCIIpan-4.3/)
- **MCP Integration**: Built with FastMCP framework

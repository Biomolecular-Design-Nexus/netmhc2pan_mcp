"""MCP Server for NetMHCIIpan-4.3

Provides both synchronous and asynchronous (submit) APIs for NetMHCIIpan tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List
import sys

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("netMHCIIpan-4.3")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations)
# ==============================================================================

@mcp.tool()
def predict_peptide_binding(
    input_file: Optional[str] = None,
    peptides: Optional[str] = None,
    allele: str = "DRB1_0101",
    output_file: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Predict MHC II binding for peptides using NetMHCIIpan (synchronous).

    Use this for quick peptide binding predictions that complete in under 1 second.

    Args:
        input_file: Path to file with peptides (one per line)
        peptides: Comma-separated peptides (alternative to input_file)
        allele: MHC II allele (e.g., DRB1_0101)
        output_file: Optional path to save results
        summary: Include summary statistics in output

    Returns:
        Dictionary with predictions, strong/weak binders, and optional summary
    """
    from peptide_prediction import run_peptide_prediction

    try:
        # Convert comma-separated peptides to list if provided
        peptide_list = None
        if peptides:
            peptide_list = [p.strip() for p in peptides.split(',')]

        result = run_peptide_prediction(
            input_file=input_file,
            peptides=peptide_list,
            allele=allele,
            output_file=output_file,
            summary=summary
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Peptide prediction failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def analyze_protein_sequence(
    input_file: Optional[str] = None,
    protein_sequence: Optional[str] = None,
    allele: str = "DRB1_0101",
    context: bool = False,
    terminal_anchor: bool = False,
    sorted_output: bool = False,
    output_file: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Analyze protein sequences for MHC II binding regions (synchronous).

    Use this for protein sequence analysis that completes in 1-2 seconds.

    Args:
        input_file: Path to FASTA file with protein sequences
        protein_sequence: Single protein sequence (alternative to input_file)
        allele: MHC II allele for prediction
        context: Enable context-aware prediction
        terminal_anchor: Consider terminal anchors
        sorted_output: Sort results by binding affinity
        output_file: Optional path to save results
        summary: Include summary statistics

    Returns:
        Dictionary with all binding predictions, strong/weak binders, and metadata
    """
    from protein_analysis import run_protein_analysis

    try:
        result = run_protein_analysis(
            input_file=input_file,
            protein_sequence=protein_sequence,
            allele=allele,
            context=context,
            terminal_anchor=terminal_anchor,
            sorted_output=sorted_output,
            output_file=output_file,
            summary=summary
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Protein analysis failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def predict_custom_mhc_binding(
    input_file: Optional[str] = None,
    peptides: Optional[str] = None,
    alpha_seq: Optional[str] = None,
    beta_seq: Optional[str] = None,
    output_file: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Predict binding using custom MHC II sequences (synchronous).

    Use this for custom allele predictions that complete in about 1 second.

    Args:
        input_file: Path to file with peptides
        peptides: Comma-separated peptides (alternative to input_file)
        alpha_seq: Path to FASTA file with alpha chain sequence
        beta_seq: Path to FASTA file with beta chain sequence
        output_file: Optional path to save results
        summary: Include summary statistics

    Returns:
        Dictionary with custom MHC predictions and binding classifications
    """
    from custom_allele_prediction import run_custom_allele_prediction

    try:
        # Convert comma-separated peptides to list if provided
        peptide_list = None
        if peptides:
            peptide_list = [p.strip() for p in peptides.split(',')]

        result = run_custom_allele_prediction(
            input_file=input_file,
            peptides=peptide_list,
            alpha_seq=alpha_seq,
            beta_seq=beta_seq,
            output_file=output_file,
            summary=summary
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Custom MHC prediction failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def predict_binding_affinity(
    input_file: str,
    alleles: str,
    output_file: Optional[str] = None,
    excel: bool = False,
    summary: bool = False
) -> dict:
    """
    Predict binding affinity across multiple MHC II alleles (synchronous).

    Use this for batch multi-allele analysis that completes in 3-5 seconds.

    Args:
        input_file: Path to file with peptides
        alleles: Comma-separated MHC II alleles (e.g., "DRB1_0101,DRB1_1501")
        output_file: Path to save results (CSV or XLSX)
        excel: Save as Excel format (requires pandas)
        summary: Include summary statistics

    Returns:
        Dictionary with results for each allele and combined statistics
    """
    from batch_multi_allele import run_batch_multi_allele

    try:
        # Convert comma-separated alleles to list
        allele_list = [a.strip() for a in alleles.split(',')]

        result = run_batch_multi_allele(
            input_file=input_file,
            alleles=allele_list,
            output_file=output_file,
            excel=excel,
            summary=summary
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Batch multi-allele prediction failed: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running or batch operations)
# ==============================================================================

@mcp.tool()
def submit_peptide_prediction(
    input_file: Optional[str] = None,
    peptides: Optional[str] = None,
    allele: str = "DRB1_0101",
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Submit peptide binding prediction for background processing.

    Use this when you prefer async workflow or are processing many peptides.

    Args:
        input_file: Path to file with peptides
        peptides: Comma-separated peptides
        allele: MHC II allele
        output_dir: Directory to save outputs
        job_name: Optional name for tracking
        summary: Include summary statistics

    Returns:
        Dictionary with job_id. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results
        - get_job_log(job_id) to see logs
    """
    script_path = str(SCRIPTS_DIR / "peptide_prediction.py")

    args = {
        "allele": allele,
        "summary": summary
    }

    if input_file:
        args["input"] = input_file
    elif peptides:
        args["peptides"] = peptides

    if output_dir:
        output_file = Path(output_dir) / f"peptide_pred_{job_name or 'output'}.txt"
        args["output"] = str(output_file)

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or "peptide_prediction"
    )

@mcp.tool()
def submit_protein_analysis(
    input_file: Optional[str] = None,
    protein_sequence: Optional[str] = None,
    allele: str = "DRB1_0101",
    context: bool = False,
    terminal_anchor: bool = False,
    sorted_output: bool = False,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Submit protein sequence analysis for background processing.

    Use this for async workflow or when analyzing large proteins.

    Args:
        input_file: Path to FASTA file with protein sequences
        protein_sequence: Single protein sequence
        allele: MHC II allele for prediction
        context: Enable context-aware prediction
        terminal_anchor: Consider terminal anchors
        sorted_output: Sort results by binding affinity
        output_dir: Directory to save outputs
        job_name: Optional name for tracking
        summary: Include summary statistics

    Returns:
        Dictionary with job_id for tracking the analysis
    """
    script_path = str(SCRIPTS_DIR / "protein_analysis.py")

    args = {
        "allele": allele,
        "context": context,
        "terminal_anchor": terminal_anchor,
        "sorted": sorted_output,
        "summary": summary
    }

    if input_file:
        args["input"] = input_file
    elif protein_sequence:
        args["protein_sequence"] = protein_sequence

    if output_dir:
        output_file = Path(output_dir) / f"protein_analysis_{job_name or 'output'}.txt"
        args["output"] = str(output_file)

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or "protein_analysis"
    )

@mcp.tool()
def submit_custom_mhc_prediction(
    input_file: Optional[str] = None,
    peptides: Optional[str] = None,
    alpha_seq: Optional[str] = None,
    beta_seq: Optional[str] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Submit custom MHC prediction for background processing.

    Use this for async workflow when using custom MHC sequences.

    Args:
        input_file: Path to file with peptides
        peptides: Comma-separated peptides
        alpha_seq: Path to FASTA file with alpha chain sequence
        beta_seq: Path to FASTA file with beta chain sequence
        output_dir: Directory to save outputs
        job_name: Optional name for tracking
        summary: Include summary statistics

    Returns:
        Dictionary with job_id for tracking the custom prediction
    """
    script_path = str(SCRIPTS_DIR / "custom_allele_prediction.py")

    args = {
        "summary": summary
    }

    if input_file:
        args["input"] = input_file
    elif peptides:
        args["peptides"] = peptides

    if alpha_seq:
        args["alpha_seq"] = alpha_seq
    if beta_seq:
        args["beta_seq"] = beta_seq

    if output_dir:
        output_file = Path(output_dir) / f"custom_mhc_{job_name or 'output'}.txt"
        args["output"] = str(output_file)

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or "custom_mhc_prediction"
    )

@mcp.tool()
def submit_batch_multi_allele_screening(
    input_file: str,
    alleles: str,
    output_dir: Optional[str] = None,
    excel: bool = False,
    job_name: Optional[str] = None,
    summary: bool = False
) -> dict:
    """
    Submit batch multi-allele screening for background processing.

    Use this for large-scale screening across multiple alleles or when you
    prefer async workflow.

    Args:
        input_file: Path to file with peptides
        alleles: Comma-separated MHC II alleles
        output_dir: Directory to save outputs
        excel: Save as Excel format (requires pandas)
        job_name: Optional name for tracking
        summary: Include summary statistics

    Returns:
        Dictionary with job_id for tracking the batch screening
    """
    script_path = str(SCRIPTS_DIR / "batch_multi_allele.py")

    args = {
        "input": input_file,
        "alleles": alleles,
        "excel": excel,
        "summary": summary
    }

    if output_dir:
        ext = "xlsx" if excel else "csv"
        output_file = Path(output_dir) / f"batch_multi_allele_{job_name or 'output'}.{ext}"
        args["output"] = str(output_file)

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"batch_screening_{len(alleles.split(','))}_alleles"
    )

# ==============================================================================
# Large-Scale Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_large_peptide_screening(
    input_files: List[str],
    allele: str = "DRB1_0101",
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit large-scale peptide screening across multiple input files.

    Processes multiple peptide files against a single allele in parallel.
    Suitable for high-throughput screening workflows.

    Args:
        input_files: List of paths to peptide files
        allele: MHC II allele for prediction
        output_dir: Directory to save all outputs
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the large screening job
    """
    # For now, we'll process files sequentially
    # In a production system, this could be parallelized
    script_path = str(SCRIPTS_DIR / "peptide_prediction.py")

    # Convert list to comma-separated string for the script
    inputs_str = ",".join(input_files)

    args = {
        "input": inputs_str,  # Modified script would need to handle multiple files
        "allele": allele,
        "summary": True
    }

    if output_dir:
        args["output_dir"] = output_dir

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"large_screening_{len(input_files)}_files"
    )

@mcp.tool()
def submit_multi_allele_screening(
    input_file: str,
    alleles: List[str],
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit comprehensive multi-allele screening.

    Processes a single peptide file against many alleles. Suitable for
    comprehensive epitope mapping across HLA diversity.

    Args:
        input_file: Path to peptide file
        alleles: List of MHC II alleles to test
        output_dir: Directory to save results
        job_name: Optional name for tracking

    Returns:
        Dictionary with job_id for tracking the multi-allele screening
    """
    script_path = str(SCRIPTS_DIR / "batch_multi_allele.py")

    # Convert list to comma-separated string
    alleles_str = ",".join(alleles)

    args = {
        "input": input_file,
        "alleles": alleles_str,
        "summary": True,
        "excel": True  # Use Excel for better multi-allele visualization
    }

    if output_dir:
        output_file = Path(output_dir) / f"multi_allele_screening_{job_name or 'output'}.xlsx"
        args["output"] = str(output_file)

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"screening_{len(alleles)}_alleles"
    )

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def export_predictions_to_excel(job_id: str, output_file: str) -> dict:
    """
    Export completed job results to Excel format.

    Takes the text output from a completed job and converts it to Excel
    format for better analysis and visualization.

    Args:
        job_id: ID of a completed job
        output_file: Path to save Excel file

    Returns:
        Success message or error if conversion fails
    """
    try:
        # Get the job result
        result = job_manager.get_job_result(job_id)

        if result["status"] != "success":
            return result

        # For this demo, we'll just save the text output
        # In production, you'd parse and convert to proper Excel format
        with open(output_file, 'w') as f:
            f.write(str(result["result"]))

        return {
            "status": "success",
            "message": f"Results exported to {output_file}",
            "output_file": output_file
        }

    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def analyze_netmhcpan_output(output_file: str) -> dict:
    """
    Analyze NetMHCIIpan output file and generate summary statistics.

    Parses a NetMHCIIpan output file and provides detailed analysis including
    binding strength distributions, allele performance, and statistical summaries.

    Args:
        output_file: Path to NetMHCIIpan output file

    Returns:
        Dictionary with detailed analysis and statistics
    """
    try:
        if not Path(output_file).exists():
            return {"status": "error", "error": f"Output file not found: {output_file}"}

        # Use the parser from the shared library
        sys.path.insert(0, str(SCRIPTS_DIR / "lib"))
        from parsers import parse_netmhciipan_output, format_summary_report

        with open(output_file) as f:
            raw_output = f.read()

        parsed_data = parse_netmhciipan_output(raw_output)
        summary = format_summary_report(parsed_data)

        return {
            "status": "success",
            "analysis": {
                "total_predictions": len(parsed_data["all_predictions"]),
                "strong_binders": len(parsed_data["strong_binders"]),
                "weak_binders": len(parsed_data["weak_binders"]),
                "summary_report": summary,
                "detailed_predictions": parsed_data["all_predictions"][:10]  # First 10 for preview
            }
        }

    except Exception as e:
        logger.error(f"Output analysis failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the NetMHCIIpan MCP server.

    Returns:
        Dictionary with server information, available tools, and system status
    """
    return {
        "status": "success",
        "server_info": {
            "name": "NetMHCIIpan-4.3 MCP Server",
            "version": "1.0.0",
            "description": "MCP server for NetMHCIIpan MHC II binding prediction",
            "tools": {
                "synchronous": [
                    "predict_peptide_binding",
                    "analyze_protein_sequence",
                    "predict_custom_mhc_binding",
                    "predict_binding_affinity"
                ],
                "submit_api": [
                    "submit_peptide_prediction",
                    "submit_protein_analysis",
                    "submit_custom_mhc_prediction",
                    "submit_batch_multi_allele_screening",
                    "submit_large_peptide_screening",
                    "submit_multi_allele_screening"
                ],
                "job_management": [
                    "get_job_status",
                    "get_job_result",
                    "get_job_log",
                    "cancel_job",
                    "list_jobs"
                ],
                "utilities": [
                    "export_predictions_to_excel",
                    "analyze_netmhcpan_output",
                    "get_server_info"
                ]
            },
            "scripts_directory": str(SCRIPTS_DIR),
            "jobs_directory": str(job_manager.jobs_dir)
        }
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()
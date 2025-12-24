"""
NetMHCIIpan tool wrapper utilities.

This module provides a centralized way to locate and run the NetMHCIIpan tool.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


def find_netmhciipan_path() -> Path:
    """
    Find the NetMHCIIpan executable.

    Returns:
        Path: Path to NetMHCIIpan executable

    Raises:
        FileNotFoundError: If NetMHCIIpan not found
    """
    # Try multiple potential locations
    script_dir = Path(__file__).parent.parent.parent
    potential_paths = [
        script_dir / "repo" / "netMHCIIpan-4.3" / "netMHCIIpan",
        Path("/usr/local/bin/netMHCIIpan"),
        Path("/opt/netMHCIIpan-4.3/netMHCIIpan"),
    ]

    for path in potential_paths:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"NetMHCIIpan executable not found. Checked locations: "
        f"{', '.join(str(p) for p in potential_paths)}"
    )


def run_netmhciipan(
    input_file: str,
    allele: str,
    input_type: str = "peptide",
    context: bool = False,
    terminal_anchor: bool = False,
    sorted_output: bool = False,
    alpha_seq: Optional[str] = None,
    beta_seq: Optional[str] = None,
    custom_seq: Optional[str] = None
) -> str:
    """
    Run NetMHCIIpan with specified parameters.

    Args:
        input_file: Path to input file
        allele: MHC allele name
        input_type: "peptide" or "protein"
        context: Enable context-aware prediction
        terminal_anchor: Consider terminal anchor contributions
        sorted_output: Sort results by binding affinity
        alpha_seq: Path to alpha chain sequence file
        beta_seq: Path to beta chain sequence file
        custom_seq: Path to custom HLA sequence file

    Returns:
        str: NetMHCIIpan output

    Raises:
        subprocess.CalledProcessError: If NetMHCIIpan fails
        FileNotFoundError: If NetMHCIIpan executable not found
    """
    netmhciipan_path = find_netmhciipan_path()

    # Build command
    cmd = [str(netmhciipan_path)]

    # Set input type
    if input_type == "peptide":
        cmd.extend(["-inptype", "1"])
    else:  # protein
        cmd.extend(["-inptype", "0"])

    # Add input file
    cmd.extend(["-f", input_file])

    # Add allele (if not using custom sequences)
    if not (alpha_seq or beta_seq or custom_seq):
        cmd.extend(["-a", allele])

    # Add context if requested
    if context:
        cmd.append("-context")

    # Add terminal anchor consideration
    if terminal_anchor:
        cmd.append("-termAcon")

    # Add sorted output
    if sorted_output:
        cmd.extend(["-s", "-u"])

    # Add custom sequence files
    if alpha_seq:
        cmd.extend(["-hlaseqA", alpha_seq])
    if beta_seq:
        cmd.extend(["-hlaseq", beta_seq])
    if custom_seq:
        cmd.extend(["-hlaseq", custom_seq])

    # Run NetMHCIIpan
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode,
            cmd,
            f"NetMHCIIpan failed: {e.stderr}"
        )
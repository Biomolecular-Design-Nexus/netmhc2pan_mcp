"""
Shared I/O utilities for NetMHCIIpan MCP scripts.

These functions are extracted and simplified from the use case scripts to avoid code duplication.
"""

import os
import tempfile
from pathlib import Path
from typing import Union, List, Optional


def create_temp_peptide_file(peptides: List[str]) -> str:
    """
    Create a temporary file with peptide sequences.

    Args:
        peptides: List of peptide sequences

    Returns:
        str: Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pep')
    for peptide in peptides:
        temp_file.write(f"{peptide} 0.000\n")
    temp_file.close()
    return temp_file.name


def create_temp_fasta_file(sequence: str, seq_name: str = "protein_seq") -> str:
    """
    Create a temporary FASTA file with protein sequence.

    Args:
        sequence: Protein sequence string
        seq_name: Sequence name for FASTA header

    Returns:
        str: Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.fsa')
    temp_file.write(f">{seq_name}\n{sequence}\n")
    temp_file.close()
    return temp_file.name


def safe_file_cleanup(file_path: Optional[str]) -> None:
    """
    Safely remove a temporary file.

    Args:
        file_path: Path to file to remove (can be None)
    """
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
        except OSError:
            pass  # Ignore cleanup errors


def validate_input_file(file_path: Union[str, Path]) -> Path:
    """
    Validate that an input file exists.

    Args:
        file_path: Path to input file

    Returns:
        Path: Validated path object

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path


def save_output(content: str, output_file: Union[str, Path]) -> None:
    """
    Save content to output file.

    Args:
        content: Content to save
        output_file: Output file path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(content)
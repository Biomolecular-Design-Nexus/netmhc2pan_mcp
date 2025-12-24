#!/usr/bin/env python3
"""
Script: custom_allele_prediction.py
Description: Predict binding using custom MHC sequences

Original Use Case: examples/use_case_3_custom_allele_prediction.py
Dependencies Removed: None (only standard library imports)

Usage:
    python scripts/custom_allele_prediction.py --input <input_file> --alpha-seq <alpha_file> --beta-seq <beta_file>

Example:
    python scripts/custom_allele_prediction.py --input examples/data/peptides.txt --alpha-seq examples/data/alpha_chain.fsa --beta-seq examples/data/beta_chain.fsa
    python scripts/custom_allele_prediction.py --peptides AAAGAEAGKATTE --beta-seq examples/data/beta_chain.fsa
"""

# ==============================================================================
# Minimal Imports (only standard library)
# ==============================================================================
import argparse
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json

# Add the lib directory to the path for our utilities
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from utils import create_temp_peptide_file, create_temp_fasta_file, validate_input_file, save_output, safe_file_cleanup
from netmhciipan import run_netmhciipan
from parsers import parse_netmhciipan_output, format_summary_report

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "input_type": "peptide",
    "output_format": "text",
    "use_alpha_chain": True,
    "use_beta_chain": True
}

# ==============================================================================
# Core Function
# ==============================================================================
def run_custom_allele_prediction(
    input_file: Optional[Union[str, Path]] = None,
    peptides: Optional[List[str]] = None,
    proteins: Optional[List[str]] = None,
    alpha_seq_file: Optional[Union[str, Path]] = None,
    beta_seq_file: Optional[Union[str, Path]] = None,
    combined_seq_file: Optional[Union[str, Path]] = None,
    input_type: str = "peptide",
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Predict binding using custom MHC sequences or alpha/beta chain combinations.

    Args:
        input_file: Path to input file (peptides or proteins)
        peptides: List of peptide sequences
        proteins: List of protein sequences
        alpha_seq_file: Path to alpha chain sequence file
        beta_seq_file: Path to beta chain sequence file
        combined_seq_file: Path to combined HLA sequence file
        input_type: "peptide" or "protein"
        output_file: Path to save output (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result (parsed predictions)
            - raw_output: Raw NetMHCIIpan output text
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata

    Example:
        >>> result = run_custom_allele_prediction(
        ...     input_file="examples/data/peptides.txt",
        ...     alpha_seq_file="examples/data/alpha_chain.fsa",
        ...     beta_seq_file="examples/data/beta_chain.fsa",
        ...     output_file="results/custom_predictions.txt"
        ... )
        >>> print(f"Found {len(result['result']['strong_binders'])} strong binders")
    """
    # Setup configuration
    final_config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    input_type = final_config.get("input_type", input_type)

    # Validate inputs
    if not any([input_file, peptides, proteins]):
        raise ValueError("One of input_file, peptides, or proteins must be provided")

    if sum(bool(x) for x in [input_file, peptides, proteins]) > 1:
        raise ValueError("Only one input method can be specified")

    if not any([alpha_seq_file, beta_seq_file, combined_seq_file]):
        raise ValueError("At least one custom MHC sequence file must be provided")

    # Validate sequence files
    if alpha_seq_file:
        validate_input_file(alpha_seq_file)
    if beta_seq_file:
        validate_input_file(beta_seq_file)
    if combined_seq_file:
        validate_input_file(combined_seq_file)

    temp_file = None
    try:
        # Prepare input file
        if peptides:
            temp_file = create_temp_peptide_file(peptides)
            final_input_file = temp_file
            input_type = "peptide"
        elif proteins:
            # Create temporary file with multiple protein sequences
            temp_file_obj = create_temp_fasta_file("", "temp")  # Create temp file handle
            temp_file = temp_file_obj
            with open(temp_file, 'w') as f:
                for i, protein in enumerate(proteins):
                    f.write(f">protein_{i+1}\n{protein}\n")
            final_input_file = temp_file
            input_type = "protein"
        else:
            final_input_file = str(validate_input_file(input_file))

        # Run NetMHCIIpan with custom sequences
        raw_output = run_netmhciipan(
            input_file=final_input_file,
            allele="",  # Not used with custom sequences
            input_type=input_type,
            alpha_seq=str(alpha_seq_file) if alpha_seq_file else None,
            beta_seq=str(beta_seq_file) if beta_seq_file else None,
            custom_seq=str(combined_seq_file) if combined_seq_file else None
        )

        # Parse results
        parsed_results = parse_netmhciipan_output(raw_output)

        # Save output if requested
        output_path = None
        if output_file:
            output_path = Path(output_file)
            save_output(raw_output, output_path)

        return {
            "result": parsed_results,
            "raw_output": raw_output,
            "output_file": str(output_path) if output_path else None,
            "metadata": {
                "input_file": str(input_file) if input_file else None,
                "input_type": input_type,
                "peptides_count": len(peptides) if peptides else None,
                "proteins_count": len(proteins) if proteins else None,
                "alpha_seq_file": str(alpha_seq_file) if alpha_seq_file else None,
                "beta_seq_file": str(beta_seq_file) if beta_seq_file else None,
                "combined_seq_file": str(combined_seq_file) if combined_seq_file else None,
                "config": final_config
            }
        }

    finally:
        # Clean up temporary file
        safe_file_cleanup(temp_file)


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        help='Input file with peptides or proteins'
    )
    input_group.add_argument(
        '--peptides', '-p',
        help='Comma-separated list of peptides'
    )
    input_group.add_argument(
        '--proteins',
        help='Comma-separated list of protein sequences'
    )

    seq_group = parser.add_argument_group('MHC Sequences')
    seq_group.add_argument(
        '--alpha-seq',
        help='Alpha chain FASTA sequence file'
    )
    seq_group.add_argument(
        '--beta-seq', '--beta-seq-additional',
        help='Beta chain FASTA sequence file'
    )
    seq_group.add_argument(
        '--combined-seq',
        help='Combined MHC sequence FASTA file'
    )

    parser.add_argument(
        '--input-type',
        choices=['peptide', 'protein'],
        default='peptide',
        help='Input type (default: peptide)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (optional)'
    )
    parser.add_argument(
        '--config', '-c',
        help='Config file (JSON)'
    )
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Show summary of strong/weak binders'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show full NetMHCIIpan output'
    )

    args = parser.parse_args()

    try:
        # Validate that at least one sequence file is provided
        if not any([args.alpha_seq, args.beta_seq, args.combined_seq]):
            parser.error("At least one MHC sequence file (--alpha-seq, --beta-seq, or --combined-seq) must be provided")

        # Load config if provided
        config = None
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Prepare input data
        peptides = None
        proteins = None
        if args.peptides:
            peptides = [p.strip() for p in args.peptides.split(',')]
        elif args.proteins:
            proteins = [p.strip() for p in args.proteins.split(',')]

        # Run prediction
        result = run_custom_allele_prediction(
            input_file=args.input,
            peptides=peptides,
            proteins=proteins,
            alpha_seq_file=args.alpha_seq,
            beta_seq_file=args.beta_seq,
            combined_seq_file=args.combined_seq,
            input_type=args.input_type,
            output_file=args.output,
            config=config
        )

        # Print summary if requested
        if args.summary:
            summary_report = format_summary_report(result['result'])
            print(summary_report)

        # Print verbose output if requested or no output file
        if args.verbose or (not args.output and not args.summary):
            print("\n" + "="*80)
            print("NetMHCIIpan Raw Output:")
            print("="*80)
            print(result['raw_output'])

        # Print success message
        if result['output_file']:
            print(f"✅ Results saved to: {result['output_file']}")
        else:
            print("✅ Custom allele prediction completed successfully")

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
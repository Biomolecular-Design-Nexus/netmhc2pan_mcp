#!/usr/bin/env python3
"""
Script: peptide_prediction.py
Description: Predict MHC II binding for peptides using NetMHCIIpan

Original Use Case: examples/use_case_1_peptide_prediction.py
Dependencies Removed: None (only standard library imports)

Usage:
    python scripts/peptide_prediction.py --input <input_file> --allele <allele>

Example:
    python scripts/peptide_prediction.py --input examples/data/peptides.txt --allele DRB1_0101
    python scripts/peptide_prediction.py --peptides AAAGAEAGKATTE,AALAAAAGVPPADKY --allele DRB1_0101
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

from utils import create_temp_peptide_file, validate_input_file, save_output, safe_file_cleanup
from netmhciipan import run_netmhciipan
from parsers import parse_netmhciipan_output, format_summary_report

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "allele": "DRB1_0101",
    "input_type": "peptide",
    "output_format": "text",
    "verbose": True
}

# ==============================================================================
# Core Function
# ==============================================================================
def run_peptide_prediction(
    input_file: Optional[Union[str, Path]] = None,
    peptides: Optional[List[str]] = None,
    allele: str = "DRB1_0101",
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Predict MHC class II binding for peptides using NetMHCIIpan.

    Args:
        input_file: Path to input file containing peptides
        peptides: List of peptide sequences
        allele: MHC allele for prediction
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
        >>> result = run_peptide_prediction(
        ...     input_file="examples/data/peptides.txt",
        ...     allele="DRB1_0101",
        ...     output_file="results/predictions.txt"
        ... )
        >>> print(f"Found {len(result['result']['strong_binders'])} strong binders")
    """
    # Setup configuration
    final_config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    allele = final_config.get("allele", allele)

    # Validate inputs
    if not input_file and not peptides:
        raise ValueError("Either input_file or peptides must be provided")

    if input_file and peptides:
        raise ValueError("Cannot specify both input_file and peptides")

    temp_file = None
    try:
        # Prepare input file
        if peptides:
            temp_file = create_temp_peptide_file(peptides)
            final_input_file = temp_file
        else:
            final_input_file = str(validate_input_file(input_file))

        # Run NetMHCIIpan
        raw_output = run_netmhciipan(
            input_file=final_input_file,
            allele=allele,
            input_type="peptide"
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
                "peptides_count": len(peptides) if peptides else None,
                "allele": allele,
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
        help='Input file with peptides (one per line, optionally with scores)'
    )
    input_group.add_argument(
        '--peptides', '-p',
        help='Comma-separated list of peptides'
    )

    parser.add_argument(
        '--allele', '-a',
        default="DRB1_0101",
        help='MHC allele for prediction (default: DRB1_0101)'
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
        # Load config if provided
        config = None
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Prepare peptides list
        peptides = None
        if args.peptides:
            peptides = [p.strip() for p in args.peptides.split(',')]

        # Run prediction
        result = run_peptide_prediction(
            input_file=args.input,
            peptides=peptides,
            allele=args.allele,
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
            print("✅ Prediction completed successfully")

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
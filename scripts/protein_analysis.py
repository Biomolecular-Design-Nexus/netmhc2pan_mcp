#!/usr/bin/env python3
"""
Script: protein_analysis.py
Description: Analyze protein sequences for MHC II binding regions

Original Use Case: examples/use_case_2_protein_sequence_analysis.py
Dependencies Removed: None (only standard library imports)

Usage:
    python scripts/protein_analysis.py --input <input_file> --allele <allele>

Example:
    python scripts/protein_analysis.py --input examples/data/protein.fsa --allele DRB1_0101 --context
    python scripts/protein_analysis.py --sequence ASQKRPSQ... --allele DRB1_0101 --summary
"""

# ==============================================================================
# Minimal Imports (only standard library)
# ==============================================================================
import argparse
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any
import json

# Add the lib directory to the path for our utilities
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from utils import create_temp_fasta_file, validate_input_file, save_output, safe_file_cleanup
from netmhciipan import run_netmhciipan
from parsers import parse_netmhciipan_output, format_summary_report

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "allele": "DRB1_0101",
    "input_type": "protein",
    "context": False,
    "terminal_anchor": False,
    "sorted_output": False,
    "output_format": "text"
}

# ==============================================================================
# Core Function
# ==============================================================================
def run_protein_analysis(
    input_file: Optional[Union[str, Path]] = None,
    protein_sequence: Optional[str] = None,
    allele: str = "DRB1_0101",
    context: bool = False,
    terminal_anchor: bool = False,
    sorted_output: bool = False,
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze protein sequences for MHC class II binding regions using NetMHCIIpan.

    Args:
        input_file: Path to FASTA file containing protein sequences
        protein_sequence: Single protein sequence string
        allele: MHC allele for prediction
        context: Use context-aware prediction
        terminal_anchor: Consider terminal anchor contributions
        sorted_output: Sort results by binding affinity
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
        >>> result = run_protein_analysis(
        ...     input_file="examples/data/protein.fsa",
        ...     allele="DRB1_0101",
        ...     context=True,
        ...     output_file="results/analysis.txt"
        ... )
        >>> print(f"Found {len(result['result']['strong_binders'])} strong binders")
    """
    # Setup configuration
    final_config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    allele = final_config.get("allele", allele)
    context = final_config.get("context", context)
    terminal_anchor = final_config.get("terminal_anchor", terminal_anchor)
    sorted_output = final_config.get("sorted_output", sorted_output)

    # Validate inputs
    if not input_file and not protein_sequence:
        raise ValueError("Either input_file or protein_sequence must be provided")

    if input_file and protein_sequence:
        raise ValueError("Cannot specify both input_file and protein_sequence")

    temp_file = None
    try:
        # Prepare input file
        if protein_sequence:
            temp_file = create_temp_fasta_file(protein_sequence)
            final_input_file = temp_file
        else:
            final_input_file = str(validate_input_file(input_file))

        # Run NetMHCIIpan
        raw_output = run_netmhciipan(
            input_file=final_input_file,
            allele=allele,
            input_type="protein",
            context=context,
            terminal_anchor=terminal_anchor,
            sorted_output=sorted_output
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
                "protein_sequence_length": len(protein_sequence) if protein_sequence else None,
                "allele": allele,
                "context": context,
                "terminal_anchor": terminal_anchor,
                "sorted_output": sorted_output,
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
        help='Input FASTA file with protein sequences'
    )
    input_group.add_argument(
        '--sequence', '-s',
        help='Single protein sequence string'
    )

    parser.add_argument(
        '--allele', '-a',
        default="DRB1_0101",
        help='MHC allele for prediction (default: DRB1_0101)'
    )
    parser.add_argument(
        '--context', '-c',
        action='store_true',
        help='Use context-aware prediction'
    )
    parser.add_argument(
        '--terminal-anchor', '-t',
        action='store_true',
        help='Consider terminal anchor contributions'
    )
    parser.add_argument(
        '--sorted',
        action='store_true',
        help='Sort output by binding affinity'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (optional)'
    )
    parser.add_argument(
        '--config',
        help='Config file (JSON)'
    )
    parser.add_argument(
        '--summary',
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

        # Run analysis
        result = run_protein_analysis(
            input_file=args.input,
            protein_sequence=args.sequence,
            allele=args.allele,
            context=args.context,
            terminal_anchor=args.terminal_anchor,
            sorted_output=args.sorted,
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
            print("✅ Analysis completed successfully")

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
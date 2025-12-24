#!/usr/bin/env python3
"""
Script: batch_multi_allele.py
Description: Batch prediction with multiple MHC alleles

Original Use Case: examples/use_case_4_batch_multi_allele.py
Dependencies Removed: pandas (optional, only used for CSV output)

Usage:
    python scripts/batch_multi_allele.py --input <input_file> --alleles <allele1>,<allele2>

Example:
    python scripts/batch_multi_allele.py --input examples/data/peptides.txt --alleles DRB1_0101,DRB1_1501 --output results.csv
    python scripts/batch_multi_allele.py --peptides AAAGAEAGKATTE --alleles DRB1_0101,DQB1_0602 --excel
"""

# ==============================================================================
# Minimal Imports (only standard library + optional pandas)
# ==============================================================================
import argparse
import sys
import csv
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import re

# Add the lib directory to the path for our utilities
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from utils import create_temp_peptide_file, create_temp_fasta_file, validate_input_file, save_output, safe_file_cleanup
from netmhciipan import run_netmhciipan
from parsers import parse_netmhciipan_output, format_summary_report

# Optional pandas import for Excel output
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "input_type": "peptide",
    "context": False,
    "output_format": "csv",
    "include_summary": True,
    "max_parallel_jobs": 4
}

# ==============================================================================
# CSV Output Functions (pandas-free)
# ==============================================================================
def format_predictions_to_csv(all_results: Dict[str, Dict]) -> List[List[str]]:
    """
    Convert prediction results to CSV format without pandas dependency.

    Args:
        all_results: Dict mapping allele names to parsed results

    Returns:
        List of lists representing CSV rows
    """
    # Create CSV header
    header = [
        "allele", "position", "mhc", "peptide", "core", "of", "gp", "gl",
        "ip", "il", "icore", "identity", "score", "rank", "exp_bind", "bind_level"
    ]

    rows = [header]

    # Add data rows
    for allele_name, result in all_results.items():
        for prediction in result.get('all_predictions', []):
            row = [
                allele_name,
                prediction.get('position', ''),
                prediction.get('mhc', ''),
                prediction.get('peptide', ''),
                prediction.get('core', ''),
                prediction.get('of', ''),
                prediction.get('gp', ''),
                prediction.get('gl', ''),
                prediction.get('ip', ''),
                prediction.get('il', ''),
                prediction.get('icore', ''),
                prediction.get('identity', ''),
                prediction.get('score', ''),
                prediction.get('rank', ''),
                prediction.get('exp_bind', ''),
                prediction.get('bind_level', '')
            ]
            rows.append(row)

    return rows


def save_csv_output(csv_data: List[List[str]], output_file: Union[str, Path]) -> None:
    """
    Save CSV data to file.

    Args:
        csv_data: List of lists representing CSV rows
        output_file: Output file path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)


def save_excel_output(all_results: Dict[str, Dict], output_file: Union[str, Path]) -> None:
    """
    Save results to Excel file (requires pandas).

    Args:
        all_results: Dict mapping allele names to parsed results
        output_file: Output file path
    """
    if not HAS_PANDAS:
        raise ImportError("pandas is required for Excel output. Install with: pip install pandas openpyxl")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Create summary sheet
        summary_data = []
        for allele_name, result in all_results.items():
            summary = result.get('summary', {})
            summary_data.append({
                'allele': allele_name,
                'total_predictions': summary.get('total_predictions', 0),
                'strong_binders': summary.get('strong_binders_count', 0),
                'weak_binders': summary.get('weak_binders_count', 0),
                'non_binders': summary.get('non_binders_count', 0)
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Create detailed results sheet
        csv_data = format_predictions_to_csv(all_results)
        if len(csv_data) > 1:  # Has data beyond header
            header = csv_data[0]
            data_rows = csv_data[1:]
            details_df = pd.DataFrame(data_rows, columns=header)
            details_df.to_excel(writer, sheet_name='Detailed_Results', index=False)


# ==============================================================================
# Core Function
# ==============================================================================
def run_batch_multi_allele(
    input_file: Optional[Union[str, Path]] = None,
    peptides: Optional[List[str]] = None,
    protein: Optional[str] = None,
    alleles: List[str] = None,
    context: bool = False,
    input_type: str = "peptide",
    output_file: Optional[Union[str, Path]] = None,
    excel_output: bool = False,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run binding predictions across multiple MHC alleles in batch mode.

    Args:
        input_file: Path to input file (peptides or proteins)
        peptides: List of peptide sequences
        protein: Single protein sequence
        alleles: List of MHC alleles
        context: Use context-aware prediction
        input_type: "peptide" or "protein"
        output_file: Path to save output (optional)
        excel_output: Generate Excel output instead of CSV
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - results: Dict mapping allele names to parsed results
            - summary_stats: Overall summary statistics
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata

    Example:
        >>> result = run_batch_multi_allele(
        ...     input_file="examples/data/peptides.txt",
        ...     alleles=["DRB1_0101", "DRB1_1501"],
        ...     output_file="results/batch_results.csv"
        ... )
        >>> print(f"Processed {len(result['results'])} alleles")
    """
    # Setup configuration
    final_config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    context = final_config.get("context", context)
    input_type = final_config.get("input_type", input_type)

    # Validate inputs
    if not any([input_file, peptides, protein]):
        raise ValueError("One of input_file, peptides, or protein must be provided")

    if sum(bool(x) for x in [input_file, peptides, protein]) > 1:
        raise ValueError("Only one input method can be specified")

    if not alleles or len(alleles) == 0:
        raise ValueError("At least one allele must be provided")

    temp_file = None
    all_results = {}

    try:
        # Prepare input file
        if peptides:
            temp_file = create_temp_peptide_file(peptides)
            final_input_file = temp_file
            input_type = "peptide"
        elif protein:
            temp_file = create_temp_fasta_file(protein)
            final_input_file = temp_file
            input_type = "protein"
        else:
            final_input_file = str(validate_input_file(input_file))

        # Run predictions for each allele
        for allele in alleles:
            print(f"Processing allele: {allele}...")

            try:
                # Run NetMHCIIpan for this allele
                raw_output = run_netmhciipan(
                    input_file=final_input_file,
                    allele=allele,
                    input_type=input_type,
                    context=context
                )

                # Parse results
                parsed_results = parse_netmhciipan_output(raw_output)
                all_results[allele] = {
                    **parsed_results,
                    'raw_output': raw_output
                }

                print(f"  ✅ {allele}: {len(parsed_results.get('all_predictions', []))} predictions")

            except Exception as e:
                print(f"  ❌ {allele}: Error - {e}")
                all_results[allele] = {
                    'error': str(e),
                    'strong_binders': [],
                    'weak_binders': [],
                    'all_predictions': [],
                    'summary': {'total_predictions': 0, 'strong_binders_count': 0,
                               'weak_binders_count': 0, 'non_binders_count': 0}
                }

        # Calculate summary statistics
        summary_stats = {
            'total_alleles': len(alleles),
            'successful_alleles': len([r for r in all_results.values() if 'error' not in r]),
            'failed_alleles': len([r for r in all_results.values() if 'error' in r]),
            'total_predictions': sum(len(r.get('all_predictions', [])) for r in all_results.values()),
            'total_strong_binders': sum(len(r.get('strong_binders', [])) for r in all_results.values()),
            'total_weak_binders': sum(len(r.get('weak_binders', [])) for r in all_results.values())
        }

        # Save output if requested
        output_path = None
        if output_file:
            output_path = Path(output_file)

            if excel_output:
                save_excel_output(all_results, output_path)
            else:
                csv_data = format_predictions_to_csv(all_results)
                save_csv_output(csv_data, output_path)

        return {
            "results": all_results,
            "summary_stats": summary_stats,
            "output_file": str(output_path) if output_path else None,
            "metadata": {
                "input_file": str(input_file) if input_file else None,
                "input_type": input_type,
                "alleles": alleles,
                "context": context,
                "excel_output": excel_output,
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
        '--protein',
        help='Single protein sequence'
    )

    parser.add_argument(
        '--alleles', '-a',
        required=True,
        help='Comma-separated list of MHC alleles'
    )
    parser.add_argument(
        '--context', '-c',
        action='store_true',
        help='Use context-aware prediction'
    )
    parser.add_argument(
        '--input-type',
        choices=['peptide', 'protein'],
        default='peptide',
        help='Input type (default: peptide)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (CSV or Excel)'
    )
    parser.add_argument(
        '--excel',
        action='store_true',
        help='Generate Excel output (requires pandas)'
    )
    parser.add_argument(
        '--config',
        help='Config file (JSON)'
    )
    parser.add_argument(
        '--summary', '-s',
        action='store_true',
        help='Show summary statistics'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output for each allele'
    )

    args = parser.parse_args()

    try:
        # Load config if provided
        config = None
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Parse alleles
        alleles = [a.strip() for a in args.alleles.split(',')]

        # Prepare input data
        peptides = None
        if args.peptides:
            peptides = [p.strip() for p in args.peptides.split(',')]

        # Run batch prediction
        result = run_batch_multi_allele(
            input_file=args.input,
            peptides=peptides,
            protein=args.protein,
            alleles=alleles,
            context=args.context,
            input_type=args.input_type,
            output_file=args.output,
            excel_output=args.excel,
            config=config
        )

        # Print summary statistics
        if args.summary or not args.output:
            stats = result['summary_stats']
            print("\n" + "="*80)
            print("Batch Multi-Allele Prediction Summary")
            print("="*80)
            print(f"Total alleles processed: {stats['total_alleles']}")
            print(f"Successful predictions: {stats['successful_alleles']}")
            print(f"Failed predictions: {stats['failed_alleles']}")
            print(f"Total predictions: {stats['total_predictions']}")
            print(f"Total strong binders: {stats['total_strong_binders']}")
            print(f"Total weak binders: {stats['total_weak_binders']}")

        # Print detailed results if requested
        if args.verbose:
            for allele, allele_result in result['results'].items():
                print(f"\n--- {allele} ---")
                if 'error' in allele_result:
                    print(f"❌ Error: {allele_result['error']}")
                else:
                    summary_report = format_summary_report(allele_result)
                    print(summary_report)

        # Print success message
        if result['output_file']:
            print(f"\n✅ Results saved to: {result['output_file']}")
        else:
            print("\n✅ Batch prediction completed successfully")

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
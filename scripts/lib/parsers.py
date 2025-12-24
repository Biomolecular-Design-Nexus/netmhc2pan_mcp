"""
NetMHCIIpan output parsing utilities.

This module provides functions to parse and extract information from NetMHCIIpan output.
"""

import re
from typing import Dict, List, Any


def parse_netmhciipan_output(output_text: str) -> Dict[str, Any]:
    """
    Parse NetMHCIIpan output and extract key information.

    Args:
        output_text: Raw output from NetMHCIIpan

    Returns:
        dict: Parsed results with predictions and summary statistics
    """
    results = {
        'strong_binders': [],
        'weak_binders': [],
        'all_predictions': [],
        'summary': {}
    }

    lines = output_text.split('\n')
    in_results_section = False

    for line in lines:
        # Detect start of results section
        if line.startswith(' Pos ') and 'MHC' in line and 'Peptide' in line:
            in_results_section = True
            continue

        # Parse prediction lines
        if in_results_section and line.strip() and not line.startswith('-'):
            if line.startswith('Number of'):
                break

            # Extract prediction data
            prediction = parse_prediction_line(line)
            if prediction:
                results['all_predictions'].append(prediction)

                # Classify by binding strength
                rank = prediction.get('rank', 100.0)
                if rank <= 1.0:  # Strong binder
                    results['strong_binders'].append(prediction)
                elif rank <= 5.0:  # Weak binder
                    results['weak_binders'].append(prediction)

    # Add summary statistics
    results['summary'] = {
        'total_predictions': len(results['all_predictions']),
        'strong_binders_count': len(results['strong_binders']),
        'weak_binders_count': len(results['weak_binders']),
        'non_binders_count': len(results['all_predictions']) - len(results['strong_binders']) - len(results['weak_binders'])
    }

    return results


def parse_prediction_line(line: str) -> Dict[str, Any]:
    """
    Parse a single prediction line from NetMHCIIpan output.

    Args:
        line: Single line from results section

    Returns:
        dict: Parsed prediction data or None if parsing fails
    """
    try:
        parts = line.strip().split()
        if len(parts) < 10:
            return None

        return {
            'position': int(parts[0]),
            'mhc': parts[1],
            'peptide': parts[2],
            'core': parts[3] if len(parts) > 3 else "",
            'of': parts[4] if len(parts) > 4 else "",
            'gp': parts[5] if len(parts) > 5 else "",
            'gl': parts[6] if len(parts) > 6 else "",
            'ip': parts[7] if len(parts) > 7 else "",
            'il': parts[8] if len(parts) > 8 else "",
            'icore': parts[9] if len(parts) > 9 else "",
            'identity': parts[10] if len(parts) > 10 else "",
            'score': float(parts[11]) if len(parts) > 11 and parts[11] != 'NA' else None,
            'rank': float(parts[12]) if len(parts) > 12 and parts[12] != 'NA' else 100.0,
            'exp_bind': parts[13] if len(parts) > 13 else "",
            'bind_level': parts[14] if len(parts) > 14 else ""
        }
    except (ValueError, IndexError):
        return None


def format_summary_report(results: Dict[str, Any]) -> str:
    """
    Format a summary report from parsed results.

    Args:
        results: Parsed results from parse_netmhciipan_output

    Returns:
        str: Formatted summary report
    """
    summary = results['summary']
    strong_binders = results['strong_binders']
    weak_binders = results['weak_binders']

    report = [
        "="*80,
        "NetMHCIIpan Prediction Summary",
        "="*80,
        f"Total predictions: {summary['total_predictions']}",
        f"Strong binders (≤1% rank): {summary['strong_binders_count']}",
        f"Weak binders (1-5% rank): {summary['weak_binders_count']}",
        f"Non-binders (>5% rank): {summary['non_binders_count']}",
        ""
    ]

    if strong_binders:
        report.extend([
            "Top Strong Binders:",
            "-" * 40
        ])
        for i, binder in enumerate(strong_binders[:5]):
            report.append(
                f"  {i+1}. {binder['peptide']} "
                f"(pos {binder['position']}, rank {binder['rank']:.3f}%)"
            )
        report.append("")

    if weak_binders and not strong_binders:
        report.extend([
            "Top Weak Binders:",
            "-" * 40
        ])
        for i, binder in enumerate(weak_binders[:5]):
            report.append(
                f"  {i+1}. {binder['peptide']} "
                f"(pos {binder['position']}, rank {binder['rank']:.3f}%)"
            )

    return '\n'.join(report)
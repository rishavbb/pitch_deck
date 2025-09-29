#!/usr/bin/env python3
"""
Pitch Deck Analyzer - Main Entry Point

A tool for analyzing startup pitch decks and generating comprehensive investment reports.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analyzer import PitchDeckAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Analyze startup pitch decks and generate investment reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py pitch_deck.pdf
  python main.py presentation.pptx --output custom_report.md
  python main.py deck.pdf --api-key your_openrouter_key
        """
    )
    
    parser.add_argument(
        'pitch_deck',
        help='Path to the pitch deck file (PDF, PPT, or PPTX)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output path for the analysis report (default: auto-generated)',
        default=None
    )
    
    parser.add_argument(
        '--api-key',
        help='OpenRouter API key (can also be set via OPENROUTER_API_KEY env var)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.pitch_deck):
        print(f"❌ Error: File not found: {args.pitch_deck}")
        sys.exit(1)
    
    # Initialize analyzer
    try:
        analyzer = PitchDeckAnalyzer(openrouter_api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Set your OpenRouter API key using:")
        print("   export OPENROUTER_API_KEY='your_key_here'")
        print("   or use --api-key argument")
        sys.exit(1)
    
    # Analyze pitch deck
    print(f"🚀 Starting analysis of: {args.pitch_deck}")
    print("=" * 50)
    
    result = analyzer.analyze_pitch_deck(args.pitch_deck, args.output)
    
    if result['success']:
        print("=" * 50)
        print("✅ Analysis completed successfully!")
        print(f"📊 Report saved to: {result['report_path']}")
        
        # Display summary
        extraction_info = result.get('extraction_info', {})
        analysis_info = result.get('analysis_info', {})
        
        print("\n📋 Summary:")
        print(f"   • File type: {extraction_info.get('file_type', 'Unknown')}")
        print(f"   • Content length: {extraction_info.get('content_length', 0):,} characters")
        print(f"   • Pages/Slides: {extraction_info.get('pages_slides', 'Unknown')}")
        print(f"   • AI Model: {analysis_info.get('model_used', 'Unknown')}")
        print(f"   • Analysis: {'✅ Success' if analysis_info.get('analysis_success') else '❌ Failed'}")
        
    else:
        print("=" * 50)
        print("❌ Analysis failed!")
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

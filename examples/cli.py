#!/usr/bin/env python3
"""Command-line interface for ZPLConvert."""

import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zplconvert import convert_zpl_file_to_image

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Convert ZPL to PNG images')
    
    parser.add_argument('input', help='Path to ZPL input file')
    parser.add_argument('-o', '--output', help='Path to output PNG file')
    parser.add_argument('--width', type=int, default=850, help='Width of the output image in pixels')
    parser.add_argument('--height', type=int, default=1200, help='Height of the output image in pixels')
    parser.add_argument('--dpi', type=int, default=203, help='Dots per inch resolution')
    
    args = parser.parse_args()
    
    # Default output file is input file with .png extension
    if not args.output:
        args.output = os.path.splitext(args.input)[0] + '.png'
    
    print(f"Converting {args.input} to {args.output}")
    print(f"Image size: {args.width}x{args.height} pixels, {args.dpi} DPI")
    
    try:
        convert_zpl_file_to_image(
            args.input,
            args.output,
            width=args.width,
            height=args.height,
            dpi=args.dpi
        )
        print(f"Conversion successful: {args.output}")
        return 0
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
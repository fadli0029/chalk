import sys
import argparse
from chalk import extract

def main():
    parser = argparse.ArgumentParser(prog="chalk")
    subparsers = parser.add_subparsers(dest="command")

    extract_parser = subparsers.add_parser("extract", help="Extract slides from PDF")
    extract_parser.add_argument("pdf", help="Path to PDF")
    extract_parser.add_argument("output", help="Output directory")

    args = parser.parse_args()

    if args.command == "extract":
        extract.run(args.pdf, args.output)
    else:
        parser.print_help()

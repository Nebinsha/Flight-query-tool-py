"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

import sys
import argparse
import json
import os
import logging
from datetime import datetime
from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "251ADB013"
FIRST_NAME = "NebinSha"
LAST_NAME = "Shabeek"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("-i", metavar="FILE")
    source_group.add_argument("-d", metavar="FOLDER")
    source_group.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER")

    args = parser.parse_args(argv)
    if args.j and args.o is not None:
         parser.error("-o cannot be used with -j.")

    records = []
    errors = []

    if args.j:
        try:
            with open(args.j, "r", encoding="utf-8") as file:
                records = json.load(file)
            if not isinstance(records, list):
                print("Error: JSON database must contain a list.", file=sys.stderr)
                return 1
        except (OSError, json.JSONDecodeError) as error:
            print(f"Error: Cannot load JSON database: {error}", file=sys.stderr)
            return 1
    # csv input
    else:
        if not args.a:
            parser.error("-a airport file is required with -i or -d.")
        try:
            airports=load_airports(args.a)
            if args.i:
                paths=[args.i]
            else:
                if not os.path.isdir(args.d):
                    print("Error: Input folder does not exist.", file=sys.stderr)
                    return 1
                paths =[
                    os.path.join(args.d, name)
                    for name in sorted(os.listdir(args.d))
                    if name.lower().endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                ]
                if not paths:
                    print("Error: No CSV files found in folder.", file=sys.stderr)
                    return 1
            records, errors=parse_files(paths, airports)
        except OSError as error:
            print(f"Error: Cannot read input: {error}", file=sys.stderr)
            return 1

   #save database nderrors in csv mode
    if not args.j:
        handler=None
        logger=logging.getLogger("flight_parser")
        logger.setLevel(logging.WARNING)
        logger.propagate= False
        try:
            output_file=args.o or "db.json"
            with open(output_file,"w", encoding="utf-8") as file:
                json.dump(records,file,indent=2)
            log_path = os.path.join(
                os.path.dirname(output_file) or ".", "errors.log"
            )
            handler = logging.FileHandler(
                log_path, mode="w",encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )
            logger.addHandler(handler)
            for error in errors:
                logger.warning(error)
        except OSError as error:
            print(f"Error writing output: {error}", file=sys.stderr)
            return 1
        finally:
            if handler is not None:
                logger.removeHandler(handler)
                handler.close()
    #query 
    if args.q:
        try:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)
            responses = run_queries(records, queries)
            response_folder = args.r or "."
            os.makedirs(response_folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_"
                f"{timestamp}.json"
            )
            response_path = os.path.join(response_folder, filename)
            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2)
        except (OSError, json.JSONDecodeError) as error:
            print(f"Error: Cannot process query: {error}", file=sys.stderr)
            return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())
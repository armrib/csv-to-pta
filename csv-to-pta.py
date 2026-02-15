#!/usr/bin/env python3
import argparse
import csv
import hashlib
import os
import sys
import re
import unicodedata
from datetime import datetime
import logging


def read_existing_hashes(hash_file):
    existing_hashes = set()
    if hash_file and os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            existing_hashes.update(line.strip() for line in f)
    return existing_hashes


def read_payee(payee_file):
    payees = set()
    if payee_file and os.path.exists(payee_file):
        with open(payee_file, "r") as f:
            payees.update(line.strip() for line in f)
    return sorted(payees, key=lambda x: len(x), reverse=True)


def compute_hash(entry):
    return hashlib.sha256(entry.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Convert CSV to Plain Text Accounting")
    parser.add_argument("-f", "--file", required=True, help="Input CSV file")
    parser.add_argument("-d", "--delim", default=";", help="Delimiter (default: ;)")
    parser.add_argument("-s", "--skip", action="store_true", help="Skip header line")
    parser.add_argument(
        "-r",
        "--replace-comma",
        action="store_true",
        help="Replace comma decimals with dots",
    )
    parser.add_argument(
        "-D",
        "--date-format",
        default="%Y/%m/%d",
        help="Date format (default: YYYY/MM/DD)",
    )
    parser.add_argument(
        "-c", "--date-col", required=True, type=int, help="Column index for Date"
    )
    parser.add_argument(
        "-p",
        "--payee-col",
        action="append",
        type=int,
        required=True,
        help="Column index for Payee",
    )
    parser.add_argument(
        "-a", "--amount-col", required=True, type=int, help="Column index for Amount"
    )
    parser.add_argument(
        "-b", "--begin", default=0, type=int, help="Start from row number (default: 0)"
    )
    parser.add_argument(
        "-l",
        "--ledger",
        help="Ledger file path (default: from LEDGER_FILE environment variable)",
    )
    parser.add_argument(
        "-S",
        "--hash-file",
        help="Hash file path (default: LEDGER_FILE.hashes or from LEDGER_HASH_FILE environment variable)",
    )
    parser.add_argument(
        "-A",
        "--account",
        default="Assets:Checking",
        help="Account to use (default: Assets:Checking)",
    )
    parser.add_argument(
        "-P",
        "--payee-file",
        help="Payee file path (default: from LEDGER_PAYEE_FILE environment variable)",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="Encoding of the input file (default: utf-8)",
    )
    parser.add_argument(
        "-C",
        "--config",
        help="Config file path (default: from LEDGER_CONFIG_FILE environment variable)",
    )
    parser.add_argument(
        "--log-level", default="warning", help="Log level (default: warning)"
    )
    parser.add_argument(
        "--clean", default=True, type=bool, help="Clean up payee, default: True"
    )

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    # Determine ledger file path
    ledger_file = args.ledger if args.ledger else os.environ.get("LEDGER_FILE")
    if not ledger_file:
        logging.error(
            "Ledger file not specified and LEDGER_FILE environment variable not set."
        )
        sys.exit(1)

    # Determine hash file path
    hash_file = args.hash_file if args.hash_file else os.environ.get("LEDGER_HASH_FILE")
    if not hash_file:
        logging.warning(
            "Hash file not specified and LEDGER_HASH_FILE environment variable not set, using default."
        )
        hash_file = f"{ledger_file}.hashes"

    # Determine payee file path
    payee_file = (
        args.payee_file if args.payee_file else os.environ.get("LEDGER_PAYEE_FILE")
    )
    if not payee_file:
        logging.warning(
            "Payee file not specified and LEDGER_PAYEE_FILE environment variable not set, using default."
        )
        payee_file = f"{ledger_file}.payees"

    config_file = args.config if args.config else os.environ.get("LEDGER_CONFIG_FILE")
    if not config_file:
        logging.warning(
            "Config file not specified and LEDGER_CONFIG_FILE environment variable not set, using default."
        )
        config_file = f"{ledger_file}.config"

    # Read files
    existing_hashes = read_existing_hashes(hash_file)
    logging.info(f"found {len(existing_hashes)} existing hashes")
    payees = read_payee(payee_file)
    logging.info(f"found {len(payees)} payees")

    # Convert 1-based indices from user to 0-based for Python
    d_idx = args.date_col - 1
    p_idxs = [idx - 1 for idx in args.payee_col]
    a_idx = args.amount_col - 1

    with (
        open(args.file, mode="r", encoding=args.encoding) as f,
        open(ledger_file, "a") as out,
        open(hash_file, "a") as hash_out,
    ):
        if os.path.getsize(ledger_file) == 0:
            # Dump config file at the top of the ledger file
            if os.path.exists(config_file):
                with open(config_file, "r") as config:
                    out.writelines(config.readlines())

        # Read and parse CSV file
        reader = csv.reader(f, delimiter=args.delim)

        if args.skip:
            next(reader, None)

        for row_num, row in enumerate(reader, start=1):
            logging.debug(f"\n--- Row {row_num} ---")
            logging.debug(f"row: {row}")
            if not row:
                logging.warning("Empty row detected.")
                continue  # Skip empty lines

            if row_num < args.begin:
                continue

            date = row[d_idx].strip()
            if not date:
                logging.warning("Empty date detected.")
                continue

            try:
                date_obj = datetime.strptime(date, args.date_format)
                date = date_obj.strftime("%Y/%m/%d")
            except ValueError:
                logging.error(f"Invalid date detected: {date}")
                exit(1)

            # Concatenate columns for payee description
            raw_payee = " ".join(row[idx].strip() for idx in p_idxs if idx < len(row))
            if not raw_payee:
                logging.error("Empty payee detected.")
                exit(1)

            if args.clean:
                logging.debug(f"raw payee: {raw_payee}")
                payee = raw_payee.lower()
                # This pattern matches numbers that are not surrounded by letters
                payee = re.sub(r"(?<![a-zA-Z])[0-9]+(?![a-zA-Z])", "", payee)
                # This pattern match punctuation
                payee = re.sub(r"[^\w\s]", "", payee)
                # This pattern matches multiple spaces
                payee = re.sub(r"\s+", " ", payee).strip()
                if args.encoding != "utf-8":
                    nfkd_form = unicodedata.normalize("NFKD", payee)
                    payee = "".join(
                        c for c in nfkd_form if not unicodedata.combining(c)
                    )
                logging.debug(f"cleaned payee: {payee}")
            else:
                payee = raw_payee

            found = False
            for p in payees:
                if p in payee:
                    payee = p
                    found = True
            if not found:
                logging.warning(f"Payee not found:\n{payee}")
                payee_input = input("Enter payee: ")
                if payee_input:
                    if payee_input in ["quit", "exit", "stop"]:
                        break
                    payee = payee_input
                    payees.append(payee)

            amount = row[a_idx].strip()
            if args.replace_comma:
                amount = amount.replace(",", ".")
                amount = "".join(c for c in amount if c.isdigit() or c in ".-")
            try:
                amount = float(amount)
            except ValueError:
                logging.error(f"Invalid amount detected: {amount}")
                exit(1)

            print(f"Date: {date} | Payee: {payee} | Amount: {amount}")

            entry = (
                f"{date} {payee}\n\t{args.account}  {amount}\n\tExpenses:Unknown\n\n"
            )

            # Compute hash for the entry
            entry_hash = compute_hash(entry)

            # Check if entry already exists
            if entry_hash in existing_hashes:
                print("Info: Entry already exists. Skipping.")
                continue

            out.write(entry)
            hash_out.write(f"{entry_hash}\n")
            existing_hashes.add(entry_hash)

    with open(payee_file, "w") as f:
        for payee in sorted(payees, key=lambda x: len(x), reverse=True):
            f.write(f"{payee}\n")


if __name__ == "__main__":
    main()

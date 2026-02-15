# CSV to Plain Text Accounting Converter

This script converts CSV files to plain text accounting format, suitable for ledger accounting software.

## Features

- **File Handling**: Specify input CSV file, output ledger file, hash file, and payee file.
- **CSV Processing**: Customize delimiter, skip header line, replace comma decimals with dots, specify date format, and set column indices for date, payee, and amount.
- **String Cleaning**: Functions to clean strings by removing extra spaces, numbers not surrounded by letters, and punctuation.
- **Encoding**: Support for specifying the file encoding with a default of `utf-8`.
- **Contains Matching**: Match payee names with entries in a payee file to handle variations in payee names.
- **Hashing**: Compute hash for each entry to avoid processing duplicates.
- **Environment Variables**: Use environment variables for ledger file path, hash file path, and payee file path.
- **Line Sorting**: Sort file lines based on their length in ascending or descending order.

## Usage

### Basic Usage

To convert a CSV file to plain text accounting format, use the following command:

```bash
python csv-to-pta.py [options]
python3 csv-to-pta.py [options]
./csv-to-pta.py [options]
```

### Command-line Arguments

- `-f` or `--file`: Input CSV file (required).
- `-d` or `--delim`: Delimiter used in the CSV file (default is `;`).
- `-s` or `--skip`: Skips the header line if specified.
- `-r` or `--replace-comma`: Replaces comma decimals with dots if specified.
- `-D` or `--date-format`: Date format (default is `YYYY/MM/DD`).
- `-c` or `--date-col`: Column index for the date (required).
- `-p` or `--payee-col`: Column index for the payee (required, can be specified multiple times).
- `-a` or `--amount-col`: Column index for the amount (required).
- `-b` or `--begin`: Start from row number (default is 0).
- `-l` or `--ledger`: Ledger file path (default is from `LEDGER_FILE` environment variable).
- `-S` or `--hash-file`: Hash file path (default is from `LEDGER_HASH_FILE` environment variable or `LEDGER_FILE.hashes`).
- `-A` or `--account`: Account to use (default is `Assets:Checking`).
- `-P` or `--payee-file`: Payee file path (default is from `LEDGER_PAYEE_FILE` environment variable or `LEDGER_FILE.payees`).
- `-e` or `--encoding`: Encoding of the input file (default is `utf-8`).
- `-C` or `--config`: Config file path (default is from `LEDGER_CONFIG_FILE` environment variable or `LEDGER_FILE.config`).
- `--log-level`: Log level (default is `warning`).
- `--clean`: Clean up payee, default is `True`.

### Examples

1. **Basic Conversion**:

   ```bash
   python csv-to-pta.py -f input.csv -l ledger.pta -c 1 -p 2 -a 3
   ```

2. **Specify Encoding**:

   ```bash
   python csv-to-pta.py -f input.csv -l ledger.pta -c 1 -p 2 -a 3 -e latin-1
   ```

3. **Skip Header and Replace Commas**:

   ```bash
   python csv-to-pta.py -f input.csv -l ledger.pta -c 1 -p 2 -a 3 -s -r
   ```

4. **Custom Date Format**:

   ```bash
   python csv-to-pta.py -f input.csv -l ledger.pta -c 1 -p 2 -a 3 -D "%m/%d/%Y"
   ```

## Environment Variables

- `LEDGER_FILE`: Specifies the ledger file path.
- `LEDGER_HASH_FILE`: Specifies the hash file path.
- `LEDGER_PAYEE_FILE`: Specifies the payee file path.

### Examples

**Using Environment Variables**:

   ```bash
   export LEDGER_FILE="ledger.pta"
   export LEDGER_PAYEE_FILE="payees.txt"
   python csv-to-pta.py -f input.csv -c 1 -p 2 -a 3
   ```

## String Cleaning Functions

- **remove unsurrounded numbers**: Removes numbers that are not surrounded by letters.
- **remove punctuation**: Removes punctuation from the text.
- **clean spaces**: Removes extra spaces from the text.
- **remove accents**: Removes accents from the text.

## Contains Matching

The script uses contains matching to match payee names with entries in the payee file. This helps in handling variations in payee names.

## Hashing

The script computes a hash for each entry and checks if it has already been processed by looking it up in the set of existing hashes. This avoids processing duplicate entries.

## Line Sorting

The payee file is sorted based on the length of the payee names to allow most defined string to be matched first.

## Example Output

The script will process the input CSV file and write the results to the specified ledger file. The output format is suitable for ledger-cli accounting software.

## Notes

- The script uses 1-based indices for command-line arguments but converts them to 0-based indices for Python.
- The script ask for user input if no match is found for a payee. With time you'll only be asked for unknown payees.
- The script uses SHA-256 hashing to identify duplicate entries.

```

## Troubleshooting
 
 ### Common Issues
 
 1. **File Not Found**: Ensure that the input CSV file exists and is accessible.
 2. **Invalid Date Format**: Ensure that the date format matches the format of the dates in your CSV file.
 3. **Column Index Out of Range**: Ensure that the column indices you specify are within the range of columns in your CSV file.
 
 ### Debugging
 
 To debug issues, you can pass the log-level to a higher value or add print to the script yourself.
 
 ## License
 
 This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
 
 ## Contributing
 
 Contributions are welcome! Please open an issue or submit a pull request for any changes.

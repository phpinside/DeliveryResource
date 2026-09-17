#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path
import shutil
import tempfile


DEFAULT_INPUT = Path("teachers_rows.csv")
DEFAULT_NAME = "未命名用户"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Remove teacher rows whose name is the unnamed-user placeholder."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help="CSV file to clean. Defaults to teachers_rows.csv.",
    )
    parser.add_argument(
        "--name",
        default=DEFAULT_NAME,
        help=f"Name value to remove. Defaults to {DEFAULT_NAME!r}.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create a .bak backup before overwriting the CSV.",
    )
    return parser.parse_args()


def clean_csv(csv_file: Path, placeholder_name: str, create_backup: bool) -> tuple[int, int]:
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    with csv_file.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header row: {csv_file}")
        if "name" not in reader.fieldnames:
            raise ValueError(f"CSV file must contain a 'name' column: {csv_file}")

        fd, temp_name = tempfile.mkstemp(
            prefix=f".{csv_file.name}.",
            suffix=".tmp",
            dir=csv_file.parent or Path("."),
            text=True,
        )
        temp_path = Path(temp_name)

        removed_count = 0
        kept_count = 0
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
                writer.writeheader()

                for row in reader:
                    if row.get("name", "").strip() == placeholder_name:
                        removed_count += 1
                        continue

                    writer.writerow(row)
                    kept_count += 1
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    if create_backup:
        backup_path = csv_file.with_suffix(csv_file.suffix + ".bak")
        shutil.copy2(csv_file, backup_path)

    temp_path.replace(csv_file)
    return removed_count, kept_count


def main():
    args = parse_args()
    removed_count, kept_count = clean_csv(
        args.csv_file,
        args.name,
        create_backup=not args.no_backup,
    )
    print(f"Removed {removed_count} rows with name={args.name!r}.")
    print(f"Kept {kept_count} rows.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""تنظيف ملف CSV وإخراج ملخص إحصائي."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def clean_csv(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA})
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.drop_duplicates()
    if "name" in df.columns:
        df = df.dropna(subset=["name"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def summarize(df: pd.DataFrame) -> str:
    lines = [f"Rows: {len(df)}", f"Columns: {', '.join(df.columns)}"]
    if "amount" in df.columns:
        lines.append(f"Total amount: {df['amount'].sum(skipna=True):,.2f}")
        lines.append(f"Average amount: {df['amount'].mean(skipna=True):,.2f}")
    if "city" in df.columns:
        lines.append("By city:")
        for city, count in df["city"].value_counts(dropna=True).items():
            lines.append(f"  - {city}: {count}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="CSV Cleaner")
    parser.add_argument("-i", "--input", default="sample_data/dirty_sales.csv")
    parser.add_argument("-o", "--output", default="output/clean_sales.csv")
    args = parser.parse_args()
    df = clean_csv(Path(args.input), Path(args.output))
    print(summarize(df))
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()

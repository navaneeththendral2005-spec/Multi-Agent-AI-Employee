from pathlib import Path

import pandas as pd


SUPPORTED_FORMATS = {
    ".csv",
    ".xlsx",
    ".xls"
}


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load a CSV or Excel file into a Pandas DataFrame.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(path)

    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(path)

    raise ValueError(
        f"Unsupported data format: {extension}"
    )


def analyze_data(file_path: str) -> dict:
    """
    Perform local statistical analysis on a dataset.
    """

    dataframe = load_data(file_path)

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = dataframe.select_dtypes(
        exclude="number"
    ).columns.tolist()

    missing_values = (
        dataframe.isnull()
        .sum()
        .to_dict()
    )

    statistics = {}

    if numeric_columns:

        statistics = (
            dataframe[numeric_columns]
            .describe()
            .round(2)
            .to_dict()
        )

    return {
        "file": str(file_path),
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "column_names": dataframe.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "missing_values": missing_values,
        "statistics": statistics
    }

import base64
import io
import re
import pandas as pd
from fastapi import HTTPException
from http import HTTPStatus

ENCODING_TO_TRY = ["utf-8", "cp1252", "latin1"]

def _read_csv_file(file: str | io.StringIO) -> pd.DataFrame:
    """
    Read a CSV file from a string or StringIO object.
    """
    delimiters_to_try = [",", ";", "\t"]
    df = None
    for enc in ENCODING_TO_TRY:
        for delimiter in delimiters_to_try:
            try:
                if isinstance(file, io.StringIO):
                    file.seek(0)  # Reset the file pointer
                df = pd.read_csv(file, encoding=enc, sep=delimiter)
                print(
                    f"Successfully read CSV file with encoding {enc} and delimiter '{delimiter}'"
                )
                print(f"{len(df.columns)} column(s) found. Columns: {df.columns}")
                print(f"Dataframe Shape: {df.shape}")
                print(f"Dataframe types:\n{df.dtypes}")
                print(df.head())
                # Validate the CSV contents
                # _validate_dataframe(df)

                break
            except HTTPException:
                # Re-raise HTTPExceptions (from validation) directly
                raise
            except Exception as e:
                print(
                    f"Error reading CSV file with encoding {enc} and delimiter '{delimiter}': {e}"
                )
            continue
        if df is not None:
            break
    else:
        print("Error reading CSV file. No encoding worked.")
        raise ValueError(
            f"Could not read CSV file. Supported encodings: {ENCODING_TO_TRY}. Supported delimiters: {delimiters_to_try}.",
        )

    return df


def _read_base64_file(file_base64: str) -> pd.DataFrame:
    """
    Read a CSV file from a base64 encoded string.
    """
    validate_base64_string(file_base64)
    decoded_bytes = base64.b64decode(file_base64)
    print("Successfully decoded base64 string to bytes.")

    # Try different encodings
    csv_string = None

    for encoding in ENCODING_TO_TRY:
        try:
            csv_string = decoded_bytes.decode(encoding)
            print(
                f"Successfully decoded base64 string using {encoding} encoding."
            )
            break
        except UnicodeDecodeError:
            continue

    if csv_string is None:
        raise ValueError(
            f"Failed to decode the file with any of the supported encodings ({ENCODING_TO_TRY})"
        )

    print(
        f"Successfully decoded base64 string to csv string. Sample: {csv_string[:30]}"
    )
    csv_file = io.StringIO(csv_string)
    print("Successfully converted csv string to StringIO object.")

    return _read_csv_file(csv_file)


def validate_base64_string(base64_string: str) -> bool:
    """
    Validates if a string is a valid base64 encoded string.

    Args:
        base64_string: The string to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If the string is not a valid base64 encoded string
    """
    if not base64_string:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Base64 string is empty or null.",
        )

    # Check if the string contains valid base64 characters
    if not re.match(r"^[A-Za-z0-9+/]*={0,2}$", base64_string):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid base64 string format. Contains invalid characters.",
        )

    # Check if the length is valid (must be a multiple of 4 when padded)
    if len(base64_string) % 4 != 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid base64 string length. Length must be a multiple of 4.",
        )

    # Try to decode the base64 string
    try:
        base64.b64decode(base64_string)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Failed to decode base64 string: {str(e)}",
        )
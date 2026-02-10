import re


def normalize_filename(raw_name: str, default: str = "default") -> str:
    """
    Normalize arbitrary user input into a filesystem-safe filename.
    """
    name = raw_name.strip().lower()
    name = re.sub(r"[^a-z0-9_\-]+", "_", name)
    name = name.strip("_")
    return name or default

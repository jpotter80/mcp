"""
Utility functions for the preprocessing pipeline.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List
import yaml


def load_config(config_path: str = "preprocessing/config/processing_config.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def calculate_content_hash(content: str) -> str:
    """Calculate MD5 hash of content for change detection."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def save_json(data: Any, filepath: Path) -> None:
    """Save data as JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_jsonl(data: List[Dict], filepath: Path) -> None:
    """Save data as JSONL file (one JSON object per line)."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def load_jsonl(filepath: Path) -> List[Dict]:
    """Load data from JSONL file."""
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def count_tokens(text: str, tokenizer) -> int:
    """Count tokens in text using the provided tokenizer."""
    return len(tokenizer.encode(text))


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks."""
    import re
    
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)
    
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    return text.strip()


def generate_url(file_path: Path, base_path: Path, url_base: str) -> str:
    """Generate documentation URL from file path."""
    relative_path = file_path.relative_to(base_path)
    url_path = str(relative_path).replace(".mdx", "").replace(".md", "").replace("\\", "/")
    
    # Handle index files
    if url_path.endswith("/index"):
        url_path = url_path[:-6]  # Remove '/index'
    
    return f"{url_base}/{url_path}"


def extract_section_from_url(url: str, base_url: str) -> str:
    """Extract section identifier from URL."""
    if "#" in url:
        return url.split("#")[-1]
    return ""


def create_directory_structure(base_dir: Path, subdirs: List[str]) -> None:
    """Create directory structure for output."""
    base_dir.mkdir(parents=True, exist_ok=True)
    for subdir in subdirs:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)


def get_file_list(
    directory: Path, patterns: List[str], exclude_patterns: List[str] | None = None
) -> List[Path]:
    """Get list of files matching patterns, excluding specified patterns."""
    from fnmatch import fnmatch
    
    files = []
    exclude_patterns = exclude_patterns or []
    
    for pattern in patterns:
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                # Check if file matches any exclude pattern
                relative_path = file_path.relative_to(directory)
                if not any(
                    fnmatch(str(relative_path), exp) for exp in exclude_patterns
                ):
                    files.append(file_path)
    
    return sorted(files)


def format_bytes(size: int) -> str:
    """Format byte size as human-readable string."""
    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024.0:
            return f"{size_float:.2f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.2f} TB"


def generate_document_id(file_path: Path, base_path: Path) -> str:
    """Generate unique document ID from file path."""
    relative_path = file_path.relative_to(base_path)
    doc_id = str(relative_path).replace(".mdx", "").replace(".md", "").replace("/", "-")
    return doc_id.lower()


def split_text_by_separator(
    text: str, separator: str, keep_separator: bool = False
) -> List[str]:
    """Split text by separator, optionally keeping the separator."""
    if keep_separator:
        import re
        parts = re.split(f"({re.escape(separator)})", text)
        # Recombine separator with following text
        result = []
        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                result.append(parts[i] + parts[i + 1])
            else:
                result.append(parts[i])
        return result
    else:
        return text.split(separator)

"""Build a portable source archive with an explicit, reviewed file allowlist."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(destination):
    roots = [ROOT / name for name in ("chonoi", "tests", "tools", "docs")]
    files = [p for folder in roots for p in folder.rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".zip")]
    files.extend(ROOT / name for name in ("game.contract.json", "README.md", "TEAM.md", "AGENTS.md",
                                         "CHANGELOG.md", "CREDITS.md", "LICENSE", "requirements-bench.txt"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo("chonoi-v1.0.0/" + path.relative_to(ROOT).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    checksum = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(".zip.sha256").write_text(checksum + "  " + destination.name + "\n", encoding="ascii")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist/chonoi-v1.0.0.zip")
    print(build(parser.parse_args().out))

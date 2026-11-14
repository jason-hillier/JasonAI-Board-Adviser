"""Test-only launcher for a pre-provisioned Macian verifier."""

import sys
from pathlib import Path


def run_isolated_verifier(verifier_directory, cli_path, arguments):
    """Execute CLI with an isolated, pre-provisioned authority anchor."""
    import subprocess

    verifier_directory = Path(verifier_directory).resolve()
    anchor_path = verifier_directory / "strategic_evidence_authority_anchor.py"

    if not anchor_path.is_file():
        raise ValueError("No provisioned test authority anchor.")

    launcher = verifier_directory / "run_verifier.py"

    launcher.write_text(
        "import importlib.util\n"
        "import sys\n"
        "spec = importlib.util.spec_from_file_location("
        "'strategic_evidence_authority_anchor', "
        + repr(str(anchor_path)) + ")\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        "sys.modules['strategic_evidence_authority_anchor'] = module\n"
        "sys.path.insert(0, " + repr(str(Path(cli_path).resolve().parent)) + ")\n"
        "from strategic_evidence_checkpoint_cli import main\n"
        "raise SystemExit(main())\n",
        encoding="utf-8",
    )

    return subprocess.run(
        [sys.executable, str(launcher), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )

"""Security regression tests for verifier-owned authority anchors."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import strategic_evidence_authority_anchor as anchor


@pytest.fixture
def authority_file(tmp_path):
    path = tmp_path / "authority.sha256"
    path.write_text("a" * 64, encoding="ascii")
    path.chmod(0o600)
    return path


def verify_with_simulated_owner(path, owner_uid=0):
    """Simulate secure ancestor ownership without hiding target defects."""
    import os
    import stat

    real_fstat = os.fstat
    directory_count = 0

    def controlled_fstat(fd):
        nonlocal directory_count

        metadata = real_fstat(fd)
        mode = metadata.st_mode

        if stat.S_ISDIR(mode):
            directory_count += 1

            # The verifier traverses from / towards the anchor.
            # The authority's parent is the final directory.
            # We cannot reliably identify that final directory
            # from the descriptor count alone, so preserve its
            # real permissions through an explicit target check.
            if mode & 0o022:
                if directory_count == 1:
                    mode = (mode & ~0o777) | 0o700

        return SimpleNamespace(
            st_mode=mode,
            st_uid=owner_uid,
        )

    with (
        patch.object(anchor, "PRODUCTION_AUTHORITY_ANCHOR", path),
        patch.object(anchor, "TRUSTED_AUTHORITY_FINGERPRINT", None),
        patch.object(anchor.os, "fstat", side_effect=controlled_fstat),
    ):
        return anchor.require_trusted_authority_fingerprint()


def test_valid_administrator_anchor_accepted(authority_file):
    assert verify_with_simulated_owner(authority_file) == "a" * 64


def test_missing_anchor_rejected(tmp_path):
    with pytest.raises(ValueError, match="Cannot securely open authority trust anchor"):
        verify_with_simulated_owner(tmp_path / "missing.sha256")


def test_symlink_anchor_rejected(authority_file, tmp_path):
    link = tmp_path / "linked.sha256"
    link.symlink_to(authority_file)

    with pytest.raises(ValueError, match="Cannot securely open authority trust anchor"):
        verify_with_simulated_owner(link)


def test_insecure_permissions_rejected(authority_file):
    authority_file.chmod(0o666)

    with pytest.raises(ValueError, match="Authority anchor permissions are insecure"):
        verify_with_simulated_owner(authority_file)


def test_invalid_fingerprint_rejected(authority_file):
    authority_file.write_text("invalid", encoding="ascii")

    with pytest.raises(ValueError, match="Invalid authority trust anchor"):
        verify_with_simulated_owner(authority_file)


def test_oversized_anchor_rejected(authority_file):
    authority_file.write_text("a" * 1000, encoding="ascii")

    with pytest.raises(ValueError, match="Invalid authority trust anchor"):
        verify_with_simulated_owner(authority_file)


def test_non_administrator_owner_rejected(authority_file):
    """Reject a non-root authority file in otherwise trusted directories."""
    import os
    import stat

    real_fstat = os.fstat
    inspected_file = []

    def controlled_fstat(fd):
        metadata = real_fstat(fd)

        if stat.S_ISREG(metadata.st_mode):
            inspected_file.append(True)
            return SimpleNamespace(
                st_mode=metadata.st_mode,
                st_uid=501,
            )

        return SimpleNamespace(
            st_mode=metadata.st_mode,
            st_uid=0,
        )

    with (
        patch.object(anchor, "PRODUCTION_AUTHORITY_ANCHOR", authority_file),
        patch.object(anchor, "TRUSTED_AUTHORITY_FINGERPRINT", None),
        patch.object(anchor.os, "fstat", side_effect=controlled_fstat),
    ):
        with pytest.raises(
            ValueError,
            match="Authority anchor must be owned by the system administrator",
        ):
            anchor.require_trusted_authority_fingerprint()

    assert inspected_file, "Authority-file ownership was not inspected."


def test_world_writable_authority_directory_rejected(authority_file):
    authority_file.parent.chmod(0o777)

    with pytest.raises(ValueError, match="Authority configuration directory permissions are insecure"):
        verify_with_simulated_owner(authority_file)


def test_group_writable_authority_directory_rejected(authority_file):
    authority_file.parent.chmod(0o770)

    with pytest.raises(ValueError, match="Authority configuration directory permissions are insecure"):
        verify_with_simulated_owner(authority_file)


def test_symlink_authority_directory_rejected(authority_file, tmp_path):
    link = tmp_path / "linked-directory"
    link.symlink_to(authority_file.parent, target_is_directory=True)

    linked_anchor = link / authority_file.name

    with pytest.raises(ValueError, match="Cannot securely open authority trust anchor"):
        verify_with_simulated_owner(linked_anchor)


def test_non_administrator_directory_rejected(authority_file):
    """Reject a non-root directory even when the anchor file is root-owned."""
    import os
    import stat

    real_fstat = os.fstat
    inspected_directory = []

    def controlled_fstat(fd):
        metadata = real_fstat(fd)

        if stat.S_ISDIR(metadata.st_mode):
            inspected_directory.append(True)
            return SimpleNamespace(
                st_mode=metadata.st_mode,
                st_uid=501,
            )

        return SimpleNamespace(
            st_mode=metadata.st_mode,
            st_uid=0,
        )

    with (
        patch.object(
            anchor,
            "PRODUCTION_AUTHORITY_ANCHOR",
            authority_file,
        ),
        patch.object(
            anchor,
            "TRUSTED_AUTHORITY_FINGERPRINT",
            None,
        ),
        patch.object(
            anchor.os,
            "fstat",
            side_effect=controlled_fstat,
        ),
    ):
        with pytest.raises(
            ValueError,
            match="directory must be administrator-owned",
        ):
            anchor.require_trusted_authority_fingerprint()

    assert inspected_directory, (
        "Directory ownership validation was not exercised."
    )

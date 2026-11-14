"""Verifier-owned authority trust anchor.

Production authority configuration must be provisioned independently
of checkpoint submitters and protected by deployment-level controls.
"""

from pathlib import Path
import os
import stat


# Test harnesses may replace this module with an isolated authority anchor.
TRUSTED_AUTHORITY_FINGERPRINT = None

# Production path is fixed by the verifier deployment, not by CLI arguments.
PRODUCTION_AUTHORITY_ANCHOR = Path(
    "/etc/macian/verifier/trusted-authority.sha256"
)


def require_trusted_authority_fingerprint():
    """Return a valid verifier-owned fingerprint or fail closed."""

    fingerprint = TRUSTED_AUTHORITY_FINGERPRINT

    if fingerprint is None:
        path = PRODUCTION_AUTHORITY_ANCHOR

        # Traverse from the filesystem root using directory descriptors.
        # Never follow symbolic links in the authority configuration path.
        if not path.is_absolute():
            raise ValueError("Authority anchor path must be absolute.")

        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        file_flags = os.O_RDONLY | os.O_NOFOLLOW

        if hasattr(os, "O_CLOEXEC"):
            directory_flags |= os.O_CLOEXEC
            file_flags |= os.O_CLOEXEC

        directory_fd = -1
        descriptor = -1

        try:
            directory_fd = os.open("/", directory_flags)

            for component in path.parent.parts[1:]:
                next_fd = os.open(
                    component,
                    directory_flags,
                    dir_fd=directory_fd,
                )

                os.close(directory_fd)
                directory_fd = next_fd

                metadata = os.fstat(directory_fd)

                if not stat.S_ISDIR(metadata.st_mode):
                    raise ValueError(
                        "Authority configuration component is not a directory."
                    )

                if metadata.st_uid != 0:
                    raise ValueError(
                        "Authority configuration directory must be administrator-owned."
                    )

                if metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                    raise ValueError(
                        "Authority configuration directory permissions are insecure."
                    )

            descriptor = os.open(
                path.name,
                file_flags,
                dir_fd=directory_fd,
            )

        except OSError as exc:
            raise ValueError(
                "Cannot securely open authority trust anchor."
            ) from exc

        finally:
            if directory_fd >= 0:
                os.close(directory_fd)

        try:
            metadata = os.fstat(descriptor)

            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError("Authority anchor must be a regular file.")

            if metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                raise ValueError("Authority anchor permissions are insecure.")

            if metadata.st_uid != 0:
                raise ValueError(
                    "Authority anchor must be owned by the system administrator."
                )

            with os.fdopen(descriptor, "rb") as stream:
                descriptor = -1
                raw = stream.read(65)

            if len(raw) > 65:
                raise ValueError("Authority anchor exceeds maximum size.")

            try:
                fingerprint = raw.decode("ascii").strip()
            except UnicodeError as exc:
                raise ValueError("Invalid authority anchor encoding.") from exc

        finally:
            if descriptor >= 0:
                os.close(descriptor)

    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("Invalid authority trust anchor.")

    try:
        bytes.fromhex(fingerprint)
    except ValueError as exc:
        raise ValueError("Invalid authority trust anchor.") from exc

    return fingerprint.lower()

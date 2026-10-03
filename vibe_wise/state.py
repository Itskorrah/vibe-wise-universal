"""Host-independent, read-only project state selection."""
from pathlib import Path
import re
import stat


def is_link(path):
    if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
        return True
    # Path.is_junction arrived in Python 3.12. Keep older Windows interpreters safe.
    try:
        tag = getattr(path.lstat(), 'st_reparse_tag', None)
        return tag is not None and tag in (getattr(stat, 'IO_REPARSE_TAG_MOUNT_POINT', -1),
                                          getattr(stat, 'IO_REPARSE_TAG_SYMLINK', -2))
    except FileNotFoundError:
        return False

def profile_is_active(path):
    """Check activation without copying learner notes into hook output."""
    # A linked profile could point outside the selected project's learning notes.
    if is_link(path) or not path.is_file():
        return False
    has_content = False
    try:
        with path.open(encoding="utf-8") as stream:
            # Scan the whole file: a paused marker can appear after a long profile.
            # Reading line by line avoids loading all its contents into memory.
            for line in stream:
                has_content = has_content or bool(line.strip())
                if re.fullmatch(r"Learning mode:\s*paused\s*", line, re.IGNORECASE):
                    return False
    except (OSError, UnicodeError):
        # Missing, unreadable, or invalid text isn't evidence of active learning.
        return False
    # Older profiles may lack an explicit mode. Preserve their restoration behavior.
    return has_content


def state_directory(cwd):
    """Find the nearest notes directory without crossing a Git project boundary."""
    # Starting in a source subdirectory should still find the project's notes.
    for directory in (cwd, *cwd.parents):
        # Prefer the new name at the nearest location; keep legacy notes in place.
        for name in (".vibe-wise", ".sensible-vibes"):
            state = directory / name
            if state.exists() or is_link(state):
                # Stop even if this candidate is invalid. Falling back to a parent
                # could silently load a different project's learner profile.
                return state if state.is_dir() and not is_link(state) else None
        # A .git file is a worktree boundary too. Never borrow another repo's state.
        if (directory / ".git").exists():
            break
    return None


def pending_decisions(progress):
    """Read complete pending sections across the full history, without a size cutoff.

    This is an optional index of canonical note headings and explicit awaiting
    stages, not a mandatory new state format or proof no other decisions exist.
    Agents must still search the entire file and interpret legacy notes as data.
    """
    progress = Path(progress)
    if is_link(progress) or not progress.is_file():
        raise ValueError('Progress must be a regular unlinked file: ' + str(progress))
    pending = []
    section = []
    start = 1

    def record():
        text = ''.join(section)
        if re.search(r'^#{1,6}\s+Pending decision\b|\bawaiting\s+(?:reasoning|choice confirmation|implementation approval)\b',
                     text, re.IGNORECASE | re.MULTILINE):
            pending.append({'start_line': start, 'end_line': start + len(section) - 1,
                            'text': text})

    with progress.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if re.match(r'^#{1,2}\s+', line) and section:
                record()
                section = []
                start = number
            section.append(line)
        if section:
            record()
    return pending

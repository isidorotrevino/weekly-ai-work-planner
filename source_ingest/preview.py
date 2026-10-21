# SPDX-License-Identifier: GPL-3.0-only
"""Bounded Markdown observation. Source text is data, never instructions."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import uuid

MAX_BYTES = 2 * 1024 * 1024
MAX_LINES = 20000
MAX_ITEMS = 2000
MAX_LINE_CHARS = 65536
PROFILE = 'markdown-structure.v1'


def canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def _directory(path):
    """Open every directory component without following symlinks (Linux)."""
    absolute = Path(os.path.abspath(path))
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in absolute.parts[1:]:
            new = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        return fd
    except BaseException:
        os.close(fd)
        raise


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def read_source(root, relative):
    # Reject lexical traversal before filesystem normalization.
    if not relative or relative.startswith('/') or '\\' in relative or any(p in ('', '.', '..') for p in relative.split('/')):
        raise ValueError('Source must be a relative path without traversal')
    parts = relative.split('/')
    if not parts[-1].lower().endswith('.md'):
        raise ValueError('Only explicit Markdown files are supported')
    parent = _directory(root)
    fd = None
    try:
        for component in parts[:-1]:
            new = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            os.close(parent)
            parent = new
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError('Source must be a regular file without hard links')
        if before.st_size > MAX_BYTES:
            raise ValueError('Source exceeds 2 MiB')
        def bounded_read():
            chunks, size = [], 0
            while True:
                chunk = os.read(fd, min(65536, MAX_BYTES + 1 - size))
                if not chunk:
                    return b''.join(chunks)
                chunks.append(chunk)
                size += len(chunk)
                if size > MAX_BYTES:
                    raise ValueError('Source exceeds 2 MiB')
        content = bounded_read()
        os.lseek(fd, 0, os.SEEK_SET)
        repeated = bounded_read()
        if content != repeated or _identity(before) != _identity(os.fstat(fd)):
            raise ValueError('Source changed during observation; retry with a stable file')
        return content
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)


def structure(content):
    text = content.decode('utf-8-sig', errors='strict')
    if '\x00' in text:
        raise ValueError('NUL is not permitted in Markdown')
    lines = text.splitlines()
    if len(lines) > MAX_LINES or any(len(line) > MAX_LINE_CHARS for line in lines):
        raise ValueError('Markdown exceeds line count or line length limits')
    sections, proposals, diagnostics = [], [], []
    fence, context, table_lines = None, [], 0
    for number, line in enumerate(lines, 1):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            continue
        heading = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*$', line)
        if heading:
            level = len(heading[1])
            title = heading[2]
            closing = title.rsplit(None, 1)
            if len(closing) == 2 and set(closing[1]) == {'#'}:
                title = closing[0]
            context = [s for s in context if s['level'] < level]
            section = {'level': level, 'title': title, 'line': number}
            sections.append(section)
            context.append(section)
        item = re.match(r'^([ \t]*)(?:[-+*]|[0-9]+[.)])\s+\[([ xX])\]\s+(.+?)\s*$', line)
        if item:
            proposals.append({'kind': 'CHECKLIST_CANDIDATE', 'source_marker': 'CHECKED' if item[2].lower() == 'x' else 'UNCHECKED',
                              'text': item[3], 'line_start': number, 'line_end': number,
                              'heading_lines': [s['line'] for s in context], 'activation_allowed': False})
        if line.lstrip().startswith('|'):
            table_lines += 1
        if len(sections) > MAX_ITEMS or len(proposals) > MAX_ITEMS:
            raise ValueError('Markdown exceeds section or proposal limits')
    if table_lines:
        diagnostics.append({'code': 'TABLE_SEMANTICS_NOT_PARSED', 'line_count': table_lines})
    if fence:
        diagnostics.append({'code': 'UNCLOSED_FENCE'})
    diagnostics.append({'code': 'STRUCTURAL_PREVIEW_ONLY', 'message': 'No workflow status, dependency, approval or Gentle-AI grammar inferred'})
    return sections, proposals, diagnostics


def observe(root, relative, project_id, document_id, revision):
    project_id, document_id = str(uuid.UUID(project_id)), str(uuid.UUID(document_id))
    if not revision or len(revision) > 256 or any(ord(c) < 32 or ord(c) == 127 for c in revision):
        raise ValueError('Revision must be a nonempty opaque label of at most 256 characters')
    content = read_source(root, relative)
    sections, proposals, diagnostics = structure(content)
    digest = hashlib.sha256(content).hexdigest()
    observation = {'schema': 'd5.local-preview.v1', 'profile': PROFILE, 'state': 'PREVIEW_ONLY', 'activation_allowed': False,
                   'project_id': project_id, 'document_id': document_id, 'source_kind': 'LOCAL_MARKDOWN',
                   'source_path': relative, 'observed_revision': revision, 'revision_authority': 'CALLER_LABEL_ONLY',
                   'content_sha256': digest, 'content_bytes': len(content), 'content_base64': base64.b64encode(content).decode('ascii'),
                   'sections': sections, 'proposals': proposals, 'diagnostics': diagnostics}
    for proposal in proposals:
        proposal['candidate_id'] = str(uuid.uuid5(uuid.UUID(document_id), f'{project_id}:{digest}:{PROFILE}:{proposal["line_start"]}'))
        proposal['source_locator'] = f'sha256:{digest}#L{proposal["line_start"]}'
    return observation


def save_preview(store, observation):
    """Immutable, content-addressed artifact. No mutable head or sync cursor."""
    payload = canonical(observation)
    preview_hash = hashlib.sha256(payload).hexdigest()
    path = Path(store)
    path.mkdir(parents=True, mode=0o700, exist_ok=True)
    parent = _directory(path)
    name = preview_hash + '.json'
    temporary = None
    try:
        fd, temporary = tempfile.mkstemp(prefix='.preview-', dir=path)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            # Link publishes a complete file and refuses to replace any destination.
            os.link(temporary, name, dst_dir_fd=parent, follow_symlinks=False)
        except FileExistsError:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            with os.fdopen(fd, 'rb') as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size != len(payload):
                    raise ValueError('Existing preview is not the expected immutable artifact')
                if stream.read(len(payload) + 1) != payload:
                    raise ValueError('Existing preview content mismatch')
        os.unlink(temporary)
        temporary = None
        os.fsync(parent)
        return path / name, preview_hash
    finally:
        if temporary is not None:
            os.unlink(temporary)
        os.close(parent)

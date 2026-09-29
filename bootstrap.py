#!/usr/bin/env python3
from __future__ import annotations
import base64, gzip, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / '.practice_build'
PAYLOADS = ROOT / 'payloads'


def _payload(stem: str) -> bytes:
    parts = sorted(PAYLOADS.glob(f'{stem}.part*'))
    if not parts:
        raise FileNotFoundError(f'Missing companion payload: {stem}')
    encoded = ''.join(p.read_text(encoding='ascii').strip() for p in parts)
    return gzip.decompress(base64.b64decode(encoded))


def ensure_built(force: bool = False):
    catalog = BUILD / 'exercises' / 'catalog.json'
    databases = [BUILD / 'data' / 'release' / f'case_{c}.sqlite' for c in 'abcd']
    if not force and catalog.exists() and all(p.exists() for p in databases):
        return BUILD

    scripts = BUILD / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / 'generate_data.py').write_bytes(_payload('data_generator'))
    (scripts / 'generate_exercises.py').write_bytes(_payload('exercise_generator'))

    subprocess.run([sys.executable, str(scripts / 'generate_data.py')], check=True, cwd=BUILD)
    subprocess.run([sys.executable, str(scripts / 'generate_exercises.py')], check=True, cwd=BUILD)

    if not catalog.exists() or not all(p.exists() for p in databases):
        raise RuntimeError('Companion build did not create the expected catalog and databases.')
    return BUILD


if __name__ == '__main__':
    ensure_built(force='--force' in sys.argv)
    print('Companion data is ready.')

#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, re, sqlite3, sys
from pathlib import Path
from bootstrap import ensure_built

ROOT = Path(__file__).resolve().parent
BUILD = ensure_built()
CATALOG = BUILD / 'exercises' / 'catalog.json'
DATA = BUILD / 'data' / 'release'


def load_catalog():
    return {p['id']: p for p in json.loads(CATALOG.read_text(encoding='utf-8'))}


def validate_sql(sql: str):
    stripped = re.sub(r'^\s*(--.*\n\s*)*', '', sql, flags=re.M).lstrip()
    if not re.match(r'(?is)^(select|with)\b', stripped):
        raise ValueError('Only SELECT/WITH queries are accepted by the practice checker.')
    bad = re.search(r'(?is)\b(insert|update|delete|drop|alter|create|replace|vacuum|attach|detach)\b', stripped)
    if bad:
        raise ValueError(f'Read-only checker rejected keyword: {bad.group(1)}')
    return stripped


def execute(problem, sql):
    db = (DATA / f"{problem['case']}.sqlite").resolve()
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    con.execute('PRAGMA query_only=ON')
    try:
        cur = con.execute(validate_sql(sql))
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    finally:
        con.close()
    return cols, rows


def same_value(a, b, tol=1e-6):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)
    return str(a) == str(b)


def row_key(row):
    return '\x1f'.join(f'{v:.9f}' if isinstance(v, float) else ('NULL' if v is None else str(v)) for v in row)


def compare(problem, actual_cols, actual_rows, expected_cols, expected_rows):
    if actual_cols != expected_cols:
        return False, f'Column mismatch. Expected {expected_cols}; got {actual_cols}.'
    if len(actual_rows) != len(expected_rows):
        return False, f'Row-count mismatch. Expected {len(expected_rows)}; got {len(actual_rows)}.'
    if not problem['ordered']:
        actual_rows = sorted(actual_rows, key=row_key)
        expected_rows = sorted(expected_rows, key=row_key)
    for i, (a, e) in enumerate(zip(actual_rows, expected_rows), 1):
        for j, (av, ev) in enumerate(zip(a, e), 1):
            if not same_value(av, ev):
                return False, f'First mismatch at row {i}, column {j} ({actual_cols[j-1]}): expected {ev!r}; got {av!r}.'
    return True, f'Match: {len(actual_rows)} rows, {len(actual_cols)} columns.'


def cmd_list(cat, args):
    for p in cat.values():
        if args.case and p['case'] != args.case: continue
        if args.difficulty and p['difficulty'] != args.difficulty: continue
        print(f"{p['id']}  {p['case']}  {p['difficulty']:<12}  {p['title']}")


def cmd_show(cat, args):
    p = cat[args.problem]
    print(f"Problem {p['id']}: {p['title']}\n")
    print(p['context'])
    print(p['request'])
    print('Output columns:', ', '.join(p['output_columns']))
    print('Tags:', ', '.join(p['tags']))
    if p['hints']:
        print('\nHints:')
        for i, h in enumerate(p['hints'], 1): print(f'  {i}. {h}')


def cmd_check(cat, args):
    p = cat[args.problem]
    sql = Path(args.sql_file).read_text(encoding='utf-8')
    try:
        ac, ar = execute(p, sql)
        ec, er = execute(p, p['sql'])
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    ok, msg = compare(p, ac, ar, ec, er)
    print(('PASS: ' if ok else 'FAIL: ') + msg)
    if not ok:
        print('Tip: verify output grain, filters, joins, ordering, NULL handling, and denominator definitions.')
    return 0 if ok else 1


def cmd_verify_all(cat, args):
    failures = []
    for p in cat.values():
        try:
            cols, rows = execute(p, p['sql'])
            if cols != p['output_columns']:
                failures.append((p['id'], f'column mismatch: {cols}'))
            elif len(rows) != p['expected_row_count']:
                failures.append((p['id'], f'row-count mismatch: {len(rows)}'))
        except Exception as exc:
            failures.append((p['id'], str(exc)))
    if failures:
        print(f'FAIL: {len(failures)} canonical solutions failed verification.')
        for pid, msg in failures: print(pid, msg)
        return 1
    print(f'PASS: all {len(cat)} canonical solutions execute and match the generated expected metadata.')
    return 0


def cmd_solution(cat, args):
    print(cat[args.problem]['sql'])


def main():
    cat = load_catalog()
    ap = argparse.ArgumentParser(description='SQL Casebook offline practice checker')
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('list'); p.add_argument('--case', choices=['case_a','case_b','case_c','case_d']); p.add_argument('--difficulty', choices=['foundation','intermediate','advanced']); p.set_defaults(fn=cmd_list)
    p = sp.add_parser('show'); p.add_argument('problem', choices=cat); p.set_defaults(fn=cmd_show)
    p = sp.add_parser('check'); p.add_argument('problem', choices=cat); p.add_argument('sql_file'); p.set_defaults(fn=cmd_check)
    p = sp.add_parser('verify_all'); p.set_defaults(fn=cmd_verify_all)
    p = sp.add_parser('solution'); p.add_argument('problem', choices=cat); p.set_defaults(fn=cmd_solution)
    args = ap.parse_args()
    raise SystemExit(args.fn(cat, args) or 0)


if __name__ == '__main__':
    main()

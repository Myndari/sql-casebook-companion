# SQL Casebook for Data Analysts - Companion

Offline companion for **SQL Casebook for Data Analysts** by **Myndari**.

**Book data version:** `2026.09-r1`

The book is fully usable on its own. This repository adds a self-checking local practice environment. It rebuilds the book's deterministic synthetic practice data on your computer, runs your SQL against it, and compares your result with the verified canonical result. You do **not** need a database server, subscription, or third-party Python package.

## Requirements

- Python 3.11+ recommended
- Windows, macOS, or Linux
- No paid services

SQLite is included with standard Python and is the reference execution environment for this edition.

## Download

Click **Code -> Download ZIP**, extract the ZIP, and open a terminal in the extracted folder.

Or with Git:

```bash
git clone https://github.com/Myndari/sql-casebook-companion.git
cd sql-casebook-companion
```

## Quick start

```bash
python practice.py list
python practice.py show 042
```

Save your query in a file such as `my_solution.sql`, then run:

```bash
python practice.py check 042 my_solution.sql
```

A correct result prints `PASS`. The checker compares **results rather than SQL text**, so a different but genuinely equivalent query can pass.

Reveal the canonical solution only when you choose to:

```bash
python practice.py solution 042
```

Verify the entire companion environment:

```bash
python practice.py verify_all
```

Expected final line:

```text
PASS: all 120 canonical solutions execute and match the generated expected metadata.
```

## First-run behavior

The first command builds the four versioned synthetic practice databases and the structured exercise catalog locally in `.practice_build/`. This may take a few seconds. Later commands reuse those files.

The data generation is deterministic and uses the same fixed book-data version and generator used for the verified release. The businesses and all associated people, transactions, events, amounts, and histories are fictional and synthetic.

The checker opens the generated databases read-only and accepts only `SELECT` and `WITH` queries.

## Troubleshooting

If `python` is not recognized, try `python3`.

To reset the companion, delete `.practice_build/` and run any command again.

If a query has the right values but still fails, check the requested output column names and any required ordering or tie-breakers.

## Version

Book/companion data version: **2026.09-r1**

Copyright (c) 2026 Myndari. All rights reserved.

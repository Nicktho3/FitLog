# Verification — September 9, 2026

## Automated

- `python -m pytest -q`: **14 passed** against isolated temporary SQLite databases.
- `node --check Frontend/app.js`: passed.
- `git diff --check`: passed.
- Versions recorded in `requirements-lock.txt`.

The installed Starlette test client emits two dependency deprecation warnings about httpx and AnyIO. They do not fail the tests; the locked environment preserves the verified versions.

## Browser checks

Using the running local app:

- Registered a local demo account and reached the journal.
- Logged Chicken and rice with 520 calories, 40 g protein, 60 g carbs, and 15 g fat; confirmed the totals and saved row.
- Logged Barbell squat, 3 sets of 8 at 135 lb; confirmed the saved row.
- Updated the calorie goal to 2,300 and confirmed it in the summary.
- Selected the previous date and confirmed empty lists and zero totals.
- Returned to the original date and confirmed its entries reappeared.
- Reloaded and confirmed session and database persistence.
- Signed out and signed back in successfully.
- Checked the 390 px mobile layout: document width equaled viewport width, with no horizontal overflow.
- Checked the 1,280 px desktop layout and saved `screenshot.png` using example data.

Deletion, expired sessions, malformed input, legacy bcrypt compatibility, and cross-account access are covered by the API suite. PostgreSQL and public internet deployment were not exercised. CI is supplied as an optional template; the current GitHub token cannot publish workflow files.

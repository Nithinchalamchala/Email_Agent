# preprocessing

This module cleans raw email content before it reaches any classifier or LLM. It transforms an unstructured, potentially HTML-laden email body into a clean, normalized plain-text string.

## Files

| File | Purpose |
|---|---|
| `cleaner.py` | `EmailCleaner` class with methods for HTML removal, signature stripping, and whitespace normalization. |
| `parser.py` | `preprocess_email(raw_email)` function that orchestrates the cleaning steps and returns a `CleanedEmail`. |
| `__init__.py` | Package init. |

## What the Cleaner Does

`EmailCleaner.clean(text)` applies three transformations in order:

1. **HTML removal** - Strips all HTML tags using a regex. For richer HTML handling, swap in `BeautifulSoup`.
2. **Signature removal** - Scans for common signature delimiters (`--`, `Regards,`, `Best,`, `Thanks,`, `Sincerely,`, `Cheers,`). Everything from the first match onward is discarded. The list of patterns is configurable in `config/settings.py` under `SIGNATURE_PATTERNS`.
3. **Whitespace normalization** - Collapses all runs of whitespace (tabs, newlines, multiple spaces) to a single space.

## Input and Output

- **Input**: `RawEmail` - a Pydantic model with `sender`, `subject`, `body`, `timestamp`, `thread_id`, and `metadata`.
- **Output**: `CleanedEmail` - the same fields, with `body` replaced by `cleaned_body` (the processed text).

## Extending the Cleaner

To add more sophisticated cleaning:

- **Quoted reply stripping**: Add a method that detects `>` prefix lines or `On ... wrote:` headers and removes them.
- **Per-domain rules**: Accept domain context in the constructor and apply domain-specific patterns.
- **ML-based signature extraction**: Replace the pattern list with a trained boundary detector.

# logs

Runtime log output directory.

## Purpose

This directory holds log files written by the application during execution. It is intentionally excluded from version control (listed in `.gitignore`) since log files are runtime artifacts, not source code.

## Current Logging Behavior

The current pipeline logs to stdout (console) only via the `StreamHandler` configured in `config/logging_config.py`. No file handler is configured by default. This directory is a placeholder for when file-based logging is added.

## Adding File Logging

To write logs to this directory, add a `FileHandler` in `config/logging_config.py`:

```python
import logging

fh = logging.FileHandler("logs/hermes.log")
fh.setFormatter(formatter)
logger.addHandler(fh)
```

For production use, consider rotating logs with `logging.handlers.RotatingFileHandler` to prevent unbounded file growth.

## Log Level

The log level is controlled by the `LOG_LEVEL` environment variable in `.env` (default: `INFO`). Set it to `DEBUG` to see detailed per-step pipeline logs.

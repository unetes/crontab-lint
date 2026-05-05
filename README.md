# crontab-lint

> Static analyzer and validator for crontab expressions with human-readable summaries.

---

## Installation

```bash
pip install crontab-lint
```

---

## Usage

### Command Line

```bash
crontab-lint "*/5 * * * *"
```

**Output:**
```
✔ Valid expression: */5 * * * *
  → Runs every 5 minutes
```

### Validate a full crontab file

```bash
crontab-lint --file /etc/cron.d/myjobs
```

### Python API

```python
from crontab_lint import parse, validate

result = validate("0 9 * * 1-5")
print(result.summary)
# → "Runs at 09:00 AM, Monday through Friday"

result = validate("60 * * * *")
print(result.errors)
# → ["Field 'minute' value 60 is out of range (0-59)"]
```

---

## Features

- ✅ Validates standard 5-field crontab expressions
- 📖 Generates plain-English summaries of schedules
- 🔍 Detects common mistakes and out-of-range values
- 📄 Supports bulk validation of crontab files
- 🐍 Clean Python API and CLI interface

---

## License

This project is licensed under the [MIT License](LICENSE).
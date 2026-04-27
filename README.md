# envforge

> Snapshot, diff, and restore environment variable sets across dev/staging/prod configs.

---

## Installation

```bash
pip install envforge
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envforge
```

---

## Usage

**Snapshot** your current environment:

```bash
envforge snapshot --name dev
```

**Diff** two snapshots:

```bash
envforge diff dev staging
```

**Restore** a snapshot to a `.env` file:

```bash
envforge restore dev --output .env
```

**List** saved snapshots:

```bash
envforge list
```

Snapshots are stored locally in `~/.envforge/snapshots/` as encrypted JSON files. Sensitive values are masked by default in diff output.

---

## Quick Example

```bash
# Save current environment as "prod"
envforge snapshot --name prod

# Compare prod against your local dev snapshot
envforge diff dev prod

# Output:
# + API_URL        https://api.example.com   (prod only)
# ~ LOG_LEVEL      debug → info
# - DEBUG_MODE     true                      (dev only)
```

---

## License

MIT © [envforge contributors](LICENSE)
# keyloggerapp

A minimal Python keyboard listener built with `pynput` for educational purposes.

## Authorized Use, Legal & Ethics Warning

> **WARNING:** Recording keystrokes without explicit permission is illegal and unethical in most jurisdictions.
>
> - Run this software **only** on devices you own or where you have explicit written authorization to test.
> - **Plaintext Privacy Notice:** Keystrokes are written in **plaintext** to the configured log file (default: `~/log.txt`). Never leave it running while entering passwords, API keys, financial details, or personal credentials, and securely delete test log files when finished.

## Requirements

- Python 3.10+
- `pynput>=1.7.6`

Install dependencies in a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run from the repository root (`keyloggerapp/`):

```bash
python -m keylogger.keylogger --log-file ./session.log
```

You will be shown a safety banner, the exact log file path, and prompted to type `YES` to confirm authorized local use. To pass confirmation explicitly via flag:

```bash
python -m keylogger.keylogger --log-file ./session.log --i-understand-educational-use
```

- Press **`Esc`** (or `Ctrl+C` in the terminal) at any time to stop the listener cleanly.
- Delete generated log files after testing (e.g., `rm session.log` / `Remove-Item session.log`).

## Running Automated Tests (Mocked `pynput`)

The unit test suite mocks `pynput.keyboard.Listener` completely and never starts a live OS keyboard hook:

```bash
python -m unittest discover -s tests -v
```

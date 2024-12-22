# aipaste 📸

Manually copy-pasting code into AI is garbage. aipaste automates the grind: snapshots your project, formats it for AI tools, and spits out token stats. No more BS, just results.

## TL;DR

Tired of `cat`-ing files into your clipboard and pasting them into chat interfaces? aipaste generates a single, clean Markdown file with all the junk excluded, ready for AI tools like Claude or ChatGPT. Snap it, analyze it, done.

## Features

- **No BS**: Run `aipaste snap` or `aipaste stream` to do the work for you
- **Clean & Ready**: Automatically formats your project into Markdown
- **Smart Automation**: Skips the junk (`.gitignore`) and detects 25+ languages
- **Token Intel**: Instant token usage reports across models like GPT-4, Claude, and more
- **No Junk**: Filters out binaries, large files, and irrelevant clutter
- **Fast & Reliable**: Built in Python to keep things quick and clean
- **Clipboard Ready**: Stream output directly to your clipboard

## Installation

### Prerequisites

- Python 3.8+  
- [Poetry](https://python-poetry.org/docs/#installation)
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

### Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/aipaste.git
cd aipaste

# Install dependencies via Poetry
poetry install

# Build and install for the current user
make install-user

# Or system-wide (sudo)
make build
sudo make install-system
```

### Shell Completion (Optional)

Add to your shell's config file:

```bash
# For bash (~/.bashrc)
source <(aipaste completion bash)

# For zsh (~/.zshrc)
source <(aipaste completion zsh)
```

---

## Usage

### 1) Create a Snapshot File
```bash
cd your-project
aipaste snap
```
This generates `your-project_source.md`, containing all your code in Markdown form.

### 2) Stream to Clipboard
```bash
# macOS
aipaste stream | pbcopy

# Linux
aipaste stream | xclip -selection clipboard
# or
aipaste stream | xsel --clipboard

# Windows (PowerShell)
aipaste stream | Set-Clipboard
```

### 3) Detailed Token Analysis
```bash
# If the current folder is named "myproject", it auto-detects myproject_source.md
aipaste tokens
```
Or specify a file:
```bash
aipaste tokens /path/to/snapshot.md
```

This command prints:
- File stats (characters, lines, code blocks)
- Per-model token count
- Maximum context window usage and remaining tokens

#### Example Output
```
Project File Statistics
  • File Name: myproject_source.md
  • Characters: 12,345
  • Lines: 234
  • Code Blocks: 3

Model-Specific Token Estimates:
  • GPT-4: 1,234 tokens
     ↳ Max Context: 8,192  |  Usage: 15.1%  |  Remaining: 6,958
  • GPT-O1: 1,357 tokens
     ↳ Max Context: 4,096  |  Usage: 33.1%  |  Remaining: 2,739
  • Ollama-Llama2-7B: 1,110 tokens
     ↳ Max Context: 4,096  |  Usage: 27.1%  |  Remaining: 2,986
  ...
```

---

## Command Reference

### `aipaste snap`
Creates a project snapshot (`{project-name}_source.md` by default).

Options:
- `-p, --path`: Project directory
- `-o, --output`: Output file
- `--summary/--no-summary`: Show/hide project stats in terminal
- `--max-file-size`: Maximum file size (default: 1MB)
- `-f, --force`: Overwrite existing file
- `--skip-common`: Skip common files like LICENSE
- `--skip-files`: Additional patterns to skip

### `aipaste stream`
Stream project snapshot to stdout (perfect for piping to clipboard).

Options:
- `-p, --path`: Project directory
- `--max-file-size`: Maximum file size (default: 1MB)
- `--skip-common`: Skip common files like LICENSE
- `--skip-files`: Additional patterns to skip

### `aipaste tokens [FILE]`
If `FILE` is not given, attempts to open `{cwd_name}_source.md`.  
Displays:
- File stats (characters, lines, code blocks)
- Token usage across multiple AI models (GPT-4, GPT-3.5, Claude, GPT-O1, Ollama Llama2, etc.)
- Percentage of each model's context window used & remaining tokens

### `aipaste completion [bash|zsh|fish]`
Generates a shell completion script. Example usage:
```bash
source <(aipaste completion bash)
```

---

## Development

```bash
poetry install
poetry run aipaste snap
make build
make clean
make install-user
```

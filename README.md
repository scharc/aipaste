# aipaste 📋

Stop copy-pasting code manually into AI. aipaste automates sharing your codebase with AI tools by formatting it for readability and handling clipboard operations automatically.

## Features

- **Direct to Clipboard**: Run `aipaste` to format your project and copy it to clipboard instantly
- **Auto-Format**: Generate clean Markdown with proper syntax highlighting for 25+ languages
- **Smart Filtering**: Automatically excludes binaries, large files, and irrelevant content using `.gitignore`
- **Token Aware**: Get instant token usage estimates for GPT-4, Claude, and other models
- **Flexible Output**: Stream to clipboard, save to file, or pipe to other tools
- **Fast & Reliable**: Built in Python with minimal dependencies

## Quick Start

```bash
# Install from source (see Installation section)
git clone https://github.com/scharc/aipaste.git
cd aipaste
make install-user

# Copy entire project to clipboard (default command)
cd your-project
aipaste

# Or save to file
aipaste snap

# Get token usage stats
aipaste tokens
```

## Installation

### Prerequisites
- Python 3.8+
- Poetry (optional, for development)

### Install Methods

From source:
```bash
git clone https://github.com/scharc/aipaste.git
cd aipaste
make install-user  # Install for current user
# OR
make install-system  # System-wide installation (sudo)
```

## Usage

### 1. Direct to Clipboard (Default)
Just run `aipaste` in your project directory to automatically format and copy to clipboard:
```bash
cd your-project
aipaste
```

### 2. Save to File
Generate a Markdown snapshot file:
```bash
aipaste snap
```
This creates `your-project_source.md` containing your formatted code.

### 3. Stream to Clipboard Manually
Alternatively, use the stream command with your preferred clipboard tool:
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

### 4. Token Analysis
Check token usage across different AI models:
```bash
aipaste tokens [FILE]  # FILE is optional
```

Example output:
```
Project File Statistics
  • File Name: myproject_source.md
  • Characters: 12,345
  • Lines: 234
  • Code Blocks: 3

Model-Specific Token Estimates:
  • GPT-4: 1,234 tokens
     ↳ Max Context: 8,192  |  Usage: 15.1%  |  Remaining: 6,958
  • Claude: 987 tokens
     ↳ Max Context: 100,000  |  Usage: 0.9%  |  Remaining: 99,013
  ...
```

## Command Reference

### `aipaste`
Format project and copy to clipboard (default command).

### `aipaste snap`
Create a project snapshot file with options:
- `-p, --path`: Project directory (default: current)
- `-o, --output`: Output file (default: {project}_source.md)
- `--max-file-size`: Maximum file size (default: 1MB)
- `-f, --force`: Overwrite existing file
- `--skip-common`: Skip common files (LICENSE, etc.)
- `--skip-files`: Additional patterns to skip

### `aipaste stream`
Stream formatted output, perfect for piping:
- `-p, --path`: Project directory
- `--max-file-size`: Maximum file size
- `--skip-common`: Skip common files
- `--skip-files`: Additional patterns to skip

### Shell Completion (Optional)

Add to your shell config:
```bash
# Bash (~/.bashrc)
source <(aipaste completion bash)

# Zsh (~/.zshrc)
source <(aipaste completion zsh)
```

## Development

```bash
# Setup
git clone https://github.com/scharc/aipaste.git
cd aipaste
poetry install

# Build and test
make build
make clean
make install-user
```

#!/usr/bin/env python3
import sys
from pathlib import Path
import click
from typing import List, Dict, Iterator
import fnmatch
import chardet
from rich import print as rprint
from rich.panel import Panel
from rich.syntax import Syntax
from rich.console import Console
import tiktoken
import pyperclip

class Aipaste:
    """Main class for creating AI-friendly snapshots of code projects."""

    def __init__(
        self,
        project_path: str = ".",
        output_file: str = None,
        skip_common: bool = False,
        skip_files: list = None,
    ):
        self.project_path = Path(project_path)
        self.output_file = Path(output_file).resolve() if output_file else None
        self.ignore_patterns = []
        self.skip_common = skip_common
        self.skip_files = skip_files or []
        self.common_files = {
            "LICENSE",
            "LICENSE.md",
            "LICENSE.txt",
            "CONTRIBUTING.md",
            "CONTRIBUTING",
            "CODE_OF_CONDUCT.md",
            "CODE_OF_CONDUCT",
            "CHANGELOG.md",
            "CHANGELOG",
            "SECURITY.md",
            "SECURITY",
            ".gitattributes",
            ".editorconfig",
            ".dockerignore",
        }
        self.stats = {
            "total_files": 0,
            "included_files": 0,
            "binary_files": 0,
            "ignored_files": 0,
            "total_size": 0,
            "languages": set(),
        }
        # Common binary extensions to ignore
        self.binary_extensions = {
            # Images
            "png",
            "jpg",
            "jpeg",
            "gif",
            "bmp",
            "tiff",
            "webp",
            "ico",
            "svg",
            "psd",
            "ai",
            "eps",
            "raw",
            # Documents and archives
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "zip",
            "tar",
            "gz",
            "rar",
            "7z",
            "bz2",
            "iso",
            # Executables and libraries
            "exe",
            "dll",
            "so",
            "dylib",
            "lib",
            "obj",
            "bin",
            "apk",
            "app",
            "msi",
            # Fonts
            "ttf",
            "otf",
            "woff",
            "woff2",
            "eot",
            # Media
            "mp3",
            "mp4",
            "wav",
            "ogg",
            "avi",
            "mov",
            "wmv",
            "flv",
            "mkv",
            "aac",
            "m4a",
            "flac",
            # Database
            "db",
            "sqlite",
            "sqlite3",
            "mdb",
            "frm",
            "ibd",
            # Other binary formats
            "class",
            "pyc",
            "pyo",
            "pyd",
            "o",
            "a",
            "pkl",
            "dat",
        }
        self.extension_map = {
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "py": "python",
            "rb": "ruby",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "cs": "csharp",
            "php": "php",
            "go": "go",
            "rs": "rust",
            "swift": "swift",
            "kt": "kotlin",
            "r": "r",
            "sql": "sql",
            "yaml": "yaml",
            "yml": "yaml",
            "json": "json",
            "md": "markdown",
            "html": "html",
            "css": "css",
            "scss": "scss",
            "less": "less",
            "sh": "bash",
            "bash": "bash",
            "dockerfile": "dockerfile",
        }

    def initialize(self) -> None:
        """Initialize ignore patterns from .gitignore if it exists"""
        default_patterns = [
            ".git/**",
            "node_modules/",
            ".git/",
            "dist/",
            "build/",
            "coverage/",
            ".env*",
            ".DS_Store",
            "*.log",
            "*.lock",
            "package-lock.json",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "env/",
            "venv/",
            ".env/",
            ".venv/",
            "ENV/",
            "env.bak/",
            "venv.bak/",
        ]

        # Add default patterns
        self.ignore_patterns.extend(default_patterns)

        # Read .gitignore if it exists
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            rprint(f"[blue].gitignore found. Loading patterns...[/]")
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Handle negative patterns (inclusion)
                        if line.startswith("!"):
                            # TODO: Add support for negative patterns
                            continue

                        # Normalize pattern
                        if line.startswith("./"):
                            line = line[2:]

                        # Add the pattern
                        self.ignore_patterns.append(line)
            rprint(
                f"[green]Loaded {len(self.ignore_patterns)} patterns from .gitignore[/]"
            )
        else:
            rprint(f"[yellow].gitignore not found. Using default patterns only.[/]")

    def should_ignore(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on patterns"""
        # If this is our output file, ignore it
        if self.output_file and file_path.resolve() == self.output_file:
            return True

        # Check common files to skip
        if self.skip_common and file_path.name in self.common_files:
            return True

        # Check additional files to skip
        for pattern in self.skip_files:
            if fnmatch.fnmatch(file_path.name, pattern):
                return True

        rel_path = str(file_path.relative_to(self.project_path))

        for pattern in self.ignore_patterns:
            # Handle patterns with and without slashes
            if pattern.startswith("/"):
                # Anchored to root
                pattern = pattern[1:]
            elif pattern.endswith("/"):
                # Directory matching
                if fnmatch.fnmatch(rel_path + "/", pattern):
                    return True

            # Convert .gitignore glob patterns to fnmatch patterns
            # Handle '**' pattern for recursive matching
            if "**" in pattern:
                parts = pattern.split("**")
                pattern = "*".join(parts)

            if fnmatch.fnmatch(rel_path, pattern):
                return True

            # Check if any parent directory matches
            parent_path = Path(rel_path)
            while parent_path != Path("."):
                parent_path = parent_path.parent
                if fnmatch.fnmatch(str(parent_path) + "/", pattern):
                    return True

        return False

    def get_language(self, file_path: Path) -> str:
        """Get the language identifier for syntax highlighting"""
        return self.extension_map.get(file_path.suffix.lstrip(".").lower(), "")

    def is_text_file(self, file_path: Path, max_size: int = 1_000_000) -> bool:
        """Check if a file is a text file and within size limits"""
        try:
            # Check extension first
            if file_path.suffix.lstrip(".").lower() in self.binary_extensions:
                return False

            if file_path.stat().st_size > max_size:  # Skip files larger than max_size
                return False

            # Read first 4KB of the file
            with open(file_path, "rb") as f:
                chunk = f.read(4096)

            # Try to detect the encoding
            result = chardet.detect(chunk)
            if result["encoding"] is None:
                return False

            # Check for null bytes
            if b"\x00" in chunk:
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def estimate_tokens(text: str) -> Dict[str, Dict[str, float]]:
        """
        Returns:
            {
                "GPT-4": {
                    "tokens": 1234,
                    "max_context": 8192,
                    "usage_percent": 15.07,
                    "remaining_tokens": 6958,
                    ...
                },
                ...
            }
        """

        enc = tiktoken.get_encoding("cl100k_base")
        baseline_count = len(enc.encode(text))

        # Example model specs
        model_specs = {
            "GPT-4": {
                "multiplier": 1.00,
                "max_context": 8192,
            },
            "GPT-3.5": {
                "multiplier": 1.00,
                "max_context": 4096,
            },
            "Claude": {
                "multiplier": 0.80,
                "max_context": 100000,
            },
            "GPT-O1": {
                "multiplier": 1.10,
                "max_context": 4096,
            },
            "Ollama-Llama2-7B": {
                "multiplier": 0.90,
                "max_context": 4096,
            },
            "Ollama-Llama2-13B": {
                "multiplier": 0.85,
                "max_context": 4096,
            },
        }

        results = {}
        for model_name, specs in model_specs.items():
            multiplier = specs["multiplier"]
            max_ctx = specs["max_context"]

            est_tokens = int(baseline_count * multiplier)
            usage_percent = (est_tokens / max_ctx) * 100 if max_ctx > 0 else 0
            remaining_tokens = max_ctx - est_tokens

            results[model_name] = {
                "tokens": est_tokens,
                "max_context": max_ctx,
                "usage_percent": usage_percent,
                "remaining_tokens": remaining_tokens,
            }

        return results

    def generate_tree(self) -> str:
        """Generate a directory tree of the project"""
        tree_lines = ["```", "."]
        last_level = 0
        sorted_files = sorted(
            [p for p in self.project_path.rglob("*") if not self.should_ignore(p)],
            key=lambda x: str(x),
        )

        for path in sorted_files:
            rel_path = path.relative_to(self.project_path)
            level = len(rel_path.parts) - 1
            prefix = "│   " * (level - 1) + ("├── " if level > 0 else "")
            name = rel_path.parts[-1]
            if not path.is_file():  # Directory
                tree_lines.append(f"{prefix}{name}/")
            else:
                tree_lines.append(f"{prefix}{name}")

        tree_lines.append("```")
        return "\n".join(tree_lines)

    def concatenate(
        self,
        max_file_size: int = 1_000_000,
        summary: bool = True,
        token_estimate: bool = False,
    ) -> str:
        """Concatenate all project files into a markdown string"""
        self.initialize()
        output = ["# Project Source Code\n"]

        # Add directory tree
        output.extend(["## Project Structure", self.generate_tree(), ""])

        # Collect and sort all files
        files = []
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                self.stats["total_files"] += 1
                if not self.should_ignore(file_path):
                    files.append(file_path)
                else:
                    self.stats["ignored_files"] += 1

        files.sort()

        # Process each file
        for file_path in files:
            rel_path = file_path.relative_to(self.project_path)
            if self.is_text_file(file_path, max_file_size):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    lang = self.get_language(file_path)

                    self.stats["included_files"] += 1
                    self.stats["total_size"] += len(content)
                    if lang:
                        self.stats["languages"].add(lang)

                    output.extend(
                        [f"\n## {rel_path}\n", f"```{lang}", content, "```\n"]
                    )
                except Exception as e:
                    rprint(f"[yellow]Warning:[/] Skipping {rel_path}: {str(e)}")
            else:
                self.stats["binary_files"] += 1
                output.extend([f"\n## {rel_path}\n", "*[Binary file]*\n"])

        result = "\n".join(output)

        if token_estimate:
            tokens = self.estimate_tokens(result)
            if tokens:
                token_info = ["\n## Token Estimates\n"]
                for model, count in tokens.items():
                    token_info.append(f"- {model}: ~{count:,} tokens")
                result = "\n".join([result, *token_info])

        # Print statistics to console only
        if summary:
            rprint("\n[green]Project Statistics:[/]")
            rprint(f"  • Total files scanned: {self.stats['total_files']}")
            rprint(f"  • Files included: {self.stats['included_files']}")
            rprint(f"  • Binary files: {self.stats['binary_files']}")
            rprint(f"  • Ignored files: {self.stats['ignored_files']}")
            rprint(f"  • Total size: {self.stats['total_size'] / 1024:.1f}KB")
            rprint(f"  • Languages: {', '.join(sorted(self.stats['languages']))}")

        return result

    def stream_output(
        self,
        max_file_size: int = 1_000_000,
    ) -> Iterator[str]:
        """Stream the concatenated output of all project files.

        Args:
            max_file_size: Maximum size of individual files to include

        Yields:
            Chunks of the markdown output as they're generated
        """
        self.initialize()

        # Disable rich formatting when streaming
        console = Console(file=sys.stdout, force_terminal=False)

        # Header
        yield "# Project Source Code\n\n"

        # Project structure
        yield "## Project Structure\n"
        yield self.generate_tree()
        yield "\n"

        # Process files
        files = []
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                self.stats["total_files"] += 1
                if not self.should_ignore(file_path):
                    files.append(file_path)
                else:
                    self.stats["ignored_files"] += 1

        files.sort()

        # Stream each file
        for file_path in files:
            rel_path = file_path.relative_to(self.project_path)
            yield f"\n## {rel_path}\n"

            if self.is_text_file(file_path, max_file_size):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    lang = self.get_language(file_path)
                    self.stats["included_files"] += 1
                    self.stats["total_size"] += len(content)
                    if lang:
                        self.stats["languages"].add(lang)

                    yield f"```{lang}\n"
                    yield content
                    yield "```\n"
                except Exception as e:
                    console.print(f"[yellow]Warning:[/] Skipping {rel_path}: {str(e)}")
                    yield "*[Error reading file]*\n"
            else:
                self.stats["binary_files"] += 1
                yield "*[Binary file]*\n"


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """AIpaste - Format your code for AI tools like ChatGPT and Claude."""
    if ctx.invoked_subcommand is None:
        # Capture stream output to clipboard
        output = []
        try:
            paster = Aipaste(
                project_path=".",
                output_file=None,
                skip_common=False,
                skip_files=[],
            )

            # Collect all chunks
            for chunk in paster.stream_output():
                output.append(chunk)

            # Join and copy to clipboard
            full_output = "".join(output)
            import pyperclip

            pyperclip.copy(full_output)

            console = Console(stderr=True)
            console.print("[green]✓[/] Project snapshot copied to clipboard!")

        except Exception as e:
            console = Console(stderr=True)
            console.print(f"[red]Error:[/] {str(e)}")
            raise click.Abort()


@cli.command()
@click.option(
    "-p",
    "--path",
    "project_path",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the project directory",
)
@click.option(
    "--max-file-size",
    default=1_000_000,
    type=int,
    help="Maximum file size in bytes",
)
@click.option(
    "--skip-common",
    is_flag=True,
    help="Skip commonly referenced files (LICENSE, CONTRIBUTING, etc.)",
)
@click.option(
    "--skip-files",
    multiple=True,
    help="Additional files or patterns to skip",
)
def stream(project_path, max_file_size, skip_common, skip_files):
    """Stream project snapshot to stdout for piping."""
    try:
        paster = Aipaste(
            project_path=project_path,
            output_file=None,  # We don't need an output file for streaming
            skip_common=skip_common,
            skip_files=skip_files,
        )

        for chunk in paster.stream_output(max_file_size=max_file_size):
            sys.stdout.write(chunk)
            sys.stdout.flush()  # Ensure immediate output

    except Exception as e:
        console = Console(stderr=True)
        console.print(f"[red]Error:[/] {str(e)}")
        raise click.Abort()


@cli.command()
@click.option(
    "-p",
    "--path",
    "project_path",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the project directory",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output markdown file (default: {project_dir}_source.md)",
)
@click.option(
    "--summary/--no-summary", default=True, help="Show project stats in terminal output"
)
@click.option(
    "--max-file-size", default=1_000_000, type=int, help="Maximum file size in bytes"
)
@click.option(
    "-f", "--force", is_flag=True, help="Force overwrite existing output file"
)
@click.option(
    "--skip-common",
    is_flag=True,
    help="Skip commonly referenced files (LICENSE, CONTRIBUTING, etc.)",
)
@click.option(
    "--skip-files", multiple=True, help="Additional files or patterns to skip"
)
def snap(
    project_path, output_file, summary, max_file_size, force, skip_common, skip_files
):
    """Create a markdown snapshot of your project for AI models."""
    try:
        # Generate default output filename based on project directory
        if output_file is None:
            project_name = Path(project_path).resolve().name
            output_file = Path(f"{project_name}_source.md")

        if output_file.exists() and not force:
            if not click.confirm(f"\nFile {output_file} already exists. Overwrite?"):
                rprint("[yellow]Operation cancelled.[/]")
                return

        rprint(Panel.fit("📸 Creating project snapshot...", border_style="blue"))

        paster = Aipaste(
            project_path=project_path,
            output_file=output_file,
            skip_common=skip_common,
            skip_files=skip_files,
        )
        markdown = paster.concatenate(
            max_file_size=max_file_size, summary=summary, token_estimate=False
        )

        output_file.write_text(markdown, encoding="utf-8")
        rprint(
            Panel.fit(
                f"✨ Snapshot created at [blue]{output_file}[/]", border_style="green"
            )
        )

    except Exception as e:
        rprint(Panel.fit(f"❌ Error: {str(e)}", border_style="red"))
        raise click.Abort()


@cli.command()
@click.argument("file", required=False, type=click.Path(dir_okay=False))
def tokens(file):
    """
    Print a detailed token analysis of a project snapshot or user-specified file.

    This refactors 'estimate' and 'analyze' into one command that:
      - Auto-detects the snapshot if none is provided
      - Prints file stats
      - Prints per-model token usage and context stats
    """
    try:
        # 1) Determine which file to process
        if not file:
            project_name = Path.cwd().name
            file = f"{project_name}_source.md"

        file_path = Path(file)
        if not file_path.exists():
            rprint(
                Panel.fit(
                    f"❌ No project snapshot found at '{file}'.\n"
                    f"Please run [yellow]`aipaste snap`[/] or provide a file name.\n",
                    border_style="red",
                )
            )
            raise click.Abort()

        # 2) Read the file
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # 3) Gather basic file stats
        total_chars = len(content)
        total_lines = len(lines)
        # Count code blocks by lines that start with triple backticks
        code_blocks = sum(1 for line in lines if line.strip().startswith("```")) // 2

        # 4) Estimate tokens for each model
        model_data = Aipaste.estimate_tokens(content)

        # 5) Print a detailed report
        rprint("\n[blue]Project File Statistics[/]")
        rprint(f"  • File Name: {file_path.name}")
        rprint(f"  • Characters: {total_chars:,}")
        rprint(f"  • Lines: {total_lines:,}")
        rprint(f"  • Code Blocks: {code_blocks}")

        rprint("\n[yellow]Model-Specific Token Estimates:[/]")
        for model, info in model_data.items():
            tokens = info["tokens"]
            max_ctx = info["max_context"]
            usage = info["usage_percent"]
            remaining = info["remaining_tokens"]
            rprint(f"  • {model}: [green]{tokens:,}[/] tokens")
            rprint(
                f"     ↳ Max Context: {max_ctx:,}  |  Usage: {usage:.1f}%  |  Remaining: {remaining:,}"
            )

        rprint(
            "\n[dim]Note: All values are approximate and may vary by actual model version or usage.[/]\n"
        )

    except Exception as e:
        rprint(Panel.fit(f"❌ Error: {str(e)}", border_style="red"))
        raise click.Abort()


@cli.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def completion(shell):
    """Generate shell completion script."""
    # (1) Detect if we are in a PyInstaller bundle
    if hasattr(sys, "_MEIPASS"):
        # If so, completions were placed into <_MEIPASS>/completions
        bundle_dir = Path(sys._MEIPASS)
    else:
        # (2) Otherwise, assume we're running from the repo root
        # Adjust as needed if your dev environment is different
        bundle_dir = Path(__file__).parent.parent
    # (3) Construct the path to the correct file
    completions_dir = bundle_dir / "completions"
    completion_file = completions_dir / f"aipaste.{shell}"
    # (4) Check existence & print
    if not completion_file.exists():
        rprint(f"[yellow]Warning:[/] Completion script for {shell} not available.")
        return
    click.echo(completion_file.read_text())


def main():
    cli()


if __name__ == "__main__":
    main()

# Main code for CLI using Typer

from pathlib import Path
from typing import Annotated  # Allows to add extra metadata to type of object

import typer
from rich.console import Console

from src.cli.chat import chat_command
from src.utils.config import Config

# Initialize a typer app instance
app = typer.Typer(
    name="kuro-bot",
    help="Welcome to kuro-bot, your personal AI assistant!",
    no_args_is_help=True,
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()


# Store workspace path in typer context
def workspace_callback(ctx: typer.Context, workspace: str) -> Path:
    ctx.ensure_object(dict)
    ctx.obj["workspace"] = Path(workspace)
    return Path(workspace)


# Callback allows to specify options for the main CLI, and not a particular command


@app.callback()
def main(
    ctx: typer.Context,
    workspace: str = typer.Option(
        "./default_workspace",
        "--workspace",
        "-w",
        help="Path to workspace directory.",
        callback=workspace_callback,
    ),
) -> None:
    # Configuration is loaded from workspace/config.user.yaml by default
    workspace_path = ctx.obj["workspace"]
    config_file = workspace_path / "config.user.yaml"

    if not config_file.exists():
        console.print(f"[yellow] No config found at {config_file}![/yellow]")
        raise typer.Exit(1)

    try:
        config = Config.load(workspace_path)
        ctx.obj["config"] = config
    except Exception as e:
        console.print(f"[red]Error loading config from {config_file} due to {e}[/red]")
        raise typer.Exit(1)


@app.command("chat")
def chat(
    ctx: typer.Context,
    agent: Annotated[
        str | None,
        typer.Option(
            "--agent", "-a", help="Agent ID which overrides default_agent from config"
        ),
    ] = None,
) -> None:
    # Start an interactive chat session
    chat_command(ctx, agent_id=agent)


if __name__ == "__main__":
    app()

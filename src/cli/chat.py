# We'll write a CLI chat command for interactive sessions with the bot
import asyncio

import typer  # Library for building CLI apps
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.core.agent import Agent
from src.core.agent_loader import AgentLoader
from src.utils.config import Config


# Class for interactive chat session
class ChatLoop:
    def __init__(self, config: Config, agent_id: str | None = None):
        self.config = config
        self.console = Console()

        # Load agent
        loader = AgentLoader(self.config)
        agent_id = agent_id or self.config.default_agent
        self.agent_def = loader.load(agent_id)

        # Create a new agent and session
        self.agent = Agent(self.agent_def, self.config)
        self.session = self.agent.new_session()

    # Function to get user input with a styled prompt by rich
    def get_user_input(self) -> str:
        prompt_text = Text("You", style="cyan")
        user_input = Prompt.ask(prompt_text, console=self.console)
        return user_input.strip()

    # Display agent response
    def display_agent_response(self, content: str) -> None:
        prefix = Text(f"{self.agent_def.id}: ", style="green")
        self.console.print(prefix, end="")
        self.console.print(content)

    # Run func for interactive chat loop
    async def run(self) -> None:
        self.console.print(
            Panel(
                Text("Welcome!", style="bold cyan"), title="Chat", border_style="cyan"
            )
        )
        self.console.print("Type :q to end the session!\n")

        try:
            while True:
                user_input = await asyncio.to_thread(self.get_user_input)

                if user_input == ":q":
                    self.console.print("\n[bold yellow]Goodbye![/bold yellow]\n")
                    break

                if not user_input:
                    continue

                try:
                    response = await self.session.chat(user_input)
                    self.display_agent_response(response)
                except Exception as e:
                    self.console.print(f"\n[bold red]Error:[/bold red] {e}\n")

        except (KeyboardInterrupt, EOFError) as e:
            self.console.print(f"\n[bold red]Error:[/bold red] {e}\n")


# Command to actually start interactive session
def chat_command(ctx: typer.Context, agent_id: str | None = None) -> None:
    config = ctx.obj.get("config")
    chat_loop = ChatLoop(config, agent_id)
    asyncio.run(chat_loop.run())

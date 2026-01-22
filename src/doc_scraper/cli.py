import typer
import asyncio
import os
import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Add path handling for imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doc_scraper.scraper import create_context_from_url

app = typer.Typer(help="Scrape context from a URL for LLM usage.")
console = Console()

@app.command()
def main(
    url: Optional[str] = typer.Argument(None, help="The URL to scrape."),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Directory to save the context file."),
    depth: int = typer.Option(10, "--depth", "-d", help="Maximum depth to crawl."),
    max_pages: int = typer.Option(300, "--max-pages", "-p", help="Maximum number of pages to crawl."),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Enable interactive mode."),
):
    """
    Scrape context from a URL.
    """
    if interactive and not url:
        url = Prompt.ask("Enter the URL to scrape")
    elif not url:
        console.print("[red]Error: URL is required.[/red]")
        raise typer.Exit(code=1)

    # Validate and normalize URL
    if not url.startswith("http://") and not url.startswith("https://"):
        console.print("[yellow]Warning: URL missing scheme, assuming https://[/yellow]")
        url = "https://" + url

    # Determine default output directory if not provided
    if interactive and output_dir is None:
        default_dir = "context"
        use_default = Confirm.ask(f"Save to default directory '{default_dir}'?", default=True)
        if use_default:
            output_dir = default_dir
        else:
            output_dir = Prompt.ask("Enter output directory")

    if output_dir is None:
        output_dir = "context"

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate filename based on URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace(".", "_")
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        filename = f"{domain}_context.md"
    else:
        filename = f"{domain}_{path}_context.md"

    output_file = os.path.join(output_dir, filename)

    if interactive:
        console.print(f"\n[bold]Configuration:[/bold]")
        console.print(f"URL: {url}")
        console.print(f"Output File: {output_file}")
        console.print(f"Max Depth: {depth}")
        console.print(f"Max Pages: {max_pages}")

        if Confirm.ask("Do you want to configure advanced settings?", default=False):
            depth = int(Prompt.ask("Enter max depth", default=str(depth)))
            max_pages = int(Prompt.ask("Enter max pages", default=str(max_pages)))

        if not Confirm.ask("Start scraping?", default=True):
            console.print("Aborted.")
            raise typer.Exit()

    # Run the scraper
    try:
        asyncio.run(create_context_from_url(url, output_file, depth, max_pages))
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
        if "Executable doesn't exist" in str(e) or "playwright" in str(e).lower():
            console.print("\n[yellow]It looks like Playwright browsers are not installed.[/yellow]")
            console.print("Please run: [bold green]playwright install[/bold green]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

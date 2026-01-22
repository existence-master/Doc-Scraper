import asyncio
from datetime import datetime
from urllib.parse import urlparse
import os
from rich.console import Console

from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    BFSDeepCrawlStrategy,
    FilterChain,
    DomainFilter,
    ContentTypeFilter,
    URLPatternFilter,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CacheMode
)

console = Console()

async def create_context_from_url(start_url: str, output_file: str, max_depth: int, max_pages: int):
    """
    Crawls a website starting from a given URL, scrapes content from child pages,
    and combines it into a single Markdown file for LLM context.

    Args:
        start_url (str): The initial URL to start crawling from.
        output_file (str): The path to the output Markdown file.
        max_depth (int): The maximum depth to crawl from the start URL.
        max_pages (int): The maximum number of pages to crawl.
    """
    console.print(f"[bold blue]Starting crawl at {start_url}...[/bold blue]")
    console.print(f"Max depth: {max_depth}, Max pages: {max_pages}")
    console.print(f"Output will be saved to: {output_file}")

    # Extract the base domain to keep the crawl focused
    parsed_url = urlparse(start_url)
    base_domain = parsed_url.netloc
    if not base_domain:
        console.print(f"[bold red]Error: Could not determine base domain from URL: {start_url}[/bold red]")
        return False

    console.print(f"Restricting crawl to domain: {base_domain}")
    # Also restrict to the starting path
    console.print(f"Also restricting crawl to path: {start_url}")

    # 1. Set up a filter chain to control which URLs are crawled
    filter_chain = FilterChain(filters=[
        # Only allow URLs from the same domain
        DomainFilter(allowed_domains=[base_domain]),
        # Only allow URLs that start with the initial path by adding a wildcard
        URLPatternFilter(patterns=[f"{start_url}*"]),
        # Only process standard web page content types
        ContentTypeFilter(allowed_types=['text/html', '.htm', '.php', '']) # Empty extension for root paths
    ])

    # 2. Configure a Markdown generator to produce clean content
    # PruningContentFilter helps remove boilerplate like headers, footers, etc.
    markdown_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter()
    )

    # 3. Set up the deep crawling strategy (Breadth-First Search)
    deep_crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=max_depth,
        max_pages=max_pages,
        filter_chain=filter_chain
    )

    # 4. Create the main configuration for the crawl run
    run_config = CrawlerRunConfig(
        deep_crawl_strategy=deep_crawl_strategy,
        markdown_generator=markdown_generator,
        # Use a cache to speed up development/re-runs if needed. BYPASS for fresh data.
        cache_mode=CacheMode.BYPASS,
        stream=True
    )

    all_markdown_content = []
    page_count = 0

    # 5. Initialize and run the crawler
    async with AsyncWebCrawler() as crawler:
        try:
            results_stream = await crawler.arun(url=start_url, config=run_config)

            async for result in results_stream:
                page_count += 1
                if result.success and result.markdown:
                    # Use the 'fit_markdown' if available (from PruningContentFilter),
                    # otherwise fall back to raw_markdown.
                    content = result.markdown.fit_markdown or result.markdown.raw_markdown
                    if content and content.strip():
                        console.print(f"  [green][SUCCESS][/green] Scraped content from: {result.url}")
                        formatted_content = (
                            f"---\n\n"
                            f"## Source: {result.url}\n\n"
                            f"{content.strip()}\n\n"
                        )
                        all_markdown_content.append(formatted_content)
                    else:
                        console.print(f"  [yellow][SKIPPED][/yellow] No content found on: {result.url}")
                else:
                    console.print(f"  [red][FAILED][/red] Could not process: {result.url} | Error: {result.error_message}")
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred during the crawl: {e}[/bold red]")
            return False

    # 6. Compile and write the final output file
    if all_markdown_content:
        header = (
            f"# Context File for {start_url}\n"
            f"Generated on: {datetime.now().isoformat()}\n"
            f"Total pages scraped: {len(all_markdown_content)}\n\n"
        )
        final_content = header + "".join(all_markdown_content)

        # Ensure directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)

        console.print(f"\n[bold green]✅ Successfully created context file at '{output_file}' with content from {len(all_markdown_content)} pages.[/bold green]")
        return True
    else:
        console.print("\n[bold red]❌ No content was scraped. The output file was not created.[/bold red]")
        return False

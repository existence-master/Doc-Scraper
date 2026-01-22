# doc-scraper

A Python tool to scrape website content for LLM context.

## Installation

```bash
pip install doc-scraper
```

## Post-Installation Setup

This tool uses `crawl4ai` which relies on Playwright. After installing the package, you need to install the browser binaries:

```bash
playwright install
```

Or if you are using the `crawl4ai` CLI directly:

```bash
crawl4ai-doctor
```

## Usage

```bash
doc-scraper <url>
```

Example:

```bash
doc-scraper https://docs.reducto.ai/
```

Follow the interactive prompts to configure the output directory and other settings.

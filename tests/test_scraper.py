import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from doc_scraper.scraper import create_context_from_url

@pytest.mark.asyncio
async def test_create_context_from_url_failure():
    """Test scraper handles failures gracefully."""
    with patch("doc_scraper.scraper.AsyncWebCrawler") as mock_crawler_cls:
        # Mock the context manager
        mock_instance = MagicMock()
        mock_instance.arun = AsyncMock(side_effect=Exception("Test Error"))

        mock_crawler_cls.return_value.__aenter__.return_value = mock_instance

        result = await create_context_from_url("http://example.com", "output.md", 1, 1)
        assert result is False

@pytest.mark.asyncio
async def test_create_context_from_url_success():
    """Test scraper handles success correctly."""
    with patch("doc_scraper.scraper.AsyncWebCrawler") as mock_crawler_cls:
        # Mock the context manager
        mock_instance = MagicMock()

        # Mock result stream
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.url = "http://example.com"
        mock_result.markdown.fit_markdown = "Test Content"
        mock_result.markdown.raw_markdown = "Test Content"

        # Create an async iterator for the results
        async def async_results_gen():
            yield mock_result

        # Mock arun to return the async iterator
        mock_instance.arun = AsyncMock(return_value=async_results_gen())

        mock_crawler_cls.return_value.__aenter__.return_value = mock_instance

        # Mock file writing to avoid actual file creation
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            result = await create_context_from_url("http://example.com", "output.md", 1, 1)
            assert result is True
            mock_open.assert_called_with("output.md", 'w', encoding='utf-8')

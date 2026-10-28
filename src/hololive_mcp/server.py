"""Hololive English MCP server.

Exposes talent listings, talent profiles, and recent news from the official
hololive English website to any MCP-compatible client over stdio.

Data is scraped from https://hololive.hololivepro.com/en.
"""

import logging

import requests
from bs4 import BeautifulSoup
from mcp.server.mcpserver import MCPServer

logger = logging.getLogger(__name__)

BASE_URL = "https://hololive.hololivepro.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
REQUEST_TIMEOUT = 15

mcp = MCPServer(
    "HololiveEN",
    title="hololive-mcp",
    description=(
        "Browse official hololive talent profiles and the latest news "
        "from the English version of hololive.hololivepro.com."
    ),
    website_url="https://hololive.hololivepro.com/en",
    version="0.1.0",
)


def _get_soup(path: str) -> BeautifulSoup:
    """Fetch a page from the hololive site and return a BeautifulSoup object."""
    url = f"{BASE_URL}{path}"
    logger.info("Fetching: %s", url)
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


@mcp.tool()
def list_talents() -> str:
    """Returns a formatted list of every talent listed on the official hololive English site — all generations and branches, including alumni — with their English name, Japanese name, and profile URL slug."""
    soup = _get_soup("/en/talents")
    talent_list = soup.select_one("ul.talent_list")
    if not talent_list:
        return "Could not find the talent list on the page."

    results = []
    for li in talent_list.find_all("li", recursive=False):
        a_tag = li.find("a", href=True)
        if not a_tag:
            continue
        href = a_tag["href"]
        # Extract slug from URL like .../en/talents/mori-calliope/
        slug = href.rstrip("/").split("/")[-1]

        h3 = li.find("h3")
        if h3:
            # The h3 contains the English name followed by a <span> with the Japanese name
            en_name = h3.contents[0].strip()
            jp_name_tag = h3.find("span")
            jp_name = jp_name_tag.text.strip() if jp_name_tag else ""
            results.append(f"- {en_name} ({jp_name}) | slug: {slug}")

    return "\n".join(results) if results else "No talents found."


@mcp.tool()
def get_talent_profile(talent_slug: str) -> str:
    """Fetches the profile page for a specific talent using their URL slug (e.g., 'mori-calliope', 'gawr-gura'). Returns their catchphrase, biography, and social links."""
    soup = _get_soup(f"/en/talents/{talent_slug}")
    right_box = soup.select_one(".right_box .bg_box")
    if not right_box:
        return f"Could not find profile data for slug: {talent_slug}"

    h1 = right_box.find("h1")
    name = h1.contents[0].strip() if h1 else talent_slug

    catch = right_box.select_one(".catch")
    catchphrase = catch.text.strip() if catch else "No catchphrase found."

    bio_tag = right_box.select_one(".txt")
    bio = bio_tag.get_text(separator="\n", strip=True) if bio_tag else "No biography found."

    sns_links = []
    for a in right_box.select(".t_sns a"):
        platform = a.text.strip()
        url = a.get("href", "#")
        sns_links.append(f"{platform}: {url}")

    return (
        f"**{name}**\n"
        f"Catchphrase: {catchphrase}\n\n"
        f"Biography:\n{bio}\n\n"
        f"Social Links:\n" + ("\n".join(sns_links) if sns_links else "None listed.")
    )


@mcp.tool()
def get_recent_news() -> str:
    """Fetches the latest headlines from the hololive English news page (up to 10 items). Note that each entry includes the full article body, not just the title."""
    soup = _get_soup("/en/news")
    # The news page typically lists articles in <li> or <article> elements.
    # Adjust the selector if the site's markup changes.
    news_items = soup.select("ul.news_list li, article.news_item")
    if not news_items:
        # Fallback: look for common heading links
        news_items = soup.select("h2 a, h3 a")

    results = []
    for item in news_items[:10]:  # Limit to the 10 most recent
        a_tag = item.find("a") if item.name != "a" else item
        if not a_tag or not a_tag.get("href"):
            continue
        title = a_tag.get_text(strip=True)
        href = a_tag["href"]
        if not href.startswith("http"):
            href = BASE_URL + href
        results.append(f"- [{title}]({href})")

    return "\n".join(results) if results else "No recent news found."


def main() -> None:
    """Run the MCP server over the stdio transport."""
    # Logging goes to stderr, which is safe for the stdio transport.
    logging.basicConfig(level=logging.INFO)
    mcp.run()


if __name__ == "__main__":
    main()

"""Markdown representation of rendered record details."""

from lxml import html
from markdownify import markdownify


def record_page_to_markdown(content: str, base_url: str) -> str:
    main = html.fromstring(content).xpath("//main")[0]
    for element in main.xpath(
        ".//script | .//style | .//nav | .//form | .//button | .//input"
        " | .//select | .//textarea | .//*[@hidden] | .//*[@aria-hidden='true']"
        " | .//*[contains(concat(' ', normalize-space(@class), ' '),"
        " ' etna-feedback ')]"
    ):
        element.drop_tree()
    main.make_links_absolute(base_url)
    return (
        markdownify(
            html.tostring(main, encoding="unicode"),
            heading_style="ATX",
            bullets="-",
        ).strip()
        + "\n"
    )

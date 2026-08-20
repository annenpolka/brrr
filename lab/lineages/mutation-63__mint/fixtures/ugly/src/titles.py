"""Sitbone-shaped GitHub titles are identity-as-data, not USER=you."""


def extract_title(title):
    return title.split(" - ", 1)[0]


def crawl():
    extract_title(
        "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome"
    )

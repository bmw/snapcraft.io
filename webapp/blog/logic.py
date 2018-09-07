import re
import html

from datetime import datetime


def strip_excerpt(raw_html):
    """Remove tags from a html string

    :param raw_html: The HTML to strip

    :returns: The stripped string
    """
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return html.unescape(cleantext).replace("\n", "")


def transform_article(article, featured_image=None, author=None):
    """Transform article to include featured image, human readable
    date and a stipped version of the excerpt

    :param article: The raw article object
    :param featured_image: The featured image string

    :returns: The transformed article
    """
    article["image"] = featured_image

    article["author"] = author

    if "date_gmt" in article:
        article_gmt = article["date_gmt"]
        article_date = datetime.strptime(article_gmt, "%Y-%m-%dT%H:%M:%S")
        article["date"] = article_date.strftime("%-d %B %Y")

    if "excerpt" in article and "rendered" in article["excerpt"]:
        article["excerpt"]["raw"] = strip_excerpt(
            article["excerpt"]["rendered"]
        )[:340]

        # If the excerpt doesn't end before 340 characters, add ellipsis
        raw_article = article["excerpt"]["raw"]
        # split at the last 3 characters
        raw_article_start = raw_article[:-3]
        raw_article_end = raw_article[-3:]
        # for the last 3 characters replace any part of […]
        raw_article_end = raw_article_end.replace("[", "")
        raw_article_end = raw_article_end.replace("…", "")
        raw_article_end = raw_article_end.replace("]", "")
        # join it back up
        article["excerpt"]["raw"] = "".join(
            [raw_article_start, raw_article_end, " […]"]
        )

    return article


def change_url(feed, host):
    """Change insights urls to snapcraft.io/blog

    :param feed: String with urls

    :returns: A string with converted urls
    """
    url_regex = re.compile(
        "https:\/\/admin.insights.ubuntu.com(\/\d{4}\/\d{2}\/\d{2})?"
    )
    updated_feed = re.sub(url_regex, host, feed)

    return updated_feed


def get_tag_id_list(tags):
    """Get a list of tag ids from a list of tag dicts

    :param tags: Tag dict

    :returns: A list of ids
    """

    def get_id(tag):
        return tag["id"]

    return [get_id(tag) for tag in tags]


def is_in_series(tags):
    """Does the list of tags include a tag that starts 'sc:series'

    :param tags: Tag dict

    :returns: Boolean
    """
    for tag in tags:
        if tag["name"].startswith("sc:series"):
            return True

    return False


def exclude_categories(categories):
    whitelist = [
        'Articles',
        'Canonical News',
        'Case studies',
        'Design',
        'Desktop',
        'Development'
    ]

    return [item for item in categories if item['name'] in whitelist]

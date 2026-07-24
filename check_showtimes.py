"""
Checks the VOX Cinemas showtimes page for Spider-Man: Brand New Day
and sends a high-priority ntfy.sh push notification if "06 Aug" appears
as an available date tab.

Uses scrape.do (free tier) to render the page's JavaScript and fetch it
from a residential IP -- GitHub Actions' own IPs are blocked outright by
this site's CDN, so a direct request/browser from the runner never works.

Env vars required:
  NTFY_TOPIC     - your secret ntfy.sh topic name (acts like a password)
  SCRAPEDO_TOKEN - your free scrape.do API token
"""

import os
import urllib.request
import urllib.parse

URL = "https://egy.voxcinemas.com/movies/spider-man-brand-new-day#showtimes"
TARGET_DATE = "06 Aug"  # matches "Thu 06 Aug"
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
SCRAPEDO_TOKEN = os.environ["SCRAPEDO_TOKEN"]


def get_page_text() -> str:
    encoded_url = urllib.parse.quote(URL, safe="")
    api_url = (
        f"https://api.scrape.do/?token={SCRAPEDO_TOKEN}"
        f"&url={encoded_url}"
        f"&render=true"       # execute JS so the date tabs actually load
        f"&waitUntil=networkidle0"
        f"&customWait=4000"   # extra 4s for the showtimes widget to populate
    )
    req = urllib.request.Request(api_url)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def notify(title: str, message: str, priority: str = "urgent"):
    req = urllib.request.Request(
        url=f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": "rotating_light,movie_camera",
        },
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    html = get_page_text()

    if TARGET_DATE in html:
        notify(
            title="Spider-Man tickets: Aug 6 is UP",
            message=f'"{TARGET_DATE}" is now showing on the VOX showtimes page. Go book now: {URL}',
        )
        print(f"MATCH: found '{TARGET_DATE}' — notification sent.")
    else:
        print(f"No match yet for '{TARGET_DATE}'.")


if __name__ == "__main__":
    main()

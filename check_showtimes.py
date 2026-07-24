"""
Checks the VOX Cinemas showtimes page for Spider-Man: Brand New Day
and sends a high-priority ntfy.sh push notification if "05 Aug" appears
as an available date tab.

Env vars required:
  NTFY_TOPIC   - your secret ntfy.sh topic name (acts like a password)
"""

import os
import re
import sys
from playwright.sync_api import sync_playwright
import urllib.request

URL = "https://egy.voxcinemas.com/movies/spider-man-brand-new-day#showtimes"
TARGET_DATE = "06 Aug"   # matches "Thu 06 Aug" — weekday-agnostic on purpose
NTFY_TOPIC = os.environ["NTFY_TOPIC"]


def get_date_tabs_text() -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)

        # Try to click into the showtimes/booking tab if it's not already visible
        try:
            page.get_by_text("View Showtimes", exact=False).first.click(timeout=5000)
            page.wait_for_timeout(3000)
        except Exception:
            pass

        page.wait_for_timeout(3000)  # let showtimes widget finish loading
        body_text = page.inner_text("body")
        browser.close()
        return body_text


def notify(title: str, message: str, priority: str = "urgent"):
    req = urllib.request.Request(
        url=f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": priority,   # urgent = highest, makes phone buzz/sound insistently
            "Tags": "rotating_light,movie_camera",
        },
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    text = get_date_tabs_text()

    if TARGET_DATE in text:
        notify(
            title="Spider-Man tickets: Aug 6 is UP",
            message=f'"{TARGET_DATE}" is now showing on the VOX showtimes page. Go book now: {URL}',
        )
        print(f"MATCH: found '{TARGET_DATE}' — notification sent.")
    else:
        print(f"No match yet for '{TARGET_DATE}'.")


if __name__ == "__main__":
    main()

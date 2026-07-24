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
import time
from playwright.sync_api import sync_playwright
import urllib.request

URL = "https://egy.voxcinemas.com/movies/spider-man-brand-new-day#showtimes"
TARGET_DATE = "06 Aug"   # matches "Thu 06 Aug" — weekday-agnostic on purpose
NTFY_TOPIC = os.environ["NTFY_TOPIC"]

REAL_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def get_date_tabs_text() -> str:
    last_error = None

    for attempt in range(1, 4):  # up to 3 tries — the site's CDN sometimes blocks headless connections transiently
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    args=[
                        "--disable-blink-features=AutomationControlled",  # look less like an automated browser
                        "--disable-http2",  # GitHub-hosted runners sometimes can't negotiate HTTP/2 cleanly
                    ]
                )
                context = browser.new_context(
                    user_agent=REAL_USER_AGENT,
                    viewport={"width": 1366, "height": 900},
                    locale="en-US",
                    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                )
                page = context.new_page()
                page.goto(URL, wait_until="domcontentloaded", timeout=45000)

                # Try to click into the showtimes/booking tab if it's not already visible
                try:
                    page.get_by_text("View Showtimes", exact=False).first.click(timeout=5000)
                    page.wait_for_timeout(3000)
                except Exception:
                    pass

                page.wait_for_timeout(4000)  # let showtimes widget finish loading
                body_text = page.inner_text("body")
                browser.close()
                return body_text

        except Exception as e:
            last_error = e
            print(f"Attempt {attempt} failed: {e}")
            if attempt < 3:
                time.sleep(8)

    raise last_error


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

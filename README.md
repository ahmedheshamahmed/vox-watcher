VOX Showtimes Watcher
Checks the VOX Cinemas showtimes page for Spider-Man: Brand New Day every
15 minutes, and sends a high-priority push notification to your phone the
moment "06 Aug" appears as an available date.
Setup (10 minutes, no server needed)
1. Get a notification channel (ntfy.sh — free, no account)
Install the ntfy app on your phone (App Store / Play Store).
In the app, subscribe to a topic name of your choosing — make it random
and hard to guess, e.g. ahmad-vox-spiderman-8f3k2. Anyone who knows the
topic name can send to it, so don't use something guessable.
That's it — no login required.
2. Create a GitHub repo and upload these files
Go to github.com → New repository (can be private).
Upload these three files, keeping the folder structure:
check_showtimes.py
.github/workflows/check.yml
README.md
(Easiest: git init, git add ., git commit, git push — or drag-and-drop via the GitHub web UI, which preserves folders if you drop the whole vox-watcher folder.)
3. Add your ntfy topic as a secret
In the repo: Settings → Secrets and variables → Actions → New repository secret.
Name: NTFY_TOPIC
Value: the topic name you picked in step 1 (e.g. ahmad-vox-spiderman-8f3k2).
4. Done
GitHub will now run the check every 15 minutes automatically, for free
(public repos have unlimited free Actions minutes; private repos get 2,000
free minutes/month, and this uses well under that). You can also trigger it
manually anytime from the repo's Actions tab → "Check VOX showtimes" →
Run workflow.
When "06 Aug" shows up as a date tab, your phone will buzz with an urgent
ntfy notification and a link straight to the page.
Notes
It matches on the date "06 Aug" itself, not the weekday label (Aug 6,
2026 is a Thursday, so both line up here anyway).
If VOX changes their page structure, the script may need small tweaks.

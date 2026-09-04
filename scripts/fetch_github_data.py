import json
import os
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = os.getenv("GITHUB_USERNAME", "Aditya-oss-glitch")

OUTPUT = Path("data/github.json")

session = requests.Session()

session.headers.update({
    "Accept": "application/vnd.github+json",
    "User-Agent": f"{USERNAME}-profile-readme",
})


def github_get(url, params=None):
    response = session.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_profile():

    return github_get(
        f"https://api.github.com/users/{USERNAME}"
    )


def get_repositories():

    repositories = []

    page = 1

    while True:

        batch = github_get(
            f"https://api.github.com/users/{USERNAME}/repos",
            {
                "per_page": 100,
                "page": page,
                "type": "owner",
                "sort": "pushed",
            },
        )

        repositories.extend(batch)

        if len(batch) < 100:
            break

        page += 1

    return repositories


def get_events():

    try:

        return github_get(
            f"https://api.github.com/users/{USERNAME}/events/public",
            {
                "per_page": 30,
            },
        )

    except Exception:

        return []


def get_contributions():
    """Fetch GitHub contribution calendar with exact daily counts."""
    url = f"https://github.com/users/{USERNAME}/contributions"

    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # GitHub stores the exact daily contribution count in a
    # <tool-tip> whose `for` attribute matches the day's cell id.
    tooltips = {}

    for tooltip in soup.find_all("tool-tip"):
        target = tooltip.get("for")
        if target:
            tooltips[target] = tooltip.get_text(" ", strip=True)

    contributions = []

    for cell in soup.select("[data-date]"):
        date = cell.get("data-date")
        cell_id = cell.get("id")

        if not date:
            continue

        tooltip_text = tooltips.get(cell_id, "")

        # Exact count, e.g.:
        # "2 contributions on September 3rd."
        # "1 contribution on June 30th."
        # "No contributions on ..."
        match = re.search(
            r"(\d[\d,]*)\s+contributions?",
            tooltip_text,
            re.IGNORECASE,
        )

        if match:
            count = int(match.group(1).replace(",", ""))
        else:
            count = 0

        level = int(cell.get("data-level", 0) or 0)

        contributions.append({
            "date": date,
            "count": count,
            "level": level,
        })

    # Keep the same 370-day window used by the dashboard.
    contributions.sort(key=lambda x: x["date"])

    if len(contributions) > 370:
        contributions = contributions[-370:]

    # GitHub's page also exposes the overall contribution total.
    page_text = soup.get_text(" ", strip=True)

    total_match = re.search(
        r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year",
        page_text,
        re.IGNORECASE,
    )

    exact_total = (
        int(total_match.group(1).replace(",", ""))
        if total_match
        else sum(day["count"] for day in contributions)
    )

    return contributions, exact_total


def calculate_streaks(contributions):
    """Calculate current streak, longest streak, and best single-day count."""
    if not contributions:
        return 0, 0, 0

    days = sorted(
        contributions,
        key=lambda x: x["date"]
    )

    longest_streak = 0
    current_streak = 0
    running_streak = 0
    best_day = 0

    previous_date = None

    for day in days:
        count = int(day.get("count", 0))
        best_day = max(best_day, count)

        if count > 0:
            if (
                previous_date is not None
                and (
                    __import__("datetime").date.fromisoformat(day["date"])
                    - __import__("datetime").date.fromisoformat(previous_date)
                ).days == 1
            ):
                running_streak += 1
            else:
                running_streak = 1

            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 0

        previous_date = day["date"]

    # Current streak: count backwards from the most recent day.
    for day in reversed(days):
        if int(day.get("count", 0)) > 0:
            current_streak += 1
        else:
            break

    return current_streak, longest_streak, best_day



def calculate_languages(repositories):
    """Count languages used across owned repositories."""
    counter = Counter()

    for repository in repositories:
        if repository.get("fork"):
            continue

        language = repository.get("language")

        if language:
            counter[language] += 1

    return dict(counter.most_common())

def fetch_coding_profiles():
    result = {
        "leetcode": {
            "username": "FwSJ9mrfqJ",
            "solved": None,
            "rating": None,
            "rank": None,
        },
        "codeforces": {
            "username": "code1101master",
            "solved": None,
            "rating": None,
            "rank": None,
        },
    }

    # ============================================================
    # LEETCODE
    # ============================================================

    try:
        query = (
            "query { "
            "matchedUser(username: \"FwSJ9mrfqJ\") { "
            "profile { ranking } "
            "submitStatsGlobal { "
            "acSubmissionNum { difficulty count } "
            "} "
            "} "
            "userContestRanking(username: \"FwSJ9mrfqJ\") { "
            "rating globalRanking "
            "} "
            "}"
        )

        response = requests.post(
            "https://leetcode.com/graphql",
            json={"query": query},
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://leetcode.com/",
            },
            timeout=20,
        )

        if response.ok:
            payload = response.json()
            data = payload.get("data") or {}

            user = data.get("matchedUser")

            if user:
                stats = (
                    user
                    .get("submitStatsGlobal", {})
                    .get("acSubmissionNum", [])
                )

                for item in stats:
                    if item.get("difficulty") == "All":
                        result["leetcode"]["solved"] = item.get("count")
                        break

                result["leetcode"]["rank"] = (
                    user
                    .get("profile", {})
                    .get("ranking")
                )

            contest = data.get("userContestRanking")

            if contest:
                result["leetcode"]["rating"] = contest.get("rating")

                if contest.get("globalRanking"):
                    result["leetcode"]["rank"] = contest.get(
                        "globalRanking"
                    )

    except Exception as e:
        print(f"LeetCode fetch warning: {e}")

    # ============================================================
    # CODEFORCES PROFILE
    # ============================================================

    try:
        response = session.get(
            "https://codeforces.com/api/user.info",
            params={"handles": "code1101master"},
            timeout=20,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") == "OK":
            user = payload["result"][0]

            result["codeforces"]["rating"] = user.get("rating")
            result["codeforces"]["rank"] = user.get("rank")

    except Exception as e:
        print(f"Codeforces profile warning: {e}")

    # ============================================================
    # CODEFORCES SOLVED PROBLEMS
    # ============================================================

    try:
        response = session.get(
            "https://codeforces.com/api/user.status",
            params={"handle": "code1101master"},
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") == "OK":
            solved = set()

            for submission in payload.get("result", []):
                if submission.get("verdict") != "OK":
                    continue

                problem = submission.get("problem", {})

                contest_id = problem.get("contestId")
                index = problem.get("index")

                if contest_id is not None and index:
                    solved.add(f"{contest_id}-{index}")

            result["codeforces"]["solved"] = len(solved)

    except Exception as e:
        print(f"Codeforces solved warning: {e}")

    return result
def main():

    print(
        f"Fetching GitHub data for "
        f"{USERNAME}..."
    )

    profile = get_profile()

    repositories = get_repositories()

    events = get_events()

    contributions, exact_total = get_contributions()

    current_streak, longest_streak, best_day = (
        calculate_streaks(
            contributions
        )
    )

    languages = calculate_languages(
        repositories
    )

    owned_repositories = [
        repository
        for repository in repositories
        if not repository.get("fork")
    ]

    stars = sum(
        repository.get(
            "stargazers_count",
            0,
        )
        for repository in owned_repositories
    )

    activity = []

    for event in events[:8]:

        activity.append(
            {
                "type": event.get(
                    "type",
                    "",
                ),
                "repository": event.get(
                    "repo",
                    {}
                ).get(
                    "name",
                    "",
                ),
                "date": event.get(
                    "created_at",
                    "",
                ),
            }
        )

    data = {

        "username": USERNAME,

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "profile": {

            "name": (
                profile.get("name")
                or USERNAME
            ),

            "bio": (
                profile.get("bio")
                or ""
            ),

            "repositories": profile.get(
                "public_repos",
                0,
            ),

            "followers": profile.get(
                "followers",
                0,
            ),

            "following": profile.get(
                "following",
                0,
            ),

            "profile_url": profile.get(
                "html_url",
                "",
            ),
        },

        "stars": stars,

        "languages": languages,

        "activity": activity,

        "contributions": {

            "days": contributions,

            "total": exact_total,

            "current_streak": current_streak,

            "longest_streak": longest_streak,

            "best_day": best_day,
        },

        "coding": fetch_coding_profiles(),
    }

    OUTPUT.parent.mkdir(
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved {OUTPUT}"
    )


if __name__ == "__main__":
    main()

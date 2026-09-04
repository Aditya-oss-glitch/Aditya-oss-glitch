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

    url = (
        f"https://github.com/users/"
        f"{USERNAME}/contributions"
    )

    response = session.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    days = []

    # --------------------------------------------------------
    # Find contribution cells.
    # GitHub's HTML structure can change, so we don't depend
    # on aria-label being directly on the <td>.
    # --------------------------------------------------------

    cells = soup.select(
        "[data-date]"
    )

    for cell in cells:

        date_value = cell.get(
            "data-date"
        )

        if not date_value:
            continue

        # GitHub's contribution intensity.
        try:

            level = int(
                cell.get(
                    "data-level",
                    "0",
                )
                or 0
            )

        except ValueError:

            level = 0

        count = None

        # ----------------------------------------------------
        # Try aria-label on the cell.
        # ----------------------------------------------------

        labels = []

        if cell.get("aria-label"):
            labels.append(
                cell.get("aria-label")
            )

        # ----------------------------------------------------
        # Try aria-label/title on children.
        # ----------------------------------------------------

        for child in cell.find_all():

            if child.get("aria-label"):
                labels.append(
                    child.get("aria-label")
                )

            if child.get("title"):
                labels.append(
                    child.get("title")
                )

        # ----------------------------------------------------
        # Search all discovered labels.
        # ----------------------------------------------------

        for label in labels:

            match = re.search(
                r"(\d+)\s+contribution",
                label,
                re.IGNORECASE,
            )

            if match:

                count = int(
                    match.group(1)
                )

                break

        # ----------------------------------------------------
        # If GitHub doesn't expose the exact number in the
        # cell, use the level to identify activity.
        # ----------------------------------------------------

        if count is None:

            count = 1 if level > 0 else 0

        days.append(
            {
                "date": date_value,
                "count": count,
                "level": level,
            }
        )

    # --------------------------------------------------------
    # Remove duplicate dates.
    # --------------------------------------------------------

    unique = {}

    for day in days:

        unique[
            day["date"]
        ] = day

    days = list(
        unique.values()
    )

    days.sort(
        key=lambda item: item["date"]
    )

    # --------------------------------------------------------
    # Get the exact total shown by GitHub.
    #
    # Example:
    # "39 contributions in the last year"
    # --------------------------------------------------------

    page_text = soup.get_text(
        " ",
        strip=True,
    )

    total_match = re.search(
        r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year",
        page_text,
        re.IGNORECASE,
    )

    if total_match:

        exact_total = int(
            total_match.group(1).replace(
                ",",
                "",
            )
        )

    else:

        exact_total = sum(
            day["count"]
            for day in days
        )

    # --------------------------------------------------------
    # Store the exact total separately.
    # --------------------------------------------------------

    for day in days:

        day.setdefault(
            "count",
            0,
        )

    return days, exact_total

def calculate_streaks(days):

    active_dates = {
        item["date"]
        for item in days
        if item["count"] > 0
    }

    current = 0

    cursor = date.today()

    while cursor.isoformat() in active_dates:

        current += 1

        cursor -= timedelta(
            days=1
        )

    longest = 0

    running = 0

    best_day = 0

    for item in days:

        if item["count"] > 0:

            running += 1

            longest = max(
                longest,
                running,
            )

        else:

            running = 0

        best_day = max(
            best_day,
            item["count"],
        )

    return current, longest, best_day


def calculate_languages(repositories):

    totals = Counter()

    for repository in repositories:

        if repository.get("fork"):
            continue

        try:

            languages = github_get(
                repository["languages_url"]
            )

            totals.update(
                languages
            )

        except Exception:

            continue

    total_bytes = sum(
        totals.values()
    )

    if total_bytes == 0:
        return []

    languages = []

    for name, value in totals.most_common(6):

        percentage = (
            value
            / total_bytes
            * 100
        )

        languages.append(
            {
                "name": name,
                "bytes": value,
                "percent": round(
                    percentage,
                    1,
                ),
            }
        )

    return languages

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

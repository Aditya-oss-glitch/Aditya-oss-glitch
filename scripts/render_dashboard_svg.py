import re
import html
import json
from pathlib import Path

import random
DATA = Path("data/github.json")
OUTPUT = Path("profile-dashboard.svg")

WIDTH = 1500
HEIGHT = 1050

BG = "#0d1117"
PANEL = "#010409"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"

GREEN = "#3fb950"
BRIGHT_GREEN = "#56d364"
BLUE = "#58a6ff"
PURPLE = "#a371f7"
YELLOW = "#d29922"
RED = "#f85149"

GRAPH = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#56d364",
]


def esc(value):
    return html.escape(str(value or ""))


def text(
    x,
    y,
    value,
    size=15,
    color=TEXT,
    weight="400",
    anchor="start",
):
    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" '
        f'font-size="{size}px" '
        f'font-weight="{weight}" '
        f'fill="{color}" '
        f'text-anchor="{anchor}">'
        f'{esc(value)}</text>'
    )


def panel(x, y, width, height):
    return (
        f'<rect x="{x}" y="{y}" '
        f'width="{width}" height="{height}" '
        f'rx="9" ry="9" '
        f'fill="{PANEL}" '
        f'stroke="{BORDER}" '
        f'stroke-width="1"/>'
    )


def main():

    if not DATA.exists():
        raise SystemExit(
            "data/github.json not found. "
            "Run: python scripts/fetch_github_data.py"
        )

    data = json.loads(
        DATA.read_text(encoding="utf-8")
    )

    profile = data["profile"]
    contributions = data["contributions"]

    languages = data.get(
        "languages",
        [],
    )

    activity = data.get(
        "activity",
        [],
    )

    username = data.get(
        "username",
        "Aditya-oss-glitch",
    )

    total_contributions = contributions.get(
        "total",
        0,
    )

    current_streak = contributions.get(
        "current_streak",
        0,
    )

    longest_streak = contributions.get(
        "longest_streak",
        0,
    )

    repositories = profile.get(
        "repositories",
        0,
    )

    followers = profile.get(
        "followers",
        0,
    )

    following = profile.get(
        "following",
        0,
    )

    stars = data.get(
        "stars",
        0,
    )

    svg = []

    # ============================================================
    # SVG ROOT
    # ============================================================

    svg.append(
        f'''
<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
role="img"
aria-label="Aditya GitHub developer profile dashboard">
'''
    )

    # ============================================================
    # ANIMATIONS
    # ============================================================

    svg.append(
        '''
<defs>

<style>

.panel {
    animation: panelIn 0.65s ease-out both;
}

.portrait {
    animation: portraitIn 1s ease-out 0.15s both;
}

.stat {
    animation: statIn 0.55s ease-out both;
}
.graph-reveal {
    opacity: 0;
    animation: contributionReveal 0.18s ease-out forwards;
}

.contribution-final {
    opacity: 0;
    animation-name: contributionFinal;
    animation-duration: 0.01s;
    animation-fill-mode: forwards;
    pointer-events: none;
}

@keyframes contributionFinal {
    0% {
        opacity: 0;
    }

    100% {
        opacity: 1;
    }
}

.contribution-counter {
    opacity: 0;
    animation-name: contributionCounter;
    animation-timing-function: linear;
    animation-fill-mode: both;
    animation-iteration-count: 1;
    pointer-events: none;
}

@keyframes contributionCounter {
    0% {
        opacity: 0;
    }

    1% {
        opacity: 1;
    }

    99% {
        opacity: 1;
    }

    100% {
        opacity: 0;
    }
}

.contribution-counter-final {
    opacity: 0;
    animation: finalCounter 0.25s ease-out forwards;
    animation-delay: 20s;
}

.graph-scanner {
    fill: none;
    stroke: #39ff88;
    stroke-width: 1;
    opacity: 0;
    pointer-events: none;
    animation: scannerBox 0.55s ease-in-out forwards;
}

@keyframes contributionReveal {
    0% {
        opacity: 0;
    }

    35% {
        opacity: 1;
    }

    100% {
        opacity: 1;
    }
}

@keyframes scannerBox {
    0% {
        opacity: 0;
    }

    12% {
        opacity: 1;
    }

    88% {
        opacity: 1;
    }

    100% {
        opacity: 0;
    }
}

@keyframes counterAppear {
    0% {
        opacity: 0;
        transform: translateY(2px);
    }

    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes finalCounter {
    0% {
        opacity: 0;
    }

    100% {
        opacity: 1;
    }
}

@keyframes techLogoIn {

    from {
        opacity: 0;
        transform: scale(0.55);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }

}

@keyframes techFloat {

    from {
        transform: translate(0, 0);
    }

    to {
        transform: translate(0, -3px);
    }

}

.runtime-buffer {
    animation: terminalScroll 7.2s linear 0.05s both;
}

.runtime-text {
    opacity: 1;
}

.runtime-char {
    opacity: 0;
    animation: terminalCharIn 0.035s linear both;
}

.runtime-cursor {
    animation: cursorBlink 0.9s steps(2, end) infinite;
}

@keyframes terminalScroll {

    0% {
        transform: translateY(0);
    }

    16% {
        transform: translateY(0);
    }

    20% {
        transform: translateY(-21px);
    }

    31% {
        transform: translateY(-21px);
    }

    35% {
        transform: translateY(-42px);
    }

    46% {
        transform: translateY(-42px);
    }

    50% {
        transform: translateY(-63px);
    }

    61% {
        transform: translateY(-63px);
    }

    65% {
        transform: translateY(-84px);
    }

    100% {
        transform: translateY(-84px);
    }

}

@keyframes terminalCharIn {

    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }

}

@keyframes terminalLineIn {

    from {
        opacity: 0;
        transform: translateX(-4px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }

}

@keyframes panelIn {

    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }

}

@keyframes portraitIn {

    from {
        opacity: 0;
        transform: scale(0.97);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }

}

@keyframes statIn {

    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }

}

@keyframes cellIn {

    from {
        opacity: 0;
        transform: scale(0.25);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }

}

@keyframes barIn {

    from {
        transform: scaleX(0);
    }

    to {
        transform: scaleX(1);
    }

}

@keyframes cursorBlink {

    0%, 45% {
        opacity: 1;
    }

    46%, 100% {
        opacity: 0;
    }

}

@keyframes livePulse {

    0%, 100% {
        opacity: 0.45;
    }

    50% {
        opacity: 1;
    }

}

@keyframes scan {

    from {
        transform: translateY(0);
    }

    to {
        transform: translateY(900px);
    }

}


/* ============================================================
   TECH STACK // ZERO-GRAVITY INTERACTION
   ============================================================ */

.tech-orb {
    transform-box: fill-box;
    transform-origin: center;
    pointer-events: all;
    cursor: pointer;
    animation:
        techDrift var(--duration) ease-in-out var(--delay) infinite alternate;
    transition:
        filter 0.18s ease,
        opacity 0.18s ease;
    will-change: transform;
}

.tech-hitbox {
    pointer-events: all;
    opacity: 0;
}

.tech-orb:hover {
    animation-play-state: paused;
    transform: scale(var(--hover-scale)) translateY(-2px);
    filter:
        drop-shadow(0 0 5px rgba(163, 113, 247, 0.38))
        drop-shadow(0 0 11px rgba(163, 113, 247, 0.16));
}

.tech-orb:hover .tech-logo {
    filter:
        drop-shadow(0 0 4px rgba(163, 113, 247, 0.30));
}

@keyframes techDrift {
    0% {
        transform: translate(0, 0);
    }

    50% {
        transform: translate(
            calc(var(--dx) * 0.45),
            calc(var(--dy) * 0.45)
        );
    }

    100% {
        transform: translate(
            var(--dx),
            var(--dy)
        );
    }
}

@media (prefers-reduced-motion: reduce) {
    .tech-orb {
        animation: none;
    }
}

</style>

</defs>
'''
    )

    # ============================================================
    # BACKGROUND
    # ============================================================

    svg.append(
        f'''
<rect
x="0"
y="0"
width="{WIDTH}"
height="{HEIGHT}"
fill="{BG}"/>
'''
    )

    svg.append(
        f'''
<rect
x="10"
y="10"
width="{WIDTH - 20}"
height="{HEIGHT - 20}"
rx="14"
fill="none"
stroke="{BORDER}"
stroke-width="1"/>
'''
    )

    # ============================================================
    # TOP TERMINAL BAR
    # ============================================================

    svg.append(
        text(
            38,
            48,
            "●",
            18,
            RED,
        )
    )

    svg.append(
        text(
            65,
            48,
            "●",
            18,
            YELLOW,
        )
    )

    svg.append(
        text(
            92,
            48,
            "●",
            18,
            GREEN,
        )
    )

    svg.append(
        text(
            125,
            48,
            f"{username}@github:~",
            17,
            GREEN,
            "700",
        )
    )

    svg.append(
        text(
            WIDTH - 210,
            48,
            "UPDATED",
            11,
            MUTED,
            "700",
        )
    )

    svg.append(
        '<circle '
        f'class="live-dot" '
        f'cx="{WIDTH - 130}" '
        f'cy="42" '
        f'r="5" '
        f'fill="{GREEN}"/>'
    )

    svg.append(
        text(
            WIDTH - 118,
            48,
            "LIVE",
            12,
            GREEN,
            "700",
        )
    )

    # ============================================================
    # LEFT PORTRAIT PANEL
    # ============================================================

    svg.append(
        f'''
<g
class="panel"
style="animation-delay:0.05s">

{panel(25, 70, 560, 820)}

'''
    )

    svg.append(
        text(
            48,
            105,
            "avi@github:~$ ./identity.sh",
            16,
            BLUE,
            "700",
        )
    )



    # ------------------------------------------------------------
    # INLINE ASCII PORTRAIT
    # ------------------------------------------------------------

    ascii_file = Path("avi-ascii.svg")

    if ascii_file.exists():
        ascii_svg = ascii_file.read_text(encoding="utf-8")

        start_svg = ascii_svg.find(">") + 1
        end_svg = ascii_svg.rfind("</svg>")

        if start_svg > 0 and end_svg > start_svg:
            ascii_content = ascii_svg[start_svg:end_svg]

            svg.append(
                f'''
    <svg
        x="45"
        y="120"
        width="520"
        height="560"
        viewBox="0 0 770 806"
        preserveAspectRatio="xMidYMid meet"
        class="portrait">

        {ascii_content}

    </svg>
    '''
            )

    # ============================================================
    # LIVE BUILD / RUNTIME LOG
    # ============================================================

    coding = data.get("coding", {})
    leetcode = coding.get("leetcode", {})
    codeforces = coding.get("codeforces", {})

    profile_data = data.get("profile", {})

    repo_count = (
        profile_data.get("public_repos")
        or profile_data.get("repos")
        or profile_data.get("repositories")
        or 0
    )

    activity_count = len(data.get("activity", []))

    lc_solved = leetcode.get("solved")
    lc_rank = leetcode.get("rank")
    lc_rating = leetcode.get("rating")

    cf_solved = codeforces.get("solved")
    cf_rating = codeforces.get("rating")
    cf_rank = codeforces.get("rank")

    lc_solved_display = "—" if lc_solved is None else f"{lc_solved:,}"
    lc_rank_display = "—" if lc_rank is None else f"#{lc_rank:,}"
    lc_rating_display = "UNRATED" if lc_rating is None else str(lc_rating)

    cf_solved_display = "—" if cf_solved is None else f"{cf_solved:,}"
    cf_rating_display = "UNRATED" if cf_rating is None else str(cf_rating)
    cf_rank_display = "—" if cf_rank is None else f"#{cf_rank:,}"

    runtime_logs = [
        ("$ profile --build", BLUE),
        ("[OK] identity loaded", GREEN),
        (
            f"[OK] github synchronized :: {repo_count} repos / {stars} stars",
            GREEN,
        ),
        (
            f"[OK] contributions :: {total_contributions:,}",
            GREEN,
        ),
        (
            f"[OK] streak metrics :: {current_streak} / {longest_streak}",
            GREEN,
        ),
        (
            "[OK] stack resolved :: profile source",
            GREEN,
        ),
        (
            f"[OK] coding profiles :: LC {lc_solved_display} / CF {cf_solved_display}",
            GREEN,
        ),
        (
            f"[OK] activity stream :: {activity_count} events",
            GREEN,
        ),
        (
            "> system ready",
            GREEN,
        ),
    ]

    svg.append(
        f"""
<clipPath id="runtimeTerminalClip">
    <rect
        x="45"
        y="735"
        width="520"
        height="125"
        rx="8"/>
</clipPath>

<g clip-path="url(#runtimeTerminalClip)">
    <g class="runtime-buffer">
"""
    )

    terminal_x = 65
    first_y = 758
    line_height = 21
    runtime_delays = [0.05, 0.12, 0.20, 0.40, 0.50, 0.55, 0.60, 0.68, 0.76]

    for i, (line, color) in enumerate(runtime_logs):

        delay = runtime_delays[i]

        safe_line = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        char_delay = delay

        chars = []
        for char in safe_line:
            if char == " ":
                char = "&#160;"

            chars.append(
                f'<tspan class="runtime-char" '
                f'style="animation-delay:{char_delay:.3f}s">{char}</tspan>'
            )

            char_delay += 0.035

        svg.append(

            f"""
<text
x="{terminal_x}"
y="{first_y + i * line_height}"
font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace"
font-size="12px"
font-weight="{'700' if i == 0 else '400'}"
fill="{color}"
text-anchor="start"
class="runtime-text"
style="animation-delay:{delay:.2f}s">{safe_line}</text>
"""
        )

    svg.append(
        f"""
    </g>

    
</g>
"""
    )

    svg.append("</g>")
    # ============================================================
    # PROFILE PANEL
    # ============================================================

    svg.append(
        f'''
<g
class="panel"
style="animation-delay:0.12s">

{panel(610, 70, 865, 210)}

'''
    )

    svg.append(
        text(
            635,
            112,
            "avi@github:~$ whoami",
            24,
            BLUE,
            "700",
        )
    )

    # cursor

    svg.append(
        f'''
<rect
class="cursor"
x="858"
y="91"
width="12"
height="25"
rx="1"
fill="{TEXT}"/>
'''
    )

    profile_rows = [
        (
            "USER",
            profile.get(
                "name",
                username,
            ),
            GREEN,
        ),
        (
            "ROLE",
            "Computer Science Student / Developer",
            YELLOW,
        ),
        (
            "FOCUS",
            "DSA  •  AI/ML  •  MERN  •  Cloud",
            PURPLE,
        ),
        (
            "STATUS",
            "● Building & Learning",
            GREEN,
        ),
    ]

    y = 153

    for label, value, color in profile_rows:

        svg.append(
            text(
                635,
                y,
                label,
                13,
                color,
                "700",
            )
        )

        svg.append(
            text(
                755,
                y,
                value,
                15,
                GREEN if label == "STATUS" else TEXT,
            )
        )

        y += 31

    svg.append("</g>")

    days = contributions.get(
        "days",
        [],
    )

    # ============================================================
    # CONTRIBUTION COUNTER
    # ============================================================

    window_total = sum(
        int(day.get("count", 0))
        for day in days
    )

    counter_value = total_contributions - window_total

    counter_events = []
    counter_time = 0.8

    for row in range(7):

        for column in range(53):

            index = column * 7 + row

            if index >= len(days):
                continue

            day = days[index]

            count = int(
                day.get("count", 0)
            )

            if count == 0:
                counter_time += 0.055
                continue

            counter_time += 0.50
            counter_value += count

            counter_events.append(
                (
                    counter_time,
                    counter_value,
                )
            )

    # ============================================================
    # QUICK STATS
    # ============================================================

    stats = [
        (
            "CONTRIBUTIONS",
            total_contributions,
            GREEN,
        ),
        (
            "LEETCODE",
            lc_solved_display,
            BLUE,
        ),
        (
            "CODEFORCES",
            cf_solved_display,
            PURPLE,
        ),
        (
            "STARS",
            stars,
            YELLOW,
        ),
    ]

    for i, (label, value, color) in enumerate(stats):

        x = 610 + i * 214

        svg.append(
            f'''
<g
class="stat"
style="animation-delay:{0.20 + i * 0.07:.2f}s">

{panel(x, 300, 198, 100)}

'''
        )

        svg.append(
            text(
                x + 18,
                330,
                label,
                11,
                MUTED,
                "700",
            )
        )

        # Contribution counter is synchronized with the scanner.
        if label == "CONTRIBUTIONS":

            for _i, (_time, _value) in enumerate(counter_events):

                if _i + 1 < len(counter_events):
                    _next_time = counter_events[_i + 1][0]
                else:
                    _next_time = _time + 1.0

                _duration = max(
                    0.03,
                    _next_time - _time - 0.01,
                )

                svg.append(
                    f'<text '
                    f'class="contribution-counter" '
                    f'x="{x + 18}" '
                    f'y="372" '
                    f'fill="{color}" '
                    f'style="'
                    f'animation-delay:{_time:.3f}s;'
                    f'animation-duration:{_duration:.3f}s'
                    f'">'
                    f'{_value:,}'
                    f'</text>'
                )

            # Keep the final real total visible after the scanner finishes.
            if counter_events:
                _final_time = counter_events[-1][0]
                _final_duration = 0.01

                svg.append(
                    f'<text '
                    f'class="contribution-final" '
                    f'x="{x + 18}" '
                    f'y="372" '
                    f'fill="{color}" '
                    f'style="'
                    f'animation-delay:{_final_time + 0.01:.3f}s'
                    f'">'
                    f'{total_contributions:,}'
                    f'</text>'
                )

        else:
            svg.append(
                text(
                    x + 18,
                    372,
                    str(value) if label in ("LEETCODE", "CODEFORCES") else f"{value:,}",
                    27,
                    color,
                    "700",
                )
            )

        if label == "LEETCODE":
            svg.append(
                text(
                    x + 18,
                    389,
                    "PROBLEMS SOLVED",
                    8,
                    MUTED,
                    "700",
                )
            )

            svg.append(
                text(
                    x + 105,
                    372,
                    lc_rank_display,
                    13,
                    BLUE,
                    "700",
                )
            )

            svg.append(
                text(
                    x + 105,
                    389,
                    "RANK",
                    8,
                    MUTED,
                    "700",
                )
            )

        elif label == "CODEFORCES":
            svg.append(
                text(
                    x + 18,
                    389,
                    "PROBLEMS SOLVED",
                    8,
                    MUTED,
                    "700",
                )
            )

            svg.append(
                text(
                    x + 105,
                    372,
                    cf_rating_display,
                    13,
                    PURPLE,
                    "700",
                )
            )

            svg.append(
                text(
                    x + 105,
                    389,
                    "RATING",
                    8,
                    MUTED,
                    "700",
                )
            )

        svg.append("</g>")

    # ============================================================
    # CONTRIBUTION GRAPH
    # ============================================================

    svg.append(
        f'''
<g
class="panel"
style="animation-delay:0.40s">

{panel(610, 420, 865, 250)}

'''
    )

    svg.append(
        text(
            635,
            455,
            "GITHUB CONTRIBUTION GRAPH",
            15,
            GREEN,
            "700",
        )
    )

    svg.append(
        text(
            1445,
            455,
            "53 WEEKS",
            11,
            MUTED,
            "700",
            "end",
        )
    )

    days = days[-371:]

    start_x = 635
    start_y = 485

    cell_width = 13
    cell_height = 13

    # ============================================================
    # CONTRIBUTION GRID + ROW-BY-ROW SCANNER
    # ============================================================

    # ------------------------------------------------------------
    # CONTRIBUTION GRID
    # ------------------------------------------------------------

    scanner_index = 0
    scanner_time = 0.8
    scan_delays = []

    for row in range(7):

        for column in range(53):

            index = column * 7 + row

            if index >= len(days):
                continue

            item = days[index]

            level = int(
                item.get(
                    "level",
                    0,
                )
            )

            level = max(
                0,
                min(
                    5,
                    level,
                ),
            )

            x = start_x + column * cell_width
            y = start_y + row * cell_height

            # Save the exact moment the scanner reaches this box.
            scan_delays.append(scanner_time)

            # ----------------------------------------------------
            # Contribution box + native GitHub-style tooltip.
            # ----------------------------------------------------

            count = int(
                item.get(
                    "count",
                    0,
                )
            )

            date_value = item.get(
                "date",
                "",
            )

            try:
                from datetime import datetime

                date_display = datetime.strptime(
                    date_value,
                    "%Y-%m-%d",
                ).strftime("%B %-d, %Y")

            except ValueError:
                date_display = date_value

            if count == 1:
                tooltip = (
                    f"{count} contribution on "
                    f"{date_display}"
                )
            else:
                tooltip = (
                    f"{count} contributions on "
                    f"{date_display}"
                )

            svg.append(
                f'<g class="graph-day">'
                f'<title>{esc(tooltip)}</title>'
            )

            # Every box starts black.
            svg.append(
                f'<rect '
                f'x="{x}" '
                f'y="{y}" '
                f'width="10" '
                f'height="10" '
                f'rx="2" '
                f'fill="#101418"/>'
            )

            # Valid contribution appears when scanner reaches it.
            if level > 0:

                delay = scanner_time

                svg.append(
                    f'<rect '
                    f'class="graph-reveal" '
                    f'x="{x}" '
                    f'y="{y}" '
                    f'width="10" '
                    f'height="10" '
                    f'rx="2" '
                    f'fill="{GRAPH[level]}" '
                    f'style="animation-delay:{delay:.3f}s"/>'
                )

                # Scanner pauses on a valid contribution.
                scanner_time += 0.50

            # Empty boxes are passed quickly.
            scanner_time += 0.055

            svg.append("</g>")

            scanner_index += 1

    # ------------------------------------------------------------
    # THIN GREEN SCANNER
    # ------------------------------------------------------------

    scanner_index = 0

    for row in range(7):

        for column in range(53):

            index = column * 7 + row

            if index >= len(days):
                continue

            item = days[index]

            level = int(
                item.get(
                    "level",
                    0,
                )
            )

            level = max(
                0,
                min(
                    5,
                    level,
                ),
            )

            x = start_x + column * cell_width
            y = start_y + row * cell_height

            delay = scan_delays[scanner_index]

            # Valid boxes get a longer scanner dwell.
            if level > 0:
                duration = 0.50
            else:
                duration = 0.055

            svg.append(
                f'<rect '
                f'class="graph-scanner" '
                f'x="{x}" '
                f'y="{y}" '
                f'width="10" '
                f'height="10" '
                f'rx="2" '
                f'style="'
                f'animation-delay:{delay:.3f}s;'
                f'animation-duration:{duration:.3f}s'
                f'"/>'
            )

            scanner_index += 1

    svg.append(
        text(
            635,
            625,
            f"Current streak: {current_streak} days",
            12,
            MUTED,
        )
    )

    svg.append(
        text(
            870,
            625,
            f"Longest: {longest_streak} days",
            12,
            MUTED,
        )
    )

    svg.append(
        text(
            1090,
            625,
            f"Repositories: {repositories:,}",
            12,
            MUTED,
        )
    )

    svg.append("</g>")

    # ============================================================
    # STREAK PANEL
    # ============================================================

    svg.append(
        f'''
<g
class="panel"
style="animation-delay:0.50s">

{panel(610, 700, 275, 190)}

'''
    )

    svg.append(
        text(
            635,
            735,
            "STREAK STATS",
            14,
            YELLOW,
            "700",
        )
    )

    svg.append(
        text(
            635,
            790,
            str(current_streak),
            34,
            TEXT,
            "700",
        )
    )

    svg.append(
        text(
            705,
            790,
            "CURRENT",
            11,
            MUTED,
        )
    )

    svg.append(
        text(
            635,
            840,
            str(longest_streak),
            28,
            TEXT,
            "700",
        )
    )

    svg.append(
        text(
            705,
            840,
            "LONGEST",
            11,
            MUTED,
        )
    )

    svg.append("</g>")

    # ============================================================
    # TECH STACK // PROFILE
    # ============================================================

    svg.append(
        f"""
    <g
    class="panel"
    style="animation-delay:0.55s">

    {panel(900, 700, 285, 190)}

    """
    )

    svg.append(
        text(
            925,
            735,
            "TECH STACK // PROFILE",
            14,
            PURPLE,
            "700",
        )
    )

    skills_file = Path("data/skills.json")
    skills_data = {}

    if skills_file.exists():
        try:
            skills_data = json.loads(
                skills_file.read_text(encoding="utf-8")
            )
        except Exception:
            skills_data = {}

    skill_groups = [
        ("languages", "LANG"),
        ("frontend", "FRONT"),
        ("backend", "BACK"),
        ("ai_ml", "AI/ML"),
        ("tools", "TOOLS"),
    ]

    logo_map = {
        "Python": "Py",
        "Java": "J",
        "C++": "C+",
        "JavaScript": "JS",
        "TypeScript": "TS",
        "HTML": "</>",
        "CSS": "#",
        "React": "R",
        "Node.js": "N",
        "AI/ML": "AI",
        "Git": "G",
        "GitHub": "GH",
    }

    logo_colors = {
        "Python": "#3776AB",
        "Java": "#ED8B00",
        "C++": "#00599C",
        "JavaScript": "#F7DF1E",
        "TypeScript": "#3178C6",
        "HTML": "#E34F26",
        "CSS": "#1572B6",
        "React": "#61DAFB",
        "Node.js": "#339933",
        "AI/ML": PURPLE,
        "Git": "#F05032",
        "GitHub": TEXT,
    }

    stack = []

    for group, label in skill_groups:
        for skill in skills_data.get(group, []):
            if skill not in [item[0] for item in stack]:
                stack.append((skill, label))

    # ------------------------------------------------------------
    # Floating technology logos
    # ------------------------------------------------------------

    logo_files = {
        "Python": "python.svg",
        "Java": "java.svg",
        "C++": "cplusplus.svg",
        "JavaScript": "javascript.svg",
        "HTML": "html5.svg",
        "CSS": "css.svg",
        "React": "react.svg",
        "Node.js": "nodedotjs.svg",
        "Git": "git.svg",
        "GitHub": "github.svg",
        "AI/ML": "ai.svg",
    }

    logo_colors = {
        "Python": "#3776AB",
        "Java": "#ED8B00",
        "C++": "#00599C",
        "JavaScript": "#F7DF1E",
        "HTML": "#E34F26",
        "CSS": "#1572B6",
        "React": "#61DAFB",
        "Node.js": "#339933",
        "Git": "#F05032",
        "GitHub": "#F0F0F0",
        "AI/ML": PURPLE,
    }

    def load_logo(filename, color):
        logo_path = Path("assets/tech-logos") / filename

        if not logo_path.exists():
            print(f"WARNING: missing logo: {logo_path}")
            return None

        raw = logo_path.read_text(encoding="utf-8")

        # Extract everything inside the root SVG.
        start_tag = raw.find("<svg")
        start_content = raw.find(">", start_tag)
        end_tag = raw.rfind("</svg>")

        if start_tag == -1 or start_content == -1 or end_tag == -1:
            print(f"WARNING: invalid SVG: {logo_path}")
            return None

        content = raw[start_content + 1:end_tag]

        # Remove metadata/title; only the visual paths are needed.
        content = re.sub(
            r"<title>.*?</title>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Resolve currentColor if an icon uses it.
        content = content.replace("currentColor", color)

        return content.strip()

    # ------------------------------------------------------------
    # Build stack directly from data/skills.json.
    # skills.json remains the source of truth.
    # ------------------------------------------------------------

    stack = []

    for group, label in skill_groups:
        for skill in skills_data.get(group, []):
            if skill not in [item[0] for item in stack]:
                stack.append((skill, label))

    count = len(stack)

    # Show compact technology names when the stack is small.
    # With 15+ technologies, logos become icon-only to avoid clutter.
    show_labels = count < 15

    # ------------------------------------------------------------
    # Organic responsive Tech Stack packing.
    #
    # The panel behaves like a container being filled from the
    # bottom upward. Positions are deterministic-random rather
    # than grid-based, while collision checks keep everything clean.
    # ------------------------------------------------------------

    count = len(stack)
    show_labels = count < 15

    # Existing Tech Stack panel content area.
    area_x = 925
    area_y = 750
    area_w = 235
    area_h = 135

    # Deterministic randomness: same skills -> stable composition.
    rng = random.Random(1101 + count * 37)

    # More skills means the container naturally compresses.
    if count <= 4:
        base_size = 40
    elif count <= 7:
        base_size = 34
    elif count <= 10:
        base_size = 33
    elif count <= 12:
        base_size = 31
    elif count <= 14:
        base_size = 27
    else:
        base_size = 19

    # Repeated sizes make the composition feel intentional rather
    # than every logo having a completely different scale.
    size_variations = [
        1.00, 1.00, 0.92, 1.08,
        0.96, 1.04, 1.00, 0.90,
        1.06, 0.95, 1.02, 0.93,
    ]

    def build_positions(current_size):
        items = []

        # Bottom -> top priority.
        # Earlier candidates are concentrated toward the bottom,
        # but X remains randomized.
        candidates = []

        for layer in range(18):
            layer_y = area_y + area_h - 10 - layer * 6

            if layer_y < area_y + 8:
                break

            for _ in range(32):
                cx = rng.uniform(
                    area_x + current_size / 2 + 3,
                    area_x + area_w - current_size / 2 - 3,
                )

                # Small vertical jitter keeps the layout organic.
                cy = layer_y + rng.uniform(-4, 4)

                candidates.append((cx, cy, layer))

        placed = []

        # Place larger/important-looking items first, while retaining
        # the original skills.json ordering for the final assignment.
        for i, (skill, group) in enumerate(stack):

            size = current_size * size_variations[i % len(size_variations)]

            # Label dimensions.
            if show_labels:
                label_half = max(15, len(skill) * 3.15)
                label_height = 13
            else:
                label_half = size / 2
                label_height = 0

            radius = size / 2

            best = None
            best_score = None

            # Try many randomized candidates.
            for cx, cy, layer in candidates:

                left = cx - max(radius, label_half)
                right = cx + max(radius, label_half)
                top = cy - radius
                bottom = cy + radius + label_height

                if left < area_x or right > area_x + area_w:
                    continue

                if top < area_y or bottom > area_y + area_h:
                    continue

                collision = False

                for px, py, p_radius, p_label_half, p_label_height in placed:

                    p_left = px - max(p_radius, p_label_half)
                    p_right = px + max(p_radius, p_label_half)
                    p_top = py - p_radius
                    p_bottom = py + p_radius + p_label_height

                    gap = 3

                    if not (
                        right + gap < p_left
                        or left - gap > p_right
                        or bottom + gap < p_top
                        or top - gap > p_bottom
                    ):
                        collision = True
                        break

                if collision:
                    continue

                # Strong preference for lower positions first.
                # Secondary preference keeps the composition centred.
                lower_score = layer * 100
                centre_score = abs(cx - (area_x + area_w / 2))

                score = lower_score + centre_score * 0.12 + rng.random()

                if best_score is None or score < best_score:
                    best_score = score
                    best = (cx, cy)

            if best is None:
                return None

            cx, cy = best

            placed.append(
                (
                    cx,
                    cy,
                    radius,
                    label_half,
                    label_height,
                )
            )

            items.append(
                (
                    i,
                    cx,
                    cy,
                    size,
                    max(0, 17 - layer * 0.7),
                )
            )

            # Remove candidates close to this item so later logos
            # naturally fill the remaining space.
            candidates = [
                candidate
                for candidate in candidates
                if (
                    abs(candidate[0] - cx) > radius + 8
                    or abs(candidate[1] - cy) > radius + 4
                )
            ]

        return items

    # If the first attempt is crowded, progressively shrink all
    # logos until the entire stack fits.
    positions = None

    for scale in [1.00, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76]:
        positions = build_positions(base_size * scale)

        if positions is not None:
            break

    # Absolute fallback: evenly distributed safe points, only used
    # for an extremely crowded custom skills.json.
    if positions is None:
        positions = []

        for i in range(count):
            cols = max(1, min(5, count))
            col = i % cols
            row = i // cols
            rows = (count + cols - 1) // cols

            x = area_x + (col + 0.5) * area_w / cols
            y = area_y + area_h - (row + 0.5) * area_h / rows

            positions.append(
                (
                    i,
                    x,
                    y,
                    max(16, base_size * 0.72),
                    row,
                )
            )

    positions.sort(key=lambda item: item[0])

    for i, (skill, group) in enumerate(stack):

        _, x, y, size, row_from_bottom = positions[i]

        # Filling animation: bottom items appear first.
        fill_delay = (
            0.08
            + row_from_bottom * 0.045
            + (i % 4) * 0.025
        )

        # --------------------------------------------------------
        # Zero-gravity interaction wrapper
        #
        # The invisible hitbox is intentionally larger than the
        # logo, so hovering near an icon triggers its reaction.
        # This works when the SVG is rendered directly.
        # --------------------------------------------------------

        hover_radius = max(size * 0.82, 18)

        drift_x = ((i * 17) % 13) - 6
        drift_y = ((i * 11) % 11) - 5

        duration = 3.8 + ((i * 1.37) % 3.2)
        hover_scale = 1.10 + ((i % 3) * 0.025)

        svg.append(
            f"""
        <g
        class="tech-orb"
        style="
            --dx:{drift_x:.1f}px;
            --dy:{drift_y:.1f}px;
            --duration:{duration:.2f}s;
            --delay:{fill_delay:.3f}s;
            --hover-scale:{hover_scale:.2f};
        ">
            <circle
                cx="{x:.1f}"
                cy="{y:.1f}"
                r="{hover_radius:.1f}"
                fill="transparent"
                stroke="none"
                class="tech-hitbox"/>
        """
        )

        # --------------------------------------------------------
        # Real logo
        # --------------------------------------------------------

        logo_content = None

        filename = logo_files.get(skill)

        if filename:
            if skill == "AI/ML":
                # AI/ML is a complete SVG artwork rather than a
                # Simple Icons path. Preserve its own viewBox.
                ai_path = Path("assets/tech-logos/ai.svg")

                if ai_path.exists():
                    import base64

                    ai_data = base64.b64encode(
                        ai_path.read_bytes()
                    ).decode("ascii")

                    svg.append(
                        f"""
        <image
        x="{x - size / 2:.1f}"
        y="{y - size / 2:.1f}"
        width="{size:.1f}"
        height="{size:.1f}"
        href="data:image/svg+xml;base64,{ai_data}"
        preserveAspectRatio="xMidYMid meet"
        class="tech-logo"
        style="animation-delay:{fill_delay:.3f}s"/>
        """
                    )

                    logo_content = None

            else:
                logo_content = load_logo(
                    filename,
                    logo_colors.get(skill, TEXT),
                )

        if logo_content:

            svg.append(
                f"""
        <svg
        x="{x - size / 2:.1f}"
        y="{y - size / 2:.1f}"
        width="{size:.1f}"
        height="{size:.1f}"
        viewBox="0 0 24 24"
        preserveAspectRatio="xMidYMid meet"
        class="tech-logo"
        overflow="visible"
        fill="{logo_colors.get(skill, TEXT)}">
            {logo_content}
        </svg>
        """
            )

        # --------------------------------------------------------
        # Close zero-gravity interaction wrapper
        # --------------------------------------------------------

        # --------------------------------------------------------
        # Custom AI/ML logo
        # --------------------------------------------------------

        if skill == "AI/ML" and filename is None:

            r = size * 0.42

            svg.append(
                f"""
        <g
        class="tech-logo"
        transform="translate({x:.1f},{y:.1f})">

            <line
            x1="-{r * 0.75:.1f}"
            y1="-{r * 0.45:.1f}"
            x2="0"
            y2="0"
            stroke="{PURPLE}"
            stroke-width="2"/>

            <line
            x1="{r * 0.75:.1f}"
            y1="-{r * 0.45:.1f}"
            x2="0"
            y2="0"
            stroke="{PURPLE}"
            stroke-width="2"/>

            <line
            x1="-{r * 0.75:.1f}"
            y1="{r * 0.45:.1f}"
            x2="0"
            y2="0"
            stroke="{PURPLE}"
            stroke-width="2"/>

            <line
            x1="{r * 0.75:.1f}"
            y1="{r * 0.45:.1f}"
            x2="0"
            y2="0"
            stroke="{PURPLE}"
            stroke-width="2"/>

            <circle
            cx="0"
            cy="0"
            r="{r * 0.38:.1f}"
            fill="{PURPLE}"/>

            <circle
            cx="-{r * 0.75:.1f}"
            cy="-{r * 0.45:.1f}"
            r="{r * 0.16:.1f}"
            fill="{PURPLE}"/>

            <circle
            cx="{r * 0.75:.1f}"
            cy="-{r * 0.45:.1f}"
            r="{r * 0.16:.1f}"
            fill="{PURPLE}"/>

            <circle
            cx="-{r * 0.75:.1f}"
            cy="{r * 0.45:.1f}"
            r="{r * 0.16:.1f}"
            fill="{PURPLE}"/>

            <circle
            cx="{r * 0.75:.1f}"
            cy="{r * 0.45:.1f}"
            r="{r * 0.16:.1f}"
            fill="{PURPLE}"/>

            <text
            x="0"
            y="{r * 0.16:.1f}"
            font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace"
            font-size="{r * 0.48:.1f}px"
            font-weight="700"
            fill="#ffffff"
            text-anchor="middle">AI</text>

        </g>
        """
            )

        # Small labels are shown only when the stack is below
        # the 15-logo threshold.
        if show_labels:
            label_y = y + size / 2 + 9

            svg.append(
                text(
                    x,
                    label_y,
                    skill,
                    9,
                    MUTED,
                    "600",
                    "middle",
                )
            )

        # Close this logo's zero-gravity interaction wrapper.
        svg.append("</g>")

    # Close Tech Stack panel.
    svg.append("</g>")

    # ============================================================
    # RECENT ACTIVITY
    # ============================================================

    svg.append(
        f'''
<g
class="panel"
style="animation-delay:0.60s">

{panel(1200, 700, 275, 190)}

'''
    )

    svg.append(
        text(
            1225,
            735,
            "RECENT ACTIVITY",
            14,
            GREEN,
            "700",
        )
    )

    y = 770

    if activity:

        for event in activity[:5]:

            event_type = event.get(
                "type",
                "Event",
            )

            repository = event.get(
                "repository",
                "",
            )

            if len(repository) > 24:
                repository = (
                    repository[:21]
                    + "..."
                )

            line = (
                f"• {event_type}: "
                f"{repository}"
            )

            svg.append(
                text(
                    1225,
                    y,
                    line,
                    10,
                    TEXT,
                )
            )

            y += 23

    else:

        svg.append(
            text(
                1225,
                y,
                "• No recent public events",
                10,
                MUTED,
            )
        )

    svg.append("</g>")

    # ============================================================
    # FOOTER
    # ============================================================

    svg.append(
        f'''
<g
class="panel"
style="animation-delay:0.68s">

{panel(25, 915, 1450, 105)}

'''
    )

    svg.append(
        text(
            50,
            955,
            '$ echo "Keep building. The best is yet to come."',
            14,
            MUTED,
        )
    )

    svg.append(
        text(
            50,
            985,
            "— Aditya",
            12,
            BLUE,
        )
    )

    svg.append(
        text(
            1030,
            955,
            "CURRENT MISSION",
            13,
            GREEN,
            "700",
        )
    )

    svg.append(
        text(
            1030,
            985,
            "Building  •  Learning  •  Contributing",
            14,
            TEXT,
        )
    )

    svg.append("</g>")

    # ============================================================
    # SUBTLE SCANLINE
    # ============================================================

    svg.append(
        f'''
<rect
class="scanline"
x="20"
y="70"
width="{WIDTH - 40}"
height="2"
fill="{GREEN}"/>
'''
    )

    svg.append("</svg>")

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8",
    )

    print(
        f"Created {OUTPUT}"
    )

    print(
        f"Size: {WIDTH} x {HEIGHT}"
    )


if __name__ == "__main__":
    main()

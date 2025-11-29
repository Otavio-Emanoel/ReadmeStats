#!/usr/bin/env python3
"""
GitHub Stats SVG Generator

Fetches user statistics from GitHub API and generates an SVG card
with repos, followers, stars, avatar, PRs, commits, issues, and a grade.
"""

import os
import sys
import base64
import urllib.request
import urllib.error
import json
import re
from typing import Optional

# Constants
API_TIMEOUT = 30  # Timeout in seconds for API requests
MAX_REPOS_FOR_COMMITS = 10  # Limit repos checked for commits to improve performance


def fetch_github_data(url: str, token: Optional[str] = None) -> dict:
    """Fetch data from GitHub API."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Stats-Generator",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for URL: {url}")
        raise
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason} for URL: {url}")
        raise


def fetch_avatar_base64(avatar_url: str) -> str:
    """Fetch avatar image and convert to base64."""
    try:
        req = urllib.request.Request(
            avatar_url, headers={"User-Agent": "GitHub-Stats-Generator"}
        )
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
            image_data = response.read()
            return base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        print(f"Warning: Could not fetch avatar: {e}")
        return ""


def get_user_stats(username: str, token: Optional[str] = None) -> dict:
    """Fetch comprehensive user statistics from GitHub API."""
    # Get basic user info
    user_data = fetch_github_data(
        f"https://api.github.com/users/{username}", token
    )

    # Get repositories to calculate total stars
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    repos = fetch_github_data(repos_url, token)
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

    # Search for user's PRs (merged)
    prs_data = fetch_github_data(
        f"https://api.github.com/search/issues?q=author:{username}+type:pr",
        token,
    )

    # Search for user's issues
    issues_data = fetch_github_data(
        f"https://api.github.com/search/issues?q=author:{username}+type:issue",
        token,
    )

    # Get avatar as base64
    avatar_base64 = ""
    if user_data.get("avatar_url"):
        avatar_base64 = fetch_avatar_base64(user_data["avatar_url"])

    # Estimate commits (from repos)
    total_commits = 0
    for repo in repos[:MAX_REPOS_FOR_COMMITS]:
        try:
            commits_url = (
                f"https://api.github.com/repos/{username}/"
                f"{repo['name']}/commits?author={username}&per_page=1"
            )
            req = urllib.request.Request(
                commits_url,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "GitHub-Stats-Generator",
                    **({"Authorization": f"token {token}"} if token else {}),
                },
            )
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
                # Check Link header for total count
                link_header = response.headers.get("Link", "")
                if 'rel="last"' in link_header:
                    # Extract last page number
                    match = re.search(r"page=(\d+)>; rel=\"last\"", link_header)
                    if match:
                        total_commits += int(match.group(1))
                else:
                    # Count items in response
                    commits = json.loads(response.read().decode("utf-8"))
                    total_commits += len(commits)
        except Exception:
            pass  # Skip repos that fail

    return {
        "username": username,
        "name": user_data.get("name") or username,
        "avatar_base64": avatar_base64,
        "repos": user_data.get("public_repos", 0),
        "followers": user_data.get("followers", 0),
        "following": user_data.get("following", 0),
        "stars": total_stars,
        "prs": prs_data.get("total_count", 0),
        "issues": issues_data.get("total_count", 0),
        "commits": total_commits,
    }


def calculate_grade(stats: dict) -> str:
    """
    Calculate a grade based on GitHub activity.

    Scoring system:
    - Repos: 2 points each (max 50)
    - Followers: 1 point each (max 50)
    - Stars: 3 points each (max 75)
    - PRs: 5 points each (max 75)
    - Commits: 0.5 points each (max 50)
    - Issues: 2 points each (max 25)

    Grades:
    - S: 300+
    - A+: 200-299
    - A: 150-199
    - B+: 100-149
    - B: 75-99
    - C+: 50-74
    - C: 25-49
    - D: 0-24
    """
    score = 0
    score += min(stats.get("repos", 0) * 2, 50)
    score += min(stats.get("followers", 0) * 1, 50)
    score += min(stats.get("stars", 0) * 3, 75)
    score += min(stats.get("prs", 0) * 5, 75)
    score += min(stats.get("commits", 0) * 0.5, 50)
    score += min(stats.get("issues", 0) * 2, 25)

    if score >= 300:
        return "S"
    elif score >= 200:
        return "+A"
    elif score >= 150:
        return "A"
    elif score >= 100:
        return "+B"
    elif score >= 75:
        return "B"
    elif score >= 50:
        return "+C"
    elif score >= 25:
        return "C"
    else:
        return "D"


def generate_svg(stats: dict) -> str:
    """Generate SVG card with GitHub statistics."""
    grade = calculate_grade(stats)
    name = stats.get("name", stats.get("username", "User"))
    username = stats.get("username", "")

    # Avatar clipPath definition (goes inside defs)
    avatar_clip_def = ""
    if stats.get("avatar_base64"):
        avatar_clip_def = '''
    <clipPath id="avatarClip">
      <circle cx="50" cy="50" r="40"/>
    </clipPath>'''

    # Avatar image element (goes in the body)
    avatar_base64 = stats.get("avatar_base64", "")
    avatar_image = ""
    if avatar_base64:
        avatar_image = (
            f'<image x="10" y="10" width="80" height="80" '
            f'href="data:image/png;base64,{avatar_base64}" '
            f'clip-path="url(#avatarClip)"/>'
        )

    # Grade color
    grade_colors = {
        "S": "#FFD700",
        "+A": "#00FF00",
        "A": "#7CFC00",
        "+B": "#87CEEB",
        "B": "#ADD8E6",
        "+C": "#FFA500",
        "C": "#FF8C00",
        "D": "#FF6347",
    }
    grade_color = grade_colors.get(grade, "#FFFFFF")

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d1117;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#161b22;stop-opacity:1" />
    </linearGradient>{avatar_clip_def}
  </defs>

  <!-- Background -->
  <rect width="400" height="200" rx="10" fill="url(#bg)" stroke="#30363d" stroke-width="1"/>

  <!-- Avatar -->
  <circle cx="50" cy="50" r="40" fill="#21262d"/>
  {avatar_image}

  <!-- Name and Username -->
  <text x="100" y="40" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="18" font-weight="600">{name}</text>
  <text x="100" y="60" fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12">@{username}</text>

  <!-- Grade -->
  <circle cx="360" cy="45" r="30" fill="none" stroke="{grade_color}" stroke-width="3"/>
  <text x="360" y="52" fill="{grade_color}" font-family="Segoe UI, Ubuntu, sans-serif" font-size="20" font-weight="700" text-anchor="middle">{grade}</text>

  <!-- Stats Grid -->
  <g transform="translate(20, 100)">
    <!-- Row 1 -->
    <g transform="translate(0, 0)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">Repositories</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("repos", 0)}</text>
    </g>
    <g transform="translate(90, 0)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">Followers</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("followers", 0)}</text>
    </g>
    <g transform="translate(180, 0)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">Stars</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("stars", 0)}</text>
    </g>
    <g transform="translate(270, 0)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">PRs</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("prs", 0)}</text>
    </g>

    <!-- Row 2 -->
    <g transform="translate(0, 50)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">Commits</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("commits", 0)}</text>
    </g>
    <g transform="translate(90, 50)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">Issues</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("issues", 0)}</text>
    </g>
    <g transform="translate(180, 50)">
      <text fill="#8b949e" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11">Following</text>
      <text y="18" fill="#ffffff" font-family="Segoe UI, Ubuntu, sans-serif" font-size="16" font-weight="600">{stats.get("following", 0)}</text>
    </g>
  </g>
</svg>'''

    return svg_content


def main():
    """Main function to generate GitHub stats SVG."""
    # Get username from environment or command line
    username = os.environ.get("GITHUB_USERNAME") or os.environ.get(
        "GITHUB_REPOSITORY_OWNER"
    )
    if len(sys.argv) > 1:
        username = sys.argv[1]

    if not username:
        print("Error: No GitHub username provided.")
        print("Usage: python generate_stats.py <username>")
        print("Or set GITHUB_USERNAME environment variable.")
        sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN")
    output_path = os.environ.get("OUTPUT_PATH", "docs/stats.svg")

    print(f"Fetching stats for user: {username}")

    try:
        stats = get_user_stats(username, token)
        svg_content = generate_svg(stats)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write SVG file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"SVG generated successfully: {output_path}")
        print(f"Grade: {calculate_grade(stats)}")
        print(f"Stats: {json.dumps(stats, indent=2, default=str)}")

    except Exception as e:
        print(f"Error generating stats: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

import datetime
import html
import os

import requests
from dateutil.relativedelta import relativedelta

# Configuración
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
USERNAME = "arturoguerreronc"
BIRTH_DATE = datetime.date(2005, 3, 4)
LIFE_EXPECTANCY_YEARS = 80

def get_github_stats(username, token):
    if not token:
        print("No token provided.")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(ownerAffiliations: OWNER, isFork: false) {
          totalCount
        }
        starredRepositories {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
          totalRepositoryContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalIssueContributions
        }
      }
    }
    """
    
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"login": username}},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print("Errors:", data["errors"])
                return None
                
            user = data.get("data", {}).get("user")
            if not user:
                print("User data not found.")
                return None

            repos = user.get("repositories", {}).get("totalCount", 0)
            stars = user.get("starredRepositories", {}).get("totalCount", 0)
            
            # Contributions from the last year
            contribs = user.get("contributionsCollection")
            if not contribs:
                print("Contributions data not found.")
                return None

            total_commits = contribs.get("totalCommitContributions", 0)
            total_contributions = (
                total_commits + 
                contribs.get("restrictedContributionsCount", 0) + 
                contribs.get("totalRepositoryContributions", 0) +
                contribs.get("totalPullRequestContributions", 0) +
                contribs.get("totalPullRequestReviewContributions", 0) +
                contribs.get("totalIssueContributions", 0)
            )
            
            return {
                "repos": str(repos),
                "stars": str(stars),
                "commits": str(total_commits),
                "contributions": str(total_contributions)
            }
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error while fetching GitHub stats: {e}")
        return None
    except ValueError as e:
        # For example, JSON decoding or type conversion issues
        print(f"Error processing GitHub API response: {e}")
        return None
    except Exception as e:
        # Fallback for any other unexpected exceptions
        print(f"Unexpected exception in get_github_stats: {e}")
        return None

def calculate_uptime():
    today = datetime.date.today()
    r = relativedelta(today, BIRTH_DATE)
    
    uptime_str = f"{r.years} Years, {r.months} Months, {r.days} Days"
    
    # Life expectancy
    expected_end_date = BIRTH_DATE + relativedelta(years=LIFE_EXPECTANCY_YEARS)
    total_days_expectancy = (expected_end_date - BIRTH_DATE).days
    total_days_lived = (today - BIRTH_DATE).days
    percentage = (total_days_lived / total_days_expectancy) * 100
    life_expectancy_str = f"{percentage:.1f}%"
    
    return uptime_str, life_expectancy_str

def update_svg(template_path, output_path, stats, uptime, life_expectancy):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("{{REPOS}}", html.escape(stats["repos"]))
    content = content.replace("{{STARS}}", html.escape(stats["stars"]))
    content = content.replace("{{COMMITS}}", html.escape(stats["commits"]))
    content = content.replace("{{CONTRIBUTIONS}}", html.escape(stats["contributions"]))
    content = content.replace("{{UPTIME}}", uptime)
    content = content.replace("{{LIFE_EXPECTANCY}}", life_expectancy)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {output_path}")

def main():
    stats = get_github_stats(USERNAME, GITHUB_TOKEN)
    if not stats:
        print("Using placeholder stats due to missing token or error.")
        stats = {
            "repos": "N/A",
            "stars": "N/A",
            "commits": "N/A",
            "contributions": "N/A"
        }
    
    uptime, life_expectancy = calculate_uptime()
    
    print(f"Stats: {stats}")
    print(f"Uptime: {uptime}")
    print(f"Life Expectancy: {life_expectancy}")
    
    # Actualizar Dark
    update_svg(
        "templates/dark.svg",
        "dark.svg",
        stats,
        uptime,
        life_expectancy
    )
    
    # Actualizar Light
    update_svg(
        "templates/light.svg",
        "light.svg",
        stats,
        uptime,
        life_expectancy
    )

if __name__ == "__main__":
    main()

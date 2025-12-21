import datetime
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
        repositories(first: 1, ownerAffiliations: OWNER, isFork: false) {
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
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print("Errors:", data["errors"])
                return None
                
            user = data["data"]["user"]
            repos = user["repositories"]["totalCount"]
            stars = user["starredRepositories"]["totalCount"]
            
            # Contribuciones del último año
            contribs = user["contributionsCollection"]
            total_commits = contribs["totalCommitContributions"]
            total_contributions = (
                total_commits + 
                contribs["restrictedContributionsCount"] + 
                contribs["totalRepositoryContributions"] +
                contribs["totalPullRequestContributions"] +
                contribs["totalPullRequestReviewContributions"] +
                contribs["totalIssueContributions"]
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
    except Exception as e:
        print(f"Exception: {e}")
        return None

def calculate_uptime():
    today = datetime.date.today()
    r = relativedelta(today, BIRTH_DATE)
    
    uptime_str = f"{r.years} Years, {r.months} Months, {r.days} Days"
    
    # Esperanza de vida
    total_days_lived = (today - BIRTH_DATE).days
    total_days_expectancy = LIFE_EXPECTANCY_YEARS * 365.25
    percentage = (total_days_lived / total_days_expectancy) * 100
    life_expectancy_str = f"{percentage:.1f}%"
    
    return uptime_str, life_expectancy_str

def update_svg(template_path, output_path, stats, uptime, life_expectancy):
    if not os.path.exists(template_path):
        print(f"Template not found: {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("{{REPOS}}", stats["repos"])
    content = content.replace("{{STARS}}", stats["stars"])
    content = content.replace("{{COMMITS}}", stats["commits"])
    content = content.replace("{{CONTRIBUTIONS}}", stats["contributions"])
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

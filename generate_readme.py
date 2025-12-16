#!/usr/bin/env python3
"""
GitHub Repository README Generator
Automatically fetches repositories, categorizes them, and generates a comprehensive README.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict


class GitHubRepoFetcher:
    """Fetches and processes GitHub repositories."""
    
    def __init__(self, username: str, token: str = None):
        """
        Initialize the GitHub repository fetcher.
        
        Args:
            username: GitHub username
            token: GitHub API token (optional, for higher rate limits)
        """
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def fetch_repos(self) -> List[Dict]:
        """
        Fetch all public repositories for the user.
        
        Returns:
            List of repository dictionaries
        """
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/users/{self.username}/repos"
            params = {
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            batch = response.json()
            if not batch:
                break
            
            repos.extend(batch)
            page += 1
        
        return repos
    
    def categorize_repos(self, repos: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize repositories based on language and description patterns.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            Dictionary with categories as keys and repo lists as values
        """
        categories = defaultdict(list)
        
        # Define category patterns
        category_patterns = {
            "Web Development": ["web", "frontend", "backend", "react", "vue", "django", "flask"],
            "Machine Learning": ["ml", "machine learning", "ai", "artificial intelligence", "tensorflow", "pytorch"],
            "Data Science": ["data", "analysis", "pandas", "numpy", "visualization"],
            "DevOps & Infrastructure": ["docker", "kubernetes", "ci/cd", "devops", "infrastructure", "terraform"],
            "Utilities & Tools": ["tool", "utility", "cli", "command", "library"],
            "Documentation": ["docs", "documentation", "guide", "tutorial"],
            "Games & Entertainment": ["game", "entertainment", "fun"],
        }
        
        # Language-based primary categorization
        language_categories = {
            "Python": "Python",
            "JavaScript": "JavaScript",
            "TypeScript": "TypeScript",
            "Go": "Go",
            "Rust": "Rust",
            "Java": "Java",
            "C++": "C++",
            "C#": "C#",
            "Ruby": "Ruby",
        }
        
        for repo in repos:
            categorized = False
            description = (repo.get("description") or "").lower()
            language = repo.get("language") or "Other"
            
            # Try to categorize by description patterns first
            for category, patterns in category_patterns.items():
                if any(pattern in description for pattern in patterns):
                    categories[category].append(repo)
                    categorized = True
                    break
            
            # If not categorized by description, use language
            if not categorized:
                if language in language_categories:
                    categories[language].append(repo)
                else:
                    categories["Other"].append(repo)
        
        return dict(categories)
    
    def get_stats(self, repos: List[Dict]) -> Dict:
        """Calculate repository statistics."""
        stats = {
            "total_repos": len(repos),
            "total_stars": sum(repo.get("stargazers_count", 0) for repo in repos),
            "total_forks": sum(repo.get("forks_count", 0) for repo in repos),
            "languages": set(),
            "avg_stars": 0,
        }
        
        for repo in repos:
            if repo.get("language"):
                stats["languages"].add(repo["language"])
        
        stats["languages"] = sorted(list(stats["languages"]))
        
        if repos:
            stats["avg_stars"] = round(stats["total_stars"] / len(repos), 2)
        
        return stats


class ReadmeGenerator:
    """Generates a comprehensive README file."""
    
    def __init__(self, username: str):
        """Initialize the README generator."""
        self.username = username
        self.generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def generate(self, categories: Dict[str, List[Dict]], stats: Dict) -> str:
        """
        Generate a comprehensive README.
        
        Args:
            categories: Categorized repositories
            stats: Repository statistics
            
        Returns:
            README content as a string
        """
        readme = []
        
        # Header
        readme.append(f"# {self.username}")
        readme.append("")
        readme.append(f"Welcome to my GitHub profile! Here's a comprehensive overview of my repositories.")
        readme.append("")
        
        # Statistics
        readme.append("## 📊 Repository Statistics")
        readme.append("")
        readme.append(f"- **Total Repositories**: {stats['total_repos']}")
        readme.append(f"- **Total Stars**: ⭐ {stats['total_stars']}")
        readme.append(f"- **Total Forks**: 🍴 {stats['total_forks']}")
        readme.append(f"- **Average Stars per Repo**: {stats['avg_stars']}")
        readme.append(f"- **Primary Languages**: {', '.join(stats['languages'][:5]) if stats['languages'] else 'N/A'}")
        readme.append("")
        
        # Table of Contents
        readme.append("## 📑 Table of Contents")
        readme.append("")
        for category in sorted(categories.keys()):
            anchor = category.lower().replace(" ", "-").replace("&", "")
            readme.append(f"- [{category}](#{anchor})")
        readme.append("")
        
        # Repository Listings by Category
        readme.append("## 📚 Repositories")
        readme.append("")
        
        for category in sorted(categories.keys()):
            repos = categories[category]
            readme.append(f"### {category}")
            readme.append("")
            
            # Sort repos by stars (descending)
            sorted_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
            
            for repo in sorted_repos:
                readme.append(self._format_repo_entry(repo))
            
            readme.append("")
        
        # Footer
        readme.append("---")
        readme.append("")
        readme.append(f"**Last Updated**: {self.generated_at}")
        readme.append("")
        readme.append(f"Generated by [generate_readme.py](./generate_readme.py)")
        
        return "\n".join(readme)
    
    @staticmethod
    def _format_repo_entry(repo: Dict) -> str:
        """Format a single repository entry."""
        name = repo["name"]
        url = repo["html_url"]
        description = repo.get("description") or "No description provided"
        language = repo.get("language") or "Unknown"
        stars = repo.get("stargazers_count", 0)
        
        # Build the entry
        entry = f"- **[{name}]({url})** - {description}"
        entry += f"\n  - Language: `{language}` | Stars: ⭐ {stars}"
        
        return entry


def main():
    """Main function to fetch repos and generate README."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive README from GitHub repositories"
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("GITHUB_USERNAME", "lord-joeh"),
        help="GitHub username (default: lord-joeh or GITHUB_USERNAME env var)"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub API token (optional, default: GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--output",
        default="README.md",
        help="Output file path (default: README.md)"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Fetching repositories for {args.username}...")
        fetcher = GitHubRepoFetcher(args.username, args.token)
        repos = fetcher.fetch_repos()
        print(f"✅ Found {len(repos)} repositories")
        
        print("🏷️  Categorizing repositories...")
        categories = fetcher.categorize_repos(repos)
        print(f"✅ Categorized into {len(categories)} categories")
        
        print("📊 Calculating statistics...")
        stats = fetcher.get_stats(repos)
        
        print("📝 Generating README...")
        generator = ReadmeGenerator(args.username)
        readme_content = generator.generate(categories, stats)
        
        print(f"💾 Writing to {args.output}...")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"✨ README successfully generated: {args.output}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching from GitHub API: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()

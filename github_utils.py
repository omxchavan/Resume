import requests
import os
from datetime import datetime

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

def get_github_user_profile(username):
    """
    Fetch GitHub user profile information
    
    Args:
        username (str): GitHub username
        
    Returns:
        dict: User profile information or None if not found
    """
    try:
        # Make request to GitHub API
        response = requests.get(f"{GITHUB_API_URL}/users/{username}")
        
        # Check if request was successful
        if response.status_code == 200:
            user_data = response.json()
            
            # Extract relevant information
            profile = {
                'username': user_data.get('login'),
                'name': user_data.get('name'),
                'avatar_url': user_data.get('avatar_url'),
                'bio': user_data.get('bio'),
                'company': user_data.get('company'),
                'blog': user_data.get('blog'),
                'location': user_data.get('location'),
                'email': user_data.get('email'),
                'public_repos': user_data.get('public_repos'),
                'public_gists': user_data.get('public_gists'),
                'followers': user_data.get('followers'),
                'following': user_data.get('following'),
                'created_at': format_github_date(user_data.get('created_at')),
                'updated_at': format_github_date(user_data.get('updated_at')),
                'profile_url': user_data.get('html_url')
            }
            return profile
        else:
            print(f"Error fetching GitHub profile: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching GitHub profile: {str(e)}")
        return None

def get_github_user_repos(username, sort_by='updated', direction='desc', per_page=5):
    """
    Fetch GitHub user repositories
    
    Args:
        username (str): GitHub username
        sort_by (str): Sort repositories by (created, updated, pushed, full_name)
        direction (str): Sort direction (asc, desc)
        per_page (int): Number of repositories to fetch
        
    Returns:
        list: List of repositories or empty list if not found
    """
    try:
        # Make request to GitHub API
        response = requests.get(
            f"{GITHUB_API_URL}/users/{username}/repos",
            params={
                'sort': sort_by,
                'direction': direction,
                'per_page': per_page
            }
        )
        
        # Check if request was successful
        if response.status_code == 200:
            repos_data = response.json()
            
            # Extract relevant information from each repository
            repos = []
            for repo in repos_data:
                repos.append({
                    'name': repo.get('name'),
                    'description': repo.get('description'),
                    'html_url': repo.get('html_url'),
                    'stars': repo.get('stargazers_count'),
                    'forks': repo.get('forks_count'),
                    'language': repo.get('language'),
                    'updated_at': format_github_date(repo.get('updated_at')),
                    'created_at': format_github_date(repo.get('created_at')),
                    'is_fork': repo.get('fork', False)
                })
            return repos
        else:
            print(f"Error fetching GitHub repositories: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception fetching GitHub repositories: {str(e)}")
        return []

def get_github_user_languages(username, top_repos=5):
    """
    Calculate the most used languages across user's repositories
    
    Args:
        username (str): GitHub username
        top_repos (int): Number of top repositories to analyze
        
    Returns:
        dict: Dictionary of languages and their usage percentage
    """
    try:
        # Get user's repositories
        repos = get_github_user_repos(username, per_page=top_repos)
        
        # Count languages
        languages = {}
        for repo in repos:
            language = repo.get('language')
            if language:
                if language in languages:
                    languages[language] += 1
                else:
                    languages[language] = 1
        
        # Calculate percentages
        total = sum(languages.values())
        if total > 0:
            for lang in languages:
                languages[lang] = round((languages[lang] / total) * 100)
        
        # Sort by usage (descending)
        sorted_languages = dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_languages
    except Exception as e:
        print(f"Exception calculating GitHub languages: {str(e)}")
        return {}

def format_github_date(date_str):
    """
    Format GitHub API date string to a more readable format
    
    Args:
        date_str (str): GitHub API date string
        
    Returns:
        str: Formatted date string
    """
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%b %d, %Y")
    except Exception:
        return date_str 
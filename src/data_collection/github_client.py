import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

github=Github(os.getenv("GITHUB_TOKEN"))

repos = github.search_repositories(query="language:Python stars:>100")

for repo in repos[:10]:
    print(repo.full_name,
          "| Stars:",repo.stargazers_count,
          "| Language:",repo.language
          )
print("--------------------------------------------------------------------")
repo_md=github.get_repo("NousResearch/hermes-agent")
print("Name: ",repo_md.name)
print("Description:", repo_md.description)
print("Language:", repo_md.language)
print("Stars:", repo_md.stargazers_count)
print("Forks:", repo_md.forks_count)
print("Open issues:", repo_md.open_issues_count)
print("Created:", repo_md.created_at)
print("Updated:", repo_md.updated_at)
print("Topics: ",repo_md.get_topics())
print("--------------------------------------------------------------------")
issues = repo_md.get_issues(state="open")

count=0
#Github API treats PRs as issues
for issue in issues:
    if issue.pull_request is not None:
        continue

    print("Title: ",issue.title)
    print("Body: ",issue.body)
    print("Labels:", [label.name for label in issue.labels])
    print("Comments:", issue.comments)
    print("Created:", issue.created_at)
    print("---------------------------------------------------------------------------")

    count+=1
    if count==5:
        break
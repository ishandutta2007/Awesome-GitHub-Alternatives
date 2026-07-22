import re
import json
import urllib.request
import os

readme_path = r"C:\Users\ishan\Documents\Projects\Awesome-GitHub-Alternatives\README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update SaaS Table
saas_sizes = {
    "Amazon CodeCommit": ("~$570B Revenue", 570000000000),
    "Google Cloud Repositories": ("~$300B Revenue", 300000000000),
    "Atlassian BitBucket": ("~$40B Valuation", 40000000000),
    "Keybase": ("~$20B Valuation", 20000000000),
    "GitLab": ("~$6B Valuation", 6000000000),
    "Canonical Launchpad": ("~$200M Revenue", 200000000),
    "Tuleap": ("~$5M Revenue", 5000000),
    "Planio": ("~$5M Revenue", 5000000),
    "Beanstalk": ("Acquired", 0),
    "sr.ht": ("<$1M Revenue", 100000),
    "Phabricator": ("Discontinued", -1)
}

table_start = content.find("### Core Platforms (GitHub Alternatives)\n\n| Platform")
table_end = content.find("\n\n## 🔓 Open-Source GitHub Projects", table_start)

table_text = content[table_start:table_end].strip().split('\n')
header = table_text[2] + " Company Size |"
separator = table_text[3] + "--------------|"
rows = table_text[4:]

parsed_rows = []
for row in rows:
    if not row.strip(): continue
    parts = [p.strip() for p in row.split('|') if p.strip()]
    if not parts: continue
    name_match = re.search(r'\[(.*?)\]', parts[0])
    name = name_match.group(1) if name_match else parts[0]
    
    # Strip asterisks
    name = name.replace('*', '').strip()

    size_str, size_val = saas_sizes.get(name, ("Unknown", -1))
    
    parsed_rows.append({
        'row_str': f"| {parts[0]} | {parts[1]} | {parts[2]} | {size_str} |",
        'val': size_val
    })

parsed_rows.sort(key=lambda x: x['val'], reverse=True)

new_table_lines = [
    "### Core Platforms (GitHub Alternatives)",
    "",
    "| Platform | Description | Pricing & Free Tier Limits | Company Size |",
    "|----------|-------------|----------------------------|--------------|"
] + [r['row_str'] for r in parsed_rows]

content = content[:table_start] + "\n".join(new_table_lines) + content[table_end:]

# 2. Update Open Source section
def get_stars(url):
    match = re.search(r'github\.com/([^/]+/[^/]+)', url)
    if match:
        repo = match.group(1).rstrip('/')
        api_url = f"https://api.github.com/repos/{repo}"
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return data.get('stargazers_count', 0), repo
        except Exception as e:
            print(f"Error fetching {repo}: {e}")
            return 0, repo
    return 0, None

os_start = content.find("### 💻 Dedicated Source Code Hosting & Collaboration Tools\n\n")
os_end = content.find("\n\n### Additional Strong Open-Source Options")

os_text = content[os_start:os_end]
lines = os_text.split('\n')

repos = []
current_repo = None

for line in lines[2:]:
    if line.startswith("- **["):
        match = re.search(r'- \*\*\[(.*?)\]\((.*?)\)\*\*(.*)', line)
        if match:
            name, url, rest = match.groups()
            stars, repo_path = get_stars(url)
            if repo_path:
                badge = f"[![Stars](https://img.shields.io/github/stars/{repo_path}?style=social&color=white)]({url}/stargazers)"
                new_line = f"- **[{name}]({url})** {badge}{rest}"
            else:
                new_line = line
            current_repo = {'line': new_line, 'desc': '', 'stars': stars}
            repos.append(current_repo)
        else:
            if current_repo: current_repo['desc'] += line + '\n'
    else:
        if current_repo: current_repo['desc'] += line + '\n'

repos.sort(key=lambda x: x['stars'], reverse=True)

new_os_lines = ["### 💻 Dedicated Source Code Hosting & Collaboration Tools\n"]
for r in repos:
    new_os_lines.append(r['line'])
    if r['desc'].strip():
        new_os_lines.append(r['desc'].strip())
    new_os_lines.append("")

content = content[:os_start] + "\n".join(new_os_lines).strip() + content[os_end:]

# Process the other open source section too
add_os_start = content.find("### Additional Strong Open-Source Options\n\n")
add_os_end = content.find("\n\n**Frameworks for building custom forges**")

add_os_text = content[add_os_start:add_os_end]
add_lines = add_os_text.split('\n')

add_repos = []
for line in add_lines[2:]:
    if not line.strip(): continue
    match = re.search(r'- \*\*\[(.*?)\]\((.*?)\)\*\* (.*)', line)
    if match:
        name, url, rest = match.groups()
        stars, repo_path = get_stars(url)
        if repo_path:
            badge = f"[![Stars](https://img.shields.io/github/stars/{repo_path}?style=social&color=white)]({url}/stargazers)"
            new_line = f"- **[{name}]({url})** {badge} {rest}"
        else:
            new_line = line
        add_repos.append({'line': new_line, 'stars': stars})
    else:
        match2 = re.search(r'- \*\*\[(.*?)\]\((.*?)\)\s+(.*)', line)
        if match2:
            name, url, rest = match2.groups()
            stars, repo_path = get_stars(url)
            if repo_path:
                badge = f"[![Stars](https://img.shields.io/github/stars/{repo_path}?style=social&color=white)]({url}/stargazers)"
                new_line = f"- **[{name}]({url})** {badge} {rest}"
            else:
                new_line = line
            add_repos.append({'line': new_line, 'stars': stars})
        else:
            add_repos.append({'line': line, 'stars': -1})

add_repos.sort(key=lambda x: x['stars'], reverse=True)

new_add_lines = ["### Additional Strong Open-Source Options\n"]
for r in add_repos:
    new_add_lines.append(r['line'])

content = content[:add_os_start] + "\n".join(new_add_lines).strip() + content[add_os_end:]

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated README.md")

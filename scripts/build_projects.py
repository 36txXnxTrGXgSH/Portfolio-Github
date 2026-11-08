"""Génère projects.json : la liste des projets publics lue par la page.

Lancé chaque jour par la GitHub Action (.github/workflows/projects.yml), pour que
les visiteurs n'interrogent jamais l'API GitHub eux-mêmes.
En local : GITHUB_TOKEN=$(gh auth token) python scripts/build_projects.py
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = "36txXnxTrGXgSH"
SELF_REPO = "portfolio-github"  # ce site, exclu de la liste
OUTPUT = Path(__file__).resolve().parent.parent / "projects.json"

# Images de présentation essayées dans l'ordre (dans le dépôt, branche par défaut).
# Pour choisir l'image d'un projet : ajouter un fichier "preview.png" à la racine du dépôt.
IMAGE_CANDIDATES = ["preview.png", "docs/images/01-accueil.png"]

# Installables reconnus, par plateforme. Une release qui en contient pour plusieurs
# plateformes (ex. 36Screenlink : .exe pour le PC + .apk pour le téléphone) a un bouton par plateforme.
PLATFORMS = {
    "windows": (".exe", ".msi", ".msix"),
    "android": (".apk",),
    "navigateur": (".crx", ".xpi"),
}

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def request(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "portfolio-github-build",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN and "api.github.com" in url else {}),
    })
    return urllib.request.urlopen(req, timeout=30)


def api(path):
    with request(f"https://api.github.com{path}") as res:
        return json.load(res)


def exists(url):
    try:
        with request(url, method="HEAD") as res:
            return res.status == 200
    except urllib.error.HTTPError:
        return False


def pick_files(assets):
    """Un fichier par plateforme présente dans la release ; pour une même plateforme,
    l'installateur passe avant le portable. Sans installable : le premier fichier."""
    def entry(a, platform):
        return {"platform": platform, "file": a["name"], "size": a["size"], "url": a["browser_download_url"]}

    files = []
    for platform, extensions in PLATFORMS.items():
        matching = [a for a in assets if a["name"].lower().endswith(extensions)]
        setup = [a for a in matching if "setup" in a["name"].lower() or "install" in a["name"].lower()]
        if matching:
            files.append(entry((setup or matching)[0], platform))
    if not files and assets:
        files.append(entry(assets[0], None))
    return files


def latest_release(name):
    try:
        data = api(f"/repos/{USER}/{name}/releases/latest")
    except urllib.error.HTTPError as e:
        if e.code == 404:  # pas de release : la page proposera le .zip du code
            return None
        raise
    files = pick_files(data.get("assets") or [])
    if not files:
        return None
    return {"tag": data["tag_name"], "files": files}


def preview_image(name, branch):
    raw = f"https://raw.githubusercontent.com/{USER}/{name}/{branch}/"
    return next((raw + f for f in IMAGE_CANDIDATES if exists(raw + f)), None)


def main():
    repos = api(f"/users/{USER}/repos?per_page=100&type=owner&sort=updated")
    repos = [r for r in repos if not r["fork"] and not r["private"] and r["name"].lower() != SELF_REPO]

    projects = []
    for r in repos:
        name, branch = r["name"], r["default_branch"]
        # Le vrai nombre de « Watching » (subscribers_count) n'existe que dans la fiche détaillée ;
        # le watchers_count de la liste est en fait le nombre de stars
        details = api(f"/repos/{USER}/{name}")
        projects.append({
            "name": name,
            "description": r["description"],
            "language": r["language"],
            "topics": r.get("topics", []),
            "url": r["html_url"],
            "homepage": r["homepage"],
            "updated": r["pushed_at"] or r["updated_at"],
            "branch": branch,
            "stars": r["stargazers_count"],
            "watchers": details["subscribers_count"],
            "image": preview_image(name, branch),
            "release": latest_release(name),
        })
        print(f"{name}: {(projects[-1]['release'] or {}).get('tag', 'pas de release')}", file=sys.stderr)

    # "generated" ne change le fichier que si les projets ont changé, pour éviter un commit par jour
    previous = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    generated = previous.get("generated") if previous.get("projects") == projects else None
    data = {"generated": generated or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "projects": projects}
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(projects)} projets écrits dans {OUTPUT.name}", file=sys.stderr)


if __name__ == "__main__":
    main()

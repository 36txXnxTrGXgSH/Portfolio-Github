# Portfolio Github

Page qui regroupe mes projets publics GitHub, classés par catégorie (Android, Windows, Navigateur, Autre), avec une description, une image, les compteurs stars / watching et un lien de téléchargement.

👉 **https://36txxnxtrgxgsh.github.io/Portfolio-Github/**

## Mise à jour de la liste

La page lit `projects.json`, généré par [`scripts/build_projects.py`](scripts/build_projects.py). Les visiteurs n'interrogent donc jamais l'API GitHub.

La GitHub Action [`Liste des projets`](.github/workflows/projects.yml) régénère ce fichier :
- chaque jour, vers 4 h UTC ;
- à chaque modification de ce dépôt ;
- à la demande : onglet **Actions** → **Liste des projets** → **Run workflow**, ou `gh workflow run projects.yml -R 36txXnxTrGXgSH/Portfolio-Github`.

## Règles

- **Catégorie** : selon les topics du dépôt (`android`, `windows`, `browser-extension`…), sinon selon le fichier de la dernière release (`.apk`, `.exe`, `.crx`…).
- **Fichiers à télécharger** : un installable par plateforme présente dans la dernière release (`.exe` pour Windows, `.apk` pour Android, `.crx`/`.xpi` pour le navigateur ; l'installateur passe avant le portable), sinon le code source en `.zip`.
- **Image** : `preview.png` à la racine du dépôt, sinon `docs/images/01-accueil.png`, sinon l'aperçu GitHub.

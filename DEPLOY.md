# One-time GitHub Pages setup

1. Open **Settings → Pages** for this repo:
   https://github.com/laughingdragonsproductions/Theassociatedguess/settings/pages

2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.

3. Choose branch **`gh-pages`**, folder **`/ (root)`**, then **Save**.

4. After the next push to `main`, the **Deploy gh-pages branch** workflow creates/updates `gh-pages`. The live URL will be:

   https://laughingdragonsproductions.github.io/Theassociatedguess/

Local preview (always works):

```powershell
powershell -File scripts/preview.ps1
```

Open http://localhost:8081/

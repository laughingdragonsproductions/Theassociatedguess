# Deploy The Associated Guess

## Why GitHub shows 404

Pushing to GitHub does **not** turn on the website. The repo has all the HTML (on both `main` and `gh-pages`), but **GitHub Pages hosting is still off** until you flip it in Settings once.

Local preview always works: http://localhost:8081/

## Fix GitHub Pages (about 1 minute)

You must be **signed in** as `laughingdragonsproductions` (repo owner).

1. Open: https://github.com/laughingdragonsproductions/Theassociatedguess/settings/pages  
   (If you see "Page not found", sign in to GitHub first.)

2. Under **Build and deployment → Source**, choose **Deploy from a branch**.

3. Set:
   - **Branch:** `main` (simplest — site files are already here)  
     *or* `gh-pages` (updated automatically on each push by the workflow)
   - **Folder:** `/ (root)`

4. Click **Save**.

5. Wait 1–3 minutes. GitHub will show a green box with your live URL:

   **https://laughingdragonsproductions.github.io/Theassociatedguess/**

6. Hard-refresh the page (Ctrl+F5) if you still see the old 404.

## Verify

- Homepage loads with **The Associated Guess** masthead
- CSS loads (grey background, red accent — not unstyled HTML)
- Article links work, e.g. `/article/local-dog-elected-honorary-mayor-after-attending-every-council-meeting/`

## Optional: Cloudflare Pages (custom domain later)

Same pattern as `laughing-dragons-site`: connect this repo in Cloudflare Pages, build command **none**, output directory **`/`**, then point `theassociatedguess.com` DNS at Cloudflare.

## Local preview

```powershell
powershell -File G:\LocalAIagent\Theassociatedguess\scripts\preview.ps1
```

Open http://localhost:8081/

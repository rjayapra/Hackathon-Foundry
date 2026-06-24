# Publishing to GitHub Pages

This guide explains how to publish the hackathon materials as a GitHub Pages site.

## Option 1: Publish from `docs/` folder (Recommended)

1. **Push the repo to GitHub:**
   ```bash
   cd hackathon-foundry
   git init
   git add .
   git commit -m "Initial hackathon materials"
   git remote add origin https://github.com/<your-org>/hackathon-foundry.git
   git push -u origin main
   ```

2. **Enable GitHub Pages:**
   - Go to the repo on GitHub
   - Navigate to **Settings** → **Pages**
   - Under "Source", select **Deploy from a branch**
   - Set branch to `main` and folder to `/docs`
   - Click **Save**

3. **Access your site:**
   - URL will be: `https://<your-org>.github.io/hackathon-foundry/`
   - Takes 1-2 minutes for the first build

## Option 2: Use GitHub Actions (for custom builds)

Create `.github/workflows/pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: ["main"]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/jekyll-build-pages@v1
        with:
          source: ./docs
      - uses: actions/upload-pages-artifact@v3

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

## Local Preview

```bash
cd docs
bundle install
bundle exec jekyll serve
# Open http://localhost:4000
```

## Customization

- Edit `docs/_config.yml` to change the site title, description, or theme
- Lab content lives in `docs/labs/*.md`
- The home page is `docs/index.md`
- Navigation links are defined in each lab's front matter (`prev_lab`, `next_lab`)

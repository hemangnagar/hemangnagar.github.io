# Step 2: template, index, JSON-LD partials, front-matter schema

## Files

| Path | Role |
|---|---|
| `_config.yml` | Jekyll settings for the default GitHub Pages build. `problems` collection → `/problems/<slug>/`. Excludes `docs/`, `tools/`, `promote/`. |
| `_data/projects.yml` | The eight projects: name, card anchor, problem slug, repos (url, language, license), demo, two-line summary. Single source for related links, SoftwareSourceCode JSON-LD, llms.txt and the sitemap. |
| `_layouts/base.html` | `<head>` (title = `title` + " \| Hemang Nagar", description, canonical, OG, fonts, `site.css`, BreadcrumbList), header, footer. |
| `_layouts/problem.html` | The problem-page skeleton: crumbs, eyebrow (project), H1, byline with published/updated dates, body, Related, footer CTA line, TechArticle JSON-LD. |
| `_layouts/page.html` | About / services / index pages: crumbs, H1, byline, body; Person JSON-LD when `person: true`. |
| `_includes/jsonld-*.html` | `breadcrumb` (every page under the root), `techarticle`, `person`, `software` (ItemList of SoftwareSourceCode). |
| `assets/site.css` | Tokens and base rules copied from `index.html`, plus article typography. The home page keeps its inline copy. |
| `problems/index.html` | Lists non-draft problem pages by the question they answer. |
| `_problems/<slug>.md` | One problem page per file. |

## Front-matter schema for `_problems/*.md`

```yaml
title: Enforce governance on data in motion        # H1 and <title> prefix; imperative form, ≤ 44 chars so the title stays under 60
question: How do you enforce data governance on data in motion, not after the fact?   # the query; shown in the index, alternativeHeadline in JSON-LD
slug: governance-on-data-in-motion                  # must equal the file name; used by `related`
description: 120–155 characters, written as the answer   # meta description and index blurb
project: governed-data-platform                     # key in _data/projects.yml
order: 1                                            # position in the index (home-page order)
keywords: [secondary query, secondary query]        # TechArticle.keywords; become H2 wording or body sentences
evidence:                                           # what the page shows; mirrored in the final report
  - path or description
related: [other-slug, other-slug]                   # one or two other problem pages
datePublished: 2026-10-07
dateModified: 2026-10-07                            # change only when content changes
draft: true                                         # optional; excludes from index, sitemap, llms.txt; adds noindex
image: /assets/....png                              # optional; og:image and TechArticle.image (default og-hero.png)
```

Body: the first paragraph is the direct answer (two to four sentences). Then H2s in this order: Why it is hard · How I solved it · Evidence · When this applies, and when it doesn't. The layout appends Related and the CTA line. 900–1,500 words.

## Build

GitHub Pages renders this on push to `main`. Locally:

```bash
cd tools/capture   # or any folder with a Gemfile that pins github-pages
bundle exec jekyll build -s <repo> -d <out>
```

`index.html` and the demo folders have no front matter and are copied unchanged.

# Geekish Site

Static tech news/blog site for https://thegeekish.com/.

## Structure

- `index.html` — homepage with hero, story cards, blog list, radar, social CTA, newsletter placeholder.
- `articles/` — individual article pages with canonical URLs and BlogPosting schema.
- `styles.css` — shared visual system and responsive layout.
- `robots.txt` — crawler access and sitemap location.
- `sitemap.xml` — homepage + article URLs for search engines.
- `FREE_TRAFFIC_PROMOTION_KIT.md` — draft copy and free traffic checklist.

## Deploy

Deploy the folder to Cloudflare Pages, Netlify, Vercel, GitHub Pages, or any static host. After deploy, submit:

- `https://thegeekish.com/sitemap.xml`
- `https://thegeekish.com/robots.txt`

## Content workflow

1. Add a new page under `articles/`.
2. Link it from the homepage blog/story sections.
3. Add the URL to `sitemap.xml`.
4. Turn the article into a Reel/TikTok/Short and point viewers back to the article.

## Matching social posts

Each article should have matching post copy in `social-posts/` with captions, hooks, carousel slides, and comment prompts.

## Post formats

Static image posts are allowed and encouraged. Not every article needs a video. For speed, each article can become:

- 1 feed image, 1080x1350 or 1080x1080
- 1 carousel, 4-6 slides
- 1 Story image, 1080x1920
- Optional Reel/TikTok/Short when the topic deserves motion

Default rule: if time is tight, make a strong image post first, then make video later.

## Real image files

The live homepage uses PNG images from `social-images-png/` so story pictures render reliably. SVG source files remain in `social-images/`.

const fs = require("fs");
const path = require("path");

const blogDir = path.join(__dirname, "..", "blog");
const imageDir = path.join(__dirname, "..", "assets", "blog-featured");
const slugs = fs.readdirSync(imageDir)
  .filter((name) => name.endsWith(".png"))
  .map((name) => name.slice(0, -4));

const rel = (slug) => `/assets/blog-featured/${slug}.png`;
const abs = (slug) => `https://outreachrecruitment.net${rel(slug)}`;
const words = (slug) => `${slug.replaceAll("-", " ")} — Outreach Recruitment Malta`;
const canonical = (slug) => `https://outreachrecruitment.net/blog/${slug}`;

function setMeta(html, attribute, value, content) {
  const pattern = new RegExp(
    `<meta\\b(?=[^>]*\\b${attribute}=["']${value}["'])[^>]*>`,
    "i",
  );
  return html.replace(pattern, (tag) =>
    /\bcontent=["'][^"']*["']/i.test(tag)
      ? tag.replace(/\bcontent=["'][^"']*["']/i, `content="${content}"`)
      : tag.replace(/\/?>$/, ` content="${content}"/>`),
  );
}

function updateCards(html) {
  for (const slug of slugs) {
    const article = new RegExp(
      `(<article\\b(?=[^>]*data-blog-subcategory=["'][^"']*["'])[^>]*>[\\s\\S]*?href=["']\\/blog\\/${slug}\\.html["'][\\s\\S]*?<div class=["']article-card-media["']>[\\s\\S]*?<img\\b)([^>]*)(>)`,
      "i",
    );
    const linked = new RegExp(
      `(<a\\b[^>]*href=["']\\/blog\\/${slug}\\.html["'][^>]*>[\\s\\S]*?<img\\b)([^>]*)(>)`,
      "gi",
    );
    const replace = (_, start, attrs, end) => {
      attrs = attrs
        .replace(/\s+src=["'][^"']*["']/i, "")
        .replace(/\s+srcset=["'][^"']*["']/i, "")
        .replace(/\s+alt=["'][^"']*["']/i, "");
      return `${start} src="${rel(slug)}" alt="${words(slug)}"${attrs}${end}`;
    };
    html = html.replace(article, replace).replace(linked, replace);
  }
  return html;
}

for (const name of fs.readdirSync(blogDir).filter((name) => name.endsWith(".html"))) {
  const file = path.join(blogDir, name);
  const slug = path.basename(name, ".html");
  let html = updateCards(fs.readFileSync(file, "utf8"));

  if (slugs.includes(slug)) {
    html = setMeta(html, "property", "og:image", abs(slug));
    html = setMeta(html, "name", "twitter:image", abs(slug));
    html = setMeta(html, "property", "og:image:alt", words(slug));
    html = setMeta(html, "property", "og:image:width", "1672");
    html = setMeta(html, "property", "og:image:height", "941");
    html = setMeta(html, "property", "og:image:type", "image/png");
    html = html.replace(
      /("@type":\s*"BlogPosting"[\s\S]*?"image":\s*)\{[\s\S]*?\}/i,
      `$1{\n        "@type": "ImageObject",\n        "url": "${abs(slug)}",\n        "width": 1672,\n        "height": 941\n      }`,
    );
    html = html.replace(
      /("@type":\s*"BlogPosting"[\s\S]*?"image":\s*)["'][^"']*["']/i,
      `$1{\n    "@type": "ImageObject",\n    "url": "${abs(slug)}",\n    "width": 1672,\n    "height": 941\n  }`,
    );
    html = html.replace(
      /(<div\b[^>]*class=["'][^"']*cms-featured-media[^"']*["'][^>]*>\s*<img\b)([^>]*)(>)/i,
      (_, start, attrs, end) => {
        attrs = attrs
          .replace(/\s+src=["'][^"']*["']/i, "")
          .replace(/\s+srcset=["'][^"']*["']/i, "")
          .replace(/\s+alt=["'][^"']*["']/i, "");
        return `${start} src="${rel(slug)}" srcset="${rel(slug)}" alt="${words(slug)}"${attrs}${end}`;
      },
    );
  }

  fs.writeFileSync(file, html);
}

const imageSitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
${slugs
  .sort()
  .map(
    (slug) => `  <url>
    <loc>${canonical(slug)}</loc>
    <lastmod>2026-07-24</lastmod>
    <image:image>
      <image:loc>${abs(slug)}</image:loc>
    </image:image>
  </url>`,
  )
  .join("\n")}
</urlset>
`;
fs.writeFileSync(
  path.join(__dirname, "..", "sitemaps", "sitemap-blog-images.xml"),
  imageSitemap,
);

console.log(`Updated ${slugs.length} blog images.`);

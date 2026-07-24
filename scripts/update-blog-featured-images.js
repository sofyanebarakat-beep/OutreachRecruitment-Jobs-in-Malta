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

console.log(`Updated ${slugs.length} blog images.`);

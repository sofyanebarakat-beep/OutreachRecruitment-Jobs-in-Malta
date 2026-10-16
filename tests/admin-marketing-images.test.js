const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const values = new Map();
const localStorage = {
  getItem(key) { return values.has(key) ? values.get(key) : null; },
  setItem(key, value) { values.set(key, String(value)); },
};
const window = {};
const context = { window, localStorage };

vm.runInNewContext(fs.readFileSync("admin/images.js", "utf8"), context);

const images = window.AdminImages;
assert.equal(images.postPickFor("job-without-image"), null, "jobs without an assigned image stay image-free");

values.clear();
localStorage.setItem("admin:marketing-image-for", JSON.stringify({
  "job-with-unique-image": "image-1",
  "job-sharing-image-a": "image-2",
  "job-sharing-image-b": "image-2",
  generic: "generic-image",
}));
const migratedWindow = {};
vm.runInNewContext(fs.readFileSync("admin/images.js", "utf8"), { window: migratedWindow, localStorage });
const migratedImages = migratedWindow.AdminImages;
assert.equal(migratedImages.postPickFor("job-with-unique-image"), "image-1", "unique legacy job images are preserved");
assert.equal(migratedImages.postPickFor("job-sharing-image-a"), null, "duplicate legacy image assignments are not carried over");
assert.equal(migratedImages.postPickFor("job-sharing-image-b"), null, "duplicate legacy image assignments are not carried over");
assert.equal(migratedImages.postPickFor("generic"), null, "generic-post images are not treated as job images");
assert.equal(migratedImages.pickFor("job-sharing-image-a"), "image-2", "generated-picture picks remain separate");

migratedImages.setPostPick("job-sharing-image-a", "image-2");
assert.equal(migratedImages.postPickFor("job-sharing-image-a"), "image-2");
migratedImages.setPostPick("job-sharing-image-b", "image-2");
assert.equal(migratedImages.postPickFor("job-sharing-image-a"), null, "one image cannot be assigned to multiple jobs");
assert.equal(migratedImages.postPickFor("job-sharing-image-b"), "image-2");
migratedImages.setPostPick("job-sharing-image-b", null);
assert.equal(migratedImages.postPickFor("job-sharing-image-b"), null);

console.log("admin marketing image tests passed");

/* Admin › picture library for marketing posts.
 *
 * Online (signed in + Supabase Storage bucket "marketing", see supabase/marketing_storage.sql):
 *   pictures are saved in the bucket and get a public URL, so they can be embedded in emails.
 * Otherwise: pictures are saved in this browser (IndexedDB).
 * Large pictures are resized (max 1600px) before saving. The picture chosen for each job is remembered.
 */
(() => {
  "use strict";
  const BUCKET = "marketing", DB = "outreach-admin", OS = "images", PICK_KEY = "admin:marketing-image-for";
  const POST_PICK_KEY = "admin:marketing-post-image-for";

  const idb = () => new Promise((res, rej) => {
    const r = indexedDB.open(DB, 1);
    r.onupgradeneeded = () => r.result.createObjectStore(OS, { keyPath: "id" });
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  });
  const tx = async (mode, fn) => {
    const db = await idb();
    return new Promise((res, rej) => {
      const t = db.transaction(OS, mode), st = t.objectStore(OS), out = fn(st);
      t.oncomplete = () => res(out?.result ?? out); t.onerror = () => rej(t.error);
    });
  };

  // Resize to max 1600px; keep PNG (transparency) as PNG, everything else as JPEG.
  async function shrink(file) {
    if (!/^image\/(png|jpeg|webp)$/.test(file.type)) return file;
    const bmp = await createImageBitmap(file);
    const scale = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
    if (scale === 1 && file.size < 900 * 1024) return file;
    const c = Object.assign(document.createElement("canvas"), { width: Math.round(bmp.width * scale), height: Math.round(bmp.height * scale) });
    c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
    const type = file.type === "image/png" ? "image/png" : "image/jpeg";
    const blob = await new Promise((r) => c.toBlob(r, type, 0.88));
    return new File([blob], file.name.replace(/\.\w+$/, type === "image/png" ? ".png" : ".jpg"), { type });
  }
  const slugName = (n) => n.toLowerCase().replace(/\.[^.]+$/, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 50) || "image";

  const Images = {
    mode: "local", note: "",
    async init() {
      const S = window.AdminStore;
      if (S?.mode === "supabase" && S.sb) {
        // list() can return an empty list without an error when the bucket does not exist, so ask for
        // the bucket itself; a signed-in admin may not be allowed to read bucket metadata, in which
        // case the first upload decides (see add()).
        const { error } = await S.sb.storage.from(BUCKET).list("", { limit: 1 });
        const bucket = await S.sb.storage.getBucket(BUCKET);
        const missing = /not found/i.test(error?.message || "") || /not found/i.test(bucket.error?.message || "");
        if (!error && !missing) { this.mode = "online"; this.note = ""; return; }
        this.note = "The online picture folder is not set up yet, so pictures are saved in this browser. To keep them online (any device, and inside emails), run supabase/marketing_storage.sql once in Supabase → SQL Editor.";
      } else {
        this.note = "Pictures are saved in this browser until you sign in.";
      }
      this.mode = "local";
    },
    async list() {
      if (this.mode === "online") {
        const sb = window.AdminStore.sb;
        const { data, error } = await sb.storage.from(BUCKET).list("posts", { limit: 200, sortBy: { column: "created_at", order: "desc" } });
        if (error) throw error;
        return (data || []).filter((f) => f.name && !f.name.startsWith(".")).map((f) => {
          const path = "posts/" + f.name;
          return { id: path, name: f.name, url: sb.storage.from(BUCKET).getPublicUrl(path).data.publicUrl, online: true };
        });
      }
      const rows = await tx("readonly", (st) => st.getAll());
      return (rows || []).sort((a, b) => b.created - a.created).map((r) => ({ ...r, url: URL.createObjectURL(r.blob), online: false }));
    },
    async add(file) {
      const f = await shrink(file);
      if (this.mode === "online") {
        const path = `posts/${Date.now()}-${slugName(file.name)}.${f.type === "image/png" ? "png" : f.type === "image/gif" ? "gif" : f.type === "image/webp" ? "webp" : "jpg"}`;
        const { error } = await window.AdminStore.sb.storage.from(BUCKET).upload(path, f, { contentType: f.type, cacheControl: "31536000" });
        if (!error) return path;
        if (!/bucket not found|not found/i.test(error.message || "")) throw error;
        // Bucket missing: fall back to this browser so the picture is still saved.
        this.mode = "local";
        this.note = "The online picture folder is not set up yet, so pictures are saved in this browser. To keep them online (any device, and inside emails), run supabase/marketing_storage.sql once in Supabase → SQL Editor.";
      }
      const id = `local-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      await tx("readwrite", (st) => st.put({ id, name: file.name, type: f.type, blob: f, created: Date.now() }));
      return id;
    },
    async remove(id) {
      if (this.mode === "online" && !id.startsWith("local-")) {
        const { error } = await window.AdminStore.sb.storage.from(BUCKET).remove([id]);
        if (error) throw error;
      } else await tx("readwrite", (st) => st.delete(id));
      const map = this.picks(); for (const k of Object.keys(map)) if (map[k] === id) delete map[k];
      try { localStorage.setItem(PICK_KEY, JSON.stringify(map)); } catch {}
      const postMap = this.postPicks(); for (const k of Object.keys(postMap)) if (postMap[k] === id) delete postMap[k];
      try { localStorage.setItem(POST_PICK_KEY, JSON.stringify(postMap)); } catch {}
    },
    picks() { try { return JSON.parse(localStorage.getItem(PICK_KEY) || "{}"); } catch { return {}; } },
    pickFor(key) { return this.picks()[key] || null; },
    setPick(key, id) {
      const map = this.picks(); id ? (map[key] = id) : delete map[key];
      try { localStorage.setItem(PICK_KEY, JSON.stringify(map)); } catch {}
    },
    postPicks() {
      try {
        const saved = localStorage.getItem(POST_PICK_KEY);
        if (saved !== null) {
          const picks = JSON.parse(saved);
          return picks && typeof picks === "object" && !Array.isArray(picks) ? picks : {};
        }
      } catch { return {}; }
      const legacy = this.picks(), counts = {};
      for (const [key, id] of Object.entries(legacy)) {
        if (key !== "generic" && typeof id === "string" && id) counts[id] = (counts[id] || 0) + 1;
      }
      const migrated = {};
      for (const [key, id] of Object.entries(legacy)) {
        if (key !== "generic" && typeof id === "string" && id && counts[id] === 1) migrated[key] = id;
      }
      try { localStorage.setItem(POST_PICK_KEY, JSON.stringify(migrated)); } catch {}
      return migrated;
    },
    postPickFor(key) { return this.postPicks()[key] || null; },
    setPostPick(key, id) {
      const picks = this.postPicks();
      if (id) {
        for (const otherKey of Object.keys(picks)) if (otherKey !== key && picks[otherKey] === id) delete picks[otherKey];
        picks[key] = id;
      } else delete picks[key];
      try { localStorage.setItem(POST_PICK_KEY, JSON.stringify(picks)); } catch {}
    },
    // PNG blob of an image (clipboard only accepts PNG)
    async pngBlob(url) {
      const blob = await (await fetch(url)).blob();
      if (blob.type === "image/png") return blob;
      const bmp = await createImageBitmap(blob);
      const c = Object.assign(document.createElement("canvas"), { width: bmp.width, height: bmp.height });
      c.getContext("2d").drawImage(bmp, 0, 0);
      return new Promise((r) => c.toBlob(r, "image/png"));
    },
  };
  window.AdminImages = Images;
})();

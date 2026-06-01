document.getElementById("year").textContent = new Date().getFullYear();

const lb = document.getElementById("lightbox");
const lbImg = document.getElementById("lbImg");
let idx = 0;

const visible = () =>
  [...document.querySelectorAll(".category:not([hidden]) .gallery img")];

function show(i) {
  const v = visible();
  if (!v.length) return;
  idx = (i + v.length) % v.length;
  const el = v[idx];
  lbImg.src = el.src;
  lbImg.alt = el.alt;
}

function open(el) {
  const v = visible();
  idx = v.indexOf(el);
  show(idx);
  lb.classList.add("open");
  lb.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function close() {
  lb.classList.remove("open");
  lb.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

document.querySelectorAll(".gallery img").forEach((el) =>
  el.addEventListener("click", () => open(el))
);

const pills = [...document.querySelectorAll(".filter-pill")];
const cats = [...document.querySelectorAll(".category")];
pills.forEach((p) =>
  p.addEventListener("click", () => {
    const f = p.dataset.filter;
    pills.forEach((q) => {
      const on = q === p;
      q.classList.toggle("is-active", on);
      q.setAttribute("aria-pressed", on);
    });
    cats.forEach((c) => (c.hidden = f !== "all" && c.dataset.cat !== f));
  })
);
document.getElementById("lbClose").addEventListener("click", close);
document.getElementById("lbNext").addEventListener("click", () => show(idx + 1));
document.getElementById("lbPrev").addEventListener("click", () => show(idx - 1));
lb.addEventListener("click", (e) => { if (e.target === lb) close(); });

document.addEventListener("keydown", (e) => {
  if (!lb.classList.contains("open")) return;
  if (e.key === "Escape") close();
  if (e.key === "ArrowRight") show(idx + 1);
  if (e.key === "ArrowLeft") show(idx - 1);
});

// share: copy-link button
document.querySelectorAll(".share-copy").forEach((b) => {
  b.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(b.dataset.url); } catch (e) {}
    b.classList.add("copied");
    setTimeout(() => b.classList.remove("copied"), 1600);
  });
});

// year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// homepage full-page slideshow — one slide fills the screen, slides to the next
(function () {
  const track = document.getElementById("ssTrack");
  if (!track) return;
  const stage = document.getElementById("slideshow");
  const n = track.children.length;
  if (!n) return;
  let i = 0, timer;
  function go(k) { i = (k + n) % n; track.style.transform = "translateX(" + (-i * 100) + "%)"; }
  const next = () => go(i + 1);
  const prev = () => go(i - 1);
  function start() { timer = setInterval(next, 5000); }
  function restart() { clearInterval(timer); start(); }
  const nb = document.getElementById("ssNext"), pb = document.getElementById("ssPrev");
  if (nb) nb.addEventListener("click", () => { next(); restart(); });
  if (pb) pb.addEventListener("click", () => { prev(); restart(); });
  stage.addEventListener("mouseenter", () => clearInterval(timer));
  stage.addEventListener("mouseleave", start);
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { next(); restart(); }
    if (e.key === "ArrowLeft") { prev(); restart(); }
  });
  start();
})();

// share: copy-link button
document.querySelectorAll(".share-copy").forEach((b) => {
  b.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(b.dataset.url); } catch (e) {}
    b.classList.add("copied");
    setTimeout(() => b.classList.remove("copied"), 1600);
  });
});

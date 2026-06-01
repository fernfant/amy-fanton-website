// year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// homepage filmstrip slider
(function () {
  const track = document.getElementById("filmTrack");
  if (!track) return;
  const prev = document.getElementById("filmPrev");
  const next = document.getElementById("filmNext");
  let timer;
  const step = () => Math.max(track.clientWidth * 0.7, 320);
  const atEnd = () => track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
  function go(dir) {
    if (dir > 0 && atEnd()) track.scrollTo({ left: 0, behavior: "smooth" });
    else track.scrollBy({ left: dir * step(), behavior: "smooth" });
  }
  function start() { timer = setInterval(() => go(1), 4500); }
  function restart() { clearInterval(timer); start(); }
  next.addEventListener("click", () => { go(1); restart(); });
  prev.addEventListener("click", () => { go(-1); restart(); });
  track.addEventListener("mouseenter", () => clearInterval(timer));
  track.addEventListener("mouseleave", start);
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { go(1); restart(); }
    if (e.key === "ArrowLeft") { go(-1); restart(); }
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

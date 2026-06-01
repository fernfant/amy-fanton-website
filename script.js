// year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// homepage filmstrip slider — animates one image at a time
(function () {
  const track = document.getElementById("filmTrack");
  if (!track) return;
  const prev = document.getElementById("filmPrev");
  const next = document.getElementById("filmNext");
  const slides = [].slice.call(track.querySelectorAll(".film-slide"));
  if (!slides.length) return;
  let i = 0, timer, anim;

  const maxScroll = () => track.scrollWidth - track.clientWidth;
  // largest slide index that still produces a distinct scroll stop
  function lastIndex() {
    const m = maxScroll(); let li = 0;
    slides.forEach((s, k) => { if (s.offsetLeft <= m + 1) li = k; });
    return li;
  }
  function animateTo(target) {
    cancelAnimationFrame(anim);
    target = Math.max(0, Math.min(target, maxScroll()));
    const start = track.scrollLeft, dist = target - start;
    if (Math.abs(dist) < 1) return;
    const dur = 420, t0 = performance.now();
    const ease = (p) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);
    (function frame(now) {
      const p = Math.min(1, (now - t0) / dur);
      track.scrollLeft = start + dist * ease(p);
      if (p < 1) anim = requestAnimationFrame(frame);
    })(t0);
  }
  function show(n) {
    const li = lastIndex();
    if (n > li) n = 0;
    else if (n < 0) n = li;
    i = n;
    animateTo(i === 0 ? 0 : slides[i].offsetLeft);
  }
  const go = (dir) => show(i + dir);

  function start() { timer = setInterval(() => go(1), 4000); }
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

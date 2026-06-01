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

// enquiry form (Web3Forms) — graceful fallback to email
(function () {
  const form = document.getElementById("contactForm");
  if (!form) return;
  const status = document.getElementById("formStatus");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    status.textContent = "Sending…";
    status.className = "form-status";
    try {
      const res = await fetch(form.action, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        form.reset();
        status.textContent = "Thank you — your message is on its way. I'll be in touch soon.";
        status.classList.add("ok");
      } else {
        throw new Error(data.message || "send failed");
      }
    } catch (err) {
      status.textContent = "Something went wrong. Please email amy@fantonphotography.com directly.";
      status.classList.add("err");
    } finally {
      btn.disabled = false;
    }
  });
})();

// share: copy-link button
document.querySelectorAll(".share-copy").forEach((b) => {
  b.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(b.dataset.url); } catch (e) {}
    b.classList.add("copied");
    setTimeout(() => b.classList.remove("copied"), 1600);
  });
});

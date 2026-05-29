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

const form = document.getElementById("contactForm");
if (form) {
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
}

document.getElementById("year").textContent = new Date().getFullYear();

const items = [...document.querySelectorAll(".gallery-item")];
const lb = document.getElementById("lightbox");
const lbImg = document.getElementById("lbImg");
let view = items.slice(); // currently visible items the lightbox cycles through
let idx = 0;

function show(i) {
  idx = (i + view.length) % view.length;
  const el = view[idx].querySelector("img");
  lbImg.src = el.src;
  lbImg.alt = el.alt;
}

function open(item) {
  const i = view.indexOf(item);
  if (i === -1) return;
  show(i);
  lb.classList.add("open");
  lb.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function close() {
  lb.classList.remove("open");
  lb.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

items.forEach((item) => item.addEventListener("click", () => open(item)));
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

// ---------- Category filters ----------
const pills = [...document.querySelectorAll(".filter-pill")];
const emptyMsg = document.getElementById("galleryEmpty");
function applyFilter(cat) {
  view = [];
  items.forEach((item) => {
    const match = cat === "all" || item.dataset.cat === cat;
    item.hidden = !match;
    if (match) view.push(item);
  });
  if (emptyMsg) emptyMsg.hidden = view.length > 0;
}
pills.forEach((pill) => {
  pill.addEventListener("click", () => {
    pills.forEach((p) => {
      const on = p === pill;
      p.classList.toggle("is-active", on);
      p.setAttribute("aria-pressed", on ? "true" : "false");
    });
    applyFilter(pill.dataset.filter);
  });
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

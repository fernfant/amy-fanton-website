document.getElementById("year").textContent = new Date().getFullYear();

const imgs = [...document.querySelectorAll("#gallery img")];
const lb = document.getElementById("lightbox");
const lbImg = document.getElementById("lbImg");
let idx = 0;

function show(i) {
  idx = (i + imgs.length) % imgs.length;
  const el = imgs[idx];
  lbImg.src = el.src;
  lbImg.alt = el.alt;
}

function open(i) {
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

imgs.forEach((el, i) => el.addEventListener("click", () => open(i)));
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

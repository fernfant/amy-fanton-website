const y = document.getElementById("year");
if (y) y.textContent = new Date().getFullYear();

const lb = document.getElementById("lightbox");
const lbImg = document.getElementById("lbImg");
const imgs = [...document.querySelectorAll(".post-gallery img")];
let idx = 0;

function show(i) {
  if (!imgs.length) return;
  idx = (i + imgs.length) % imgs.length;
  lbImg.src = imgs[idx].src;
  lbImg.alt = imgs[idx].alt;
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
if (lb) {
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
}

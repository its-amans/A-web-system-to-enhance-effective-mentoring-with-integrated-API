const toggle = document.querySelector(".menu-toggle");
const menu = document.querySelector(".headList");

toggle.addEventListener("click", () => {
  menu.classList.toggle("active");
});

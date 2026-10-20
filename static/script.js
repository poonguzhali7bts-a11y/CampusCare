const menu = document.getElementById("menu");
const nav = document.getElementById("nav");
if (menu && nav) menu.addEventListener("click", () => nav.classList.toggle("open"));

document.querySelectorAll("form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    for (const field of form.querySelectorAll("[required]")) {
      if (!field.value.trim()) {
        event.preventDefault();
        field.focus();
        alert("Please complete all required fields.");
        return;
      }
    }
  });
});

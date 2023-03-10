const value = document.querySelector("#current");
const input = document.querySelector("#currentRange");
value.textContent = input.value;
input.addEventListener("input", (event) => {
  value.textContent = event.target.value;
});
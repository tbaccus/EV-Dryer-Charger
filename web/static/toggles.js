const dryerEnableBtn = document.querySelector("#dryerEnable");
const dryerEnableLab = document.querySelector("#dryerEnableLabel");
const dryerStartTime = document.querySelector("#dryerStartTime");
const dryerStartTimeLabel = document.getElementById("dryerStartTimeLabel");

dryerEnableBtn.addEventListener('change', function () {
  if (this.checked) {
    dryerEnableLab.textContent = "Disable";
    dryerStartTimeLabel.style.backgroundColor = "var(--bs-success-bg-subtle)";
  } else {
    dryerEnableLab.textContent = "Enable";
    dryerStartTimeLabel.style.backgroundColor = "var(--bs-form-control-disabled-bg)";
  }

  dryerStartTime.toggleAttribute("disabled");
});

const chargerEnableBtn = document.querySelector("#chargerEnable");
const chargerEnableLab = document.querySelector("#chargerEnableLabel");
const chargerStartTime = document.querySelector("#chargerStartTime");
const chargerStartTimeLabel = document.getElementById("chargerStartTimeLabel");

chargerEnableBtn.addEventListener('change', function () {
  if (this.checked) {
    chargerEnableLab.textContent = "Disable";
    chargerStartTimeLabel.style.backgroundColor = "var(--bs-success-bg-subtle)";
  } else {
    chargerEnableLab.textContent = "Enable";
    chargerStartTimeLabel.style.backgroundColor = "var(--bs-form-control-disabled-bg)";
  }

  chargerStartTime.toggleAttribute("disabled");
});

const dryerSwitch = document.querySelector("#dryerSwitch");
const dryerToggle = document.querySelector("#dryerToggle");
const chargerToggle = document.querySelector("#chargerToggle");

dryerSwitch.addEventListener('change', function () {
  if (this.checked) {
    chargerToggle.classList.remove("text-success");
    chargerToggle.classList.add("text-success-emphasis");
    dryerToggle.classList.remove("text-success-emphasis");
    dryerToggle.classList.add("text-success");
  } else {
    dryerToggle.classList.remove("text-success");
    dryerToggle.classList.add("text-success-emphasis");
    chargerToggle.classList.remove("text-success-emphasis");
    chargerToggle.classList.add("text-success");
  }
});
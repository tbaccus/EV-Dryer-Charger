const curChar = document.querySelector("#currentCharge");

$(document).on('submit', '#settingsForm', function (e) {
  e.preventDefault();
  $.ajax({
    type: 'POST',
    url: '/',
    data: {
      dryerSwitch: $("#dryerSwitch").val(),
      dryerEnable: $("#dryerEnable").val(),
      dryerStartTime: $("#dryerStartTime").val(),
      chargerEnable: $("#chargerEnable").val(),
      chargerStartTime: $("#chargerStartTime").val(),
      currentRange: $("#currentRange").val()
    },
    success: function () {
      curChar.textContent = $("#currentRange").val();
    }
  });
});
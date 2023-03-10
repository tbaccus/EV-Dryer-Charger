function test(event) {
  const formData = new FormData();

  formData.append("button", "I want to send this to backend");

  fetch("/home", {
    method: "POST",
    body: formData
  }).then(function (response) {
    data = response.json();
    return data;
  }).then(function (data) {
    alert(data.info);
    console.log(data);
  }).catch((error) => {
    console.error('Error:', error);
  });

  event.preventDefault();
}
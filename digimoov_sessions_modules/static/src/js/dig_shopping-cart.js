document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("cpf_video")
    .setAttribute("src", "https://www.youtube.com/embed/PN7gVHdT7x4");
});
function onChangeCheckButton() {
  if (document.getElementById("options-date").value !== "all") {
    document.getElementById("pm_shop_checkout").removeAttribute("disabled");
  } else {
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("disabled", "disabled");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("cpf_video")
    .setAttribute("src", "https://www.youtube.com/embed/PN7gVHdT7x4");
});
function onChangeCheckButton() {
  if (document.getElementById("options-date")) {
    if (
      document.getElementById("options-date").value === "all" ||
      document.getElementById("centre_examen").value === "all"
    ) {
      document
        .getElementById("pm_shop_checkout")
        .setAttribute("aria-disabled", "true");
      document.getElementById("pm_shop_checkout").classList.add("disabled");
    } else if (
      document.getElementById("options-date").value !== "all" &&
      document.getElementById("centre_examen").value !== "all"
    ) {
      document
        .getElementById("pm_shop_checkout")
        .removeAttribute("aria-disabled");
      document.getElementById("pm_shop_checkout").classList.remove("disabled");
    }
  } else {
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("aria-disabled", "true");
    document.getElementById("pm_shop_checkout").classList.add("disabled");
  }
}

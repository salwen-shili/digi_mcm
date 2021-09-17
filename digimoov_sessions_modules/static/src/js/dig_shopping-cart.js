document.addEventListener("DOMContentLoaded", function () {
  const formation = document.getElementById("cpf_pm").value;

  console.log(formation);

  document
    .getElementById("cpf_video")
    .setAttribute("src", "https://www.youtube.com/embed/PN7gVHdT7x4");
});
function disableButton() {
  const selectDate = document.getElementById("exam_date").value;
  console.log("selectDate", selectDate);
  if (selectDate !== "all") {
    document.getElementById("pm_shop_checkout").removeAttribute("disabled");
  } else
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("disabled", "disabled");
}
function enableButton() {
  const selectExamen = document.getElementById("centre_examen").value;
  if (selectExamen) {
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("disabled", "disabled");
  } else document.getElementById("pm_shop_checkout").removeAttribute("enabled");
}

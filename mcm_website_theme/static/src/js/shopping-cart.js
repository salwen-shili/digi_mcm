document.addEventListener("DOMContentLoaded", function () {
  var formation = document.getElementById("cpf_pm").value;

  // var cpfTaxi =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_taxielearning/81121988000085_TAXI_ELEARNING";
  // var cpfVmdtr =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_VMDTR_Elearning/81121988000085_VMDTR_E-learning";
  // var cpfVtc =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_VTC_E-LEARNING/81121988000085_VTC_E-LEARNING";
  if (formation === "Formation à distance VTC") {
    var urlVtc = "https://www.youtube.com/embed/19BiYQVwZFs";
    document.getElementById("cpf_video").setAttribute("src", urlVtc);
  } else {
    document
      .getElementById("cpf_video")
      .setAttribute("src", "https://www.youtube.com/embed/vLIr9mckz8M");
  }
});

// function disableButton() {
//   var selectDate = document.getElementById("exam_date").value;
//   console.log("disablebutton", selectDate);
//   if (selectDate !== "all") {
//     document.getElementById("pm_shop_checkout").removeAttribute("disabled");
//   } else
//     document
//       .getElementById("pm_shop_checkout")
//       .setAttribute("disabled", "disabled");
// }
// function enableButton() {
//   var selectExamen = document.getElementById("region_examen").value;
//   console.log("enableButton()", selectExamen);
//   if (selectExamen) {
//     document
//       .getElementById("pm_shop_checkout")
//       .setAttribute("disabled", "disabled");
//   } else document.getElementById("pm_shop_checkout").removeAttribute("enabled");
// }
function onChangeCheckButton() {
  if (document.getElementById("options-date")) {
    if (
      document.getElementById("options-date").value === "all" ||
      document.getElementById("region_examen").value === "all"
    ) {
      document
        .getElementById("pm_shop_checkout")
        .setAttribute("aria-disabled", "true");
      document.getElementById("pm_shop_checkout").classList.add("disabled");
    } else if (
      document.getElementById("options-date").value !== "all" &&
      document.getElementById("region_examen").value !== "all"
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

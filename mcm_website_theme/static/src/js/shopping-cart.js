document.addEventListener("DOMContentLoaded", function () {
  console.log("ready doc");
  const formation = document.getElementById("cpf_pm").value;

  console.log(formation);

  // const cpfTaxi =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_taxielearning/81121988000085_TAXI_ELEARNING";
  // const cpfVmdtr =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_VMDTR_Elearning/81121988000085_VMDTR_E-learning";
  // const cpfVtc =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_VTC_E-LEARNING/81121988000085_VTC_E-LEARNING";
  if (formation === "Formation à distance VTC") {
    const urlVtc = "https://www.youtube.com/embed/19BiYQVwZFs";
    document.getElementById("cpf_video").setAttribute("src", urlVtc);
  } else {
    document
      .getElementById("cpf_video")
      .setAttribute("src", "https://www.youtube.com/embed/vLIr9mckz8M");
  }
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
  const selectExamen = document.getElementById("region_examen").value;
  if (selectExamen) {
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("disabled", "disabled");
  } else document.getElementById("pm_shop_checkout").removeAttribute("enabled");
}
function verify_payment_method() {
  stripe_pm = document.getElementById("stripe_pm");

  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      document.getElementById("pm_shop").href = "/shop/checkout?express=1";
      document.getElementById("pm_shop_check").href =
        "/shop/checkout?express=1";
      document.getElementById("a_pm_shop_checkout").href =
        "/shop/checkout?express=1";
    }
  }
  pole_emploi_pm = document.getElementById("pole_emploi_pm");
  if (pole_emploi_pm) {
    if (pole_emploi_pm.checked == true) {
      document.getElementById("pm_shop").href = "/new/ticket/pole_emploi";
      document.getElementById("pm_shop_check").href = "/new/ticket/pole_emploi";
      document.getElementById("a_pm_shop_checkout").href =
        "/new/ticket/pole_emploi";
    }
  }
  cpf_pm = document.getElementById("cpf_pm");

  if (cpf_pm) {
    if (cpf_pm.checked == true) {
      if (cpf_pm.value == "Formation à distance TAXI") {
        console.log("TAXI", cpf_pm.value);
        document
          .getElementById("pm_shop")
          .setAttribute("href", "https://bit.ly/3DOiZG6");
        document.getElementById("pm_shop_check").href =
          "https://bit.ly/3DOiZG6";
        document.getElementById("a_pm_shop_checkout").href =
          "https://bit.ly/3DOiZG6";
      }
      if (cpf_pm.value == "Formation à distance VMDTR") {
        console.log("VMDTR", cpf_pm.value);
        document
          .getElementById("pm_shop")
          .setAttribute("href", "https://bit.ly/3tbAxXw");
        document
          .getElementById("pm_shop_check")
          .setAttribute("href", "https://bit.ly/3tbAxXw");
        document
          .getElementById("a_pm_shop_checkout")
          .setAttribute("href", "https://bit.ly/3tbAxXw");
      }
      if (cpf_pm.value == "Formation à distance VTC") {
        console.log("VTC", cpf_pm.value);
        document.getElementById("pm_shop").href = "https://bit.ly/3mZoImh";
        document.getElementById("pm_shop_check").href =
          "https://bit.ly/3mZoImh";
        document.getElementById("a_pm_shop_checkout").href =
          "https://bit.ly/3mZoImh";
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("cpf_video")
    .setAttribute("src", "https://www.youtube.com/embed/PN7gVHdT7x4");
});
function onChangeCheckButton() {
  console.log("onChangeCheckButton");
  console.log(
    'document.getElementById("options-date")',
    document.getElementById("options-date")
  );
  if (document.getElementById("options-date").value !== "all") {
    document.getElementById("pm_shop_checkout").removeAttribute("disabled");
    console.log(
      "dateOPTions: button enable",

      document.getElementById("pm_shop_checkout")
    );
  } else {
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("disabled", "disabled");
  }
  // if (){

  // }
  // else {
  //   document.getElementById("select-date").innerHTML
  // }
}

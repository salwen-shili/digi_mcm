document.addEventListener("DOMContentLoaded", function () {
  console.log("contract ready");

  //   var s = document.location.href;
  //   s = s.substring(0, s.indexOf("#") - 1);

  //   console.log(s);

  //   document.getElementById("paymentIsSuccess").value == "True"
  //     ? show=true:
  //         show=false
  var show = true;
  //   document.getElementById("paymentIsSuccess").value == "True"
  //     ? show=true:
  //         show=false
  if (show) {
    console.log("show");
    window.location.href = "#popup1";
  }
});

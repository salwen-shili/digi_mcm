window.location.href = '#';
document.addEventListener('DOMContentLoaded', function () {
  ////console.log("contract ready");

  var isSigned = document.getElementById('issigned').value;
  if (isSigned !== 'sent') {
    //console.log(isSigned);
  } else {
    //console.log('no signed');
    window.location.href = '#popup1';
  }

  //   var s = document.location.href;
  //   s = s.substring(0, s.indexOf("#") - 1);

  //   //console.log(s);

  //   document.getElementById("paymentIsSuccess").value == "True"
  //     ? show=true:
  //         show=false

  //   document.getElementById("paymentIsSuccess").value == "True"
  //     ? show=true:
  //         show=false
});

$('#identity').bind('change', function () {
  var filename = $('#identity').val();
  if (/^\s*$/.test(filename)) {
    $('#file-upload1').removeClass('active');
    $('#noFile1').text('No file chosen...');
  } else {
    $('#file-upload1').addClass('active');
    $('#noFile1').text(filename.replace('C:\\fakepath\\', ''));
  }
});
$('#identity2').bind('change', function () {
  var filename = $('#identity2').val();
  if (/^\s*$/.test(filename)) {
    $('#file-upload2').removeClass('active');
    $('#noFile2').text('No file chosen...');
  } else {
    $('#file-upload2').addClass('active');
    $('#noFile2').text(filename.replace('C:\\fakepath\\', ''));
  }
});
// $("#permis").bind("change", function () {
//   var filename = $("#permis").val();
//   if (/^\s*$/.test(filename)) {
//     $("#file-upload3").removeClass("active");
//     $("#noFile3").text("No file chosen...");
//   } else {
//     $("#file-upload3").addClass("active");
//     $("#noFile3").text(filename.replace("C:\\fakepath\\", ""));
//   }
// });

// $("#permis1").bind("change", function () {
//   var filename = $("#permis1").val();
//   if (/^\s*$/.test(filename)) {
//     $("#file-upload4").removeClass("active");
//     $("#noFile4").text("No file chosen...");
//   } else {
//     $("#file-upload4").addClass("active");
//     $("#noFile4").text(filename.replace("C:\\fakepath\\", ""));
//   }
// });

$('#mcm_my_documents_form').submit(function (event) {
  event.preventDefault();
  window.location.href = '#popup1';
});
function onClickBtn() {
  window.location.href = '#';

  document.getElementById('mcm_my_documents_form').submit();
  $('div.spanner').addClass('show');
  $('div.overlay').addClass('show');
}

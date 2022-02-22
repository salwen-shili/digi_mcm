document.addEventListener('DOMContentLoaded', function () {
  var url;
  var message;
  if (document.getElementById('url')) {
    url = document.getElementById('url').value;
  }

  if (document.getElementById('message')) {
    message = document.getElementById('message').value;
  }
  if (!document.getElementById('echec_examen').value) {
    document.getElementById('notifMessage').innerHTML = message;
    document.getElementById('btnRepassage').href = url;
  }
  return;
});
function openPopup() {
  //console.log(document.getElementById('popup1'));
  document.getElementById('popup1').style.display = 'unset';
}
function closePopup() {
  //console.log(document.getElementById('popup1'));
  document.getElementById('popup1').style.display = 'none';
}

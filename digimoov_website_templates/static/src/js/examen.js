document.addEventListener('DOMContentLoaded', function () {
  //get message and url redirection from backend
  var url;
  var message;
  if (document.getElementById('url')) {
    url = document.getElementById('url').value;
  }

  if (document.getElementById('message')) {
    message = document.getElementById('message').value;
  }
  //check in case of error to prevent displaying odoo js error
  if (!document.getElementById('echec_examen').value) {
    //change popup to the adequate message
    //setting the url
    document.getElementById('notifMessage').innerHTML = message;
    document.getElementById('btnRepassage').href = url;
  }
  return;
});
// to open popup
function openPopup() {
  //console.log(document.getElementById('popup1'));
  document.getElementById('popup1').style.display = 'unset';
}
//to close popup
function closePopup() {
  //console.log(document.getElementById('popup1'));
  document.getElementById('popup1').style.display = 'none';
}

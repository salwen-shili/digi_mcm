var message = {
  False: '',
  exam_not_passed: '',
  in_process: `La correction de votre examen est en cours. Vous recevrez votre résultat dans 24 heures.`,
  success:
    'Félicitations, vous avez réussi votre examen. Cliquez sur continuer pour finaliser votre inscription.',
  failed: "Malheureusement vous n'avez pas réussi votre examen.",
};
var notifMessage;
var condition;
var btnContiner;

function setPopup() {
  if (document.getElementById('notifMessage')) {
    notifMessage = document.getElementById('notifMessage');
    condition = document.getElementById('exam_state');
    if (condition.value == 'in_process') {
      notifMessage.innerHTML = message['in_process'];
      openPopup();
    } else if (condition.value == 'success') {
      notifMessage.innerHTML = message['success'];
      openPopup();
    } else if (condition.value == 'failed') {
      notifMessage.innerHTML = message['failed'];
      openPopup();
    } else return;
  }

  return;
}

function openPopup() {
  document.getElementById('popup1').style.display = 'flex';
}
function closePopup() {
  document.getElementById('popup1').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
  setPopup();
});

var message = {
  False: '',
  exam_not_passed: '',
  in_process: `La correction de votre examen est en cours. Vous recevrez votre résultat dans 24 heures.`,
  success:
    'Félicitations, vous avez réussi votre examen. Cliquez sur continuer pour finaliser votre inscription.',
  failed: "Malheureusement vous n'avez pas réussi votre examen.",
  cartIsEmpty: `Vous pouvez ajouter votre formation dans le panier en cliquant sur continer.`,
};
var notifMessage;
var condition;
var btnContiner;
var cartIsEmpty;

function setPopup() {
  if (document.getElementById('notifMessage')) {
    notifMessage = document.getElementById('notifMessage');
    condition = document.getElementById('exam_state');
    btnContiner = document.getElementById('btn-inside-popup');
    cartIsEmpty = document.getElementById('cartIsEmpty');
    // if (cartIsEmpty.value == 'True') {
    //   notifMessage.innerHTML = message['cartIsEmpty'];
    //   btnContiner.addEventListener('click', function () {
    //     document.getElementById('form-1-1').submit();
    //     return false;
    //   });
    //   openPopup();
    //   return;
    // } else
    if (condition.value == 'in_process' && !cartIsEmpty.value == 'True') {
      notifMessage.innerHTML = message['in_process'];
      btnContiner.addEventListener('click', function () {
        closePopup();
      });
      openPopup();
    } else if (condition.value == 'success' && !cartIsEmpty.value == 'True') {
      notifMessage.innerHTML = message['success'];
      openPopup();
      btnContiner.addEventListener('click', function () {
        closePopup();
        window.location.href = '/my/home';
      });
    } else if (condition.value == 'failed' && !cartIsEmpty.value == 'True') {
      notifMessage.innerHTML = message['failed'];
      openPopup();

      btnContiner.addEventListener('click', function () {
        closePopup();
      });
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

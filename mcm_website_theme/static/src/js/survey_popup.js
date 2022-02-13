var message = {
  exam_not_passed_true: 'Vous allez commencer votre examen',
  exam_not_passed_false: 'Vous avez deja passe votre examen',
};
var notifMessage;
var examNotPassed;
var btnContiner;
var surveybtn;

function setPopup() {
  if (document.getElementById('notifMessage')) {
    notifMessage = document.getElementById('notifMessage');
    examNotPassed = document.getElementById('exam_not_passed');
    console.log(examNotPassed.value);
    examNotPassed.value == 'True'
      ? (notifMessage.innerHTML = message['exam_not_passed_true'])
      : (notifMessage.innerHTML = message['exam_not_passed_false']);
    //set button href
    btnContiner = document.getElementById('btn-inside-popup');
    surveybtn = document.querySelector('.btn');
    btnContiner.href = surveybtn.href;
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
  openPopup();
});

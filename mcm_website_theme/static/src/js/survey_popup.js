const exam_not_passed_true = `Pour que vous puissiez profiter de notre offre, vous devez passer un petit examen blanc de
                                <b>30 MINUTES</b>
                                afin de tester vos connaissances en langue française. L'objet de cet examen est de mesurer votre degré d'assimilation des cours qui vous seront attribués lors de la formation.`;

var message = {
  exam_not_passed_true: exam_not_passed_true,
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
    // btnContiner = document.getElementById('btn-inside-popup');
    // surveybtn = document.querySelector('.btn');
    // btnContiner.href = surveybtn.href;
  }

  return;
}

function scrolltoTop() {
  window.scrollTo(0, 0);
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

function openPopupMail() {
  document.getElementById('popup2').style.display = 'flex';
}
function closePopupMail() {
  document.getElementById('popup2').style.display = 'none';
  scrolltoTop();
}

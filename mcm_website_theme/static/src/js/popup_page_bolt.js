var message = {
  exam_not_passed_true: exam_not_passed_true,
  exam_not_passed_false: 'Vous avez deja passe votre examen',
};
var notifMessage;
var condition;
var btnContiner;

function setPopup() {
  if (document.getElementById('notifMessage')) {
    notifMessage = document.getElementById('notifMessage');
    // examNotPassed = document.getElementById('exam_not_passed');
    // console.log(examNotPassed.value);
    // examNotPassed.value == 'True'
    //   ? (notifMessage.innerHTML = message['exam_not_passed_true'])
    //   : (notifMessage.innerHTML = message['exam_not_passed_false']);
    // //set button href
    // btnContiner = document.getElementById('btn-inside-popup');
    // surveybtn = document.querySelector('.btn');
    // btnContiner.href = surveybtn.href;
    if (condition == '') {
      notifMessage = '';
      openPopup();
    } else if (condition == '') {
      notifMessage = '';
      openPopup();
    } else if (condition == '') {
      notifMessage = '';
      openPopup();
    } else if (condition == '') {
      notifMessage = '';
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

//  <div id="popup1" class="overlay">
//                 <div class="popup">
//                     <h2 class="text-left">
//                         <i class="fa fa-info-circle" style="color: #111111"></i>
//                     </h2>
//                     <a class="close" onclick="closePopup()">
//                         <i class="fa fa-times"></i>
//                     </a>
//                     <!-- <div class="content">
//                         <p id="notifMessage" style="text-align: center; font-size: 16px"></p>
//                         <div class="" style="text-align-last: center; margin-block-start: 1.5rem">
//                             <div id="default">
//                                 <a id="btn-inside-popup">
//                                     <button class="rkmd-btn btn-black" onclick="">Continuer</button>
//                                 </a>
//                             </div>
//                         </div>
//                     </div> -->
//                     <div class="row align-items-center">
//                         <div class="col-lg-6 pt16 pb16 js-scroll slide-left ">
//                             <img data-src="/mcm_website_theme/static/src/img/homepage/mcm-academy-centre-de-formation-en-ligne-des-métiers-de-transports.webp" src="/mcm_website_theme/static/src/img/homepage/mcm-academy-centre-de-formation-en-ligne-des-métiers-de-transports.png" class="img img-fluid mx-auto lazy" alt="candidats centre de formation vtc" />
//                         </div>
//                         <div class="col-lg-6 pt16 pb16 js-scroll slide-right ">
//                             <h2 class="text-left">
//                                 <b>Testons vos connaissances...</b>
//                             </h2>
//                             <p id="notifMessage" style="text-align: left; font-size: 16px"></p>
//                             <div class="" style=" ">
//                                 <div id="default" class="text-center" style="margin: 1rem 0rem">
//                                     <a id="btn-inside-popup">
//                                         <button class="rkmd-btn btn-black" onclick="">Je me lance!</button>
//                                     </a>

//                                 </div>
//                                 <div class="btn-bot text-left" sytle="margin-top:12px">
//                                     <p>
//                                         <span>*Une seule tentative est prise en compte.</span>
//                                         <br />

//                                         <span>
//                                             *Si vous n'êtes pas disponible pour passer le test,
//                                             <a style="color: blue; cursor:pointer" onclick="openPopupMail();closePopup();">cliquez ici</a>
//                                             pour recevoir le lien par mail et le repasser plus tard.
//                                         </span>

//                                     </p>
//                                 </div>
//                             </div>
//                         </div>
//                     </div>

//                 </div>
//             </div>

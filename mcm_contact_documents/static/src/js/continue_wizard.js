function openCalendly() {
  document.querySelector('.calendly-badge-content').click();
}

//

const finish = `<h2 class="purple-text text-center"><strong>FÉLICITATIONS !</strong></h2> <br>
                            <div class="row justify-content-center">
                                <div class="col-3"> <img src="/mcm_contact_documents/static/img/GwStPmg.png" class="fit-image"> </div>
                            </div> <br><br>
                            <div class="row justify-content-center">
                                <div class="col-10 text-center">
                                    <h5 class="purple-text text-center" style="line-height: 30px;margin-block-end: 2rem;">Vous êtes bien inscris chez <span style="font-weight: 600;">MCM ACADEMY!</span> <br/>
                                    Vous pouvez accéder à notre plateforme de formation en créant votre compte apprenant ci dessous <i class="fa fa-hand-o-down"></i>
                                    </h5>
                                    
                                    
                                    
                                </div>
                                <a id ="button-continuer" href="https://formation.mcm-academy.fr/register?next=/dashboard" target='_blank'>
                                        <button class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
                                            <i class="material-icons right">send</i>Commencer votre formation</button>
                                    </a>
                                </div>
                           `;
const rdv = `<h2 class="purple-text text-center"><strong>FÉLICITATIONS !</strong></h2> <br>
                            <div class="row justify-content-center">
                                <div class="col-3"> <img src="/mcm_contact_documents/static/img/GwStPmg.png" class="fit-image"> </div>
                            </div> <br><br>
                            <div class="row justify-content-center">
                                <div class="col-10 text-center">
                                    <h5 class="purple-text text-center" style="line-height: 30px;margin-block-end: 2rem;">
                                      Félicitations pour votre inscription, l'un de nos agents va vous contacter suite au rendez-vous réservé pour finaliser le financement de votre examen
                                    </h5>
                                    
                                    
                                    
                                </div>
                                        
                                  
                                </div>
                           `;
const noRdv = `<h2 class="purple-text text-center"><strong>FÉLICITATIONS !</strong></h2> <br>
                            <div class="row justify-content-center">
                                <div class="col-3"> <img src="/mcm_contact_documents/static/img/GwStPmg.png" class="fit-image"> </div>
                            </div> <br><br>
                            <div class="row justify-content-center">
                                <div class="col-10 text-center">
                                    <h5 class="purple-text text-center" style="line-height: 30px;margin-block-end: 2rem;">
                                      Veuillez réserver un créneau pour finaliser votre inscription a l'examen VTC afin d'accéder à la plateforme de formation
                                    </h5>
                                    
                                    
                                    
                                </div>
                               <button id ="button-continuer" onclick='openCalendly();' class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
                                            <i class="material-icons right">send</i>Réserver un rendez-vous</button>
                                </div>
                           `;
const isNotSignedMessage = `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.`;

const textCoordonnees = `<b>Félicitations!</b> Vous avez terminé la première étape d'inscription, cliquez sur <b>continuer</b> pour passer à l'<b>étape suivante<b/>. `;
const textDocuments = `<b>Félicitations!</b> Vous avez terminé la deuxième étape d'inscription, cliquez sur <b>continuer</b> pour passer à l'<b>étape suivante<b/>. `;
const textFinancement = `<b>Félicitations!</b> Vous avez terminé la troisième étape d'inscription, cliquez sur <b>continuer</b> pour passer à l'<b>étape suivante<b/>. `;
var rdvIsBooked = false;
var bolt_contract_uri = '/';
const finishBolt = {
  rdv: rdv,
  noRdv: noRdv,
};

document.addEventListener('DOMContentLoaded', function () {
  //calendly inputs
  if (document.getElementById('rdvIsBooked')) {
    rdvIsBooked = document.getElementById('rdvIsBooked').value;
  }
  var user_name = document.getElementById('user_name_connected').value;
  var user_email = document.getElementById('user_email_connected').value;
  //
  const current = document.getElementById('step_value');
  // console.log(current.value);

  const finished = document.getElementById('finished');
  const documents = document.getElementById('personal');
  const documentsUrl = '/charger_mes_documents';
  const financement = document.getElementById('payment');
  const financementUrl = '/shop/cart';
  const validation = document.getElementById('confirm');
  const validationUrl = '/validation';
  const btnContinuer = document.getElementById('button-continuer');
  const questionnaireUrl = '/coordonnees';
  const textDescription = document.getElementById('textDescription');
  var bolt_contract_uri = '/';
  //is Bolt

  var isBolt = document.getElementById('isBolt').value;
  const isSigned = document.getElementById('isSigned').value;
  // const rdvIsBooked = document.getElementById('finished');
  // const rdvIsBooked = document.getElementById('rdvIsBooked').value;
  // const contractIsSigned = document.getElementById('contractIsSigned').value;
  //

  var step = 1;
  console.log('step', current.value);
  switch (current.value) {
    case 'coordonnées':
      step = 1;
      btnContinuer.setAttribute('href', questionnaireUrl);

      textDescription.innerHTML = textCoordonnees;

      break;
    case 'document':
      step = 2;
      documents.classList.add('active');

      textDescription.innerHTML = textDocuments;

      btnContinuer.setAttribute('href', documentsUrl);

      break;
    case 'financement':
      //has not signed his contract
      //he has paid so he must has a contract
      //we recheck if we have an url
      if (document.getElementById('bolt_contract_uri').value !== 'False') {
        bolt_contract_uri = document.getElementById('bolt_contract_uri').value;
        console.log(bolt_contract_uri);
        if (document.getElementById('btn-action')) {
          textDescription.textContent = isNotSignedMessage;
          btnAction = document.getElementById('btn-action');
          btnAction.innerText = 'Signer mon contrat';
          btnAction.addEventListener('click', function () {
            window.location.href = bolt_contract_uri;
          });
        }
      } else {
        step = 3;
        documents.classList.add('active');
        financement.classList.add('active');

        textDescription.innerHTML = textFinancement;

        btnContinuer.setAttribute('href', financementUrl);
      }

      break;
    case 'validation':
      step = 4;
      documents.classList.add('active');
      financement.classList.add('active');
      validation.classList.add('active');
      btnContinuer.setAttribute('href', validationUrl);
      if (current.value === 'finish') {
        finished.innerHTML = finish;
      }
      break;
    case 'finish':
      step = 4;
      console.log(step);
      documents.classList.add('active');
      financement.classList.add('active');
      validation.classList.add('active');

      if (isBolt == 'True') {
        if (isSigned == 'True') {
          alert();
          //Client bolt + contrat is signed
          //check if he has reserved an appointment
          if (rdvIsBooked == 'True') {
            //has reserved => he will wait for his call
            finished.innerHTML = finishBolt['rdv'];
            console.log("rdvIsBooked == 'True'", rdvIsBooked == 'True');
          } else {
            console.log("else rdvIsBooked == 'True'", rdvIsBooked == 'True');
            // has to reserve appointment
            //  => Show bolt calendly
            finished.innerHTML = finishBolt['noRdv'];
            Calendly.initBadgeWidget({
              url: 'https://calendly.com/mcm-academy/examen-vtc-cma',
              prefill: {
                name: user_name,
                email: user_email,
              },
              text: "Inscription à l'examen VTC",
              color: '#1A1A1A',
              textColor: '#FFFFFF',
            });
          }
        }
      } else {
        // his not bolt
        // => Step 4 is his final step
        // => redirect to e-learning plateform
        finished.innerHTML = finish;
      }

      break;

    default:
      break;
  }
  var progressBarValue = step * 25;
  console.log(step);
  document.getElementsByClassName('progress-bar')[0].style.width =
    progressBarValue + '%';
});

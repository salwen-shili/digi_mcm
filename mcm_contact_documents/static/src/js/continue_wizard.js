function openCalendly() {
  if (document.querySelector('.calendly-badge-content')) {
    document.querySelector('.calendly-badge-content').click();
  } else {
    console.log('Error Loading Calendly...');
  }
}

//

const financement = document.getElementById('payment');
const financementUrl = `/shop/cart?${Math.floor(Math.random() * 100)}`;
const validation = document.getElementById('confirm');
const validationUrl = `/validation?${Math.floor(Math.random() * 100)}`;
const btnContinuer = document.getElementById('button-continuer');

const textDescription = document.getElementById('textDescription');

const messageAction = {
  coordonnees: {
    message: `<b>Félicitations!</b> Vous avez terminé la première étape de votre inscription. Cliquez sur <b>continuer</b> pour passer à l'<b>étape suivante<b/>. `,
    url: `/coordonnees?${Math.floor(Math.random() * 100)}`,
  },
  documents: {
    message: `<b>Félicitations!</b> Vous avez terminé l'étape <b>Coordonnées</b> de votre inscription. Pour passer à l'étape suivante merci de vous munir d'une copie originale de votre carte d'identité, et veuillez choisir le mode de téléchargement souhaité :`,
    url: `/charger_mes_documents?${Math.floor(Math.random() * 100)}`,
  },
  financement: {
    message: `<b>Félicitations!</b> Vous avez chargé vos documents. Vous pourrez désormais choisir votre date et centre d'examen et financer votre formation.`,
    url: `/shop/cart?${Math.floor(Math.random() * 100)}`,
  },
  isNotSigned: {
    message: `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.`,
    url: '',
  },

  cartIsEmpty: {
    message: `Votre panier est vide. Vous devez choisir votre formation en cliquant sur continuer.`,
    url: '/bolt#pricing',
  },
  boltWrongCart: {
    message: `Vous n'avez pas choisit la <b>formation VTC BOLT</b>. Vous devez cliquer sur continuer pour mettre à jour votre panier`,
    url: '/bolt#pricing',
  },
  boltExamen: {
    inProcess: {
      message: `La correction de votre examen est en cours. Vous recevrez votre résultat dans 24 heures.`,
      url: `/coordonnees?${Math.floor(Math.random() * 100)}`,
    },
    notpassed: {
      message: `<b>Félicitations!</b> Vous avez terminé la première étape de votre inscription. Cliquez sur <b>continuer</b> pour passer votre <b> examen blanc<b/>. `,
      url: `/coordonnees?${Math.floor(Math.random() * 100)}`,
    },
    succed: {
      message:
        'Félicitations, vous avez réussi votre examen. Cliquez sur continuer pour finaliser votre inscription.',
      url: `/coordonnees?${Math.floor(Math.random() * 100)}`,
    },
    failed: {
      message: "Malheureusement vous n'avez pas réussi votre examen.",
      url: `#`,
    },
  },
};

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
var rdvIsBooked = false;
var bolt_contract_uri = '/';
const finishBolt = {
  rdv: rdv,
  noRdv: noRdv,
};

//wait page load

document.addEventListener('DOMContentLoaded', function () {
  //calendly inputs
  if (document.getElementById('rdvIsBooked')) {
    rdvIsBooked = document.getElementById('rdvIsBooked').value;
  }
  var boltWrongCart;
  if (document.getElementById('boltWrongCart')) {
    boltWrongCart = document.getElementById('boltWrongCart').value;
  }
  var user_name = document.getElementById('user_name_connected').value;
  var user_email = document.getElementById('user_email_connected').value;
  //
  const current = document.getElementById('step_value');

  // console.log(current.value);

  var bolt_contract_uri = '/';
  //is Bolt

  var isBolt = document.getElementById('isBolt').value;
  const isSigned = document.getElementById('isSigned').value;
  // const rdvIsBooked = document.getElementById('finished');
  // const rdvIsBooked = document.getElementById('rdvIsBooked').value;
  // const contractIsSigned = document.getElementById('contractIsSigned').value;
  //

  // const financementUrl = `/shop/cart?${Math.floor(Math.random() * 100)}`;

  // const validationUrl = `/validation?${Math.floor(Math.random() * 100)}`;
  const btnContinuer = document.getElementById('button-continuer');

  const textDescription = document.getElementById('textDescription');
  activateStep(current.value);
  //console.log('step', current.value);
  if (isBolt == 'True' && boltWrongCart == 'True') {
    //bolt user with a wrong cart (other than bolt-vtc)
    btnContinuer.setAttribute('href', messageAction.boltWrongCart.url);
    textDescription.innerHTML = messageAction.boltWrongCart.message;
    return;
  } else if (
    isBolt == 'True' &&
    document.getElementById('cartIsEmpty').value === 'True' &&
    document.getElementById('bolt_contract_uri').value === 'False'
  ) {
    //bolt user with empty cart
    btnContinuer.setAttribute('href', messageAction.cartIsEmpty.url);
    textDescription.innerHTML = messageAction.cartIsEmpty.message;
    return;
  }

  switch (current.value) {
    case 'coordonnées':
      // coordonnes is the first step by default
      // we will treat exam state of bolt here any way
      //Bolt exam state : exam_not_passed, in_process, success, failed
      if (isBolt == 'True') {
        if (document.getElementById('exam_state')) {
          switch (document.getElementById('exam_state').value) {
            case 'exam_not_passed':
              btnContinuer.setAttribute(
                'href',
                messageAction.boltExamen.notpassed.url
              );
              textDescription.innerHTML =
                messageAction.boltExamen.notpassed.message;
              break;
            case 'in_process':
              btnContinuer.setAttribute(
                'href',
                messageAction.boltExamen.inProcess.url
              );
              textDescription.innerHTML =
                messageAction.boltExamen.inProcess.message;
              break;
            case 'success':
              btnContinuer.setAttribute(
                'href',
                messageAction.boltExamen.succed.url
              );
              textDescription.innerHTML =
                messageAction.boltExamen.succed.message;
              break;
            case 'failed':
              btnContinuer.setAttribute(
                'href',
                messageAction.boltExamen.failed.url
              );
              textDescription.innerHTML =
                messageAction.boltExamen.failed.message;
              break;
          }
        }
      } else {
        // coordonnees
        btnContinuer.setAttribute('href', messageAction.coordonnees.url);
        textDescription.innerHTML = messageAction.coordonnees.message;
      }
      break;
    case 'document':
      textDescription.innerHTML = messageAction.documents.message;
      // btnContinuer.setAttribute('href', messageAction.documents.url);
      const uploadMode = `<a  href="/charger_mes_documents_manual" class="text-center next action-button" style="float: unset !important; width: 111px;" value="Manuel"  />
                                                <a href="/charger_mes_documents" class="text-center next action-button" style="float: unset !important; width: 111px;" value="Automatique" ;`;
      // btnContinuer.html = uploadMode;
      break;
    case 'financements':
      //has not signed his contract
      //he has paid so he must has a contract
      //we recheck if we have an url

      if (document.getElementById('bolt_contract_uri').value !== 'False') {
        bolt_contract_uri = document.getElementById('bolt_contract_uri').value;
        console.log(bolt_contract_uri);
        if (document.getElementById('btn-action')) {
          textDescription.textContent = messageDescription[isNotSignedMessage];
          btnAction = document.getElementById('btn-action');
          btnAction.innerText = 'Signer mon contrat';
          btnAction.addEventListener('click', function () {
            window.location.href = bolt_contract_uri;
          });
        }
      } else {
        textDescription.innerHTML = messageDescription[textFinancement];
        btnContinuer.setAttribute('href', financementUrl);
      }

      break;
    case 'validation':
      btnContinuer.setAttribute('href', validationUrl);
      if (current.value === 'finish') {
        finished.innerHTML = finish;
      }
      break;
    case 'finish':
      if (isBolt == 'True') {
        if (isSigned == 'True') {
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
            setTimeout(function () {
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
            }, 1500);
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

  //
});

function activateStep(stepValue) {
  const finished = document.getElementById('finished');
  const documents = document.getElementById('personal');
  const financement = document.getElementById('payment');
  const validation = document.getElementById('confirm');
  console.log(stepValue);
  var step = 1;

  switch (stepValue) {
    case 'document':
      step = 2;
      documents.classList.add('active');

      break;
    case 'financement':
      step = 3;
      documents.classList.add('active');
      financement.classList.add('active');

      break;
    case 'validation':
      step = 4;
      documents.classList.add('active');
      financement.classList.add('active');
      validation.classList.add('active');

      break;
    case 'finish':
      step = 4;
      documents.classList.add('active');
      financement.classList.add('active');
      validation.classList.add('active');
      break;

    default:
      break;
  }

  var progressBarValue = step * 25;
  //console.log(step);
  document.getElementsByClassName('progress-bar')[0].style.width =
    progressBarValue + '%';
}

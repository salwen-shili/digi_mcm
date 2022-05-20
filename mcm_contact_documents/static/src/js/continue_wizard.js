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
  boltIsSigned: {
    isSignedBolt_registredCMA: {
      message: `Bravo ! Votre inscription à la formation et à l'examen est complète, vous pouvez commencer votre formation en cliquant sur le bouton suivant.`,
      url: '/',
    },
    isSignedBolt_notRegistredCMA: {
      message: `Vos documents sont en cours de vérification, dès qu'ils seront validés, nous vous inscrirons à l'examen VTC auprès de la chambre des métiers.`,
      url: '/',
    },
  },
  cartIsEmpty: {
    bolt: {
      message: `Votre panier est vide. Vous devez choisir votre formation en cliquant sur continuer.`,
      url: '/bolt#pricing',
    },
    nonBolt: {
      message: `Votre panier est vide. Vous devez choisir votre formation en cliquant sur continuer.`,
      url: '/#pricing',
    },
  },
  boltWrongProduct: {
    message: `Vous n'avez pas choisit la <b>formation VTC BOLT</b>. Vous devez cliquer sur continuer pour mettre à jour votre panier`,
    url: '/bolt#pricing',
  },
  boltExamen: {
    inProcess: {
      message: `La correction de votre examen est en cours. Vous recevrez votre résultat dans 24 heures.`,
      url: `/examen-blanc`,
    },
    notpassed: {
      message: `<b>Félicitations!</b> Vous avez terminé la première étape de votre inscription. Cliquez sur <b>continuer</b> pour passer votre <b> examen blanc<b/>. `,
      url: `/examen-blanc`,
    },
    succed: {
      message:
        'Félicitations, vous avez réussi votre examen. Cliquez sur continuer pour finaliser votre inscription.',
      url: `/examen-blanc`,
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
  const finished = document.getElementById('finished');
  const documents = document.getElementById('personal');
  //calendly inputs
  if (document.getElementById('rdvIsBooked')) {
    rdvIsBooked = document.getElementById('rdvIsBooked').value;
  }
  var boltWrongProduct;
  if (document.getElementById('boltWrongProduct')) {
    boltWrongProduct = document.getElementById('boltWrongProduct').value;
  }
  var user_name = document.getElementById('user_name_connected').value;
  var user_email = document.getElementById('user_email_connected').value;
  //
  const current = document.getElementById('step_value');

  // console.log(current.value);

  var bolt_contract_uri = '/';
  //is Bolt

  var isBoltState = document.getElementById('isBolt').value;
  const isSignedState = document.getElementById('isSigned').value;
  // const rdvIsBooked = document.getElementById('finished');
  // const rdvIsBooked = document.getElementById('rdvIsBooked').value;
  // const contractIsSigned = document.getElementById('contractIsSigned').value;

  // const financementUrl = `/shop/cart?${Math.floor(Math.random() * 100)}`;

  // const validationUrl = `/validation?${Math.floor(Math.random() * 100)}`;
  const btnContinuer = document.getElementById('button-continuer');

  const textDescription = document.getElementById('textDescription');
  activateStep(current.value);
  //console.log('step', current.value);

  //===================================================================================================================
  //
  //                           All Dashboard conditions starts here
  //
  //====================================================================================================================

  if (isBoltState == 'True' && boltWrongProduct == 'True') {
    //bolt user with a wrong cart (other than bolt-vtc) [old process]
    btnContinuer.setAttribute('href', messageAction.boltWrongProduct.url);
    textDescription.innerHTML = messageAction.boltWrongProduct.message;
    return;
  } else if (
    isBoltState == 'True' &&
    document.getElementById('cartIsEmpty').value == 'True'
  ) {
    //=============================REMOVE COMMENT AFTER CORRECTING CONTRACT URI===========================================
    //bolt user with empty cart
    // btnContinuer.setAttribute('href', messageAction.cartIsEmpty.bolt.url);
    // textDescription.innerHTML = messageAction.cartIsEmpty.bolt.message;
    //====================================================================================================================

    //===================================================================================================================
    //
    //                          Old process => exam state replaced with note.
    //
    //====================================================================================================================
    // if (document.getElementById('exam_state')) {
    //   switch (document.getElementById('exam_state').value) {
    //     case 'exam_not_passed':
    //       btnContinuer.setAttribute('href', messageAction.boltExamen.notpassed.url);
    //       textDescription.innerHTML = messageAction.boltExamen.notpassed.message;

    //       break;
    //     // case 'in_process':
    //     //   btnContinuer.setAttribute(
    //     //     'href',
    //     //     messageAction.boltExamen.inProcess.url
    //     //   );
    //     //   textDescription.innerHTML =
    //     //     messageAction.boltExamen.inProcess.message;
    //     //   break;
    //     case 'success':
    //       btnContinuer.setAttribute('href', messageAction.boltExamen.succed.url);
    //       textDescription.innerHTML = messageAction.boltExamen.succed.message;
    //       break;
    //     case 'failed':
    //       btnContinuer.setAttribute('href', messageAction.boltExamen.failed.url);
    //       textDescription.innerHTML = messageAction.boltExamen.failed.message;
    //       break;
    //   }
    // }

    const partner = partnerInformation();
    partner.then((p) => {
      //const url = `/inscription-bolt?nom[first]=${p.fisrtname}&nom[last]=${lastName}&email=${email}&numeroDe93=${phone}&adresse=${street}&adresse[city]=${p.city}&adresse[postal]=${zip}`;
      console.log(p);

      if (p.note_exam == false) {
        if (p.ipJotForm == false) {
          // bolt redirect to inscription (Old users generally)
          btnContinuer.setAttribute(
            'href',
            `/inscription-bolt?nom[first]=${p.fisrtname}&nom[last]=${p.lastName}&email=${p.email}&numeroDe93=${p.phone}&adresse=${p.street}&adresse[city]=${p.city}&adresse[postal]=${p.zip}`
          );
          textDescription.innerHTML =
            'Vous pouvez charger vos documents en cliquant sur continuer.';
        } else if (p.ipJotForm == true) {
          // bolt client has an account completed with jotform and need to pass his exam
          btnContinuer.setAttribute(
            'href',
            `/examen-blanc?nom[first]=${p.fisrtname}&nom[last]=${p.lastName}&email=${p.email}&numeroDe172=${p.phone}&adresse=${p.street}&adresse[city]=${p.city}&adresse[postal]=${p.zip}`
          );
          textDescription.innerHTML = messageAction.boltExamen.notpassed.message;
        }
      } else if (p.note_exam != false) {
        //bolt client has passed his exam
        switch (p.exam_state) {
          case 'success':
            //Testing contract signed or not
            console.log('isSignedState', isSignedState);
            bolt_contract_uri = document.getElementById('bolt_contract_uri').value;
            console.log(bolt_contract_uri);
            if (isSignedState == 'True') {
              // testing is registred to CMA or not with evalbox true or false

              if (p.evalbox == false) {
                //not registred in CMA
                textDescription.innerHTML =
                  messageAction.boltIsSigned.isSignedBolt_notRegistredCMA.message;
                btnContinuer.setAttribute(
                  'href',
                  messageAction.boltIsSigned.isSignedBolt_notRegistredCMA.url
                );

                btnContinuer.innerHTML = ``;
              } else {
                //is registred in CMA
                textDescription.innerHTML =
                  messageAction.boltIsSigned.isSignedBolt_registredCMA.message;
                btnContinuer.setAttribute(
                  'href',
                  messageAction.boltIsSigned.isSignedBolt_registredCMA.url
                );

                btnContinuer.innerHTML = `\n <button id="btn-action" class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
                                            <i class="material-icons right">send</i>
                                            Continuer
                                        </button>`;
              }
            } else {
              //constract is not signed
              bolt_contract_uri = document.getElementById('bolt_contract_uri').value;
              console.log(bolt_contract_uri);
              textDescription.innerHTML = `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat.`;

              btnContinuer.setAttribute('href', bolt_contract_uri);

              btnContinuer.innerHTML = `\n <button id="btn-action" class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
                                            <i class="material-icons right">send</i>
                                            Signer mon contrat
                                        </button>`;
              btnAction.addEventListener('click', function () {
                window.location.href = bolt_contract_uri;
              });
            }

            // btnContinuer.setAttribute(
            //   'href',
            //   `/inscription-bolt?nom[first]=${p.fisrtname}&nom[last]=${p.lastName}&email=${p.email}&numeroDe93=${p.phone}&adresse=${p.street}&adresse[city]=${p.city}&adresse[postal]=${p.zip}`
            // );
            // textDescription.innerHTML = p.note_exam + p.exam_state;
            break;
          case 'failed':
            btnContinuer.setAttribute(
              'href',
              `/inscription-bolt?nom[first]=${p.fisrtname}&nom[last]=${p.lastName}&email=${p.email}&numeroDe93=${p.phone}&adresse=${p.street}&adresse[city]=${p.city}&adresse[postal]=${p.zip}`
            );
            btnContinuer.innerHTML = `\n <button id="btn-action" class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
                                            <i class="material-icons right">send</i>
                                            voir l'offre
                                        </button>`;
            textDescription.innerHTML = `<b>Malheureusement <b/> 🙁, vous avez obtenu une note de ${
              p.note_exam / 5
            }/20 ce qui n'est pas suffisant pour bénéficier de l'offre à 20€ <br/>(note minimum pour bénéficier de l'offre : 8/20).<br/>
Mais nous avons une autre offre pour vous...`;

            break;

          default:
            break;
        }
      }
    });

    return;
  } else if (
    document.getElementById('cartIsEmpty').value == 'True' &&
    document.getElementById('bolt_contract_uri').value == 'False'
  ) {
    //not a bolt user with empty cart
    btnContinuer.setAttribute('href', messageAction.cartIsEmpty.nonBolt.url);
    textDescription.innerHTML = messageAction.cartIsEmpty.nonBolt.message;
  }

  switch (current.value) {
    case 'coordonnées':
      // coordonnes is the first step by default
      // we will treat exam state of bolt here any way
      //Bolt exam state : exam_not_passed, in_process, success, failed

      if (document.getElementById('cartIsEmpty').value == 'False') {
        //
        // if (isBoltState == 'True') {
        //   if (document.getElementById('exam_state')) {
        //     switch (document.getElementById('exam_state').value) {
        //       case 'exam_not_passed':
        //         btnContinuer.setAttribute('href', messageAction.boltExamen.notpassed.url);
        //         textDescription.innerHTML = messageAction.boltExamen.notpassed.message;
        //         break;
        //       // case 'in_process':
        //       //   btnContinuer.setAttribute(
        //       //     'href',
        //       //     messageAction.boltExamen.inProcess.url
        //       //   );
        //       //   textDescription.innerHTML =
        //       //     messageAction.boltExamen.inProcess.message;
        //       //   break;
        //       case 'success':
        //         btnContinuer.setAttribute('href', messageAction.boltExamen.succed.url);
        //         textDescription.innerHTML = messageAction.boltExamen.succed.message;
        //         break;
        //       case 'failed':
        //         btnContinuer.setAttribute('href', messageAction.boltExamen.failed.url);
        //         textDescription.innerHTML = messageAction.boltExamen.failed.message;
        //         break;
        //     }
        //   }
        // }
        //else{}
        //
        // coordonnees
        // const partner = partnerInformation();
        // partner.then((p) => {
        //   console.log(p);
        //   alert();
        // });
        // btnContinuer.setAttribute('href', messageAction.coordonnees.url);
        // textDescription.innerHTML = messageAction.coordonnees.message;
      }

      break;
    case 'document':
      if (document.getElementById('cartIsEmpty').value == 'False') {
        step = 2;
        documents.classList.add('active');

        textDescription.innerHTML = messageAction.documents.message;

        // btnContinuer.setAttribute('href', documentsUrl);
        const uploadDocumentBtns = `
        <div style="
  
    display: flex;
    align-content: center;
    justify-content: center;
    align-items: flex-end;
    flex-wrap: wrap;
    flex-direction: row;
">
                                    <div class="">
                                        <a id="button-continuer" href="/charger_mes_documents_manual?${Math.floor(
                                          Math.random() * 100
                                        )}" style="margin-right: 8px;">
                                            <button id="btn-action" class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;width:116px">
                                            
                                            Manuel
                                        </button>
                                        </a>
                                    </div>

                                    <div class="">

                                        <a id="button-continuer" href="/charger_mes_documents?${Math.floor(
                                          Math.random() * 100
                                        )}">
                                            <button id="btn-action" class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;width:116px;">
                                            
                                            Auto
                                        </button>
                                        </a>
                                    </div>
                                </div>`;
        finished.innerHTML = uploadDocumentBtns;

        break;
      }
    case 'financement':
      //has not signed his contract
      //he has paid so he must has a contract
      //we recheck if we have an url
      if (document.getElementById('cartIsEmpty').value == 'False') {
        if (document.getElementById('bolt_contract_uri').value !== 'False') {
          bolt_contract_uri = document.getElementById('bolt_contract_uri').value;

          if (document.getElementById('btn-action')) {
            textDescription.textContent = messageDescription[isNotSignedMessage];
            btnAction = document.getElementById('btn-action');
            btnAction.innerText = 'Signer mon contrat';
            btnAction.addEventListener('click', function () {
              window.location.href = bolt_contract_uri;
            });
          }
        } else {
          textDescription.innerHTML = messageAction.financement.message;
          btnContinuer.setAttribute('href', messageAction.financement.url);
        }

        break;
      }

    // case 'validation':
    //   btnContinuer.setAttribute('href', validationUrl);
    //   if (current.value === 'finish') {
    //     finished.innerHTML = finish;
    //   }
    //   break;
    case 'finish':
      if (document.getElementById('cartIsEmpty').value == 'False') {
        if (isBoltState == 'True') {
          if (isSignedState == 'True') {
            //********************* New process with Jotform*/
            //********************* */
            //********************* */
            finished.innerHTML = finishBolt['rdv'];
            //********************* End New process with Jotform */
            //********************* */
            //********************* */

            //*****************************//
            //*****************************//
            //************** Old Process     *******************//
            //Client bolt + contrat is signed
            //check if he has reserved an appointment
            // if (rdvIsBooked == 'True') {
            //   //has reserved => he will wait for his call
            //   finished.innerHTML = finishBolt['rdv'];
            //   console.log("rdvIsBooked == 'True'", rdvIsBooked == 'True');
            // } else {
            //   console.log("else rdvIsBooked == 'True'", rdvIsBooked == 'True');
            //   // has to reserve appointment
            //   //  => Show bolt calendly
            //   finished.innerHTML = finishBolt['noRdv'];
            //   setTimeout(function () {
            //     Calendly.initBadgeWidget({
            //       url: 'https://calendly.com/mcm-academy/examen-vtc-cma',
            //       prefill: {
            //         name: user_name,
            //         email: user_email,
            //       },
            //       text: "Inscription à l'examen VTC",
            //       color: '#1A1A1A',
            //       textColor: '#FFFFFF',
            //     });
            //   }, 1500);
            // }
            //************** End Old Process ****************//
            //*****************************//
            //*****************************//
          }
        } else {
          // his not bolt
          // => Step 4 is his final step
          // => redirect to e-learning plateform
          finished.innerHTML = finish;
        }
      }

      break;

    default:
      break;
  }
  // var test = partnerInformation();
  // test.then((res) => {
  //   textDescription.innerHTML = res.name;
  // });
  //
});

function activateStep(stepValue) {
  const finished = document.getElementById('finished');
  const documents = document.getElementById('personal');
  const financement = document.getElementById('payment');
  const validation = document.getElementById('confirm');
  // console.log(stepValue);
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
  document.getElementsByClassName('progress-bar')[0].style.width = progressBarValue + '%';
}

//HTTP REQUEST CALL
const partnerInformation = async () => {
  try {
    // const res = await JSON.parse(sendHttpRequest('POST', '/get_data_user_connected', {}));
    const res = await sendHttpRequest('POST', '/get_data_user_connected', {});
    const partner = JSON.parse(res.result);
    // console.log(partner.response);
    // console.log(partner.response[0]);
    return partner.response[0];
  } catch (e) {
    return 'error partnerInformation()';
  }
  // const res = await sendHttpRequest('POST', '/get_data_user_connected', {});
  // const partner = JSON.parse(res.result);
  // console.log(partner.response);
  // console.log(partner.response[0]);
  // return partner.response[0];
};
const sendHttpRequest = (method, url, data) => {
  const promise = new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);

    xhr.responseType = 'json';

    if (data) {
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    }

    xhr.onload = () => {
      if (xhr.status >= 400) {
        reject(xhr.response);
      } else {
        resolve(xhr.response);
      }
    };

    xhr.onerror = () => {
      reject('Something went wrong!');
    };

    xhr.send(JSON.stringify(data));
  });
  return promise;
};

//

var showContract;
var list;
document.addEventListener('DOMContentLoaded', function () {
  showContract = document.getElementById("showContract");
   list = document.querySelectorAll(".o_portal_docs.list-group");
  if (showContract) showContract = showContract.value
  else showContract = null
  if (list && showContract=="False"){
    if (list[0].children){
      Array.from(list[0].children).forEach((card) => {
        if (card.title == "Contrats non signés" || card.title == "Contrats signés"){
          card.remove()
        }
      })

    }
  }
  
  const current = document.getElementById('step_value');
  console.log(current.value);

  const finish = `<h2 class="purple-text text-center"><strong>FÉLICITATIONS !</strong></h2> <br>
                            <div class="row justify-content-center">
                                <div class="col-3"> <img src="/mcm_contact_documents/static/img/GwStPmg.png" class="fit-image"> </div>
                            </div> <br><br>
                            <div class="row justify-content-center">
                                <div class="col-10 text-center">
                                    <h5 class="purple-text text-center" style="line-height: 30px;margin-block-end: 2rem;">Vous êtes bien inscris chez <span style="font-weight: 600;">DIGIMOOV!</span>
                <br/>
     Vous allez recevoir vos accès à la plateforme de formation très prochainement
            </h5>
                                    
                                    
                                    
                                </div>
                         
                                </div>
                                `;

  const finished = document.getElementById('finished');

  const documents = document.getElementById('personal');
  const documentsUrl = '/charger_mes_documents';
  const financement = document.getElementById('payment');
  const financementUrl = '/shop/cart';
  const validation = document.getElementById('confirm');
  const validationUrl = '/validation';
  const btnContinuer = document.getElementById('button-continuer');
  const questionnaireUrl = '/coordonnees';

  const messageAction = {
    coordonnees: {
      message: `<b>Félicitations!</b> Vous avez terminé la première étape de votre inscription. Cliquez sur <b>continuer</b> pour passer à l'<b>étape suivante<b/>. `,
      url: `/coordonnees?${Math.floor(Math.random() * 100)}`,
    },
    documents: {
      message: `<b>Félicitations!</b> Vous avez terminé l'étape <b>Coordonnées</b> de votre inscription. Pour passer à l'étape suivante merci de vous munir d'une copie originale de votre pièce d'identité et cliquer sur continuer.`,
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

  if (document.getElementById('cartIsEmpty').value == 'True' &&
  document.getElementById('contract_uri').value == 'False')
  
 {
  //not a bolt user with empty cart
  btnContinuer.setAttribute('href', messageAction.cartIsEmpty.nonBolt.url);
  textDescription.innerHTML = messageAction.cartIsEmpty.nonBolt.message;
  return 
}

  var step = 1;
  console.log('step', current.value);
  switch (current.value) {
    case 'coordonnées':
     
      step = 1;

      // btnContinuer.setAttribute('href', questionnaireUrl);
      btnContinuer.setAttribute('href', messageAction.coordonnees.url);
      textDescription.innerHTML = messageAction.coordonnees.message;

     
      break;
    case 'document':
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
                                        <a id="button-continuer" href="/charger_mes_documents?${Math.floor(
                                          Math.random() * 100
                                        )}" style="margin-right: 8px;">
                                            <button id="btn-action" class="rkmd-btn green-shop  ripple-effect ripple-yellow" type="submit" style="font-size: 11px;width:116px">
                                            
                                            Continuer
                                        </button>
                                        </a>
                                    </div>

                                   
                                </div>`;
      // auto and manual possible to uncomment when return to auto verification
      //<div class=''>
      //    <a
      //      id='button-continuer'
      //      href='/charger_mes_documents?${Math.floor(Math.random() * 100)}'
      //    >
      //      <button
      //        id='btn-action'
      //        class='rkmd-btn green-shop  ripple-effect ripple-yellow'
      //        type='submit'
      //        style='font-size: 11px;width:116px;'
      //      >
      //        Auto
      //      </button>
      //    </a>
      //  </div>;

      finished.innerHTML = uploadDocumentBtns;
     
      break;
    case 'financement':
      step = 3;
      documents.classList.add('active');
      financement.classList.add('active');
      textDescription.innerHTML = messageAction.financement.message;
      btnContinuer.setAttribute('href', messageAction.financement.url);

      
      
      //has not signed his contract
      //he has paid so he must has a contract
      //we recheck if we have an url
      if (document.getElementById('cartIsEmpty').value == 'True') {
        console.log("empty")
        if (document.getElementById('contract_uri').value != 'False') {
          console.log("contract_uri")
    

          if (document.getElementById('button-continuer')) {
            if (showContract == "False"){
              document.getElementsByClassName('progress-bar')[0].style.width = step * 25 + '%';
              textDescription.textContent = `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en cliquant sur continuer.`;
            
            btnContinuer.innerHTML = `<button class="rkmd-btn green-shop ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
            <i class="material-icons right">send</i>
            Continuer
        </button>` ;
           
            btnContinuer.setAttribute('href', document.getElementById('urlCpfLourd').value);

            }else{

            textDescription.textContent = `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.`;
            
            btnContinuer.innerHTML = `<button class="rkmd-btn green-shop ripple-effect ripple-yellow" type="submit" style="font-size: 11px;">
            <i class="material-icons right">send</i>
            Signer mon contrat
        </button>` ;
           
            btnContinuer.setAttribute('href', document.getElementById('contract_uri').value);
            }
          }
        } 

        break;
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
      //console.log(step);
      documents.classList.add('active');
      financement.classList.add('active');
      validation.classList.add('active');

      finished.innerHTML = finish;

      break;

    default:
      break;
  }
  var progressBarValue = step * 25;
  //console.log(step);
  document.getElementsByClassName('progress-bar')[0].style.width = progressBarValue + '%';
});



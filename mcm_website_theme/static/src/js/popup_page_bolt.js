var message = {
  False: '',
  exam_not_passed: 'Vous pouvez passer votre examen blanc en cliquant sur continuer.',
  in_process: `La correction de votre examen est en cours. Vous recevrez votre résultat dans 24 heures.`,
  success:
    'Félicitations, vous avez réussi votre examen. Cliquez sur continuer pour finaliser votre inscription.',
  failed: "Malheureusement vous n'avez pas réussi votre examen.",
  cartIsEmpty: `Vous pouvez ajouter votre formation dans le panier en cliquant sur continuer.`,
};
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
      url: `/my/home`,
    },
    failed: {
      message: "Malheureusement vous n'avez pas réussi votre examen.",
      url: `#`,
    },
  },
};
var notifMessage;
var condition;
var btnContiner;
var cartIsEmpty;

function setPopup() {
  if (document.getElementById('notifMessage')) {
    const btnContinuer = document.getElementById('btn-inside-popup');
    const textDescription = document.getElementById('notifMessage');

    // condition = document.getElementById('exam_state');

    // cartIsEmpty = document.getElementById('cartIsEmpty');
    // if (cartIsEmpty.value == 'True') {
    //   notifMessage.innerHTML = message['cartIsEmpty'];
    //   btnContiner.addEventListener('click', function () {
    //     document.getElementById('form-1-1').submit();
    //     return false;
    //   });
    //   openPopup();
    //   return;
    // } else

    //console.log(condition.value == 'in_process' && cartIsEmpty.value == 'True');

    // if (condition.value == 'success') {
    //   notifMessage.innerHTML = message['success'];
    //   openPopup();
    //   btnContiner.addEventListener('click', function () {
    //     closePopup();
    //     // window.location.href = '/my/home';
    //   });
    // } else if (condition.value == 'failed') {
    //   notifMessage.innerHTML = message['failed'];
    //   openPopup();

    //   btnContiner.addEventListener('click', function () {
    //     closePopup();
    //   });
    // } else if (condition.value == 'exam_not_passed') {
    //   notifMessage.innerHTML = message['exam_not_passed'];
    //   openPopup();

    //   btnContiner.addEventListener('click', function () {
    //     window.location.href = '/examen-blanc';
    //   });
    // } else return;

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
        } else if (p.ipJotForm != false) {
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

            btnContinuer.setAttribute('href', messageAction.boltExamen.succed.url);
            textDescription.innerHTML = messageAction.boltExamen.succed.message;
            break;
          case 'failed':
            btnContinuer.setAttribute('href', `https://www.lamaisonduchauffeurvtc.fr/`);
            btnContinuer.innerHTML = `\n <button class="rkmd-btn btn-black">voir l'offre</button>`;
            textDescription.innerHTML = `<b>Malheureusement <b/> 🙁, vous avez obtenu une note de ${
              p.note_exam / 5
            }/20 ce qui n'est pas suffisant pour bénéficier de l'offre à 20€ <br/>(note minimum pour bénéficier de l'offre : 8/20).<br/>
Mais nous avons une autre offre pour vous...`;

            break;

          default:
            break;
        }
      }
      openPopup();
    });

    //***************** */
    //***************** */
    //*****************Old process */
    //***************** */
    // if (condition.value == 'in_process' && !(cartIsEmpty.value == 'True')) {
    //   notifMessage.innerHTML = message['in_process'];
    //   btnContiner.addEventListener('click', function () {
    //     closePopup();
    //   });
    //   openPopup();
    // } else if (condition.value == 'success' && !(cartIsEmpty.value == 'True')) {
    //   notifMessage.innerHTML = message['success'];
    //   openPopup();
    //   btnContiner.addEventListener('click', function () {
    //     closePopup();
    //     window.location.href = '/my/home';
    //   });
    // } else if (condition.value == 'failed' && !(cartIsEmpty.value == 'True')) {
    //   notifMessage.innerHTML = message['failed'];
    //   openPopup();

    //   btnContiner.addEventListener('click', function () {
    //     closePopup();
    //   });
    // } else return;
    //***************** */
    //***************** End old process*/
    //***************** */
    //***************** */
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

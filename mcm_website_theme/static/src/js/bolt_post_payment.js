var message = {
  isSignedBolt_registredCAM: `Vos documents sont en cours de vérification, dès qu'ils seront validés, nous vous inscrirons à l'examen VTC auprès de la chambre des métiers.`,
  isSignedBolt_notRegistredCMA: `Félicitation ! Votre inscription est bien validée, nous allons procéder à la vérification de vos documents et votre inscription à l'examen. Vous n'avez plus rien à faire, on s'occupe du reste. 😉 <br/>
Vous aurez accès à la plateforme de formation sous 48h si tous vos documents sont valides. <br/>`,
  not_signed_bolt: '',
  is_signed: '',
  not_signed:
    'Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! \n Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.',
};
var notifMessage;
var isBolt;
var isSigned;

function setPopup() {
  if (document.getElementById('notifMessage')) {
    notifMessage = document.getElementById('notifMessage');
    isBolt = document.getElementById('bolt').value == 'True' ? true : false;
    isSigned = document.getElementById('issigned').value == 'sent' ? false : true;

    console.log('isSigned', isSigned, 'isBolt', isBolt);

    //set button href
    btnContiner = document.getElementById('btn-inside-popup');
    // surveybtn = document.querySelector('.btn');
    // btnContiner.href = surveybtn.href;
    // -----------------------------------------------------------------
    // OLD PROCESS, open calendly onlick continuer and show a vide
    // if (isBolt && isSigned) {
    //   //Test registration to CMA
    //   // if (){

    //   // }
    //   notifMessage.innerHTML = message['is_signed_bolt'];

    //   //set iframe
    //   document.getElementById(
    //     'iframe'
    //   ).innerHTML = `<div class='embed-responsive embed-responsive-16by9'>
    //     <div id='player' class='embed-responsive-item'></div>
    //   </div>`;
    //   //iframe
    //   // 2. This code loads the IFrame Player API code asynchronously.
    //   var tag = document.createElement('script');

    //   tag.src = 'https://www.youtube.com/iframe_api';
    //   var firstScriptTag = document.getElementsByTagName('script')[0];
    //   firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    //   const player = document.getElementById('player');
    //   player.addEventListener('onStateChange', function (state) {
    //     console.log(state);
    //     if (state === 0) {
    //       openCalendly();
    //     }
    //   });
    //   btnContiner.addEventListener('click', function () {
    //     openCalendly();
    //   });
    // } else {
    //   notifMessage.innerHTML = message['not_signed'];
    //   btnContiner.addEventListener('click', function () {
    //     closePopup();
    //   });
    // }
    // -----------------------------------------------------------------
    if (isBolt && isSigned) {
      //Test registration to CMA
      notifMessage.innerHTML = message['isSignedBolt_notRegistredCMA'];
      document.getElementById('btn-inside-popup').style.display = 'none';
      openPopup();
    }
  }

  return;
}

// window.addEventListener('message', receiveMessage, false);
// function receiveMessage(event) {
//   console.log(event);
// }

// function openCalendly() {
//   // stopVideo();
//   // if (document.querySelector('.calendly-badge-content')) {
//   //   document.querySelector('.calendly-badge-content').click();
//   // } else {
//   //   console.log('Problem loading calendly...');
//   // }
// }
function openPopup() {
  //console.log(document.getElementById('popup1'));
  document.getElementById('popup1').style.display = 'flex';
}
function closePopup() {
  //console.log(document.getElementById('popup1'));
  // if (isBolt && isSigned) {
  //   stopVideo();
  // }
  document.getElementById('popup1').style.display = 'none';
}

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;
function onYouTubeIframeAPIReady() {
  player = new YT.Player('player', {
    height: '360',
    width: '640',
    videoId: '-rWX_mjB4VU',
    events: {
      onReady: onPlayerReady,
      onStateChange: onPlayerStateChange,
    },
  });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
  event.target.playVideo();
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;

function onPlayerStateChange(event) {
  // if (event.data == YT.PlayerState.PLAYING && !done) {
  //   setTimeout(stopVideo, 6000);
  //   done = true;
  // }

  if (event.data == YT.PlayerState.ENDED) openCalendly();
}
function stopVideo() {
  // player.stopVideo();
}

document.addEventListener('DOMContentLoaded', function () {
  const partner = partnerInformation();
  partner.then((p) => {
    if (p.evalbox == false) {
      setPopup();
    }
  });

  return;
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

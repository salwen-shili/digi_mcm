const isSignedBolt = `Vous devrez visualiser cette vidéo, pour bien suivre le processus <a target="_blank" href="https://www.examentaxivtc.fr/#!/register" style="color:blue">d'inscription </a>
            à la chambre des métiers et de l'artisanat.`;

var message = {
  is_signed_bolt: isSignedBolt,
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
    isBolt = document.getElementById('bolt').value == 'bolt' ? true : false;
    isSigned =
      document.getElementById('issigned').value == 'sent' ? false : true;

    console.log('isSigned', isSigned, isBolt);

    //set button href
    btnContiner = document.getElementById('btn-inside-popup');
    // surveybtn = document.querySelector('.btn');
    // btnContiner.href = surveybtn.href;
    if (isBolt && isSigned) {
      notifMessage.innerHTML = message['is_signed_bolt'];

      //set iframe
      document.getElementById(
        'iframe'
      ).innerHTML = `<div class='embed-responsive embed-responsive-16by9'>
        <div id='player' class='embed-responsive-item'></div>
      </div>`;
      //iframe
      // 2. This code loads the IFrame Player API code asynchronously.
      var tag = document.createElement('script');

      tag.src = 'https://www.youtube.com/iframe_api';
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
      const player = document.getElementById('player');
      player.addEventListener('onStateChange', function (state) {
        console.log(state);
        if (state === 0) {
          openCalendly();
        }
      });
      btnContiner.addEventListener('click', function () {
        openCalendly();
      });
    } else {
      notifMessage.innerHTML = message['not_signed'];
      btnContiner.addEventListener('click', function () {
        closePopup();
      });
    }
  }

  return;
}

// window.addEventListener('message', receiveMessage, false);
// function receiveMessage(event) {
//   console.log(event);
// }

function openCalendly() {
  stopVideo();
  document.querySelector('.calendly-badge-content').click();
}
function openPopup() {
  //console.log(document.getElementById('popup1'));
  document.getElementById('popup1').style.display = 'flex';
}
function closePopup() {
  //console.log(document.getElementById('popup1'));
  if (isBolt && isSigned) {
    stopVideo();
  }
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
  player.stopVideo();
}

document.addEventListener('DOMContentLoaded', function () {
  setPopup();
  openPopup();

  return;
});

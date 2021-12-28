document.addEventListener('DOMContentLoaded', function () {
  const current = document.getElementById('step_value');
  console.log(current.value);

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
                                            <i class="material-icons right">send</i>continuer</button>
                                    </a>
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

  var step = 1;
  console.log('step', current.value);
  switch (current.value) {
    case 'coordonnées':
      step = 1;

      btnContinuer.setAttribute('href', questionnaireUrl);

      break;
    case 'document':
      step = 2;
      documents.classList.add('active');
      btnContinuer.setAttribute('href', documentsUrl);

      break;
    case 'financement':
      step = 3;
      documents.classList.add('active');
      financement.classList.add('active');

      btnContinuer.setAttribute('href', financementUrl);

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

      finished.innerHTML = finish;

      break;

    default:
      break;
  }
  var progressBarValue = step * 25;
  console.log(step);
  document.getElementsByClassName('progress-bar')[0].style.width =
    progressBarValue + '%';
});

odoo.define('digimoov_website_templates.portal_cpf', function (require) {
  'use strict';

  var publicWidget = require('web.public.widget');
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
  const addUserPlateform = () => {
    window.location.href = '#popup1';
    document.getElementById(
      'popupcontent'
    ).innerHTML = `<div style="text-align: -webkit-center;"><div class="spinner"></div></div>`;
    sendHttpRequest('POST', '/shop/adduser_plateform', {}).then((res) => {
      console.log('res.result.url');

      if (res.result.url) {
        if (res.result.url.includes('https://')) {
          for (let index = 0; index < 200; index++) {
            frame();
          }
          document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px; text-align: center;">                              
                                 ${res.result.ajout}
                                 <br/>
                                </p>
                         <div style="text-align:center">
                            <a onclick='window.open("${res.result.url}");return false;'> <button type="button" class="btn btn-secondary action-button shake" style="padding: 6px 34px;"> Continuer </button></a>
                        </div>     
         `;
        }
      } else {
        if (res.result.ajout) {
          //js-container-animation to animate
          if (res.result.url) {
            document.getElementById('popupcontent').innerHTML = `
                            <p  style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                                <a href="#"> <button type="button" class="btn btn-secondary action-button" onclick="closepopup()"  style="padding: 8px 29px;" > Fermer </button></a>

                            </div>
         `;
          }
          document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                                <a href="#"> <button type="button" class="btn btn-secondary action-button"  onclick="closepopup()" style="padding: 8px 29px;" > Fermer </button></a>
                            </div>
         `;
        }
        if (
          res.result.ajout &&
          res.result.ajout ==
            'Vous avez choisi de préserver votre droit de rétractation sous un délai de 14 jours. Si vous souhaitez renoncer à ce droit et commencer votre formation dés maintenant, veuillez cliquer sur continuer.'
        ) {
          document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                              <button type="button" class="btn btn-secondary action-button" id="non_renonce" style="padding: 7.5px 38.5px;" onclick="closepopup('/my/home')">Attendre 14 jours</button>
                                <button type="button" class="btn btn-secondary action-button shake" style="padding: 7.5px 38.5px;" onclick="renonce()" > Continuer </button>
                            </div>

         `;
        }
      }
    });
  };
  addUserPlateform();

  publicWidget.registry.RequestRenouncee = publicWidget.Widget.extend({
    selector: '.o_portal_my_home',
    events: {
      'change #renonce_request_box': 'check_renounce', // vérifier s'il y a eu un changement de valeur au niveau de checkbox du demande de renonce dans le portal client
    },
    check_renounce: function () {
      var self = this;
      var demande_renonce = false;
      var renonce = document.getElementById('renonce_request_box'); // on recupère la demande de renonce en portal à partir id
      if (renonce) {
        // on teste si on a trouvé le checkbox de la demande de renonce dans le portal client
        if (renonce.checked == true) {
          // on vérifie si le client a cocher la demande de renonce
          demande_renonce = true; // on change le variable demande renonce à vrai pour l'envoyer via url en python pour mettre à jour la fiche de client
        }
      }
      this._rpc({
        route: '/update_renonce', // on prepare un url de mise à jour de la demande de renonce par la suite on va la developpé en python dans controller
        params: {
          demande_renonce: demande_renonce, // on envoi la valeur du demande du renonce comme paramètre avec l'url
        },
      }).then(function () {
        return window.location.reload(); // dés que l'url termine l'éxécution on recharge la page de portal client
      });
    },
  });
});

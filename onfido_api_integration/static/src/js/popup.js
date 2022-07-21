
  
  function setPopup() {
    if (document.getElementById('notifMessage')) {
      const btnContinuer = document.getElementById('btn-inside-popup');
      const textDescription = document.getElementById('notifMessage');
      btnContinuer.innerHTML = `\n <button id="btn-action" class="rkmd-btn btn-black ripple-effect ripple-yellow" type="submit" style="font-size: 11px;width: 145px;" onclick="closePopup()">
                                              Fermer
                                          </button>`;
      textDescription.innerHTML = `Cher(e)s candidat(e)s, nous vous annonçons que l'offre relative à la formation VTC à 20 euros en collaboration avec BOLT a touchée à sa fin. <br>
  Nous clôturons les inscriptions dés aujourd'hui.
  Mais ne soyez pas découragés ! car vous aurez la possibilité d'en profiter de nouveau, lors de la prochaine session de formation prévue pour le 29/09/2022 et dont les inscriptions seront ouvertes sur notre site web à partir du 04/07/2022.`;
  
      openPopup();
      return;
  
    }
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
  

  
  
  //
  
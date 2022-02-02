$(document).ready(function () {
  var validSubmit = {
    phone_valid: false,
  };
    function checkPhone(prop, value) {
    if (value.length > 0) {
      const pattern = /^(07|06)[0-9]\d{7}$/;
      if (value.match(pattern)) return false;
      else
        return `Votre numéro de téléphone doit commencer par 06 ou 07 suivie par 8 chiffres`;
    } else return '';
  }
    $(`#phone`).keyup(function (e) {
    const phone = $('#phone').val();
    const errorMessage = checkPhone('numero de téléphone', phone);
    if (errorMessage === false) {
      validSubmit['phone_valid'] = true;

      if (checkValidationButton(validSubmit)) {
        // buttonInscrire.removeAttribute("disabled");
      }

      $(`#phone_container `).removeClass('error-input-field');
      $(`#phone_helper `).append('');
    } else {
      validSubmit['phone_valid'] = false;
      $(`#phone_container `).addClass('error-input-field');
      $(`#phone_helper span `).text(errorMessage);
    }
  });
});

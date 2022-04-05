$(document).ready(function () {
  const apiCommunes = 'https://geo.api.gouv.fr/communes?codePostal=';

  const format = '&format=json';

  let zipcode = $('#zipcode');

  let voie = $('#voie');
  let typeVoie = $('#voie');
  let nomVoie = $('#nom_voie');
  //test password

  function checkPhone(prop, value) {
    if (value.length > 0) {
      const pattern = /^(07|06)[0-9]\d{7}$/;
      if (value.match(pattern)) return false;
      else
        return `Votre numéro de téléphone doit commencer par 06 ou 07 suivie par 8 chiffres`;
    } else return 'Ce champs est obligatoire!';
  }
  $(`#phone`).keyup(function (e) {
    const phone = $('#phone').val();
    const errorMessage = checkPhone('numero de téléphone', phone);
    if (errorMessage === false) {
      $(`#phone_container `).removeClass('error-input-field');
      $(`#phone_helper `).append('');
    } else {
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#phone_container `).addClass('error-input-field');
      $(`#phone_helper span `).text(errorMessage);
    }
  });

  $(`#password`).keyup(function (e) {
    const password = $('#password').val();
    const errorMessage = checkPassword(password);
    if (errorMessage === false) {
      $(`#password_container `).removeClass('error-input-field');
      $(`#password_helper `).append('');
    } else {
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#password_container `).addClass('error-input-field');
      $(`#password_helper span `).text(errorMessage);
    }
  });

  function checkPassword(value) {
    if (value.length > 0) {
      if (value.length < 8)
        return 'Votre mot de passe doit contenir au minimum 8 caractères';
      else {
        const pattern =
          /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!/+/='":;(){}[|@$ %^&*-]).{8,}$/;
        if (value.match(pattern)) return false;
        else
          return `Votre mot de passe doit contenir une combinaison de chiffres, caractères spéciaux, lettres majuscules et minuscules!`;
      }
    } else return 'Ce champs est obligatoire!';
  }
  //Validate Address

  $(zipcode).on('blur', function () {
    var code = $(this).val();
    //console.log(code);
    let url = apiCommunes + code + format;
    //console.log(url);

    fetch(url, { method: 'get' })
      .then((response) => response.json())
      .then((results) => {
        let city = $('#city') ?? $('#city_reset');
        //console.log(city);
        // console.log(results);
        $(city).find('option').remove();
        if (results.length) {
          //console.log('enter');
          $(`#city_container `).removeClass('error-input-field');
          $(`#city `).removeClass('error-input-field');
          $(`#city_helper `).append('');
          $('#city_container').removeAttr('aria-disabled');
          $(city).removeAttr('disabled');
          $(voie).removeAttr('disabled');
          $(city).focus();
          $(`#city_container `).html(`
          <select class="outlined-text-field disabled" name="city" id="city_reset" type="hidden" required="required">
         
          </select>
                                                <label for="city" style="left: 2rem !important">Ville *
                                                </label>
                                                <i class="material-icons error-icon">error_outline</i>
                                                <div class="helper-text bg-c" id="city_helper">
                                                    <span></span>
                                                </div>
                                                `);
          city = $('#city_reset');

          $.each(results, function (key, value) {
            //console.log(value);
            //console.log(value.nom);
            $(city).removeAttr('disbaled');

            $(city).append(
              '<option value="' + value.nom + '">' + value.nom + '</option>'
            );
            $(`#city_reset ~ label`).animate(
              {
                fontSize: '0.8rem',
                top: '-0.7rem',
                padding: '0.25rem',
              },
              80
            );
          });
        } else {
          if ($(zipcode).val()) {
            $('#city_container').attr(`aria-disabled="true"`);
            $(city).attr(`disbaled="disabled"`);
            $(voie_container).attr(`disbaled="disabled"`);
            $(voie).attr(`disbaled="disabled"`);
            $(`#city_container `).addClass('error-input-field');
            $(`#city `).addClass('error-input-field');
            $(`#city_helper span`).text('Aucune commmune avec ce code postal.');
          } else {
            $(`#city_container `).removeClass('error-input-field');
            $(`#city `).removeClass('error-input-field');
            $(`#city_helper `).append('');
            $('#city_container').removeAttr(`aria-disabled="true"`);
            $(city).removeAttr(`disbaled="disabled"`);
            $(voie_container).removeAttr(`disbaled="disabled"`);
            $(voie).removeAttr(`disbaled="disabled"`);
          }
        }
      })
      .catch((err) => {
        // console.log(err);
        $(city).find('option').remove();
      });
  });

  if (voie.val()) {
    $(`#voie ~ label`).animate(
      {
        fontSize: '0.8rem',
        top: '-0.7rem',
        padding: '0.25rem',
      },
      80
    );
  }
  $('#first_form').submit(function (e) {
    const check = document.querySelector('.error-input-field');
    if (check != null) {
      e.preventDefault();
      return;
    } else {
    }
  });
});

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
    showPasswordPopover();
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
    checkStrength(password);
  });

  function checkPassword(value) {
    if (value.length > 0) {
      if (value.length < 8)
        return 'Votre mot de passe doit contenir au minimum 8 caractères';
      else return false;
      // else {
      //   const pattern =
      //     /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!/+/='":;(){}[|@$ %^&*-]).{8,}$/;
      //   if (value.match(pattern)) return false;
      //   else
      //     return `Votre mot de passe doit contenir une combinaison de chiffres, caractères spéciaux, lettres majuscules et minuscules!`;
      // }
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

let state = false;
let password = document.getElementById('password');
let passwordStrength = document.getElementById('password-strength');
let lowUpperCase = document.querySelector('.low-upper-case i');
let number = document.querySelector('.one-number i');
// let specialChar = document.querySelector('.one-special-char i');
let eightChar = document.querySelector('.eight-character i');
let nivLevel = document.querySelector('.nivLevel');

function checkStrength(password) {
  let strength = 0;

  //If password contains both lower and uppercase characters
  if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) {
    strength += 1;
    lowUpperCase.classList.remove('fa-check');
    lowUpperCase.classList.add('fa-check');
  } else {
    lowUpperCase.classList.add('fa-check');
    lowUpperCase.classList.remove('fa-check');
  }
  //If it has numbers and characters
  if (password.match(/([0-9])/)) {
    strength += 1;

    number.classList.add('fa-check');
  } else {
    number.classList.remove('fa-check');
  }
  //If it has one special character
  // if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) {
  //   strength += 1;

  //   specialChar.classList.add('fa-check');
  // } else {
  //   specialChar.classList.remove('fa-check');
  // }
  //If password is greater than 5
  if (password.length > 7) {
    strength += 1;

    eightChar.classList.add('fa-check');
  } else {
    eightChar.classList.remove('fa-check');
  }

  // If value is less than 2
  if (strength == 0) {
    passwordStrength.classList.remove('progress-bar-warning');
    passwordStrength.classList.remove('progress-bar-success');
    passwordStrength.classList.remove('progress-bar-danger');
    nivLevel.classList.remove('niv-level-1');
    nivLevel.classList.remove('niv-level-2');
    nivLevel.classList.remove('niv-level-3');

    nivLevel.classList.add('niv-level-1');
    nivLevel.innerHTML = 'faible';
  }
  if (strength == 1) {
    passwordStrength.classList.remove('progress-bar-warning');
    passwordStrength.classList.remove('progress-bar-success');
    passwordStrength.classList.add('progress-bar-danger');
    passwordStrength.style = 'width: 25%';
    nivLevel.innerHTML = 'faible';
    nivLevel.classList.add('niv-level-1');
    nivLevel.classList.remove('niv-level-3');
    nivLevel.classList.remove('niv-level-2');
  } else if (strength == 2) {
    passwordStrength.classList.remove('progress-bar-success');
    passwordStrength.classList.remove('progress-bar-danger');
    passwordStrength.classList.add('progress-bar-warning');
    passwordStrength.style = 'width: 55%';
    nivLevel.innerHTML = 'moyenne';
    nivLevel.classList.add('niv-level-2');
    nivLevel.classList.remove('niv-level-1');
    nivLevel.classList.remove('niv-level-3');
  } else if (strength == 3) {
    passwordStrength.classList.remove('progress-bar-warning');
    passwordStrength.classList.remove('progress-bar-danger');
    passwordStrength.classList.add('progress-bar-success');
    passwordStrength.style = 'width: 100%';
    nivLevel.innerHTML = 'optimale';
    nivLevel.classList.add('niv-level-3');
    nivLevel.classList.remove('niv-level-1');
    nivLevel.classList.remove('niv-level-2');
  }
}
//Hide password poover
function hidePasswordPopover() {
  const password = $('#password').val();
  if (password.length > 7) {
    document.getElementById('popover-password').classList.add('hide');
  }
}
function showPasswordPopover() {
  document.getElementById('popover-password').classList.remove('hide');
}

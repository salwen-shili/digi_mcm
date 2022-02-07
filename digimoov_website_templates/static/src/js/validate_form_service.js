function checkLetters(prop, value) {
  if (value.length > 0) {
    const pattern = /^[A-Z,a-z,À-ÿ '-]{2,}$/;
    if (value.match(pattern)) return false;
    else return `Votre ${prop} doit contenir des lettres seulement!`;
  } else return 'Ce champs est obligatoire!';
}
function checkemail(value) {
  if (value.length > 0) {
    const pattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (value.match(pattern)) return false;
    else return `Votre email est incorrecte!`;
  } else return 'Ce champs est obligatoire!';
}
function checkPhone(prop, value) {
  if (value.length > 0) {
    const pattern = /^(07|06)[0-9]\d{7}$/;
    if (value.match(pattern)) return false;
    else
      return `Votre numéro de téléphone doit commencer par 06 ou 07 suivie par 8 chiffres`;
  } else return '';
}

$(document).ready(function () {
  const listId = [
    'contact_lastname',
    'contact_name',
    'phone',
    'address',
    'email_from',
    'objet',
    'message',
    'entreprise',
  ];

  listId.map((id) => {
    if ($(`#${id}`).val()) {
      $(`#${id} ~ label`).animate(
        {
          top: '0',
          fontSize: '12px',
        },
        80
      );
    }
    $(`#${id}`).focusin(function () {
      $(`#${id} ~ label`).animate(
        {
          top: '0',
          fontSize: '12px',
        },
        80
      );
    });
    $(`#${id}`).focusout(function () {
      if ($(this).val() === '') {
        $(`#${id} ~ label`).animate(
          {
            top: '17px',
            fontSize: '16px',
          },
          80
        );
      }
    });
  });

  //Phone number has another format that the validation pattern
  //We created a hidden input to take the value of the disabled phone input so we can submitted
  //Disabled input can not be submitted
  $('#phone_copy').val($('#phone').val());
  $('#phone').change(function () {
    $('#phone_copy').val($('#phone').val());
  });

  $(`#contact_lastname`).keyup(function (e) {
    const contact_lastname = $('#contact_lastname').val();
    const errorMessage = checkLetters('nom', contact_lastname);
    if (errorMessage === false) {
      $(`#contact_lastname_container `).removeClass('error-input-field');
      $(`#contact_lastname_helper `).append('');
    } else {
      $(`#contact_lastname_container `).addClass('error-input-field');
      $(`#contact_lastname_helper span `).text(errorMessage);
    }
  });

  $(`#contact_name`).keyup(function (e) {
    const contact_name = $('#contact_name').val();
    const errorMessage = checkLetters('prenom', contact_name);
    if (errorMessage === false) {
      $(`#contact_name_container `).removeClass('error-input-field');
      $(`#contact_name_helper `).append('');
    } else {
      $(`#contact_name_container `).addClass('error-input-field');
      $(`#contact_name_helper span `).text(errorMessage);
    }
  });
  $(`#email_from`).keyup(function (e) {
    const email_from = $('#email_from').val();
    const errorMessage = checkemail(email_from);
    if (errorMessage === false) {
      $(`#email_from_container `).removeClass('error-input-field');
      $(`#email_from_helper `).append('');
    } else {
      $(`#email_from_container `).addClass('error-input-field');
      $(`#email_from_helper span `).text(errorMessage);
    }
  });

  $(`#phone`).keyup(function (e) {
    const phone = $('#phone').val();
    console.log($('#phone').val());
    const errorMessage = checkPhone('numero de téléphone', phone);
    if (errorMessage === false) {
      $(`#phone_container `).removeClass('error-input-field');
      $(`#phone_helper `).append('');
    } else {
      $(`#phone_container `).addClass('error-input-field');
      $(`#phone_helper span `).text(errorMessage);
    }
  });
});

$('#form-check').submit(function (e) {
  const check = document.querySelector('.error-input-field');
  if (check != null) {
    e.preventDefault();
    return;
  }
});

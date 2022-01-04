$(document).ready(function () {
  //setProgress BAR
  $('.progress-bar').css('width', '25%');
  //
  const apiCommunes = 'https://geo.api.gouv.fr/communes?codePostal=';
  const apiVoie = 'https://api-adresse.data.gouv.fr/search/?q=';
  const format = '&format=json';
  let checked = false;
  let zipcode = $('#zipcode');
  let city = $('#city');
  let voie = $('#voie');
  let typeVoie = $('#voie');
  let nomVoie = $('#nom_voie');
  let introuvable = $('#introuvable');
  $(introuvable).click(function () {
    checked = !checked;
    if (checked) {
      $('#nom_voie_container')
        .html(`<input type="text" name="nom_voie" id="nom_voie" class="outlined-text-field" autocomplete="off" placeholder=" " />
                      <label for="nom_voie">Nom de voie *</label>
                      <i class="material-icons error-icon">error_outline</i>
                      <div class="helper-text bg-c " id="nom_voie_helper">
                        <span></span>
                      </div>`);
      $('#voie_container')
        .html(` <input type="text" id="voie" class="outlined-text-field" autocomplete="off" />
                      <label for="voie">Type de voie *</label>
                      <i class="material-icons error-icon">error_outline</i>
                      <div class="helper-text bg-c " id="voie_helper">
                        <span></span>
                      </div> `);
    }

    const listId = [
      'lastname',
      'firstname',
      'phone',
      'address',
      'email',
      'confirm_email',
      'password',
      'zipcode',
      'city',
      'voie',
      'voie_input',
      'nom_voie',
      'num_voie',
      'comp_address',
    ];
    listId.map((id) => {
      $(`#${id}`).focusin(function () {
        $(`#${id} ~ label`).animate(
          {
            fontSize: '0.8rem',
            top: '-0.7rem',
            padding: '0.25rem',
          },
          80
        );
      });
      $(`#${id}`).focusout(function () {
        if ($(this).val() === '') {
          $(`#${id} ~ label`).animate(
            {
              fontSize: '1rem',
              top: '1rem',
              padding: 0,
            },
            80
          );
        }
      });
    });
  });

  $(zipcode).on('blur', function () {
    var code = $(this).val();
    //console.log(code);
    let url = apiCommunes + code + format;
    //console.log(url);

    fetch(url, { method: 'get' })
      .then((response) => response.json())
      .then((results) => {
        //console.log(results);
        $(city).find('option').remove();
        if (results.length) {
          $(`#city_container `).removeClass('error-input-field');
          $(`#city `).removeClass('error-input-field');
          $(`#city_helper `).append('');
          $('#city_container').removeAttr('aria-disabled');
          $(city).removeAttr('disabled');
          $(voie).removeAttr('disabled');
          $(city).focus();
          $.each(results, function (key, value) {
            //console.log(value);
            //console.log(value.nom);
            $(city).removeAttr('disbaled');

            $(city).append(
              '<option value="' + value.nom + '">' + value.nom + '</option>'
            );
          });
        } else {
          if ($(zipcode).val()) {
            //
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
        //console.log(err);
        $(city).find('option').remove();
      });
  });

  //fetch voie address
  $(typeVoie).on('blur', function () {
    let voieVal = $(this).val();
    //console.log(voieVal);
    // https://api-adresse.data.gouv.fr/search/?q=cour&type=street&postcode=75001
    let url =
      apiVoie +
      voieVal +
      '&type=street&postcode=' +
      zipcode.val() +
      '&city=' +
      city.val();
    //console.log(url);

    fetch(url, { method: 'get' })
      .then((response) => response.json())
      .then((results) => {
        $(nomVoie).find('option').remove();
        const filteredResults = results.features.filter(
          (val) =>
            val.properties.name.split(' ')[0].toUpperCase() ===
            voieVal.toUpperCase()
        );
        //console.log("filter", filteredResults);
        const finalResult = filteredResults.map((v) => {
          var values = v.properties.name.split(' ');

          var subs = values[1]
            ? v.properties.name.substr(v.properties.name.indexOf(' ') + 1)
            : '';
          return subs.charAt(0).toUpperCase() + subs.slice(1) + ` (${voieVal})`;
        });
        //console.log(finalResult, finalResult.length);
        if (finalResult.length) {
          $(`#nom_voie_container `).removeClass('error-input-field');
          $(`#nom_voie `).removeClass('error-input-field');
          $(`#nom_voie_helper `).append('');
          $('#nom_voie_container').removeAttr('aria-disabled');
          $(nom_voie).removeAttr('disabled');
          $(nom_voie).focus();

          //   console.log("finalResult ", finalResult);
          $.each(finalResult, function (key, value) {
            $(nomVoie).append(
              '<option value="' + value + '">' + value + '</option>'
            );
          });
        } else {
          $('#nom_voie_container').attr(`aria-disabled="true"`);
          $('#nom_voie').attr(`disbaled="disabled"`);
          $(`#nom_voie_container `).addClass('error-input-field');
          $(`#nom_voie `).addClass('error-input-field');
          $(`#nom_voie_helper span`).text('Aucun nom de voie avec ce type.');
        }
      })
      .catch((err) => {
        console.log(err);
        $(nomVoie).find('option').remove();
      });
  });
});

$(document).ready(function () {
  //Validate Address

  const apiCommunes = 'https://geo.api.gouv.fr/communes?codePostal=';

  const format = '&format=json';

  let zipcode = $('#zipcode');

  let voie = $('#voie');
  let typeVoie = $('#voie');
  let nomVoie = $('#nom_voie');

  $(zipcode).on('blur', function () {
    var code = $(this).val();
    console.log(code);
    let url = apiCommunes + code + format;
    console.log(url);

    fetch(url, { method: 'get' })
      .then((response) => response.json())
      .then((results) => {
        let city = $('#city') ?? $('#city_reset');
        console.log(city);
        // console.log(results);
        $(city).find('option').remove();
        if (results.length) {
          console.log('enter');
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
            console.log(value);
            console.log(value.nom);
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
  $('#first_form').submit(function (e) {
    const check = document.querySelector('.error-input-field');
    if (check != null) {
      e.preventDefault();
      return;
    } else {
      (function (w, d, t, r, u) {
        var f, n, i;
        (w[u] = w[u] || []),
          (f = function () {
            var o = {
              ti: document.getElementById('microsoft_tracking_key').value,
            };
            (o.q = w[u]), (w[u] = new UET(o)), w[u].push('pageLoad');
          }),
          (n = d.createElement(t)),
          (n.src = r),
          (n.async = 1),
          (n.onload = n.onreadystatechange =
            function () {
              var s = this.readyState;
              (s && s !== 'loaded' && s !== 'complete') ||
                (f(), (n.onload = n.onreadystatechange = null));
            }),
          (i = d.getElementsByTagName(t)[0]),
          i.parentNode.insertBefore(n, i);
      })(window, document, 'script', '//bat.bing.com/bat.js', 'uetq');
      console.log('inside script');
      window.uetq = window.uetq || [];
      window.uetq.push(
        'event',
        "click sur inscription a partir de vous n'avez pas de compte",
        {
          event_category: 'Inscription',
          event_label: 'Inscription',
          event_value: '10',
        }
      );
    }
  });
});

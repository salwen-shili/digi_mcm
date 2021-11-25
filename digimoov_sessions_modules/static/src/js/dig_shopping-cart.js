document.addEventListener('DOMContentLoaded', function () {
  //xmlhttprequest
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
  const sendData = (condition) => {
    sendHttpRequest('POST', '/shop/payment/update_condition', {
      params: {
        condition: condition,
      },
    })
      .then((responseData) => {})
      .catch((err) => {});
  };
  onchangeTextButton1();
  document
    .getElementById('checkbox_conditions')
    .addEventListener('change', function () {
      var condition = document.getElementById('checkbox_conditions').checked;
      var error = document.getElementById('error_conditions');
      var continueBtn = document.getElementById('continueBtn');
      if (condition) {
        continueBtn.removeAttribute('disabled');
        continueBtn.classList.remove('disabled');
        error.style.display = 'none';

        sendData(condition);
      } else {
        continueBtn.setAttribute('disabled', 'disabled');
        continueBtn.classList.add('disabled');
        error.style.display = 'inline-block';
        sendData(condition);
      }
    });
  //end

  document
    .getElementById('cpf_video')
    .setAttribute('src', 'https://www.youtube.com/embed/PN7gVHdT7x4');
});

function onChangeCheckButton() {
  if (document.getElementById('options-date')) {
    if (
      document.getElementById('options-date').value === 'all' ||
      document.getElementById('centre_examen').value === 'all'
    ) {
      document
        .getElementById('pm_shop_checkout')
        .setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout').classList.add('disabled');
      document
        .getElementById('pm_shop_checkout2')
        .setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout2').classList.add('disabled');
    } else if (
      document.getElementById('options-date').value !== 'all' &&
      document.getElementById('centre_examen').value !== 'all'
    ) {
      document.getElementById('pm_shop_checkout').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout').classList.remove('disabled');
      document.getElementById('pm_shop_checkout2').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout2').classList.remove('disabled');
      document.getElementById('error_choix_date').style.display = 'none';
    }
  } else {
    document
      .getElementById('pm_shop_checkout')
      .setAttribute('disabled', 'true');
    document.getElementById('pm_shop_checkout').classList.add('disabled');
    document
      .getElementById('pm_shop_checkout2')
      .setAttribute('disabled', 'true');
    document.getElementById('pm_shop_checkout2').classList.add('disabled');
  }
}
//show popup if date is selected
function showPopup() {
  if (!document.getElementById('options-date')) {
    document.getElementById('error_no_date').style.display = 'inline-block';
    return;
  }
  document.getElementById('error_no_date').style.display = 'none';
  var optionsDate = document.getElementById('options-date').value;
  var cpfChecked = false;
  if (document.getElementById('cpf_pm')) {
    cpfChecked = document.getElementById('cpf_pm').checked;
  }

  var continueBtn = document.getElementById('continueBtn');
  var textbtn;
  cpfChecked
    ? (textbtn = 'Mobiliser mon CPF')
    : (textbtn = 'Passer au paiement');

  if (optionsDate != 'all' && optionsDate != '') {
    document.getElementById('error_choix_date_popup').style.display = 'none';
    continueBtn.innerText = textbtn;
    window.location.href = '#popup1';
  } else {
    document.getElementById('error_choix_date').style.display = 'inline-block';
  }
}

function msTracking(event, event_category, event_label, event_value) {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: '134610618',
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

  window.uetq = window.uetq || [];
  window.uetq.push('event', event, {
    event_category: event_category,
    event_label: event_label,
    event_value: event_value,
  });
}

function verify_payment_method() {
  //user can navigate #popup1 to the url directly so we need to secure
  //that he can't pass if he didn't choose a date
  if (!document.getElementById('options-date')) {
    return (document.getElementById('error_choix_date_popup').style.display =
      'inline-block');
  } else {
    var optionsDate = document.getElementById('options-date').value;

    if (optionsDate == 'all' || optionsDate == '') {
      return (document.getElementById('error_choix_date_popup').style.display =
        'inline-block');
    } else {
      document.getElementById('error_choix_date_popup').style.display = 'none';
    }
  }
  //here we are sure that user has selected the date
  //if condition de vente (checkbox_conditions) is checked - passer ou paiment ou mobiliser mon cpf
  var conditionCheckbox = document.getElementById('checkbox_conditions');
  var error = document.getElementById('error_conditions');
  if (conditionCheckbox.checked == true) {
    error.style.display = 'none';
    condition = true;
  } else {
    error.style.display = 'inline-block';
    condition = false;
  }
  if (condition == false) {
    return;
  }

  stripe_pm = document.getElementById('stripe_pm');
  console.log(stripe_pm, 'stripe_pm');
  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      window.location.href = '/shop/checkout?express=1';
      return;
    }
  }

  if (cpf_pm) {
    console.log(cpf_pm, 'cpf_pm');
    if (cpf_pm.checked == true) {
      if (cpf_pm.value == 'Formation pro') {
        window.location.href = 'https://bit.ly/3nMlm2A';
        msTracking(
          'clic sur mobiliser mon cpf pro',
          'CPF',
          'Inscription CPF pro',
          '680'
        );
        return;
      }
      if (cpf_pm.value == 'Formation premium') {
        window.location.href = 'https://bit.ly/38IxvSa';
        msTracking(
          'clic sur mobiliser mon cpf premium',
          'CPF',
          'Inscription CPF Premium',
          '680'
        );
        return;
      }
      if (
        cpf_pm.value ==
        '[transport-routier] Formation capacité transport routier'
      ) {
        window.location.href = 'www.google.tn';
        msTracking(
          'clic sur mobiliser mon cpf Formation capacité transport routier',
          'CPF',
          'Inscription CPF Formation capacité transport routier',
          '680'
        );
        return;
      }
    }
  }
}

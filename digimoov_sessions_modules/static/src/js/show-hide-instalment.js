document.addEventListener('DOMContentLoaded', function () {
  displayInstalmentPayment();
  document
    .getElementById('checkbox_instalment')
    .addEventListener('click', function () {
      displayInstalmentPayment();
    });
});

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
function showInstalment() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility =
      'unset';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'unset';
    document.getElementById('order_amount_to_pay').style.display = 'revert';
  }
}
function hideInstalment() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility =
      'hidden';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'hidden';
  }
}
function displayInstalmentPayment() {
  if (document.getElementById('order_instalment')) {
    var orderInstalment = document.getElementById('order_instalment');
    orderInstalment.style.visibility = 'unset';
    orderInstalment.style.display = 'revert';
    if (document.getElementById('checkbox_instalment')) {
      var instalment = document.getElementById('checkbox_instalment').checked;
      sendHttpRequest('POST', '/shop/payment/update_amount', {
        params: {
          instalment: instalment,
        },
      })
        .then((responseData) => {
          console.log('send instalment');
        })
        .catch((err) => {});
      if (instalment) {
        showInstalment();
      } else {
        hideInstalment();
      }
    }
  }
}

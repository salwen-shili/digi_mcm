//renonce value
var renonceValue = false;
// popup 1
function openPopup1() {
  document.getElementById('popup1').style.display = 'flex';
}

function closePopup1() {
  document.getElementById('popup1').style.display = 'none';
}

// popup 2 Renonce
function openPopup2() {
  closePopup1();
  console.log('renonceValue:', renonceValue);
  if (renonceValue == 'False') {
    document.getElementById('popup2').style.display = 'flex';
  }
}

function closePopup2() {
  document.getElementById('popup2').style.display = 'none';
  error_conditions.style.display = 'none';
}
function continuebtn() {
  console.log('checkbox_failures.checked', checkbox_failures.checked);
  if (checkbox_failures.checked) {
    document.getElementById('popup2').style.display = 'none';
  } else {
    error_conditions.style.display = 'inline-block';
  }
}

// Popup 3
function openPopup3() {
  closePopup2();
  document.getElementById('popup3').style.display = 'flex';
}

function closePopup3() {
  document.getElementById('popup3').style.display = 'none';
}

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
const renonce = () => {
  var token = window.location.search.split('=')[1];
  console.log('token:', token);
  sendHttpRequest('POST', '/shop/payment/update_failures_not_signed', {
    params: {
      failures: checkbox_failures.checked,
      token: token,
    },
  })
    .then((responseData) => {})
    .catch((err) => {});
};

document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('renonceValue')) {
    renonceValue = document.getElementById('renonceValue').value;
  }
  var isSigned = document.getElementById('issigned').value;
  if (isSigned !== 'sent') {
    console.log(isSigned);
  } else {
    console.log('not signed');
    openPopup1();
  }
});

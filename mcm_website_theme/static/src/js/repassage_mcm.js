document.addEventListener('DOMContentLoaded', function () {
    //get message and url redirection from backend
    var url;
    var message;
    if (document.getElementById('url')) {
      url = document.getElementById('url').value;
    }
  
    if (document.getElementById('message')) {
      message = document.getElementById('message').value;
    }
    //check in case of error to prevent displaying odoo js error
    if (!document.getElementById('echec_examen').value) {
      //change popup to the adequate message
      //setting the url
      document.getElementById('notifMessage').innerHTML = message;
      document.getElementById('btnRepassage').href = url;
    }
    return;
  });
  // to open popup
  function openPopup() {
    document.getElementById('popup1').style.display = 'flex';
  }
    // to close popup
  function closePopup() {
    document.getElementById('popup1').style.display = 'none';
  }
  

  //

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

// const getInfoRepassage = (condition) => {
//   sendHttpRequest("POST", "/shop/payment/update_condition", {
//     params: {
//       condition: condition,
//     },
//   })
//     .then((responseData) => {})
//     .catch((err) => {});
// };

function getRepassageInfo(){
  console.log("get")
}

function onChangeSelect(formation, index){
  console.log(formation, index)
 switch (formation) {
  case "VTC":
    checkVTC();
    break;
  case "TAXI":
    checkTAXI();
  default:
    break;
 }
}

function checkVTC(){

}

function checkTAXI(){
  
}
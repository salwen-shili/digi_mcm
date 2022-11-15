var vtcAccess = null;
var TaxiAccess = null;
var btnRepassage = null;

document.addEventListener('DOMContentLoaded', function () {
  //State
  var vtcAccess = null;
  var TaxiAccess = null;
  btnRepassage = document.getElementById("btn-repassage");



  

  //



// const getInfoRepassage = (condition) => {
//   sendHttpRequest("POST", "/shop/payment/update_condition", {
//     params: {
//       condition: condition,
//     },
//   })
//     .then((responseData) => {})
//     .catch((err) => {});
// };
       // to open popup
     

  });



  
function getRepassageInfo(){
  console.log("get")
}

function openPopup() {
  document.getElementById('popup1').style.display = 'flex';
}
  // to close popup
function closePopup() {
  document.getElementById('popup1').style.display = 'none';
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
  vtcAccess? btnRepassage.classList.remove('hide') : btnRepassage.classList.add('hide')
}

function checkTAXI(){
  TaxiAccess? btnRepassage.classList.remove('hide') : btnRepassage.classList.add('hide')
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



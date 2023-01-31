//required values to check necessary action

//API call to check if the amount to be paid has been paid
var isLourdPaidEmptyCart = false;

getIsLourdPaidEmptyCart();
//End API call to check if the amount to be paid has been paid
var cartIsEmpty = false;

var isSigned = '';

const messages = {
  isSigned:`Félicitations pour votre inscription.`,
  isNotSigned: `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.`,
  emptyCartNoContract: `Votre panier est vide, veuillez cliquer sur continuer pour ajouter votre formation.`,
  isLourdPaid:`Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès!
  Vous pouvez maintenant finaliser votre inscription en cliquant sur continuer.`
};
var contract_uri = '/';
var btnAction;
function setPopup() {



  if (document.getElementById('cartIsEmpty')) {
    cartIsEmpty = document.getElementById('cartIsEmpty');
    //check if value exist
    if (cartIsEmpty) {
      if (document.getElementById('isSigned')) {
        isSigned = document.getElementById('isSigned').value;
      }
      if (document.getElementById('notifMessage')) {
        notifMessage = document.getElementById('notifMessage');
        //set the message
      }
      //contract is signed
      if (isSigned == 'True') {
        openPopup()
    
     
      
            //set description inside popup
            notifMessage.textContent = messages['isSigned'];
            if (document.getElementById('btn-action')) {
              btnAction = document.getElementById('btn-action');
              btnAction.addEventListener('click', function () {
                // contract is signed
                // redirection to my/home
                console.log('redirection...', 'myhome');
                window.location.href = '/my/home';
              });
            }
           
        
    
      } else {
        console.log(document.getElementById('contract_uri').value); //false if no contract
        //contract is not signed
        //get uri to sign contract
        if (document.getElementById('contract_uri').value !== '') {
          if(isLourdPaidEmptyCart){
           
       
          if (document.getElementById('btn-action')) {
            //set notification message to the right description
            notifMessage.textContent = messages['isLourdPaid'];
            btnAction = document.getElementById('btn-action');
            //change button to 'signer mon contrat'
            btnAction.innerText = 'Continuer';
            btnAction.addEventListener('click', function () {
              //redirection to the uri
             
              window.location.href = "https://bit.ly/3k2ueVO";
            });
          }
        }
          else{
            contract_uri =
            document.getElementById('contract_uri').value;
          console.log(contract_uri);
          if (document.getElementById('btn-action')) {
            //set notification message to the right description
            notifMessage.textContent = messages['isNotSigned'];
            btnAction = document.getElementById('btn-action');
            //change button to 'signer mon contrat'
            btnAction.innerText = 'Signer mon contrat';
            btnAction.addEventListener('click', function () {
              //redirection to the uri
              console.log('redirection...', contract_uri);
              window.location.href = contract_uri;
            });
          }
          }
          
        } else if (document.getElementById('btn-action')) {
          //set notification message to the right description
          notifMessage.textContent = messages['emptyCartNoContract'];
          btnAction = document.getElementById('btn-action');
          //change button to 'signer mon contrat'
          btnAction.innerText = 'continuer';
          btnAction.addEventListener('click', function () {
            //redirection to the uri
            console.log('redirection...', `/bolt#pricing`);
            
            window.location.href = `/#pricing`;
          });
        }
      }

      //
    }
  }

  return;
}
//open popup
function openPopup() {
  document.getElementById('popupEmptyCart').style.display = 'flex';
}
//close popup
function closePopup() {
  document.getElementById('popupEmptyCart').style.display = 'none';
  window.location.href = '/my/home';
}


// Wait for the page to load, to set the popup btn action and message description
//
document.addEventListener('DOMContentLoaded', function () {
  setPopup();
  // receive user and user email address
  var user_name = '';
  var user_email = '';
  //check if values are available
  if (document.getElementById('user_name_connected')) {
    user_name = document.getElementById('user_name_connected').value;
  }
  if (document.getElementById('user_email_connected')) {
    user_email = document.getElementById('user_email_connected').value;
  }
  if (document.getElementById('isSigned')) {
    isSigned = document.getElementById('isSigned').value;
  }
  //Actions on signed contract

  //contract is signed
  if (isSigned == 'True') {
    //loggin info
    console.log('isSigned', isSigned);
    console.log('rdvIsBooked', rdvIsBooked);

    if (rdvIsBooked == 'False') {
      //set calendly if rdv is not booked
      setTimeout(function () {
        Calendly.initBadgeWidget({
          url: 'https://calendly.com/mcm-academy/examen-vtc-cma',
          prefill: {
            name: user_name,
            email: user_email,
          },
          text: "Inscription à l'examen VTC",
          color: '#1A1A1A',
          textColor: '#FFFFFF',
        });
      }, 1500);
    }
    openPopup();
  } else {
    //contract is not signed open popup
    if (document.getElementById('contract_uri')) {
      if (document.getElementById('contract_uri')) {
        openPopup();
      }
    }
  }
});


const getIsLourdPaid = () => {
  sendHttpRequestt('POST', '/shop/payment/islourdpaid',
    {
      params: {
      }
    })
    .then((res) => {
      console.log(res, "================================================= >");
      isLourdPaid = res.result.islourdpaid
    })
    .catch((err) => {
      console.log(err);
    });
};

//xmlhttprequest
const sendHttpRequestt = (method, url, data) => {
  const promise = new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);

    xhr.responseType = "json";

    if (data) {
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    }

    xhr.onload = () => {
      if (xhr.status >= 400) {
        reject(xhr.response);
      } else {
        resolve(xhr.response);
      }
    };

    xhr.onerror = () => {
      reject("Something went wrong!");
    };

    xhr.send(JSON.stringify(data));
  });
  return promise;
};
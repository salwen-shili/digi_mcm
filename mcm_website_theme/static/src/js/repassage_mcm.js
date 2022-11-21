// Variables initialisation
var vtcAccess = true;
var taxiAccess = null;
var btnRepassage = null;
var state = null;
var divMessage = null;
var props = {
  'notifMessage': null,
  "btn": null,
  "selectFormation": '',
  "product_id": null,
  "redirection":"null"
};
var divRepassage = ` 
<select onchange="onChangeSelect(this.options[this.selectedIndex].value, this.selectedIndex)" style="
 
padding: 12px 5px;
margin: 0 30px 19px 0;
">
<option selected="selected" disabled="disabled">Selectionner votre formation</option>
<option value="VTC">VTC</option>
<option value="TAXI">TAXI</option>
</select>
<button class="btn-shop hide " onclick="submitForm()" id="btn-repassage"> 
Dés maintenant !                         
</button>
<div id="error-message" class="hide" style="
text-align: -webkit-center;
">
<div class="alert alert-warning" style="
max-width: 49%;
color: #000;
">
Vous n'êtes pas autorisé à accéder à cette rubrique. <a onclick="openPopup()" style="
color: #3c39bd;
font-weight: 600;
text-decoration: underline !important;
cursor: pointer;
">Plus d'informations</a>.
</div>
</div>

`;

document.addEventListener("DOMContentLoaded", function () {
  //State

  state = getInfoRepassage();

  state.then(function (result) {
    // store result
    state = result;

    //Add html when promise is resolved
    document.getElementById("repassage-taxi-vtc").innerHTML = divRepassage;
    //setting state
    props.product_id = document.getElementById("product_id");
    btnRepassage = document.getElementById("btn-repassage");
    // setting access taxi
    taxiAccess = state.response.taxi.access;
    vtcAccess = state.response.vtc.access;
    divMessage = document.getElementById("error-message");
    document.getElementById("update-cart").addEventListener('submit', onSubmitForm);
    // setting popup vars
    props.notifMessage = document.getElementById("notifMessage");
    props.btn = document.getElementById("btn-inside-popup");
    return state;
  });
});

const getInfoRepassage = async (first = false) => {
  let responseData = await sendHttpRequest(
    "POST",
    "/get-datas-user-examen",
    {}
  );
  if (responseData) {
    if (responseData.hasOwnProperty("result")) {
      if (first) {
        
      }
      // console.log(JSON.parse(responseData.result));

      return JSON.parse(responseData.result);
    }
  }

  // catch((err) => {console.log(err)});
};



function onSubmitForm(e) {
 
  e.preventDefault();
  if ( props.product_id.value !="False"){

    window.location.href= props.btn.href
    
  } else {
 
    document.getElementById("update-cart").submit()
  }
  
  
  //redirection auto / manual mode

}

function submitForm(){
  if (document.getElementById("update-cart"))
  document.getElementById("update-cart").submit()
}


// to open popup
function openPopup(moreInfo) {
  document.getElementById("popup1").style.display = "flex";

}
// to close popup
function closePopup() {
  document.getElementById("popup1").style.display = "none";
}
// setPopup action and message
function setPopup(formation) {
  console.log("formation", formation)
  if (formation == "TAXI") {
    props.notifMessage.innerHTML = state.response.taxi.message;
    // setting btn action 
    // add product ID if allowed for submit 
    if (state.response.taxi.echec_examen != "False") {
      props.product_id.value = state.response.taxi.echec_examen
      props.btn.setAttribute('type', 'submit')
      // else just set the href if not allowed 
    } else {
      props.btn.removeAttribute("type")
      props.btn.href = state.response.taxi.url
    }
  } else if (formation == "VTC") {
    props.notifMessage.innerHTML = state.response.vtc.message;
    // setting btn action 
    // add product ID if allowed for submit 
    if (state.response.vtc.echec_examen != "False") {
      props.product_id.value = state.response.vtc.echec_examen
      props.btn.setAttribute('type', 'submit')
      // else just set the href if not allowed 
    } else {
      props.btn.removeAttribute("type")
      props.btn.href = state.response.vtc.url
    }
  }
}

function displayPopupBtn(display) {
  //hide btn
  if (display) {
    props.btn.classList.add("hide");
  }
  else {
    //show btn action
    props.btn.classList.remove("hide")
  }
}


// Select option choix repassage 
function onChangeSelect(formation, index) {
  console.log(formation, index);
  props.selectFormation = formation;
  switch (formation) {
    case "VTC":
      // All actions when selecting VTC
      // show btn 
      if (vtcAccess != "denied") {
        btnRepassage.classList.remove("hide");
        divMessage.classList.add("hide");
        // setup popup with action-btn
        // Hide btn and show error message
      } else {
        btnRepassage.classList.add("hide");
        divMessage.classList.remove("hide");
        // setup popup without action-btn
      }
      setPopup("VTC")
      break;
    case "TAXI":
      // All actions when selecting VTC
      if (taxiAccess != "denied") {
        btnRepassage.classList.remove("hide");
        divMessage.classList.add("hide");
        // setup popup with action-btn
      } else {
        btnRepassage.classList.add("hide");
        divMessage.classList.remove("hide");
        // setup popup without action-btn  
      }
      setPopup("TAXI")
    default:
      break;
  }
}





//xmlhttprequest
const sendHttpRequest = (method, url, data) => {
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

 //Values in "stripe_pm" "cpf_pm" "pole_emploi_pm":
var paymentMethod = 'all';
var urlCpf = false;
let demandeurEmploi = false;
var numeroPoleEmploi = ""
var cpf_pm;


document.onreadystatechange = function () {
  if (document.readyState == "complete") {
    document.getElementById("cover-spin").remove();

    tourguide.start();

  }
}
var villeLourd = [
  "PARIS",
  "NANTES",
  "METZ",
  "LILLE",
  "LYON",
  "TOULOUSE",
  "MARSEILLE",
  "GUADELOUPE",
];
var villeLeger = [
  "PARIS",
  "NANTES",
  "NICE",
  "BORDEAUX",
  "LYON",
  "TOULOUSE",
  "MARSEILLE",
];
// Lourd Reste a charge 
var isLourd = false;
var isLourdPaid = false;

// Need to get if it lourd has been paid 

document.addEventListener("DOMContentLoaded", function () {
  //demandeur emploi

  if (document.getElementById("radio1")){
    
  }

  //
  windowUrl = window.location.href;
  console.log(
    windowUrl,
    windowUrl.includes("formation-pro") ||
      windowUrl.includes("formation-solo") ||
      windowUrl.includes("formation-premium")
  );
  if (windowUrl.includes("lourd")) {
    isLourd = true;
    //API call to check if the amount to be paid has been paid
    getIsLourdPaid();
    
    
    var selectCenter = document.getElementById("centre_examen");
    indexOption = 0;
    Array.from(selectCenter.options).forEach(function (option_element) {
      let option_text = option_element.text;
      index = villeLourd.indexOf(option_text.toUpperCase());
      if (
        index == -1 &&
        option_text.toUpperCase() != "CLIQUEZ ICI"
      ) {
        //remove option
        selectCenter.remove(indexOption);
        indexOption--;
      }
      indexOption++;
    });
  }

  if (
    windowUrl.includes("formation-pro") ||
    windowUrl.includes("formation-solo") ||
    windowUrl.includes("formation-premium") ||
    windowUrl.includes("repassage")
  ) {
    var selectCenter = document.getElementById("centre_examen");
    indexOption = 0;
    Array.from(selectCenter.options).forEach(function (option_element) {
      let option_text = option_element.text;

      index = villeLeger.indexOf(option_text.toUpperCase());
      console.log(option_text, index);
      if (
        index == -1 &&
        option_text.toUpperCase() != "CLIQUEZ ICI"
      ) {
        //remove option
        console.log("delete", indexOption, selectCenter[indexOption]);
        selectCenter.remove(indexOption);
        indexOption--;
      }

      indexOption++;
    });
  }

  displayInstalmentPayment();
  // onchangeTextButton1();
  document
    .getElementById("checkbox_conditions")
    .addEventListener("change", function () {
      var condition = document.getElementById("checkbox_conditions");
      if (condition){
        var condition = condition.checked;
      }
      var error = document.getElementById("error_conditions");
      var continueBtn = document.getElementById("continueBtn");
      if (condition) {
        continueBtn.removeAttribute("disabled");
        continueBtn.classList.remove("disabled");
        error.style.display = "none";

        updateCondition(condition);
      } else {
        continueBtn.setAttribute("disabled", "disabled");
        continueBtn.classList.add("disabled");
        error.style.display = "block";
        updateCondition(condition);
      }
    });
  //end

  // document
  //   .getElementById("cpf_video")
  //   .setAttribute("src", "https://www.youtube.com/embed/PN7gVHdT7x4");

  //event on click on checkbox paiement installment
  var checkboxEvent =  document.getElementById("checkbox_instalment")
  if(checkboxEvent){
checkboxEvent = checkboxEvent.addEventListener("click", function () {
  if (document.getElementById('checkbox_instalment').checked){
    hidePromo();
  }else {showPromo()}
  displayInstalmentPayment();
  
});
  }
  
    
});

//animation
var colors = ["#000000", "#fdd105", "#959595", "#d5a376", "#ff1e00"];
function frame() {
  confetti({
    particleCount: 2,
    angle: 60,
    spread: 55,
    origin: { x: 0 },
    colors: colors,
  });
  confetti({
    particleCount: 2,
    angle: 120,
    spread: 55,
    origin: { x: 1 },
    colors: colors,
  });
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

const updateCondition = (condition) => {
  sendHttpRequest("POST", "/shop/payment/update_condition", {
    params: {
      condition: condition,
    },
  })
    .then((responseData) => {})
    .catch((err) => {});
};

//adduserplateform
const addUserPlateform = () => {
  document.getElementById(
    "popupcontent"
  ).innerHTML = `<div style="text-align: -webkit-center;"><div class="spinner"></div></div>`;
  sendHttpRequest("POST", "/shop/adduser_plateform", {}).then((res) => {
    if (res != undefined) {
      if (res.hasOwnProperty("result")) {
        if (res.result.hasOwnProperty("url")) {
          {
            if (res.result.url.includes("https://")) {
              for (let index = 0; index < 200; index++) {
                frame();
              }
              document.getElementById("popupcontent").innerHTML = `
                                  <p style="margin-top: 12px; text-align: center;">                              
                                       ${res.result.ajout}
                                       <br/>
                                      </p>
                               <div style="text-align:center">
                                  <a onclick='window.open("${res.result.url}");return false;'> <button type="button" class="btn btn-shop shake" style="padding: 6px 34px;"> Continuer </button></a>
                              </div>
                         
             
               `;
            }
          }
        } else {
          if (res.result.hasOwnProperty("ajout")) {
            //js-container-animation to animate
            if (res.result.hasOwnProperty("url")) {
              document.getElementById("popupcontent").innerHTML = `
                                <p style="margin-top: 12px;text-align: justify;">                              
                                     ${res.result.ajout}     
                                </p>
                                <div style="text-align:center">
                                    <a href="#"> <button type="button" class="btn btn-shop-close" onclick="closepopup()"  > Fermer </button></a>
    
                                </div>
             `;
            }
            document.getElementById('popupcontent').innerHTML = `
                                <p style="margin-top: 12px;text-align: justify;">
                                     ${res.result.ajout}
                                </p>
                                <div style="text-align:center">
                                    <a href="#"> <button type="button" class="btn btn-shop-close" onclick="closepopup()"  > Fermer </button></a>
                                </div>
             `;
            if (
              res.result.ajout ==
              "Vous avez choisi de préserver votre droit de rétractation sous un délai de 14 jours. Si vous souhaitez renoncer à ce droit et commencer votre formation dés maintenant, veuillez cliquer sur continuer."
            ) {
              document.getElementById("popupcontent").innerHTML = `
                                  <p style="margin-top: 12px;text-align: justify;">                              
                                       ${res.result.ajout}     
                                  </p>
                                  <div style="text-align:center">
                                      <button type="button" class="btn btn-shop-close" id="non_renonce" style="padding: 7.5px 38.5px;" onclick="closepopup('/my/home')">Attendre 14 jours</button>
                                      <button type="button" class="btn btn-shop shake" style="padding: 7.5px 38.5px;" onclick="renonce()" > Continuer </button>
                                  </div>
               `;
            }
          }
        }
      }
    }
  });

  //                        <div style="text-align:center">
  //                           <a href="${res.result.url}"> <button type="button" class="btn btn-shop-close" onclick="()=>window.location.href=${res.result.url} > Continuer </button></a>
  //                       </div>

  //        `;
  //     } else {
  //       document.getElementById('popupcontent').innerHTML = `
  //                           <p style="margin-top: 12px;    text-align: center;">
  //                                ${res.result.ajout}
  //                               </p>

  //                        <div style="text-align:center">
  //                           <a href="#"> <button type="button" class="btn btn-shop-close" onclick="closepopup()" > Fermer </button></a>
  //                       </div>

  //        `;
  //     }
  //   })

  //   .catch((err) => {
  //     console.log('error addUser', err);
  //   });
};
//cpf accepted
const cpfAccepted = () => {
  sendHttpRequest("POST", "/shop/cpf_accepted", {})
    .then((res) => {
      if (res.result.state) {
        addUserPlateform();
      }
    })
    .catch((err) => {
      console.log(err);
    });
};

function onChangeCheckButton() {
  hideAlertDate();

  if (document.getElementById("options-date")) {
    //No session available
    if (
      document.getElementById("options-date").value === "all" ||
      document.getElementById("centre_examen").value === "all"
    ) {
      // console.log(document.getElementById('options-date'));
     document.getElementById('pm_shop_checkout').classList.add('disabled');

      document.getElementById('pm_shop_checkout2').classList.add('disabled');
    }
    //we have available sessions
    else if (
      document.getElementById("options-date").value !== "all" &&
      document.getElementById("centre_examen").value !== "all"
    ) {
      
      document.getElementById("pm_shop_checkout").classList.remove("disabled");
     
      document.getElementById("pm_shop_checkout2").classList.remove("disabled");
      document.getElementById("error_choix_date").style.display = "none";
      //available session ===> check if we have surpassed 4 months
      // const sel = document.getElementById('options-date');
      // const isAccessible = sessionIsAccessible(sel.options[sel.selectedIndex].text);
      // if (isAccessible) {
      //   disablePaymentButton();
      // }

      // get selected option and show/hide alert for session >4 months
      const sel = document.getElementById("options-date");

      sessionIsAccessible({
        session: sel.options[sel.selectedIndex].getAttribute("data"),
        id: sel.options[sel.selectedIndex].getAttribute("id"),
      });
    }
  } else {
   
    document.getElementById("pm_shop_checkout").classList.add("disabled");
 
    document.getElementById("pm_shop_checkout2").classList.add("disabled");
  }
}

//show popup if date is selected
function showPopup() {
  if (document.getElementById("input-pole-emploie")){
    numeroPoleEmploi = document.getElementById("input-pole-emploie").value
  }
//demandeur d'emploi
if (isDemandeurEmploiReplied()){
  hideDemandeurEmploiQuestionError()
  if (demandeurEmploi){
    if (isNumeroEmploieEmpty() == true){
     return showDemandeurEmploiNumeroError()
    }else{
      if (!verifyNumEmploi(numeroPoleEmploi)) {
        hideDemandeurEmploiNumeroError();
        return showWithId("num_emploi_helper")
      }
      hideWithId("num_emploi_helper")
      hideDemandeurEmploiNumeroError()
      
    }
    
    
  }
}else{
  hideDemandeurEmploiNumeroError()
  hideWithId("num_emploi_helper")
  return showDemandeurEmploiQuestionError()
  
}

sendDemandeurEmploi(numeroPoleEmploi,demandeurEmploi)


//End //demandeur d'emploi



    let optionsDate = document.getElementById('options-date');
    if (optionsDate != null){
      optionsDate=optionsDate.value
    }
  let cpfChecked = false;

  

  if (document.getElementById("centre_examen")) {
    let region = document.getElementById("centre_examen").value
    if (region != 'all') {
      document.getElementById('error_choix_centre_examen').style.display = 'none';
      
    } else {
      document.getElementById('error_choix_centre_examen').style.display = 'block';
      scrollToError();
      return
    }

  }

  
  if (optionsDate != 'all' && optionsDate != '') {
    document.getElementById('error_choix_date_popup').style.display = 'none';

  } else {
    document.getElementById('error_choix_date').style.display = 'block';
    scrollToError();
    return
  }

  if (!document.getElementById("options-date")) {
    document.getElementById('error_no_date').style.display = 'block';
    scrollState = true;
    scrollToError()
    return;
  }
  if (!['pole_emploi_pm', 'stripe_pm', 'cpf_pm'].includes(paymentMethod)) {
    document.getElementById('error_no_method').style.display = 'block';
    scrollState = true;
    scrollToError()
    return;
  }
  hideError_no_method()

  document.getElementById("error_no_date").style.display = "none";



  if (document.getElementById('cpf_pm')) {
    cpfChecked = paymentMethod == "cpf_pm" ? true : false;
  }
  var continueBtn = document.getElementById("continueBtn");
  var textbtn;

  var polechecked = false;
  if (document.getElementById('pole_emploi_pm')) {
    polechecked = paymentMethod == "pole_emploi_pm" ? true : false;

  }
  // change btn text inside popup
  cpfChecked || polechecked
    ? (isLourd ? textbtn="Je paye maintenant !" : textbtn = "Mobiliser mon CPF")
    : (textbtn = "Je paye maintenant !");
  if (isLourdPaid){
    textbtn = "Mobiliser mon CPF"
  }
  if (optionsDate != "all" && optionsDate != "") {
    if (document.getElementById("error_choix_date_popup")) {
      document.getElementById("error_choix_date_popup").style.display = "none";
    }

    continueBtn.innerText = textbtn;
    window.location.href = "#popup1";
  } else {
    if (document.getElementById("error_choix_date")) {
      document.getElementById("error_choix_date").style.display =
        "block";
    }
  }

  //transport lourd
  if ((window.location.href.includes("lourd") && cpfChecked) || polechecked) {
    //send islourd and payment method
    isLourdnPayment(isLourd,paymentMethod)
    if (document.getElementById("input_lourd"))
    // Si formation : Lourd 
    // Voir si reste a charge est paye 
    // Si oui masquer le reste a charge dans le le popup
    console.log("============================================== islourdpaid:", isLourdPaid)
    if (isLourdPaid){
      document.getElementById("input_lourd").style.display = "none";
    }else{
      document.getElementById("input_lourd").style.display = "block";
    } 
  }

}

function verify_payment_method() {

  //user can navigate #popup1 to the url directly so we need to secure
  //that he can't pass if he didn't choose a date
  if (!document.getElementById("options-date")) {
    return (document.getElementById("error_choix_date_popup").style.display =
      "block");
  } else {
    var optionsDate = document.getElementById("options-date").value;

    if (optionsDate == "all" || optionsDate == "") {
      return (document.getElementById("error_choix_date_popup").style.display =
        "block");
    } else {
      if (document.getElementById("error_choix_date_popup")) {
        document.getElementById("error_choix_date_popup").style.display =
          "none";
      }
    }
  }
  //here we are sure that user has selected the date
  //if condition de vente (checkbox_conditions) is checked - passer ou paiment ou mobiliser mon cpf
  var conditionCheckbox;
  var conditionlourd;
  var error;
  if (document.getElementById("checkbox_conditions")) {
    conditionCheckbox = document.getElementById("checkbox_conditions");
    error = document.getElementById("error_conditions");
    if (conditionCheckbox.checked == true) {
      error.style.display = "none";
      condition = true;
    } else {
      error.style.display = "block";
      condition = false;
    }
    if (condition == false) {
      return;
    }
  }
  if (document.getElementById("input_lourd")) {
    conditionlourd = document.getElementById("checkbox_lourd");
  }

  //redirection stripe
  var stripe_pm = document.getElementById('stripe_pm');
  // console.log(stripe_pm, 'stripe_pm');
  if (stripe_pm) {
    if (paymentMethod == "stripe_pm") {
      window.location.href = "/shop/checkout?express=1";
      return;
    }
  }
  pole_emploi_pm = document.getElementById('pole_emploi_pm') ?? false;
    var cpf_pm = document.getElementById('cpf_pm');

  // var state = 'accepted';
  var state = document.getElementById("state").value;


  if (cpf_pm) {
    // console.log(cpf_pm, 'cpf_pm');
   var emploichecked = paymentMethod == "pole_emploi_pm" ? true : false;
   if (paymentMethod == "cpf_pm" || emploichecked == true) {
      if (cpf_pm.value == "Formation pro") {
        switch (true) {
          case state.includes("https://www.moncompteformation.gouv.fr/"):
            window.open(state, "_blank");
            break;
          case state == "accepted":
            cpfAccepted();

            // document.getElementById('popupcontent').innerHTML = 'finished...';
            break;

          default:
            if (urlCpf)
          window.open(urlCpf, "_blank");
          else{
            window.open("https://bit.ly/3uLde9W", "_blank");
  
          }

            break;
        }
        return;
      }
      if (cpf_pm.value == "Formation premium") {
        switch (true) {
          case state.includes("https://www.moncompteformation.gouv.fr/"):
            
            window.open(state, "_blank");
            break;
          case state == "accepted":
           
            
            cpfAccepted();
            break;

          default:
            
          if (urlCpf)
          window.open(urlCpf, "_blank");
          else{
            window.open("https://bit.ly/3LJQLQP", "_blank");
  
          }

            break;
        }
        return;
      }
      if (
        cpf_pm.value.includes(
          "Formation attestation de transport poids lourd"
        ) &&
        conditionlourd.checked == true
      ) {
        if (!urlCpf){
          urlCpf="https://bit.ly/3k2ueVO"
        }
    

        // Open /payment => Reste a charge 
        // window.open("https://bit.ly/3k2ueVO", "_blank");
       
        // Si le rete a charge est paye, redirection vers cpf
        if (isLourdPaid){
          window.open(urlCpf, "_blank");
        }else {
          window.location.href = "/shop/checkout?express=1";
        }
    }
  }
}
}

function hideError_no_method() {
  if (document.getElementById('error_no_method').style.display == 'block') document.getElementById('error_no_method').style.display = 'none';

}
function scrollToError() {
  if (document.getElementById('options-date'))
    document.getElementById('options-date').scrollIntoView({ behavior: 'smooth', block: 'center' });
}



function closepopup(msg) {
  if (msg) {
    window.location.href = msg;
    return;
  }
  let lourd = ""
  if (window.location.href.includes("lourd")){
    lourd = `   <div class="input checkbox" id="input_lourd" style="display:none;margin-top: 12px;">
    <input type="checkbox" id="checkbox_lourd" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.conditions" t-att-value="website_sale_order.conditions">
        <label for="conditions" style="display:inline">
            Je m'engage à régler le montant de reste à charge de
            <b>200€</b>
            une fois mon financement CPF de
            <b>2000€</b>
            accepté
        </label>
    </input>
  
  </div>`
  }
  document.getElementById("popupcontent").innerHTML = `
  <p id="notifMessage">
                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que DIGIMOOV procédera à l'exécution immédiate de ma formation en ligne et à ce titre, je
                            renonce expressément à exercer mon droit de rétractation conformément aux dispositions de
                            l'article L.221-28 1° du code de la consommation.
                                    </label>
                                </input>
                            </div>
                           ${lourd}
                            <div class="input checkbox" style="margin-top: 12px;">
                                <input type="checkbox" id="checkbox_conditions" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.conditions" t-att-value="website_sale_order.conditions">
                                    <label for="conditions" style="display:inline">
                                        J'ai lu et j'accepte les
                                        <a href="/conditions" target="blank" style="font-weight: 600; color: #000;">
                                            conditions générales de vente
                                        </a>
                                    </label>
                                </input>
                            </div>
                            <p id="error_conditions" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez acceptez les conditions générales de ventes
                            </p>

                            <p id="error_choix_date_popup" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez fermer cette fenêtre et selectionner votre date d'examen
                            </p>
                        </p>
                        <style>
                            .action-button {
                            height: 40px;
                            width: 185px;
                            font-size: 15px;
                            background-color: #152856;
                            border: 1px solid hsl(240, 44%, 28%);
                            color: #ffffff;
                            font-weight: 600;
                            border-radius: 5px;
                            box-shadow: 0 2px 4px 0 rgba(87, 71, 81, 0.2);
                            cursor: pointer;
                            transition: all 2s ease-out;
                            transition: all 0.2s ease-out;
                            }
                            .action-button:hover,
                            .action-button:focus {
                            background-color: #ffffff;
                            border: 1px solid hsl(240, 44%, 28%);
                            color: #000000;
                            transition: all 0.2s ease-out;
                            }

                        </style>
                        

                        <div style="text-align:center">
                        <a href="#">  
                        <button type="button" class="btn btn-shop-close" id="Précédent"  >Fermer</button>
                        </a>
                            <button type="button" class="btn btn-shop shake" id="continueBtn" onclick="verify_payment_method()">Continuer</button>
                        </div>`;
}

function renonce() {
  document.getElementById("popupcontent").innerHTML = `
                                                     
                                 <p id="notifMessage">

                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que DIGIMOOV
                                        procédera à l'exécution immédiate de ma formation en ligne et à ce titre, je
                            renonce expressément à exercer mon droit de rétractation conformément aux dispositions de
                            l'article L.221-28 1° du code de la consommation.
                                    </label>
                                </input>
                            </div>
                            
                            <p id="error_conditions" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez acceptez les conditions générales de ventes
                            </p>

                            <p id="error_choix_date_popup" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez fermer cette fenêtre et selectionner votre date d'examen
                            </p>
                        </p> 
                       
                          
                            <div style="text-align:center">
                             <button type="button" class="btn btn-shop-close" id="Précédent"   onclick="cpfAccepted()">Précédent</button>
                             <button type="button" class="btn btn-shop shake" id="continueBtn" onclick="verify_payment_method()">Continuer</button>
                          </div>
         `;
}

// Création d'une fonction showpoleemploidetails pour afficher les détails de pole emploi et hidepoleemploidetails pour masquer les détails pole emploi.
// Création d'une fonction sendpoleemploistate qui récupère l'état de radio button et envoyer cet état au backend avec un post request vers /shop/cart/update_pole_emploi  (checked : true ou false)
// Cette méthode est utilise à chaque clic d'un radio button
const sendPoleEmploiState = (pole_emploi_state) => {
  sendHttpRequest("POST", "/shop/cart/update_pole_emploi", {
    params: {
      pole_emploi_state: pole_emploi_state,
    },
  })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

//hide pole emploie details
function hidePoleEmploiDetails() {
  if (document.getElementById("pole-emploi-details")) {
    document.getElementById("pole-emploi-details").classList.add("hide");
   
  }
}
//show pole emploie details
function showPoleEmploiDetails() {
  if (document.getElementById("pole-emploi-details")) {
    document.getElementById("pole-emploi-details").classList.remove("hide");
    if (document.getElementById("arrow-down-pole-emploi")) {
      document
        .getElementById("arrow-down-pole-emploi")
        .classList.remove("hide");
    }
  }
}

//hide pole emploie details
function hideCpfDetails() {
  if (document.getElementById("cpf-details")) {
    document.getElementById("cpf-details").classList.add("hide");
    
  }
}
//show pole emploie details
function showCpfDetails() {
  if (document.getElementById("cpf-details")) {
    document.getElementById("cpf-details").classList.remove("hide");
    if (document.getElementById("arrow-down")) {
      document.getElementById("arrow-down").classList.remove("hide");
    }
  }
}

//on click cpf / carte bleu
function onchangeTextButton() {
  //hide cpf details when pole_emploi is checked

  if (document.getElementById('pole_emploi_pm')) {
    if (paymentMethod == "pole_emploi_pm") {
      //send pole emploi checked = true
      //hide cpf details
      poleEmploieFixDisplay();
      sendPoleEmploiState(paymentMethod == "pole_emploi_pm");
      
    }  else if (paymentMethod == "cpf_pm") {
      //show cpf
      showCpfDetails();
      //hide poleEmploi details
      hidePoleEmploiDetails();

      //send pole emploi checked
      sendPoleEmploiState(paymentMethod == "pole_emploi_pm");
    } else {
      //show cpf
      hideCpfDetails;
      //hide poleEmploi details
      hidePoleEmploiDetails();

      //send pole emploi checked
      sendPoleEmploiState(paymentMethod == "pole_emploi_pm");
    }
  }
  var stripe_pm = document.getElementById("stripe_pm");
  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      document.getElementById("pm_shop_check").href =
        "/shop/checkout?express=1";

      document.getElementById("pm_shop_checkout").href =
        "/shop/checkout?express=1";
    }
  }
  if (cpf_pm) {
    // console.log(cpf_pm, 'cpf_pm');
   var emploichecked = paymentMethod == "pole_emploi_pm" ? true : false;
   if (paymentMethod == "cpf_pm" || emploichecked == true) {


      if (document.getElementById("pm_shop_checkout2")) {
        document.getElementById("pm_shop_checkout2").innerText =
          "Mobiliser mon CPF";
      }
      if (document.getElementById("pm_shop_checkout")) {
        document.getElementById("pm_shop_checkout").innerText =
          "Mobiliser mon CPF";
      }
      if (cpf_pm.value == "Formation pro") {
        document.getElementById("pm_shop_check").href =
          "https://bit.ly/3uLde9W";
        document.getElementById("pm_shop_checkout").href =
          "https://bit.ly/3uLde9W";
      }
      if (cpf_pm.value == "Formation premium") {
        document.getElementById("pm_shop_check").href =
          "https://bit.ly/3LJQLQP";
        document.getElementById("pm_shop_checkout").href =
          "https://bit.ly/3LJQLQP";
      }
      // if (document.getElementById('promo_code')) {
      //   document.getElementById('promo_code').style.display = 'none';
      // }
      // if (document.getElementById('promo_button')) {
      //   document.getElementById('promo_button').style.display = 'none';
      // }
      // if (document.getElementById('promo_input')) {
      //   document.getElementById('promo_input').style.display = 'none';
      // }
      // if (document.getElementById('order_instalment')) {
      //   document.getElementById('order_instalment').style.display = 'none';
      //   document.getElementById('order_instalment_number').style.display =
      //     'none';
      //   document.getElementById('order_amount_to_pay').style.display = 'none';
      // }

      // hide instalment

      displayInstalmentPayment(); //hide instalment
      displayPromo(); //hide promo

      if (document.getElementById("order_instalment")) {
        document.getElementById("order_instalment").style.display = "none"; //hide instalment
        document.getElementById("order_instalment_number").style.display =
          "none";
      }
      if (document.getElementById("order_amount_to_pay")) {
        document.getElementById("order_amount_to_pay").style.display = "none";
      }
    }
  }

  if (document.getElementById("pm_shop_text")) {
    //Show CPF video and details
    document.getElementById("cpf-details").classList.remove("hide");
    document.getElementById("arrow-down").classList.remove("hide");

    document.getElementById("pm_shop_text").innerHTML = "Mobiliser mon CPF";
    document.getElementById("pm_shop_check_text").innerHTML =
      "Mobiliser mon CPF";
    document.getElementById("pm_shop_checkout_text").innerHTML =
      "Mobiliser mon CPF";
  }
}

function onchangeTextButton1() {
  //hide cpf details when pole_emploi is checked
  hideAlertDate();
  if (document.getElementById("pole_emploi_checkbox")) {
    //hide poleEmploi details

    sendPoleEmploiState(paymentMethod == "pole_emploi_pm");
    //send pole emploi checked
    hidePoleEmploiDetails();
  }

  if (document.getElementById("pm_shop_checkout")) {
    document.getElementById("pm_shop_checkout").innerText =
      "Je paye maintenant !";
  }
  if (document.getElementById("pm_shop_checkout2")) {
    document.getElementById("pm_shop_checkout2").innerText =
      "Je paye maintenant !";
  }
  if (document.getElementById("cpf-details")) {
    document.getElementById("cpf-details").classList.add("hide");
    if (document.getElementById("arrow-down")) {
      document.getElementById("arrow-down").classList.add("hide");
    }
  }
  // //show hide instalment
  displayInstalmentPayment(); //show instalment
  displayPromo(); //show promo
  // if (document.getElementById('promo_code')) {
  //   document.getElementById('promo_code').style.display = 'inline';
  // }
  // if (document.getElementById('promo_button')) {
  //   document.getElementById('promo_button').style.display = 'inline';
  // }

  // if (document.getElementById('promo_input')) {
  //   document.getElementById('promo_input').style.display = 'inline';
  // }
  // if (document.getElementById('order_instalment')) {
  //   document.getElementById('order_instalment').style.display = 'revert';
  //   document.getElementById('order_instalment_number').style.display = 'revert';
  //   document.getElementById('order_amount_to_pay').style.display = 'revert';
  //   document.getElementById('order_instalment').style.visibility = 'unset';
  //   document.getElementById('order_instalment_number').style.visibility =
  //     'unset';
  //   document.getElementById('order_amount_to_pay').style.visibility = 'unset';
  // }

  var stripe_pm = document.getElementById("stripe_pm");
  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      document.getElementById("pm_shop_check").href =
        "/shop/checkout?express=1";

      document.getElementById("pm_shop_checkout").href =
        "/shop/checkout?express=1";
    }
  }

  if (document.getElementById("pm_shop_text")) {
    if (document.getElementById("cpf-details")) {
      document.getElementById("cpf-details").classList.add("hide");
      document.getElementById("arrow-down").classList.add("hide");
      if (document.getElementById("pm_shop_checkout")) {
        document.getElementById("pm_shop_checkout").innerHTML =
          "Je paye maintenant !";
      }
      if (document.getElementById("pm_shop_checkout2")) {
        document.getElementById("pm_shop_checkout2").innerText =
          "Je paye maintenant !";
      }
    }

    // if (document.getElementById('promo_code')) {
    //   document.getElementById('promo_code').style.display = 'inline';
    // } else {
    //   document.getElementById('promo_input').style.display = 'inline';
    //   document.getElementById('promo_button').style.display = 'inline';
    // }
    // if (document.getElementById('order_instalment')) {
    //   document.getElementById('order_instalment').style.display = 'visible';
    // }
    // instalment = document.getElementById('checkbox_instalment');
    // if (instalment) {
    //   if (instalment.checked == true) {
    //     document.getElementById('order_instalment_number').style.display =
    //       'visible';
    //     document.getElementById('order_amount_to_pay').style.display =
    //       'visible';
    //   }
    // }
  }
}
function show_coupon() {
  if (document.getElementById("promo_input")) {
    document.getElementById("promo_input").style.display = "inline";
  }
  if (document.getElementById("promo_button")) {
    document.getElementById("promo_button").style.display = "inline";
  }
}

// display promo - instalment

function showInstalment() {
  if (document.getElementById("order_instalment_number")) {
    document.getElementById("order_instalment_number").style.visibility =
      "unset";
  }
  if (document.getElementById("order_amount_to_pay")) {
    document.getElementById("order_amount_to_pay").style.visibility = "unset";
    document.getElementById("order_amount_to_pay").style.display = "revert";
  }
}

function hideInstalment() {
  if (document.getElementById("order_instalment_number")) {
    document.getElementById("order_instalment_number").style.visibility =
      "hidden";
  }
  if (document.getElementById("order_amount_to_pay")) {
    document.getElementById("order_amount_to_pay").style.visibility = "hidden";
  }
}

function displayInstalmentPayment() {
   if (document.getElementById('order_instalment')) {
    var orderInstalment = document.getElementById('order_instalment');
    orderInstalment.style.visibility = 'unset';
    orderInstalment.style.display = 'revert';
    if (document.getElementById('checkbox_instalment')) {
      var instalment = document.getElementById('checkbox_instalment').checked;
      selectPaymentInstallmentOption(instalment)
      
      if (instalment) {
        showInstalment();
        sendHttpRequest('POST', '/shop/payment/update_amount', {
          params: {
            instalment: true,
          },
        })
          .then((responseData) => { })
          .catch((err) => { });
      } else {
        hideInstalment();
        sendHttpRequest('POST', '/shop/payment/update_amount', {
          params: {
            instalment: false,
          },
        })
          .then((responseData) => { })
          .catch((err) => { });
      }
    }
  }
}
function selectPaymentInstallmentOption(instalment) {

  let select
  if (document.getElementById("financement")) {
    select = document.getElementById("financement");

  } else {
    return
  }
  index = document.getElementById("financement").selectedIndex
  if ([1, 2].indexOf(index) != -1) {
    if (instalment) {
      select.options[2].selected = 'selected'
     

    } else {
      select.options[1].selected = 'selected'
      
    }
  }
}

function displayPromo() {
  if (document.getElementById('stripe_pm')) {
    if (paymentMethod == "stripe_pm") {
      showPromo();
    } else {
      hidePromo();
    }
  }
}
function showPromo() {
  if (document.getElementById("promo_code")) {
    //when promo button is shown we don't need to show promo_code
    if (document.getElementById("promo_button")) {
      if (document.getElementById("promo_button").style.display != "none") {
        // document.getElementById('promo_code').style.display = 'none';
      } else {
        document.getElementById("promo_code").style.display = "unset";
      }
    }
  }
  if (document.getElementById("promo_button")) {
    document.getElementById("promo_button").style.display = "inline";
  }

  if (document.getElementById("promo_input")) {
    document.getElementById("promo_input").style.display = "inline";
  }
}

function hidePromo() {
  if (document.getElementById("promo_code")) {
    document.getElementById("promo_code").style.display = "none";
  }
  if (document.getElementById("promo_button")) {
    document.getElementById("promo_button").style.display = "none";
  }
  if (document.getElementById("promo_input")) {
    document.getElementById("promo_input").style.display = "none";
  }
}

//Disable both payment buttons
function disablePaymentButton() {
  document.getElementById("pm_shop_checkout").setAttribute("disabled", "true");
  document.getElementById("pm_shop_checkout").classList.add("disabled");
  document.getElementById("pm_shop_checkout2").setAttribute("disabled", "true");
  document.getElementById("pm_shop_checkout2").classList.add("disabled");
}
//Enable both payment buttons
function enablePaymentButton() {
  document.getElementById("pm_shop_checkout").removeAttribute("disabled");
  document.getElementById("pm_shop_checkout").classList.remove("disabled");
  document
    .getElementById("pm_shop_checkout2")
    .removeAttribute("disabled");
  document.getElementById("pm_shop_checkout2").classList.remove("disabled");
}

// show a warning message for session > 4 months
function showAlertDate() {
  if (document.getElementById("error_choix_date_4"))
    document.getElementById("error_choix_date_4").style.display =
      "block";
}
// hide the warning message for session > 4 months
function hideAlertDate() {
  if (document.getElementById("error_choix_date_4"))
    document.getElementById("error_choix_date_4").style.display = "none";
}

// This function substract 4 months from date session,
function sessionIsAccessible(prop) {
  hideAlertDate();

  // alert(new Date(prop));
  const toDay = new Date();
  const sessionDate = new Date(prop.session);
  console.log("sessionDate :", sessionDate);
  const months = monthDiff(toDay, sessionDate);

  //init
  let isAccessible = false;
  //if months == 4 check toDay's day is superior to session's day
  //wass commented && toDay.getFullYear() == sessionDate.getFullYear() 
  if (months == 4 ) {
    console.log(
      sessionDate.getDate(),
      toDay.getDate(),
      sessionDate.getDate() - toDay.getDate() <= 0
    );
    sessionDate.getDate() - toDay.getDate() <= 0
      ? (isAccessible = true)
      : (isAccessible = false);
  } else if (months < 4) {
    isAccessible = true;
  }
  console.log("=========================================", sessionDate);
  // if (sessionDate != 'all') {
  //   updateExamDate({
  //     exam_date_id: prop.id,
  //     status: isAccessible,
  //     availableDate: availableDate(sessionDate),
  //   });
  // }
  if (window.location.href.includes("lourd")) {
    isAccessible = true;
  }
  // console.log('isAccessible :', isAccessible);
  if (!isAccessible) {
    showAlertDate();
    disablePaymentButton();
    setAvailableDate(sessionDate);
    updateExamDate({
      exam_date_id: prop.id,
      status: isAccessible,
      availableDate: availableDate(sessionDate),
    });
  } else {
    hideAlertDate();
    //send exam date (session and write into client file)

    updateExamDate({
      exam_date_id: prop.id,
      status: isAccessible,
      availableDate: availableDate(sessionDate),
    });
    return;
  }
}
// Substract 2 dates and get months
function monthDiff(d1, d2) {
  var months;
  months = (d2.getFullYear() - d1.getFullYear()) * 12;
  months -= d1.getMonth();
  months += d2.getMonth();

  return months;
}

function formatDateEN(date) {
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  });
}

function formatDateFR(date) {
  return date.toLocaleString("fr-FR", {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  });
}

function availableDate(sessionDate) {
  const futureDate = new Date(sessionDate);
  const month = futureDate.getMonth();
  futureDate.setMonth(futureDate.getMonth() - 4);
  while (futureDate.getMonth() === month) {
    futureDate.setDate(futureDate.getDate() - 1);
  }

  return formatDateFR(futureDate);
}
// set available date input and return it
function setAvailableDate(sessionDate) {
  if (document.getElementById("available-date")) {
    document.getElementById("available-date").innerHTML =
      availableDate(sessionDate);
  } else return;
}

//post request to /shop/cart/update_exam_date
const updateExamDate = (props) => {
  sendHttpRequest("POST", "/shop/cart/update_exam_date", {
    params: {
      exam_date_id: props.exam_date_id,
      status: props.status,
      availableDate: props.availableDate,
    },
  })
    .then((responseData) => {
    if (responseData.hasOwnProperty("result")){
      if (responseData.result.hasOwnProperty("url_cpf")){
        urlCpf = responseData.result.url_cpf ?? false;
      }
      console.log("Url cpf: ", urlCpf)
      
    }
   
  })
    .catch((err) => {});
};

//Show departement only for taxi 
function showDepartement(){
 
  return
  
}

// fix display whene selecting pole emploi or cpf 
// paiement en plusieur fois 
// code promo 
function fixDisplay() {


  if (document.getElementById('promo_code')) {
    document.getElementById('promo_code').style.display = 'none';
  }
  if (document.getElementById('promo_button')) {
    document.getElementById('promo_button').style.display = 'none';
  }
  if (document.getElementById('promo_input')) {
    document.getElementById('promo_input').style.display = 'none';
  }
  if (document.getElementById('order_instalment')) {
    document.getElementById('order_instalment').style.display = 'none';
    document.getElementById('order_instalment_number').style.visibility =
      'hidden';
    if (document.getElementById('order_instalment_number_order')) {
      document.getElementById('order_instalment_number_order').style.visibility =
        'hidden';
    }
    document.getElementById('order_amount_to_pay').style.display = 'none';
    if (document.getElementById('order_amount_to_pay_amount')) {
      document.getElementById('order_amount_to_pay_amount').style.display =
        'none';
    }

  }
}


//Base function mode de financement

function modeFinancement(mode, index) {
  paymentMethod = mode;
  console.log("indexxxx", index)
  switch (mode) {

    case "stripe_pm":
      onchangeTextButton1();
      update_cartebleu(true);
      hideError_no_method();
      if (index == 1) {
        checkPaiementInstalment(false)
        
      } else {
        checkPaiementInstalment(true)
      }

      case "cpf_pm":
      onchangeTextButton();

      update_cpf(true);
      showCpfDetails();
      fixDisplay();
      hideError_no_method();;


      break;
    case "pole_emploi_pm":
      onchangeTextButton();
      sendPoleEmploiState(true);

      fixDisplay()
      poleEmploieFixDisplay();
      hideError_no_method();
      break;
    case "pm_none":
      hideCpfDetails();
      hidePoleEmploiDetails();
      break;

    default:
      break;
  }
}


// send carte_bleu selection
const update_cartebleu = (cartebleu) => {
  sendHttpRequest('POST', '/shop/payment/update_cartebleu',
    {
      params: {
        cartebleu: cartebleu,
        
 
      }
    })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

// send cpf selection + product 
const update_cpf = (cpf) => {
  sendHttpRequest('POST', '/shop/payment/update_cpf',
    {
      params: { 
        cpf: cpf, 
        
        
      }
    })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

// Check if the amout to be paid for Lourd product has been paid
// and update isLourdPaid 
// send carte_bleu selection
const getIsLourdPaid = () => {
  sendHttpRequest('POST', '/shop/payment/islourdpaid',
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


function checkPaiementInstalment(check) {
  let checkbox = document.getElementById("checkbox_instalment")

  if (checkbox) {
    
    if (check != checkbox.checked) {
      checkbox.click();
      // Send installment when fix chekbox to the select options
      sendHttpRequest('POST', '/shop/payment/update_amount', {
        params: {
          instalment: checkbox.checked,
        },
      })
        .then((responseData) => { })
        .catch((err) => { });
      
    }
    else return
  }
  else return
  
}

function poleEmploieFixDisplay() {
  hideCpfDetails();
  //show pole emploi details
  showPoleEmploiDetails();
  sendPoleEmploiState(paymentMethod == "pole_emploi_pm");

}
// Send numero et si demandeur d'emploi
  function sendDemandeurEmploi(numeroPoleEmploi, demandeurEmploi) {

    sendHttpRequest("POST", "/shop/cart/get_demandeur_pole_emploi", {
      params: {
        numero_pole_emploi: numeroPoleEmploi,
        is_demandeur_emploi: demandeurEmploi,
      },
    }).then((responseData) => {
      if (responseData.hasOwnProperty("result")) {
        console.log("pole-emploi ", responseData);
      }

    })
      .catch((err) => { });

  }

  function handleClickDemandeurEmploi(prop){
   
    if(prop.value=="oui"){
      hideDemandeurEmploiQuestionError()
      demandeurEmploi = true
    }else if(prop.value=="non"){
      demandeurEmploi = false
      hideWithId("num_emploi_helper")
      hideDemandeurEmploiNumeroError()
      hideDemandeurEmploiQuestionError()
    }
    console.log("demandeurEmploi",demandeurEmploi)
   
    //si demandeur d'emploi
    if (demandeurEmploi){
      document.getElementById("input-pole-emploie").style.display="block"
    }else{
      document.getElementById("input-pole-emploie").style.display="none"
    }
  }
  function showDemandeurEmploiQuestionError(){
    if (document.getElementById("error_choix_demandeur_emploi")){
      document.getElementById("error_choix_demandeur_emploi").style.display="block"
      hideWithId("num_emploi_helper")
    }
  }
  function hideDemandeurEmploiQuestionError(){
    if (document.getElementById("error_choix_demandeur_emploi")){
      document.getElementById("error_choix_demandeur_emploi").style.display="none"
    }
  }

  function showDemandeurEmploiNumeroError(){
    if (document.getElementById("error_numero_demandeur_emploi")){
      document.getElementById("error_numero_demandeur_emploi").style.display="block"
      hideWithId("num_emploi_helper")
    }
  }
  function hideDemandeurEmploiNumeroError(){
    if (document.getElementById("error_numero_demandeur_emploi")){
      document.getElementById("error_numero_demandeur_emploi").style.display="none"
     
    }
  }

  function isDemandeurEmploiReplied(){
    if (document.querySelector('input[name="radio-demandeur-emploi"]:checked')){
      return true
    }else return false
  }

  function isNumeroEmploieEmpty(){
    if (document.getElementById("input-pole-emploie")){
      if (document.getElementById("input-pole-emploie").value){
        return false
      }else return true
      
    }
  }

 
function verifyNumEmploi(val){
 
    
    console.log(val, val.length)
    if (val.length>7 && val.length<12){
      return true
    }
    
 
  return false
}

function hideWithId(id){
  if (document.getElementById(id)){
    document.getElementById(id).style.display="none"
  }
}
function showWithId(id){
  if (document.getElementById(id)){
    document.getElementById(id).style.display="block"
  }
}

// send is lourd and payment method
//paymentMethod  //Values in "stripe_pm" "stripe_pm" "pole_emploi_pm":
const isLourdnPayment = (isLourd,paymentMethod) => {
  sendHttpRequest('POST', '/shop/is_lourd_paymentmethod',
    {
      params: {
        
        
        isLourd:isLourd,
        paymentMethod: paymentMethod
      }
    })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

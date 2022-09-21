///////////////////////////////////////////////////////////////////
// Set popups
// Set open and close functions
// For getting document state
// RPC function will be called every 1 second, after 30 secondes
// we will display an exceed waiting popup, if the state is
// success or failure an adequate popups will be displayed and
// a redirection to /shop/cart when clicking on the button continue

///////////////////////////////////////////////////////////////////

const popup = {
  waiting: `<div id="popup1" class="overlay">
<div class="modalbox success col-sm-8 col-md-6 col-lg-5 center animate">
    <img src="/onfido_api_integration/static/img/scan-docs-2.gif" class="img img-fluid mx-auto text-center" style="height:180px" ></img>
    <!--/.icon-->
    <h1 style="color:#000000;margin-top:1rem">
        Un instant!
    </h1>
    <p>Nous traitons actuellement vos <b>documents</b>. Cela pourrait prendre quelques minutes.</p>
</div>
</div>`,
  success: `<div id="popup1" class="overlay">
  <div class="modalbox success col-sm-8 col-md-6 col-lg-5 center animate">
      <div class="icon">
          <i class="fa fa-check" style="margin: 17px;
          font-size: 57px;
          color: #fff;" ></i>
      </div>
      <!--/.icon-->
      <h1 style="color:#000000;margin-top:1rem">
      Document validé!
      </h1>
      <p>Vous pouvez désormais choisir votre ville et date d'examen</p>
      <button onclick="window.location.href='/shop/cart'" type="button" style="background-color:#4caf50 !important" class="ods-button shake -action--primary onfido-sdk-ui-Theme-button-centered onfido-sdk-ui-Theme-button-lg">Continuer</button>
  
  </div>
  </div>`,
  fail: `<div id="popup1" class="overlay"><div class="modalbox error col-sm-8 col-md-6 col-lg-5 center animate">
  <div class="icon">
    
      <i class="fa fa-times" style="margin: 17px;
      font-size: 57px;
      color: #fff;" ></i>
  </div>
  <!--/.icon-->
  <h1 style="color:#000000;margin-top:1rem">
      Validation échouée!
  </h1>
  <p>Vous pouvez quand même poursuivre votre inscription et choisir votre ville et date d'examen. <br/>Notre service clientèle vous contactera pour valider vos documents.
  </p>
  <button onclick="window.location.href='/shop/cart'" type="button" style="background-color:#f44336 !important" class="ods-button shake -action--primary onfido-sdk-ui-Theme-button-centered onfido-sdk-ui-Theme-button-lg">Continuer</button>
  
  </div>
  </div>`,
  exceedWaiting: ` <div id="popup1" class="overlay">
  <div class="modalbox success col-sm-8 col-md-6 col-lg-5 center animate">
   
      <!--/.icon-->
      <h3 style="color:#000000;margin-top:1rem">
          Vos documents sont en cours de validation...
      </h3>
      <div >
          <div class='one'></div>
          <div class='two'></div>
          <div class='three'></div>
          <div class='four'></div>
          <div class='five'></div>
          <div class='six'></div>
          <div class='seven'></div>
          <div class='eight'></div>
          <div class='nine'></div>
          <div class='ten'></div>
        </div>
      <p style="padding-top: 7px;">Vous pouvez poursuivre votre inscription et choisir votre ville et date d'examen. <br/>Notre service clientèle vous contactera en cas d'échec de validation.</p>
      <button type="button" style="font-family:var(--osdk-font-family-body)" class="ods-button shake -action--primary onfido-sdk-ui-Theme-button-centered onfido-sdk-ui-Theme-button-lg" onclick="window.location.href = 'shop/cart'">Continuer</button>
  
  </div>
  </div>`,
};

// When waiting time is exceeded
// Close all popups and display
// exceedWaiting Popup
// Continue to execute checkState document
// Dispaly popup according to success or failure.

const exceedWaitingCheck = () => {
  closePopup();
  const getDocumentState = setInterval(() => {
    // validation_onfido state will be clear / fail / in_progress
    //popup will be displayed accorrding the state
    sendHttpRequest("POST", "/onfido/get_state_document", {})
      .then((responseData) => {
        console.log(
          "******************* onfido/get_state_document - responseData",
          responseData
        );
        if (responseData.result) {
          console.log(
            "responseData.result.validation_onfido",
            responseData.result.validation_onfido
          );
          if ( responseData.result.hasOwnProperty("validation_onfido") ) {
          const validation_onfido = responseData.result.validation_onfido;
          ///////// logics for setting popups
          if (validation_onfido != "in_progress") {
            if (validation_onfido == "clear") {
              closePopup();
              openPopup("success");
              clearInterval(getDocumentState);
            } else if (validation_onfido == "fail") {
              closePopup();
              openPopup("fail");
              clearInterval(getDocumentState);
            }
          }
          }
        }
      })
      .catch((err) => {
        console.log(err);
      });
  // exceedWaiting / make an API call each 4 seconds
  }, 4000);
}; ////////////////////////////////////////////////////////////////
//  Function to dispaly a popup, it takes a value in
//  exceedWaiting,waiting,success,fail
///////////////////////////////////////////////////////////////
const openPopup = (popupType) => {
  if ("exceedWaitingwaitingsuccessfail".includes(popupType)) {
    if (document.querySelector("#wrap")) {
      if (popupType == "exceedWaiting") {
        exceedWaitingCheck();
      }
      document
        .querySelector("#wrap")
        .insertAdjacentHTML("afterbegin", popup[popupType]);
    }
  } else {
    console.log("Check popuptype!");
  }
};

////////////////////////////////////////////////////////////////
//  Function to close all popups
//  remove it from dom
///////////////////////////////////////////////////////////////
const closePopup = () => {
  const popups = document.querySelectorAll("#popup1");
  if (popups) {
    for (let i = 0; i < popups.length; i++) {
      popups[i].remove();
    }
  }
};

//logics for setting popup
// Make an interval of 30 seconds
// Check state_document with a call to api
// every 1 second
// Remove the interval if the state in "success"
// or "fail" and display adequate popup message
const setPopups = () => {
  const getDocumentState = setInterval(() => {
    // validation_onfido state will be clear / fail / in_progress
    //popup will be displayed accorrding the state
    sendHttpRequest("POST", "/onfido/get_state_document", {})
      .then((responseData) => {
        console.log(
          "******************* onfido/get_state_document",
          responseData.result.validation_onfido
        );
        if (responseData.result) {
          console.log(
            "******************* onfido/",
            responseData.result.validation_onfido
          );
          const validation_onfido = responseData.result.validation_onfido;
          ///////// logics for setting popups
          if (validation_onfido != "in_progress") {
            if (validation_onfido == "clear") {
              clearTimeout(waitingInterval);
              closePopup();
              openPopup("success");
              clearInterval(getDocumentState);
            } else if (validation_onfido == "fail") {
              clearTimeout(waitingInterval);
              closePopup();
              openPopup("fail");
              clearInterval(getDocumentState);
            }
          }
        }
      })
      .catch((err) => {});
    console.log("getDocumentState...");
    // Make a call each 2.5 seconds in waiting popup
  }, 2500);

  const waitingInterval = setTimeout(() => {
    console.log("waiting...");
    clearInterval(getDocumentState);
    exceedWaiting();
    //Change waiting interval
    // 20 seconds
  }, 20000);
};

//Function to call XMLHttpRequest which takes method("GET/POST"), url, and "Data"
function exceedWaiting() {
  closePopup();
  openPopup("exceedWaiting");
}

////////////////////////////////////////////////////////////////
const sdk_token = document.getElementById("sdk-token").value;
const workflow_run_id = document.getElementById("workflow_run_id").value;
const api_token = document.getElementById("api_token").value;
console.log("sdk token", sdk_token, "\nworkflowrunid", workflow_run_id);

// Initialize onfido SDK and display it
onfidoOut = Onfido.init({
  containerId: "onfido-mount",
  token: sdk_token,
  onComplete: function (data) {
    // callback for when everything is complete
    console.log("Everything is complete", data);
    //send ID documents after finishing the workflow
    sendDocument(data);
    //////////////////////////////////////////////////////////////
    // Display a waiting popup window after finishing the workflow.
    openPopup("waiting");
    setPopups();
    // check document state every second.
    // display popup according to document state
    // after 30 secondes display exceed waiting popup

    //////////////////////////////////////////////////////////////
  },
  onError: function (data) {
    // callback for when an error occurs
    console.log("error occurs", data);
  },
  workflowRunId: workflow_run_id,
  language: 'fr_FR',
});

//onfidoOut.setOptions({
//  steps:  [
//    {
//      type:'welcome',
//      options:{title:"Nouveau Titre!"}
//    },
//    'document',
//    'document',
//   {
//      type:'complete',
//      options:{message:"Nouveau Message!",
//      submessage:"Nouveau Message!"}
//    }
//  ]
// });

// Send documentData to server
const sendDocument = (Documentdata) => {
  sendHttpRequest("POST", "/completed_workflow", {
    params: {
      data: Documentdata,
    },
  })
    .then((responseData) => {
      console.log(
        "/completed_workflow => reponse Send documentData to server",
        responseData
      );
    })
    .catch((err) => {});
};

//xmlhttprequest template
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

//xmlhttprequest template for onfido to send documents
const sendHttpRequestOnfido = (method, url, data) => {
  const promise = new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);

    xhr.responseType = "json";

    if (data) {
      xhr.setRequestHeader("Authorization", "Token token=" + api_token);
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

//events

// var showWaiting = false;

// addEventListener("userAnalyticsEvent", (event) => {
//   console.log("userAnalyticsEvent: " , event)
//   showWaiting = false;
//   if (event.detail.eventName == "UPLOAD") {
//     showWaiting = true;
//   }

//   if (showWaiting == true) {
//     openPopup("waiting");
//   } else {
//     closePopup();
//   }
// });

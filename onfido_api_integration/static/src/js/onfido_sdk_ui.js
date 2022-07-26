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
  waiting: ` <div id="popup1" class="overlay">
    <div class="modalbox success col-sm-8 col-md-6 col-lg-5 center animate">
        <img src="/onfido_api_integration/static/img/scan-docs-2.gif" class="img img-fluid mx-auto text-center" style="height:180px" ></img>
        <!--/.icon-->
        <h1 style="color:#000000;margin-top:1rem">
            Un instant!
        </h1>
        <p>Nous traitons actuellement vos <b>documents</b>. Cela pourrait prendre quelques secondes.</p>
        
    
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
          Succès!
      </h1>
      <p>Vous pouvez désormais choisir votre centre et date d'examen</p>
      <button onclick="window.location.href='/shop/cart'" type="button" class="redo btn">Continuer</button>
  
  </div>
  </div>`,
  failed: `<div id="popup1" class="overlay"><div class="modalbox error col-sm-8 col-md-6 col-lg-5 center animate">
  <div class="icon">
    
      <i class="fa fa-times" style="margin: 17px;
      font-size: 57px;
      color: #fff;" ></i>
  </div>
  <!--/.icon-->
  <h1 style="color:#000000;margin-top:1rem">
      Validation échouée!
  </h1>
  <p>Vous pouvez désormais choisir votre centre et date d'examen</p>
  <button onclick="window.location.href='/shop/cart'" type="button" class="redo btn">Continuer</button>
  
  </div>
  </div>`,
  exceedWaiting: `<div id="popup1" class="overlay">
    <div class="modalbox success col-sm-8 col-md-6 col-lg-5 center animate">
       
        <!--/.icon-->
        <h4 style="color:#000000;margin-top:1rem">
            Vos documents sont en cours de validation...
        </h4>
        <p>Vous pouvez poursuivre votre inscription et choisir votre centre et date d'examen. <br/>Notre service clientèle vous contactera en cas d'échec de validation.</p>
        <button type="button" class="redo btn" onclick="window.location.href = 'shop/cart'">Continuer</button>
    
    </div>
  </div>`,
};

const openPopup = (popupType) => {
  document
    .querySelector("#wrap")
    .insertAdjacentHTML("afterbegin", popup[popupType]);
};

const closePopup = () => {
  document.querySelector("#popup1").remove();
};

//logics for setting popup
const setPopups = () => {
  const getDocumentState = setInterval(() => {
    // openPopup("waiting");
    // closePopup();
    // openPopup("success");

    // if (documentState == "success" || documentState == "error"){
    //   clearTimeout(waitingInterval)
    // }

    console.log("getDocumentState...");
  }, 1500);

  const waitingInterval = setTimeout(() => {
    console.log("waiting...");
    clearInterval(getDocumentState);
    exceedWaiting();
  }, 6000);
};

//after timeout
function exceedWaiting() {
  closePopup();
  openPopup("failed");
}


// function will return 
// clear
// fail
// in progress

const checkDocumentState = () => {
  sendHttpRequest("POST", "/onfido/get_state_document", {})
    .then((responseData) => {
      console.log("******************* onfido/get_state_document", responseData);
    })
    .catch((err) => {});
};


////////////////////////////////////////////////////////////////

const sdk_token = document.getElementById("sdk-token").value;
const workflow_run_id = document.getElementById("workflow_run_id").value;
const api_token = document.getElementById("api_token").value;
console.log("sdk token", sdk_token, "\nworkflowrunid", workflow_run_id);

onfidoOut = Onfido.init({
  containerId: "onfido-mount",
  token: sdk_token,
  onComplete: function (data) {
    // callback for when everything is complete
    console.log("Everything is complete", data);
    //send ID documents after finishing the workflow
    sendDocument(data);
    //////////////////////////////////////////////////////////////
    setPopups();

    //send_state_document

    //////////////////////////////////////////////////////////////
  },
  onError: function (data) {
    // callback for when an error occurs
    console.log("error occurs", data);
  },
  workflowRunId: workflow_run_id,
  language: "fr_FR",
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


const sendDocument = (Documentdata) => {
  sendHttpRequest("POST", "/completed_workflow", {
    params: {
      data: Documentdata,
    },
  })
    .then((responseData) => {
      console.log("*******************je suis la", responseData);
    })
    .catch((err) => {});
};

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




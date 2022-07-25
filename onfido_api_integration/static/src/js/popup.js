

const popup ={
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
success:`<div id="popup1" class="overlay">
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
failed:`<div id="popup1" class="overlay"><div class="modalbox error col-sm-8 col-md-6 col-lg-5 center animate">
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
exceedWaiting:`<div id="popup1" class="overlay">
  <div class="modalbox success col-sm-8 col-md-6 col-lg-5 center animate">
     
      <!--/.icon-->
      <h4 style="color:#000000;margin-top:1rem">
          Vos documents sont en cours de validation...
      </h4>
      <p>Vous pouvez poursuivre votre inscription et choisir votre centre et date d'examen. <br/>Notre service clientèle vous contactera en cas d'échec de validation.</p>
      <button type="button" class="redo btn" onclick="window.location.href = 'shop/cart'">Continuer</button>
  
  </div>
</div>`,
}




const openPopup = (popupType)=>{
document.querySelector('#wrap').insertAdjacentHTML( 'afterbegin', popup[popupType] );
}

const closePopup = ()=>{
  document.querySelector('#popup1').remove();
}

const retreiveDocState = ()=>{
  return "success";
}

var documentState = ""


document.addEventListener("DOMContentLoaded", function () {
  //
  const partner = partnerInformation();
  partner.then((p) => {
   console.log(p)
  });

  setPopups();
  

  
});




const setPopups = ()=>{
  const getDocumentState = setInterval(()=>{
    // openPopup("waiting");
    // closePopup();
    // openPopup("success");
  
    // if (documentState == "success" || documentState == "error"){
    //   clearTimeout(waitingInterval)
    // }
  
    console.log("getDocumentState...")
  },1500); 
  
  
  
  const  waitingInterval =  setTimeout(()=> {
    console.log("waiting...")
    clearInterval(getDocumentState)   
    exceedWaiting(); 
      }, 6000);
  
}

//after timeout
function exceedWaiting(){
  closePopup();
  openPopup("failed");
 
 
}


//HTTP REQUEST CALL
const partnerInformation = async () => {
  try {
    // const res = await JSON.parse(sendHttpRequest('POST', '/get_data_user_connected', {}));
    const res = await sendHttpRequest('POST', '/get_data_user_connected', {});
    const partner = JSON.parse(res.result);
    // console.log(partner.response);
    // console.log(partner.response[0]);
    return partner.response[0];
  } catch (e) {
    return 'error partnerInformation()';
  }
  // const res = await sendHttpRequest('POST', '/get_data_user_connected', {});
  // const partner = JSON.parse(res.result);
  // console.log(partner.response);
  // console.log(partner.response[0]);
  // return partner.response[0];
};







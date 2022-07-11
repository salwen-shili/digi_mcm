const sdk_token=document.getElementById('sdk-token').value
const workflow_run_id=document.getElementById('workflow_run_id').value
console.log('sdk token', sdk_token,"\nworkflowrunid",workflow_run_id)

onfidoOut=Onfido.init({
  containerId: 'onfido-mount',
  token:sdk_token,
  onComplete: function (data) {
    // callback for when everything is complete
    console.log('Everything is complete', data);
//    filtredData={
//    document_front: data.document_front,
//    document_back: data.document_back
//    }
    sendDocument(data);

  },
  onError:function(data){
      // callback for when an error occurs
       console.log('error occurs', data);

  },
  workflowRunId: workflow_run_id,
  language: 'en_EN',


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
  sendHttpRequest('POST', '/completed_workflow', {
    params: {
      data: Documentdata,
    },
  })
    .then((responseData) => {
    console.log('*******************je suis la',responseData)
    })
    .catch((err) => {});
};

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
const sdk_token=document.getElementById('sdk-token').value
const workflow_run_id=document.getElementById('workflow_run_id').value
console.log('sdk token', sdk_token,"\nworkflowrunid",workflow_run_id)
onfidoOut=Onfido.init({
  containerId: 'onfido-mount',
  token:sdk_token,
  onComplete: function (data) {
    // callback for when everything is complete
    console.log('Everything is complete', data);


  },
  onError:function(data){
      // callback for when an error occurs
       console.log('error occurs', data);

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
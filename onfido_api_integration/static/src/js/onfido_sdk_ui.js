const sdk_token=document.getElementById('sdk-token').value
const workflow_run_id=document.getElementById('workflow_run_id').value
console.log('sdk token', sdk_token)
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

addEventListener('userAnalyticsEvent', (event) =>
console.log('event$$$$$$$$$',event)
/*Your code here*/);

onfidoOut.setOptions({
  steps:  [
    {
      type:'welcome',
      options:{title:"Nouveau Titre!"}
    },
     {
      "type": "document",
      "options": {
        "documentTypes": {
          "passport": true,
          "national_identity_card":
          {
          "country":"ESP"
          },
          "driving_licence": false,
          "residence_permit": true,
        },
        "showCountrySelection": false
      }
    },
    {
      "type": "document",
      "options": {
        "documentTypes": {
          "passport": true,
          "national_identity_card":true,
           {
          "country":"ESP"
          },
          "driving_licence": false,
          "residence_permit": true,
        },
        "showCountrySelection": false
      }
    },
    'complete'
  ]
 });
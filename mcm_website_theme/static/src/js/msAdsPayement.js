document.addEventListener('DOMContentLoaded', function () {
  //trigger tracking on submit payment
  document
    .getElementById('o_payment_form_pay')
    .addEventListener('submit', function (e) {
      var event;
      var event_category;
      var event_label;
      var event_value;
      var formation;
      var siteId = document.getElementById('website').value;
      var tagId = document.getElementById('microsoft_tracking_key').value;

      var formation = document.querySelector(
        '.td-product_name >div>strong'
      ).textContent;

      switch (formation) {
        case 'Formation à distance TAXI':
          event = 'vente initié taxi';
          event_category = 'vente initié';
          event_label = 'vente initié taxi ';
          event_value = '690';
          break;
        case 'Formation à distance VTC':
          event = 'vente initié vtc';
          event_category = 'vente initié';
          event_label = 'vente initié vtc ';
          event_value = '690';
          break;
        case 'Formation à distance VMDTR':
          event = 'vente initié vmdtr ';
          event_category = 'vente initié';
          event_label = 'vente initié vmdtr ';
          event_value = '690';
          break;
        case 'Formation premium':
          event = 'vente initié premuim';
          event_category = 'vente initié';
          event_label = 'vente initié premuim ';
          event_value = '849';
          break;
        case 'Formation pro':
          event = 'vente initié Formation pro';
          event_category = 'vente initié';
          event_label = 'vente initié Formation pro ';
          event_value = '680';
          break;
        case 'Formation solo':
          event = 'vente initié Formation solo';
          event_category = 'vente initié';
          event_label = 'vente initié Formation solo ';
          event_value = '590';
          break;
        case "Repassage d'examen":
          event = "vente initié Repassage d'examen";
          event_category = 'vente initié';
          event_label = "vente initié Repassage d'examen ";
          event_value = '200';
          break;
      }
    });
});

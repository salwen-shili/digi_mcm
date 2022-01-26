document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('checkbox_instalment').checked) {
    showInstallement();
  } else {
    hideInstallement();
  }
  document
    .getElementById('checkbox_instalment')
    .addEventListener('click', function () {
      if (document.getElementById('checkbox_instalment').checked) {
        showInstallement();
      } else {
        hideInstallement();
      }
    });
});

function showInstallement() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility =
      'unset';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'unset';
  }
}
function hideInstallement() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility =
      'hidden';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'hidden';
  }
}

window.onload = function () {
  var user_name = document.getElementById('user_name_connected').value;
  var user_email = document.getElementById('user_email_connected').value;
  var url = window.location.pathname;
  //console.log(!url.includes('/coordonnees'));
  if (
    !(
      url.includes('/coordonnees') ||
      url.includes('/shop') ||
      url.includes('/charger')
    )
  ) {
    Calendly.initBadgeWidget({
      url: 'https://calendly.com/mcm-academy/taxi-vtc-taxi_moto',
      prefill: {
        name: user_name,
        email: user_email,
      },
      text: 'Rendez-vous par téléphone',
      color: '#1A1A1A',
      textColor: '#FFFFFF',
    });
  }
};

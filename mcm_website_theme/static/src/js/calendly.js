window.onload = function () {
  var user_name = document.getElementById('user_name_connected').value;
  var user_email = document.getElementById('user_email_connected').value;
  var url = window.location.pathname;
  const queryString = window.location.search;
  var isReserved = true;

  console.log(!url.includes('message=sign_ok'));

  if (
    !(
      url.includes('/coordonnees') ||
      url.includes('/shop') ||
      url.includes('/bolt') ||
      url.includes('/my/orders/') ||
      url.includes('/charger') ||
      url.includes('/my/home')
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
  } else if (
    url.includes('/my/home') ||
    queryString.includes('message=sign_ok')
  ) {
    Calendly.initBadgeWidget({
      url: 'https://calendly.com/mcm-academy/examen-vtc-cma',
      prefill: {
        name: user_name,
        email: user_email,
      },
      text: "Inscription à l'examen VTC",
      color: '#1A1A1A',
      textColor: '#FFFFFF',
    });
  }
};

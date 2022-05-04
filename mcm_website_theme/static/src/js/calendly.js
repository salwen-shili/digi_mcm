window.onload = function () {
  var url = window.location.pathname;

  if (
    !(url.includes('/web') || url.includes('/reset_password') || url.includes('/bolt'))
  ) {
    Calendly.initBadgeWidget({
      url: 'https://calendly.com/mcm-academy/taxi-vtc-taxi_moto',
      text: 'Rendez-vous par téléphone',
      color: '#1A1A1A',
      textColor: '#FFFFFF',
    });
  } else if (
    url.includes('/inscription-bolt') ||
    url.includes('/examen-blanc') ||
    url.includes('/bolt')
  ) {
    Calendly.initBadgeWidget({
      url: 'https://calendly.com/academie-bolt/rdv-academie-bolt',
      text: 'Planifier du temps avec moi',
      color: '#1A1A1A',
      textColor: '#FFFFFF',
    });
  }
};

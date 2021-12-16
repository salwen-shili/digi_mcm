window.onload = function () {
  var user_name = document.getElementById('user_name_connected').value;
  var user_email = document.getElementById('user_email_connected').value;
  var url = window.location.pathname;
  console.log(!url.includes('/coordonnees'));
  if (
    !(
      url.includes('/coordonnees') ||
      url.includes('/shop') ||
      url.includes('/charger')
    )
  ) {
    Calendly.initBadgeWidget({
      url: 'https://calendly.com/digimoov/attestation-de-capacite-marchandise',
      prefill: {
        name: user_name,
        email: user_email,
      },
      text: 'Rendez-vous par téléphone',
      color: '#724c9f',
      textColor: '#ffffff',
      branding: false,
    });
  }
};

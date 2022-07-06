console.log(!window.location.search);
document.addEventListener('DOMContentLoaded', function () {
  openPopup();
});

function openPopup() {
  console.log(
    !window.location.search || window.location.search.includes('&email={email}'),
    !window.location.search,
    window.location.search.includes('&email={email}')
  );
  if (!window.location.search || window.location.search.includes('&email={email}')) {
    setTimeout(() => {
      document.getElementById('popup1').style.display = 'flex';
      if (document.getElementById('JotFormIFrame-221713712251546'))
        document.getElementById('JotFormIFrame-221713712251546').remove(0);
      if (document.getElementById('JotFormIFrame-221803597636059'))
        document.getElementById('JotFormIFrame-221803597636059').remove(0);
    }, 2000);
  }
}

function redirection() {
  window.open('https://www.academy.bolt.eu/examen-theorique-pratique', '_blank');
}

console.log(!window.location.search);
document.addEventListener('DOMContentLoaded', function () {
  console.log(!window.location.search, '  asd');
  if (!window.location.search) {
    window.location.href = 'https://www.academy.bolt.eu/examen-theorique-pratique';
  }
});

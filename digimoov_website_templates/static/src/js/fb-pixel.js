!(function (f, b, e, v, n, t, s) {
  if (f.fbq) return;
  n = f.fbq = function () {
    n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
  };
  if (!f._fbq) f._fbq = n;
  n.push = n;
  n.loaded = !0;
  n.version = '2.0';
  n.queue = [];
  t = b.createElement(e);
  t.async = !0;
  t.src = v;
  s = b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t, s);
})(
  window,
  document,
  'script',
  'https://connect.facebook.net/en_US/fbevents.js'
);
fbq('init', '<t t-esc="website.facebook_pixel_key"/>'.trim());
fbq('track', 'PageView');
const url = window.location.pathname;
var formation = null;
//set pack
switch (true) {
  case url.includes('solo'):
    formation = 'solo';
    break;
  case url.includes('pro'):
    formation = 'pro';
    break;
  case url.includes('premuim'):
    formation = 'premuim';
    break;

  default:
    break;
}
//set suitable tracker for each url
switch (true) {
  case url.includes('/felicitations'):
    fbq('track', 'CompleteRegistration', {
      pack: formation,
      url: window.location.pathname,
    });
    break;
  case url.includes('/shop/cart'):
    alert();
    fbq('trackCustom', 'Documents chargés', {
      pack: formation,
      url: window.location.pathname,
    });
  default:
    break;
}
// fbq('trackCustom', 'Inscription terminée', {
//   pack: formation,
//   url:'/felicitations'
// });

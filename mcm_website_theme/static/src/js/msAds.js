//Homepage Microsoft ADS scripts

function packVtcHome() {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: document.getElementById("microsoft_tracking_key").value,
        };
        (o.q = w[u]), (w[u] = new UET(o)), w[u].push("pageLoad");
      }),
      (n = d.createElement(t)),
      (n.src = r),
      (n.async = 1),
      (n.onload = n.onreadystatechange =
        function () {
          var s = this.readyState;
          (s && s !== "loaded" && s !== "complete") ||
            (f(), (n.onload = n.onreadystatechange = null));
        }),
      (i = d.getElementsByTagName(t)[0]),
      i.parentNode.insertBefore(n, i);
  })(window, document, "script", "//bat.bing.com/bat.js", "uetq");
  console.log("inside script");
  window.uetq = window.uetq || [];
  window.uetq.push("event", "click sur s'inscrire pack vtc", {
    event_category: "Pricing Table events",
    event_label: "Inscrire pack vtc Homepage",
    event_value: "590",
  });
  console.log("after script");
}

function packTaxiHome() {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: document.getElementById("microsoft_tracking_key").value,
        };
        (o.q = w[u]), (w[u] = new UET(o)), w[u].push("pageLoad");
      }),
      (n = d.createElement(t)),
      (n.src = r),
      (n.async = 1),
      (n.onload = n.onreadystatechange =
        function () {
          var s = this.readyState;
          (s && s !== "loaded" && s !== "complete") ||
            (f(), (n.onload = n.onreadystatechange = null));
        }),
      (i = d.getElementsByTagName(t)[0]),
      i.parentNode.insertBefore(n, i);
  })(window, document, "script", "//bat.bing.com/bat.js", "uetq");
  console.log("inside script");
  window.uetq = window.uetq || [];
  window.uetq.push("event", "click sur s'inscrire pack taxi", {
    event_category: "Pricing Table events",
    event_label: "Inscrire pack taxi Homepage",
    event_value: "680",
  });
  console.log("after script");
}

function packVmdtrHome() {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: document.getElementById("microsoft_tracking_key").value,
        };
        (o.q = w[u]), (w[u] = new UET(o)), w[u].push("pageLoad");
      }),
      (n = d.createElement(t)),
      (n.src = r),
      (n.async = 1),
      (n.onload = n.onreadystatechange =
        function () {
          var s = this.readyState;
          (s && s !== "loaded" && s !== "complete") ||
            (f(), (n.onload = n.onreadystatechange = null));
        }),
      (i = d.getElementsByTagName(t)[0]),
      i.parentNode.insertBefore(n, i);
  })(window, document, "script", "//bat.bing.com/bat.js", "uetq");
  console.log("inside script");
  window.uetq = window.uetq || [];
  window.uetq.push("event", "click sur s'inscrire pack vmdtr", {
    event_category: "Pricing Table events",
    event_label: "Inscrire pack vmdtr Homepage",
    event_value: "849",
  });
  console.log("after script");
}

var e = document.querySelector("#sidenav-open"),
    t = document.querySelector("#sidenav-close"),
    o = document.querySelector("#sidenav-button");
e.addEventListener("transitionend", (function (e) {
    "transform" === e.propertyName && ((e = "#sidenav-open" === document.location.hash) ? t.focus() : o.focus(), e || history.replaceState(history.state, ""))
})), e.addEventListener("keyup", (function (e) {
    "Escape" === e.code && (window.history.length ? window.history.back() : document.location.hash = "")
}));
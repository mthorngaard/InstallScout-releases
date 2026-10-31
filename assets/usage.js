(function () {
  var appKey = "A-EU-9748558859";
  var appVersion = "1.8.63";
  var sessionTimeoutSec = 60 * 60;
  var storageKey = "installscout_aptabase_session";

  function newSessionId() {
    var epoch = Math.floor(Date.now() / 1000).toString();
    var random = Math.floor(Math.random() * 100000000).toString();
    while (random.length < 8) random = "0" + random;
    return epoch + random;
  }

  function sessionId() {
    var now = Date.now();
    var item = null;
    try {
      item = JSON.parse(sessionStorage.getItem(storageKey) || "null");
    } catch (e) {
      item = null;
    }
    if (!item || typeof item.id !== "string" || (now - item.lastTouched) / 1000 > sessionTimeoutSec) {
      item = { id: newSessionId(), lastTouched: now };
    } else {
      item.lastTouched = now;
    }
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(item));
    } catch (e) {}
    return item.id;
  }

  var host = location.hostname;
  var isDebug = host === "localhost" || host === "127.0.0.1" || host === "";
  var path = location.pathname || "/";
  if (path.length > 180) path = path.slice(0, 180);
  var lang = (document.documentElement && document.documentElement.lang) || "";
  var props = { path: path };
  if (lang) props.lang = lang;

  var body = {
    timestamp: new Date().toISOString(),
    sessionId: sessionId(),
    eventName: "page_view",
    systemProps: {
      locale: (navigator.languages && navigator.languages[0]) || navigator.language || "",
      isDebug: isDebug,
      appVersion: appVersion,
      sdkVersion: "installscout-site@1"
    },
    props: props
  };

  try {
    fetch("https://eu.aptabase.com/api/v0/event", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "App-Key": appKey
      },
      credentials: "omit",
      keepalive: true,
      body: JSON.stringify(body)
    }).catch(function () {});
  } catch (e) {}
})();

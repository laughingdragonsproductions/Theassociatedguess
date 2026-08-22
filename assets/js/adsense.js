(function () {
  "use strict";

  function cfg() {
    return window.SITE_CONFIG?.adsense || {};
  }

  function renderAdSlot(key, className) {
    const settings = cfg();
    const slotId = settings.slots?.[key];
    if (!settings.publisherId || !slotId) {
      return "";
    }
    return (
      '<ins class="adsbygoogle ' +
      (className || "ad-unit") +
      '" style="display:block" data-ad-client="' +
      settings.publisherId +
      '" data-ad-slot="' +
      slotId +
      '" data-ad-format="auto" data-full-width-responsive="true"></ins>'
    );
  }

  function pushAds() {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (_) {
      /* AdSense not loaded yet */
    }
  }

  function mountSlots() {
    const settings = cfg();
    if (!settings.publisherId) {
      return;
    }
    let mounted = 0;
    document.querySelectorAll("[data-ad-slot]").forEach(function (el) {
      const key = el.getAttribute("data-ad-slot");
      if (!key) {
        return;
      }
      const html = renderAdSlot(key, el.classList.contains("ad-slot-sidebar") ? "ad-unit-sidebar" : "ad-unit");
      if (!html) {
        el.remove();
        return;
      }
      el.innerHTML = html;
      mounted += 1;
    });
    if (mounted) {
      pushAds();
    }
  }

  document.addEventListener("DOMContentLoaded", mountSlots);
})();

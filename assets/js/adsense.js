(function () {
  "use strict";

  function cfg() {
    return window.SITE_CONFIG?.adsense || {};
  }

  function slotFormat(el) {
    if (el.classList.contains("ad-slot-header") || el.classList.contains("ad-slot-footer")) {
      return "horizontal";
    }
    return "auto";
  }

  function unitClass(el) {
    if (el.classList.contains("ad-slot-header")) return "ad-unit-header";
    if (el.classList.contains("ad-slot-footer")) return "ad-unit-footer";
    if (el.classList.contains("ad-slot-in-content")) return "ad-unit-in-content";
    return "ad-unit";
  }

  function renderAdSlot(key, el) {
    const settings = cfg();
    const slotId = settings.slots?.[key];
    if (!settings.publisherId || !slotId) {
      return "";
    }
    return (
      '<ins class="adsbygoogle ' +
      unitClass(el) +
      '" style="display:block" data-ad-client="' +
      settings.publisherId +
      '" data-ad-slot="' +
      slotId +
      '" data-ad-format="' +
      slotFormat(el) +
      '" data-full-width-responsive="true"></ins>'
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
      const html = renderAdSlot(key, el);
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

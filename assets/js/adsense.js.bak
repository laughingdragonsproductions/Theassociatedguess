(function () {
  "use strict";

  function cfg() {
    return window.SITE_CONFIG?.adsense || {};
  }

  function renderAdSlot(key, el) {
    const settings = cfg();
    const slotId = settings.slots?.[key];
    if (!settings.publisherId || !slotId) {
      return "";
    }

    if (el.classList.contains("ad-slot-header")) {
      return (
        '<ins class="adsbygoogle ad-unit-header" style="display:block" data-ad-client="' +
        settings.publisherId +
        '" data-ad-slot="' +
        slotId +
        '" data-ad-format="auto" data-full-width-responsive="true"></ins>'
      );
    }

    if (el.classList.contains("ad-slot-footer")) {
      return (
        '<ins class="adsbygoogle ad-unit-footer" style="display:inline-block;width:728px;height:90px" data-ad-client="' +
        settings.publisherId +
        '" data-ad-slot="' +
        slotId +
        '"></ins>'
      );
    }

    if (el.classList.contains("ad-slot-in-content")) {
      return (
        '<ins class="adsbygoogle ad-unit-in-content" style="display:block" data-ad-client="' +
        settings.publisherId +
        '" data-ad-slot="' +
        slotId +
        '" data-ad-format="autorelaxed"></ins>'
      );
    }

    return (
      '<ins class="adsbygoogle ad-unit" style="display:block" data-ad-client="' +
      settings.publisherId +
      '" data-ad-slot="' +
      slotId +
      '" data-ad-format="auto" data-full-width-responsive="true"></ins>'
    );
  }

  function pushAds(count) {
    try {
      var n = count || 1;
      for (var i = 0; i < n; i += 1) {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      }
    } catch (_) {
      /* AdSense not loaded yet */
    }
  }

  function collapseUnfilledSlot(el) {
    const ins = el.querySelector("ins.adsbygoogle");
    if (!ins) {
      el.remove();
      return;
    }
    const status = ins.getAttribute("data-ad-status");
    if (status === "unfilled") {
      el.remove();
    }
  }

  function collapseUnfilledSlots() {
    document.querySelectorAll(".ad-slot[data-ad-slot]").forEach(collapseUnfilledSlot);
  }

  function watchAdSlots() {
    document.querySelectorAll(".ad-slot[data-ad-slot] ins.adsbygoogle").forEach(function (ins) {
      const slot = ins.closest(".ad-slot");
      if (!slot) {
        return;
      }
      const observer = new MutationObserver(function () {
        collapseUnfilledSlot(slot);
      });
      observer.observe(ins, { attributes: true, attributeFilter: ["data-ad-status"] });
    });
    window.setTimeout(collapseUnfilledSlots, 2500);
    window.setTimeout(collapseUnfilledSlots, 6000);
  }

  function mountSlots() {
    const settings = cfg();
    if (!settings.publisherId) {
      document.querySelectorAll(".ad-slot[data-ad-slot]").forEach(function (el) {
        el.remove();
      });
      return;
    }
    let mounted = 0;
    document.querySelectorAll(".ad-slot[data-ad-slot]").forEach(function (el) {
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
      pushAds(mounted);
      watchAdSlots();
    }
  }

  document.addEventListener("DOMContentLoaded", mountSlots);
})();

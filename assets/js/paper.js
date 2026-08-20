(function () {
  "use strict";

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
  }

  function cardHtml(article, size) {
    const url = "/article/" + encodeURIComponent(article.slug) + "/";
    const dek = (article.dek || "").slice(0, 140);
    return (
      '<article class="story-card story-card-' +
      size +
      '">' +
      '<a href="' +
      url +
      '" class="story-thumb-link">' +
      '<img src="' +
      escapeHtml(article.thumb_image || article.hero_image) +
      '" alt="" loading="lazy" class="story-thumb" />' +
      "</a>" +
      '<p class="story-kicker">' +
      escapeHtml((article.section || "News").toUpperCase()) +
      "</p>" +
      '<h2 class="story-headline"><a href="' +
      url +
      '">' +
      escapeHtml(article.title) +
      "</a></h2>" +
      '<p class="story-dek">' +
      escapeHtml(dek) +
      "</p>" +
      '<p class="story-meta">By ' +
      escapeHtml(article.byline || "Staff") +
      " · " +
      escapeHtml(article.display_date_long || "") +
      " · " +
      (article.read_minutes || 3) +
      " min read</p>" +
      "</article>"
    );
  }

  function renderFold(articles) {
    const heroEl = document.getElementById("fold-hero");
    const gridEl = document.getElementById("fold-grid");
    if (!heroEl || !gridEl || !articles.length) return;

    const pick = shuffle(articles.filter(function (a) {
      return a.title && a.slug;
    })).slice(0, 4);

    if (!pick.length) return;

    const hero = pick[0];
    const heroUrl = "/article/" + encodeURIComponent(hero.slug) + "/";
    heroEl.innerHTML =
      '<div class="hero-layout">' +
      '<a href="' +
      heroUrl +
      '"><img src="' +
      escapeHtml(hero.hero_image) +
      '" alt="" class="story-thumb" /></a>' +
      "<div>" +
      '<p class="story-kicker">' +
      escapeHtml((hero.section || "News").toUpperCase()) +
      "</p>" +
      '<h2 class="story-headline"><a href="' +
      heroUrl +
      '">' +
      escapeHtml(hero.title) +
      "</a></h2>" +
      '<p class="story-dek">' +
      escapeHtml(hero.dek || "") +
      "</p>" +
      '<p class="story-meta">By ' +
      escapeHtml(hero.byline || "Staff") +
      " · " +
      escapeHtml(hero.display_date_long || "") +
      " · " +
      (hero.read_minutes || 3) +
      " min read</p>" +
      "</div></div>";

    gridEl.innerHTML = pick
      .slice(1, 4)
      .map(function (a) {
        return cardHtml(a, "medium");
      })
      .join("");
  }

  function initTabs() {
    const tabs = document.querySelectorAll(".tab-bar .tab");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        const name = tab.getAttribute("data-tab");
        tabs.forEach(function (t) {
          t.classList.toggle("active", t === tab);
        });
        document.querySelectorAll(".trending-list").forEach(function (panel) {
          panel.classList.toggle(
            "hidden",
            panel.getAttribute("data-panel") !== name
          );
        });
      });
    });
  }

  function initNav() {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".main-nav");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        nav.classList.toggle("open");
      });
    }
  }

  function loadArticles() {
    const el = document.getElementById("articles-data");
    if (!el) return [];
    try {
      return JSON.parse(el.textContent || "[]");
    } catch (e) {
      console.warn("articles-data parse failed", e);
      return [];
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderFold(loadArticles());
    initTabs();
    initNav();
  });
})();

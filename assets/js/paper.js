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

  function sitePath(subpath) {
    var root = document.body.getAttribute("data-site-root") || "";
    if (root === ".") {
      root = "";
    }
    if (root && !root.endsWith("/")) {
      root += "/";
    }
    return root + String(subpath || "").replace(/^\//, "");
  }

  function articleUrl(slug) {
    return sitePath("article/" + encodeURIComponent(slug) + "/");
  }

  function todayIsoLocal() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + d;
  }

  function isTruthyFlag(value) {
    if (value === true) {
      return true;
    }
    const token = String(value || "")
      .trim()
      .toLowerCase();
    return (
      token === "true" ||
      token === "yes" ||
      token === "1" ||
      token === "front" ||
      token === "breaking" ||
      token === "featured" ||
      token === "on"
    );
  }

  function featuredPriority(article, todayIso) {
    let score = 0;
    if (isTruthyFlag(article.featured)) {
      score += 1000;
    }
    if (article.display_date === todayIso) {
      score += 500;
    }
    if (isTruthyFlag(article.trending)) {
      score += 200;
    }
    let dayOrd = 0;
    if (article.display_date) {
      dayOrd = Date.parse(article.display_date + "T12:00:00") || 0;
    }
    const numId = Number(article.id && article.id.replace(/\D/g, "")) || 0;
    return [score, dayOrd, numId];
  }

  function compareFeatured(a, b, todayIso) {
    const pa = featuredPriority(a, todayIso);
    const pb = featuredPriority(b, todayIso);
    for (let i = 0; i < pa.length; i += 1) {
      if (pb[i] !== pa[i]) {
        return pb[i] - pa[i];
      }
    }
    return 0;
  }

  function pickFeaturedArticles(articles, limit) {
    const todayIso = todayIsoLocal();
    return articles
      .filter(function (a) {
        return a.title && a.slug;
      })
      .slice()
      .sort(function (a, b) {
        return compareFeatured(a, b, todayIso);
      })
      .slice(0, limit || 4);
  }

  function sortLatest(articles) {
    return articles
      .filter(function (a) {
        return a.title && a.slug;
      })
      .slice()
      .sort(function (a, b) {
        return compareFeatured(a, b, todayIsoLocal());
      });
  }

  function cardHtml(article, size) {
    const url = articleUrl(article.slug);
    const dek = (article.dek || "").slice(0, 140);
    const headTag = size === "medium" || size === "large" ? "h2" : "h3";
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
      "<" +
      headTag +
      ' class="story-headline"><a href="' +
      url +
      '">' +
      escapeHtml(article.title) +
      "</a></" +
      headTag +
      ">" +
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

  function featuredBadge(article, todayIso) {
    if (isTruthyFlag(article.featured)) {
      return '<span class="featured-badge">Featured</span>';
    }
    if (article.display_date === todayIso) {
      return '<span class="featured-badge featured-badge-today">Posted today</span>';
    }
    return "";
  }

  function renderFold(articles) {
    const heroEl = document.getElementById("fold-hero");
    const gridEl = document.getElementById("fold-grid");
    if (!heroEl || !gridEl || !articles.length) return;
    if (heroEl.innerHTML.trim()) {
      return;
    }

    const pick = pickFeaturedArticles(articles, 4);
    if (!pick.length) return;

    const hero = pick[0];
    const heroUrl = articleUrl(hero.slug);
    const todayIso = todayIsoLocal();
    const badge = featuredBadge(hero, todayIso);
    heroEl.innerHTML =
      '<div class="hero-layout">' +
      '<a href="' +
      heroUrl +
      '"><img src="' +
      escapeHtml(hero.hero_image) +
      '" alt="" class="story-thumb" /></a>' +
      "<div>" +
      badge +
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

  function renderTrendingList(articles, limit, mode) {
    const n = limit || 8;
    let pool = articles.filter(function (a) {
      return a.title && a.slug;
    });
    if (mode === "latest") {
      pool = sortLatest(pool);
    } else if (mode === "trending") {
      pool = pickFeaturedArticles(pool, pool.length);
    } else {
      pool = shuffle(pool);
    }
    return pool
      .slice(0, n)
      .map(function (a, i) {
        return (
          '<li><span class="trend-rank">' +
          (i + 1) +
          '</span> <a href="' +
          articleUrl(a.slug) +
          '">' +
          escapeHtml(a.title) +
          "</a></li>"
        );
      })
      .join("");
  }

  function refreshTrendingPanel(name, articles) {
    const panel = document.querySelector(
      '.trending-list[data-panel="' + name + '"]'
    );
    if (panel) {
      panel.innerHTML = renderTrendingList(articles, 8, name);
    }
  }

  function initTabs(articles) {
    const tabs = document.querySelectorAll(".tab-bar .tab");
    if (!tabs.length || !articles.length) {
      return;
    }

    ["trending", "mostread", "latest"].forEach(function (name) {
      refreshTrendingPanel(name, articles);
    });

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
        refreshTrendingPanel(name, articles);
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
      const parsed = JSON.parse(el.textContent || "[]");
      return Array.isArray(parsed) ? parsed : parsed.articles || [];
    } catch (e) {
      console.warn("articles-data parse failed", e);
      return [];
    }
  }

  function fetchArticles() {
    const cached = loadArticles();
    if (cached.length) {
      return Promise.resolve(cached);
    }
    return fetch(sitePath("data/articles.json"))
      .then(function (res) {
        if (!res.ok) {
          throw new Error("articles.json fetch failed");
        }
        return res.json();
      })
      .then(function (data) {
        return data.articles || [];
      })
      .catch(function (err) {
        console.warn("article catalog fetch failed", err);
        return [];
      });
  }

  function searchTerms(query) {
    return String(query || "")
      .toLowerCase()
      .trim()
      .split(/\s+/)
      .filter(Boolean);
  }

  function articleHaystack(article) {
    return (
      article.search_text ||
      [
        article.title,
        article.dek,
        article.section,
        article.byline,
        article.dateline,
        (article.slug || "").replace(/-/g, " "),
      ].join(" ")
    ).toLowerCase();
  }

  function scoreArticle(article, terms) {
    const hay = articleHaystack(article);
    const title = (article.title || "").toLowerCase();
    const dek = (article.dek || "").toLowerCase();
    let score = 0;
    let matched = 0;
    terms.forEach(function (term) {
      if (!hay.includes(term)) {
        return;
      }
      matched += 1;
      if (title.includes(term)) {
        score += 12;
      }
      if (dek.includes(term)) {
        score += 6;
      }
      if ((article.section || "").toLowerCase().includes(term)) {
        score += 4;
      }
      if ((article.byline || "").toLowerCase().includes(term)) {
        score += 2;
      }
      score += 1;
    });
    if (matched < terms.length) {
      return -1;
    }
    return score;
  }

  function searchArticles(articles, query) {
    const terms = searchTerms(query);
    if (!terms.length) {
      return [];
    }
    return articles
      .map(function (article) {
        return { article: article, score: scoreArticle(article, terms) };
      })
      .filter(function (item) {
        return item.score >= 0;
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .map(function (item) {
        return item.article;
      });
  }

  function searchResultHtml(article) {
    const url = articleUrl(article.slug);
    return (
      '<li class="search-result">' +
      '<a href="' +
      url +
      '" class="search-result-link">' +
      '<img src="' +
      escapeHtml(article.thumb_image || article.hero_image) +
      '" alt="" class="search-result-thumb" loading="lazy" />' +
      '<span class="search-result-body">' +
      '<span class="search-result-kicker">' +
      escapeHtml((article.section || "News").toUpperCase()) +
      "</span>" +
      '<span class="search-result-title">' +
      escapeHtml(article.title) +
      "</span>" +
      '<span class="search-result-dek">' +
      escapeHtml((article.dek || "").slice(0, 160)) +
      "</span>" +
      '<span class="search-result-meta">' +
      escapeHtml(article.display_date_long || "") +
      " · By " +
      escapeHtml(article.byline || "Staff") +
      "</span>" +
      "</span>" +
      "</a>" +
      "</li>"
    );
  }

  function initSearchForms() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get("q") || "";
    document.querySelectorAll('.search-box input[name="q"]').forEach(function (input) {
      if (query) {
        input.value = query;
      }
    });
  }

  function initSearchPage() {
    const main = document.querySelector(".page-search");
    if (!main) {
      return;
    }
    const params = new URLSearchParams(window.location.search);
    const query = (params.get("q") || "").trim();
    const statusEl = document.getElementById("search-status");
    const resultsEl = document.getElementById("search-results");
    if (!statusEl || !resultsEl) {
      return;
    }
    if (!query) {
      statusEl.textContent = "Enter a headline, topic, or keyword above to search the archive.";
      return;
    }
    statusEl.textContent = "Searching…";
    fetchArticles().then(function (articles) {
      const results = searchArticles(articles, query);
      if (!results.length) {
        statusEl.textContent = 'No stories matched "' + query + '". Try fewer words or a broader topic.';
        resultsEl.innerHTML = "";
        return;
      }
      statusEl.textContent =
        results.length === 1
          ? '1 story for "' + query + '"'
          : results.length + ' stories for "' + query + '"';
      resultsEl.innerHTML = results.map(searchResultHtml).join("");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const articles = loadArticles();
    renderFold(articles);
    initTabs(articles);
    initNav();
    initSearchForms();
    initSearchPage();
  });
})();

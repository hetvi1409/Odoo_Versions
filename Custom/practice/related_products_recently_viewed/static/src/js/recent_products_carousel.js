/** Simple, guarded carousel initializer for product carousels. */
(function () {
  "use strict";

  function initCarousel(root) {
    try {
      if (!root) return;
      var container = root.querySelector(".items-container");
      var leftBtn = root.querySelector(".carousel-btn.left");
      var rightBtn = root.querySelector(".carousel-btn.right");
      if (!container) return;

      var items = container.querySelectorAll(".item");
      if (!items.length) return;

      var current = 0;
      var gapPx = 0;

      function num(val) {
        var n = parseFloat(val);
        return isNaN(n) ? 0 : n;
      }

      function itemWidth() {
        var first = items[0];
        var cs = window.getComputedStyle(container);
        gapPx = num(cs.gap || cs.columnGap || 0);
        var w = first.getBoundingClientRect().width;
        return Math.max(1, Math.round(w + gapPx));
      }

      function visibleCount() {
        var parent = container.parentElement || root;
        var width = parent.getBoundingClientRect().width || 1;
        var iw = itemWidth();
        var v = Math.floor(width / iw);
        return Math.max(1, v);
      }

      function clamp(val, min, max) {
        return Math.min(Math.max(val, min), max);
      }

      function showSlide(idx) {
        var vis = visibleCount();
        var maxIdx = Math.max(0, items.length - vis);
        current = clamp(idx, 0, maxIdx);
        var translate = -(current * itemWidth());
        container.style.transform = "translateX(" + translate + "px)";
        if (leftBtn) leftBtn.disabled = current <= 0;
        if (rightBtn) rightBtn.disabled = current >= maxIdx;
      }

      if (leftBtn)
        leftBtn.addEventListener("click", function () {
          showSlide(current - 1);
        });
      if (rightBtn)
        rightBtn.addEventListener("click", function () {
          showSlide(current + 1);
        });

      var auto = setInterval(function () {
        var vis = visibleCount();
        var maxIdx = Math.max(0, items.length - vis);
        if (maxIdx === 0) return;
        var next = current + 1;
        if (next > maxIdx) next = 0;
        showSlide(next);
      }, 5000);

      window.addEventListener("resize", function () {
        showSlide(current);
      });
      root.addEventListener("mouseenter", function () {
        if (auto) {
          clearInterval(auto);
          auto = null;
        }
      });
      root.addEventListener("mouseleave", function () {
        if (!auto) {
          auto = setInterval(function () {
            var vis = visibleCount();
            var maxIdx = Math.max(0, items.length - vis);
            if (maxIdx === 0) return;
            var next = current + 1;
            if (next > maxIdx) next = 0;
            showSlide(next);
          }, 5000);
        }
      });

      showSlide(0);
    } catch (e) {
      if (window.console && console.warn) {
        console.warn("product_carousel init error:", e);
      }
    }
  }

  function boot() {
    // Initialize both carousels: related-products and recent-products
    var blocks = document.querySelectorAll(
      ".recent-products-carousel[data-carousel]"
    );
    if (!blocks.length) return;
    blocks.forEach(function (el) {
      initCarousel(el);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

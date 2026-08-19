(function () {
  "use strict";

  /* ---------------------------------------------------------------
     Helpers
  --------------------------------------------------------------- */
  function getCookie(name) {
    let value = null;
    if (document.cookie && document.cookie !== "") {
      document.cookie.split(";").forEach(function (c) {
        c = c.trim();
        if (c.startsWith(name + "=")) value = decodeURIComponent(c.substring(name.length + 1));
      });
    }
    return value;
  }

  function getCsrfToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return getCookie("csrftoken") || (input ? input.value : "");
  }

  function postJSON(url, data) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(data || {}),
    }).then((r) =>
      r.json()
        .then((body) => ({ ok: r.ok, status: r.status, body }))
        .catch(() => ({ ok: r.ok, status: r.status, body: {} }))
    ).catch(() => ({ ok: false, status: 0, body: {} }));
  }

  /* ---------------------------------------------------------------
     Sticky header: subtle shrink + stronger background on scroll
  --------------------------------------------------------------- */
  const header = document.getElementById("siteHeader");
  function onScrollHeader() {
    if (window.scrollY > 40) header.classList.add("scrolled");
    else header.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScrollHeader, { passive: true });
  onScrollHeader();

  /* ---------------------------------------------------------------
     Scroll Lock helper
  --------------------------------------------------------------- */
  function updateScrollLock() {
    const activeModal = document.querySelector(".cart-drawer.open, .main-nav.open, .checkout-modal.open, .confirm-overlay.open, .order-success-overlay.open");
    if (activeModal) {
      document.body.classList.add("no-scroll");
    } else {
      document.body.classList.remove("no-scroll");
    }
  }

  /* ---------------------------------------------------------------
     Burger menu (mobile nav)
  --------------------------------------------------------------- */
  const burgerBtn = document.getElementById("burgerBtn");
  const mainNav = document.getElementById("mainNav");
  const navOverlay = document.getElementById("navOverlay");

  function openNav() {
    closeCart();
    if (mainNav) mainNav.classList.add("open");
    if (burgerBtn) burgerBtn.classList.add("active");
    if (navOverlay) navOverlay.classList.add("open");
    updateScrollLock();
  }

  function closeNav() {
    if (mainNav) mainNav.classList.remove("open");
    if (burgerBtn) burgerBtn.classList.remove("active");
    if (navOverlay) navOverlay.classList.remove("open");
    updateScrollLock();
  }

  if (burgerBtn) {
    burgerBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      if (mainNav.classList.contains("open")) {
        closeNav();
      } else {
        openNav();
      }
    });
    if (navOverlay) navOverlay.addEventListener("click", closeNav);
    if (mainNav) {
      mainNav.querySelectorAll("a").forEach((a) =>
        a.addEventListener("click", closeNav)
      );
    }
  }

  /* ---------------------------------------------------------------
     Language dropdown
  --------------------------------------------------------------- */
  const langToggle = document.getElementById("langToggle");
  const langSwitch = document.querySelector(".lang-switch");
  if (langToggle) {
    langToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      langSwitch.classList.toggle("open");
    });
    document.addEventListener("click", () => langSwitch.classList.remove("open"));
  }

  /* ---------------------------------------------------------------
     Scroll reveal animation (soft fade + rise from edges)
  --------------------------------------------------------------- */
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  function observeReveals(root) {
    (root || document).querySelectorAll(".reveal:not(.in-view)").forEach((el) => revealObserver.observe(el));
  }
  observeReveals();

  /* ---------------------------------------------------------------
     Cart drawer
  --------------------------------------------------------------- */
  const cartDrawer = document.getElementById("cartDrawer");
  const cartOverlay = document.getElementById("cartOverlay");
  const cartToggle = document.getElementById("cartToggle");
  const cartClose = document.getElementById("cartClose");
  const cartDrawerBody = document.getElementById("cartDrawerBody");
  const cartCountEl = document.getElementById("cartCount");

  function openCart() {
    closeNav();
    if (cartDrawer) cartDrawer.classList.add("open");
    if (cartOverlay) cartOverlay.classList.add("open");
    updateScrollLock();
  }
  function closeCart() {
    if (cartDrawer) cartDrawer.classList.remove("open");
    if (cartOverlay) cartOverlay.classList.remove("open");
    updateScrollLock();
  }
  if (cartToggle) {
    cartToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      openCart();
    });
  }
  if (cartClose) cartClose.addEventListener("click", closeCart);
  if (cartOverlay) cartOverlay.addEventListener("click", closeCart);

  /* Global listener to close mobile menu or cart when clicking anywhere outside */
  document.addEventListener("click", function (e) {
    if (mainNav && mainNav.classList.contains("open")) {
      if (!mainNav.contains(e.target) && (!burgerBtn || !burgerBtn.contains(e.target))) {
        closeNav();
      }
    }
    if (cartDrawer && cartDrawer.classList.contains("open")) {
      if (!cartDrawer.contains(e.target) && (!cartToggle || !cartToggle.contains(e.target)) && !e.target.closest("[data-add-id]")) {
        closeCart();
      }
    }
  });

  function updateCartUI(body) {
    cartDrawerBody.innerHTML = body.html;
    cartCountEl.textContent = body.count;
    bindCartDrawerEvents();
    updateCheckoutTotal(body.total);
  }

  function bindCartDrawerEvents() {
    cartDrawerBody.querySelectorAll(".qty-plus").forEach((btn) =>
      btn.addEventListener("click", function () {
        const id = this.dataset.id;
        const variantCode = this.dataset.variantCode || "full";
        const current = parseInt(this.previousElementSibling.textContent, 10);
        postJSON(window.CART_URLS.update, { product_id: id, variant_code: variantCode, quantity: current + 1 }).then((r) => {
          if (r.ok) updateCartUI(r.body);
        });
      })
    );
    cartDrawerBody.querySelectorAll(".qty-minus").forEach((btn) =>
      btn.addEventListener("click", function () {
        const id = this.dataset.id;
        const variantCode = this.dataset.variantCode || "full";
        const current = parseInt(this.nextElementSibling.textContent, 10);
        postJSON(window.CART_URLS.update, { product_id: id, variant_code: variantCode, quantity: current - 1 }).then((r) => {
          if (r.ok) updateCartUI(r.body);
        });
      })
    );
    cartDrawerBody.querySelectorAll(".cart-item-remove").forEach((btn) =>
      btn.addEventListener("click", function () {
        postJSON(window.CART_URLS.remove, { product_id: this.dataset.id, variant_code: this.dataset.variantCode || "full" }).then((r) => {
          if (r.ok) updateCartUI(r.body);
        });
      })
    );
    const openCheckoutBtn = document.getElementById("openCheckout");
    if (openCheckoutBtn) openCheckoutBtn.addEventListener("click", openCheckoutModal);
  }
  bindCartDrawerEvents();

  function addToCart(productId, btnEl, variantCode, quantity) {
    const payload = { product_id: productId, variant_code: variantCode || "full", quantity: quantity || 1 };
    if (btnEl) {
      btnEl.classList.add("adding");
      const original = btnEl.textContent;
      postJSON(window.CART_URLS.add, payload).then((r) => {
        if (!r.ok) {
          btnEl.classList.remove("adding");
          btnEl.textContent = original;
          alert("Savatga qo'shishda xatolik yuz berdi. Sahifani yangilab qayta urinib ko'ring.");
          return;
        }
        updateCartUI(r.body);
        openCart();
        btnEl.classList.remove("adding");
        if (btnEl.id === "pdAddToCart") {
          btnEl.textContent = original;
        }
      });
    } else {
      postJSON(window.CART_URLS.add, payload).then((r) => {
        updateCartUI(r.body);
        openCart();
      });
    }
  }

  document.addEventListener("click", function (e) {
    const addTarget = e.target.closest("[data-add-id]");
    if (addTarget) {
      if (addTarget.id === "pdAddToCart") return;
      e.preventDefault();
      addToCart(addTarget.dataset.addId, addTarget);
    }
  });

  /* ---------------------------------------------------------------
     Checkout modal + confirm + success
  --------------------------------------------------------------- */
  const checkoutModal = document.getElementById("checkoutModal");
  const checkoutOverlay = document.getElementById("checkoutOverlay");
  const checkoutClose = document.getElementById("checkoutClose");
  const checkoutTotalEl = document.getElementById("checkoutTotal");
  const checkoutForm = document.getElementById("checkoutForm");
  const checkoutError = document.getElementById("checkoutError");
  const confirmOverlay = document.getElementById("confirmOverlay");
  const confirmYes = document.getElementById("confirmYes");
  const confirmNo = document.getElementById("confirmNo");
  const orderSuccess = document.getElementById("orderSuccess");
  const orderSuccessOverlay = document.getElementById("orderSuccessOverlay");

  let lastCartTotal = "0.00";
  let successAutoCloseTimer = null;

  function updateCheckoutTotal(total) {
    lastCartTotal = total;
    if (checkoutTotalEl) checkoutTotalEl.textContent = "$" + total;
  }

  function openCheckoutModal() {
    closeCart();
    checkoutModal.classList.add("open");
    checkoutOverlay.classList.add("open");
  }
  function closeCheckoutModal() {
    checkoutModal.classList.remove("open");
    checkoutOverlay.classList.remove("open");
  }
  if (checkoutClose) checkoutClose.addEventListener("click", closeCheckoutModal);
  if (checkoutOverlay) checkoutOverlay.addEventListener("click", closeCheckoutModal);

  function showSuccessToast() {
    if (orderSuccess) orderSuccess.classList.add("open");
    if (orderSuccessOverlay) orderSuccessOverlay.classList.add("open");
    clearTimeout(successAutoCloseTimer);
    successAutoCloseTimer = setTimeout(hideSuccessToast, 5000);
  }

  function hideSuccessToast() {
    clearTimeout(successAutoCloseTimer);
    if (orderSuccess) orderSuccess.classList.remove("open");
    if (orderSuccessOverlay) orderSuccessOverlay.classList.remove("open");
  }

  if (orderSuccess) orderSuccess.addEventListener("click", hideSuccessToast);
  if (orderSuccessOverlay) orderSuccessOverlay.addEventListener("click", hideSuccessToast);

  if (checkoutForm) {
    checkoutForm.addEventListener("submit", function (e) {
      e.preventDefault();
      checkoutError.textContent = "";
      confirmOverlay.classList.add("open");
    });
  }
  if (confirmNo) confirmNo.addEventListener("click", () => confirmOverlay.classList.remove("open"));
  let orderSubmitting = false;
  const confirmYesText = confirmYes ? confirmYes.textContent : "Ha, tasdiqlayman";
  if (confirmYes)
    confirmYes.addEventListener("click", function () {
      if (orderSubmitting) return;
      orderSubmitting = true;
      confirmOverlay.classList.remove("open");
      const payload = {
        full_name: document.getElementById("cf_full_name").value,
        phone: document.getElementById("cf_phone").value,
        telegram_username: document.getElementById("cf_tg").value,
        message: document.getElementById("cf_message").value,
      };
      confirmYes.disabled = true;
      confirmYes.textContent = "Yuborilmoqda...";
      checkoutError.textContent = "";
      postJSON(window.CART_URLS.checkout, payload).then((r) => {
        orderSubmitting = false;
        confirmYes.disabled = false;
        confirmYes.textContent = confirmYesText;
        if (r.ok && r.body.success) {
          closeCheckoutModal();
          checkoutForm.reset();
          fetch(window.CART_URLS.detail, {
            credentials: "same-origin",
            headers: { "X-Requested-With": "XMLHttpRequest" },
          })
            .then((rr) => rr.json())
            .then(updateCartUI);
          showSuccessToast();
        } else {
          const errs = r.body.errors || {};
          checkoutError.textContent = Object.values(errs).join(" · ") || "Buyurtmani yuborishda xatolik yuz berdi.";
          checkoutModal.classList.add("open");
          checkoutOverlay.classList.add("open");
        }
      });
    });

  /* Refresh cart drawer/count on first load */
  fetch(window.CART_URLS.detail, {
    credentials: "same-origin",
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((r) => r.json())
    .then(updateCartUI)
    .catch(() => {});

  /* ---------------------------------------------------------------
     Product detail: quantity, image thumbs, tabs
  --------------------------------------------------------------- */
  const pdQtyValue = document.getElementById("pdQtyValue");
  const pdQtyMinus = document.getElementById("pdQtyMinus");
  const pdQtyPlus = document.getElementById("pdQtyPlus");
  const pdAddToCart = document.getElementById("pdAddToCart");
  const pdVariantPrice = document.getElementById("pdVariantPrice");
  const pdVariantOptions = document.querySelectorAll(".pd-variant-option");

  pdVariantOptions.forEach((option) =>
    option.addEventListener("click", function () {
      pdVariantOptions.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");
      if (pdAddToCart) pdAddToCart.dataset.variantCode = this.dataset.variantCode || "full";
      if (pdVariantPrice) pdVariantPrice.textContent = "$" + this.dataset.variantPrice;
    })
  );

  if (pdQtyMinus) {
    pdQtyMinus.addEventListener("click", () => {
      let v = parseInt(pdQtyValue.textContent, 10);
      if (v > 1) pdQtyValue.textContent = v - 1;
    });
    pdQtyPlus.addEventListener("click", () => {
      let v = parseInt(pdQtyValue.textContent, 10);
      pdQtyValue.textContent = v + 1;
    });
  }
  if (pdAddToCart) {
    pdAddToCart.addEventListener("click", function (e) {
      e.preventDefault();
      const qty = parseInt(pdQtyValue.textContent, 10) || 1;
      const id = this.dataset.addId;
      postJSON(window.CART_URLS.add, { product_id: id, variant_code: this.dataset.variantCode || "full", quantity: qty }).then((r) => {
        if (r.ok) {
          updateCartUI(r.body);
          openCart();
        }
      });
    });
  }

  document.querySelectorAll(".pd-thumb").forEach((thumb) =>
    thumb.addEventListener("click", function () {
      document.getElementById("pdMainImg").src = this.dataset.src;
      document.querySelectorAll(".pd-thumb").forEach((t) => t.classList.remove("active"));
      this.classList.add("active");
    })
  );

  document.querySelectorAll(".pd-tab-head").forEach((head) =>
    head.addEventListener("click", function () {
      document.querySelectorAll(".pd-tab-head").forEach((h) => h.classList.remove("active"));
      document.querySelectorAll(".pd-tab-panel").forEach((p) => p.classList.remove("active"));
      this.classList.add("active");
      document.querySelector('.pd-tab-panel[data-panel="' + this.dataset.tab + '"]').classList.add("active");
    })
  );

  /* ---------------------------------------------------------------
     Product detail community votes
  --------------------------------------------------------------- */
  const pdVotesSection = document.querySelector(".pd-votes-section");
  if (pdVotesSection) {
    const voteButtons = pdVotesSection.querySelectorAll(".pd-vote-option");
    const voteStatus = pdVotesSection.querySelector(".pd-vote-status");
    const voteUrl = pdVotesSection.dataset.voteUrl;
    const voteErrorLabel = pdVotesSection.dataset.errorLabel || "Tanlovni saqlab bo'lmadi";

    function setVoteStatus(message, isError) {
      if (!voteStatus) return;
      voteStatus.textContent = message || "";
      voteStatus.classList.toggle("is-error", Boolean(isError));
      voteStatus.classList.toggle("is-visible", Boolean(message));
    }

    voteButtons.forEach((button) => {
      button.addEventListener("click", function () {
        if (this.disabled || !voteUrl) return;
        const group = this.closest(".pd-vote-group");
        const voteType = group ? group.dataset.voteType : "";
        const choice = this.dataset.voteChoice || "";
        if (!voteType || !choice) return;

        voteButtons.forEach((item) => { item.disabled = true; });
        group.classList.add("is-saving");
        setVoteStatus("");

        postJSON(voteUrl, { vote_type: voteType, choice: choice }).then((response) => {
          if (!response.ok || !response.body || !response.body.ok) {
            setVoteStatus(voteErrorLabel, true);
            return;
          }

          const counts = response.body.counts || {};
          group.querySelectorAll(".pd-vote-option").forEach((item) => {
            const itemChoice = item.dataset.voteChoice || "";
            const selected = response.body.selected === itemChoice;
            item.classList.toggle("is-selected", selected);
            item.setAttribute("aria-pressed", selected ? "true" : "false");
            const count = item.querySelector("[data-vote-count]");
            if (count) count.textContent = String(counts[itemChoice] || 0);
          });

          const total = group.querySelector("[data-vote-total]");
          if (total) total.textContent = String(response.body.total || 0);
          setVoteStatus(
            response.body.selected
              ? (pdVotesSection.dataset.savedLabel || "Tanlovingiz saqlandi")
              : (pdVotesSection.dataset.clearedLabel || "Tanlov bekor qilindi")
          );
        }).catch(() => {
          setVoteStatus(voteErrorLabel, true);
        }).finally(() => {
          voteButtons.forEach((item) => { item.disabled = false; });
          group.classList.remove("is-saving");
        });
      });
    });
  }

  /* ---------------------------------------------------------------
     Shared price range visuals
  --------------------------------------------------------------- */
  function initPriceRangeVisual(wrap) {
    const inputs = wrap.querySelectorAll('input[type="range"]');
    const labels = wrap.querySelectorAll(".price-values span");
    if (inputs.length < 2 || labels.length < 2) return;

    const minInput = inputs[0];
    const maxInput = inputs[1];
    const minLimit = parseInt(wrap.dataset.minPrice || minInput.min || "0", 10);
    const maxLimit = parseInt(wrap.dataset.maxPrice || maxInput.max || "0", 10);

    function update() {
      if (parseInt(minInput.value, 10) > parseInt(maxInput.value, 10)) {
        [minInput.value, maxInput.value] = [maxInput.value, minInput.value];
      }
      labels[0].textContent = "$" + minInput.value;
      labels[1].textContent = "$" + maxInput.value;

      const total = Math.max(maxLimit - minLimit, 1);
      const start = ((parseInt(minInput.value, 10) - minLimit) / total) * 100;
      const end = ((parseInt(maxInput.value, 10) - minLimit) / total) * 100;
      wrap.style.setProperty("--range-start", start + "%");
      wrap.style.setProperty("--range-end", end + "%");
    }

    minInput.addEventListener("input", update);
    maxInput.addEventListener("input", update);
    update();
  }

  document.querySelectorAll(".price-range-wrap").forEach(initPriceRangeVisual);

  /* ---------------------------------------------------------------
     SPA Navigation & Assembly Animations
  --------------------------------------------------------------- */
  function scrollToSection(sectionId, genderFilter) {
    const target = document.getElementById(sectionId);
    if (target) {
      const topOffset = target.getBoundingClientRect().top + window.pageYOffset - 75;
      window.scrollTo({ top: topOffset, behavior: "smooth" });

      if (genderFilter) {
        filterHomeCatalog(genderFilter);
      }
    }
  }

  document.querySelectorAll(".nav-link, a[data-section]").forEach((link) => {
    link.addEventListener("click", function (e) {
      const sectionId = this.dataset.section || (this.getAttribute("href") || "").split("#")[1];
      const isHome = document.body.contains(document.getElementById("hero"));

      if (isHome && sectionId && document.getElementById(sectionId)) {
        e.preventDefault();
        const gender = this.dataset.gender;
        scrollToSection(sectionId, gender);

        if (mainNav) mainNav.classList.remove("open");
      }
    });
  });

  /* ---------------------------------------------------------------
     Home Catalog Dynamic AJAX Filtering with Disappear/Assemble Animations
  --------------------------------------------------------------- */
  const homeGrid = document.getElementById("productGrid");
  const homeGenderTabs = document.getElementById("homeGenderTabs");
  const homeFilterForm = document.getElementById("homeFilterForm");

  function filterHomeCatalog(genderValue, extraParams) {
    if (!homeGrid) return;

    const existingCards = homeGrid.querySelectorAll(".product-card");
    existingCards.forEach((card) => card.classList.add("card-disappearing"));

    if (homeGenderTabs && genderValue) {
      homeGenderTabs.querySelectorAll(".tab").forEach((t) => {
        t.classList.toggle("active", t.dataset.gender === genderValue);
      });
    }

    if (homeFilterForm && genderValue) {
      const radio = homeFilterForm.querySelector('input[name="gender"][value="' + genderValue + '"]');
      if (radio) radio.checked = true;
    }

    const params = new URLSearchParams(extraParams || {});
    if (genderValue && genderValue !== "all") {
      params.set("gender", genderValue);
    }
    params.set("home", "1");

    const catalogUrl = (window.CART_URLS && window.CART_URLS.catalog) || "/catalog/";

    setTimeout(() => {
      fetch(catalogUrl + "?" + params.toString(), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((r) => r.json())
        .then((data) => {
          homeGrid.innerHTML = data.html;

          const newCards = homeGrid.querySelectorAll(".product-card");
          newCards.forEach((card, idx) => {
            card.style.setProperty("--delay", (idx * 60) + "ms");
            card.classList.add("card-assembling");
          });

          observeReveals(homeGrid);
        })
        .catch((err) => {
          console.error("Filtering error:", err);
        });
    }, 250);
  }

  if (homeGenderTabs) {
    homeGenderTabs.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        const gender = this.dataset.gender;
        filterHomeCatalog(gender);
      });
    });
  }

  if (homeFilterForm) {
    homeFilterForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const gender = formData.get("gender") || "all";
      const params = {};
      if (formData.get("min_price")) params.min_price = formData.get("min_price");
      if (formData.get("max_price")) params.max_price = formData.get("max_price");
      if (formData.get("concentration")) params.concentration = formData.get("concentration");

      filterHomeCatalog(gender, params);
    });

    homeFilterForm.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.addEventListener("change", function () {
        if (typeof homeFilterForm.requestSubmit === "function") {
          homeFilterForm.requestSubmit();
        } else {
          homeFilterForm.dispatchEvent(new Event("submit", { cancelable: true }));
        }
      });
    });
  }

  /* ---------------------------------------------------------------
     Full Catalog Page AJAX Filters + Infinite Scroll
  --------------------------------------------------------------- */
  const catalogSection = document.querySelector(".catalog-section");
  const productGrid = document.getElementById("productGrid");

  if (productGrid && catalogSection && !document.getElementById("hero")) {
    const gridLoader = document.getElementById("gridLoader");
    const sortSelect = document.getElementById("sortSelect");
    const priceMin = document.getElementById("priceMin");
    const priceMax = document.getElementById("priceMax");
    const priceMinLabel = document.getElementById("priceMinLabel");
    const priceMaxLabel = document.getElementById("priceMaxLabel");
    const priceWrap = document.querySelector(".price-range-wrap");
    const resultCount = document.querySelector(".result-count");
    const resetBtn = document.getElementById("resetFilters");

    let currentParams = new URLSearchParams(window.location.search);
    let loading = false;

    function buildQuery(page) {
      const params = new URLSearchParams(currentParams);
      if (page) params.set("page", page);
      else params.delete("page");
      return params.toString();
    }

    function reloadGrid(pushHistory) {
      const query = buildQuery();
      if (pushHistory) history.replaceState(null, "", "?" + query);

      const existingCards = productGrid.querySelectorAll(".product-card");
      existingCards.forEach((card) => card.classList.add("card-disappearing"));

      setTimeout(() => {
        fetch(window.location.pathname + "?" + query, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
        })
          .then((r) => r.json())
          .then((data) => {
            productGrid.innerHTML = data.html;
            productGrid.dataset.nextPage = data.next_page || "";
            productGrid.dataset.hasNext = data.has_next ? "1" : "0";
            if (resultCount) resultCount.textContent = data.count + " ta mahsulot";

            const newCards = productGrid.querySelectorAll(".product-card");
            newCards.forEach((card, idx) => {
              card.style.setProperty("--delay", (idx * 60) + "ms");
              card.classList.add("card-assembling");
            });

            observeReveals(productGrid);
          });
      }, 200);
    }

    document.querySelectorAll('input[name="gender"]').forEach((input) =>
      input.addEventListener("change", function () {
        if (this.value === "all") currentParams.delete("gender");
        else currentParams.set("gender", this.value);
        document.querySelectorAll(".gender-tabs.compact .tab").forEach((t) => t.classList.remove("active"));
        const tab = document.querySelector('.gender-tabs.compact .tab[data-gender="' + this.value + '"]');
        if (tab) tab.classList.add("active");
        reloadGrid(true);
      })
    );

    document.querySelectorAll(".gender-tabs.compact .tab").forEach((tab) =>
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        const gender = this.dataset.gender;
        if (gender === "all") currentParams.delete("gender");
        else currentParams.set("gender", gender);
        document.querySelectorAll(".gender-tabs.compact .tab").forEach((t) => t.classList.remove("active"));
        this.classList.add("active");
        const radio = document.querySelector('input[name="gender"][value="' + gender + '"]');
        if (radio) radio.checked = true;
        reloadGrid(true);
      })
    );

    document.querySelectorAll('input[name="concentration"]').forEach((input) =>
      input.addEventListener("change", function () {
        if (!this.value) currentParams.delete("concentration");
        else currentParams.set("concentration", this.value);
        reloadGrid(true);
      })
    );

    if (sortSelect) {
      sortSelect.addEventListener("change", function () {
        currentParams.set("sort", this.value);
        reloadGrid(true);
      });
    }

    const minLimit = priceWrap ? parseInt(priceWrap.dataset.minPrice || (priceMin ? priceMin.min : "0"), 10) : 0;
    const maxLimit = priceWrap ? parseInt(priceWrap.dataset.maxPrice || (priceMax ? priceMax.max : "0"), 10) : 0;

    function setInitialPriceValues() {
      if (!priceMin || !priceMax) return;
      const urlMin = parseInt(currentParams.get("min_price") || priceMin.value, 10);
      const urlMax = parseInt(currentParams.get("max_price") || priceMax.value, 10);
      priceMin.value = Math.max(minLimit, Math.min(urlMin, maxLimit));
      priceMax.value = Math.max(minLimit, Math.min(urlMax, maxLimit));
      if (parseInt(priceMin.value, 10) > parseInt(priceMax.value, 10)) {
        priceMin.value = priceMax.value;
      }
    }

    function updatePriceLabels() {
      if (!priceMin || !priceMax) return;
      if (priceMinLabel) priceMinLabel.textContent = "$" + priceMin.value;
      if (priceMaxLabel) priceMaxLabel.textContent = "$" + priceMax.value;
      if (priceWrap) {
        const total = Math.max(maxLimit - minLimit, 1);
        const start = ((parseInt(priceMin.value, 10) - minLimit) / total) * 100;
        const end = ((parseInt(priceMax.value, 10) - minLimit) / total) * 100;
        priceWrap.style.setProperty("--range-start", start + "%");
        priceWrap.style.setProperty("--range-end", end + "%");
      }
    }
    let priceDebounce;
    function onPriceChange() {
      if (parseInt(priceMin.value, 10) > parseInt(priceMax.value, 10)) {
        [priceMin.value, priceMax.value] = [priceMax.value, priceMin.value];
      }
      updatePriceLabels();
      clearTimeout(priceDebounce);
      priceDebounce = setTimeout(() => {
        if (parseInt(priceMin.value, 10) <= minLimit) currentParams.delete("min_price");
        else currentParams.set("min_price", priceMin.value);
        if (parseInt(priceMax.value, 10) >= maxLimit) currentParams.delete("max_price");
        else currentParams.set("max_price", priceMax.value);
        reloadGrid(true);
      }, 400);
    }
    if (priceMin) {
      setInitialPriceValues();
      priceMin.addEventListener("input", onPriceChange);
      priceMax.addEventListener("input", onPriceChange);
      updatePriceLabels();
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        currentParams = new URLSearchParams();
        window.location.href = window.location.pathname;
      });
    }

    /* Infinite scroll */
    if (gridLoader) {
      const scrollSentinel = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting && !loading) {
              const hasNext = productGrid.dataset.hasNext === "1";
              const nextPage = productGrid.dataset.nextPage;
              if (!hasNext || !nextPage) return;
              loading = true;
              gridLoader.style.display = "flex";
              const query = buildQuery(nextPage);
              fetch(window.location.pathname + "?" + query, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
              })
                .then((r) => r.json())
                .then((data) => {
                  productGrid.insertAdjacentHTML("beforeend", data.html);
                  productGrid.dataset.nextPage = data.next_page || "";
                  productGrid.dataset.hasNext = data.has_next ? "1" : "0";
                  observeReveals(productGrid);
                  gridLoader.style.display = "none";
                  loading = false;
                });
            }
          });
        },
        { rootMargin: "300px" }
      );
      scrollSentinel.observe(gridLoader);
    }
  }

  /* ---------------------------------------------------------------
     Product Card Image Slider (hover auto-slide + manual arrows)
  --------------------------------------------------------------- */
  function initCardSliders(root) {
    (root || document).querySelectorAll(".card-slider").forEach(function (slider) {
      if (slider._sliderInit) return;          // prevent double-init
      slider._sliderInit = true;

      const imgs = slider.querySelectorAll(".slider-img");
      const dots = slider.querySelectorAll(".slider-dot");
      const prevBtn = slider.querySelector(".slider-prev");
      const nextBtn = slider.querySelector(".slider-next");
      if (imgs.length < 2) return;             // nothing to slide

      let current = 0;
      let autoTimer = null;
      let pauseTimer = null;
      const interval = parseInt(slider.dataset.interval, 10) || 2000;

      function goTo(idx) {
        imgs[current].classList.remove("active");
        if (dots[current]) dots[current].classList.remove("active");
        current = (idx + imgs.length) % imgs.length;
        imgs[current].classList.add("active");
        if (dots[current]) dots[current].classList.add("active");
      }

      function startAuto() {
        stopAuto();
        autoTimer = setInterval(function () { goTo(current + 1); }, interval);
      }

      function stopAuto() {
        clearInterval(autoTimer);
        autoTimer = null;
      }

      /* Hover: start / stop auto-slide */
      const card = slider.closest(".product-card");
      if (card) {
        card.addEventListener("mouseenter", startAuto);
        card.addEventListener("mouseleave", function () {
          stopAuto();
          clearTimeout(pauseTimer);
        });
      }

      /* Manual arrows — pause auto briefly then resume */
      function manualNav(dir) {
        stopAuto();
        goTo(current + dir);
        clearTimeout(pauseTimer);
        pauseTimer = setTimeout(startAuto, 3000);
      }
      if (prevBtn) prevBtn.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); manualNav(-1); });
      if (nextBtn) nextBtn.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); manualNav(1); });

      /* Dot clicks */
      dots.forEach(function (dot, i) {
        dot.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          stopAuto();
          goTo(i);
          clearTimeout(pauseTimer);
          pauseTimer = setTimeout(startAuto, 3000);
        });
      });
    });
  }

  /* Init sliders on page load */
  initCardSliders();

  /* Re-init sliders whenever new product cards are injected via AJAX
     (covers both home catalog filter and full catalog page). */
  const sliderGrid = document.getElementById("productGrid");
  if (sliderGrid) {
    const gridObserver = new MutationObserver(function () {
      initCardSliders(sliderGrid);
    });
    gridObserver.observe(sliderGrid, { childList: true, subtree: false });
  }

})();

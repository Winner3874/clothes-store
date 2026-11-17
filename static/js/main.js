(() => {
    const formatPrice = (amount) => new Intl.NumberFormat("zh-TW").format(amount);

    const initializeInteractions = () => {
        const checkoutForm = document.querySelector("[data-confirm-checkout]");
        const clearCartForm = document.querySelector("[data-confirm-clear]");

        if (checkoutForm && !checkoutForm.dataset.confirmBound) {
            checkoutForm.dataset.confirmBound = "true";
            checkoutForm.addEventListener("submit", (event) => {
                if (!window.confirm("\u78ba\u5b9a\u8981\u9001\u51fa\u8a02\u55ae\u55ce\uff1f")) event.preventDefault();
            });
        }
        if (clearCartForm && !clearCartForm.dataset.confirmBound) {
            clearCartForm.dataset.confirmBound = "true";
            clearCartForm.addEventListener("submit", (event) => {
                if (!window.confirm("\u78ba\u5b9a\u8981\u6e05\u7a7a\u8cfc\u7269\u8eca\u55ce\uff1f")) event.preventDefault();
            });
        }

        document.querySelectorAll("[data-cart-row]").forEach((row) => {
            const quantityInput = row.querySelector("[data-cart-quantity]");
            if (!quantityInput || quantityInput.dataset.bound) return;
            quantityInput.dataset.bound = "true";

            const updateCartTotals = () => {
                let cartTotal = 0;
                document.querySelectorAll("[data-cart-row]").forEach((cartRow) => {
                    const input = cartRow.querySelector("[data-cart-quantity]");
                    const quantity = Number.parseInt(input?.value, 10);
                    if (!Number.isInteger(quantity) || quantity < 1) return;
                    const lineTotal = Number.parseInt(cartRow.dataset.unitPrice, 10) * quantity;
                    cartRow.querySelector("[data-line-total]").textContent = formatPrice(lineTotal);
                    cartTotal += lineTotal;
                });
                const totalElement = document.querySelector("[data-cart-total]");
                if (totalElement) totalElement.textContent = formatPrice(cartTotal);
            };

            quantityInput.addEventListener("input", updateCartTotals);
            const saveQuantity = () => {
                const quantity = Number.parseInt(quantityInput.value, 10) || 1;
                quantityInput.value = Math.min(99, Math.max(1, quantity));
                updateCartTotals();
                quantityInput.form.requestSubmit();
            };
            quantityInput.addEventListener("change", saveQuantity);
            row.querySelectorAll("[data-quantity-step]").forEach((button) => {
                button.addEventListener("click", () => {
                    const step = Number.parseInt(button.dataset.quantityStep, 10);
                    const quantity = Number.parseInt(quantityInput.value, 10) || 1;
                    quantityInput.value = Math.min(99, Math.max(1, quantity + step));
                    saveQuantity();
                });
            });
        });
    };

    const renderResponse = async (response, { addHistory = true, scrollPosition = null } = {}) => {
        const html = await response.text();
        const nextDocument = new DOMParser().parseFromString(html, "text/html");
        if (!nextDocument.body || response.status >= 500) throw new Error("Page update failed");

        const destination = new URL(response.url || window.location.href, window.location.href);
        if (addHistory) {
            history.replaceState({ ...(history.state || {}), scroll: { x: window.scrollX, y: window.scrollY } }, "");
            const currentURL = new URL(window.location.href);
            if (destination.pathname === currentURL.pathname && destination.search === currentURL.search && destination.hash === currentURL.hash) {
                history.replaceState({ softPage: true, scroll: { x: window.scrollX, y: window.scrollY } }, "", destination.pathname + destination.search + destination.hash);
            } else {
                history.pushState({ softPage: true }, "", destination.pathname + destination.search + destination.hash);
            }
        }

        document.title = nextDocument.title;
        document.body.replaceWith(nextDocument.body);
        if (scrollPosition) window.scrollTo(scrollPosition.x, scrollPosition.y);
        initializeInteractions();
    };

    document.addEventListener("submit", async (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || event.defaultPrevented || form.target === "_blank") return;
        if (form.dataset.allowNavigation === "true") return;
        event.preventDefault();
        const submitter = event.submitter;
        const method = (submitter?.formMethod || form.method || "get").toUpperCase();
        const action = new URL(submitter?.formAction || form.action || window.location.href, window.location.href);
        const formData = new FormData(form);
        if (submitter?.name) formData.append(submitter.name, submitter.value);
        const options = { method, credentials: "same-origin", headers: { "X-Requested-With": "fetch" } };

        if (method === "GET") {
            for (const [key, value] of formData.entries()) {
                if (typeof value === "string") action.searchParams.set(key, value);
            }
        } else {
            options.body = formData;
        }

        const oldScroll = { x: window.scrollX, y: window.scrollY };
        form.querySelectorAll("button[type=submit], input[type=submit]").forEach((button) => { button.disabled = true; });
        try {
            const response = await fetch(action, options);
            if (!response.ok) throw new Error(`Request failed: ${response.status}`);
            await renderResponse(response, { scrollPosition: oldScroll });
        } catch (error) {
            console.error("Could not update the page without reloading:", error);
            form.querySelectorAll("button[type=submit], input[type=submit]").forEach((button) => { button.disabled = false; });
            console.error("Request failed; the page was left in place.");
        }
    });

    window.addEventListener("popstate", async (event) => {
        try {
            const response = await fetch(window.location.href, {
                credentials: "same-origin",
                headers: { "X-Requested-With": "fetch" },
            });
            await renderResponse(response, { addHistory: false, scrollPosition: event.state?.scroll || { x: 0, y: 0 } });
        } catch {
            window.location.reload();
        }
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeInteractions, { once: true });
    } else {
        initializeInteractions();
    }
    history.scrollRestoration = "manual";
})();

(() => {
    const formatPrice = (amount) => new Intl.NumberFormat("zh-TW").format(amount);

    const initializeInteractions = () => {
        document.querySelectorAll("[data-cart-row]").forEach((row) => {
            const quantityInput = row.querySelector("[data-cart-quantity]");
            if (!quantityInput || quantityInput.dataset.bound) return;
            quantityInput.dataset.bound = "true";
            const maxQuantity = Math.max(1, Number.parseInt(quantityInput.max, 10) || 99);

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
            let saveTimer;
            const saveQuantity = () => {
                const quantity = Number.parseInt(quantityInput.value, 10) || 1;
                quantityInput.value = Math.min(maxQuantity, Math.max(1, quantity));
                updateCartTotals();
                clearTimeout(saveTimer);
                saveTimer = setTimeout(() => quantityInput.form.requestSubmit(), 250);
            };
            quantityInput.addEventListener("change", saveQuantity);
            row.querySelectorAll("[data-quantity-step]").forEach((button) => {
                button.addEventListener("click", () => {
                    const step = Number.parseInt(button.dataset.quantityStep, 10);
                    const quantity = Number.parseInt(quantityInput.value, 10) || 1;
                    quantityInput.value = Math.min(maxQuantity, Math.max(1, quantity + step));
                    saveQuantity();
                });
            });
        });
        document.querySelectorAll("[data-gallery-image]").forEach((button) => {
            if (button.dataset.bound) return;
            button.dataset.bound = "true";
            button.addEventListener("click", () => {
                const mainImage = document.querySelector("[data-gallery-main]");
                if (mainImage) mainImage.src = button.dataset.galleryImage;
                document.querySelectorAll("[data-gallery-image]").forEach((thumbnail) => {
                    thumbnail.classList.toggle("active", thumbnail === button);
                });
            });
        });

        document.querySelectorAll("[data-open-product-modal]").forEach((button) => {
            if (button.dataset.bound) return;
            button.dataset.bound = "true";
            button.addEventListener("click", () => {
                const dialog = document.querySelector("[data-product-order-dialog]");
                if (!dialog) return;
                const form = dialog.querySelector("[data-product-order-form]");
                const colorSelect = dialog.querySelector("[data-dialog-colors]");
                const sizeSelect = dialog.querySelector("[data-dialog-sizes]");
                const quantity = dialog.querySelector("[data-dialog-quantity]");
                const stock = Math.max(0, Number.parseInt(button.dataset.productStock, 10) || 0);
                const fill = (select, source) => {
                    select.replaceChildren(...source.split(",").map((value) => value.trim()).filter(Boolean).map((value) => {
                        const option = document.createElement("option");
                        option.value = value;
                        option.textContent = value;
                        return option;
                    }));
                };
                dialog.querySelector("[data-dialog-product-name]").textContent = button.dataset.productName;
                dialog.querySelector("[data-dialog-stock]").textContent = `In stock: ${stock}`;
                form.action = button.dataset.addUrl;
                fill(colorSelect, button.dataset.colorOptions || "Default");
                fill(sizeSelect, button.dataset.sizeOptions || "One size");
                quantity.max = String(Math.max(1, Math.min(stock, 99)));
                quantity.value = "1";
                dialog.showModal();
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
        if (scrollPosition) requestAnimationFrame(() => window.scrollTo(scrollPosition.x, scrollPosition.y));
        initializeInteractions();
    };

    document.addEventListener("submit", async (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || form.target === "_blank" || form.method === "dialog") return;
        if (form.matches("[data-confirm-checkout]") && !window.confirm("\u78ba\u5b9a\u8981\u9001\u51fa\u8a02\u55ae\u55ce\uff1f")) {
            event.preventDefault();
            return;
        }
        if (form.matches("[data-confirm-clear]") && !window.confirm("\u78ba\u5b9a\u8981\u6e05\u7a7a\u8cfc\u7269\u8eca\u55ce\uff1f")) {
            event.preventDefault();
            return;
        }
        event.preventDefault();
        const submitter = event.submitter;
        const submitterMethod = submitter?.hasAttribute("formmethod") ? submitter.formMethod : "";
        const submitterAction = submitter?.hasAttribute("formaction") ? submitter.formAction : "";
        const method = (submitterMethod || form.method || "get").toUpperCase();
        const action = new URL(submitterAction || form.action || window.location.href, window.location.href);
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
            let notice = document.querySelector("[data-request-error]");
            if (!notice) {
                notice = document.createElement("div");
                notice.dataset.requestError = "true";
                notice.setAttribute("role", "alert");
                notice.style.cssText = "position:fixed;right:1rem;bottom:1rem;z-index:2000;max-width:24rem;padding:.75rem 1rem;background:#842029;color:#fff;border-radius:.5rem;box-shadow:0 2px 12px #0003";
                document.body.append(notice);
            }
            notice.textContent = "Request failed. Please try again.";
            notice.style.opacity = "1";
            notice.style.transition = "opacity .4s ease";
            clearTimeout(notice.fadeTimer);
            notice.fadeTimer = setTimeout(() => {
                notice.style.opacity = "0";
                setTimeout(() => notice.remove(), 450);
            }, 3000);
        }
    }, true);

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

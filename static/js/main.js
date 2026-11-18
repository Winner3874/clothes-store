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

    // Keep normal browser form navigation for search, cart, favorites, and checkout.
    // Intercepting every form with fetch made these core actions silently fail when
    // a request was redirected or the response could not be swapped into the page.
    document.addEventListener("submit", (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || form.target === "_blank" || form.method === "dialog") return;
        if (form.matches("[data-product-order-form]")) {
            const scrollField = form.querySelector("[data-scroll-position]");
            if (scrollField) scrollField.value = String(Math.round(window.scrollY));
        }
        if (form.matches("[data-confirm-checkout]") && !window.confirm("\u78ba\u5b9a\u8981\u9001\u51fa\u8a02\u55ae\u55ce\uff1f")) {
            event.preventDefault();
            return;
        }
        if (form.matches("[data-confirm-clear]") && !window.confirm("\u78ba\u5b9a\u8981\u6e05\u7a7a\u8cfc\u7269\u8eca\u55ce\uff1f")) {
            event.preventDefault();
            return;
        }
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeInteractions, { once: true });
    } else {
        initializeInteractions();
    }

    const restoreProductListScroll = () => {
        const match = window.location.hash.match(/^#scroll-y-(\d+)$/);
        if (!match) return;
        window.scrollTo(0, Number.parseInt(match[1], 10));
        history.replaceState(history.state, "", window.location.pathname + window.location.search);
    };
    if (document.readyState === "complete") {
        requestAnimationFrame(restoreProductListScroll);
    } else {
        window.addEventListener("load", restoreProductListScroll, { once: true });
    }
})();

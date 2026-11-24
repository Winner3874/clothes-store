(() => {
    const formatPrice = (amount) => new Intl.NumberFormat("zh-TW").format(amount);

    const initializeInteractions = () => {
        document.querySelectorAll("[data-status-filter]").forEach((select) => {
            if (select.dataset.bound) return;
            select.dataset.bound = "true";
            select.addEventListener("change", () => select.form?.requestSubmit());
        });

        document.querySelectorAll("[data-order-status-form]").forEach((form) => {
            const select = form.querySelector("[data-order-status-input]");
            const notice = form.querySelector("[data-unsaved-status]");
            const saveButton = form.querySelector("[data-save-order-status]");
            if (!select || !notice || !saveButton || form.dataset.bound) return;
            form.dataset.bound = "true";
            const updateDirtyState = () => {
                const changed = select.value !== form.dataset.originalStatus;
                notice.hidden = !changed;
                saveButton.disabled = !changed;
            };
            select.addEventListener("change", updateDirtyState);
            updateDirtyState();
        });

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
        document.querySelectorAll("[data-gallery]").forEach((gallery) => {
            if (gallery.dataset.bound) return;
            gallery.dataset.bound = "true";
            const thumbs = [...document.querySelectorAll("[data-gallery-image]")];
            if (thumbs.length < 2) gallery.querySelectorAll("[data-gallery-step]").forEach((button) => button.hidden = true);
            const show = (index) => {
                if (!thumbs.length) return;
                const selected = (index + thumbs.length) % thumbs.length;
                gallery.dataset.galleryIndex = String(selected);
                const image = gallery.querySelector("[data-gallery-main]");
                if (image) image.src = thumbs[selected].dataset.galleryImage;
                thumbs.forEach((thumb, i) => {
                    thumb.classList.toggle("active", i === selected);
                    if (i === selected) thumb.scrollIntoView({block:"nearest", inline:"nearest", behavior:"smooth"});
                });
            };
            gallery.querySelectorAll("[data-gallery-step]").forEach((button) => button.addEventListener("click", () => show(Number(gallery.dataset.galleryIndex || 0) + Number(button.dataset.galleryStep))));
            thumbs.forEach((button, i) => button.addEventListener("click", () => show(i)));
        });
        document.querySelectorAll("[data-card-gallery]").forEach((gallery) => {
            const photos = gallery.dataset.images.split("|").filter(Boolean);
            let index = 0;
            gallery.querySelectorAll("[data-card-step]").forEach((button) => button.addEventListener("click", (event) => {
                event.preventDefault(); event.stopPropagation();
                index = (index + Number(button.dataset.cardStep) + photos.length) % photos.length;
                gallery.querySelector("[data-card-photo]").src = photos[index];
                gallery.querySelector("[data-card-count]").textContent = `${index + 1} / ${photos.length}`;
            }));
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
                dialog.querySelector("[data-dialog-stock]").textContent = `\u5269\u9918\u6578\u91CF\uFF1A${stock}`;
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
        if (form.matches(".favorite-form, .favorite-toggle")) {
            event.preventDefault();
            const button = form.querySelector("button[type='submit']");
            if (!button || form.dataset.saving === "true") return;
            form.dataset.saving = "true";
            button.disabled = true;
            fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin"
            }).then((response) => {
                if (!response.ok) throw new Error("Favorite update failed");
                return response.json();
            }).then(({ added }) => {
                if (form.matches(".favorite-form")) {
                    const label = added ? "取消收藏" : "收藏";
                    button.textContent = added ? "♥" : "♡";
                    button.setAttribute("aria-label", label);
                    button.title = label;
                } else {
                    button.textContent = added ? "♥ 取消收藏" : "♡ 加入收藏";
                }
            }).catch(() => window.location.reload()).finally(() => {
                form.dataset.saving = "false";
                button.disabled = false;
            });
            return;
        }
        if (form.matches("[data-product-order-form]")) {
            const scrollField = form.querySelector("[data-scroll-position]");
            if (scrollField) scrollField.value = String(Math.round(window.scrollY));
        }
        if (form.matches(".favorite-form")) {
            const scrollField = form.querySelector("[data-favorite-scroll]");
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

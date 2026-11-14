document.addEventListener("DOMContentLoaded", () => {
    const checkoutForm = document.querySelector("[data-confirm-checkout]");
    const clearCartForm = document.querySelector("[data-confirm-clear]");

    const confirmForm = (form, message) => {
        if (form) {
            form.addEventListener("submit", (event) => {
                if (!window.confirm(message)) {
                    event.preventDefault();
                }
            });
        }
    };

    confirmForm(checkoutForm, "確定要送出訂單嗎？送出後購物車會清空。");
    confirmForm(clearCartForm, "確定要清空購物車嗎？");

    const formatPrice = (amount) => new Intl.NumberFormat("zh-TW").format(amount);

    const updateCartTotals = () => {
        let cartTotal = 0;

        document.querySelectorAll("[data-cart-row]").forEach((row) => {
            const quantityInput = row.querySelector("[data-cart-quantity]");
            const quantity = Number.parseInt(quantityInput.value, 10);

            if (!Number.isInteger(quantity) || quantity < 1) {
                return;
            }

            const lineTotal = Number.parseInt(row.dataset.unitPrice, 10) * quantity;
            row.querySelector("[data-line-total]").textContent = formatPrice(lineTotal);
            cartTotal += lineTotal;
        });

        const totalElement = document.querySelector("[data-cart-total]");
        if (totalElement) {
            totalElement.textContent = formatPrice(cartTotal);
        }
    };

    document.querySelectorAll("[data-cart-row]").forEach((row) => {
        const quantityInput = row.querySelector("[data-cart-quantity]");
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
});

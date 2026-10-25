// 放置前端互動程式。目前只對示範結帳加上確認提示。
document.addEventListener("DOMContentLoaded", () => {
    const checkoutForm = document.querySelector("[data-confirm-checkout]");

    if (checkoutForm) {
        checkoutForm.addEventListener("submit", (event) => {
            const confirmed = window.confirm(
                "這是示範結帳，不會進行實際付款。要繼續嗎？"
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    }
});

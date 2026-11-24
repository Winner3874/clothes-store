STYLESHEET = r'''
/* ========================================
   StyleLab Store — Minimalist Black & White
   ======================================== */

:root {
    --color-bg: #fdfdfd;
    --color-surface: #ffffff;
    --color-text: #111111;
    --color-muted: #666666;
    --color-primary: #111111;
    --color-primary-hover: #333333;
    --color-border: #e0e0e0;
    --radius-card: 4px; /* 極微小的圓角 */
    --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.04);
    --shadow-hover: 0 10px 30px rgba(0, 0, 0, 0.08);
}

/* ---------- 基本設定 ---------- */

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--color-bg);
    color: var(--color-text);
    font-family:
        "Noto Sans TC",
        "PingFang TC",
        "Microsoft JhengHei",
        sans-serif;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}

::selection {
    background: rgba(0, 0, 0, 0.1);
}

/* ---------- 導覽列（固定在最上方且稍微透明） ---------- */

.navbar,
.navbar.navbar-dark.bg-dark {
    position: sticky !important;
    top: 0;
    z-index: 1000;
    background: rgba(255, 255, 255, 0.85) !important; /* 一點點透明 */
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--color-border);
    padding: 16px 0;
}

.navbar .navbar-brand {
    color: var(--color-text) !important;
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: -0.4px;
}

.navbar .navbar-brand:hover {
    color: var(--color-muted) !important;
}

/* ---------- 頁面標題 ---------- */

main.container {
    padding-top: 40px;
}

section > h1 {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 26px !important;
    color: var(--color-text);
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: 800;
    letter-spacing: -0.8px;
}

section > h1::before {
    width: 4px;
    height: 24px;
    border-radius: 2px;
    background: var(--color-text);
    content: "";
}

/* ---------- 商品卡片 ---------- */

.product-card {
    overflow: hidden;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card); /* 微小圓角 */
    background: var(--color-surface);
    box-shadow: var(--shadow-card);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        border-color 0.2s ease;
}

.product-card:hover {
    transform: translateY(-4px);
    border-color: #999999;
    box-shadow: var(--shadow-hover);
}

.product-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 190px;
    margin: 12px 12px 0;
    border-radius: 2px;
    background: #f4f4f4;
    font-size: 4.5rem;
    transition: transform 0.2s ease;
}

.product-card:hover .product-icon {
    transform: scale(1.01);
}

.product-detail-card {
    max-width: 760px;
    overflow: hidden;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    background: var(--color-surface);
    box-shadow: var(--shadow-card);
}

.auth-card {
    max-width: 480px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    box-shadow: var(--shadow-card);
}

.product-detail-icon {
    display: grid;
    min-height: 280px;
    place-items: center;
    background: #f4f4f4;
    font-size: 7rem;
}

.product-icon:focus-visible,
.product-card a:focus-visible {
    outline: 3px solid #555;
    outline-offset: 3px;
}

.product-card .card-body {
    padding: 20px;
}

.product-card .card-title {
    margin-bottom: 8px;
    color: var(--color-text);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.3px;
}

.product-card .card-text {
    margin-bottom: 20px;
    color: var(--color-muted) !important;
    font-size: 0.92rem;
    line-height: 1.6;
}

.product-card .text-danger {
    color: var(--color-text) !important;
    font-size: 1.2rem !important;
    font-weight: 800;
    white-space: nowrap;
}

/* ---------- 按鈕 ---------- */

.btn {
    border-radius: var(--radius-card); /* 微小圓角 */
    font-weight: 600;
    transition:
        transform 0.15s ease,
        background-color 0.15s ease,
        border-color 0.15s ease;
}

.btn:active {
    transform: scale(0.98);
}

.btn-primary {
    border-color: #111111;
    background: #111111;
    color: #ffffff;
}

.btn-primary:hover,
.btn-primary:focus-visible {
    border-color: #333333;
    background: #333333;
    color: #ffffff;
}

.btn-success {
    border-color: #111111;
    background: #111111;
    color: #ffffff;
}

.btn-success:hover {
    border-color: #333333;
    background: #333333;
}

.btn-outline-danger {
    border-color: #cccccc;
    color: #111111;
}

.btn-outline-danger:hover {
    border-color: #111111;
    background: #111111;
    color: #ffffff;
}

.product-card .btn {
    padding: 10px 14px;
    font-size: 0.88rem;
}

/* ---------- 購物車 ---------- */

.cart-card {
    position: sticky;
    top: 84px; /* 配合上方固定導覽列的高度留白 */
    overflow: hidden;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    background: var(--color-surface);
    box-shadow: var(--shadow-card) !important;
}

.cart-card .card-header {
    padding: 18px 20px;
    border-bottom: 1px solid var(--color-border);
    background: #111111 !important;
    color: #ffffff;
}

.cart-card .card-header h2 {
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0;
}

.cart-card .card-body {
    padding: 20px;
}

.cart-card .list-group-item {
    padding-top: 14px;
    padding-bottom: 14px;
    border-color: var(--color-border);
    background: transparent;
}

.cart-card .list-group-item h3 {
    color: var(--color-text);
    font-weight: 700;
}

.cart-card .list-group-item small {
    display: inline-block;
    margin-top: 4px;
    color: var(--color-muted) !important;
}

.cart-line h3 {
    flex: 1;
    line-height: 1.4;
}

.quantity-form {
    display: flex;
    align-items: center;
    gap: 6px;
}

.quantity-form input {
    width: 56px;
    padding: 4px;
    text-align: center;
    appearance: textfield;
    -moz-appearance: textfield;
}

.quantity-form input::-webkit-inner-spin-button,
.quantity-form input::-webkit-outer-spin-button {
    margin: 0;
    -webkit-appearance: none;
}

.quantity-step {
    display: inline-grid;
    width: 28px;
    height: 30px;
    place-items: center;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    background: #fff;
    color: var(--color-text);
    line-height: 1;
}

.quantity-step:hover {
    border-color: var(--color-text);
}

.cart-card .text-success {
    color: #111111 !important;
}

.cart-card .text-muted {
    color: var(--color-muted) !important;
}

.cart-card .btn {
    padding: 10px 14px;
}

/* ---------- 空購物車與提示文字 ---------- */

.cart-card .text-center {
    padding: 20px 0;
}

.cart-card p.small {
    font-size: 0.78rem;
    line-height: 1.6;
}

/* ---------- 結帳示範頁 ---------- */

.success-card {
    max-width: 560px;
    padding: 40px !important;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    background: var(--color-surface);
    box-shadow: var(--shadow-hover);
}

.success-card .display-4 {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    margin: 0 auto;
    border-radius: var(--radius-card);
    background: #f4f4f4;
    font-size: 2.5rem;
}

.success-card h1 {
    font-weight: 800;
}

.success-card p {
    color: var(--color-muted);
}

/* ---------- 響應式版面 ---------- */

@media (max-width: 991.98px) {
    .cart-card {
        position: static;
    }
}

@media (max-width: 575.98px) {
    .navbar {
        padding: 12px 0;
    }

    .navbar .navbar-brand {
        font-size: 1.05rem;
    }

    main.container {
        padding-top: 20px;
    }

    section > h1 {
        margin-bottom: 18px !important;
    }

    .product-icon {
        min-height: 155px;
        font-size: 3.8rem;
    }

    .product-card .card-body {
        padding: 16px;
    }

    .cart-card .card-body {
        padding: 16px;
    }

    .success-card {
        padding: 24px 18px !important;
    }
}

/* ---------- 尊重減少動畫的系統設定 ---------- */

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ---------- StyleLab warm editorial storefront ---------- */
:root {
    --color-bg: #f7f5ef;
    --color-surface: #fffefa;
    --color-text: #263f38;
    --color-muted: #858981;
    --color-primary: #294e43;
    --color-primary-hover: #1e3e35;
    --color-border: #e9e7df;
    --radius-card: 18px;
    --shadow-card: 0 8px 28px rgba(44, 57, 48, .055);
    --shadow-hover: 0 14px 34px rgba(44, 57, 48, .12);
}

body.storefront { background: #f7f5ef !important; color: #293e37; }
.store-nav, .store-nav.navbar.navbar-dark.bg-dark { position: sticky !important; top: 0; z-index: 1000; padding: 13px 0; background: rgba(250,249,245,.94) !important; border-bottom: 1px solid #e9e7df; backdrop-filter: blur(14px); }
.store-nav .container { max-width: 1180px; }
.store-nav .navbar-brand { display:flex; align-items:center; gap:10px; color:#294e43 !important; font-size:1.08rem; font-weight:750; letter-spacing:.02em; }
.brand-mark { display:grid; width:30px; height:30px; place-items:center; border-radius:50%; background:#294e43; color:#fffefa; font-family:Georgia,serif; font-size:17px; }
.nav-actions { gap:clamp(10px,2vw,26px) !important; }
.store-nav .nav-link,.nav-text-button { color:#53645b; font-size:.83rem; }
.store-nav .nav-link:hover,.nav-text-button:hover { color:#294e43; }
.nav-text-button { padding:0; border:0; background:transparent; }
.nav-join { color:#294e43; text-decoration:none; font-size:.83rem; }
.bag-link { padding:8px 13px; border:1px solid #dfe3da; border-radius:999px; color:#294e43; text-decoration:none; font-size:.8rem; }
.bag-link:hover { background:#e9eee8; color:#294e43; }
.store-main { max-width:1180px; padding-top:48px; }
.store-hero { padding:20px 0 29px; }
.eyebrow { margin:0 0 10px; color:#7b897e; font-size:.67rem; font-weight:700; letter-spacing:.15em; }
.store-hero h1 { margin:0; color:#28443b; font-family:Georgia,"Noto Serif TC",serif; font-size:clamp(2rem,4.4vw,3.3rem); font-weight:500; letter-spacing:-.045em; line-height:1.22; }
.mobile-break { display:none; }
.hero-copy { margin:14px 0 0; color:#82877f; font-size:.94rem; }
.store-search { display:flex; align-items:center; gap:12px; max-width:680px; min-height:54px; margin:0 0 20px; padding:5px 7px 5px 17px; border:1px solid #e8e6de; border-radius:15px; background:#fffefa; box-shadow:0 3px 12px #3c483b0a; }
.store-search>span { color:#557267; font-size:1.45rem; line-height:1; }
.store-search input { flex:1; min-width:0; padding:9px 0; border:0; outline:0; background:transparent; color:#293e37; font-size:.88rem; }
.store-search input::placeholder { color:#a0a39c; }
.store-search button { padding:9px 16px; border:0; border-radius:10px; background:#edf1eb; color:#294e43; font-size:.8rem; font-weight:650; }
.store-search button:hover { background:#dfe8df; }
.category-pills { display:flex; flex-wrap:wrap; gap:9px; margin:0 0 42px; }
.category-pill { padding:8px 17px; border:1px solid #e6e4dc; border-radius:999px; background:#faf9f5; color:#68756d; font-size:.8rem; text-decoration:none; transition:all .18s ease; }
.category-pill:hover { border-color:#bfcfc4; color:#294e43; }
.category-pill.active { border-color:#294e43; background:#294e43; color:#fffefa; }
.catalog-heading { display:flex; align-items:end; justify-content:space-between; margin-bottom:18px; }
.catalog-heading .eyebrow { margin-bottom:5px; }
.catalog-heading h2 { margin:0; color:#29443b; font-family:Georgia,"Noto Serif TC",serif; font-size:1.65rem; font-weight:500; }
.catalog-heading>span { padding-bottom:3px; color:#848981; font-size:.78rem; }
.catalog-layout { display:grid; grid-template-columns:minmax(0,1fr) 300px; align-items:start; gap:30px; }
.product-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px 20px; }
.product-card { position:relative; overflow:hidden; min-width:0; border:0; border-radius:18px; background:transparent; box-shadow:none; transition:transform .2s ease; }
.product-card:hover { transform:translateY(-3px); border-color:transparent; box-shadow:none; }
.product-icon { position:relative; display:grid; min-height:0; aspect-ratio:1.08/1; margin:0; overflow:hidden; place-items:center; border-radius:17px; background:radial-gradient(ellipse at 50% 86%,#d8c9ad 0,#e8dfd0 35%,#f0ece3 76%); color:#5d705f; text-decoration:none; }
.product-card:nth-child(4n+2) .product-icon { background:radial-gradient(ellipse at 50% 85%,#c4b18e 0,#ded2b9 42%,#ece8dd 80%); }
.product-card:nth-child(4n+3) .product-icon { background:radial-gradient(ellipse at 50% 87%,#d3b995 0,#eadac1 40%,#f0ebe1 82%); }
.product-card:nth-child(4n+4) .product-icon { background:radial-gradient(ellipse at 50% 86%,#cbb59d 0,#e2d1be 42%,#efe8dc 83%); }
.product-icon span { display:grid; width:100%; height:100%; place-items:center; font-size:clamp(5rem,11vw,9rem); filter:drop-shadow(0 13px 11px #4850431e); transition:transform .35s ease; }
.product-card:hover .product-icon span { transform:scale(1.06) rotate(-2deg); }
.product-icon i { position:absolute; right:11px; bottom:11px; left:11px; padding:8px; border:1px solid #ffffff88; border-radius:10px; background:#fffefa9c; color:#334c40; font-size:.7rem; font-style:normal; text-align:center; opacity:0; transform:translateY(5px); transition:all .2s ease; }
.product-card:hover .product-icon i,.product-icon:focus-visible i { opacity:1; transform:translateY(0); }
.favorite-form { position:absolute; z-index:2; top:12px; right:12px; }
.favorite-form button { display:grid; width:36px; height:36px; place-items:center; border:1px solid #ffffffa8; border-radius:50%; background:#fffefaed; color:#31564a; font-size:1.25rem; line-height:1; box-shadow:0 2px 8px #263f3814; }
.favorite-form button:hover { background:#294e43; color:white; }
.product-card .card-body { padding:13px 2px 0; }
.product-category { display:block; margin-bottom:4px; color:#858a80; font-size:.7rem; }
.product-title-row { display:flex; align-items:baseline; justify-content:space-between; gap:8px; }
.product-title-row h3 { margin:0; font-size:1rem; font-weight:650; letter-spacing:.005em; }
.product-title-row h3 a { color:#29443b; text-decoration:none; }
.product-title-row strong { flex:none; color:#334c41; font-size:.91rem; font-weight:650; }
.product-description { min-height:1.4em; margin:4px 0 12px; overflow:hidden; color:#898d85; font-size:.76rem; text-overflow:ellipsis; white-space:nowrap; }
.add-button { display:flex; width:100%; align-items:center; justify-content:space-between; padding:10px 12px; border:1px solid #e4e7df; border-radius:11px; background:#fffefa88; color:#315548; font-size:.78rem; font-weight:650; transition:all .18s ease; }
.add-button:hover { border-color:#294e43; background:#294e43; color:#fffefa; }
.add-button span { font-size:1rem; }
.cart-card { position:sticky; top:86px; overflow:hidden; padding:22px 19px 15px; border:1px solid #e8e7df; border-radius:17px; background:#fffefa; box-shadow:0 6px 22px #3443370b !important; }
.cart-heading { display:flex; align-items:center; justify-content:space-between; padding-bottom:17px; border-bottom:1px solid #efeee8; }
.cart-heading .eyebrow { margin-bottom:4px; font-size:.6rem; }
.cart-heading h2 { margin:0; color:#29443b; font-size:1.08rem; font-weight:650; }
.cart-heading h2 span { display:inline-grid; min-width:21px; height:21px; margin-left:4px; place-items:center; border-radius:50%; background:#e8eee7; color:#365c4d; font-size:.68rem; vertical-align:2px; }
.cart-flower { color:#9baf9d; font-size:1.35rem; }
.cart-list { margin:0; padding:0; list-style:none; }
.cart-line { padding:16px 0; border-bottom:1px solid #efeee8; }
.cart-line-top,.cart-line-bottom { display:flex; align-items:center; justify-content:space-between; gap:8px; }
.cart-line h3 { margin:0 0 4px; color:#354940; font-size:.83rem; font-weight:650; }
.cart-line small { color:#96998f; font-size:.73rem; }
.cart-line-top>strong { color:#354940; font-size:.77rem; font-weight:650; white-space:nowrap; }
.cart-line-bottom { margin-top:10px; }
.quantity-form { display:flex; align-items:center; gap:7px; }
.quantity-form input { width:32px; padding:3px 0; border:0; background:transparent; color:#354940; font-size:.8rem; text-align:center; appearance:textfield; -moz-appearance:textfield; }
.quantity-form input::-webkit-inner-spin-button,.quantity-form input::-webkit-outer-spin-button { margin:0; -webkit-appearance:none; }
.quantity-step { display:grid; width:25px; height:25px; place-items:center; border:1px solid #e4e7df; border-radius:50%; background:#fffefa; color:#456456; line-height:1; }
.quantity-step:hover { border-color:#294e43; }
.remove-button,.clear-button { padding:0; border:0; background:none; color:#999a91; font-size:.72rem; }
.remove-button:hover,.clear-button:hover { color:#905c4a; }
.cart-total { display:flex; justify-content:space-between; margin:18px 0 14px; color:#777e75; font-size:.82rem; }
.cart-total strong { color:#29443b; font-size:.98rem; }
.checkout-button { display:flex; width:100%; align-items:center; justify-content:space-between; padding:13px 16px; border:0; border-radius:11px; background:#294e43; color:#fffefa; font-size:.82rem; font-weight:650; transition:background .18s ease; }
.checkout-button:hover { background:#1e3e35; color:#fffefa; }
.checkout-button span { font-size:1.1rem; }
.cart-card form .checkout-button { margin:0; }
.clear-button { display:block; margin:12px auto 0; }
.cart-empty { padding:27px 0 21px; text-align:center; }
.cart-empty>span { color:#91a394; font-size:1.7rem; }
.cart-empty p { margin:6px 0 4px; color:#41574b; font-size:.86rem; font-weight:600; }
.cart-empty small { color:#93968d; font-size:.71rem; }
.cart-note { margin:17px -19px -15px; padding:12px 10px; background:#f4f5ef; color:#7c897d; font-size:.68rem; text-align:center; }
.empty-products { padding:54px 20px; border:1px dashed #d8ddd3; border-radius:16px; background:#fbfaf6; text-align:center; }
.empty-products>span { color:#789083; font-size:2rem; }
.empty-products h3 { margin:10px 0 7px; color:#354d42; font-size:1.1rem; }
.empty-products p { color:#858981; font-size:.85rem; }
.empty-products a,.continue-link { color:#315548; font-size:.82rem; text-decoration:none; }
.empty-products a:hover,.continue-link:hover { text-decoration:underline; }
.store-footer { display:flex; justify-content:space-between; margin-top:55px; padding:19px 0 25px; border-top:1px solid #e6e5dd; color:#8a8e85; font-size:.75rem; }
.store-footer span:first-child { color:#536b5f; font-weight:700; letter-spacing:.06em; }
.detail-main { max-width:1060px; padding-top:28px; }
.back-link { display:inline-block; margin:0 0 20px; color:#65776a; font-size:.8rem; text-decoration:none; }
.back-link:hover { color:#294e43; }
.detail-layout { display:grid; grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr); overflow:hidden; border:1px solid #e8e6dd; border-radius:22px; background:#fffefa; box-shadow:0 12px 38px #3443370d; }
.detail-art { position:relative; display:grid; min-height:540px; overflow:hidden; place-items:center; background:radial-gradient(ellipse at 51% 72%,#d4c2a3 0,#e4d8c3 36%,#f0ece3 73%); }
.detail-art::after { position:absolute; right:0; bottom:0; left:0; height:29%; background:linear-gradient(0deg,#cdbb9e55,transparent); content:""; }
.detail-badge { position:absolute; z-index:1; top:22px; left:22px; padding:8px 12px; border:1px solid #fffefaad; border-radius:999px; background:#fffefaaf; color:#4c6354; font-size:.63rem; font-weight:700; letter-spacing:.08em; }
.detail-product-icon { position:relative; z-index:1; display:grid; width:80%; height:80%; place-items:center; color:#5b705e; font-size:clamp(9rem,19vw,15rem); filter:drop-shadow(0 20px 18px #34433726); }
.detail-art-caption { position:absolute; z-index:1; right:22px; bottom:18px; color:#657165; font-size:.62rem; letter-spacing:.16em; }
.detail-copy { display:flex; flex-direction:column; justify-content:center; padding:clamp(28px,5vw,58px); }
.detail-copy>.eyebrow { font-size:.67rem; }
.detail-title-row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.detail-title-row h1 { margin:0; color:#29443b; font-family:Georgia,"Noto Serif TC",serif; font-size:clamp(1.8rem,3.2vw,2.7rem); font-weight:500; letter-spacing:-.035em; }
.detail-title-row>strong { flex:none; color:#304d41; font-size:1.28rem; font-weight:550; }
.detail-rating { margin-top:11px; color:#527262; font-size:.88rem; letter-spacing:.09em; }
.detail-rating small { color:#8b9088; font-size:.71rem; letter-spacing:0; }
.detail-description { margin:23px 0 25px; color:#777e75; font-size:.88rem; line-height:1.9; }
.detail-note { display:flex; align-items:center; gap:12px; padding:15px 0; border-top:1px solid #eeede6; border-bottom:1px solid #eeede6; }
.detail-note>span { display:grid; width:36px; height:36px; place-items:center; border-radius:50%; background:#edf1eb; color:#466c5a; }
.detail-note strong,.detail-note small { display:block; }
.detail-note strong { color:#3b5145; font-size:.79rem; }
.detail-note small { margin-top:3px; color:#93968d; font-size:.7rem; }
.detail-perks { display:flex; justify-content:space-between; gap:7px; padding:17px 0 25px; color:#66776b; font-size:.67rem; }
.detail-actions { display:grid; gap:10px; }
.detail-actions form .checkout-button { padding:15px 17px; }
.detail-favorite { display:block; width:100%; padding:12px; border:1px solid #e4e7df; border-radius:11px; background:transparent; color:#496457; font-size:.8rem; text-align:center; text-decoration:none; }
.detail-favorite:hover { border-color:#afc0b3; background:#f5f7f1; color:#294e43; }
.continue-link { align-self:center; margin-top:19px; }

@media (max-width: 991.98px) {
    .store-main { padding-top:35px; }
    .catalog-layout { grid-template-columns:minmax(0,1fr) 270px; gap:20px; }
    .product-grid { gap:20px 14px; }
    .cart-card { top:78px; }
    .detail-art { min-height:470px; }
    .detail-copy { padding:32px; }
}
@media (max-width: 767.98px) {
    .store-main { padding-top:25px; }
    .store-hero { padding:15px 0 21px; }
    .store-hero h1 { font-size:2.3rem; }
    .mobile-break { display:block; }
    .hero-copy { max-width:340px; font-size:.83rem; }
    .category-pills { gap:7px; margin-bottom:30px; }
    .category-pill { padding:7px 13px; font-size:.75rem; }
    .catalog-layout { grid-template-columns:1fr; gap:28px; }
    .product-grid { gap:20px 13px; }
    .product-icon { aspect-ratio:.96/1; border-radius:14px; }
    .product-icon span { font-size:clamp(4.5rem,18vw,7rem); }
    .product-icon i { display:none; }
    .product-card .card-body { padding-top:10px; }
    .product-title-row { align-items:flex-start; }
    .product-title-row h3 { font-size:.88rem; }
    .product-title-row strong { font-size:.79rem; }
    .product-description { margin-bottom:9px; font-size:.68rem; }
    .add-button { padding:9px 10px; font-size:.72rem; }
    .favorite-form { top:9px; right:9px; }
    .favorite-form button { width:32px; height:32px; }
    .cart-card { position:static; }
    .detail-main { padding-top:20px; }
    .detail-layout { grid-template-columns:1fr; border-radius:17px; }
    .detail-art { min-height:0; aspect-ratio:1.1/1; }
    .detail-product-icon { font-size:clamp(8rem,38vw,13rem); }
    .detail-copy { padding:28px 23px; }
    .detail-title-row h1 { font-size:2rem; }
    .detail-title-row>strong { font-size:1.1rem; }
    .store-footer { margin-top:35px; }
}
@media (max-width: 380px) {
    .store-nav .container { padding-right:14px; padding-left:14px; }
    .store-nav .navbar-brand { gap:6px; font-size:.96rem; }
    .nav-actions { gap:9px !important; }
    .bag-link { padding:7px 9px; font-size:.72rem; }
    .product-title-row { flex-wrap:wrap; gap:1px 6px; }
    .product-title-row h3 { width:100%; }
    .detail-perks { font-size:.59rem; }
}

/* Storefront refinement: familiar, practical retail catalog styling */
body.storefront { background:#f2f3f5 !important; color:#333; }
.store-nav,.store-nav.navbar.navbar-dark.bg-dark { padding:10px 0; background:#fff !important; border-bottom:1px solid #e4e5e7; }
.store-nav .navbar-brand { color:#2c3540 !important; font-size:1.05rem; font-weight:750; }
.brand-mark { width:28px; height:28px; border-radius:6px; background:#78664e; font-family:inherit; font-size:14px; font-weight:700; }
.store-nav .nav-link,.nav-text-button,.nav-join { color:#535b63; font-size:.82rem; }
.nav-login { padding:8px 13px; border:1px solid #75664e; border-radius:6px; background:#75664e; color:#fffefa; font-size:.8rem; text-decoration:none; }
.nav-login:hover { border-color:#62543f; background:#62543f; color:#fffefa; }
.nav-join { text-decoration:none; }
.nav-join:hover { color:#62543f; text-decoration:underline; }
.desktop-account-links { display:flex; align-items:center; gap:clamp(10px,2vw,26px); }
.mobile-account { display:none; position:relative; }
.mobile-account summary { padding:7px 9px; border:1px solid #dedfe2; border-radius:6px; color:#535b63; cursor:pointer; font-size:.75rem; list-style:none; white-space:nowrap; }
.mobile-account summary::-webkit-details-marker { display:none; }
.mobile-account[open] .mobile-account-menu { position:absolute; z-index:1200; top:calc(100% + 8px); right:0; display:grid; min-width:148px; padding:6px; border:1px solid #e1e2e4; border-radius:8px; background:#fff; box-shadow:0 7px 20px #20252a20; }
.mobile-account-menu a { padding:10px; border-radius:5px; color:#434b50; font-size:.8rem; text-decoration:none; }
.mobile-account-menu a:hover { background:#f3f1ec; color:#62543f; }
.bag-link { border-color:#dedfe2; border-radius:7px; background:#fff; color:#3c434a; }
.bag-link:hover { background:#f2ede3; color:#66543d; }
.store-main { padding-top:24px; }
.store-hero { padding:15px 0 18px; }
.store-hero .eyebrow { margin-bottom:6px; color:#8b7d68; font-size:.62rem; letter-spacing:.13em; }
.store-hero h1 { color:#343a40; font-family:inherit; font-size:clamp(1.65rem,3.5vw,2.35rem); font-weight:700; letter-spacing:-.04em; line-height:1.28; }
.hero-copy { margin-top:7px; color:#777d83; font-size:.84rem; }
.store-search { max-width:none; min-height:47px; margin-bottom:14px; padding:4px 5px 4px 13px; border:1px solid #dedfe2; border-radius:8px; background:#fff; box-shadow:none; }
.store-search>span { color:#70777e; font-size:1.25rem; }
.store-search input { font-size:.83rem; }
.store-search button { padding:9px 17px; border-radius:6px; background:#e9e1d2; color:#514936; font-size:.77rem; }
.store-search button:hover { background:#ded3bf; }
.category-pills { gap:8px; margin-bottom:22px; padding-bottom:12px; border-bottom:1px solid #e0e1e3; }
.category-pill { padding:7px 14px; border-color:#dedfe2; border-radius:7px; background:#fff; color:#5f656b; font-size:.76rem; }
.category-pill:hover { border-color:#b8aa92; color:#65563f; }
.category-pill.active { border-color:#75664e; background:#75664e; color:#fffefa; }
.catalog-heading { align-items:center; margin-bottom:12px; }
.catalog-heading .eyebrow { margin-bottom:3px; color:#858a90; font-size:.58rem; }
.catalog-heading h2 { color:#333a40; font-family:inherit; font-size:1.27rem; font-weight:700; }
.catalog-heading>span { color:#777e84; font-size:.72rem; }
.catalog-layout { grid-template-columns:minmax(0,1fr) 285px; gap:20px; }
.product-grid { gap:15px; }
.product-card,.product-card:hover { overflow:hidden; border:1px solid #e4e5e7; border-radius:9px; background:#fff; box-shadow:0 2px 7px rgba(25,34,42,.045); transform:none; transition:box-shadow .18s ease,border-color .18s ease; }
.product-card:hover { border-color:#d6c2cc; box-shadow:0 5px 15px rgba(25,34,42,.09); }
.product-icon,.product-card:nth-child(4n+2) .product-icon,.product-card:nth-child(4n+3) .product-icon,.product-card:nth-child(4n+4) .product-icon { aspect-ratio:1.18/1; border-radius:0; background:#fff; }
.product-icon span { font-size:clamp(4.7rem,9vw,7rem); filter:drop-shadow(0 7px 7px #20252a19); }
.product-icon i { display:none; }
.favorite-form { top:9px; right:9px; }
.favorite-form button { width:31px; height:31px; border:1px solid #e4e4e4; color:#666; box-shadow:none; }
.favorite-form button:hover { border-color:#75664e; background:#75664e; color:white; }
.product-card .card-body { padding:11px 12px 13px; }
.product-category { margin-bottom:3px; color:#898e93; font-size:.65rem; }
.product-title-row { align-items:flex-start; }
.product-title-row h3 { font-size:.9rem; line-height:1.4; }
.product-title-row h3 a { color:#343a40; }
.product-title-row strong { color:#756044; font-size:.88rem; font-weight:750; }
.product-description { min-height:0; margin:5px 0 10px; color:#84898e; font-size:.7rem; }
.add-button { padding:9px 10px; border-color:#e2e3e5; border-radius:6px; background:#fff; color:#555d64; font-size:.73rem; }
.add-button:hover { border-color:#75664e; background:#75664e; color:white; }
.cart-card { top:78px; padding:17px 15px 13px; border-color:#e1e2e4; border-radius:9px; box-shadow:0 2px 8px rgba(25,34,42,.045) !important; }
.cart-heading { padding-bottom:13px; }
.cart-heading .eyebrow { color:#888e93; }
.cart-heading h2 { color:#343a40; font-size:1rem; }
.cart-heading h2 span { border-radius:5px; background:#f0eadf; color:#67583f; }
.cart-flower { color:#938269; }
.cart-line { border-color:#ececee; }
.cart-line h3,.cart-line-top>strong { color:#42484d; }
.quantity-step { border-radius:5px; }
.cart-total strong { color:#756044; }
.checkout-button { border-radius:6px; background:#75664e; }
.checkout-button:hover { background:#62543f; }
.cart-note { background:#f6f6f7; color:#777e84; }
.cart-empty>span { color:#938269; }
.cart-empty p { color:#454c51; }
.empty-products { border-radius:9px; background:#fff; }
.empty-products h3 { color:#343a40; }
.empty-products a,.continue-link { color:#756044; }
.store-footer { margin-top:37px; border-color:#dedfe2; }
.store-footer span:first-child { color:#4a535a; }
.store-footer a { color:#756044; font-size:.73rem; text-decoration:none; }
.store-footer a:hover { text-decoration:underline; }
.stock-label { margin:0 0 9px; color:#777c78; font-size:.7rem; }
.stock-label strong { color:#555b55; font-weight:700; }
.stock-label.low-stock,.stock-label.low-stock strong { color:#9a6b36; }
.stock-label.out-of-stock,.stock-label.out-of-stock strong { color:#a14e48; }
.add-button:disabled,.checkout-button:disabled { cursor:not-allowed; opacity:.58; }
.detail-stock { margin:-10px 0 19px; font-size:.8rem; }
.seller-page { min-height:100vh; }
.seller-login-wrap { display:grid; min-height:calc(100vh - 60px); place-items:center; padding-top:35px; padding-bottom:55px; }
.seller-login-card { width:min(100%,430px); padding:34px; border:1px solid #e1e2e4; border-radius:10px; background:#fff; box-shadow:0 3px 16px #2222; }
.seller-login-card h1,.inventory-heading h1 { margin:0; color:#343a40; font-size:1.6rem; font-weight:700; }
.seller-login-card>p:not(.eyebrow),.inventory-heading>div>p:not(.eyebrow) { margin:7px 0 22px; color:#777e84; font-size:.82rem; }
.seller-login-card form label,.inventory-row form label { display:block; margin:13px 0 6px; color:#515960; font-size:.77rem; font-weight:650; }
.seller-login-card form input { width:100%; margin-bottom:4px; padding:10px 11px; border:1px solid #dfe1e3; border-radius:6px; background:#fff; }
.seller-login-card form .checkout-button { margin-top:18px; }
.seller-login-card>small { display:block; margin-top:19px; color:#858a90; font-size:.7rem; line-height:1.65; }
.seller-inventory-wrap { max-width:960px; padding-top:38px; }
.inventory-heading { display:flex; align-items:center; justify-content:space-between; gap:15px; margin-bottom:20px; }
.inventory-heading>div>p:not(.eyebrow) { margin-bottom:0; }
.inventory-list { overflow:hidden; border:1px solid #e1e2e4; border-radius:9px; background:#fff; }
.inventory-row { display:flex; align-items:center; justify-content:space-between; gap:20px; padding:15px 19px; border-bottom:1px solid #ececee; }
.inventory-row:last-child { border-bottom:0; }
.inventory-product { display:flex; min-width:0; align-items:center; gap:13px; }
.inventory-icon { display:grid; width:51px; height:51px; flex:none; place-items:center; border:1px solid #e9e8e3; border-radius:7px; background:#f6f5f1; font-size:1.8rem; }
.inventory-product small { color:#858a90; font-size:.67rem; }
.inventory-product h2 { margin:2px 0; color:#343a40; font-size:.9rem; font-weight:650; }
.inventory-product p { margin:0; color:#777e84; font-size:.72rem; }
.inventory-row form { flex:none; }
.inventory-row form label { margin:0 0 5px; }
.inventory-row form>div { display:flex; gap:7px; }
.inventory-row form input { width:100px; padding:7px 9px; border:1px solid #dedfe2; border-radius:5px; }
.inventory-row form button { padding:7px 13px; border:0; border-radius:5px; background:#75664e; color:#fff; font-size:.76rem; }
.inventory-row form button:hover { background:#62543f; }
.inventory-empty { margin:0; padding:30px; color:#777e84; text-align:center; }

.seller-pill { display:inline-flex; align-items:center; padding:3px 8px; border-radius:999px; background:#eee8db; color:#67583f; font-size:.68rem; font-weight:700; vertical-align:middle; }
.seller-nav { position:sticky; top:0; z-index:10; border-bottom:1px solid #e3e1dc; background:#fff; }
.seller-nav>.container { min-height:64px; }
.seller-brand { color:#343a40; font-weight:800; text-decoration:none; }
.seller-brand span { margin-left:7px; color:#8b795b; font-size:.76rem; }
.seller-links,.seller-identity { display:flex; align-items:center; gap:15px; }
.seller-links a,.seller-identity button { color:#50575d; font-size:.8rem; text-decoration:none; }
.seller-links a:hover { color:#8b795b; }
.seller-identity { font-size:.8rem; }
.seller-identity form { margin:0; }
.seller-identity button { padding:5px 10px; border:1px solid #dedfe2; border-radius:5px; background:#fff; }
.seller-content { max-width:1050px; padding-top:35px; padding-bottom:70px; }
.seller-content>h1,.seller-page-heading h1 { margin:0 0 20px; color:#343a40; font-size:1.65rem; font-weight:750; }
.seller-page-heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:22px; }
.seller-page-heading .eyebrow { margin:0 0 6px; color:#9a896a; font-size:.67rem; letter-spacing:.14em; }
.seller-page-heading p { margin:8px 0 0; color:#72787d; }
.seller-stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(165px,1fr)); gap:13px; margin-bottom:25px; }
.seller-stats a,.seller-shortcuts a { display:flex; flex-direction:column; gap:7px; padding:19px; border:1px solid #e4e3df; border-radius:9px; background:#fff; color:#464d52; text-decoration:none; }
.seller-stats a span,.seller-shortcuts a span { color:#777e84; font-size:.78rem; }
.seller-stats a strong { color:#806d4f; font-size:1.5rem; }
.seller-shortcuts { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:13px; }
.seller-shortcuts a strong { color:#343a40; }
.seller-filter { display:flex; align-items:center; gap:9px; margin:0 0 17px; }
.seller-filter select,.seller-order-card select { padding:8px 10px; border:1px solid #dfe1e3; border-radius:5px; background:#fff; }
.seller-filter button,.seller-order-card footer form button { padding:8px 13px; border:0; border-radius:5px; background:#75664e; color:#fff; }
.seller-order-list,.seller-product-list,.seller-audit-list { display:grid; gap:12px; }
.seller-order-card { padding:17px 19px; border:1px solid #e3e3e0; border-radius:9px; background:#fff; }
.seller-order-card>header,.seller-order-card>header>div,.seller-order-card>footer { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.seller-order-card>header time,.seller-audit-list time { color:#858a90; font-size:.72rem; }
.seller-status { display:inline-block; margin-left:10px; padding:4px 9px; border-radius:999px; background:#f0ede6; color:#665b48; font-size:.7rem; }
.seller-status.status-delivered { background:#dff2e5; color:#20683a; }
.seller-status.status-cancelled { background:#f8e3e1; color:#923b34; }
.seller-customer { margin:12px 0; color:#6e7479; font-size:.82rem; }
.seller-order-card ul { margin:0; padding:0; list-style:none; }
.seller-order-card li { display:flex; justify-content:space-between; gap:12px; padding:5px 0; color:#454c51; font-size:.8rem; }
.seller-order-card>footer { flex-wrap:wrap; margin-top:13px; padding-top:12px; border-top:1px solid #ececee; }
.seller-order-card footer form { display:flex; align-items:center; gap:8px; margin:0; }
.seller-order-card footer form { flex-wrap:wrap; }
.seller-order-card footer form label { color:#70767b; font-size:.75rem; }
.seller-order-card select { padding:6px 8px; font-size:.78rem; }
.unsaved-status { padding:4px 8px; border-radius:5px; background:#fff0ce; color:#815c16; font-size:.7rem; font-weight:650; }
.seller-form-actions { flex-wrap:wrap; }
.seller-form-actions .checkout-button { width:auto; min-width:100px; margin:0; padding:8px 15px; }
.seller-add-product,.seller-edit-form { margin-bottom:21px; padding:18px; border:1px solid #e3e3e0; border-radius:9px; background:#fff; }
.seller-add-product summary { color:#75664e; font-weight:700; cursor:pointer; }
.seller-add-product form { margin-top:15px; }
.seller-form-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
.seller-form-grid label { display:flex; flex-direction:column; gap:5px; color:#555c61; font-size:.77rem; font-weight:650; }
.seller-form-grid label small { color:#92979b; font-size:.68rem; font-weight:400; }
.seller-form-grid input,.seller-form-grid textarea { width:100%; padding:8px 10px; border:1px solid #dfe1e3; border-radius:5px; font:inherit; font-weight:400; }
.seller-form-wide { grid-column:1/-1; }
.seller-form-actions { display:flex; align-items:center; gap:15px; margin-top:16px; }
.seller-form-actions a { color:#72787d; }
.seller-product-list article { display:flex; align-items:center; justify-content:space-between; gap:15px; padding:12px 15px; border:1px solid #e6e6e3; border-radius:8px; background:#fff; }
.seller-product-info,.seller-product-actions { display:flex; align-items:center; gap:12px; }
.seller-product-info img,.seller-product-info>span { display:grid; width:49px; height:49px; place-items:center; object-fit:cover; border-radius:6px; background:#f3f2ee; font-size:1.5rem; }
.seller-product-info div { display:grid; gap:4px; }
.seller-product-info small { color:#82888d; font-size:.72rem; }
.seller-product-actions form { margin:0; }
.seller-product-actions a,.seller-product-actions button { padding:6px 10px; border:1px solid #dedfe2; border-radius:5px; background:#fff; color:#565d62; font-size:.75rem; text-decoration:none; }
.seller-product-actions button { color:#a14840; }
.seller-audit-list article { display:grid; grid-template-columns:140px 140px 1fr; gap:9px 14px; padding:13px 15px; border:1px solid #e5e5e2; border-radius:7px; background:#fff; font-size:.8rem; }
.seller-audit-list small { grid-column:2/-1; color:#81878c; }
.seller-muted { margin-top:-12px; color:#858a90; font-size:.82rem; }

@media (max-width:767.98px) {
    .store-main { padding-top:17px; }
    .store-hero { padding:11px 0 15px; }
    .store-hero .eyebrow { font-size:.56rem; }
    .store-hero h1 { font-size:1.8rem; }
    .hero-copy { margin-top:6px; font-size:.76rem; }
    .category-pills { flex-wrap:nowrap; overflow-x:auto; margin-right:-12px; margin-bottom:17px; padding:0 12px 11px 0; scrollbar-width:none; }
    .category-pills::-webkit-scrollbar { display:none; }
    .category-pill { flex:none; padding:7px 12px; }
    .catalog-heading { margin-bottom:10px; }
    .catalog-heading h2 { font-size:1.13rem; }
    .catalog-heading>span { font-size:.66rem; }
    .catalog-layout { gap:20px; }
    .product-grid { gap:11px; }
    .product-card,.product-card:hover { border-radius:7px; }
    .product-icon,.product-card:nth-child(4n+2) .product-icon,.product-card:nth-child(4n+3) .product-icon,.product-card:nth-child(4n+4) .product-icon { aspect-ratio:.95/1; }
    .product-icon span { font-size:clamp(4rem,17vw,6rem); }
    .product-card .card-body { padding:9px 9px 10px; }
    .product-title-row h3 { font-size:.78rem; }
    .product-title-row strong { font-size:.76rem; }
    .product-description { margin:4px 0 8px; font-size:.64rem; }
    .add-button { padding:8px; font-size:.68rem; }
    .favorite-form button { width:28px; height:28px; font-size:1.05rem; }
    .cart-card { position:static; }
    .seller-login-card { padding:25px 21px; }
    .seller-inventory-wrap { padding-top:25px; }
    .inventory-row { align-items:flex-start; flex-direction:column; gap:12px; padding:13px; }
    .inventory-row form { width:100%; }
    .inventory-row form>div { max-width:280px; }
    .inventory-heading { align-items:flex-start; flex-direction:column; }
    .seller-links { order:3; width:100%; overflow:auto; gap:13px; padding:9px 0; }
    .seller-links a { flex:none; }
    .seller-stats,.seller-shortcuts { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .seller-order-card>header,.seller-order-card>footer { align-items:flex-start; flex-direction:column; }
    .seller-audit-list article { grid-template-columns:1fr 1fr; }
    .seller-audit-list small { grid-column:1/-1; }
}
@media (max-width:575.98px) {
    .desktop-account-links { display:none; }
    .mobile-account { display:block; }
    .store-nav .nav-actions { gap:8px !important; }
    .store-nav .container { flex-wrap:nowrap; }
}


/* Account dropdown and dedicated cart entry */
.catalog-layout { grid-template-columns:minmax(0,1fr); }
.account-menu { position:relative; }
.account-menu summary { display:flex; align-items:center; gap:9px; cursor:pointer; list-style:none; white-space:nowrap; color:#3e474e; font-size:.82rem; }
.account-menu summary::-webkit-details-marker { display:none; }
.account-avatar { display:grid; width:34px; height:34px; place-items:center; border:1px solid #e1e2e4; border-radius:50%; background:#f5f3ef; font-size:1.08rem; }
.account-name { max-width:150px; overflow:hidden; text-overflow:ellipsis; font-weight:650; }
.account-chevron { color:#82888d; font-size:1rem; }
.account-menu[open] .account-dropdown { position:absolute; z-index:1200; top:calc(100% + 11px); right:0; display:grid; min-width:190px; padding:7px; border:1px solid #e1e2e4; border-radius:9px; background:#fff; box-shadow:0 9px 24px #20252a20; }
.account-dropdown a,.account-dropdown form button { display:block; width:100%; padding:10px 11px; border:0; border-radius:6px; background:transparent; color:#424a50; font-size:.82rem; text-align:left; text-decoration:none; }
.account-dropdown a:hover,.account-dropdown form button:hover { background:#f4f3f0; color:#62543f; }
.account-dropdown form { margin-top:5px; padding-top:5px; border-top:1px solid #ececee; }
.account-dropdown form button { color:#9b4d48; }
.bag-link { order:-1; position:relative; display:grid; width:42px; height:42px; place-items:center; padding:8px; border:1px solid #dedfe2; border-radius:50%; color:#3c434a; }
.bag-link svg { width:21px; height:21px; fill:none; stroke:currentColor; stroke-linecap:round; stroke-linejoin:round; stroke-width:1.7; }
.bag-link .cart-count { position:absolute; top:-5px; right:-5px; display:grid; min-width:19px; height:19px; padding:0 4px; place-items:center; border-radius:999px; background:#75664e; color:white; font-size:.62rem; line-height:1; }
.bag-link:hover { background:#f2ede3; color:#66543d; }
.cart-page { max-width:850px; min-height:65vh; }
.cart-page .catalog-heading { margin:16px 0 20px; }
.cart-page .catalog-heading h1 { margin:0; font-size:1.5rem; font-weight:700; }
.cart-page .cart-card { position:static; padding:20px; }
.cart-page .cart-line { padding:17px 0; }
.cart-page .cart-line:first-child { padding-top:0; }
.cart-page .cart-total { margin-top:18px; }
.cart-page .checkout-button { width:100%; margin-top:13px; }
.cart-page .clear-button { margin-top:10px; }
.cart-page .cart-empty { margin-top:20px; padding:55px 20px; }
.cart-page .store-footer { justify-content:space-between; }
@media (max-width:575.98px) {
    .account-name { max-width:78px; }
    .account-menu summary { gap:6px; font-size:.74rem; }
    .account-avatar { width:32px; height:32px; }
    .bag-link { width:38px; height:38px; }
    .store-nav .nav-actions { gap:11px !important; }
}


/* Product options dialog and focused product detail */
.product-order-dialog { width:min(92vw,450px); max-width:450px; padding:27px; border:1px solid #e1e2e4; border-radius:14px; background:#fff; color:#343a40; box-shadow:0 18px 60px #18201d35; }
.product-order-dialog::backdrop { background:#18201d77; backdrop-filter:blur(2px); }
.dialog-close-form { position:absolute; top:12px; right:12px; }
.dialog-close { width:34px; height:34px; border:0; border-radius:50%; background:#f1f2f3; color:#555; font-size:1.35rem; line-height:1; }
.dialog-heading { margin-bottom:20px; padding-right:30px; }
.dialog-heading .eyebrow { margin-bottom:5px; }
.dialog-heading h2 { margin:0; font-size:1.2rem; font-weight:700; }
[data-product-order-form] { display:grid; gap:8px; }
[data-product-order-form] label { margin-top:5px; color:#555d64; font-size:.78rem; font-weight:650; }
[data-product-order-form] select,[data-product-order-form] input { width:100%; min-height:42px; padding:8px 10px; border:1px solid #dedfe2; border-radius:6px; background:white; color:#343a40; }
[data-product-order-form] .checkout-button { margin-top:12px; }
.dialog-stock { margin:4px 0 0; color:#7c8389; font-size:.75rem; }
.detail-layout-clean { grid-template-columns:minmax(0,1fr) minmax(0,.9fr); overflow:hidden; border:1px solid #e4e5e7; border-radius:12px; background:#fff; box-shadow:0 2px 9px #20252a0a; }
.detail-photo { min-height:450px; background:#fff; }
.detail-photo::after { display:none; }
.detail-photo img { width:100%; height:100%; max-height:550px; object-fit:contain; }
.detail-photo .detail-product-icon { display:grid; width:100%; height:100%; place-items:center; font-size:8rem; }
.detail-layout-clean .detail-copy { gap:12px; padding:clamp(25px,4vw,48px); }
.detail-category { color:#777e84; font-size:.82rem; }
.detail-layout-clean .detail-copy h1 { margin:0; color:#343a40; font-size:clamp(1.5rem,3vw,2.1rem); font-weight:700; }
.detail-layout-clean .detail-description { margin:0; color:#656d74; font-size:.9rem; line-height:1.8; white-space:pre-line; }
.detail-price { margin:3px 0 0; color:#756044; font-size:1.3rem; font-weight:750; }
.detail-layout-clean .detail-rating { margin:0; }
.rating-heart { color:#d5d7d9; font-size:1.15rem; }
.rating-heart.filled { color:#b35e63; }
.detail-layout-clean .detail-rating small { margin-left:7px; }
.detail-layout-clean .detail-stock { margin:0; }
.detail-layout-clean .detail-actions { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-top:7px; }
.detail-layout-clean .detail-actions>button { min-width:160px; margin:0; }
.detail-layout-clean .detail-favorite { min-height:45px; padding:11px 15px; border:1px solid #dedfe2; border-radius:6px; background:#fff; color:#535b63; font-size:.8rem; }
.detail-layout-clean .detail-favorite:hover { border-color:#75664e; color:#62543f; }
@media (max-width:767.98px) {
    .detail-layout-clean { grid-template-columns:1fr; }
    .detail-photo { min-height:0; aspect-ratio:1/1; }
    .detail-layout-clean .detail-copy { padding:22px; }
}

.product-icon .product-photo { display:block; width:100%; height:100%; object-fit:cover; filter:none; }
.inventory-controls { display:grid; grid-template-columns:minmax(150px,.7fr) minmax(250px,1.3fr); align-items:end; gap:16px; }
.inventory-controls form { min-width:0; }
.inventory-controls .image-upload-form input[type=file] { min-width:0; max-width:100%; padding:6px; font-size:.68rem; }
.inventory-controls .image-upload-form small { display:block; margin-top:4px; color:#858a90; font-size:.65rem; }
.inventory-photo { object-fit:cover; }
@media (max-width:767.98px) {
    .inventory-controls { width:100%; grid-template-columns:1fr; gap:12px; }
}

.detail-photo { display:flex; flex-direction:column; gap:12px; padding:15px; background:#fff; }
.gallery-main-wrap { display:grid; min-height:300px; flex:1; place-items:center; }
.gallery-main { display:block; width:100%; height:100%; max-height:500px; object-fit:contain; }
.gallery-thumbnails { display:flex; justify-content:center; gap:9px; overflow-x:auto; padding:2px 2px 6px; }
.gallery-thumbnails button { width:66px; height:66px; flex:none; overflow:hidden; padding:0; border:1px solid #dedfe2; border-radius:6px; background:white; }
.gallery-thumbnails button.active { border:2px solid #75664e; }
.gallery-thumbnails img { display:block; width:100%; height:100%; object-fit:cover; }
.inventory-gallery { display:flex; flex-wrap:wrap; gap:8px; grid-column:1/-1; }
.inventory-thumb { position:relative; width:62px; height:62px; overflow:hidden; border:1px solid #e1e2e4; border-radius:6px; background:#fff; }
.inventory-thumb img { width:100%; height:100%; object-fit:cover; }
.inventory-thumb form { position:absolute; right:2px; bottom:2px; margin:0; }
.inventory-thumb button { padding:2px 5px; border:0; border-radius:3px; background:#0009; color:#fff; font-size:.6rem; }

/* Store navigation and centered listing favorite controls */
.favorite-form button { box-sizing:border-box; padding:0; display:flex; align-items:center; justify-content:center; text-align:center; font-family:Arial,sans-serif; font-weight:400; }


/* Buyer order progress and compact product photo galleries */
.order-filter { margin:0 0 18px; }
.order-progress { display:flex; align-items:flex-start; margin:20px 0 24px; padding:0; list-style:none; }
.order-progress li { position:relative; display:flex; flex:1; flex-direction:column; align-items:center; gap:7px; color:#92979b; text-align:center; }
.order-progress li::before { position:absolute; z-index:0; top:15px; right:50%; width:100%; height:3px; background:#e3e5e7; content:""; }
.order-progress li:first-child::before { display:none; }
.order-progress li.is-complete::before { background:#4c8b68; }
.order-progress li>span { z-index:1; display:grid; width:32px; height:32px; place-items:center; border:2px solid #d9dcde; border-radius:50%; background:#fff; font-size:.8rem; }
.order-progress li.is-complete>span { border-color:#4c8b68; background:#4c8b68; color:#fff; }
.order-progress li.is-current { color:#315d42; font-weight:700; }
.order-progress li small { font-size:.75rem; }
.order-cancelled { color:#a33b36; font-weight:650; }
.gallery-main-wrap { position:relative; }
.gallery-arrow,.card-gallery-arrow { position:absolute; z-index:2; display:grid; width:38px; height:38px; place-items:center; border:0; border-radius:50%; background:#fffE; color:#302d29; box-shadow:0 2px 10px #0002; font-size:1.6rem; line-height:1; }
.gallery-arrow:hover,.card-gallery-arrow:hover { background:#fff; }
.gallery-prev { left:10px; top:50%; transform:translateY(-50%); }
.gallery-next { right:10px; top:50%; transform:translateY(-50%); }
.product-card-gallery { position:relative; }
.card-gallery-arrow { width:30px; height:30px; top:50%; transform:translateY(-50%); font-size:1.25rem; }
.card-gallery-arrow.prev { left:8px; }
.card-gallery-arrow.next { right:8px; }
.card-gallery-count { position:absolute; right:8px; bottom:8px; padding:3px 7px; border-radius:12px; background:#1119; color:#fff; font-size:.68rem; }
.gallery-thumbnails { justify-content:flex-start; max-width:100%; }
.gallery-thumbnails button { scroll-margin-inline:8px; }
@media(max-width:575.98px) { .order-progress li small { font-size:.65rem; } .order-progress li>span { width:28px; height:28px; } .order-progress li::before { top:13px; } }


.account-avatar { overflow:hidden; flex:none; padding:0; }
.account-avatar img,.avatar-preview img { display:block; width:100%; height:100%; border-radius:50%; object-fit:cover; }
.avatar-upload { display:grid; justify-items:start; gap:8px; }
.avatar-upload>label { font-weight:650; }
.avatar-upload input[type=file] { max-width:420px; }
.avatar-preview { display:grid; width:88px; height:88px; overflow:hidden; place-items:center; border:1px solid #e1e2e4; border-radius:50%; background:#f5f3ef; font-size:2rem; }
.avatar-preview img { border-radius:50%; }
.gallery-arrow,.card-gallery-arrow { padding:0; font-size:0; line-height:0; }
.gallery-arrow::before,.card-gallery-arrow::before { position:absolute; top:50%; left:50%; width:10px; height:10px; border-top:2px solid currentColor; border-right:2px solid currentColor; content:""; }
.gallery-arrow.gallery-prev::before,.card-gallery-arrow.prev::before { transform:translate(-50%,-50%) rotate(-135deg); }
.gallery-arrow.gallery-next::before,.card-gallery-arrow.next::before { transform:translate(-50%,-50%) rotate(45deg); }

html { scrollbar-gutter: stable; }
.account-avatar,.avatar-preview { position:relative; }
.account-avatar::after,.avatar-preview::after { content:attr(data-fallback); color:#75664e; font-size:.9rem; font-weight:700; }
.account-avatar img,.avatar-preview img { position:absolute; inset:0; z-index:1; }


/* Keep product gallery geometry fixed while source photos change. */
.product-card-gallery { width:100%; aspect-ratio:1.18 / 1; overflow:hidden; }
.product-card-gallery .product-icon { width:100%; height:100%; aspect-ratio:auto; }
.product-card-gallery .product-photo { width:100%; height:100%; object-fit:contain; }
.gallery-main-wrap { position:relative; width:100%; aspect-ratio:1 / 1; min-height:0; flex:0 0 auto; overflow:hidden; }
.gallery-main { width:100%; height:100%; max-height:none; object-fit:contain; }
.detail-photo { min-height:0; }
@media(max-width:767.98px) {
  .product-card-gallery { aspect-ratio:.95 / 1; }
}

'''

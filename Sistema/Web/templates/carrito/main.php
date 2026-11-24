<div
  class="export-wrapper"
  style="
    width: 1440px;
    min-height: 812px;
    position: relative;
    font-family: var(--font-family-body);
    background-color: var(--background);
  "
>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@100;200;300;400;500;600;700;800;900&family=Geist:wght@100;200;300;400;500;600;700;800;900&family=IBM+Plex+Mono:wght@100;200;300;400;500;600;700&family=IBM+Plex+Sans:wght@100;200;300;400;500;600;700&family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Nunito:wght@200;300;400;500;600;700;800;900&family=PT+Serif:wght@400;700&family=Roboto+Slab:wght@100;200;300;400;500;600;700;800;900&family=Roboto:wght@100;300;400;500;700;900&family=Shantell+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap"
    rel="stylesheet"
  />
  <html>
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Milonga Bazar - Carrito</title>

      <style id="base-styles">
        * {
          box-sizing: border-box;
        }

        .export-wrapper {
          margin: 0;
          padding: 0;
        }

        .page-container {
          min-height: 812px;
          display: flex;
          flex-direction: column;
          background: var(--muted);
          color: var(--foreground);
          font-family: var(--font-family-body);
        }

        .clickable {
          cursor: default;
        }
      </style>

      <style id="header-styles">
        .header {
          background-color: var(--background);
          border-bottom: 1px solid var(--border);
          padding-bottom: 12px;
        }

        .header-top,
        .header-bottom {
          max-width: 1200px;
          margin: 0 auto;
          padding-left: 16px;
          padding-right: 16px;
          width: 100%;
        }

        .header-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 40px;
          padding-top: 12px;
          padding-bottom: 12px;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 8px;
          white-space: nowrap;
          font-size: 24px;
          font-weight: 700;
          color: var(--primary);
        }

        .logo-badge {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: var(--radius-sm);
          background: var(--primary);
          color: var(--primary-foreground);
        }

        .search-container {
          flex: 1;
          display: flex;
          align-items: center;
          background: var(--input);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          overflow: hidden;
          min-width: 0;
          height: 40px;
        }

        .search-input {
          flex: 1;
          display: flex;
          align-items: center;
          height: 100%;
          padding: 0 16px;
          min-width: 0;
        }

        .search-placeholder {
          font-size: 15px;
          color: var(--muted-foreground);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .search-button {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-left: 1px solid var(--border);
          background: var(--background);
          flex-shrink: 0;
        }

        .header-promo {
          display: flex;
          align-items: center;
          gap: 8px;
          white-space: nowrap;
          font-size: 14px;
          font-weight: 500;
          color: var(--foreground);
        }

        .header-bottom {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
        }

        .location-nav {
          display: flex;
          align-items: center;
          gap: 32px;
          min-width: 0;
        }

        .location {
          display: flex;
          align-items: center;
          gap: 8px;
          white-space: nowrap;
        }

        .location-text {
          display: flex;
          flex-direction: column;
          line-height: 1.1;
        }

        .location-text-top {
          font-size: 11px;
          color: var(--muted-foreground);
        }

        .location-text-bottom {
          font-size: 13px;
          font-weight: 500;
          color: var(--foreground);
        }

        .main-nav,
        .user-nav {
          display: flex;
          align-items: center;
          gap: 16px;
          min-width: 0;
        }

        .main-nav-item,
        .user-nav-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          font-weight: 500;
          color: var(--foreground);
          white-space: nowrap;
        }

        .cart-container {
          position: relative;
        }

        .cart-badge {
          position: absolute;
          top: -4px;
          right: -4px;
          width: 16px;
          height: 16px;
          border-radius: 999px;
          background: var(--primary);
          color: var(--primary-foreground);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          font-weight: 700;
        }
      </style>

      <style id="cart-styles">
        .cart-layout {
          display: grid;
          grid-template-columns: minmax(0, 1fr) 420px;
          gap: 24px;
          max-width: 1200px;
          margin: 0 auto;
          width: 100%;
          padding: 32px 16px 64px;
          flex: 1;
          align-items: start;
        }

        .cart-items-section {
          display: flex;
          flex-direction: column;
          gap: 16px;
          min-width: 0;
        }

        .cart-title {
          font-size: 24px;
          font-weight: 600;
          color: var(--foreground);
          margin: 0;
        }

        .cart-subtitle {
          font-size: 14px;
          color: var(--muted-foreground);
          margin: 0;
        }

        .cart-item-list {
          display: flex;
          flex-direction: column;
          background: var(--card);
          border-radius: var(--radius-md);
          border: 1px solid var(--border);
          overflow: hidden;
        }

        .cart-item {
          display: flex;
          align-items: flex-start;
          padding: 24px;
          gap: 24px;
          border-bottom: 1px solid var(--border);
        }

        .cart-item:last-child {
          border-bottom: none;
        }

        .item-image {
          width: 112px;
          height: 112px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border);
          overflow: hidden;
          flex-shrink: 0;
          background: var(--background);
        }

        .item-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .item-details {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 16px;
          min-width: 0;
          padding-top: 4px;
        }

        .item-title {
          font-size: 16px;
          font-weight: 500;
          color: var(--foreground);
          margin: 0;
          line-height: 1.4;
        }

        .item-meta {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .item-tag {
          background: var(--secondary);
          color: var(--secondary-foreground);
          border-radius: var(--radius-xl);
          padding: 6px 10px;
          font-size: 12px;
          font-weight: 500;
          white-space: nowrap;
        }

        .item-actions {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
          margin-top: auto;
        }

        .item-action-btn {
          font-size: 13px;
          color: var(--primary);
          font-weight: 500;
          white-space: nowrap;
        }

        .item-side {
          width: 220px;
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 16px;
          flex-shrink: 0;
          padding-top: 4px;
        }

        .item-controls {
          display: flex;
          align-items: flex-start;
        }

        .item-quantity-control {
          display: flex;
          align-items: center;
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          height: 44px;
          overflow: hidden;
          background: var(--background);
        }

        .qty-btn {
          width: 48px;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--background);
          color: var(--foreground);
        }

        .qty-value {
          width: 56px;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 500;
          border-left: 1px solid var(--border);
          border-right: 1px solid var(--border);
        }

        .item-price-col {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 6px;
          min-width: 0;
        }

        .item-price {
          font-size: 20px;
          font-weight: 500;
          color: var(--foreground);
        }

        .item-stock {
          font-size: 12px;
          color: var(--success);
          font-weight: 500;
        }

        .cart-summary-section {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .summary-card,
        .reserve-card {
          background: var(--card);
          border-radius: var(--radius-md);
          border: 1px solid var(--border);
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .summary-title {
          font-size: 18px;
          font-weight: 600;
          margin: 0;
          color: var(--foreground);
        }

        .summary-row {
          display: flex;
          justify-content: space-between;
          gap: 16px;
          font-size: 15px;
          color: var(--foreground);
        }

        .summary-row.total {
          font-size: 20px;
          font-weight: 600;
          padding-top: 16px;
          border-top: 1px solid var(--border);
        }

        .summary-row-note {
          font-size: 13px;
          color: var(--muted-foreground);
          margin-top: -8px;
        }

        .payment-methods-section,
        .purchase-methods-section {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding-top: 16px;
          border-top: 1px solid var(--border);
        }

        .payment-title,
        .purchase-title,
        .reserve-title {
          font-size: 15px;
          font-weight: 600;
          margin: 0;
          color: var(--foreground);
        }

        .payment-option,
        .purchase-option {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 16px;
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          background: var(--background);
        }

        .payment-option.selected,
        .purchase-option.selected {
          border-color: var(--primary);
          background: var(--muted);
        }

        .radio-circle {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          border: 2px solid var(--border);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-top: 2px;
          flex-shrink: 0;
        }

        .payment-option.selected .radio-circle,
        .purchase-option.selected .radio-circle {
          border-color: var(--primary);
        }

        .payment-option.selected .radio-circle::after,
        .purchase-option.selected .radio-circle::after {
          content: "";
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--primary);
        }

        .option-copy {
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 0;
        }

        .payment-label,
        .purchase-label {
          font-size: 14px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--foreground);
          white-space: nowrap;
        }

        .payment-description,
        .purchase-description,
        .reserve-description {
          font-size: 13px;
          color: var(--muted-foreground);
          line-height: 1.4;
        }

        .btn-checkout,
        .btn-secondary {
          width: 100%;
          padding: 16px;
          border-radius: var(--radius-sm);
          font-size: 16px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          white-space: nowrap;
        }

        .btn-checkout {
          background: var(--primary);
          color: var(--primary-foreground);
        }

        .btn-secondary {
          background: var(--secondary);
          color: var(--secondary-foreground);
        }

        .reserve-card {
          gap: 12px;
        }
      </style>
    </head>
    <body>
      <div id="page" class="page-container">
        <header id="header" class="header">
          <div class="header-top">
            <div
              id="logo"
              class="logo clickable"
              data-media-type="banani-button"
            >
              <div class="logo-badge">
                <iconify-icon
                  icon="lucide:store"
                  style="font-size: 20px; color: var(--primary-foreground)"
                ></iconify-icon>
              </div>
              <span>Milonga Bazar</span>
            </div>

            <div id="search-container" class="search-container">
              <div class="search-input">
                <span class="search-placeholder"
                  >Buscar productos, marcas y más...</span
                >
              </div>
              <div
                class="search-button clickable"
                data-media-type="banani-button"
              >
                <div
                  style="
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  "
                >
                  <iconify-icon
                    icon="lucide:search"
                    style="font-size: 20px; color: var(--muted-foreground)"
                  ></iconify-icon>
                </div>
              </div>
            </div>

            <div id="header-promo" class="header-promo">
              <div
                style="
                  width: 20px;
                  height: 20px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                "
              >
                <iconify-icon
                  icon="lucide:truck"
                  style="font-size: 20px; color: var(--foreground)"
                ></iconify-icon>
              </div>
              <span>Envíos a todo el país</span>
            </div>
          </div>

          <div class="header-bottom">
            <div class="location-nav">
              <div
                id="location"
                class="location clickable"
                data-media-type="banani-button"
              >
                <div
                  style="
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  "
                >
                  <iconify-icon
                    icon="lucide:map-pin"
                    style="font-size: 20px; color: var(--foreground)"
                  ></iconify-icon>
                </div>
                <div class="location-text">
                  <span class="location-text-top">Enviar a</span>
                  <span class="location-text-bottom">Capital Federal</span>
                </div>
              </div>

              <nav id="main-nav" class="main-nav">
                <div
                  class="main-nav-item clickable"
                  data-media-type="banani-button"
                >
                  Categorías
                  <div
                    style="
                      width: 14px;
                      height: 14px;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                    "
                  >
                    <iconify-icon
                      icon="lucide:chevron-down"
                      style="font-size: 14px; color: var(--foreground)"
                    ></iconify-icon>
                  </div>
                </div>
                <div
                  class="main-nav-item clickable"
                  data-media-type="banani-button"
                >
                  Ofertas
                </div>
                <div
                  class="main-nav-item clickable"
                  data-media-type="banani-button"
                >
                  Historial
                </div>
                <div
                  class="main-nav-item clickable"
                  data-media-type="banani-button"
                >
                  Ayuda
                </div>
              </nav>
            </div>

            <nav id="user-nav" class="user-nav">
              <div
                class="user-nav-item clickable"
                data-media-type="banani-button"
              >
                <div
                  style="
                    width: 18px;
                    height: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  "
                >
                  <iconify-icon
                    icon="lucide:user"
                    style="font-size: 18px; color: var(--foreground)"
                  ></iconify-icon>
                </div>
                <span>Mi cuenta</span>
              </div>
              <div
                class="user-nav-item clickable"
                data-media-type="banani-button"
              >
                Mis compras
              </div>
              <div
                class="user-nav-item clickable"
                data-media-type="banani-button"
              >
                <div
                  style="
                    width: 18px;
                    height: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  "
                >
                  <iconify-icon
                    icon="lucide:bell"
                    style="font-size: 18px; color: var(--foreground)"
                  ></iconify-icon>
                </div>
              </div>
              <div
                class="user-nav-item cart-container clickable"
                data-media-type="banani-button"
              >
                <div
                  style="
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  "
                >
                  <iconify-icon
                    icon="lucide:shopping-cart"
                    style="font-size: 20px; color: var(--foreground)"
                  ></iconify-icon>
                </div>
                <span class="cart-badge">3</span>
              </div>
            </nav>
          </div>
        </header>

        <main id="cart-content" class="cart-layout">
          <div class="cart-items-section">
            <h1 class="cart-title">Carrito</h1>
            <p class="cart-subtitle">
              Revisá tus artículos, elegí cómo querés comprar y finalizá tu
              pedido online o con reserva.
            </p>
            <div class="cart-item-list">
              <div class="cart-item">
                <div class="item-image">
                  <img
                    data-aspect-ratio="1:1"
                    data-query="traditional argentine mate cup gourd with bombilla clean white background product shot, soft pink and cream color palette"
                    alt="Mate de calabaza"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/7f475cad-6c67-47ad-b629-fdcf4661dcb9.jpg"
                  />
                </div>
                <div class="item-details">
                  <div>
                    <h3 class="item-title">
                      Mate De Calabaza Imperial Camionero Con Virola De Alpaca
                    </h3>
                  </div>
                  <div class="item-meta">
                    <span class="item-tag">Retiro disponible</span>
                    <span class="item-tag">Últimas unidades</span>
                  </div>
                  <div class="item-actions">
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Eliminar</span
                    >
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Guardar para después</span
                    >
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Reservar</span
                    >
                  </div>
                </div>
                <div class="item-side">
                  <div class="item-controls">
                    <div class="item-quantity-control">
                      <div
                        class="qty-btn clickable"
                        data-media-type="banani-button"
                      >
                        <iconify-icon
                          icon="lucide:minus"
                          style="font-size: 14px; color: var(--foreground)"
                        ></iconify-icon>
                      </div>
                      <div class="qty-value">1</div>
                      <div
                        class="qty-btn clickable"
                        data-media-type="banani-button"
                      >
                        <iconify-icon
                          icon="lucide:plus"
                          style="font-size: 14px; color: var(--foreground)"
                        ></iconify-icon>
                      </div>
                    </div>
                  </div>
                  <div class="item-price-col">
                    <span class="item-price">$ 18.500</span>
                    <span class="item-stock">Stock inmediato</span>
                  </div>
                </div>
              </div>

              <div class="cart-item">
                <div class="item-image">
                  <img
                    data-aspect-ratio="1:1"
                    data-query="wicker pendant lamp rattan bohemian style clean white background product shot, soft pink and cream color palette"
                    alt="Lámpara de mimbre"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/f896d98a-540d-4f50-9a62-d8c9a71888be.jpg"
                  />
                </div>
                <div class="item-details">
                  <div>
                    <h3 class="item-title">
                      Lámpara Colgante De Mimbre Y Rattan Diseño Campana 40cm
                    </h3>
                  </div>
                  <div class="item-meta">
                    <span class="item-tag">Envío disponible</span>
                    <span class="item-tag">Hecho a mano</span>
                  </div>
                  <div class="item-actions">
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Eliminar</span
                    >
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Guardar para después</span
                    >
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Reservar</span
                    >
                  </div>
                </div>
                <div class="item-side">
                  <div class="item-controls">
                    <div class="item-quantity-control">
                      <div
                        class="qty-btn clickable"
                        data-media-type="banani-button"
                      >
                        <iconify-icon
                          icon="lucide:minus"
                          style="font-size: 14px; color: var(--foreground)"
                        ></iconify-icon>
                      </div>
                      <div class="qty-value">1</div>
                      <div
                        class="qty-btn clickable"
                        data-media-type="banani-button"
                      >
                        <iconify-icon
                          icon="lucide:plus"
                          style="font-size: 14px; color: var(--foreground)"
                        ></iconify-icon>
                      </div>
                    </div>
                  </div>
                  <div class="item-price-col">
                    <span class="item-price">$ 32.000</span>
                    <span class="item-stock">Despacho en 48 hs</span>
                  </div>
                </div>
              </div>

              <div class="cart-item">
                <div class="item-image">
                  <img
                    data-aspect-ratio="1:1"
                    data-query="cast iron skillet frying pan clean white background product shot, soft pink and cream color palette"
                    alt="Sartén de hierro"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/577f545b-14ac-4109-97bc-aaa8a93a793d.jpg"
                  />
                </div>
                <div class="item-details">
                  <div>
                    <h3 class="item-title">
                      Sartén De Hierro Fundido 26cm Mango Madera Apto Inducción
                    </h3>
                  </div>
                  <div class="item-meta">
                    <span class="item-tag">Retiro hoy</span>
                    <span class="item-tag">Apto cocina a gas</span>
                  </div>
                  <div class="item-actions">
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Eliminar</span
                    >
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Guardar para después</span
                    >
                    <span
                      class="item-action-btn clickable"
                      data-media-type="banani-button"
                      >Reservar</span
                    >
                  </div>
                </div>
                <div class="item-side">
                  <div class="item-controls">
                    <div class="item-quantity-control">
                      <div
                        class="qty-btn clickable"
                        data-media-type="banani-button"
                      >
                        <iconify-icon
                          icon="lucide:minus"
                          style="font-size: 14px; color: var(--foreground)"
                        ></iconify-icon>
                      </div>
                      <div class="qty-value">1</div>
                      <div
                        class="qty-btn clickable"
                        data-media-type="banani-button"
                      >
                        <iconify-icon
                          icon="lucide:plus"
                          style="font-size: 14px; color: var(--foreground)"
                        ></iconify-icon>
                      </div>
                    </div>
                  </div>
                  <div class="item-price-col">
                    <span class="item-price">$ 29.999</span>
                    <span class="item-stock">3 disponibles</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <aside class="cart-summary-section">
            <div class="summary-card">
              <h2 class="summary-title">Resumen de compra</h2>

              <div class="summary-row">
                <span>Productos (3)</span>
                <span>$ 80.499</span>
              </div>
              <div class="summary-row">
                <span>Envío</span>
                <span style="color: var(--success); font-weight: 500"
                  >Gratis</span
                >
              </div>
              <div class="summary-row total">
                <span>Total</span>
                <span>$ 80.499</span>
              </div>
              <div class="summary-row-note">
                Podés finalizar la compra ahora o reservar los productos para
                retirarlos luego.
              </div>

              <div class="purchase-methods-section">
                <h3 class="purchase-title">Método de compra</h3>
                <div
                  class="purchase-option selected clickable"
                  data-media-type="banani-button"
                >
                  <div class="radio-circle"></div>
                  <div class="option-copy">
                    <div class="purchase-label">Compra online</div>
                    <div class="purchase-description">
                      Pagás ahora y coordinamos envío o retiro.
                    </div>
                  </div>
                </div>
                <div
                  class="purchase-option clickable"
                  data-media-type="banani-button"
                >
                  <div class="radio-circle"></div>
                  <div class="option-copy">
                    <div class="purchase-label">Reserva en tienda</div>
                    <div class="purchase-description">
                      Reservá por 24 hs y pagá al retirar en Milonga.
                    </div>
                  </div>
                </div>
              </div>

              <div class="payment-methods-section">
                <h3 class="payment-title">Método de pago</h3>
                <div
                  class="payment-option selected clickable"
                  data-media-type="banani-button"
                >
                  <div class="radio-circle"></div>
                  <div class="option-copy">
                    <div class="payment-label">Tarjeta de débito o crédito</div>
                    <div class="payment-description">
                      Pago online en un solo cobro.
                    </div>
                  </div>
                </div>
                <div
                  class="payment-option clickable"
                  data-media-type="banani-button"
                >
                  <div class="radio-circle"></div>
                  <div class="option-copy">
                    <div class="payment-label">Transferencia bancaria</div>
                    <div class="payment-description">
                      Te enviamos los datos al confirmar la compra.
                    </div>
                  </div>
                </div>
                <div
                  class="payment-option clickable"
                  data-media-type="banani-button"
                >
                  <div class="radio-circle"></div>
                  <div class="option-copy">
                    <div class="payment-label">Efectivo al retirar</div>
                    <div class="payment-description">
                      Disponible si elegís reserva o retiro por el local.
                    </div>
                  </div>
                </div>
              </div>

              <div
                class="btn-checkout clickable"
                data-media-type="banani-button"
              >
                Pagar ahora
              </div>
            </div>

            <div class="reserve-card">
              <h3 class="reserve-title">Reserva sin pago online</h3>
              <div class="reserve-description">
                Ideal para un bazar chico: apartás los productos y coordinás el
                retiro o pago por mensaje.
              </div>
            </div>
          </aside>
        </main>
      </div>
    </body>
  </html>
  <script src="https://code.iconify.design/iconify-icon/3.0.0/iconify-icon.min.js"></script>
  <style>
    :root {
      --background: #fffdfc;
      --foreground: #1f1720;
      --border: #00000012;
      --input: #ffffff;
      --primary: #e85d93;
      --primary-foreground: #ffffff;
      --secondary: #faf3f7;
      --secondary-foreground: #1f1720;
      --muted: #f6edf2;
      --muted-foreground: #7e6a75;
      --success: #1f9d55;
      --success-foreground: #ffffff;
      --accent: #f8bbd0;
      --accent-foreground: #1f1720;
      --destructive: #d7265e;
      --destructive-foreground: #ffffff;
      --warning: #f7c7d9;
      --warning-foreground: #1f1720;
      --card: #ffffff;
      --card-foreground: #1f1720;
      --sidebar: #fdf4f8;
      --sidebar-foreground: #1f1720;
      --sidebar-primary: #f9d7e4;
      --sidebar-primary-foreground: #1f1720;
      --radius-sm: 4px;
      --radius-md: 6px;
      --radius-lg: 8px;
      --radius-xl: 12px;
      --font-family-body: Inter;
    }
  </style>
</div>

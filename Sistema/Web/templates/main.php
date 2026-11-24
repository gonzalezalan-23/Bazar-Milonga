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
      <style id="base-styles">
        * {
          box-sizing: border-box;
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

      <style id="content-styles">
        .main-content {
          max-width: 1200px;
          margin: 0 auto;
          width: 100%;
          padding: 24px 16px 64px;
          display: flex;
          flex-direction: column;
          gap: 40px;
          flex: 1;
        }

        .hero-banner {
          width: 100%;
          height: 280px;
          overflow: hidden;
          border-radius: var(--radius-md);
          background: var(--card);
        }

        .hero-banner img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }

        .section {
          display: flex;
          flex-direction: column;
        }

        .section-header {
          display: flex;
          align-items: flex-end;
          gap: 16px;
          margin-bottom: 20px;
        }

        .section-title {
          margin: 0;
          font-size: 24px;
          font-weight: 500;
          color: var(--foreground);
        }

        .section-link {
          font-size: 14px;
          font-weight: 500;
          color: var(--primary);
          white-space: nowrap;
        }

        .product-grid {
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 16px;
        }

        .product-card {
          display: flex;
          flex-direction: column;
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          overflow: hidden;
          min-width: 0;
        }

        .product-image {
          width: 100%;
          aspect-ratio: 1 / 1;
          border-bottom: 1px solid var(--border);
          background: var(--card);
          overflow: hidden;
        }

        .product-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }

        .product-info {
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          flex: 1;
        }

        .product-price-row {
          display: flex;
          align-items: baseline;
          gap: 8px;
          flex-wrap: wrap;
        }

        .product-price {
          font-size: 24px;
          font-weight: 500;
          color: var(--foreground);
        }

        .product-discount {
          font-size: 13px;
          font-weight: 500;
          color: var(--success);
          white-space: nowrap;
        }

        .product-shipping {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          font-weight: 600;
          color: var(--success);
          white-space: nowrap;
        }

        .product-title {
          font-size: 14px;
          font-weight: 400;
          line-height: 1.3;
          color: var(--muted-foreground);
          min-height: 54px;
          overflow: hidden;
        }

        .product-actions {
          padding: 0 16px 16px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .btn-add-cart,
        .btn-buy-now {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 10px 12px;
          border-radius: var(--radius-sm);
          white-space: nowrap;
          font-size: 14px;
          font-weight: 500;
        }

        .btn-add-cart {
          background: var(--primary);
          color: var(--primary-foreground);
        }

        .btn-buy-now {
          background: var(--secondary);
          color: var(--secondary-foreground);
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

        <main id="main-content" class="main-content">
          <section
            id="hero-banner"
            class="hero-banner clickable"
            data-media-type="banani-button"
          >
            <img
              data-aspect-ratio="21:9"
              data-query="ecommerce promotional banner for small bazaar home goods sale with blush pink palette, elegant decor objects, soft feminine retail aesthetic, warm neutral and pink tones"
              alt="Banner de ofertas"
              src="https://storage.googleapis.com/banani-generated-images/generated-images/a5186f97-adc6-44f5-9488-cdf0b1354002.jpg"
            />
          </section>

          <section id="section-offers" class="section">
            <div class="section-header">
              <h2 class="section-title">Ofertas en Bazar Milonga</h2>
              <div
                class="section-link clickable"
                data-media-type="banani-button"
              >
                Ver todas
              </div>
            </div>

            <div class="product-grid">
              <div class="product-card" id="product-1">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="traditional argentine mate cup gourd with bombilla clean white background product shot"
                    alt="Mate de calabaza"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/e511382d-b81f-4df6-8f56-487dcacdaf59.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 18.500</span>
                    <span class="product-discount">15% OFF</span>
                  </div>
                  <div class="product-shipping">
                    Llega gratis mañana
                    <div
                      style="
                        width: 12px;
                        height: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                      "
                    >
                      <iconify-icon
                        icon="lucide:zap"
                        style="font-size: 12px; color: var(--success)"
                      ></iconify-icon>
                    </div>
                  </div>
                  <div class="product-title">
                    Mate De Calabaza Imperial Camionero Con Virola De Alpaca
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                  <div
                    class="btn-buy-now clickable"
                    data-media-type="banani-button"
                  >
                    Comprar ahora
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-2">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="set of rustic ceramic dinner plates stacked clean white background product shot"
                    alt="Juego de platos"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/c4ebfbf5-71ed-4e88-9cb0-e1b7b242a5b1.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 45.900</span>
                  </div>
                  <div class="product-shipping">Llega gratis mañana</div>
                  <div class="product-title">
                    Juego De Vajilla 12 Piezas Platos Cerámica Rústica Artesanal
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                  <div
                    class="btn-buy-now clickable"
                    data-media-type="banani-button"
                  >
                    Comprar ahora
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-3">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="wicker pendant lamp rattan bohemian style clean white background product shot"
                    alt="Lámpara de mimbre"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/996008c0-e946-4f4e-a315-c2e28b78cb09.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 32.000</span>
                    <span class="product-discount">10% OFF</span>
                  </div>
                  <div class="product-shipping">Llega gratis el jueves</div>
                  <div class="product-title">
                    Lámpara Colgante De Mimbre Y Rattan Diseño Campana 40cm
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                  <div
                    class="btn-buy-now clickable"
                    data-media-type="banani-button"
                  >
                    Comprar ahora
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-4">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="stainless steel cutlery set 24 pieces in wooden box clean background product shot"
                    alt="Juego de cubiertos"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/9322f6ee-10aa-499e-a441-963cd90020ab.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 68.400</span>
                  </div>
                  <div class="product-shipping">Llega gratis mañana</div>
                  <div class="product-title">
                    Set Juego De Cubiertos 24 Piezas Acero Inoxidable Premium
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                  <div
                    class="btn-buy-now clickable"
                    data-media-type="banani-button"
                  >
                    Comprar ahora
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-5">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="cast iron skillet frying pan clean white background product shot"
                    alt="Sartén de hierro"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/10bc905e-b58f-4ae0-9d7c-b87a64e6fad5.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 29.999</span>
                    <span class="product-discount">20% OFF</span>
                  </div>
                  <div class="product-shipping">Llega gratis hoy</div>
                  <div class="product-title">
                    Sartén De Hierro Fundido 26cm Mango Madera Apto Inducción
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                  <div
                    class="btn-buy-now clickable"
                    data-media-type="banani-button"
                  >
                    Comprar ahora
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="section-history" class="section">
            <div class="section-header">
              <h2 class="section-title">Basado en tu última visita</h2>
              <div
                class="section-link clickable"
                data-media-type="banani-button"
              >
                Ver historial completo
              </div>
            </div>

            <div class="product-grid">
              <div class="product-card" id="product-6">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="woven bohemian cotton rug texture clean background product shot"
                    alt="Alfombra"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/0240d484-27a1-4448-a74b-1ff88d30a2da.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 54.000</span>
                  </div>
                  <div class="product-shipping">Llega gratis mañana</div>
                  <div class="product-title">
                    Alfombra Tejida Algodón 120x180cm Diseño Nórdico Lavable
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-7">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="glass storage jars containers with bamboo lids clean white background product shot"
                    alt="Frascos de vidrio"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/f56a5b63-21d6-43ad-8e43-11a487dff4cc.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 12.500</span>
                  </div>
                  <div class="product-shipping">Llega mañana</div>
                  <div class="product-title">
                    Set X4 Frascos De Vidrio Borosilicato Tapa Bambú Herméticos
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-8">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="french press coffee maker glass and steel clean white background product shot"
                    alt="Cafetera"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/d0cf6d2b-330b-473e-aac3-e1007ec743a9.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 24.800</span>
                    <span class="product-discount">5% OFF</span>
                  </div>
                  <div class="product-shipping">Llega gratis mañana</div>
                  <div class="product-title">
                    Cafetera Prensa Francesa 800ml Vidrio Y Acero Inoxidable
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-9">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="wooden cutting board acacia wood clean white background product shot"
                    alt="Tabla de picar"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/b78b8ecb-6f13-445f-8c15-aae8452cd0b0.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 16.200</span>
                  </div>
                  <div class="product-shipping">Llega el viernes</div>
                  <div class="product-title">
                    Tabla De Picar Madera Acacia Rectangular 40x30cm Premium
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                </div>
              </div>

              <div class="product-card" id="product-10">
                <div
                  class="product-image clickable"
                  data-media-type="banani-button"
                >
                  <img
                    data-aspect-ratio="1:1"
                    data-query="ceramic mugs set of 4 pastel colors clean white background product shot"
                    alt="Tazas"
                    src="https://storage.googleapis.com/banani-generated-images/generated-images/e66740cb-14b1-41e2-8011-73e4d4783422.jpg"
                  />
                </div>
                <div class="product-info">
                  <div class="product-price-row">
                    <span class="product-price">$ 19.500</span>
                  </div>
                  <div class="product-shipping">Llega gratis mañana</div>
                  <div class="product-title">
                    Set 4 Tazas Jarro Mug Cerámica Colores Pastel 350ml
                  </div>
                </div>
                <div class="product-actions">
                  <div
                    class="btn-add-cart clickable"
                    data-media-type="banani-button"
                  >
                    Agregar al carrito
                  </div>
                </div>
              </div>
            </div>
          </section>
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

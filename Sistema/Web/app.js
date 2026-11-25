// ─── Estado global ────────────────────────────────────────────────────────────
// Lista de productos cargados desde la API. Se pre-carga desde localStorage
// para que el catálogo aparezca instantáneamente mientras llega la respuesta.
let products = [];
try {
  const cached = JSON.parse(localStorage.getItem('milonga-products-cache') || '[]');
  products = Array.isArray(cached) ? cached : [];
} catch {
  products = [];
}

// true cuando la API respondió correctamente al menos una vez en esta sesión.
// Se usa para habilitar el botón "Confirmar reserva".
let apiReady = false;

// Categoría activa en el filtro del catálogo.
let category = 'Todos';

// Página actual del catálogo (base 1) y productos por página.
let currentPage = 1;
const PAGE_SIZE = 20;

// Carrito: array de objetos { id, qty }. Se persiste en localStorage.
let cart = [];
try {
  const saved = JSON.parse(localStorage.getItem('milonga-cart') || '[]');
  cart = Array.isArray(saved)
    ? saved.filter(x => x && Number.isInteger(Number(x.id)) && Number.isInteger(Number(x.qty)) && Number(x.qty) > 0)
    : [];
} catch {
  cart = [];
}

// Elemento que tenía el foco antes de abrir el carrito, para restaurarlo al cerrar.
let lastFocus = null;


// ─── Utilidades ───────────────────────────────────────────────────────────────

// Formatea un número como moneda argentina: $ 1.200
const money = value =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(value);

// Escapa caracteres especiales HTML para evitar XSS al insertar texto en innerHTML.
const escapeHTML = value =>
  String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));

// Referencias a elementos del DOM que se usan en múltiples funciones.
const grid  = document.querySelector('#product-grid');
const toast = document.querySelector('#toast');
let toastTimer;

// Muestra un mensaje flotante (toast) que desaparece a los 3,2 segundos.
function showToast(text) {
  toast.textContent = text;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
}


// ─── Configuración de la tienda ───────────────────────────────────────────────

// Carga tienda.json y actualiza la dirección y la foto de portada.
// Si falla (sin servidor PHP), muestra un texto de reemplazo.
async function loadStoreConfig() {
  const addressNode = document.querySelector('#store-address');
  try {
    const response = await fetch('./tienda.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('No se pudo cargar la configuración del local.');
    const settings = await response.json();

    // Dirección del local
    if (addressNode) {
      addressNode.textContent =
        typeof settings.direccion === 'string' && settings.direccion.trim()
          ? settings.direccion.trim()
          : 'Dirección a confirmar';
    }

    // Foto de portada: solo se acepta una ruta dentro de uploads/
    const imagePath = typeof settings.imagen_portada === 'string' ? settings.imagen_portada : '';
    if (!/^uploads\/[A-Za-z0-9._-]+$/.test(imagePath)) return;

    const hero  = document.querySelector('.hero-art');
    const photo = document.querySelector('#hero-image');
    photo.addEventListener('load', () => {
      photo.hidden = false;
      hero.classList.add('has-photo');
    }, { once: true });
    photo.src = `./${imagePath.split('/').map(encodeURIComponent).join('/')}`;

  } catch {
    if (addressNode) addressNode.textContent = 'Dirección a confirmar';
  }
}


// ─── Catálogo ─────────────────────────────────────────────────────────────────

// Convierte una fila de la API (formato de la base de datos) en el objeto
// que usa el resto del código. Asigna emoji y color de fondo por categoría.
function productFromDb(row) {
  const categoryName = row.categoria || 'Otros';

  // Emoji y color de fondo por categoría. Podés agregar más entradas acá.
  const visuals = {
    Skincare:   ['🧴', '#f5e1df'],
    Maquillaje: ['💄', '#f6e7dc'],
    Accesorios: ['🎀', '#f3e2ed'],
  };
  const visual = Object.hasOwn(visuals, categoryName) ? visuals[categoryName] : ['✿', '#f2e9ec'];

  // Valida que la ruta de imagen sea segura antes de usarla.
  const image =
    typeof row.imagen === 'string' && /^uploads\/[A-Za-z0-9._-]+$/.test(row.imagen)
      ? `./${row.imagen.split('/').map(encodeURIComponent).join('/')}`
      : '';

  // Etiqueta de disponibilidad que aparece en la tarjeta.
  const tag =
    Number(row.stock) === 0 ? 'Agotado' :
    Number(row.stock) <= 3  ? 'Quedan pocas unidades' :
                              'Disponible';

  return {
    id:          Number(row.id),
    name:        row.nombre,
    description: typeof row.descripcion === 'string' ? row.descripcion : '',
    category:    categoryName,
    price:       Number(row.precio_venta),
    stock:       Number(row.stock),
    image,
    emoji:       visual[0],
    bg:          visual[1],
    tag,
  };
}

// Pide el catálogo a la API PHP y actualiza la vista.
// showStatus: si es true, muestra un toast con el resultado (útil al actualizar manualmente).
async function loadCatalog({ showStatus = false } = {}) {
  const note = document.querySelector('.sample-note');
  note.textContent = 'Actualizando disponibilidad…';

  try {
    const response = await fetch('./api.php?action=products', { headers: { Accept: 'application/json' } });
    const data = await response.json();
    if (!response.ok || !Array.isArray(data.products)) throw new Error(data.error || 'No se pudo cargar el catálogo.');

    // IDs que estaban en el carrito antes de actualizar, para detectar productos eliminados.
    const oldIds = new Set(cart.map(item => Number(item.id)));

    products  = data.products.map(productFromDb);
    apiReady  = true;

    // Guarda en caché para la próxima carga de página.
    try { localStorage.setItem('milonga-products-cache', JSON.stringify(products)); } catch {}

    note.textContent = products.length ? 'Productos y disponibilidad actuales' : 'Catálogo sin productos';

    // Reconstruye los botones de filtro con las categorías disponibles.
    const categories = ['Todos', ...new Set(products.map(p => p.category))];
    if (!categories.includes(category)) category = 'Todos';
    document.querySelector('#filters').innerHTML = categories
      .map((name, i) => `<button type="button" class="filter ${i === 0 ? 'active' : ''}" data-category="${escapeHTML(name)}">${escapeHTML(name)}</button>`)
      .join('');

    // Quita del carrito los productos que ya no existen en el catálogo.
    const availableIds = new Set(products.map(p => p.id));
    const removed = [...oldIds].filter(id => !availableIds.has(id)).length;
    cart = cart.filter(item => availableIds.has(Number(item.id)));

    renderProducts();
    saveCart();

    if (removed && !showStatus) showToast(`${removed} producto(s) del carrito ya no están en el catálogo.`);
    if (showStatus) showToast(
      removed
        ? 'Disponibilidad actualizada. Quité del carrito un producto que ya no está en el catálogo; revisá el resto antes de enviar.'
        : 'Disponibilidad actualizada. Revisá tu carrito antes de enviar.'
    );

  } catch (error) {
    apiReady = false;
    note.textContent = 'No se pudo conectar con el inventario';
    grid.innerHTML = `
      <div class="empty-results" role="status">
        <strong>No pudimos cargar los productos.</strong><br>
        Verificá que el servidor PHP esté funcionando y volvé a intentar.<br>
        <button type="button" class="button primary retry-catalog" data-retry-catalog>Reintentar</button>
      </div>`;
    document.querySelector('#filters').replaceChildren();
    renderCart();
    if (showStatus) showToast('No se pudo actualizar el catálogo. Tu carrito sigue guardado.');
  }
}

// Renderiza las tarjetas de producto según el filtro y la búsqueda activos.
// Aplica paginación: muestra PAGE_SIZE productos por página.
function renderProducts() {
  const normalize = s => s.toLocaleLowerCase('es').normalize('NFD').replace(/\p{Diacritic}/gu, '');
  const q = normalize(document.querySelector('#search').value.trim());

  const visible = products.filter(p =>
    (category === 'Todos' || p.category === category) &&
    normalize(`${p.name} ${p.category} ${p.description}`).includes(q)
  );

  // Al cambiar filtro o búsqueda, volver a la primera página.
  const totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  if (currentPage > totalPages) currentPage = 1;

  const start      = (currentPage - 1) * PAGE_SIZE;
  const paginated  = visible.slice(start, start + PAGE_SIZE);

  if (!visible.length) {
    grid.innerHTML = `<div class="empty-results">${
      products.length
        ? 'No hay productos que coincidan. Probá otra búsqueda o categoría.'
        : 'Todavía no hay productos disponibles. El local puede cargarlos desde Ingresos.'
    }</div>`;
    renderPagination(0);
    return;
  }

  grid.innerHTML = paginated.map(p => `
    <article class="product-card">
      <div class="product-visual" style="--bg:${p.bg}">
        <span class="product-tag ${p.stock === 0 ? 'sold-out' : ''}">${escapeHTML(p.tag)}</span>
        ${p.image
          ? `<img class="product-image" src="${escapeHTML(p.image)}" alt="" loading="lazy">`
          : `<span class="product-emoji" aria-hidden="true">${p.emoji}</span>`}
        <button
          type="button"
          class="quick-add"
          data-add="${p.id}"
          aria-label="${p.stock === 0 ? 'Sin stock: ' : 'Agregar al carrito: '}${escapeHTML(p.name)}"
          ${p.stock === 0 ? 'disabled' : ''}
        >${p.stock === 0 ? 'Agotado' : '+'}</button>
      </div>
      <div class="product-info">
        <span class="product-category">${escapeHTML(p.category)}</span>
        <h3 class="product-name">${escapeHTML(p.name)}</h3>
        ${p.description ? `<p class="product-description">${escapeHTML(p.description)}</p>` : ''}
        <span class="product-price">${money(p.price)}</span>
        <span class="product-stock">${p.stock > 0 ? `${p.stock} disponibles` : 'Sin unidades disponibles'}</span>
      </div>
    </article>`).join('');

  renderPagination(totalPages);
}

// Renderiza los botones de paginación debajo de la grilla.
// Si hay una sola página, oculta el paginador.
function renderPagination(totalPages) {
  const nav = document.querySelector('#pagination');
  nav.innerHTML = '';
  if (totalPages <= 1) return;

  // Botón «Anterior»
  const prev = document.createElement('button');
  prev.textContent = '←';
  prev.setAttribute('aria-label', 'Página anterior');
  prev.disabled = currentPage === 1;
  prev.addEventListener('click', () => goToPage(currentPage - 1));
  nav.appendChild(prev);

  // Números de página: siempre muestra la primera, la última
  // y las 2 adyacentes a la actual. Pone “…” donde hay saltos.
  const pages = new Set([1, totalPages]);
  for (let i = currentPage - 2; i <= currentPage + 2; i++) {
    if (i >= 1 && i <= totalPages) pages.add(i);
  }
  let last = 0;
  for (const page of [...pages].sort((a, b) => a - b)) {
    if (last && page - last > 1) {
      const dots = document.createElement('span');
      dots.textContent = '…';
      dots.style.cssText = 'padding:0 4px;color:#a08f98;align-self:center';
      nav.appendChild(dots);
    }
    const btn = document.createElement('button');
    btn.textContent = page;
    btn.setAttribute('aria-label', `Página ${page}`);
    if (page === currentPage) btn.setAttribute('aria-current', 'page');
    btn.addEventListener('click', () => goToPage(page));
    nav.appendChild(btn);
    last = page;
  }

  // Botón «Siguiente»
  const next = document.createElement('button');
  next.textContent = '→';
  next.setAttribute('aria-label', 'Página siguiente');
  next.disabled = currentPage === totalPages;
  next.addEventListener('click', () => goToPage(currentPage + 1));
  nav.appendChild(next);
}

// Cambia a la página indicada y hace scroll al inicio del catálogo.
function goToPage(page) {
  currentPage = page;
  renderProducts();
  document.querySelector('#productos').scrollIntoView({ behavior: 'smooth', block: 'start' });
}


// ─── Carrito ──────────────────────────────────────────────────────────────────

// Guarda el carrito en localStorage y vuelve a renderizarlo.
function saveCart() {
  try { localStorage.setItem('milonga-cart', JSON.stringify(cart)); } catch {}
  renderCart();
}

// Devuelve true si el carrito está listo para confirmar:
// la API respondió, hay al menos un producto y todas las cantidades son válidas.
function validCart() {
  return apiReady && cart.length > 0 && cart.every(item => {
    const p = products.find(x => x.id === Number(item.id));
    return p && item.qty > 0 && item.qty <= p.stock;
  });
}

// Agrega una unidad de un producto al carrito.
function addToCart(id) {
  const p = products.find(x => x.id === id);
  if (!apiReady || !p || p.stock < 1) return showToast('Este producto no tiene unidades disponibles.');
  const item = cart.find(x => x.id === id);
  if (item && item.qty >= p.stock) return showToast('Ya agregaste todas las unidades disponibles.');
  item ? item.qty++ : cart.push({ id, qty: 1 });
  saveCart();
  showToast(`${p.name} se agregó al carrito.`);
}

// Renderiza el contenido del panel lateral del carrito.
function renderCart() {
  const count = cart.reduce((n, x) => n + x.qty, 0);
  document.querySelector('#cart-count').textContent       = count;
  document.querySelector('#cart-title-count').textContent = `(${count})`;

  const itemsEl = document.querySelector('#cart-items');
  const empty   = cart.length === 0;

  // Cuando el carrito está vacío, #cart-items no debe crecer (flex: 0)
  // para que #cart-empty ocupe el espacio y quede centrado verticalmente.
  itemsEl.style.flex = empty ? '0' : '';

  itemsEl.innerHTML = cart.map(item => {
    const p = products.find(y => y.id === Number(item.id));

    // Producto no encontrado (puede pasar si el caché está desactualizado)
    if (!p) return `
      <div class="cart-row needs-review">
        <div class="cart-item-details">
          <b>Producto #${Number(item.id)}</b>
          <small>No pudimos verificar su información.</small>
          <button type="button" class="remove-item" data-remove="${Number(item.id)}">Quitar</button>
        </div>
      </div>`;

    const over = item.qty > p.stock;
    return `
      <div class="cart-row ${over ? 'needs-review' : ''}">
        <div class="cart-thumb" style="--bg:${p.bg}" aria-hidden="true">
          ${p.image ? `<img src="${escapeHTML(p.image)}" alt="" loading="lazy">` : p.emoji}
        </div>
        <div class="cart-item-details">
          <b>${escapeHTML(p.name)}</b>
          <small>${money(p.price)} por unidad</small>
          <div class="quantity">
            <button type="button" data-qty="${p.id}" data-delta="-1" aria-label="Quitar una unidad de ${escapeHTML(p.name)}">−</button>
            <span>${item.qty}</span>
            <button type="button" data-qty="${p.id}" data-delta="1"  aria-label="Agregar una unidad de ${escapeHTML(p.name)}" ${item.qty >= p.stock ? 'disabled' : ''}>+</button>
            <button type="button" class="remove-item" data-remove="${p.id}">Quitar</button>
          </div>
          ${over ? `<small class="availability-warning">Pediste ${item.qty}; ahora solo quedan ${p.stock}. Ajustá la cantidad.</small>` : ''}
          ${p.stock === 0 ? '<small class="availability-warning">Agotado. Quitalo o esperá a que vuelva a estar disponible.</small>' : ''}
        </div>
        <span class="cart-line-total">${money(p.price * item.qty)}</span>
      </div>`;
  }).join('');

  // Total del carrito (suma precio × cantidad de cada ítem)
  document.querySelector('#cart-total').textContent = money(
    cart.reduce((n, x) => n + (products.find(p => p.id === Number(x.id))?.price || 0) * x.qty, 0)
  );

  // Muestra u oculta el mensaje de carrito vacío y el pie con el total
  document.querySelector('#cart-empty').hidden  = !empty;
  document.querySelector('#cart-bottom').hidden = empty;

  // Habilita el botón de confirmar solo si el carrito es válido
  document.querySelector('#checkout').disabled = !validCart();

  // Aviso de cantidades inválidas (stock insuficiente)
  document.querySelector('#cart-warning').hidden = validCart() || empty;
}

// Abre o cierra el panel lateral del carrito.
// Al abrir: guarda el foco actual y lo mueve al botón de cerrar.
// Al cerrar: devuelve el foco al elemento que lo tenía antes.
function setCart(open) {
  const panel = document.querySelector('#cart-panel');
  if (open) {
    lastFocus = document.activeElement;
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
    document.querySelector('#overlay').hidden = false;
    document.body.style.overflow = 'hidden';
    document.querySelector('#close-cart').focus();
  } else {
    const wasOpen = panel.classList.contains('open');
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    document.querySelector('#overlay').hidden = true;
    document.body.style.overflow = '';
    if (wasOpen) (lastFocus?.isConnected ? lastFocus : document.querySelector('#open-cart')).focus();
  }
}


// ─── Eventos del catálogo ─────────────────────────────────────────────────────

// Clic en la grilla: "Reintentar" recarga el catálogo; "+" agrega al carrito.
grid.addEventListener('click', e => {
  if (e.target.closest('[data-retry-catalog]')) { loadCatalog({ showStatus: true }); return; }
  const btn = e.target.closest('[data-add]');
  if (btn && !btn.disabled) addToCart(Number(btn.dataset.add));
});

// Clic en los botones de filtro por categoría.
// Resetea a la página 1 para que los resultados aparezcan desde el principio.
document.querySelector('#filters').addEventListener('click', e => {
  const btn = e.target.closest('[data-category]');
  if (!btn) return;
  category = btn.dataset.category;
  currentPage = 1;
  document.querySelectorAll('.filter').forEach(x => x.classList.toggle('active', x === btn));
  renderProducts();
});

// Búsqueda en tiempo real mientras el usuario escribe.
// Resetea a la página 1 para que los resultados aparezcan desde el principio.
document.querySelector('#search').addEventListener('input', () => {
  currentPage = 1;
  renderProducts();
});


// ─── Eventos del carrito ──────────────────────────────────────────────────────

// Clic dentro de la lista de ítems: quitar producto o cambiar cantidad.
document.querySelector('#cart-items').addEventListener('click', e => {
  const removeBtn = e.target.closest('[data-remove]');
  const qtyBtn    = e.target.closest('[data-qty]');

  if (removeBtn) {
    cart = cart.filter(x => x.id !== Number(removeBtn.dataset.remove));
  }

  if (qtyBtn) {
    const item  = cart.find(i => i.id === Number(qtyBtn.dataset.qty));
    const p     = products.find(i => i.id === Number(qtyBtn.dataset.qty));
    const delta = Number(qtyBtn.dataset.delta);

    if (item && delta < 0) {
      item.qty--;
      if (item.qty < 1) cart = cart.filter(i => i !== item);
    } else if (item && p && delta > 0 && item.qty < p.stock) {
      item.qty++;
    }
  }

  saveCart();
});

// Botones para abrir y cerrar el panel del carrito.
document.querySelector('#open-cart').addEventListener('click',    () => setCart(true));
document.querySelector('#close-cart').addEventListener('click',   () => setCart(false));
document.querySelector('#overlay').addEventListener('click',      () => setCart(false));
document.querySelector('#keep-shopping').addEventListener('click', () => setCart(false));

// Botón "Actualizar disponibilidad" dentro del carrito.
document.querySelector('#refresh-stock').addEventListener('click', () => loadCatalog({ showStatus: true }));

// Teclado: Escape cierra el carrito; Tab atrapa el foco dentro del panel.
document.addEventListener('keydown', e => {
  const panel = document.querySelector('#cart-panel');
  if (!panel.classList.contains('open')) return;

  if (e.key === 'Escape') { setCart(false); return; }

  if (e.key === 'Tab') {
    const focusable = [...panel.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),textarea:not(:disabled)')]
      .filter(el => !el.hidden);
    if (!focusable.length) return;
    const first = focusable[0];
    const last  = focusable.at(-1);
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});


// ─── Checkout (formulario de reserva) ────────────────────────────────────────

// Abre el diálogo de reserva con el subtotal calculado.
document.querySelector('#checkout').addEventListener('click', () => {
  if (!validCart()) return showToast('Actualizá la disponibilidad y revisá las cantidades.');
  setCart(false);
  document.querySelector('#checkout-summary').textContent = money(
    cart.reduce((sum, item) => sum + (products.find(p => p.id === item.id)?.price || 0) * item.qty, 0)
  );
  document.querySelector('#checkout-fields').hidden      = false;
  document.querySelector('#order-confirmation').hidden   = true;
  document.querySelector('#checkout-dialog').setAttribute('aria-labelledby', 'checkout-title');
  document.querySelector('#checkout-dialog').showModal();
  document.querySelector('#checkout-title').focus({ preventScroll: true });
});

// Cierra el diálogo de reserva (botón ×).
document.querySelector('#close-checkout').addEventListener('click',    () => document.querySelector('#checkout-dialog').close());
document.querySelector('#close-confirmation').addEventListener('click', () => document.querySelector('#checkout-dialog').close());

// Envío del formulario de reserva.
document.querySelector('#checkout-form').addEventListener('submit', async e => {
  e.preventDefault();
  if (!validCart()) { showToast('Revisá el stock antes de enviar la reserva.'); return; }

  // Guarda una copia del carrito para mostrar en la confirmación si la API no devuelve ítems.
  const snapshot = cart.map(item => ({ product: products.find(p => p.id === item.id), qty: item.qty }));
  const total    = snapshot.reduce((sum, line) => sum + line.product.price * line.qty, 0);

  const button = document.querySelector('#send-order');
  button.disabled    = true;
  button.textContent = 'Enviando reserva…';

  const form = new FormData(e.currentTarget);
  try {
    const response = await fetch('./api.php?action=orders', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        nombre:     form.get('name'),
        telefono:   form.get('phone'),
        entrega:    form.get('delivery'),
        comentario: form.get('note'),
        items:      cart.map(item => ({ id: item.id, cantidad: item.qty })),
      }),
    });

    const result = await response.json().catch(() => ({ error: 'El servidor devolvió una respuesta inválida.' }));

    // 409 = el stock cambió entre que el usuario armó el carrito y envió el pedido.
    if (response.status === 409) {
      await loadCatalog({ showStatus: true });
      throw new Error('El stock cambió mientras preparabas el pedido. Revisá las cantidades y volvé a intentarlo.');
    }
    if (!response.ok) throw new Error(result.error || 'No se pudo registrar la reserva.');

    // Muestra la pantalla de confirmación con el número de reserva y los ítems.
    document.querySelector('#confirmation-id').textContent = `Reserva #${result.order_id}`;
    const confirmedItems = Array.isArray(result.items)
      ? result.items
      : snapshot.map(line => ({ nombre: line.product.name, cantidad: line.qty, precio_unitario: line.product.price }));
    document.querySelector('#confirmation-items').innerHTML = confirmedItems
      .map(line => `<li>${Number(line.cantidad)} × ${escapeHTML(line.nombre)} <span>${money(Number(line.precio_unitario) * Number(line.cantidad))}</span></li>`)
      .join('');
    document.querySelector('#confirmation-total').textContent = money(Number(result.total));

    document.querySelector('#checkout-fields').hidden    = true;
    document.querySelector('#order-confirmation').hidden = false;
    document.querySelector('#checkout-dialog').setAttribute('aria-labelledby', 'confirmation-title');

    // Vacía el carrito y resetea el formulario.
    cart = [];
    saveCart();
    e.currentTarget.reset();
    document.querySelector('#checkout-dialog').querySelector('#confirmation-title').focus({ preventScroll: true });

  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled   = false;
    button.innerHTML  = 'Solicitar reserva <span>→</span>';
  }
});

// Al cerrar el diálogo (cualquier forma), restaura el estado inicial del formulario.
document.querySelector('#checkout-dialog').addEventListener('close', () => {
  document.querySelector('#checkout-dialog').setAttribute('aria-labelledby', 'checkout-title');
  document.querySelector('#open-cart').focus();
});


// ─── Menú de navegación móvil ─────────────────────────────────────────────────

const menuToggle = document.querySelector('#menu-toggle');
const mainNav    = document.querySelector('#main-nav');

// Abre o cierra el menú hamburguesa en pantallas chicas.
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  mainNav.classList.toggle('open', open);
});

// Cierra el menú al hacer clic en un enlace de navegación.
mainNav.addEventListener('click', e => {
  if (e.target.closest('a')) {
    menuToggle.setAttribute('aria-expanded', 'false');
    mainNav.classList.remove('open');
  }
});

// Cierra el menú con Escape.
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
    menuToggle.setAttribute('aria-expanded', 'false');
    mainNav.classList.remove('open');
    menuToggle.focus();
  }
});


// ─── Inicio ───────────────────────────────────────────────────────────────────

document.querySelector('#year').textContent = new Date().getFullYear();
renderCart();       // Muestra el carrito guardado antes de que llegue la API
loadStoreConfig();  // Carga dirección y foto de portada desde tienda.json
loadCatalog();      // Carga el catálogo desde la API PHP

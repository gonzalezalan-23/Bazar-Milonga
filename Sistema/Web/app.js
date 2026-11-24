let products = [];
try { const cached=JSON.parse(localStorage.getItem('milonga-products-cache')||'[]'); products=Array.isArray(cached)?cached:[]; } catch { products=[]; }
let apiReady = false;
let category = 'Todos';
let cart = [];
let lastFocus = null;
try {
  const saved = JSON.parse(localStorage.getItem('milonga-cart') || '[]');
  cart = Array.isArray(saved) ? saved.filter(x => x && Number.isInteger(Number(x.id)) && Number.isInteger(Number(x.qty)) && Number(x.qty) > 0) : [];
} catch { cart = []; }
const money = value => new Intl.NumberFormat('es-AR', {style:'currency', currency:'ARS', maximumFractionDigits:0}).format(value);
const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const grid = document.querySelector('#product-grid');
const toast = document.querySelector('#toast');
let toastTimer;
function showToast(text) { toast.textContent = text; toast.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove('show'), 3200); }
async function loadStoreConfig() {
  const addressNode=document.querySelector('#store-address');
  try {
    const response=await fetch('./tienda.json',{cache:'no-store'});
    if(!response.ok)throw new Error('No se pudo cargar la configuración del local.');
    const settings=await response.json();
    if(addressNode)addressNode.textContent=typeof settings.direccion==='string'&&settings.direccion.trim()?settings.direccion.trim():'Dirección a confirmar';
    const imagePath=typeof settings.imagen_portada==='string'?settings.imagen_portada:'';
    if(!/^uploads\/[A-Za-z0-9._-]+$/.test(imagePath))return;
    const hero=document.querySelector('.hero-art'),photo=document.querySelector('#hero-image');
    photo.addEventListener('load',()=>{photo.hidden=false;hero.classList.add('has-photo');},{once:true});
    photo.src=`./${imagePath.split('/').map(encodeURIComponent).join('/')}`;
  } catch {
    if(addressNode)addressNode.textContent='Dirección a confirmar';
  }
}
function productFromDb(row) {
  const categoryName = row.categoria || 'Otros';
  const visuals = {Skincare:['🧴','#f5e1df'], Maquillaje:['💄','#f6e7dc'], Accesorios:['🎀','#f3e2ed']};
  const visual = Object.hasOwn(visuals, categoryName) ? visuals[categoryName] : ['✿','#f2e9ec'];
  const image = typeof row.imagen === 'string' && /^uploads\/[A-Za-z0-9._-]+$/.test(row.imagen) ? `./${row.imagen.split('/').map(encodeURIComponent).join('/')}` : '';
  return {id:Number(row.id), name:row.nombre, description:typeof row.descripcion==='string'?row.descripcion:'', category:categoryName, price:Number(row.precio_venta), stock:Number(row.stock), image, emoji:visual[0], bg:visual[1], tag:Number(row.stock)===0?'Agotado':Number(row.stock)<=3?'Quedan pocas unidades':'Disponible'};
}
async function loadCatalog({showStatus = false} = {}) {
  const note = document.querySelector('.sample-note');
  note.textContent = 'Actualizando disponibilidad…';
  try {
    const response = await fetch('./api.php?action=products', {headers:{Accept:'application/json'}});
    const data = await response.json();
    if (!response.ok || !Array.isArray(data.products)) throw new Error(data.error || 'No se pudo cargar el catálogo.');
    const oldIds = new Set(cart.map(item => Number(item.id)));
    products = data.products.map(productFromDb);
    try { localStorage.setItem('milonga-products-cache', JSON.stringify(products)); } catch {}
    apiReady = true;
    note.textContent = products.length ? 'Productos y disponibilidad actuales' : 'Catálogo sin productos';
    const categories = ['Todos', ...new Set(products.map(p => p.category))];
    if (!categories.includes(category)) category = 'Todos';
    document.querySelector('#filters').innerHTML = categories.map((name,i) => `<button type="button" class="filter ${i===0?'active':''}" data-category="${escapeHTML(name)}">${escapeHTML(name)}</button>`).join('');
    const availableIds = new Set(products.map(p => p.id));
    const removed = [...oldIds].filter(id => !availableIds.has(id)).length;
    cart = cart.filter(item => availableIds.has(Number(item.id)));
    renderProducts();
    saveCart();
    if (removed && !showStatus) showToast(`${removed} producto(s) del carrito ya no están en el catálogo.`);
    if (showStatus) showToast(removed ? 'Disponibilidad actualizada. Quité del carrito un producto que ya no está en el catálogo; revisá el resto antes de enviar.' : 'Disponibilidad actualizada. Revisá tu carrito antes de enviar.');
  } catch (error) {
    apiReady = false;
    note.textContent = 'No se pudo conectar con el inventario';
    grid.innerHTML = '<div class="empty-results" role="status"><strong>No pudimos cargar los productos.</strong><br>Verificá que el servidor PHP esté funcionando y volvé a intentar.<br><button type="button" class="button primary retry-catalog" data-retry-catalog>Reintentar</button></div>';
    document.querySelector('#filters').replaceChildren();
    renderCart();
    if (showStatus) showToast('No se pudo actualizar el catálogo. Tu carrito sigue guardado.');
  }
}
function saveCart() { try { localStorage.setItem('milonga-cart', JSON.stringify(cart)); } catch {} renderCart(); }
function renderProducts() {
  const q=document.querySelector('#search').value.trim().toLocaleLowerCase('es');
  const visible=products.filter(p=>(category==='Todos'||p.category===category)&&`${p.name} ${p.category} ${p.description}`.toLocaleLowerCase('es').includes(q));
  grid.innerHTML=visible.length?visible.map(p=>`<article class="product-card"><div class="product-visual" style="--bg:${p.bg}"><span class="product-tag ${p.stock===0?'sold-out':''}">${escapeHTML(p.tag)}</span>${p.image?`<img class="product-image" src="${escapeHTML(p.image)}" alt="" loading="lazy">`:`<span class="product-emoji" aria-hidden="true">${p.emoji}</span>`}<button type="button" class="quick-add" data-add="${p.id}" aria-label="${p.stock===0?'Sin stock: ': 'Agregar al carrito: '}${escapeHTML(p.name)}" ${p.stock===0?'disabled':''}>${p.stock===0?'Agotado':'+'}</button></div><div class="product-info"><span class="product-category">${escapeHTML(p.category)}</span><h3 class="product-name">${escapeHTML(p.name)}</h3>${p.description?`<p class="product-description">${escapeHTML(p.description)}</p>`:''}<span class="product-price">${money(p.price)}</span><span class="product-stock">${p.stock>0?`${p.stock} disponibles`:'Sin unidades disponibles'}</span></div></article>`).join(''):`<div class="empty-results">${products.length?'No hay productos que coincidan. Probá otra búsqueda o categoría.':'Todavía no hay productos disponibles. El local puede cargarlos desde Ingresos.'}</div>`;
}
function validCart() { return apiReady && cart.length>0 && cart.every(item => {const p=products.find(x=>x.id===Number(item.id));return p && item.qty>0 && item.qty<=p.stock;}); }
function addToCart(id) { const p=products.find(x=>x.id===id); if(!apiReady||!p||p.stock<1)return showToast('Este producto no tiene unidades disponibles.'); const item=cart.find(x=>x.id===id); if(item&&item.qty>=p.stock)return showToast('Ya agregaste todas las unidades disponibles.'); item?item.qty++:cart.push({id,qty:1}); saveCart(); showToast(`${p.name} se agregó al carrito.`); }
function renderCart() {
  const count=cart.reduce((n,x)=>n+x.qty,0); document.querySelector('#cart-count').textContent=count; document.querySelector('#cart-title-count').textContent=`(${count})`;
  const items=document.querySelector('#cart-items');
  items.innerHTML=cart.map(item=>{const p=products.find(y=>y.id===Number(item.id));if(!p)return `<div class="cart-row needs-review"><div class="cart-item-details"><b>Producto #${Number(item.id)}</b><small>No pudimos verificar su información.</small><button type="button" class="remove-item" data-remove="${Number(item.id)}">Quitar</button></div></div>`;const over=item.qty>p.stock;return `<div class="cart-row ${over?'needs-review':''}"><div class="cart-thumb" style="--bg:${p.bg}" aria-hidden="true">${p.image?`<img src="${escapeHTML(p.image)}" alt="" loading="lazy">`:p.emoji}</div><div class="cart-item-details"><b>${escapeHTML(p.name)}</b><small>${money(p.price)} por unidad</small><div class="quantity"><button type="button" data-qty="${p.id}" data-delta="-1" aria-label="Quitar una unidad de ${escapeHTML(p.name)}">−</button><span>${item.qty}</span><button type="button" data-qty="${p.id}" data-delta="1" aria-label="Agregar una unidad de ${escapeHTML(p.name)}" ${item.qty>=p.stock?'disabled':''}>+</button><button type="button" class="remove-item" data-remove="${p.id}">Quitar</button></div>${over?`<small class="availability-warning">Pediste ${item.qty}; ahora solo quedan ${p.stock}. Ajustá la cantidad.</small>`:''}${p.stock===0?'<small class="availability-warning">Agotado. Quitalo o esperá a que vuelva a estar disponible.</small>':''}</div><span class="cart-line-total">${money(p.price*item.qty)}</span></div>`;}).join('');
  document.querySelector('#cart-total').textContent=money(cart.reduce((n,x)=>n+(products.find(p=>p.id===Number(x.id))?.price||0)*x.qty,0));
  const empty=cart.length===0; document.querySelector('#cart-empty').hidden=!empty; document.querySelector('#cart-bottom').hidden=empty;
  document.querySelector('#checkout').disabled=!validCart();
  document.querySelector('#cart-warning').hidden=validCart()||empty;
}
function setCart(open) {
  const panel=document.querySelector('#cart-panel');
  if(open){lastFocus=document.activeElement;panel.classList.add('open');panel.setAttribute('aria-hidden','false');document.querySelector('#overlay').hidden=false;document.body.style.overflow='hidden';document.querySelector('#close-cart').focus();}
  else {const wasOpen=panel.classList.contains('open');panel.classList.remove('open');panel.setAttribute('aria-hidden','true');document.querySelector('#overlay').hidden=true;document.body.style.overflow='';if(wasOpen)(lastFocus?.isConnected?lastFocus:document.querySelector('#open-cart')).focus();}
}
grid.addEventListener('click',e=>{if(e.target.closest('[data-retry-catalog]')){loadCatalog({showStatus:true});return;}const b=e.target.closest('[data-add]');if(b&&!b.disabled)addToCart(Number(b.dataset.add));});
document.querySelector('#filters').addEventListener('click',e=>{const b=e.target.closest('[data-category]');if(!b)return;category=b.dataset.category;document.querySelectorAll('.filter').forEach(x=>x.classList.toggle('active',x===b));renderProducts();});
document.querySelector('#search').addEventListener('input',renderProducts);
document.querySelector('#cart-items').addEventListener('click',e=>{const q=e.target.closest('[data-qty]'),r=e.target.closest('[data-remove]');if(r)cart=cart.filter(x=>x.id!==Number(r.dataset.remove));if(q){const item=cart.find(i=>i.id===Number(q.dataset.qty)),p=products.find(i=>i.id===Number(q.dataset.qty)),delta=Number(q.dataset.delta);if(item&&delta<0){item.qty--;if(item.qty<1)cart=cart.filter(i=>i!==item);}else if(item&&p&&delta>0&&item.qty<p.stock)item.qty++;}saveCart();});
document.querySelector('#open-cart').addEventListener('click',()=>setCart(true));document.querySelector('#close-cart').addEventListener('click',()=>setCart(false));document.querySelector('#overlay').addEventListener('click',()=>setCart(false));document.querySelector('#keep-shopping').addEventListener('click',()=>setCart(false));
document.querySelector('#refresh-stock').addEventListener('click',()=>loadCatalog({showStatus:true}));
document.addEventListener('keydown',e=>{const panel=document.querySelector('#cart-panel');if(!panel.classList.contains('open'))return;if(e.key==='Escape'){setCart(false);return;}if(e.key==='Tab'){const focusable=[...panel.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),textarea:not(:disabled)')].filter(el=>!el.hidden);if(!focusable.length)return;const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}});
document.querySelector('#checkout').addEventListener('click',()=>{if(!validCart())return showToast('Actualizá la disponibilidad y revisá las cantidades.');setCart(false);document.querySelector('#checkout-summary').textContent=money(cart.reduce((sum,item)=>sum+(products.find(p=>p.id===item.id)?.price||0)*item.qty,0));document.querySelector('#checkout-fields').hidden=false;document.querySelector('#order-confirmation').hidden=true;document.querySelector('#checkout-dialog').setAttribute('aria-labelledby','checkout-title');document.querySelector('#checkout-dialog').showModal();document.querySelector('#checkout-title').focus({preventScroll:true});});
document.querySelector('#close-checkout').addEventListener('click',()=>document.querySelector('#checkout-dialog').close());
document.querySelector('#close-confirmation').addEventListener('click',()=>document.querySelector('#checkout-dialog').close());
document.querySelector('#checkout-form').addEventListener('submit',async e=>{
  e.preventDefault();if(!validCart()){showToast('Revisá el stock antes de enviar la reserva.');return;}
  const snapshot=cart.map(item=>({product:products.find(p=>p.id===item.id),qty:item.qty}));
  const total=snapshot.reduce((sum,line)=>sum+line.product.price*line.qty,0);
  const button=document.querySelector('#send-order');button.disabled=true;button.textContent='Enviando reserva…';
  const form=new FormData(e.currentTarget);
  try{
    const response=await fetch('./api.php?action=orders',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({nombre:form.get('name'),telefono:form.get('phone'),entrega:form.get('delivery'),comentario:form.get('note'),items:cart.map(item=>({id:item.id,cantidad:item.qty}))})});
    const result=await response.json().catch(()=>({error:'El servidor devolvió una respuesta inválida.'}));
    if(response.status===409){await loadCatalog({showStatus:true});throw new Error('El stock cambió mientras preparabas el pedido. Revisá las cantidades y volvé a intentarlo.');}
    if(!response.ok)throw new Error(result.error||'No se pudo registrar la reserva.');
    document.querySelector('#confirmation-id').textContent=`Reserva #${result.order_id}`;
    const confirmedItems=Array.isArray(result.items)?result.items:snapshot.map(line=>({nombre:line.product.name,cantidad:line.qty,precio_unitario:line.product.price}));
    document.querySelector('#confirmation-items').innerHTML=confirmedItems.map(line=>`<li>${Number(line.cantidad)} × ${escapeHTML(line.nombre)} <span>${money(Number(line.precio_unitario)*Number(line.cantidad))}</span></li>`).join('');
    document.querySelector('#confirmation-total').textContent=money(Number(result.total));
    document.querySelector('#checkout-fields').hidden=true;document.querySelector('#order-confirmation').hidden=false;document.querySelector('#checkout-dialog').setAttribute('aria-labelledby','confirmation-title');
    cart=[];saveCart();e.currentTarget.reset();document.querySelector('#checkout-dialog').querySelector('#confirmation-title').focus({preventScroll:true});
  }catch(error){showToast(error.message);}
  finally{button.disabled=false;button.innerHTML='Solicitar reserva <span>→</span>';}
});
document.querySelector('#checkout-dialog').addEventListener('close',()=>{document.querySelector('#checkout-dialog').setAttribute('aria-labelledby','checkout-title');document.querySelector('#open-cart').focus();});
const menuToggle=document.querySelector('#menu-toggle'), mainNav=document.querySelector('#main-nav');
menuToggle.addEventListener('click',()=>{const open=menuToggle.getAttribute('aria-expanded')!=='true';menuToggle.setAttribute('aria-expanded',String(open));mainNav.classList.toggle('open',open);});
mainNav.addEventListener('click',e=>{if(e.target.closest('a')){menuToggle.setAttribute('aria-expanded','false');mainNav.classList.remove('open');}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menuToggle.getAttribute('aria-expanded')==='true'){menuToggle.setAttribute('aria-expanded','false');mainNav.classList.remove('open');menuToggle.focus();}});
document.querySelector('#year').textContent=new Date().getFullYear();renderCart();loadStoreConfig();loadCatalog();

# Manual de usuario · Milonga Bazar

## Qué hace el sistema

La app de escritorio administra productos, categorías, costos, precios y stock. La tienda local muestra los productos publicados y recibe solicitudes de reserva. Ambos programas comparten `Sistema/App/milonga_datos.db`.

Las reservas web no se cobran en línea: el local debe contactar al cliente para confirmar disponibilidad, pago y entrega. La versión actual está pensada para uso local en una computadora.

## Iniciar los dos programas

1. Abrí PowerShell y ejecutá:

   ```powershell
   cd D:\2026\Bazar\Sistema\App
   python -m pip install -r requirements.txt
   python main.py
   ```

2. En otra ventana de PowerShell ejecutá:

   ```powershell
   cd D:\2026\Bazar\Sistema\Web
   C:\xampp\php\php.exe -S 127.0.0.1:8000
   ```

3. Abrí `http://127.0.0.1:8000/` en el navegador. Para detener PHP, volvé a esa ventana y presioná `Ctrl+C`.

## Cargar un producto o reponer unidades

1. Entrá a **Ingresos**.
2. Escribí al menos dos letras. Las coincidencias aparecen debajo del nombre; podés seleccionarlas con mouse o teclado.
3. Si terminás de escribir un nombre que ya existe, se completan automáticamente categoría, descripción, costo, precio y estado de la foto. La cantidad queda vacía para que ingreses las unidades que recibiste.
4. Si elegís un producto sugerido, se completan esos mismos datos. Al guardar, las unidades se suman a su stock. Si no hay coincidencia y no elegís una sugerencia, se crea un producto nuevo.
5. Para crear una categoría nueva, presioná **Agregar categoría**, escribí el nombre y confirmá.
6. Si querés, agregá una descripción breve que verá la gente en la tienda.
7. Ingresá unidades, costo de compra y precio de venta.
8. Opcionalmente, elegí una foto JPG, PNG o WebP de hasta 8 MB.
9. Presioná **Guardar en inventario**.

El costo de compra ingresado en cada operación queda guardado en el historial de movimientos. Aunque después cambies el precio de compra del producto, los egresos históricos reflejan el costo real de cada ingreso.

## Buscar, editar y retirar productos

- En **Stock actual**, escribí nombre o categoría.
- **Editar** permite corregir unidades, precio y foto. Las diferencias de stock se anotan como ajuste.
- **Movimientos** muestra ingresos, reservas web, cancelaciones, ventas locales y ajustes.
- **Retirar del catálogo** deja el producto y su historial guardados, pero fija stock y precio en cero.
- **Avisos** muestra productos con stock bajo.
- Usá **A+** y **A−** en el menú lateral para cambiar el tamaño de los controles.

## Registrar una venta del local

1. Entrá a **Ventas y pedidos** y elegí **Nueva venta local**.
2. Buscá el producto, elegilo en la lista y agregá las unidades con **+**.
3. Seleccioná el medio de pago y revisá el total.
4. Presioná **Confirmar venta** una sola vez.
5. **Historial local** permite revisar las 100 ventas más recientes y anular una venta completa.

## Gestionar una reserva web

1. En **Ventas y pedidos**, el filtro inicial muestra pedidos pendientes.
2. Usá **Empezar preparación**, **Marcar listo para entregar** y **Marcar como entregado** según corresponda.
3. Si se cancela una reserva, usá **Cancelar y reponer stock**.

## Ver el balance

Entrá a **Balance** para ver un resumen de los últimos 3 meses calendario (mes actual y los dos anteriores). Para cada mes se muestra:

- **Ventas locales**: total de ventas de mostrador registradas, sin contar las anuladas.
- **Pedidos web entregados**: total de pedidos de la tienda marcados como entregados, sin contar cancelados ni pendientes.
- **Compras de mercadería**: suma de `cantidad × costo unitario` de cada ingreso de stock. Solo se incluyen los ingresos realizados con esta versión del sistema, que guarda el costo en el momento del ingreso. Los movimientos anteriores sin ese dato aparecen con un aviso y se excluyen del cálculo.
- **Gastos manuales**: gastos registrados con el botón **Registrar gasto**.
- **Balance neto**: ingresos menos egresos del mes.

Al pie se muestra el total acumulado del período.

## Registrar un gasto manual

1. Entrá a **Balance** y presioná **Registrar gasto**.
2. Completá la fecha en formato `AAAA-MM-DD`, una descripción y el importe.
3. Presioná **Guardar gasto**.

Usá esta función para registrar bolsas, fletes, servicios u otros gastos que no corresponden a ingresos de mercadería.

## Fotos y archivos

Las fotos que se muestran en la tienda se guardan en `Sistema/Web/uploads`. No muevas ni renombres esos archivos desde el Explorador. Si una foto no carga, verificá que siga en esa carpeta y volvé a elegirla en **Editar**.

## Copia de seguridad y recuperación

1. Cerrá la app de escritorio y detené el servidor PHP.
2. Copiá `Sistema/App/milonga_datos.db` y toda la carpeta `Sistema/Web/uploads` a un medio separado o a una carpeta con fecha.
3. Para restaurar, detené ambos programas y reemplazá la base y la carpeta de fotos por una misma copia de respaldo.
4. Abrí primero la app de escritorio para que aplique migraciones de esquema y luego iniciá PHP.

Guardá la base y las fotos juntas: la base guarda las rutas de imagen, no los archivos de imagen.

## Límites de esta versión local

- Solo es accesible desde esta computadora (`127.0.0.1`). No publiques el servidor PHP en Internet ni compartas la base SQLite por una carpeta de red.
- No incluye pagos online, facturación fiscal, impresión de comprobantes, usuarios/roles ni sincronización entre varias cajas.
- Los productos con precio cero se ocultan del catálogo y no se pueden vender.

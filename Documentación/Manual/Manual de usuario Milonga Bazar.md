![Logotipo de Milonga](../../Sistema/Web/assets/logo-milonga.png)

# Milonga Bazar

## Manual de inicio y operación

Versión local para una computadora

Guía para iniciar, operar y cuidar los datos del sistema

### Contenido

- 1 Propósito y alcance
- 2 Requisitos y preparación
- 3 Iniciar y cerrar el sistema
  - 3.1 Aplicación de escritorio
  - 3.2 Tienda web
- 4 Cargar mercadería
- 5 Consultar y editar inventario
- 6 Registrar una venta local
- 7 Atender solicitudes de la tienda
  - 7.1 Recorrido del cliente
  - 7.2 Gestión en el local
- 8 Consultar el balance y registrar gastos
- 9 Accesibilidad y navegación
- 10 Respaldo y recuperación
  - 10.1 Crear una copia
  - 10.2 Restaurar una copia
- 11 Solución de problemas
- 12 Límites y cuidado de la información
- 13 Referencia rápida

# 1 Propósito y alcance

Este manual explica cómo iniciar y usar el inventario de escritorio y la tienda web local. Ambos programas trabajan sobre Sistema/App/milonga_datos.db. El sistema está preparado para una sola computadora y no cobra ni factura desde la tienda.

# 2 Requisitos y preparación

- Windows con Python 3 instalado.
- PHP de XAMPP con PDO SQLite habilitado.
- Dependencias de Python instaladas desde Sistema/App/requirements.txt.
- Navegador actualizado.
- Copia de respaldo de la base y Sistema/Web/uploads antes de migrar o mover el proyecto.

# 3 Iniciar y cerrar el sistema

## 3.1 Aplicación de escritorio

Abrí PowerShell y ejecutá:

```powershell
cd D:\2026\Bazar\Sistema\App
python -m pip install -r requirements.txt
python main.py
```

Instalá dependencias una vez y repetí el comando si cambia requirements.txt. "Requirement already satisfied" indica que el paquete ya está instalado; por sí solo no es un error.

## 3.2 Tienda web

En otra ventana de PowerShell ejecutá:

```powershell
cd D:\2026\Bazar\Sistema\Web
C:\xampp\php\php.exe -S 127.0.0.1:8000
```

Abrí http://127.0.0.1:8000/ en el navegador. Dejá activas ambas ventanas mientras trabajás. Para cerrar, volvé a la consola PHP y presioná Ctrl+C; luego cerrá la app.

# 4 Cargar mercadería

- Abrí Ingresos y escribí el nombre. La lista puede mostrar productos coincidentes.
- Elegí la sugerencia para recuperar un producto existente. Al completar el nombre exacto también se completan sus datos.
- Revisá categoría, descripción, costo y precio. Ingresá la cantidad recibida; este campo se completa en cada ingreso.
- Si no elegís un producto existente, completá el formulario para crear uno nuevo.
- Para una categoría nueva, usá Agregar categoría y guardala antes de seleccionarla.
- Si corresponde, elegí una imagen JPG, PNG o WebP de hasta 8 MB. Guardá el ingreso.

El costo de compra ingresado queda guardado en el historial de movimientos. Aunque después cambies el precio de compra del producto, los egresos históricos reflejan el costo real de cada ingreso.

La búsqueda reduce el riesgo de crear variantes como "vincha" y "vinchas". Revisá la sugerencia antes de confirmar para no mezclar artículos distintos.

# 5 Consultar y editar inventario

- En Stock actual, buscá por nombre o categoría.
- Usá Editar para modificar precio, datos del catálogo, fotografía o saldo según las opciones disponibles.
- Consultá Movimientos para seguir ingresos, ajustes, ventas, reservas y devoluciones.
- Revisá Avisos para detectar stock bajo.
- Retirar del catálogo conserva el historial y evita publicar o vender el artículo fijando precio y stock en cero.

# 6 Registrar una venta local

- Entrá a Ventas y pedidos y elegí Nueva venta local.
- Buscá artículos y agregá unidades con +. La pantalla informa el stock y no debe permitir excederlo.
- Elegí medio de pago y revisá los importes.
- Confirmá una vez. La venta guarda los artículos y descuenta stock en la misma operación.
- Abrí Historial local para consultar ventas recientes. Anular y reponer stock devuelve las unidades una sola vez y conserva el registro como anulado.

El registro sirve para el control del bazar. No es una factura fiscal ni informa una terminal de cobro.

# 7 Atender solicitudes de la tienda

## 7.1 Recorrido del cliente

- Buscar y filtrar artículos.
- Agregar productos con + y revisar el carrito.
- Enviar la reserva con nombre, teléfono y modalidad de entrega; el comentario es opcional.
- Guardar el número de confirmación. El local coordina disponibilidad, pago y entrega fuera de la web.

## 7.2 Gestión en el local

- Abrí Ventas y pedidos. La vista inicial muestra pedidos pendientes. Actualizá si acaba de enviarse una reserva.
- Revisá contacto, artículos, cantidades, total estimado y modalidad de entrega.
- Usá Empezar preparación, Marcar listo para entregar y Marcar como entregado según corresponda.
- Si se cancela antes de la entrega, usá Cancelar y reponer stock. La operación no duplica la devolución si se repite.

Una reserva descuenta stock cuando se registra. Marcar Entregado no registra un pago.

# 8 Consultar el balance y registrar gastos

Entrá a **Balance** para ver el resumen de los últimos 3 meses calendario. Para cada mes se muestra:

- Ventas locales registradas (excluye anuladas).
- Pedidos web entregados (excluye cancelados y pendientes).
- Compras de mercadería: calculadas desde el costo guardado en cada ingreso, no desde el precio de compra actual del producto.
- Gastos manuales registrados con el botón **Registrar gasto**.
- Balance neto del mes.

Al pie aparece el total acumulado del período.

Si hay ingresos de mercadería anteriores a esta versión del sistema, aparece un aviso indicando que esos movimientos no tienen costo registrado y se excluyen del cálculo de egresos de compras.

Para registrar un gasto manual:

1. Presioná **Registrar gasto**.
2. Completá la fecha en formato `AAAA-MM-DD`, una descripción y el importe.
3. Presioná **Guardar gasto**.

Usá esta función para bolsas, fletes, servicios u otros gastos que no corresponden a ingresos de mercadería.

# 9 Accesibilidad y navegación

- Usá A+ y A− en el menú lateral para ajustar el tamaño de controles; la preferencia se guarda localmente.
- En pantallas chicas, la tienda adapta navegación y tarjetas.
- La búsqueda y los filtros ayudan a reducir el recorrido.
- Abrí el carrito para revisar cantidades y subtotal antes de enviar la reserva.

# 10 Respaldo y recuperación

## 10.1 Crear una copia

- Cerrá la aplicación y detené PHP.
- Copiá Sistema/App/milonga_datos.db.
- Copiá completa la carpeta Sistema/Web/uploads.
- Copiá Sistema/Web/tienda.json para conservar dirección y foto de portada.
- Opcionalmente, copiá Sistema/App/preferencias.json para conservar el tamaño de controles elegido.
- Guardá estos archivos y carpetas juntos en una carpeta identificada con la fecha.

## 10.2 Restaurar una copia

- Detené los dos programas.
- Reemplazá la base, la carpeta de fotos y, si la respaldaste, tienda.json con archivos de la misma copia.
- Iniciá primero la app para que aplique migraciones.
- Iniciá PHP y revisá el catálogo.

# 11 Solución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| La tienda no abre | Confirmá que PHP continúa ejecutándose y que la URL sea 127.0.0.1:8000. |
| No aparecen productos | Comprobá la carpeta del proyecto y que los artículos tengan precio de venta mayor que cero. |
| Error SQLite en PHP | Verificá que PHP de XAMPP tenga habilitado PDO SQLite. |
| No carga una foto | Verificá que el archivo siga en Sistema/Web/uploads y volvé a elegirlo desde la app. |
| Requirement already satisfied | Es informativo: pip encontró el paquete instalado. |
| Excepción al usar A− o A+ | Se reportó un TclError relacionado con un menú desplegable CustomTkinter. No se confirmó solución; anotá los pasos y el momento del error. |
| El balance muestra un aviso de movimientos sin costo | Son ingresos anteriores a la versión actual. Se excluyen del cálculo; los nuevos ingresos sí guardan el costo. |

# 12 Límites y cuidado de la información

- La tienda escucha en la PC local y no debe publicarse ni reenviarse desde el router.
- No uses la misma base SQLite desde una carpeta de red ni varias computadoras.
- No hay pagos online, facturación, cuentas ni perfiles de acceso.
- Las reservas guardan datos de contacto. Protegé el equipo y los respaldos, y conservá esos datos solo el tiempo necesario.
- El catálogo depende de los archivos de uploads; incluí la carpeta completa en cada respaldo.

# 13 Referencia rápida

| Tarea | Pantalla o ruta |
| --- | --- |
| Ingresar mercadería | Ingresos |
| Revisar y ajustar saldo | Stock actual y Movimientos |
| Crear categoría | Ingresos → Agregar categoría |
| Registrar venta | Ventas y pedidos → Nueva venta local |
| Preparar reserva web | Ventas y pedidos |
| Ver balance mensual | Balance |
| Registrar gasto manual | Balance → Registrar gasto |
| Ubicación de la base | Sistema/App/milonga_datos.db |
| Fotos y configuración | Sistema/Web/uploads y tienda.json |

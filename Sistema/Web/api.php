<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function respond(int $status, array $body): never {
    http_response_code($status);
    echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

$transactionOpen = false;
try {
    if (!extension_loaded('pdo_sqlite')) {
        throw new RuntimeException('PHP necesita tener habilitado PDO SQLite.');
    }

    // Coincide con la ubicación establecida en App/database.py.
    $dbPath = dirname(__DIR__) . DIRECTORY_SEPARATOR . 'App' . DIRECTORY_SEPARATOR . 'milonga_datos.db';
    $db = new PDO('sqlite:' . $dbPath, null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
    $db->exec('PRAGMA foreign_keys = ON');
    $db->exec('CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT,
        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
        precio_compra REAL,
        precio_venta REAL NOT NULL DEFAULT 0
    )');
    $productColumns = $db->query('PRAGMA table_info(productos)')->fetchAll(PDO::FETCH_COLUMN, 1);
    if (!in_array('imagen', $productColumns, true)) {
        $db->exec('ALTER TABLE productos ADD COLUMN imagen TEXT');
    }
    if (!in_array('descripcion', $productColumns, true)) {
        $db->exec('ALTER TABLE productos ADD COLUMN descripcion TEXT');
    }
    $db->exec('CREATE TABLE IF NOT EXISTS pedidos_web (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        cliente TEXT NOT NULL,
        telefono TEXT NOT NULL,
        entrega TEXT NOT NULL,
        comentario TEXT,
        total REAL NOT NULL,
        estado TEXT NOT NULL DEFAULT \'Pendiente de coordinación\'
    )');
    $db->exec('CREATE TABLE IF NOT EXISTS pedido_web_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL REFERENCES pedidos_web(id),
        producto_id INTEGER NOT NULL REFERENCES productos(id),
        nombre_producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL CHECK (cantidad > 0),
        precio_unitario REAL NOT NULL
    )');
    $db->exec('CREATE TABLE IF NOT EXISTS movimientos_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER REFERENCES productos(id),
        fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        tipo TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        stock_resultante INTEGER,
        detalle TEXT
    )');

    $action = $_GET['action'] ?? '';
    if ($action === 'products' && $_SERVER['REQUEST_METHOD'] === 'GET') {
        $rows = $db->query('SELECT id, nombre, categoria, stock, precio_venta, imagen, descripcion FROM productos WHERE precio_venta > 0 ORDER BY nombre')->fetchAll(PDO::FETCH_ASSOC);
        foreach ($rows as &$row) {
            $image = is_string($row['imagen'] ?? null) ? $row['imagen'] : '';
            $safePath = preg_match('~^uploads/[A-Za-z0-9._-]+$~', $image) === 1;
            $row['imagen'] = $safePath && is_file(__DIR__ . DIRECTORY_SEPARATOR . $image) ? $image : null;
        }
        unset($row);
        respond(200, ['products' => $rows]);
    }

    if ($action !== 'orders' || $_SERVER['REQUEST_METHOD'] !== 'POST') {
        respond(404, ['error' => 'Ruta no encontrada.']);
    }

    $input = json_decode(file_get_contents('php://input') ?: '', true, 512, JSON_THROW_ON_ERROR);
    if (!is_array($input)) respond(422, ['error' => 'Revisá tus datos y los productos del pedido.']);
    $name = $input['nombre'] ?? null;
    $phone = $input['telefono'] ?? null;
    $delivery = $input['entrega'] ?? null;
    $comment = $input['comentario'] ?? '';
    $items = $input['items'] ?? null;
    if (!is_string($name) || !is_string($phone) || !is_string($delivery) || !is_string($comment)) {
        respond(422, ['error' => 'Revisá tus datos y los productos del pedido.']);
    }
    $name = trim($name);
    $phone = trim($phone);
    $delivery = trim($delivery);
    $comment = trim($comment);
    if ($name === '' || strlen($name) > 300 || $phone === '' || strlen($phone) > 120 || $delivery === '' || strlen($delivery) > 200 || strlen($comment) > 1000 || !is_array($items) || count($items) < 1 || count($items) > 50) {
        respond(422, ['error' => 'Revisá tus datos y los productos del pedido.']);
    }

    $quantities = [];
    foreach ($items as $item) {
        if (!is_array($item)) respond(422, ['error' => 'Hay un artículo inválido en el pedido.']);
        $id = filter_var($item['id'] ?? null, FILTER_VALIDATE_INT);
        $qty = filter_var($item['cantidad'] ?? null, FILTER_VALIDATE_INT);
        if (!$id || !$qty || $qty < 1 || $qty > 99) respond(422, ['error' => 'Hay una cantidad inválida en el pedido.']);
        $quantities[$id] = ($quantities[$id] ?? 0) + $qty;
        if ($quantities[$id] > 99) respond(422, ['error' => 'La cantidad solicitada es demasiado grande.']);
    }

    // Bloquea escrituras concurrentes y verifica el stock antes de modificarlo.
    $db->exec('BEGIN IMMEDIATE');
    $transactionOpen = true;
    $select = $db->prepare('SELECT id, nombre, stock, precio_venta FROM productos WHERE id = :id');
    $update = $db->prepare('UPDATE productos SET stock = stock - :qty WHERE id = :id AND stock >= :qty');
    $selected = [];
    $total = 0.0;
    foreach ($quantities as $id => $qty) {
        $select->execute([':id' => $id]);
        $product = $select->fetch(PDO::FETCH_ASSOC);
        if (!$product || (int)$product['stock'] < $qty || (float)$product['precio_venta'] <= 0) {
            $db->exec('ROLLBACK');
            $transactionOpen = false;
            respond(409, ['error' => 'Cambió la disponibilidad de un producto. Actualizá el catálogo e intentá de nuevo.']);
        }
        $product['cantidad'] = $qty;
        $selected[] = $product;
        $total += (float)$product['precio_venta'] * $qty;
    }

    $insertOrder = $db->prepare('INSERT INTO pedidos_web(cliente, telefono, entrega, comentario, total) VALUES (:cliente, :telefono, :entrega, :comentario, :total)');
    $insertOrder->execute([':cliente' => $name, ':telefono' => $phone, ':entrega' => $delivery, ':comentario' => $comment, ':total' => $total]);
    $orderId = (int)$db->lastInsertId();
    $insertItem = $db->prepare('INSERT INTO pedido_web_items(pedido_id, producto_id, nombre_producto, cantidad, precio_unitario) VALUES (:pedido, :producto, :nombre, :cantidad, :precio)');
    foreach ($selected as $product) {
        $update->execute([':qty' => $product['cantidad'], ':id' => $product['id']]);
        if ($update->rowCount() !== 1) {
            $db->exec('ROLLBACK');
            $transactionOpen = false;
            respond(409, ['error' => 'No hay stock suficiente para completar el pedido.']);
        }
        $insertItem->execute([':pedido' => $orderId, ':producto' => $product['id'], ':nombre' => $product['nombre'], ':cantidad' => $product['cantidad'], ':precio' => $product['precio_venta']]);
        $movement = $db->prepare("INSERT INTO movimientos_stock(producto_id,tipo,cantidad,stock_resultante,detalle) VALUES(:id,'Reserva web',:quantity,:stock,:detail)");
        $movement->execute([':id' => $product['id'], ':quantity' => -(int)$product['cantidad'], ':stock' => (int)$product['stock'] - (int)$product['cantidad'], ':detail' => 'Pedido #' . $orderId]);
    }
    $db->exec('COMMIT');
    $transactionOpen = false;
    $confirmedItems = array_map(static fn(array $item): array => ['nombre' => $item['nombre'], 'cantidad' => $item['cantidad'], 'precio_unitario' => (float)$item['precio_venta']], $selected);
    respond(201, ['order_id' => $orderId, 'total' => $total, 'status' => 'Pendiente de coordinación', 'items' => $confirmedItems]);
} catch (JsonException $error) {
    respond(422, ['error' => 'El formato de la solicitud no es válido.']);
} catch (Throwable $error) {
    if ($transactionOpen && isset($db) && $db instanceof PDO) {
        try { $db->exec('ROLLBACK'); } catch (Throwable $ignored) {}
    }
    error_log('Milonga Bazar API: ' . $error->getMessage());
    respond(500, ['error' => 'No se pudo completar la solicitud. Revisá la configuración del servidor.']);
}


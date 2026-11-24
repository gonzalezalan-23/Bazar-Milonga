<?php
// Apache suele priorizar index.php sobre index.html; servimos la nueva tienda integrada.
readfile(__DIR__ . '/index.html');

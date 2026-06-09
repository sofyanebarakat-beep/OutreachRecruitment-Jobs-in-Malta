<?php
// Static site router — intercepts WordPress before any DB connection.
// wp-load.php requires this file; we handle the request and exit early.

header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$ext  = pathinfo($path, PATHINFO_EXTENSION);

// Let PHP admin files and wp-* paths fall through to WordPress
if ($ext === 'php' || strpos($path, '/wp-') === 0) {
    // Define minimum constants so wp-load.php doesn't fatal-error
    define('DB_NAME',     'disabled');
    define('DB_USER',     'disabled');
    define('DB_PASSWORD', 'disabled');
    define('DB_HOST',     'localhost');
    define('DB_CHARSET',  'utf8');
    define('DB_COLLATE',  '');
    $table_prefix = 'wp_';
    define('ABSPATH', dirname(__FILE__) . '/');
    return; // Let WordPress continue loading for admin paths
}

$path = rtrim($path, '/');
$path = str_replace('..', '', $path);
$base = __DIR__;

// Homepage
if ($path === '') {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . '/index.html');
    exit;
}

// /employers → employers.html
if (file_exists($base . $path . '.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '.html');
    exit;
}

// /jobs/ → jobs/index.html
if (file_exists($base . $path . '/index.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '/index.html');
    exit;
}

// 404
http_response_code(404);
header('Content-Type: text/html; charset=utf-8');
readfile(file_exists($base . '/404.html') ? $base . '/404.html' : $base . '/index.html');
exit;

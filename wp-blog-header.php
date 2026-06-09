<?php
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = rtrim($path, '/');
$path = str_replace('..', '', $path);
$base = __DIR__;

// Static assets served directly by nginx — skip
if ($path !== '' && pathinfo($path, PATHINFO_EXTENSION) !== '') {
    return;
}

// /employers -> employers.html
if ($path !== '' && file_exists($base . $path . '.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '.html');
    exit;
}

// /jobs/ -> jobs/index.html
if ($path !== '' && file_exists($base . $path . '/index.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '/index.html');
    exit;
}

// Homepage
header('Content-Type: text/html; charset=utf-8');
readfile($base . '/index.html');
exit;

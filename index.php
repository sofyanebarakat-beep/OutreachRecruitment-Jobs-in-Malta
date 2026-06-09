<?php
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = rtrim($path, '/');
$path = str_replace(['..', '//'], '', $path);
$base = __DIR__;

// Serve existing files (assets, CSS, JS, images) directly
if ($path !== '' && pathinfo($path, PATHINFO_EXTENSION) !== '') {
    return false;
}

// Try exact .html match  (/employers -> employers.html)
if ($path !== '' && file_exists($base . $path . '.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '.html');
    exit;
}

// Try /index.html  (/jobs/ -> jobs/index.html)
if (file_exists($base . $path . '/index.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '/index.html');
    exit;
}

// Fallback: serve homepage
header('Content-Type: text/html; charset=utf-8');
readfile($base . '/index.html');
exit;

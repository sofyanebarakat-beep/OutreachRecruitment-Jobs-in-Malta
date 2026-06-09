<?php
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$ext = pathinfo($path, PATHINFO_EXTENSION);

// Don't intercept PHP scripts or WordPress admin paths
if ($ext === 'php' ||
    strpos($path, '/wp-admin') === 0 ||
    strpos($path, '/wp-login') === 0 ||
    strpos($path, '/wp-cron') === 0) {
    return;
}

// Don't intercept static assets (nginx serves these directly)
$staticExts = ['css','js','png','jpg','jpeg','gif','svg','ico','woff','woff2','ttf','webm','mp4','pdf','webp','json','xml','txt'];
if (in_array($ext, $staticExts)) {
    return;
}

header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');

$path = rtrim($path, '/');
$path = str_replace('..', '', $path);
$base = '/html';

// Homepage
if ($path === '') {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . '/index.html');
    exit;
}

// /employers -> employers.html
if (file_exists($base . $path . '.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '.html');
    exit;
}

// /jobs/ -> jobs/index.html
if (file_exists($base . $path . '/index.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($base . $path . '/index.html');
    exit;
}

// 404 fallback — serve our custom 404 page
http_response_code(404);
header('Content-Type: text/html; charset=utf-8');
if (file_exists($base . '/404.html')) {
    readfile($base . '/404.html');
} else {
    readfile($base . '/index.html');
}
exit;

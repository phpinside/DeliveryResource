/**
 * 站点密码门禁（Vercel Edge Middleware）。
 *
 * 工作方式：
 * 1. 所有请求先经过这里，未携带有效登录 Cookie 的请求无法访问任何页面或资源。
 * 2. 页面请求（text/html）会收到一个内联的密码输入页。
 * 3. 密码提交到 /api/login（Serverless 函数）校验，通过后写入 HttpOnly Cookie。
 * 4. 携带有效 Cookie 的请求原样放行。
 *
 * 密码配置：在 Vercel 项目 Settings → Environment Variables 中设置：
 *   SITE_PASSWORD  访问密码（未设置时兜底为 change-me）
 *   SITE_SECRET    任意随机字符串（用于生成 Cookie 令牌；更换后所有已登录会话立即失效）
 */

const COOKIE_NAME = 'site_auth';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 登录有效期：7 天

async function expectedToken() {
  const password = process.env.SITE_PASSWORD || 'change-me';
  const secret = process.env.SITE_SECRET || 'please-set-SITE_SECRET';
  const data = new TextEncoder().encode(password + '|' + secret);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, '0')).join('');
}

function readCookie(request, name) {
  const header = request.headers.get('cookie');
  if (!header) return null;
  for (const part of header.split(/;\s*/)) {
    const eq = part.indexOf('=');
    if (eq > -1 && part.slice(0, eq) === name) return part.slice(eq + 1);
  }
  return null;
}

function isPageRequest(request) {
  return (request.headers.get('accept') || '').includes('text/html');
}

function loginPageResponse() {
  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<link rel="icon" href="data:,">
<title>访问验证 · 华北交付中心</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px;
    background: linear-gradient(160deg, #172f40, #203c50 55%, #2b4d63);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #273a47; }
  .card { width: min(400px, 100%); background: #fff; border-radius: 14px; padding: 44px 40px 40px;
    box-shadow: 0 24px 60px rgba(9, 24, 35, .45); text-align: center; }
  .mark { width: 56px; height: 58px; margin: 0 auto 20px; display: grid; place-items: center;
    border-radius: 6px 6px 16px 6px; background: #203c50; color: #dbc39b; }
  .mark svg { width: 30px; height: 30px; }
  .eyebrow { margin: 0; font-size: 11px; font-weight: 600; letter-spacing: 3px; color: #876638; }
  h1 { margin: 10px 0 6px; font-size: 21px; letter-spacing: 2px; color: #172f40;
    font-family: "Songti SC", "STSong", "Noto Serif CJK SC", serif; }
  .sub { margin: 0 0 26px; font-size: 13px; color: #65737d; line-height: 1.7; }
  form { display: grid; gap: 12px; }
  input { width: 100%; padding: 13px 16px; font-size: 15px; border: 1px solid #cbd6dc; border-radius: 8px; outline: none;
    transition: border-color .2s, box-shadow .2s; }
  input:focus { border-color: #35776e; box-shadow: 0 0 0 3px rgba(53, 119, 110, .18); }
  button { padding: 13px 16px; font-size: 15px; letter-spacing: 4px; color: #fff; background: #203c50;
    border: 0; border-radius: 8px; cursor: pointer; transition: background .2s; }
  button:hover { background: #876638; }
  button:disabled { opacity: .6; cursor: wait; }
  .error { margin: 2px 0 0; font-size: 12.5px; color: #b4232a; }
</style>
</head>
<body>
<main class="card">
  <div class="mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10.5" width="16" height="10" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/><circle cx="12" cy="15.5" r="1.4" fill="currentColor" stroke="none"/></svg></div>
  <p class="eyebrow">华北交付中心</p>
  <h1>访问验证</h1>
  <p class="sub">本站内容仅对授权用户开放，<br>请输入访问密码后继续。</p>
  <form id="gate-form">
    <input id="gate-password" type="password" placeholder="请输入访问密码" autocomplete="current-password" autofocus required>
    <button type="submit">进入网站</button>
    <p class="error" id="gate-error" hidden>密码不正确，请重试。</p>
  </form>
</main>
<script>
  (function () {
    var form = document.getElementById('gate-form');
    var input = document.getElementById('gate-password');
    var button = form.querySelector('button');
    var error = document.getElementById('gate-error');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var password = input.value;
      if (!password) { input.focus(); return; }
      button.disabled = true;
      button.textContent = '验证中…';
      error.hidden = true;
      fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: password })
      }).then(function (res) {
        if (!res.ok) throw new Error('unauthorized');
        location.reload();
      }).catch(function () {
        error.hidden = false;
        button.disabled = false;
        button.textContent = '进入网站';
        input.select();
      });
    });
  })();
</script>
</body>
</html>`;
  return new Response(html, {
    status: 401,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store',
    },
  });
}

export default async function middleware(request) {
  const { pathname } = new URL(request.url);

  // 登录接口本身必须始终可达
  if (pathname.startsWith('/api/')) return fetch(request);

  const token = readCookie(request, COOKIE_NAME);
  if (token && token === (await expectedToken())) return fetch(request);

  // 未登录：页面请求给密码输入页，静态资源一律 401
  if (isPageRequest(request)) return loginPageResponse();
  return new Response('Unauthorized', { status: 401, headers: { 'cache-control': 'no-store' } });
}

export const config = { matcher: '/(.*)' };

/**
 * 登录接口：POST /api/login，JSON body { password }。
 *
 * - 密码与 Vercel 环境变量 SITE_PASSWORD 比对（未设置时兜底为 change-me）。
 * - 校验通过后写入 HttpOnly Cookie（值是密码+密钥的 SHA-256，不含明文密码），
 *   Edge Middleware（middleware.js）凭该 Cookie 放行后续请求。
 */

const crypto = require('crypto');

const COOKIE_NAME = 'site_auth';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 登录有效期：7 天，与 middleware.js 保持一致

function sha256Hex(value) {
  return crypto.createHash('sha256').update(value, 'utf8').digest('hex');
}

// 先哈希再比较，保证长度一致且抗时序攻击
function safeEqual(a, b) {
  const ha = crypto.createHash('sha256').update(String(a), 'utf8').digest();
  const hb = crypto.createHash('sha256').update(String(b), 'utf8').digest();
  return crypto.timingSafeEqual(ha, hb);
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, message: 'Method Not Allowed' });
  }

  const password = (req.body && req.body.password) || '';
  const expected = process.env.SITE_PASSWORD || 'change-me';
  const secret = process.env.SITE_SECRET || 'please-set-SITE_SECRET';

  if (!password || !safeEqual(password, expected)) {
    return res.status(401).json({ ok: false, message: '密码不正确' });
  }

  const token = sha256Hex(expected + '|' + secret);
  res.setHeader(
    'Set-Cookie',
    `${COOKIE_NAME}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${COOKIE_MAX_AGE}`
  );
  return res.status(200).json({ ok: true });
};

const BASE_URL = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
import axios from "axios";

export function getToken() {
  return localStorage.getItem("access_token") || "";
}

export async function apiGet(path) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const data = await res.json();
  return { res, data };
}


export async function apiPost(path, body) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  return { res, data };
}

export async function apiDelete(path) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    data = await res.json();
  } else {
    // 不是 JSON（比如 404 HTML），读成文本，方便你调试
    const text = await res.text();
    data = { success: false, message: text };
  }

  return { res, data };
}


// ✅ 新增：安全读取（JSON / HTML / 空响应都不会炸）
async function safeRead(res) {
  const text = await res.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch (e) {
    // 不是 JSON（比如 Django 500 的 HTML 报错页）
    return { success: false, message: "非JSON响应", raw: text };
  }
}

export async function apiPostForm(path, formData) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      // ⚠️ 不要手动写 Content-Type，让浏览器自动带 boundary
    },
    body: formData,
  });

  // 兼容后端异常返回 HTML
  const text = await res.text();
  try {
    const data = JSON.parse(text);
    return { res, data };
  } catch {
    console.error("[apiPostForm] 非 JSON 响应：", { url: `${BASE_URL}${path}`, status: res.status, rawPreview: text.slice(0, 300) });
    throw new Error("后端返回非JSON（可能500）");
  }
}





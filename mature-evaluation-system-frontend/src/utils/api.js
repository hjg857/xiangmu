const BASE_URL = import.meta.env.VITE_API_BASE || "";
import axios from "axios";

export function getToken() {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("access") ||
    localStorage.getItem("token") ||
    ""
  );
}

export async function apiGet(path) {
  const token = getToken();

  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    headers
  });

  const data = await safeRead(res);

  if (res.status === 401) {
    console.warn("[apiGet] 401 未认证：", {
      path,
      tokenExists: !!token,
      data
    });

    throw new Error("登录已失效，请重新登录");
  }

  return { res, data };
}


export async function apiPost(path, body) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json"
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  });

  const data = await safeRead(res);

  if (res.status === 401) {
    console.warn("[apiPost] 401 未认证：", {
      path,
      tokenExists: !!token,
      data
    });

    throw new Error("登录已失效，请重新登录");
  }

  return { res, data };
}

export async function apiDelete(path) {
  const token = getToken();

  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method: "DELETE",
    headers
  });

  const data = await safeRead(res);

  if (res.status === 401) {
    console.warn("[apiDelete] 401 未认证：", {
      path,
      tokenExists: !!token,
      data
    });

    throw new Error("登录已失效，请重新登录");
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

  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  const data = await safeRead(res);

  if (res.status === 401) {
    console.warn("[apiPostForm] 401 未认证：", {
      path,
      tokenExists: !!token,
      data
    });

    throw new Error("登录已失效，请重新登录");
  }

  return { res, data };
}





import { auth } from "./auth";

const BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = auth.get();
  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(opts.headers ?? {}),
    },
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? `Request failed (${res.status})`);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

async function reqBlob(path: string): Promise<Blob> {
  const token = auth.get();
  const res = await fetch(`${BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.blob();
}

// No Content-Type header here — the browser sets multipart/form-data with
// the correct boundary itself when the body is a FormData instance.
async function reqForm<T>(path: string, form: FormData): Promise<T> {
  const token = auth.get();
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}

export interface Package {
  id: string;
  slug: string;
  name: string;
  price_lkr: number;
  description: string;
}

export interface Order {
  id: string;
  package_id: string;
  amount_lkr: number;
  status: string;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_orders: number;
  paid_orders: number;
  total_cvs: number;
  revenue_lkr: number;
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

export interface AdminOrder {
  id: string;
  user_id: string;
  user_email: string;
  package_id: string;
  amount_lkr: number;
  status: string;
  created_at: string;
}

export interface AdminCV {
  id: string;
  user_id: string;
  user_email: string;
  filename: string;
  status: string;
  created_at: string;
  grade_score: number | null;
  grade_feedback: string | null;
  graded_at: string | null;
}

export interface CV {
  id: string;
  filename: string;
  status: string;
  parsed: Record<string, unknown> | null;
  is_current: boolean;
  created_at: string;
  grade_score: number | null;
  grade_feedback: string | null;
  graded_at: string | null;
  grade_acknowledged: boolean;
}

export const api = {
  register: (email: string, full_name: string, password: string, phone: string) =>
    req("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, full_name, password, phone }),
    }),

  login: (email: string, password: string) =>
    req<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  googleAuth: (credential: string) =>
    req<{ access_token: string }>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential }),
    }),

  authConfig: () => req<{ google_client_id: string }>("/auth/config"),

  me: () =>
    req<{
      id: string;
      email: string;
      full_name: string;
      is_admin: boolean;
      phone: string | null;
    }>("/auth/me"),

  packages: () => req<Package[]>("/packages"),

  myOrders: () => req<Order[]>("/payments/orders"),

  admin: {
    stats: () => req<AdminStats>("/admin/stats"),
    users: () => req<AdminUser[]>("/admin/users"),
    orders: () => req<AdminOrder[]>("/admin/orders"),
    cvs: () => req<AdminCV[]>("/admin/cvs"),
    downloadCv: (id: string) => reqBlob(`/admin/cvs/${id}/download`),
    gradeCv: (id: string, score: number, feedback: string) =>
      req<AdminCV>(`/admin/cvs/${id}/grade`, {
        method: "PATCH",
        body: JSON.stringify({ score, feedback }),
      }),
  },

  uploadCV: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return reqForm<CV>("/cv/upload", form);
  },

  myCv: () => req<CV | null>("/cv/me"),

  downloadMyCv: () => reqBlob("/cv/me/download"),

  acknowledgeGrade: () => req<CV>("/cv/me/acknowledge", { method: "POST" }),

  saveAssessment: (answers: Record<string, unknown>) =>
    req("/assessment", { method: "PUT", body: JSON.stringify({ answers }) }),

  chat: (message: string) =>
    req<{ reply: string }>("/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),

  checkout: (package_id: string) =>
    req<{ order_id: string; amount_lkr: number }>("/payments/checkout", {
      method: "POST",
      body: JSON.stringify({ package_id }),
    }),

  // Dev-only: stands in for PayHere's webhook so the paid flow can be
  // tested without a PayHere sandbox account. 404s once the API is
  // running with ENVIRONMENT=production.
  simulatePaid: (orderId: string) =>
    req<Order>(`/payments/orders/${orderId}/simulate-paid`, { method: "POST" }),
};

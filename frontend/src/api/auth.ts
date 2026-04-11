import { http } from "./http";

export interface AuthPayload {
  username: string;
  password: string;
}

export interface RegisterPayload extends AuthPayload {
  confirm_password: string;
}

export interface MeResponse {
  id: number | null;
  username: string;
  is_authenticated: boolean;
  is_demo: boolean;
}

export async function ensureCsrfCookie(): Promise<void> {
  await http.get("/auth/csrf/");
}

export async function loginUser(payload: AuthPayload): Promise<MeResponse> {
  await ensureCsrfCookie();
  const response = await http.post<MeResponse>("/auth/login/", payload);
  await ensureCsrfCookie();
  return response.data;
}

export async function registerUser(payload: RegisterPayload): Promise<MeResponse> {
  await ensureCsrfCookie();
  const response = await http.post<MeResponse>("/auth/register/", payload);
  await ensureCsrfCookie();
  return response.data;
}

export async function logoutUser(): Promise<void> {
  await ensureCsrfCookie();
  await http.post("/auth/logout/");
  await ensureCsrfCookie();
}

export async function fetchMe(): Promise<MeResponse> {
  const response = await http.get<MeResponse>("/users/me/");
  return response.data;
}

import apiClient from "./apiClient";

import type { ApiSuccessResponse, User } from "@/types/auth";

export interface AuthPayload {
  username: string;
  email?: string;
  password: string;
  confirmPassword?: string;
}

interface AuthResponseData {
  user: User;
}

export async function fetchCurrentUser() {
  const response = await apiClient.get<ApiSuccessResponse<AuthResponseData>>(
    "/auth/me/",
  );
  return response.data.data.user;
}

export async function registerAccount(payload: Required<Pick<AuthPayload, "username" | "email" | "password" | "confirmPassword">>) {
  const response = await apiClient.post<ApiSuccessResponse<AuthResponseData>>("/auth/register/", {
    username: payload.username,
    email: payload.email,
    password: payload.password,
    confirm_password: payload.confirmPassword,
  });
  return response.data.data.user;
}

export async function loginAccount(payload: Required<Pick<AuthPayload, "username" | "password">>) {
  const response = await apiClient.post<ApiSuccessResponse<AuthResponseData>>("/auth/login/", payload);
  return response.data.data.user;
}

export async function logoutAccount() {
  await apiClient.post("/auth/logout/", {});
}

export async function updateProfile(payload: Pick<User, "username" | "email">) {
  const response = await apiClient.patch<ApiSuccessResponse<AuthResponseData>>("/auth/me/", payload);
  return response.data.data.user;
}

export async function requestPasswordReset(email: string) {
  await apiClient.post("/auth/password-reset/", { email });
}

export async function confirmPasswordReset(payload: { uid: string; token: string; password: string; confirmPassword: string }) {
  await apiClient.post("/auth/password-reset/confirm/", {
    uid: payload.uid,
    token: payload.token,
    password: payload.password,
    confirm_password: payload.confirmPassword,
  });
}

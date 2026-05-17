import client from './client'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { email: string; password: string }
export interface TokenResponse { access_token: string; refresh_token: string; token_type: string }

export const authApi = {
  login: (data: LoginPayload) => client.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterPayload) => client.post('/auth/register', data),
  logout: () => client.post('/auth/logout'),
}

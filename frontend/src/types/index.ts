export interface User {
  id: string
  email: string
  full_name: string
  role: {
    id: string
    name: string
  }
  department?: {
    id: string
    name: string
  }
  status: string
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

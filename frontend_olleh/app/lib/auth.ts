import { api, tokenStorage, type TokenPair } from './api-client';
import { loginSchema, signupSchema, type LoginInput, type SignupInput, type User, type TokenPair as TokenPairType } from './schemas/auth';

/**
 * Authentication API functions
 */
export const authApi = {
  /**
   * Login with email and password
   */
  login: async (credentials: LoginInput): Promise<TokenPairType> => {
    const validated = loginSchema.parse(credentials);
    const tokens = await api.post<TokenPair>('/auth/jwt/create/', {
      email: validated.email,
      password: validated.password,
    });
    
    tokenStorage.setTokens(tokens);
    return tokens;
  },

  /**
   * Register a new user
   */
  signup: async (data: SignupInput): Promise<User> => {
    const validated = signupSchema.parse(data);
    return api.post<User>('/auth/users/', {
      email: validated.email,
      password: validated.password,
      re_password: validated.re_password,
    });
  },

  /**
   * Get current authenticated user
   */
  getCurrentUser: async (): Promise<User> => {
    return api.get<User>('/auth/users/me/');
  },

  /**
   * Logout (clears tokens)
   */
  logout: (): void => {
    tokenStorage.clearTokens();
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return tokenStorage.hasTokens();
  },

  /**
   * Verify token validity
   */
  verifyToken: async (token: string): Promise<boolean> => {
    try {
      await api.post('/auth/jwt/verify/', { token });
      return true;
    } catch {
      return false;
    }
  },
};

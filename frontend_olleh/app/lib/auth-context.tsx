import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { authApi } from './auth';
import { tokenStorage } from './api-client';
import { type User } from './schemas/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, redirectTo?: string) => Promise<void>;
  signup: (email: string, password: string, rePassword: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => tokenStorage.hasTokens());
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch current user if authenticated
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['auth', 'user'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Update authentication state when user data changes
  useEffect(() => {
    if (error) {
      const hadTokens = tokenStorage.hasTokens();
      setIsAuthenticated(false);
      tokenStorage.clearTokens();
      // Only show toast if we had tokens (session expired)
      if (hadTokens) {
        toast.info('Your session has expired. Please log in again.');
      }
    } else if (user) {
      setIsAuthenticated(true);
    }
  }, [user, error]);

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: ({ email, password, redirectTo }: { email: string; password: string; redirectTo?: string }) =>
      authApi.login({ email, password }),
    onSuccess: (_, variables) => {
      setIsAuthenticated(true);
      queryClient.invalidateQueries({ queryKey: ['auth', 'user'] });
      // Redirect to the page user was trying to access, or home
      navigate(variables.redirectTo || '/', { replace: true });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Login failed. Please try again.');
    },
  });

  // Signup mutation
  const signupMutation = useMutation({
    mutationFn: ({ email, password, rePassword }: { email: string; password: string; rePassword: string }) =>
      authApi.signup({ email, password, re_password: rePassword }),
    onSuccess: () => {
      // After signup, automatically log in
      loginMutation.mutate({ email: signupMutation.variables?.email || '', password: signupMutation.variables?.password || '' });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Signup failed. Please try again.');
    },
  });

  const login = async (email: string, password: string, redirectTo?: string) => {
    await loginMutation.mutateAsync({ email, password, redirectTo });
  };

  const signup = async (email: string, password: string, rePassword: string) => {
    await signupMutation.mutateAsync({ email, password, rePassword });
  };

  const logout = () => {
    authApi.logout();
    setIsAuthenticated(false);
    queryClient.clear();
    toast.info('You have been logged out successfully.');
    navigate('/login');
  };

  const value: AuthContextType = {
    user: user || null,
    isAuthenticated,
    isLoading: isLoading || loginMutation.isPending || signupMutation.isPending,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

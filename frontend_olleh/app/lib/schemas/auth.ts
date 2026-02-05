import { z } from 'zod';

/**
 * Login schema
 */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  password: z
    .string()
    .min(1, 'Password is required'),
});

export type LoginInput = z.infer<typeof loginSchema>;

/**
 * Signup schema
 */
export const signupSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .max(254, 'Email is too long'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
  re_password: z
    .string()
    .min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.re_password, {
  message: "Passwords don't match",
  path: ['re_password'],
});

export type SignupInput = z.infer<typeof signupSchema>;

/**
 * Token pair schema
 */
export const tokenPairSchema = z.object({
  access: z.string(),
  refresh: z.string(),
});

export type TokenPair = z.infer<typeof tokenPairSchema>;

/**
 * User schema
 */
export const userSchema = z.object({
  id: z.number(),
  email: z.string().email(),
});

export type User = z.infer<typeof userSchema>;

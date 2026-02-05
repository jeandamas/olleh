import { z } from 'zod';

/**
 * Payment Mode Enum
 */
export const paymentModeEnum = z.enum(['mobile_money', 'cash', 'bank']);
export type PaymentMode = z.infer<typeof paymentModeEnum>;

/**
 * Status Enum
 */
export const statusEnum = z.enum(['pending', 'paid', 'active', 'expired', 'canceled']);
export type MembershipStatus = z.infer<typeof statusEnum>;

/**
 * Membership schema (available membership tiers)
 */
export const membershipSchema = z.object({
  id: z.number(),
  name: z.string(),
  price: z.number(),
  max_order_price: z.number(),
  description: z.string(),
  duration_days: z.number(),
  is_available: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type Membership = z.infer<typeof membershipSchema>;

/**
 * User Membership List schema (for listing user memberships)
 */
export const userMembershipListSchema = z.object({
  id: z.number(),
  user: z.number(),
  user_email: z.string().email(),
  membership: z.number(),
  membership_name: z.string(),
  membership_price: z.number(),
  status: statusEnum,
  start_date: z.string().datetime().nullable(),
  end_date: z.string().datetime().nullable(),
  payment_mode: paymentModeEnum.nullable(),
  payment_reference: z.string().nullable(),
  amount_paid: z.number().nullable(),
  is_active: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type UserMembershipList = z.infer<typeof userMembershipListSchema>;

/**
 * User Membership Detail schema (detailed view)
 */
export const userMembershipDetailSchema = z.object({
  id: z.number(),
  user: z.number(),
  user_email: z.string().email(),
  membership: z.number(),
  membership_details: membershipSchema,
  status: statusEnum,
  start_date: z.string().datetime().nullable(),
  end_date: z.string().datetime().nullable(),
  payment_mode: paymentModeEnum.nullable(),
  payment_reference: z.string().nullable(),
  amount_paid: z.number().nullable(),
  payment_confirmed_by: z.number().nullable(),
  confirmed_by_email: z.string().email(),
  payment_confirmed_at: z.string().datetime().nullable(),
  is_active: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type UserMembershipDetail = z.infer<typeof userMembershipDetailSchema>;

/**
 * User Membership Create schema
 */
export const userMembershipCreateSchema = z.object({
  membership: z.number(),
  payment_mode: paymentModeEnum.nullable().optional(),
  payment_reference: z.string().max(100).nullable().optional(),
  amount_paid: z.number().min(0).nullable().optional(),
});

export type UserMembershipCreate = z.infer<typeof userMembershipCreateSchema>;

/**
 * User Membership Update schema
 */
export const userMembershipUpdateSchema = z.object({
  payment_mode: paymentModeEnum.nullable().optional(),
  payment_reference: z.string().max(100).nullable().optional(),
  amount_paid: z.number().min(0).nullable().optional(),
});

export type UserMembershipUpdate = z.infer<typeof userMembershipUpdateSchema>;

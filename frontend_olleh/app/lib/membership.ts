import { api } from './api-client';
import type {
  Membership,
  UserMembershipList,
  UserMembershipDetail,
  UserMembershipCreate,
  UserMembershipUpdate,
} from './schemas/membership';

/**
 * Membership API functions
 */
export const membershipApi = {
  /**
   * Get all available membership tiers
   */
  getAvailableMemberships: async (): Promise<Membership[]> => {
    return api.get<Membership[]>('/api/memberships/');
  },

  /**
   * Get a specific membership tier by ID
   */
  getMembership: async (id: number): Promise<Membership> => {
    return api.get<Membership>(`/api/memberships/${id}/`);
  },

  /**
   * Get user's active membership
   */
  getActiveMembership: async (): Promise<UserMembershipDetail | null> => {
    try {
      return await api.get<UserMembershipDetail>('/api/user-memberships/active/');
    } catch (error: unknown) {
      const err = error as { status?: number };
      // 404 means no active membership
      if (err.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Get user's pending memberships
   */
  getPendingMemberships: async (): Promise<UserMembershipList[]> => {
    return api.get<UserMembershipList[]>('/api/user-memberships/pending/');
  },

  /**
   * Get all user memberships
   */
  getUserMemberships: async (): Promise<UserMembershipList[]> => {
    return api.get<UserMembershipList[]>('/api/user-memberships/');
  },

  /**
   * Get user membership history (expired and canceled)
   */
  getMembershipHistory: async (): Promise<UserMembershipList[]> => {
    return api.get<UserMembershipList[]>('/api/user-memberships/history/');
  },

  /**
   * Get a specific user membership by ID
   */
  getUserMembership: async (id: string): Promise<UserMembershipDetail> => {
    return api.get<UserMembershipDetail>(`/api/user-memberships/${id}/`);
  },

  /**
   * Create a new membership request
   */
  createMembershipRequest: async (data: UserMembershipCreate): Promise<UserMembershipCreate> => {
    return api.post<UserMembershipCreate>('/api/user-memberships/', data);
  },

  /**
   * Update payment information for a pending membership
   */
  updateMembershipPayment: async (
    id: string,
    data: UserMembershipUpdate
  ): Promise<UserMembershipUpdate> => {
    return api.patch<UserMembershipUpdate>(`/api/user-memberships/${id}/`, data);
  },

  /**
   * Cancel a membership request
   */
  cancelMembership: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/user-memberships/${id}/`);
  },
};

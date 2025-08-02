/**
 * Authentication Service using Supabase
 * Handles user authentication, authorization, and session management
 */

import { createClient, SupabaseClient, User, Session } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL!;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY!;

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  role: 'user' | 'legal_team' | 'admin';
  organization?: string;
  created_at: string;
  last_sign_in?: string;
  preferences?: {
    theme: 'light' | 'dark';
    language: string;
    notifications: boolean;
    analytics_opt_in: boolean;
  };
}

export interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
}

class AuthService {
  private supabase: SupabaseClient;
  private authStateListeners: ((state: AuthState) => void)[] = [];
  private currentState: AuthState = {
    user: null,
    profile: null,
    session: null,
    loading: true,
    error: null
  };

  constructor() {
    this.supabase = createClient(supabaseUrl, supabaseAnonKey);
    this.initializeAuth();
  }

  /**
   * Initialize authentication state
   */
  private async initializeAuth(): Promise<void> {
    try {
      // Get initial session
      const { data: { session }, error } = await this.supabase.auth.getSession();
      
      if (error) {
        this.updateState({ error: error.message, loading: false });
        return;
      }

      if (session) {
        const profile = await this.fetchUserProfile(session.user.id);
        this.updateState({
          user: session.user,
          session,
          profile,
          loading: false,
          error: null
        });
      } else {
        this.updateState({ loading: false });
      }

      // Listen for auth changes
      this.supabase.auth.onAuthStateChange(async (event, session) => {
        console.log('Auth state changed:', event, session);
        
        if (session) {
          const profile = await this.fetchUserProfile(session.user.id);
          this.updateState({
            user: session.user,
            session,
            profile,
            loading: false,
            error: null
          });
        } else {
          this.updateState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: null
          });
        }
      });

    } catch (error) {
      console.error('Auth initialization error:', error);
      this.updateState({ 
        error: 'Failed to initialize authentication', 
        loading: false 
      });
    }
  }

  /**
   * Update auth state and notify listeners
   */
  private updateState(updates: Partial<AuthState>): void {
    this.currentState = { ...this.currentState, ...updates };
    this.authStateListeners.forEach(listener => listener(this.currentState));
  }

  /**
   * Subscribe to auth state changes
   */
  onAuthStateChange(callback: (state: AuthState) => void): () => void {
    this.authStateListeners.push(callback);
    
    // Immediately call with current state
    callback(this.currentState);
    
    // Return unsubscribe function
    return () => {
      const index = this.authStateListeners.indexOf(callback);
      if (index > -1) {
        this.authStateListeners.splice(index, 1);
      }
    };
  }

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string, metadata?: {
    full_name?: string;
    organization?: string;
    role?: 'user' | 'legal_team';
  }): Promise<{ success: boolean; error?: string }> {
    try {
      this.updateState({ loading: true, error: null });

      const { data, error } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      });

      if (error) {
        this.updateState({ error: error.message, loading: false });
        return { success: false, error: error.message };
      }

      if (data.user) {
        // Create user profile
        await this.createUserProfile(data.user.id, {
          email,
          full_name: metadata?.full_name,
          organization: metadata?.organization,
          role: metadata?.role || 'user'
        });
      }

      this.updateState({ loading: false });
      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign up failed';
      this.updateState({ error: errorMessage, loading: false });
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string): Promise<{ success: boolean; error?: string }> {
    try {
      this.updateState({ loading: true, error: null });

      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) {
        this.updateState({ error: error.message, loading: false });
        return { success: false, error: error.message };
      }

      // Update last sign in
      if (data.user) {
        await this.updateUserProfile(data.user.id, {
          last_sign_in: new Date().toISOString()
        });
      }

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign in failed';
      this.updateState({ error: errorMessage, loading: false });
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Sign in with Google OAuth
   */
  async signInWithGoogle(): Promise<{ success: boolean; error?: string }> {
    try {
      const { data, error } = await this.supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });

      if (error) {
        return { success: false, error: error.message };
      }

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Google sign in failed';
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Sign out
   */
  async signOut(): Promise<{ success: boolean; error?: string }> {
    try {
      this.updateState({ loading: true });

      const { error } = await this.supabase.auth.signOut();

      if (error) {
        this.updateState({ error: error.message, loading: false });
        return { success: false, error: error.message };
      }

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign out failed';
      this.updateState({ error: errorMessage, loading: false });
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Reset password
   */
  async resetPassword(email: string): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      });

      if (error) {
        return { success: false, error: error.message };
      }

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Password reset failed';
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Update password
   */
  async updatePassword(newPassword: string): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await this.supabase.auth.updateUser({
        password: newPassword
      });

      if (error) {
        return { success: false, error: error.message };
      }

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Password update failed';
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Fetch user profile
   */
  private async fetchUserProfile(userId: string): Promise<UserProfile | null> {
    try {
      const { data, error } = await this.supabase
        .from('user_profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) {
        console.error('Error fetching user profile:', error);
        return null;
      }

      return data as UserProfile;

    } catch (error) {
      console.error('Error fetching user profile:', error);
      return null;
    }
  }

  /**
   * Create user profile
   */
  private async createUserProfile(userId: string, profileData: Partial<UserProfile>): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('user_profiles')
        .insert({
          id: userId,
          ...profileData,
          created_at: new Date().toISOString(),
          preferences: {
            theme: 'light',
            language: 'en',
            notifications: true,
            analytics_opt_in: true
          }
        });

      if (error) {
        console.error('Error creating user profile:', error);
      }

    } catch (error) {
      console.error('Error creating user profile:', error);
    }
  }

  /**
   * Update user profile
   */
  async updateUserProfile(userId: string, updates: Partial<UserProfile>): Promise<{ success: boolean; error?: string }> {
    try {
      const { error } = await this.supabase
        .from('user_profiles')
        .update(updates)
        .eq('id', userId);

      if (error) {
        return { success: false, error: error.message };
      }

      // Refresh profile in state
      const updatedProfile = await this.fetchUserProfile(userId);
      this.updateState({ profile: updatedProfile });

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Profile update failed';
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: 'user' | 'legal_team' | 'admin'): boolean {
    return this.currentState.profile?.role === role;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.currentState.user && !!this.currentState.session;
  }

  /**
   * Check if user is legal team member
   */
  isLegalTeam(): boolean {
    return this.hasRole('legal_team') || this.hasRole('admin');
  }

  /**
   * Get current auth state
   */
  getAuthState(): AuthState {
    return this.currentState;
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.currentState.user;
  }

  /**
   * Get current user profile
   */
  getCurrentProfile(): UserProfile | null {
    return this.currentState.profile;
  }

  /**
   * Get Supabase client for direct access
   */
  getSupabaseClient(): SupabaseClient {
    return this.supabase;
  }
}

// Create and export singleton instance
export const authService = new AuthService();

// Export types
export type { AuthState, UserProfile };

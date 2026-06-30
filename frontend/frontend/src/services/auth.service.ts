import { supabase } from '../lib/supabase';
import { User } from '../types';

const mapUser = (supabaseUser: any, profile: any): User => ({
  id: supabaseUser.id,
  email: supabaseUser.email ?? '',
  fullName: profile?.full_name ?? supabaseUser.user_metadata?.full_name ?? supabaseUser.email?.split('@')[0] ?? '',
  barEnrollment: profile?.bar_enrollment ?? supabaseUser.user_metadata?.bar_enrollment,
  practiceAreas: profile?.practice_areas ?? ['General Practice'],
  createdAt: supabaseUser.created_at,
});

const fetchProfile = async (userId: string) => {
  const { data } = await supabase
    .from('user_profiles')
    .select('*')
    .eq('id', userId)
    .maybeSingle();
  return data;
};

export const authService = {
  async getCurrentUser(): Promise<User | null> {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) return null;
    const profile = await fetchProfile(session.user.id);
    return mapUser(session.user, profile);
  },

  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);
    const profile = await fetchProfile(data.user.id);
    return {
      token: data.session.access_token,
      user: mapUser(data.user, profile),
    };
  },

  async signUp(
    fullName: string,
    email: string,
    barEnrollment: string,
    password: string
  ): Promise<{ token: string; user: User }> {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName } },
    });
    if (error) throw new Error(error.message);
    if (!data.user) throw new Error('Sign up failed. Please try again.');

    // Create user profile row
    await supabase.from('user_profiles').upsert({
      id: data.user.id,
      full_name: fullName,
      bar_enrollment: barEnrollment,
      practice_areas: ['General Practice'],
      email,
    });

    const user = mapUser(data.user, { full_name: fullName, bar_enrollment: barEnrollment, practice_areas: ['General Practice'] });
    return { token: data.session?.access_token ?? '', user };
  },

  async logout(): Promise<void> {
    await supabase.auth.signOut();
  },

  async resetPassword(email: string): Promise<void> {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });
    if (error) throw new Error(error.message);
  },

  async getAccessToken(): Promise<string | null> {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token ?? null;
  },

  async updateProfile(updates: { fullName?: string; barEnrollment?: string; practiceAreas?: string[] }): Promise<void> {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.user) throw new Error('Not authenticated');

    const row: Record<string, unknown> = { id: session.user.id };
    if (updates.fullName !== undefined) row.full_name = updates.fullName;
    if (updates.barEnrollment !== undefined) row.bar_enrollment = updates.barEnrollment;
    if (updates.practiceAreas !== undefined) row.practice_areas = updates.practiceAreas;

    const { error } = await supabase.from('user_profiles').upsert(row);
    if (error) throw new Error(error.message);
  },
};

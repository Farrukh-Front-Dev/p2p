/* ── Auth ────────────────────────────────────────────────────────────────────── */
export interface LoginRequest {
  login: string
  password: string
}

export interface LoginResponse {
  status: 'ok' | 'need_telegram'
  access_token?: string
  refresh_token?: string
  token_type: string
  onboarding_done: boolean
  temp_token?: string
  bot_url?: string
}

export interface VerifyCodeRequest {
  temp_token: string
  code: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  onboarding_done: boolean
}

export interface RefreshRequest {
  refresh_token: string
}

/* ── User ────────────────────────────────────────────────────────────────────── */
export interface UserPublic {
  id: string
  telegram_username?: string | null
  first_name?: string | null
  last_name?: string | null
  avatar_url?: string | null
  campus?: string | null
  core_program?: string | null
  main_track?: string | null
  coalition_name?: string | null
  level: number
  xp: number
}

export interface UserMe extends UserPublic {
  school21_login: string
  email?: string | null
  current_location?: string | null
  peer_points: number
  peer_coins: number
  languages: string[]
  is_admin: boolean
  onboarding_done: boolean
}

export interface ProfileUpdate {
  first_name?: string
  last_name?: string
  avatar_url?: string
}

/* ── Slot ────────────────────────────────────────────────────────────────────── */
export type SlotStatus =
  | 'open'
  | 'booked'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'absent'

export interface Slot {
  id: string
  reviewer_id: string
  reviewee_id?: string | null
  reviewer_project: string
  reviewee_project?: string | null
  start_time: string
  end_time: string
  actual_start?: string | null
  actual_end?: string | null
  duration_minutes?: number | null
  status: SlotStatus
  is_online: boolean
  campus: string
}

export interface SlotCreate {
  reviewer_project: string
  start_time: string
  end_time: string
  is_online: boolean
}

export interface SlotSearchResult {
  id: string
  start_time: string
  end_time: string
  campus: string
  is_online: boolean
}

/* ── Review ──────────────────────────────────────────────────────────────────── */
export interface Review {
  id: string
  slot_id: string
  author_id: string
  target_id: string
  is_positive: boolean
  comment?: string | null
}

export interface ReviewCreate {
  slot_id: string
  is_positive: boolean
  comment?: string
}

/* ── Notification ────────────────────────────────────────────────────────────── */
export interface Notification {
  id: string
  type: string
  title?: string | null
  body?: string | null
  slot_id?: string | null
  is_read: boolean
  created_at: string
}

/* ── Dashboard ───────────────────────────────────────────────────────────────── */
export interface DashboardResponse {
  user: UserMe
  xp_to_next_level: number
  active_slots: Slot[]
  unread_notifications: number
}

/* ── Leaderboard ─────────────────────────────────────────────────────────────── */
export interface LeaderboardEntry {
  id: string
  school21_login: string
  first_name?: string | null
  last_name?: string | null
  avatar_url?: string | null
  level: number
  xp: number
  count?: number
}

/* ── Onboarding ──────────────────────────────────────────────────────────────── */
export interface OnboardingStatus {
  onboarding_done: boolean
  main_track?: string | null
  languages: string[]
}

export interface Project {
  title: string
  id?: string
}

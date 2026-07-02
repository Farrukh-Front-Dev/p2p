import { Slot, UserMe, DashboardResponse, LeaderboardEntry, Notification, Project, ProfileStats, Review } from '@/shared/types/api';

const STORAGE_KEY = 'peer_learn_mock_db';

interface MockDatabaseState {
  user: UserMe;
  slots: Slot[];
  notifications: Notification[];
  reviews: Review[];
  settings: {
    languages: string[];
    campus: string;
    theme: 'light' | 'dark';
  };
  skills: Record<string, number>;
}

const DEFAULT_TEACHABLE_PROJECTS: Project[] = [
  { id: '1', title: 'libft' },
  { id: '2', title: 'get_next_line' },
  { id: '3', title: 'ft_printf' },
  { id: '4', title: 'born2beroot' },
  { id: '5', title: 'push_swap' },
  { id: '6', title: 'so_long' },
];

const DEFAULT_IN_PROGRESS_PROJECTS: Project[] = [
  { id: '7', title: 'minishell' },
  { id: '8', title: 'cub3d' },
  { id: '9', title: 'philosophers' },
  { id: '10', title: 'webserv' },
  { id: '11', title: 'ft_irc' },
];

function getInitialState(): MockDatabaseState {
  // Generate some high quality seed data so the dashboard is alive!
  const now = new Date();
  
  // Slot 1: Active booked slot where our user is receiving a peer-evaluation (reviewee)
  const slot1: Slot = {
    id: 'mock-s-1',
    reviewer_id: 'mock-u-alice', // teacher login
    reviewee_id: 'current-mock-user-id',
    reviewer_project: 'minishell',
    reviewee_project: 'minishell',
    start_time: new Date(now.getTime() + 15 * 60 * 1000).toISOString(), // starts in 15 mins
    end_time: new Date(now.getTime() + 60 * 60 * 1000).toISOString(),
    status: 'booked',
    is_online: true,
    campus: 'Yunusobod Campus',
  };

  // Slot 2: Active booked slot where our user is giving a peer-evaluation (reviewer)
  const slot2: Slot = {
    id: 'mock-s-2',
    reviewer_id: 'current-mock-user-id',
    reviewee_id: 'mock-u-bob', // student login
    reviewer_project: 'libft',
    reviewee_project: 'libft',
    start_time: new Date(now.getTime() + 120 * 60 * 1000).toISOString(), // starts in 2 hours
    end_time: new Date(now.getTime() + 165 * 60 * 1000).toISOString(),
    status: 'booked',
    is_online: false,
    campus: 'Yunusobod Campus',
  };

  // Slot 3: Open slot created by another student that we can search and book
  const slot3: Slot = {
    id: 'mock-s-3',
    reviewer_id: 'mock-u-charlie',
    reviewer_project: 'philosophers',
    start_time: new Date(now.getTime() + 180 * 60 * 1000).toISOString(),
    end_time: new Date(now.getTime() + 225 * 60 * 1000).toISOString(),
    status: 'open',
    is_online: true,
    campus: 'Yunusobod Campus',
  };

  // Slot 4: Completed slot
  const slot4: Slot = {
    id: 'mock-s-4',
    reviewer_id: 'current-mock-user-id',
    reviewee_id: 'mock-u-dave',
    reviewer_project: 'ft_printf',
    reviewee_project: 'ft_printf',
    start_time: new Date(now.getTime() - 180 * 60 * 1000).toISOString(),
    end_time: new Date(now.getTime() - 135 * 60 * 1000).toISOString(),
    status: 'completed',
    is_online: false,
    campus: 'Yunusobod Campus',
  };

  const notification1: Notification = {
    id: 'mock-n-1',
    type: 'slot_booked',
    title: 'Darsingiz band qilindi',
    body: 'Siz ochgan "libft" darsingizni @bob ismli student band qildi. Belgilangan vaqtda tayyor bo‘ling.',
    slot_id: 'mock-s-2',
    is_read: false,
    created_at: new Date(now.getTime() - 10 * 60 * 1000).toISOString(),
  };

  const notification2: Notification = {
    id: 'mock-n-2',
    type: 'point_received',
    title: 'Ball qo‘shildi!',
    body: 'Sizga muvaffaqiyatli baholash darsi uchun 1 Peer Point taqdim etildi.',
    is_read: true,
    created_at: new Date(now.getTime() - 120 * 60 * 1000).toISOString(),
  };

  const review1: Review = {
    id: 'mock-r-1',
    slot_id: 'mock-s-4',
    author_id: 'mock-u-dave',
    target_id: 'current-mock-user-id',
    is_positive: true,
    comment: 'Juda zo‘r tushuntirib berdi! Kod sirlari va xatolarimni chuqur tahlil qildik. Rahmat!',
  };

  return {
    user: {
      id: 'current-mock-user-id',
      school21_login: 's21_demo_master',
      first_name: 'Farrux',
      last_name: 'Djumayev',
      telegram_username: 'farrukh_dj',
      email: 'farrukhdjumayev0542@gmail.com',
      avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=150&auto=format&fit=crop',
      campus: 'Yunusobod Campus',
      core_program: 'School21 Core Program',
      main_track: 'Go / TypeScript Backend Developer',
      coalition_name: 'Valkyrie',
      level: 12,
      xp: 12450,
      peer_points: 7,
      peer_coins: 380,
      languages: ['Uzbek', 'English'],
      is_admin: true,
      onboarding_done: true,
    },
    slots: [slot1, slot2, slot3, slot4],
    notifications: [notification1, notification2],
    reviews: [review1],
    settings: {
      languages: ['Uzbek', 'English'],
      campus: 'Yunusobod Campus',
      theme: 'dark',
    },
    skills: {
      'C/C++ Programming': 85,
      'Algorithms': 78,
      'Docker & DevOps': 68,
      'Database Optimization': 72,
    },
  };
}

export const mockDb = {
  getState(): MockDatabaseState {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        // Fall back
      }
    }
    const state = getInitialState();
    this.saveState(state);
    return state;
  },

  saveState(state: MockDatabaseState) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  },

  reset() {
    localStorage.removeItem(STORAGE_KEY);
  },

  getMockUser(): UserMe {
    return this.getState().user;
  },

  updateMockUser(payload: Partial<UserMe>): UserMe {
    const state = this.getState();
    const updatedUser = { ...state.user, ...payload };
    state.user = updatedUser;
    this.saveState(state);
    return updatedUser;
  },

  getMockDashboard(): DashboardResponse {
    const state = this.getState();
    const now = new Date().toISOString();
    
    // active slots are those booked, start or in_progress that are relative to the user
    const curUserId = state.user.id;
    const activeSlots = state.slots.filter(s => 
      s.status !== 'completed' && 
      s.status !== 'cancelled' && 
      s.status !== 'absent' &&
      (s.reviewer_id === curUserId || s.reviewee_id === curUserId)
    );

    const unreadCount = state.notifications.filter(n => !n.is_read).length;

    // custom dynamic: make sure user level calculation feels progressive
    const level = state.user.level;
    const currentLevelBaseXp = level * level * 100;
    const nextLevelBaseXp = (level + 1) * (level + 1) * 100;
    const totalNeededForNext = nextLevelBaseXp - currentLevelBaseXp;
    const currentEarnedInLevel = Math.max(0, state.user.xp - currentLevelBaseXp);
    const xp_to_next_level = Math.max(50, totalNeededForNext - currentEarnedInLevel);

    return {
      user: state.user,
      xp_to_next_level,
      active_slots: activeSlots,
      unread_notifications: unreadCount,
    };
  },

  getMockSlots(status?: string, date?: string): Slot[] {
    const state = this.getState();
    let list = state.slots;

    if (status) {
      list = list.filter(s => s.status === status);
    }

    if (date) {
      // Basic date matching prefix comparison
      list = list.filter(s => s.start_time.startsWith(date));
    }

    return list;
  },

  createMockSlot(payload: { reviewer_project: string; start_time: string; is_online: boolean }): Slot {
    const state = this.getState();
    const now = new Date();
    
    const startObj = new Date(payload.start_time);
    const endObj = new Date(startObj.getTime() + 45 * 60 * 1000); // default 45 minutes evaluation duration

    const newSlot: Slot = {
      id: `mock-s-${now.getTime()}`,
      reviewer_id: state.user.id,
      reviewer_project: payload.reviewer_project,
      start_time: startObj.toISOString(),
      end_time: endObj.toISOString(),
      status: 'open',
      is_online: payload.is_online,
      campus: state.user.campus || 'Yunusobod Campus',
    };

    state.slots.unshift(newSlot);
    
    // Log helpful notification
    const notification: Notification = {
      id: `mock-n-${now.getTime()}`,
      type: 'slot_created',
      title: 'Yangi dars ochildi',
      body: `Siz muvaffaqiyatli "${payload.reviewer_project}" loyihasi bo‘yicha yangi bo‘sh baholash darchasi yaratdingiz.`,
      slot_id: newSlot.id,
      is_read: false,
      created_at: now.toISOString(),
    };
    state.notifications.unshift(notification);

    this.saveState(state);
    return newSlot;
  },

  getMockSlotById(id: string): Slot {
    const state = this.getState();
    const slot = state.slots.find(s => s.id === id);
    if (!slot) {
      throw new Error('Slot topilmadi');
    }
    return slot;
  },

  cancelMockSlot(id: string, reason?: string): Slot {
    const state = this.getState();
    const idx = state.slots.findIndex(s => s.id === id);
    if (idx === -1) {
      throw new Error('Slot topilmadi');
    }
    state.slots[idx].status = 'cancelled';
    
    // Add point back to booker if it was booked
    const slot = state.slots[idx];
    if (slot.reviewee_id === state.user.id) {
      state.user.peer_points += 1; // refunded
    }

    this.saveState(state);
    return slot;
  },

  bookMockSlot(id: string, reviewee_project?: string): Slot {
    const state = this.getState();
    const idx = state.slots.findIndex(s => s.id === id);
    if (idx === -1) {
      throw new Error('Slot topilmadi');
    }

    const slot = state.slots[idx];
    if (slot.status !== 'open') {
      throw new Error('Ushbu slotni band qilib bo‘lmaydi');
    }

    slot.status = 'booked';
    slot.reviewee_id = state.user.id;
    slot.reviewee_project = reviewee_project || slot.reviewer_project;

    // Deduct peer point
    if (state.user.peer_points >= 1) {
      state.user.peer_points -= 1;
    }

    // Add notification
    const now = new Date();
    const notification: Notification = {
      id: `mock-n-${now.getTime()}`,
      type: 'slot_booked',
      title: 'Siz baholash darsini band qildingiz!',
      body: `Tabriklaymiz! "${slot.reviewer_project}" bo‘yicha dars muvaffaqiyatli band qilindi. @${slot.reviewer_id} sizni tekshiradi.`,
      slot_id: slot.id,
      is_read: false,
      created_at: now.toISOString(),
    };
    state.notifications.unshift(notification);

    this.saveState(state);
    return slot;
  },

  startMockSlot(id: string): Slot {
    const state = this.getState();
    const idx = state.slots.findIndex(s => s.id === id);
    if (idx === -1) {
      throw new Error('Slot topilmadi');
    }
    state.slots[idx].status = 'in_progress';
    state.slots[idx].actual_start = new Date().toISOString();

    this.saveState(state);
    return state.slots[idx];
  },

  finishMockSlot(id: string): Slot {
    const state = this.getState();
    const idx = state.slots.findIndex(s => s.id === id);
    if (idx === -1) {
      throw new Error('Slot topilmadi');
    }

    const slot = state.slots[idx];
    slot.status = 'completed';
    slot.actual_end = new Date().toISOString();

    const isOurUserReviewer = slot.reviewer_id === state.user.id;
    if (isOurUserReviewer) {
      // Award peer points (+1) and XP (+150) for teaching/evaluating
      state.user.peer_points += 1;
      state.user.xp += 150;
      state.user.peer_coins += 15;
    } else {
      // User learned (+100 XP)
      state.user.xp += 100;
    }

    // Check level up (highly dynamic and cool!)
    const currentXp = state.user.xp;
    const currentLevel = state.user.level;
    const xpNeededForCurrentLevel = currentLevel * currentLevel * 100;
    const xpNeededForNextLevel = (currentLevel + 1) * (currentLevel + 1) * 100;
    
    if (currentXp >= xpNeededForNextLevel) {
      state.user.level += 1;
      // Add level up notification
      state.notifications.unshift({
        id: `mock-n-lvl-${Date.now()}`,
        type: 'level_up',
        title: 'TABRIKLAYMIZ! Darajangiz oshdi ⚡',
        body: `Siz School21 dagi keyingi LEVEL ${state.user.level} darajasiga erishdingiz! O‘rganishdan to‘xtamang.`,
        is_read: false,
        created_at: new Date().toISOString(),
      });
    }

    // Add completion notification
    state.notifications.unshift({
      id: `mock-n-finish-${Date.now()}`,
      type: 'slot_completed',
      title: 'Peer-Review muvaffaqiyatli yakunlandi!',
      body: `"${slot.reviewer_project}" loyihasi bo‘yicha baholash yakunlandi. Sherigingiz uchun fikr va reyting qayd qiling.`,
      slot_id: slot.id,
      is_read: false,
      created_at: new Date().toISOString(),
    });

    this.saveState(state);
    return slot;
  },

  absentMockSlot(id: string): Slot {
    const state = this.getState();
    const idx = state.slots.findIndex(s => s.id === id);
    if (idx === -1) {
      throw new Error('Slot topilmadi');
    }
    state.slots[idx].status = 'absent';
    this.saveState(state);
    return state.slots[idx];
  },

  searchMockSlots(project: string): Slot[] {
    const state = this.getState();
    const curUserId = state.user.id;
    
    // Make sure we have a couple of dummy open slots if search is empty, so they can book!
    const filtered = state.slots.filter(s => 
      s.status === 'open' && 
      s.reviewer_project.toLowerCase() === project.toLowerCase() &&
      s.reviewer_id !== curUserId
    );

    // If search gets nothing, dynamically generate 2 matching open slots for the demo,
    // so the platform is fully exploratory and pleasant!
    if (filtered.length === 0) {
      const now = new Date();
      
      const names = ['anvar_s21', 'umid_pir', 'jasur_k', 'nodira_ai', 'shavkat_dev'];
      const campuses = ['Yunusobod Campus', 'Yunusobod Campus', 'Samarkand Digital'];
      
      const mockResult1: Slot = {
        id: `mock-gen-1-${Date.now()}`,
        reviewer_id: names[Math.floor(Math.random() * names.length)],
        reviewer_project: project,
        start_time: new Date(now.getTime() + 45 * 60 * 1000).toISOString(),
        end_time: new Date(now.getTime() + 90 * 60 * 1000).toISOString(),
        status: 'open',
        is_online: true,
        campus: campuses[0],
      };

      const mockResult2: Slot = {
        id: `mock-gen-2-${Date.now()}`,
        reviewer_id: names[(Math.floor(Math.random() * names.length) + 1) % names.length],
        reviewer_project: project,
        start_time: new Date(now.getTime() + 180 * 60 * 1000).toISOString(),
        end_time: new Date(now.getTime() + 225 * 60 * 1000).toISOString(),
        status: 'open',
        is_online: false,
        campus: campuses[1],
      };

      state.slots.push(mockResult1, mockResult2);
      this.saveState(state);
      return [mockResult1, mockResult2];
    }

    return filtered;
  },

  getMockTeachableProjects(): Project[] {
    return DEFAULT_TEACHABLE_PROJECTS;
  },

  getMockInProgressProjects(): Project[] {
    return DEFAULT_IN_PROGRESS_PROJECTS;
  },

  getMockMostXP(): LeaderboardEntry[] {
    return [
      { rank: 1, user_id: 'mock-u-anvar', first_name: 'Anvar coding', last_name: 'Karimov', value: 24500 },
      { rank: 2, user_id: 'mock-u-nodira', first_name: 'Nodira AI', last_name: 'Ismailova', value: 18900 },
      { rank: 3, user_id: 'current-mock-user-id', first_name: 'Farrux', last_name: 'Djumayev', value: 12450 },
      { rank: 4, user_id: 'mock-u-umar', first_name: 'Umar rust', last_name: 'Alizoda', value: 9200 },
      { rank: 5, user_id: 'mock-u-shirin', first_name: 'Shirin web', last_name: 'Saidova', value: 8100 },
      { rank: 6, user_id: 'mock-u-jasur', first_name: 'Jasur C++', last_name: 'Nazarov', value: 7400 },
    ];
  },

  getMockMostTaught(): LeaderboardEntry[] {
    return [
      { rank: 1, user_id: 'mock-u-nodira', first_name: 'Nodira AI', last_name: 'Ismailova', value: 42 },
      { rank: 2, user_id: 'current-mock-user-id', first_name: 'Farrux', last_name: 'Djumayev', value: 28 },
      { rank: 3, user_id: 'mock-u-anvar', first_name: 'Anvar coding', last_name: 'Karimov', value: 25 },
      { rank: 4, user_id: 'mock-u-jasur', first_name: 'Jasur C++', last_name: 'Nazarov', value: 19 },
    ];
  },

  getMockMostLearned(): LeaderboardEntry[] {
    return [
      { rank: 1, user_id: 'mock-u-umar', first_name: 'Umar rust', last_name: 'Alizoda', value: 35 },
      { rank: 2, user_id: 'mock-u-shirin', first_name: 'Shirin web', last_name: 'Saidova', value: 24 },
      { rank: 3, user_id: 'current-mock-user-id', first_name: 'Farrux', last_name: 'Djumayev', value: 18 },
      { rank: 4, user_id: 'mock-u-anvar', first_name: 'Anvar coding', last_name: 'Karimov', value: 15 },
    ];
  },

  getMockNotifications(): Notification[] {
    return this.getState().notifications;
  },

  markMockNotificationAsRead(id: string) {
    const state = this.getState();
    const notification = state.notifications.find(n => n.id === id);
    if (notification) {
      notification.is_read = true;
    }
    this.saveState(state);
  },

  markMockAllNotificationsAsRead() {
    const state = this.getState();
    state.notifications.forEach(n => n.is_read = true);
    this.saveState(state);
  },

  createMockReview(payload: { slot_id: string; is_positive: boolean; comment?: string }): Review {
    const state = this.getState();
    const now = Date.now();
    const newReview: Review = {
      id: `mock-r-${now}`,
      slot_id: payload.slot_id,
      author_id: state.user.id,
      target_id: 'some-student',
      is_positive: payload.is_positive,
      comment: payload.comment || '',
    };
    state.reviews.unshift(newReview);
    this.saveState(state);
    return newReview;
  },

  getMockMyReviews(): Review[] {
    return this.getState().reviews;
  },

  getMockUserReviews(userId: string): Review[] {
    const state = this.getState();
    return state.reviews;
  },

  getMockSettings() {
    return this.getState().settings;
  },

  updateMockLanguage(lang: string) {
    const state = this.getState();
    if (!state.settings.languages.includes(lang)) {
      state.settings.languages.push(lang);
    }
    this.saveState(state);
    return { languages: state.settings.languages };
  },

  updateMockTheme(theme: 'light' | 'dark') {
    const state = this.getState();
    state.settings.theme = theme;
    this.saveState(state);
    return { theme };
  },

  getMockSkills(): Record<string, number> {
    return this.getState().skills;
  },

  getMockProfileStats(): ProfileStats {
    const state = this.getState();
    const positive_reviews = state.reviews.filter(r => r.is_positive).length;
    const negative_reviews = state.reviews.filter(r => !r.is_positive).length;
    return {
      positive_reviews,
      negative_reviews,
      all_reviews: state.reviews.length,
      taught_count: 28,
      learned_count: 18,
    };
  }
};

import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useProfile } from '@/features/profile/hooks';
import { profileService } from '@/features/profile/api';
import { reviewsService } from '@/features/reviews/api';
import { Card, Avatar, Button, Input, Spinner, Badge, Skeleton, PageHeader } from '@/shared/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  User,
  GraduationCap,
  BookOpen,
  ThumbsUp,
  ThumbsDown,
  Edit,
  Code,
  ChevronLeft,
  MessageSquare,
} from 'lucide-react';

const profileUpdateSchema = z.object({
  first_name: z.string().min(2, 'Ism kamida 2 ta belgidan iborat bo\'lishi kerak'),
  last_name: z.string().min(2, 'Familiya kamida 2 ta belgidan iborat bo\'lishi kerak'),
  avatar_url: z.string().url('To\'g\'ri rasm URL manzilini kiriting').or(z.literal('')),
});

type FormValues = z.infer<typeof profileUpdateSchema>;

export default function ProfilePage() {
  const { username } = useParams<{ username?: string }>();

  // If username is present, we show public profile; otherwise own profile
  if (username) {
    return <PublicProfileView username={username} />;
  }

  return <OwnProfileView />;
}

// ─── OWN PROFILE ────────────────────────────────────────────────────────────────

function OwnProfileView() {
  const { profile, isLoadingProfile, updateProfile, isUpdatingProfile, skills, isLoadingSkills } = useProfile();
  const [isEditing, setIsEditing] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(profileUpdateSchema),
  });

  const handleEditOpen = () => {
    if (profile?.user) {
      setValue('first_name', profile.user.first_name || '');
      setValue('last_name', profile.user.last_name || '');
      setValue('avatar_url', profile.user.avatar_url || '');
    }
    setIsEditing(true);
  };

  const onUpdateSubmit = async (values: FormValues) => {
    try {
      await updateProfile(values);
      setIsEditing(false);
    } catch (_e) { /* error handled in hook */ }
  };

  if (isLoadingProfile || !profile) {
    return (
      <div className="flex flex-col gap-4 sm:gap-6 animate-fade-in font-ibm-plex-mono text-white">
        {/* Title */}
        <div className="flex flex-col gap-2">
          <Skeleton variant="text" className="w-1/4 h-6" />
          <Skeleton variant="text" className="w-[45%] h-3.5" />
        </div>

        {/* Profile Header Card Skeleton */}
        <div className="p-4 sm:p-6 flex flex-col items-center sm:flex-row sm:items-start justify-between gap-4 sm:gap-6 rounded-3xl border-2 border-black bg-[#2A3442] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-5 w-full">
            <Skeleton variant="circle" className="h-20 w-20 sm:h-24 sm:w-24 flex-shrink-0" />
            <div className="flex flex-col items-center sm:items-start gap-2.5 w-full">
              <div className="flex items-center gap-2 w-full justify-center sm:justify-start">
                <Skeleton variant="text" className="w-32 sm:w-40 h-5" />
                <Skeleton variant="rect" className="w-20 h-5 rounded-md" />
              </div>
              <Skeleton variant="text" className="w-24 h-3.5" />
              <Skeleton variant="text" className="w-[60%] h-3" />
            </div>
          </div>
        </div>

        {/* Stats Matrix Skeleton */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-4 sm:p-5 flex flex-col gap-3 rounded-2xl border-2 border-black bg-[#2A3442] shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
              <div className="flex items-center gap-2">
                <Skeleton variant="circle" className="h-4 w-4" />
                <Skeleton variant="text" className="w-16 h-3" />
              </div>
              <Skeleton variant="text" className="w-12 h-8" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const { user, stats } = profile;

  return (
    <div className="flex flex-col gap-4 sm:gap-6 animate-fade-in font-ibm-plex-mono text-white">
      <PageHeader
        title="Mening Profilim"
        subtitle="Platformadagi darajangiz, dars va fikr-mulohazalar statistikasi boshqaruvi."
        icon={User}
      />

      {/* Profile Header Card */}
      <Card hover={false} className="p-4 sm:p-6 flex flex-col items-center sm:flex-row sm:items-start justify-between gap-4 sm:gap-6 relative overflow-hidden rounded-3xl border-2 border-black bg-[#2A3442] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-5 w-full sm:w-auto">
          <Avatar src={user.avatar_url} name={user.school21_login} size="xl" />
          <div className="flex flex-col items-center sm:items-start gap-1 min-w-0">
            <div className="flex flex-col sm:flex-row items-center gap-2">
              <h2 className="text-base sm:text-lg font-black text-white font-montserrat tracking-tight text-center sm:text-left">
                {user.first_name} {user.last_name}
              </h2>
              <Badge type="primary">{`LEVEL ${user.level}`}</Badge>
            </div>
            <span className="text-xs text-[#38C9E6] font-bold">@{user.school21_login}</span>
            <span className="text-[10px] text-[#B0BEC5] uppercase tracking-wider font-extrabold mt-1 text-center sm:text-left">
              Program: {user.core_program || 'CORE'} • Track: {user.main_track || 'Web'}
            </span>

            {/* Language Badges */}
            <div className="flex flex-wrap justify-center sm:justify-start gap-1.5 mt-3">
              {user.languages.map((l) => (
                <span key={l} className="text-[10px] uppercase tracking-widest font-black px-2.5 py-1 rounded-xl bg-[#34495E] text-[#cdbdff] border-2 border-black shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]">
                  {l}
                </span>
              ))}
            </div>
          </div>
        </div>

        <Button variant="secondary" onClick={handleEditOpen} className="text-xs uppercase font-extrabold tracking-wider font-montserrat w-full sm:w-auto min-h-11">
          <Edit className="h-4 w-4" /> Edit Profile
        </Button>
      </Card>

      {/* Edit Form inline Card */}
      {isEditing && (
        <Card className="p-4 sm:p-6 border-2 border-black bg-[#2A3442] animate-slide-in rounded-3xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <form onSubmit={handleSubmit(onUpdateSubmit)} className="flex flex-col gap-4">
            <h3 className="text-sm font-extrabold text-white border-b-2 border-black pb-3 font-montserrat uppercase tracking-wider">
              Profil Ma'lumotlarini Tahrirlash
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input label="Ism" error={errors.first_name?.message} {...register('first_name')} />
              <Input label="Familiya" error={errors.last_name?.message} {...register('last_name')} />
            </div>
            <Input
              label="Avatar loyiha yoki rasm URL manzili"
              error={errors.avatar_url?.message}
              placeholder="https://..."
              {...register('avatar_url')}
            />
            <div className="flex flex-col-reverse sm:flex-row gap-3 justify-end pt-2">
              <Button type="button" variant="ghost" onClick={() => setIsEditing(false)} disabled={isUpdatingProfile} className="w-full sm:w-auto min-h-11">
                Bekor qilish
              </Button>
              <Button type="submit" variant="primary" disabled={isUpdatingProfile} className="w-full sm:w-auto min-h-11">
                {isUpdatingProfile ? 'Saqlanmoqda...' : 'Saqlash'}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Stats Matrix */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        {/* Teach count */}
        <Card className="p-3 sm:p-5 flex flex-col gap-1.5 sm:gap-2 rounded-2xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] bg-[#2A3442]">
          <div className="flex items-center gap-2 text-[#cdbdff]">
            <GraduationCap className="h-4 w-4 flex-shrink-0" />
            <span className="text-[9px] sm:text-[10px] uppercase tracking-widest font-extrabold text-[#B0BEC5] font-montserrat truncate">O'rgatilgan</span>
          </div>
          <span className="text-xl sm:text-2xl font-black text-white mt-1 font-montserrat leading-none">{stats.taught_count} <span className="text-xs">marta</span></span>
          <span className="text-[9px] sm:text-[10px] text-[#B0BEC5] leading-relaxed">Reviewer sifatida</span>
        </Card>

        {/* Learn count */}
        <Card className="p-3 sm:p-5 flex flex-col gap-1.5 sm:gap-2 rounded-2xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] bg-[#2A3442]">
          <div className="flex items-center gap-2 text-[#38C9E6]">
            <BookOpen className="h-4 w-4 flex-shrink-0" />
            <span className="text-[9px] sm:text-[10px] uppercase tracking-widest font-extrabold text-[#B0BEC5] font-montserrat truncate">O'rganilgan</span>
          </div>
          <span className="text-xl sm:text-2xl font-black text-white mt-1 font-montserrat leading-none">{stats.learned_count} <span className="text-xs">marta</span></span>
          <span className="text-[9px] sm:text-[10px] text-[#B0BEC5] leading-relaxed">Reviewee sifatida</span>
        </Card>

        {/* Positive Review */}
        <Card className="p-3 sm:p-5 flex flex-col gap-1.5 sm:gap-2 rounded-2xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] bg-[#263E33]">
          <div className="flex items-center gap-2 text-[#43E8A0]">
            <ThumbsUp className="h-4 w-4 flex-shrink-0" />
            <span className="text-[9px] sm:text-[10px] uppercase tracking-widest font-extrabold text-white/80 font-montserrat truncate">Ijobiy</span>
          </div>
          <span className="text-xl sm:text-2xl font-black text-[#43E8A0] mt-1 font-montserrat leading-none">{stats.positive_reviews} <span className="text-xs">ta</span></span>
          <span className="text-[9px] sm:text-[10px] text-white/75 leading-relaxed">Sheriklar olqishladi</span>
        </Card>

        {/* Negative Review */}
        <Card className="p-3 sm:p-5 flex flex-col gap-1.5 sm:gap-2 rounded-2xl border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] bg-[#4A2D2D]">
          <div className="flex items-center gap-2 text-[#FF9B9B]">
            <ThumbsDown className="h-4 w-4 flex-shrink-0" />
            <span className="text-[9px] sm:text-[10px] uppercase tracking-widest font-extrabold text-white/80 font-montserrat truncate">Salbiy</span>
          </div>
          <span className="text-xl sm:text-2xl font-black text-[#FF9B9B] mt-1 font-montserrat leading-none">{stats.negative_reviews} <span className="text-xs">ta</span></span>
          <span className="text-[9px] sm:text-[10px] text-white/75 leading-relaxed">Jiddiy kamchiliklar</span>
        </Card>
      </div>

      {/* Skills list */}
      <div className="flex flex-col gap-4 mt-2">
        <span className="text-sm font-extrabold text-white flex items-center gap-2 border-b-2 border-black pb-3 font-montserrat uppercase tracking-wider">
          <Code className="h-5 w-5 text-[#38C9E6]" /> Texnik Ko'nikmalar
        </span>

        {isLoadingSkills ? (
          <Spinner size="sm" />
        ) : skills.length === 0 ? (
          <Card className="p-6 text-center text-[#B0BEC5] text-xs">
            Hech qanday ko'nikmalar qayd etilmagan.
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
            {(() => {
              const maxPoints = Math.max(...skills.map((s) => s.points), 1);
              return skills.map((skill) => (
                <Card key={skill.name} hover={false} className="p-4 sm:p-5 bg-[#2A3442] border-2 border-black rounded-2xl shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  <div className="flex justify-between items-center mb-2.5 text-xs gap-2">
                    <span className="font-extrabold text-[#B0BEC5] font-montserrat uppercase tracking-wider truncate">{skill.name}</span>
                    <span className="font-black text-[#38C9E6] font-ibm-plex-mono flex-shrink-0">{skill.points}</span>
                  </div>
                  {/* Visual bar — eng yuqori balga nisbatan normallashtirilgan */}
                  <div className="h-4.5 w-full rounded-full bg-[#34495E] border-2 border-black overflow-hidden p-[2px] shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]">
                    <div className="h-full bg-gradient-to-r from-[#38C9E6] to-[#43E8A0] rounded-full" style={{ width: `${Math.round((skill.points / maxPoints) * 100)}%` }} />
                  </div>
                </Card>
              ));
            })()}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── PUBLIC PROFILE ─────────────────────────────────────────────────────────────

function PublicProfileView({ username }: { username: string }) {
  const { data: userPublic, isLoading: isLoadingPublic, isError: isErrorPublic } = useQuery({
    queryKey: ['profile', 'public', username],
    queryFn: () => profileService.getPublicProfile(username),
    enabled: !!username,
  });

  const userId = userPublic?.id;
  const { data: reviews = [], isLoading: isLoadingReviews } = useQuery({
    queryKey: ['reviews', 'user', userId],
    queryFn: () => reviewsService.getUserReviews(userId || ''),
    enabled: !!userId,
  });

  if (isLoadingPublic) {
    return (
      <div className="flex flex-col gap-4 sm:gap-6 animate-fade-in font-ibm-plex-mono text-white">
        {/* Top breadcrumb skeleton */}
        <div>
          <Skeleton variant="text" className="w-32 h-3" />
        </div>

        {/* Header Info Block Skeleton */}
        <div className="p-4 sm:p-6 flex flex-col items-center sm:flex-row sm:items-start gap-4 sm:gap-5 rounded-3xl border-2 border-black bg-[#2A3442] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <Skeleton variant="circle" className="h-20 w-20 sm:h-24 sm:w-24 flex-shrink-0" />
          <div className="flex flex-col items-center sm:items-start gap-2.5 w-full">
            <div className="flex items-center gap-2 w-full justify-center sm:justify-start">
              <Skeleton variant="text" className="w-32 sm:w-40 h-5" />
              <Skeleton variant="rect" className="w-20 h-5 rounded-md" />
            </div>
            <Skeleton variant="text" className="w-24 h-3.5" />
            <Skeleton variant="text" className="w-[60%] h-3" />
          </div>
        </div>

        {/* Reviews skeleton */}
        <div className="flex flex-col gap-4">
          <div className="border-b-2 border-black pb-3">
            <Skeleton variant="text" className="w-48 h-4" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {[1, 2].map((i) => (
              <div key={i} className="p-4 sm:p-5 border-2 border-black bg-[#2A3442] rounded-2xl flex flex-col gap-3 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <Skeleton variant="text" className="w-1/4 h-4" />
                <Skeleton variant="text" className="w-full h-8" />
                <Skeleton variant="rect" className="w-full h-4 rounded-md mt-1" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isErrorPublic || !userPublic) {
    return (
      <div className="flex flex-col gap-4 sm:gap-6 animate-fade-in font-ibm-plex-mono text-white">
        <PageHeader
          title="Talaba Profili"
          subtitle="Foydalanuvchi ma'lumotlari."
          icon={User}
        />
        <Card className="p-6 sm:p-8 text-center border-2 border-black rounded-3xl bg-[#2A3442] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <p className="text-[#FF9B9B] font-bold text-sm mb-3">
            Ushbu talaba topilmadi yoki ma'lumotlarni yuklab bo'lmadi.
          </p>
          <Link to="/leaderboard" className="text-xs uppercase tracking-wider text-[#38C9E6] underline font-montserrat font-extrabold">
            Reyting ro'yxatiga qaytish
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 sm:gap-6 animate-fade-in font-ibm-plex-mono text-white">
      {/* Top breadcrumb */}
      <div>
        <Link
          to="/leaderboard"
          className="inline-flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-[#B0BEC5] hover:text-white transition-colors font-montserrat min-h-11 py-2"
        >
          <ChevronLeft className="h-4 w-4" /> Reytingga qaytish
        </Link>
      </div>

      <PageHeader
        title={`${userPublic.first_name || 'Ism'} ${userPublic.last_name || 'Familiya'}`}
        subtitle={`@${userPublic.telegram_username || 'telegram_yo\'q'} — ${userPublic.core_program || 'CORE'} • ${userPublic.main_track || 'Web'}`}
        icon={User}
      />

      {/* Header Info Block */}
      <Card hover={false} className="p-4 sm:p-6 flex flex-col items-center sm:flex-row sm:items-start gap-4 sm:gap-5 relative overflow-hidden bg-[#2A3442] border-2 border-black rounded-3xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <Avatar src={userPublic.avatar_url} name={userPublic.telegram_username} size="xl" />
        <div className="flex flex-col items-center sm:items-start gap-1 min-w-0">
          <div className="flex flex-col sm:flex-row items-center gap-2">
            <h2 className="text-base sm:text-lg font-black text-white font-montserrat tracking-tight text-center sm:text-left">
              {userPublic.first_name || 'Ism'} {userPublic.last_name || 'Familiya'}
            </h2>
            <Badge type="secondary">{`LEVEL ${userPublic.level}`}</Badge>
          </div>
          <span className="text-xs text-[#38C9E6] font-bold">
            @{userPublic.telegram_username || 'telegram_yo\'q'}
          </span>
          <span className="text-[10px] text-[#B0BEC5] uppercase tracking-wider font-extrabold mt-1 text-center sm:text-left break-words">
            Program: {userPublic.core_program || 'CORE'} • Track: {userPublic.main_track || 'Web'} • Campus: {userPublic.campus || 'Mavjud emas'}
          </span>
          {userPublic.coalition_name && (
            <span className="text-[10px] text-[#cdbdff] font-bold uppercase mt-1">
              Koalitsiya: {userPublic.coalition_name}
            </span>
          )}
        </div>
      </Card>

      {/* Reviews about this user */}
      <div className="flex flex-col gap-4">
        <span className="text-sm font-extrabold text-white flex items-center gap-2 border-b-2 border-black pb-3 font-montserrat uppercase tracking-wider">
          <MessageSquare className="h-5 w-5 text-[#38C9E6]" /> Fikrlar (Reviews)
        </span>

        {isLoadingReviews ? (
          <Spinner size="sm" />
        ) : reviews.length === 0 ? (
          <Card className="p-6 sm:p-8 text-center bg-[#2A3442]/50 text-[#B0BEC5] text-xs border-2 border-black rounded-2xl">
            Hali bu talaba haqida hech qanday fikr-mulohazalar yozib qoldirilmagan.
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {reviews.map((rev) => (
              <Card key={rev.id} hover={false} className="p-4 sm:p-5 border-2 border-black flex flex-col justify-between gap-3 sm:gap-4 bg-[#2A3442] rounded-2xl shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {rev.is_positive ? (
                      <ThumbsUp className="h-5 w-5 text-[#43E8A0] bg-[#43E8A0]/10 p-1 rounded" />
                    ) : (
                      <ThumbsDown className="h-5 w-5 text-[#FF9B9B] bg-[#FF9B9B]/10 p-1 rounded" />
                    )}
                    <span className={`text-xs font-black uppercase tracking-wider font-montserrat ${rev.is_positive ? 'text-[#43E8A0]' : 'text-[#FF9B9B]'}`}>
                      {rev.is_positive ? 'Ijobiy' : 'Salbiy'}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-[#B0BEC5] leading-relaxed italic break-words">
                  &ldquo;{rev.comment || 'Tavsif qoldirilmagan'}&rdquo;
                </p>

                <div className="text-[9px] text-[#B0BEC5] uppercase tracking-wider font-bold border-t-2 border-black/30 pt-3 flex justify-between font-montserrat">
                  <span>Baholovchi a'zo</span>
                  <span className="text-[#43E8A0] font-black">SAQLANGAN</span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

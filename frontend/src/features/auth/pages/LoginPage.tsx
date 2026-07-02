import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '@/features/auth/hooks';
import { useAuthStore } from '@/features/auth/store';
import { Button } from '@/shared/ui';
import { Key, Eye, EyeOff, ChevronRight, Send } from 'lucide-react';
import { triggerToast } from '@/shared/stores/toast';

const loginSchema = z.object({
  login: z.string().min(2, 'Login kamida 2 ta belgidan iborat bo\'lishi kerak'),
  password: z.string().min(4, 'Parol kamida 4 ta belgidan iborat bo\'lishi kerak'),
});

const verifySchema = z.object({
  code: z.string().length(6, 'Kod roppa-rosa 6 ta raqam bo\'lishi kerak'),
});

type LoginFormValues = z.infer<typeof loginSchema>;
type VerifyFormValues = z.infer<typeof verifySchema>;

const SLIDES = [
  {
    title: 'Gamification',
    description: 'Gain knowledge. Complete projects and achieve higher Levels.',
  },
  {
    title: 'Peer-to-Peer Review',
    description: 'Evaluate your peers and receive objective feedback to progress daily.',
  },
  {
    title: 'Fast Slots Booking',
    description: 'Instantly schedule p2p reviews, gain coins, and upgrade your level.',
  }
];

export default function LoginPage() {
  const { login, isLoggingIn, loginData, verifyCode, isVerifyingCode } = useAuth();
  const { setTokens } = useAuthStore();
  const [showOtp, setShowOtp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);

  // Auto slideshow carousel on left side
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % SLIDES.length);
    }, 4500);
    return () => clearInterval(interval);
  }, []);

  const {
    register: loginRegister,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const {
    register: verifyRegister,
    handleSubmit: handleVerifySubmit,
    formState: { errors: verifyErrors },
  } = useForm<VerifyFormValues>({
    resolver: zodResolver(verifySchema),
  });

  const onLoginSubmit = (values: LoginFormValues) => {
    login(values, {
      onSuccess: (data) => {
        if (data.status === 'need_telegram') {
          setShowOtp(true);
          triggerToast('Telegram botdan olingan tasdiqlash kodini kiriting', 'info');
        } else if (data.status === 'ok' && data.access_token) {
          setTokens(data.access_token, data.refresh_token as string, data.onboarding_done);
          triggerToast('Muvaffaqiyatli kirdingiz!', 'success');
        }
      },
    });
  };

  const onVerifySubmit = (values: VerifyFormValues) => {
    if (!loginData?.temp_token) {
      triggerToast('Vaqtinchalik seans tugagan. Qaytadan login qiling.', 'error');
      setShowOtp(false);
      return;
    }

    verifyCode({
      temp_token: loginData.temp_token,
      code: values.code,
    });
  };

  return (
    <div className="min-h-screen bg-[#1E2A38] text-white flex flex-col justify-center relative overflow-hidden font-sans p-4 select-none">
      {/* Background Pipeline Curve Art & Colorful Squircles */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg" fill="none">
          <defs>
            <linearGradient id="gradient-pipe-left" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38C9E6" stopOpacity="0.4" />
              <stop offset="50%" stopColor="#38C9E6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#cdbdff" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="gradient-pipe-right" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#cdbdff" stopOpacity="0.1" />
              <stop offset="50%" stopColor="#38C9E6" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#43E8A0" stopOpacity="0.5" />
            </linearGradient>
          </defs>

          {/* Left Flow Path */}
          <path
            d="M -50 250 C 150 150, 50 350, -100 500"
            stroke="url(#gradient-pipe-left)"
            strokeWidth="32"
            strokeLinecap="round"
          />

          {/* Connected Main curved bridge flow */}
          <path
            d="M -100 250 C 200 100, -80 600, 400 800 C 600 900, 800 600, 1000 400 C 1100 300, 1200 150, 1400 50"
            stroke="url(#gradient-pipe-right)"
            strokeWidth="28"
            strokeLinecap="round"
          />
        </svg>

        {/* Floating background neon lights */}
        <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-[#38C9E6]/5 rounded-full blur-[140px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#cdbdff]/5 rounded-full blur-[160px]" />

        {/* Ambient Squircles — hidden on mobile */}
        <div className="hidden lg:block absolute -left-12 top-[35%] w-24 h-24 bg-[#38C9E6] rotate-12 opacity-80" style={{ borderRadius: '24px 0' }} />
        <div className="hidden lg:block absolute left-[45%] bottom-[5%] w-32 h-32 bg-gradient-to-br from-[#cdbdff] to-[#38C9E6] rotate-[22deg] opacity-90" style={{ borderRadius: '32px 0' }} />
        <div className="hidden lg:block absolute right-[6%] top-[12%] w-36 h-36 bg-[#43E8A0] rotate-[15deg] opacity-80" style={{ borderRadius: '36px 0' }} />
        <div className="hidden lg:block absolute right-[22%] top-[30%] w-20 h-20 bg-[#43E8A0]/70 -rotate-12 opacity-90" style={{ borderRadius: '20px 0' }} />
      </div>

      {/* Brand Retro Icon Logo — scaled down on mobile */}
      <div className="absolute top-0 left-0 z-20 pointer-events-none w-[267px] h-[192px] scale-[0.6] sm:scale-75 origin-top-left lg:scale-100 animate-fade-in">
        <svg
          width="267"
          height="192"
          viewBox="0 0 267 192"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="absolute inset-0"
        >
          <defs>
            <linearGradient id="paint1_linear" x1="32" y1="0" x2="267" y2="192" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38C9E6" />
              <stop offset="45%" stopColor="#43E8A0" />
              <stop offset="100%" stopColor="#43E8A0" />
            </linearGradient>
          </defs>
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M32 0V13.915C32 21.7049 38.3771 28.0207 46.2424 28.0207H87.1894C109.306 28.0207 129.917 57.4932 129.917 78.2724V174.368C129.917 184.106 137.887 192 147.72 192H249.197C259.03 192 267 184.106 267 174.368V72.1012C267 62.3629 259.03 54.469 249.197 54.469H153.061C121.9 54.469 101.432 25.3759 101.432 13.0333V0H32Z"
            fill="url(#paint1_linear)"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M167.13 125.745L167.14 125.734C167.644 125.21 168.327 124.916 169.038 124.916H190.67C192.019 124.916 193.112 123.776 193.112 122.369V113.221C193.112 112.483 193.394 111.775 193.896 111.254L193.906 111.244C194.41 110.721 195.093 110.427 195.805 110.427H204.56C205.909 110.427 207.003 109.286 207.003 107.879V99.5434C207.003 98.137 205.909 96.9962 204.56 96.9962H195.804C195.09 96.9962 194.405 96.7003 193.901 96.1741C193.396 95.6475 193.112 94.9336 193.112 94.1889V85.0539C193.112 83.6471 192.019 82.5066 190.67 82.5066H155.952C154.581 82.5066 153.469 83.6658 153.469 85.0964V93.3473C153.469 94.7775 154.581 95.937 155.952 95.937H191.431C192.146 95.937 192.831 96.2331 193.337 96.7603C193.842 97.2875 194.126 98.0023 194.126 98.7479V108.684C194.126 109.426 193.843 110.138 193.338 110.662L193.332 110.668C192.827 111.192 192.145 111.486 191.433 111.486H169.802C168.453 111.486 167.36 112.627 167.36 114.033V123.174C167.36 123.914 167.077 124.625 166.576 125.148L166.567 125.157C166.065 125.681 165.384 125.975 164.675 125.975H155.912C154.563 125.975 153.469 127.115 153.469 128.522V136.858C153.469 138.265 154.563 139.405 155.912 139.405H164.683C165.393 139.405 166.074 139.699 166.576 140.223H166.576C167.078 140.746 167.36 141.456 167.36 142.196V151.336C167.36 152.743 168.453 153.883 169.802 153.884L204.52 153.884C205.891 153.884 207.003 152.725 207.003 151.294V143.043C207.003 141.613 205.891 140.454 204.52 140.454L169.038 140.453C168.327 140.453 167.644 140.159 167.139 139.636L167.13 139.626C166.628 139.106 166.346 138.398 166.346 137.66V127.711C166.346 126.973 166.628 126.265 167.13 125.745Z"
            fill="#1E2A38"
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M227.01 96.1741C226.505 95.6475 226.222 94.9336 226.222 94.1889V85.0653C226.222 83.6522 225.123 82.5066 223.768 82.5066H215.799C214.444 82.5066 213.345 83.6522 213.345 85.0653V93.3783C213.345 94.7911 214.444 95.937 215.799 95.937H224.542C225.256 95.937 225.94 96.2325 226.445 96.7591L226.447 96.7615C226.445 97.2878 227.235 98.0017 227.235 98.7464V151.325C227.235 152.738 228.334 153.884 229.689 153.884H237.658C239.013 153.884 240.111 152.738 240.111 151.325V99.5552C240.111 98.1418 239.013 96.9962 237.658 96.9962H228.913C228.199 96.9962 227.515 96.7007 227.01 96.1741Z"
            fill="#1E2A38"
          />
        </svg>

        {/* 'SCHOOL' text written vertically */}
        <div
          className="absolute flex flex-col items-center justify-between text-[6px] sm:text-[6.5px] leading-none font-black uppercase text-[#43E8A0] select-none pointer-events-none font-mono tracking-tighter"
          style={{
            left: '228.8px',
            top: '101.5px',
            width: '10.5px',
            height: '46px',
          }}
        >
          <span>S</span>
          <span>C</span>
          <span>H</span>
          <span>O</span>
          <span>O</span>
          <span>L</span>
        </div>
      </div>

      {/* Main Split Container — single column mobile, two columns on lg */}
      <div className="max-w-[1240px] w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-14 items-center relative z-10">

        {/* Left Side: Slideshow — hidden on mobile, shown on lg */}
        <div className="hidden lg:flex lg:col-span-6 flex-col justify-center items-start lg:pr-8">
          <div className="min-h-[160px] flex flex-col justify-center">
            {SLIDES.map((slide, idx) => (
              <div
                key={slide.title}
                className={`transition-all duration-700 ease-in-out transform ${
                  idx === currentSlide
                    ? 'opacity-100 translate-x-0 relative block'
                    : 'opacity-0 -translate-x-4 absolute hidden'
                }`}
              >
                <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black font-montserrat tracking-tight mb-4">
                  {slide.title}
                </h2>
                <p className="text-[#B0BEC5] text-base sm:text-lg max-w-md leading-relaxed font-normal">
                  {slide.description}
                </p>
              </div>
            ))}
          </div>

          {/* Interactive Slide dots */}
          <div className="flex gap-2.5 mt-8 items-center">
            {SLIDES.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentSlide(idx)}
                className={`h-2.5 rounded-full transition-all duration-300 cursor-pointer ${
                  idx === currentSlide ? 'w-6 bg-[#43E8A0]' : 'w-2.5 bg-[#34495E] hover:bg-[#B0BEC5]'
                }`}
                aria-label={`Slide ${idx + 1}`}
              />
            ))}
          </div>
        </div>

        {/* Right Side: Login Card — full width mobile, right-aligned desktop */}
        <div className="lg:col-span-6 flex justify-center lg:justify-end pt-16 sm:pt-20 lg:pt-0">
          <div
            className="w-full max-w-[460px] border-2 border-black rounded-3xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] overflow-hidden"
          >
            <div
              className="w-full h-full bg-[#2A3442] p-4 sm:p-6 lg:p-8 flex flex-col"
            >

              {/* Header Title inside card */}
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-white tracking-tight leading-snug font-montserrat">
                Welcome to School 21
              </h1>
              <p className="text-[#B0BEC5] text-xs sm:text-sm mt-2 sm:mt-3 leading-relaxed">
                Please enter your login and password that you received earlier
              </p>

              {!showOtp ? (
                /* Login form */
                <form onSubmit={handleLoginSubmit(onLoginSubmit)} className="flex flex-col gap-4 sm:gap-5 mt-6 sm:mt-8">

                  {/* Login field */}
                  <div className="flex flex-col gap-1.5">
                    <div
                      className={`w-full bg-[#34495E] text-white rounded-xl min-h-11 p-2.5 sm:p-[9px] px-3 sm:px-4 flex flex-col justify-between transition-all border-2 ${
                        loginErrors.login ? 'border-[#FF9B9B] ring-2 ring-[#FF9B9B]/20' : 'border-black focus-within:border-[#38C9E6]'
                      }`}
                    >
                      <label className="text-[10px] text-[#B0BEC5] font-bold select-none leading-none pt-0.5 font-montserrat uppercase tracking-wider">login</label>
                      <input
                        type="text"
                        disabled={isLoggingIn}
                        autoCapitalize="none"
                        {...loginRegister('login')}
                        className="w-full bg-transparent text-white text-sm font-semibold focus:outline-none focus:ring-0 leading-tight h-[22px] p-0 border-none select-all font-ibm-plex-mono"
                      />
                    </div>
                    {loginErrors.login && (
                      <span className="text-[11px] text-[#FF9B9B] font-bold ml-1">{loginErrors.login.message}</span>
                    )}
                  </div>

                  {/* Password field */}
                  <div className="flex flex-col gap-1.5">
                    <div
                      className={`w-full bg-[#34495E] text-white rounded-xl min-h-11 p-2.5 sm:p-[9px] px-3 sm:px-4 flex items-center justify-between transition-all border-2 ${
                        loginErrors.password ? 'border-[#FF9B9B] ring-2 ring-[#FF9B9B]/20' : 'border-black focus-within:border-[#38C9E6]'
                      }`}
                    >
                      <div className="flex-grow flex flex-col justify-between">
                        <label className="text-[10px] text-[#B0BEC5] font-bold select-none leading-none pt-0.5 font-montserrat uppercase tracking-wider">password</label>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          disabled={isLoggingIn}
                          {...loginRegister('password')}
                          className="w-full bg-transparent text-white text-sm font-semibold focus:outline-none focus:ring-0 leading-tight h-[22px] p-0 border-none select-all font-ibm-plex-mono"
                        />
                      </div>
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="text-[#B0BEC5] hover:text-white transition-colors p-2 sm:p-1 ml-2 flex-shrink-0 cursor-pointer min-h-11 min-w-11 sm:min-h-0 sm:min-w-0 flex items-center justify-center"
                      >
                        {showPassword ? <EyeOff className="h-5 w-5 stroke-[2]" /> : <Eye className="h-5 w-5 stroke-[2]" />}
                      </button>
                    </div>
                    {loginErrors.password && (
                      <span className="text-[11px] text-[#FF9B9B] font-bold ml-1">{loginErrors.password.message}</span>
                    )}
                  </div>

                  {/* Action button — full width on mobile */}
                  <div className="flex items-center mt-2 sm:mt-3">
                    <button
                      type="submit"
                      disabled={isLoggingIn}
                      className="h-11 w-full sm:w-auto px-6 bg-gradient-to-r from-[#38C9E6] to-[#43E8A0] hover:translate-y-[1px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:translate-y-[2px] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] text-black font-black text-sm rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <span>{isLoggingIn ? 'Logging in...' : 'Log in'}</span>
                      <ChevronRight className="h-4 w-4 stroke-[3px]" />
                    </button>
                  </div>
                </form>
              ) : (
                /* Telegram OTP Verification */
                <form onSubmit={handleVerifySubmit(onVerifySubmit)} className="flex flex-col gap-4 sm:gap-5 mt-6 sm:mt-8">
                  <div className="bg-[#34495E] border-2 border-black p-3 sm:p-4 rounded-xl flex flex-col gap-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                    <span className="text-[10px] text-[#38C9E6] font-black uppercase tracking-widest font-montserrat">
                      Secure Telegram Authentication
                    </span>
                    <p className="text-xs text-[#B0BEC5] leading-relaxed">
                      Please open the bot using the link below to retrieve your securely generated 6-digit confirmation code.
                    </p>
                    {loginData?.bot_url && (
                      <a
                        href={loginData.bot_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-start gap-1 text-xs font-black text-[#43E8A0] hover:text-[#38C9E6] uppercase tracking-wider mt-2 min-h-11 sm:min-h-0"
                      >
                        <Send className="h-3.5 w-3.5" /> Open Telegram Bot
                      </a>
                    )}
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <div
                      className={`w-full bg-[#34495E] text-white rounded-xl min-h-11 p-2.5 sm:p-[9px] px-3 sm:px-4 flex flex-col justify-between transition-all border-2 ${
                        verifyErrors.code ? 'border-[#FF9B9B] ring-2 ring-[#FF9B9B]/20' : 'border-black focus-within:border-[#38C9E6]'
                      }`}
                    >
                      <label className="text-[10px] text-[#B0BEC5] font-bold select-none leading-none pt-0.5 font-montserrat uppercase tracking-wider">verification code</label>
                      <input
                        type="text"
                        maxLength={6}
                        disabled={isVerifyingCode}
                        {...verifyRegister('code')}
                        className="w-full bg-transparent text-white text-sm font-semibold focus:outline-none focus:ring-0 leading-tight h-[22px] p-0 border-none select-all font-ibm-plex-mono tracking-widest text-center"
                        placeholder="000 000"
                      />
                    </div>
                    {verifyErrors.code && (
                      <span className="text-[11px] text-[#FF9B9B] font-bold ml-1">{verifyErrors.code.message}</span>
                    )}
                  </div>

                  <div className="flex flex-col gap-3 mt-2">
                    <button
                      type="submit"
                      disabled={isVerifyingCode}
                      className="h-11 w-full bg-gradient-to-r from-[#38C9E6] to-[#43E8A0] hover:translate-y-[1px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:translate-y-[2px] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] text-black font-black text-sm rounded-xl flex items-center justify-center gap-2 transition-all cursor-pointer border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <Key className="h-4 w-4 stroke-[2.5]" />{' '}
                      {isVerifyingCode ? 'Verifying OTP...' : 'Verify OTP Code'}
                    </button>

                    <button
                      type="button"
                      onClick={() => setShowOtp(false)}
                      className="text-xs font-bold text-center text-[#B0BEC5] hover:text-[#38C9E6] mt-1 transition-colors cursor-pointer min-h-11 sm:min-h-0 flex items-center justify-center"
                    >
                      Go back to log in
                    </button>
                  </div>
                </form>
              )}

              {/* Decorative separator */}
              <hr className="border-black/30 my-4 sm:my-6" />

              {/* Footer inside login card */}
              <div className="flex flex-col gap-2">
                <span className="text-white text-xs sm:text-sm font-bold font-montserrat">
                  How to begin the study?
                </span>
                <p className="text-[#B0BEC5] text-[11px] sm:text-xs leading-relaxed">
                  If you want to study at the next-gen School, press the{' '}
                  <a
                    href="https://21-school.ru"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#38C9E6] hover:underline font-semibold"
                  >
                    link to School21
                  </a>
                </p>
              </div>

            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

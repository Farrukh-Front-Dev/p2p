interface ProgressBarProps {
  percent: number;
  labelLeft?: string;
  labelRight?: string;
}

export function ProgressBar({ percent, labelLeft, labelRight }: ProgressBarProps) {
  const boundedPercent = Math.max(0, Math.min(100, percent));

  return (
    <div className="flex flex-col gap-2 w-full">
      {(labelLeft || labelRight) && (
        <div className="flex justify-between items-center text-[10px] text-[#B0BEC5] uppercase tracking-widest font-extrabold font-montserrat">
          <span>{labelLeft}</span>
          <span>{labelRight}</span>
        </div>
      )}
      <div className="h-4.5 w-full rounded-full bg-[#34495E] border-2 border-black overflow-hidden p-[2px] shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${boundedPercent}%`,
            background: 'linear-gradient(90deg, #38C9E6 0%, #43E8A0 100%)',
          }}
        />
      </div>
    </div>
  );
}
export default ProgressBar;

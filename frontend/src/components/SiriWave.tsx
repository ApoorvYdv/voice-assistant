const SiriWave = ({ status }: { status: "idle" | "listening" | "processing" | "speaking" }) => {
  const bars = [0.4, 0.6, 0.8, 0.5, 0.7, 0.4, 0.6, 0.3];
  
  const getBarHeight = (baseHeight: number) => {
    switch (status) {
      case 'listening': return baseHeight * 2;
      case 'speaking': return baseHeight * 1.5;
      case 'processing': return baseHeight * 0.5;
      default: return 0;
    }
  };

  return (
    <div className="flex justify-center items-center gap-1.5 h-full">
      {bars.map((height, i) => (
        <div
          key={i}
          className="w-1.5 rounded-full bg-gradient-to-br from-blue-400 to-cyan-300 transition-all duration-300 ease-in-out"
          style={{ 
            height: `${getBarHeight(height * 100)}%`,
            animation: status !== 'idle' ? `wave ${1 + i * 0.1}s infinite ease-in-out` : 'none',
          }}
        />
      ))}
      <style jsx>{`
        @keyframes wave {
          0%, 100% { transform: scaleY(0.8); }
          50% { transform: scaleY(1.2); }
        }
      `}</style>
    </div>
  );
};

export default SiriWave;
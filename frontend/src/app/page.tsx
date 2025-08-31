import VoiceAssistant from "@/components/VoiceAssistant";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-black text-white">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-bold mb-2">LangGraph Voice Assistant</h1>
        <p className="text-gray-400">
          Powered by Next.js, CopilotKit, and LangGraph
        </p>
      </div>
      <VoiceAssistant />
    </main>
  );
}
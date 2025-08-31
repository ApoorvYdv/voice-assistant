'use client';
import { useState, useRef } from "react";
import { Mic, Zap, Bot, Wrench } from "lucide-react";
import AgentFlowDisplay, { FlowStep } from "./AgentFlowDisplay";
import SiriWave from "./SiriWave";
import { useVoiceRecognition } from "@/hooks/useVoiceRecognition";

export default function VoiceAssistant() {
  const [flow, setFlow] = useState<FlowStep[]>([]);
  const [status, setStatus] = useState<"idle" | "listening" | "processing" | "speaking">("idle");
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const processTranscript = async (transcript: string) => {
    console.log("transcribe started")
    setStatus("processing");
    setFlow([]); // Reset flow on new request

    // Add user's message to the flow
    setFlow(prev => [...prev, { type: 'user_message', data: { message: transcript } }]);

    try {
      const response = await fetch("http://localhost:8000/invoke-assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: transcript }),
      });

      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // SSE sends events separated by double newlines
        const events = chunk.split("\n\n").filter(Boolean);
        
        for (const event of events) {
          if (event.startsWith("data: ")) {
            const dataStr = event.substring(6);
            const data = JSON.parse(dataStr);

            if (data.type === 'step') {
              setFlow(prev => [...prev, { type: 'agent_step', data: data.data }]);
            } else if (data.type === 'audio_data') {
              const audioBase64 = data.data;
              const audioSrc = `data:audio/mpeg;base64,${audioBase64}`;
              const audio = new Audio(audioSrc);
              audioRef.current = audio;
              setStatus("speaking");
              audio.play();
              audio.onended = () => {
                setStatus("idle");
              };
            }
          }
        }
      }
    } catch (error) {
      console.error("Error streaming from backend:", error);
      setFlow(prev => [...prev, { type: 'error', data: { text: "Sorry, I encountered an error." } }]);
      setStatus("idle");
    }
  };
  
  const { isListening, start, stop } = useVoiceRecognition({
    onStart: () => setStatus("listening"),
    onResult: (transcript) => processTranscript(transcript),
    onEnd: () => setStatus("idle"),
  });

  const handleMicClick = () => {
    if (isListening) {
      stop();
    } else if (status === "idle") {
      start();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-gray-900/50 backdrop-blur-md rounded-2xl p-6 border border-gray-700 shadow-2xl">
        <AgentFlowDisplay steps={flow} />

        <div className="h-24 mt-6 flex items-center justify-center">
            <SiriWave status={status} />
        </div>
        
        <div className="flex justify-center mt-6">
          <button
            onClick={handleMicClick}
            disabled={status === "processing" || status === "speaking"}
            className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300
              ${isListening ? 'bg-red-500' : 'bg-blue-500'}
              hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed
              focus:outline-none focus:ring-4 focus:ring-blue-400/50`
            }
          >
            <Mic size={32} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
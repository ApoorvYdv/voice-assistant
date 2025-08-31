import { useState, useEffect, useRef } from 'react';

// The type definitions are now available globally after installation

interface VoiceRecognitionOptions {
  onStart?: () => void;
  onResult?: (transcript: string) => void;
  onEnd?: () => void;
  onError?: (error: SpeechRecognitionErrorCode) => void; // Using the specific type
}

export const useVoiceRecognition = (options: VoiceRecognitionOptions) => {
  const [isListening, setIsListening] = useState(false);
  // Explicitly type the ref with the SpeechRecognition interface
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) {
      console.error("Speech Recognition API not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      options.onStart?.();
    };

    // Use the SpeechRecognitionEvent type
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      options.onResult?.(transcript);
    };

    // Use the SpeechRecognitionErrorEvent type
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      // The event itself is not the error, event.error is
      options.onError?.(event as unknown as SpeechRecognitionErrorCode);
    };
    
    recognition.onend = () => {
      setIsListening(false);
      options.onEnd?.();
    };

    recognitionRef.current = recognition;
  // This eslint-disable is safe because we want to wire this up once with the initial options
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); 

  const start = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start();
    }
  };

  const stop = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  return { isListening, start, stop };
};
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";
import { CopilotPopup, CopilotSidebar } from "@copilotkit/react-ui";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Jarvis",
  description: "Jarvis - Voice Assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <CopilotKit
          runtimeUrl="/api/copilotkit"
          agent="voice-assistant"
          textToSpeechUrl="http://localhost:8000/v1/voice-assistant/text-to-speech" // Use proxy endpoint
          transcribeAudioUrl="http://localhost:8000/v1/voice-assistant/speech-to-text"
        >
          <CopilotPopup
            defaultOpen={true}
            instructions={
              "You are assisting the user as best as you can. Answer in the best way possible given the data you have."
            }
            labels={{
              title: "Sidebar Assistant",
              initial: "How can I help you today?",
            }}
          >
            {children}
          </CopilotPopup>
        </CopilotKit>
      </body>
    </html>
  );
}
"use client";
import { useState } from "react";
import { LiveKitRoom, RoomAudioRenderer, BarVisualizer, useVoiceAssistant, VoiceAssistantControlBar } from "@livekit/components-react";

type Connection = { token: string; serverUrl: string };
function Conversation() {
  const { state, audioTrack } = useVoiceAssistant();
  return <><div className="visualizer"><BarVisualizer state={state} trackRef={audioTrack} barCount={7} /></div>
    <p className="status" role="status">{state === "connecting" ? "Connecting to your agent…" : state === "listening" ? "Listening to you" : state === "speaking" ? "Your assistant is speaking" : state === "thinking" ? "Thinking…" : state === "disconnected" ? "Agent disconnected" : "Waiting for the agent…"}</p>
    <RoomAudioRenderer /><VoiceAssistantControlBar /></>;
}
export default function Home() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function connect() {
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/connect", { method: "POST" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Unable to connect");
      setConnection(result);
    } catch (failure) { setError(failure instanceof Error ? failure.message : "Unable to connect"); }
    finally { setBusy(false); }
  }
  return <main><header><a href="/" className="brand">SDR<span> / voice studio</span></a><span className="badge">LOCAL DEMO</span></header>
    <section className="studio"><p className="eyebrow">YOUR SALES ASSISTANT</p><h1>A conversation<br />starts here.</h1>
    <p className="intro">Talk to your AI SDR. Test its voice, response time and how it listens before connecting your phone line.</p>
    <div className="session">{connection ? <LiveKitRoom token={connection.token} serverUrl={connection.serverUrl} connect audio video={false}
      onDisconnected={() => setConnection(null)} onError={() => { setError("Connection or microphone failed. Check browser permissions and try again."); setConnection(null); }}><Conversation /></LiveKitRoom>
      : <><div className="idle-bars" aria-hidden="true">{[22,40,62,88,62,40,22].map((height,i)=><i key={i} style={{height}} />)}</div><button disabled={busy} onClick={connect}>{busy ? "Connecting…" : "Start a test conversation"}<span>↗</span></button><p className="hint">Allow microphone access when prompted.</p></>}
      {error && <p className="error" role="alert">{error}</p>}</div>
    <footer><span>Deepgram Nova-3</span><span>GPT-4o-mini via LiveKit</span><span>Cartesia Sonic-3</span></footer></section>
    <p className="note">Demo mode · No calls placed · Meetings and CRM are not connected</p></main>;
}

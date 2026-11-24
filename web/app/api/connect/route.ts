import { randomUUID } from "node:crypto";
import { AccessToken, RoomAgentDispatch, RoomConfiguration } from "livekit-server-sdk";
export const runtime = "nodejs";
export async function POST(request: Request) {
  // Next.js can rewrite request.url to localhost; Host preserves the browser authority.
  const host = request.headers.get("host");
  const origin = request.headers.get("origin");
  const localAuthority = /^(localhost|127\.0\.0\.1)(:\d+)?$/;
  if (process.env.NODE_ENV === "production" || !host || !localAuthority.test(host) || (origin && origin !== `http://${host}`)) {
    return Response.json({ error: "This test endpoint is available locally only." }, { status: 403 });
  }
  const { LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET } = process.env;
  if (!LIVEKIT_URL || !LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
    return Response.json({ error: "LiveKit environment variables are missing on the server." }, { status: 503 });
  }
  try {
    const room = `sdr-test-${randomUUID()}`;
    const token = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, { identity: `tester-${randomUUID()}`, ttl: "10m" });
    token.addGrant({ roomJoin: true, room, canPublish: true, canSubscribe: true, canPublishData: true });
    token.roomConfig = new RoomConfiguration({ agents: [new RoomAgentDispatch({ agentName: process.env.AGENT_NAME || "ai-sdr" })], emptyTimeout: 60, maxParticipants: 2 });
    return Response.json({ token: await token.toJwt(), serverUrl: LIVEKIT_URL }, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return Response.json({ error: "Could not create a LiveKit session." }, { status: 500 });
  }
}

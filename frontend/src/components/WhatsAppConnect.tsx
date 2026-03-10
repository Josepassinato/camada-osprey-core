import { useState, useEffect, useRef } from "react";

interface WhatsAppConnectProps {
  officeId: string;
  onConnected?: (phone: string) => void;
}

type Status = "idle" | "connecting" | "qr" | "connected" | "error" | "timeout";

export default function WhatsAppConnect({ officeId, onConnected }: WhatsAppConnectProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [qrImage, setQrImage] = useState<string | null>(null);
  const [phone, setPhone] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const startConnection = () => {
    setStatus("connecting");
    setQrImage(null);

    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${proto}//${window.location.host}/api/whatsapp/qr/${officeId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("[WhatsApp] WS connected");
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "qr") {
        setQrImage(msg.qr);
        setStatus("qr");
      } else if (msg.type === "connected") {
        setPhone(msg.phone);
        setStatus("connected");
        ws.close();
        if (onConnected) onConnected(msg.phone);
      } else if (msg.type === "timeout") {
        setStatus("timeout");
        ws.close();
      } else if (msg.type === "error") {
        setStatus("error");
        ws.close();
      }
    };

    ws.onerror = () => setStatus("error");
    ws.onclose = (e) => {
      if (status === "connecting") {
        // Only set error if we never got a message
        setStatus((prev) => (prev === "connecting" ? "error" : prev));
      }
    };
  };

  const reset = () => {
    wsRef.current?.close();
    setStatus("idle");
    setQrImage(null);
    setPhone(null);
  };

  useEffect(() => () => { wsRef.current?.close(); }, []);

  // ── IDLE ────────────────────────────────────────────────────
  if (status === "idle") return (
    <div style={styles.card}>
      <div style={styles.icon}>💬</div>
      <h3 style={styles.title}>Connect WhatsApp</h3>
      <p style={styles.subtitle}>
        Receive and send client messages directly through WhatsApp.
      </p>
      <button onClick={startConnection} style={styles.btn}>
        Connect WhatsApp →
      </button>
    </div>
  );

  // ── CONNECTING ──────────────────────────────────────────────
  if (status === "connecting") return (
    <div style={styles.card}>
      <div style={styles.spinner} />
      <p style={styles.subtitle}>Generating QR Code...</p>
    </div>
  );

  // ── QR CODE ─────────────────────────────────────────────────
  if (status === "qr") return (
    <div style={styles.card}>
      <h3 style={styles.title}>Scan the QR Code</h3>
      <p style={styles.subtitle}>
        Open WhatsApp on your phone → <strong>Linked Devices</strong> →{" "}
        <strong>Link a Device</strong>
      </p>
      {qrImage && (
        <div style={styles.qrWrapper}>
          <img src={qrImage} alt="QR Code WhatsApp" style={styles.qrImage} />
        </div>
      )}
      <p style={{ fontSize: 12, color: "#A0A09A", marginTop: 12 }}>
        QR Code refreshes automatically · 2 min timeout
      </p>
      <button onClick={reset} style={styles.btnSecondary}>
        Cancel
      </button>
    </div>
  );

  // ── CONNECTED ────────────────────────────────────────────────
  if (status === "connected") return (
    <div style={{ ...styles.card, borderColor: "#BBF7D0" }}>
      <div style={{ fontSize: 40 }}>✅</div>
      <h3 style={{ ...styles.title, color: "#16A34A" }}>WhatsApp Connected!</h3>
      {phone && (
        <p style={styles.subtitle}>Number: <strong>{phone}</strong></p>
      )}
      <p style={{ fontSize: 13, color: "#6B6B65" }}>
        Your AI Chief of Staff can now send and receive messages.
      </p>
    </div>
  );

  // ── TIMEOUT ──────────────────────────────────────────────────
  if (status === "timeout") return (
    <div style={styles.card}>
      <div style={{ fontSize: 32 }}>⏱️</div>
      <h3 style={styles.title}>QR Code Expired</h3>
      <p style={styles.subtitle}>Scan time has expired.</p>
      <button onClick={startConnection} style={styles.btn}>
        Generate New QR Code
      </button>
    </div>
  );

  // ── ERROR ────────────────────────────────────────────────────
  return (
    <div style={styles.card}>
      <div style={{ fontSize: 32 }}>⚠️</div>
      <h3 style={styles.title}>Connection Error</h3>
      <p style={styles.subtitle}>Could not connect to WhatsApp.</p>
      <button onClick={startConnection} style={styles.btn}>
        Try Again
      </button>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#fff",
    border: "1px solid #E8E8E2",
    borderRadius: 16,
    padding: "32px 28px",
    textAlign: "center" as const,
    maxWidth: 380,
    margin: "0 auto",
  },
  icon: { fontSize: 40, marginBottom: 12 },
  title: {
    fontSize: 18,
    fontWeight: 600,
    color: "#111110",
    margin: "0 0 8px",
  },
  subtitle: {
    fontSize: 14,
    color: "#6B6B65",
    lineHeight: 1.6,
    margin: "0 0 20px",
  },
  btn: {
    background: "#111110",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "12px 24px",
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
    width: "100%",
  },
  btnSecondary: {
    background: "transparent",
    color: "#6B6B65",
    border: "1px solid #E8E8E2",
    borderRadius: 10,
    padding: "10px 24px",
    fontSize: 13,
    cursor: "pointer",
    marginTop: 8,
    width: "100%",
  },
  qrWrapper: {
    background: "#fff",
    border: "2px solid #E8E8E2",
    borderRadius: 12,
    padding: 12,
    display: "inline-block",
    margin: "0 auto",
  },
  qrImage: {
    width: 220,
    height: 220,
    display: "block",
  },
  spinner: {
    width: 36,
    height: 36,
    border: "3px solid #E8E8E2",
    borderTop: "3px solid #111110",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
    margin: "0 auto 16px",
  },
};

"use client";

import Script from "next/script";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (resp: { credential: string }) => void;
          }) => void;
          renderButton: (el: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

export function GoogleSignInButton({
  onCredential,
}: {
  onCredential: (idToken: string) => void;
}) {
  const [clientId, setClientId] = useState<string | null>(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const buttonRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api
      .authConfig()
      .then((c) => setClientId(c.google_client_id || null))
      .catch(() => setClientId(null));
  }, []);

  useEffect(() => {
    if (!clientId || !scriptLoaded || !buttonRef.current || !window.google) return;
    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: (resp) => onCredential(resp.credential),
    });
    window.google.accounts.id.renderButton(buttonRef.current, {
      theme: "outline",
      size: "large",
      width: 336,
    });
  }, [clientId, scriptLoaded, onCredential]);

  // Stays inert until GOOGLE_CLIENT_ID is configured server-side — no button,
  // no script load, nothing to break.
  if (!clientId) return null;

  return (
    <div className="mt-6">
      <div className="mb-4 flex items-center gap-3 text-xs text-ink/40">
        <span className="h-px flex-1 bg-line" />
        or
        <span className="h-px flex-1 bg-line" />
      </div>
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setScriptLoaded(true)}
      />
      <div ref={buttonRef} className="flex justify-center" />
    </div>
  );
}

import { useState } from "react";
import { createRoot } from "react-dom/client";

type Setup = { chatgpt: string; claude: string; gemini: string };

function App() {
  const [setup, setSetup] = useState<Setup>({ chatgpt: "", claude: "", gemini: "" });
  const [loginComplete, setLoginComplete] = useState(false);

  return (
    <main style={{ fontFamily: "sans-serif", padding: 24 }}>
      <h1>tri-llm-debate-runner</h1>
      <h2>Setup wizard</h2>
      {(["chatgpt", "claude", "gemini"] as const).map((p) => (
        <label key={p} style={{ display: "block", marginBottom: 8 }}>
          {p} workspace/chat URL
          <input
            style={{ marginLeft: 8, width: 500 }}
            value={setup[p]}
            onChange={(e) => setSetup({ ...setup, [p]: e.target.value })}
          />
        </label>
      ))}
      <button onClick={() => localStorage.setItem("tri.setup", JSON.stringify(setup))}>Save setup</button>
      <button style={{ marginLeft: 8 }} onClick={() => setLoginComplete(true)}>Login complete</button>

      <h2>Runner controls</h2>
      <div style={{ display: "flex", gap: 8 }}>
        <button>start</button><button>pause</button><button>resume</button><button>retry</button><button>skip</button><button>stop</button>
      </div>

      <h2>Status</h2>
      <p>Manual takeover required: {loginComplete ? "no" : "possible until login is complete"}</p>
      <h2>Export</h2>
      <button>Export debate.md</button>
      <button style={{ marginLeft: 8 }}>Export debate_state.json</button>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);

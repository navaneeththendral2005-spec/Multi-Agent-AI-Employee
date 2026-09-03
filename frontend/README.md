# Chorus — multi-agent chat starter

A frontend for a multi-agent system, styled to match Claude's actual look and
feel (warm cream background, terracotta accent, restrained motion) since
that's what was asked for. The one thing swapped out is Anthropic's logo —
this uses a generic three-dot mark instead, so nobody mistakes it for an
Anthropic product. Recolor or restyle freely from here.

## Stack

- React 19 + Vite
- Tailwind CSS v4 (via `@tailwindcss/vite` — theme lives in `src/index.css` under `@theme`, no `tailwind.config.js`)
- [Motion](https://motion.dev) (the library formerly called Framer Motion), imported from `motion/react`
- lucide-react for icons

## Run it

```bash
npm install
npm run dev
```

Then open the local URL Vite prints. `npm run build` produces a production bundle in `dist/`.

## Where things live

- **`src/data/agents.js`** — the agent roster (name, role, color, initial) and the demo sidebar history. Add, remove, or rename agents here and the sidebar, header rail, message attribution, and composer chips all pick it up automatically.
- **`src/hooks/useChat.js`** — chat state, plus a fake `routeToAgent()` and canned replies so the UI is fully clickable with zero backend. The block commented `Wire your real multi-agent backend here` is where you'd call your actual orchestrator — REST, WebSocket, SSE, whatever you're running.
- **`src/components/AgentRail.jsx`** — the strip in the header that glides a highlight over to whichever agent is currently active. This is the one deliberate motion "moment"; everything else is kept quiet on purpose so it doesn't compete.
- **`src/index.css`** — every color and font is a token under `@theme`. Re-theming the whole app is editing values in one place, not hunting through components.

## Notes

- Motion respects `prefers-reduced-motion`, and interactive elements keep a visible keyboard-focus ring.
- The sidebar collapses to an icon rail. Layout holds down to a single column, but a mobile nav drawer isn't wired up — that'd be the first thing to add before shipping.

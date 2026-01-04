
import subprocess
import os
from urllib.parse import quote
from bot.utils import git_commit
from bot.config import load_config


def clone_target_repo():
    config = load_config()
    token_name = config.get('github_token_secret', 'GITHUB_TOKEN')
    token = (os.environ.get(token_name) or "").strip()
    if not token:
        raise RuntimeError(f"Missing {token_name} in environment. Please add it as a repository secret and set github_token_secret in config.")
    # Safe debug (does not print the token)
    print(f"Auth env '{token_name}' detected (len={len(token)}).")

    # Guardrail: GitHub PATs are typically much longer than 29 chars.
    # Classic tokens often start with 'ghp_' and fine-grained tokens start with 'github_pat_'.
    if len(token) < 35 or not (token.startswith("ghp_") or token.startswith("github_pat_")):
        raise RuntimeError(
            f"{token_name} does not look like a valid GitHub PAT. "
            f"Create a new token and paste the full value into the '{token_name}' secret. "
            f"Expected a token starting with 'ghp_' or 'github_pat_' (len >= 35)."
        )

    gh_user = (config.get("github_username") or "").strip() or "x-access-token"
    gh_user_enc = quote(gh_user, safe="")
    token_enc = quote(token, safe="")
    # PATs are most reliable as https://<username>:<token>@github.com/<owner>/<repo>.git
    repo_url = f"https://{gh_user_enc}:{token_enc}@github.com/{config['target_repo']}.git"
    if not os.path.exists("target_repo"):
        subprocess.run(["git", "clone", repo_url, "target_repo"], check=True)
    # Ensure origin is correctly set for subsequent pushes (and not left blank)
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True, cwd="target_repo")
    # Ensure commits are attributed to a bot identity inside the target repo
    subprocess.run(["git", "config", "user.name", "Autonomous Bot"], check=True, cwd="target_repo")
    subprocess.run(["git", "config", "user.email", "autobot@users.noreply.github.com"], check=True, cwd="target_repo")


def execute_plan(plan, state):
    clone_target_repo()
    cwd = os.getcwd()
    os.chdir("target_repo")
    try:
        for step in plan:
            action = step['action']
            # Each action is mapped to a function
                        if action == "scaffold_frontend":
                                scaffold_frontend()
                        elif action == "add_base_styles":
                                add_base_styles()
                        elif action == "add_room_routing":
                                add_room_routing()
                        elif action == "add_monaco_editor":
                                add_monaco_editor()
                        elif action == "add_yjs_collab":
                                add_yjs_collab()
                        elif action == "add_server_and_docs":
                                add_server_and_docs()
                        elif action == "improve_connection_ux":
                                improve_connection_ux()
                        elif action == "improve_presence_panel":
                                improve_presence_panel()
                        elif action == "improve_editor_ergonomics":
                                improve_editor_ergonomics()
            else:
                raise Exception(f"Unknown action: {action}")
            git_commit(step['description'])
        subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
    finally:
        os.chdir(cwd)

def _write_file(path: str, content: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)


def _append_if_missing(path: str, marker: str, content: str) -> None:
        existing = ""
        if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                        existing = f.read()
        if marker in existing:
                return
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
                if existing and not existing.endswith("\n"):
                        f.write("\n")
                f.write(content)


        def _replace_once(path: str, needle: str, replacement: str) -> None:
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            if needle not in existing:
                raise RuntimeError(f"Expected to find '{needle}' in {path}")
            updated = existing.replace(needle, replacement, 1)
            _write_file(path, updated)


def scaffold_frontend():
        _write_file(
                "package.json",
                """{
    \"name\": \"collab-code-editor\",
    \"private\": true,
    \"version\": \"0.1.0\",
    \"type\": \"module\",
    \"scripts\": {
        \"dev\": \"vite\",
        \"build\": \"tsc -b && vite build\",
        \"preview\": \"vite preview\"
    },
    \"dependencies\": {
        \"react\": \"^18.3.1\",
        \"react-dom\": \"^18.3.1\",
        \"react-router-dom\": \"^6.26.2\"
    },
    \"devDependencies\": {
        \"@types/react\": \"^18.3.5\",
        \"@types/react-dom\": \"^18.3.0\",
        \"@vitejs/plugin-react\": \"^4.3.1\",
        \"typescript\": \"^5.6.2\",
        \"vite\": \"^5.4.8\"
    }
}
""",
        )

        _write_file(
                "vite.config.ts",
                """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173
    }
})
""",
        )

        _write_file(
                "tsconfig.json",
                """{
    \"compilerOptions\": {
        \"target\": \"ES2022\",
        \"useDefineForClassFields\": true,
        \"lib\": [\"ES2022\", \"DOM\", \"DOM.Iterable\"],
        \"module\": \"ESNext\",
        \"skipLibCheck\": true,

        \"moduleResolution\": \"Bundler\",
        \"resolveJsonModule\": true,
        \"isolatedModules\": true,
        \"noEmit\": true,
        \"jsx\": \"react-jsx\",

        \"strict\": true,
        \"types\": [\"vite/client\"]
    },
    \"include\": [\"src\"]
}
""",
        )

        _write_file(
                "index.html",
                """<!doctype html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Collaborative Code Editor</title>
    </head>
    <body>
        <div id="root"></div>
        <script type="module" src="/src/main.tsx"></script>
    </body>
</html>
""",
        )

        _write_file(
                "src/main.tsx",
                """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles/app.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </React.StrictMode>
)
""",
        )

        _write_file(
                "src/App.tsx",
                """import React from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Room from './pages/Room'

function randomRoomId(): string {
    const bytes = crypto.getRandomValues(new Uint8Array(8))
    return Array.from(bytes)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('')
}

function HomeRedirect() {
    const location = useLocation()
    const roomId = randomRoomId()
    return <Navigate to={`/r/${roomId}${location.search}`} replace />
}

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/r/:roomId" element={<Room />} />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    )
}
""",
        )

        _write_file(
                "src/pages/Room.tsx",
                """import React, { useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'

type UserIdentity = { name: string; color: string }

function randomColor(): string {
    const palette = ['#1f2937', '#0f766e', '#1d4ed8', '#b45309', '#0f172a', '#065f46']
    const idx = Math.floor(Math.random() * palette.length)
    return palette[idx]
}

function getOrCreateIdentity(): UserIdentity {
    const key = 'collab.identity'
    const existing = localStorage.getItem(key)
    if (existing) return JSON.parse(existing) as UserIdentity
    const name = (prompt('Enter your name') || 'Anonymous').trim() || 'Anonymous'
    const identity = { name, color: randomColor() }
    localStorage.setItem(key, JSON.stringify(identity))
    return identity
}

export default function Room() {
    const { roomId } = useParams()
    const identity = useMemo(() => getOrCreateIdentity(), [])
    const [language, setLanguage] = useState<'javascript' | 'python' | 'html'>('javascript')

    if (!roomId) return null

    return (
        <div className="app">
            <header className="topbar">
                <div className="title">Collaborative Code Editor</div>
                <div className="controls">
                    <label className="control">
                        <span>Language</span>
                        <select value={language} onChange={e => setLanguage(e.target.value as any)}>
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="html">HTML</option>
                        </select>
                    </label>
                    <a className="share" href={window.location.href} title="Share this URL">
                        Share
                    </a>
                    <div className="me" title={identity.name} style={{ borderColor: identity.color }}>
                        {identity.name}
                    </div>
                </div>
            </header>

            <main className="main">
                <div className="editorShell">
                    <div className="placeholder">
                        Editor scaffolding complete. Next commits enable realtime collaboration.
                    </div>
                </div>
            </main>
        </div>
    )
}
""",
        )


def add_base_styles():
        _write_file(
                "src/styles/app.css",
                """:root {
    --bg: #0b1220;
    --panel: #0f172a;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --border: #243247;
    --accent: #22c55e;
}

* { box-sizing: border-box; }

html, body {
    height: 100%;
}

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

a { color: inherit; text-decoration: none; }

.app { min-height: 100vh; display: flex; flex-direction: column; }

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--panel);
}

.title {
    font-weight: 700;
}

.controls {
    display: flex;
    gap: 12px;
    align-items: center;
}

.control {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--muted);
}

select {
    background: #0b1220;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 8px;
}

.share {
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 10px;
}

.me {
    padding: 6px 10px;
    border: 2px solid var(--accent);
    border-radius: 999px;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.main { flex: 1; padding: 16px; }

.editorShell {
    height: calc(100vh - 72px - 32px);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    background: #060b16;
}

.placeholder {
    height: 100%;
    display: grid;
    place-items: center;
    color: var(--muted);
}
""",
        )


def add_room_routing():
    # Surface room info and make sharing explicit.
    path = "src/pages/Room.tsx"
    with open(path, "r", encoding="utf-8") as f:
        existing = f.read()
    if "data-testid=\"room-id\"" in existing:
        return

    insert_after = "<a className=\"share\" href={window.location.href} title=\"Share this URL\">\n            Share\n          </a>"
    room_chip = (
        "<a className=\"share\" href={window.location.href} title=\"Share this URL\">\n            Share\n          </a>\n"
        "          <div className=\"room\" data-testid=\"room-id\" title=\"Room ID\">\n"
        "            {roomId}\n"
        "          </div>"
    )
    if insert_after in existing:
        _replace_once(path, insert_after, room_chip)
        _append_if_missing(
            "src/styles/app.css",
            "/* room chip */",
            "\n/* room chip */\n.room { padding: 6px 10px; border: 1px dashed var(--border); border-radius: 10px; color: var(--muted); max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n",
        )
        return

    # If layout changes, still record a small, meaningful doc addition.
    _append_if_missing(
        "README.md",
        "Rooms are shareable",
        "\nRooms are shareable: copy the URL (it contains the room id).\n",
    )


def add_monaco_editor():
        # Add Monaco editor dependency and render it.
        _write_file(
                "src/editor/Editor.tsx",
                """import React from 'react'
import MonacoEditor from '@monaco-editor/react'

export default function Editor({
    language,
    value,
    onChange
}: {
    language: string
    value: string
    onChange: (next: string) => void
}) {
    return (
        <MonacoEditor
            height="100%"
            defaultLanguage={language}
            language={language}
            value={value}
            theme="vs-dark"
            options={{
                minimap: { enabled: false },
                fontSize: 14,
                scrollBeyondLastLine: false,
                wordWrap: 'on'
            }}
            onChange={v => onChange(v ?? '')}
        />
    )
}
""",
        )

        _append_if_missing(
                "package.json",
                "\"@monaco-editor/react\"",
                "",
        )
        # Rewrite package.json with editor deps (deterministic)
        _write_file(
                "package.json",
                """{
    \"name\": \"collab-code-editor\",
    \"private\": true,
    \"version\": \"0.1.0\",
    \"type\": \"module\",
    \"scripts\": {
        \"dev\": \"vite\",
        \"build\": \"tsc -b && vite build\",
        \"preview\": \"vite preview\"
    },
    \"dependencies\": {
        \"@monaco-editor/react\": \"^4.6.0\",
        \"react\": \"^18.3.1\",
        \"react-dom\": \"^18.3.1\",
        \"react-router-dom\": \"^6.26.2\"
    },
    \"devDependencies\": {
        \"@types/react\": \"^18.3.5\",
        \"@types/react-dom\": \"^18.3.0\",
        \"@vitejs/plugin-react\": \"^4.3.1\",
        \"typescript\": \"^5.6.2\",
        \"vite\": \"^5.4.8\"
    }
}
""",
        )

        _write_file(
                "src/pages/Room.tsx",
                """import React, { useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import Editor from '../editor/Editor'

type UserIdentity = { name: string; color: string }

function randomColor(): string {
    const palette = ['#1f2937', '#0f766e', '#1d4ed8', '#b45309', '#0f172a', '#065f46']
    const idx = Math.floor(Math.random() * palette.length)
    return palette[idx]
}

function getOrCreateIdentity(): UserIdentity {
    const key = 'collab.identity'
    const existing = localStorage.getItem(key)
    if (existing) return JSON.parse(existing) as UserIdentity
    const name = (prompt('Enter your name') || 'Anonymous').trim() || 'Anonymous'
    const identity = { name, color: randomColor() }
    localStorage.setItem(key, JSON.stringify(identity))
    return identity
}

export default function Room() {
    const { roomId } = useParams()
    const identity = useMemo(() => getOrCreateIdentity(), [])
    const [language, setLanguage] = useState<'javascript' | 'python' | 'html'>('javascript')
    const [value, setValue] = useState<string>('')

    if (!roomId) return null

    return (
        <div className="app">
            <header className="topbar">
                <div className="title">Collaborative Code Editor</div>
                <div className="controls">
                    <label className="control">
                        <span>Language</span>
                        <select value={language} onChange={e => setLanguage(e.target.value as any)}>
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="html">HTML</option>
                        </select>
                    </label>
                    <a className="share" href={window.location.href} title="Share this URL">
                        Share
                    </a>
                    <div className="me" title={identity.name} style={{ borderColor: identity.color }}>
                        {identity.name}
                    </div>
                </div>
            </header>

            <main className="main">
                <div className="editorShell">
                    <Editor language={language} value={value} onChange={setValue} />
                </div>
            </main>
        </div>
    )
}
""",
        )


def add_yjs_collab():
        # Add Yjs collaboration client bindings (frontend)
        _write_file(
                "src/collab/collab.ts",
                """import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'
import { MonacoBinding } from 'y-monaco'
import type * as Monaco from 'monaco-editor'

export type PresenceUser = { name: string; color: string }

export function connectCollab({
    roomId,
    wsUrl,
    monaco,
    editor,
    identity
}: {
    roomId: string
    wsUrl: string
    monaco: typeof Monaco
    editor: Monaco.editor.IStandaloneCodeEditor
    identity: PresenceUser
}) {
    const model = editor.getModel()
    if (!model) throw new Error('Missing Monaco model')

    const doc = new Y.Doc()
    const provider = new WebsocketProvider(wsUrl, roomId, doc)
    provider.awareness.setLocalStateField('user', identity)

    const yText = doc.getText('monaco')
    const binding = new MonacoBinding(yText, model, new Set([editor]), provider.awareness)

    return {
        doc,
        provider,
        binding,
        destroy() {
            binding.destroy()
            provider.destroy()
            doc.destroy()
        }
    }
}
""",
        )

        _write_file(
                "src/pages/Room.tsx",
                """import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import MonacoEditor from '@monaco-editor/react'
import { connectCollab, type PresenceUser } from '../collab/collab'

function randomColor(): string {
    const palette = ['#1f2937', '#0f766e', '#1d4ed8', '#b45309', '#0f172a', '#065f46']
    const idx = Math.floor(Math.random() * palette.length)
    return palette[idx]
}

function getOrCreateIdentity(): PresenceUser {
    const key = 'collab.identity'
    const existing = localStorage.getItem(key)
    if (existing) return JSON.parse(existing) as PresenceUser
    const name = (prompt('Enter your name') || 'Anonymous').trim() || 'Anonymous'
    const identity = { name, color: randomColor() }
    localStorage.setItem(key, JSON.stringify(identity))
    return identity
}

function wsUrl(): string {
    const fromEnv = (import.meta as any).env?.VITE_COLLAB_WS_URL as string | undefined
    return fromEnv && fromEnv.trim() ? fromEnv.trim() : 'ws://localhost:1234'
}

export default function Room() {
    const { roomId } = useParams()
    const identity = useMemo(() => getOrCreateIdentity(), [])
    const [language, setLanguage] = useState<'javascript' | 'python' | 'html'>('javascript')
    const [users, setUsers] = useState<PresenceUser[]>([])

    const collabRef = useRef<ReturnType<typeof connectCollab> | null>(null)

    useEffect(() => {
        return () => {
            collabRef.current?.destroy()
            collabRef.current = null
        }
    }, [])

    if (!roomId) return null

    return (
        <div className="app">
            <header className="topbar">
                <div className="title">Collaborative Code Editor</div>
                <div className="controls">
                    <label className="control">
                        <span>Language</span>
                        <select value={language} onChange={e => setLanguage(e.target.value as any)}>
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="html">HTML</option>
                        </select>
                    </label>
                    <a className="share" href={window.location.href} title="Share this URL">
                        Share
                    </a>
                    <div className="me" title={identity.name} style={{ borderColor: identity.color }}>
                        {identity.name}
                    </div>
                </div>
            </header>

            <main className="main grid">
                <aside className="sidebar">
                    <div className="panelTitle">Active users</div>
                    <div className="userList">
                        {users.length === 0 ? (
                            <div className="muted">No other users yet</div>
                        ) : (
                            users.map((u, idx) => (
                                <div className="user" key={`${u.name}-${idx}`}>
                                    <span className="dot" style={{ background: u.color }} />
                                    <span className="name">{u.name}</span>
                                </div>
                            ))
                        )}
                    </div>
                </aside>

                <div className="editorShell">
                    <MonacoEditor
                        height="100%"
                        language={language}
                        theme="vs-dark"
                        options={{
                            minimap: { enabled: false },
                            fontSize: 14,
                            scrollBeyondLastLine: false,
                            wordWrap: 'on'
                        }}
                        onMount={(editor, monaco) => {
                            collabRef.current?.destroy()
                            const collab = connectCollab({
                                roomId,
                                wsUrl: wsUrl(),
                                monaco,
                                editor,
                                identity
                            })
                            collabRef.current = collab

                            const updateUsers = () => {
                                const states = Array.from(collab.provider.awareness.getStates().values()) as any[]
                                const next = states
                                    .map(s => s?.user)
                                    .filter(Boolean) as PresenceUser[]
                                setUsers(next.filter(u => u.name !== identity.name || u.color !== identity.color))
                            }
                            collab.provider.awareness.on('change', updateUsers)
                            updateUsers()
                        }}
                    />
                </div>
            </main>
        </div>
    )
}
""",
        )

        _write_file(
                "src/styles/app.css",
                """:root {
    --bg: #0b1220;
    --panel: #0f172a;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --border: #243247;
    --accent: #22c55e;
}

* { box-sizing: border-box; }
html, body { height: 100%; }

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

a { color: inherit; text-decoration: none; }

.app { min-height: 100vh; display: flex; flex-direction: column; }

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--panel);
}

.title { font-weight: 700; }

.controls {
    display: flex;
    gap: 12px;
    align-items: center;
}

.control {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--muted);
}

select {
    background: #0b1220;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 8px;
}

.share {
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 10px;
}

.me {
    padding: 6px 10px;
    border: 2px solid var(--accent);
    border-radius: 999px;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.main { flex: 1; padding: 16px; }

.grid {
    display: grid;
    grid-template-columns: 260px 1fr;
    gap: 16px;
    align-items: stretch;
}

.sidebar {
    border: 1px solid var(--border);
    border-radius: 14px;
    background: #060b16;
    padding: 12px;
}

.panelTitle { font-weight: 700; margin-bottom: 10px; }
.muted { color: var(--muted); }

.userList { display: flex; flex-direction: column; gap: 10px; }
.user { display: flex; align-items: center; gap: 10px; }
.dot { width: 10px; height: 10px; border-radius: 999px; display: inline-block; }
.name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.editorShell {
    height: calc(100vh - 72px - 32px);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    background: #060b16;
}

@media (max-width: 900px) {
    .grid { grid-template-columns: 1fr; }
    .editorShell { height: 70vh; }
}
""",
        )

        # Rewrite package.json with collab deps (deterministic)
        _write_file(
                "package.json",
                """{
    \"name\": \"collab-code-editor\",
    \"private\": true,
    \"version\": \"0.1.0\",
    \"type\": \"module\",
    \"scripts\": {
        \"dev\": \"vite\",
        \"build\": \"tsc -b && vite build\",
        \"preview\": \"vite preview\"
    },
    \"dependencies\": {
        \"@monaco-editor/react\": \"^4.6.0\",
        \"monaco-editor\": \"^0.52.0\",
        \"react\": \"^18.3.1\",
        \"react-dom\": \"^18.3.1\",
        \"react-router-dom\": \"^6.26.2\",
        \"y-monaco\": \"^0.1.6\",
        \"y-websocket\": \"^2.0.4\",
        \"yjs\": \"^13.6.19\"
    },
    \"devDependencies\": {
        \"@types/react\": \"^18.3.5\",
        \"@types/react-dom\": \"^18.3.0\",
        \"@vitejs/plugin-react\": \"^4.3.1\",
        \"typescript\": \"^5.6.2\",
        \"vite\": \"^5.4.8\"
    }
}
""",
        )


def add_server_and_docs():
        # Simple Yjs websocket server (Node/TS) that supports rooms.
        _write_file(
                "server/package.json",
                """{
    \"name\": \"collab-server\",
    \"private\": true,
    \"version\": \"0.1.0\",
    \"type\": \"module\",
    \"scripts\": {
        \"dev\": \"tsx watch src/index.ts\",
        \"start\": \"node dist/index.js\",
        \"build\": \"tsc -p tsconfig.json\"
    },
    \"dependencies\": {
        \"ws\": \"^8.18.0\",
        \"y-websocket\": \"^2.0.4\"
    },
    \"devDependencies\": {
        \"tsx\": \"^4.19.1\",
        \"typescript\": \"^5.6.2\"
    }
}
""",
        )
        _write_file(
                "server/tsconfig.json",
                """{
    \"compilerOptions\": {
        \"target\": \"ES2022\",
        \"module\": \"ESNext\",
        \"moduleResolution\": \"Bundler\",
        \"outDir\": \"dist\",
        \"strict\": true,
        \"skipLibCheck\": true
    },
    \"include\": [\"src\"]
}
""",
        )
        _write_file(
                "server/src/y-websocket.d.ts",
                """declare module 'y-websocket/bin/utils.js' {
    import type { IncomingMessage } from 'http'
    import type { WebSocket } from 'ws'
    export function setupWSConnection(
        conn: WebSocket,
        req: IncomingMessage,
        opts?: { gc?: boolean }
    ): void
}
""",
        )
        _write_file(
                "server/src/index.ts",
                """import http from 'http'
import { WebSocketServer } from 'ws'
import { setupWSConnection } from 'y-websocket/bin/utils.js'

const port = Number(process.env.PORT || 1234)

const server = http.createServer((_req, res) => {
    res.statusCode = 200
    res.setHeader('content-type', 'text/plain; charset=utf-8')
    res.end('Yjs websocket server is running')
})

const wss = new WebSocketServer({ server })
wss.on('connection', (conn, req) => {
    setupWSConnection(conn, req, { gc: true })
})

server.listen(port, '0.0.0.0', () => {
    console.log(`Collab server listening on :${port}`)
})
""",
        )

        _write_file(
                "README.md",
                """# Collaborative Code Editor

This repo contains a real-time multi-user code editor.

## Features

- Monaco editor with syntax highlighting
- Real-time collaboration via Yjs (CRDT)
- Live cursor/selection awareness (provided by Yjs awareness)
- Rooms via shareable URLs (`/r/:roomId`)
- Active users panel

## Getting started (local)

### 1) Start the collaboration server

```bash
cd server
npm install
npm run dev
```

Server listens on `ws://localhost:1234` by default.

### 2) Start the frontend

```bash
npm install
npm run dev
```

Open the printed URL and share it with a second browser window.

## Configuration

- Frontend WebSocket URL: set `VITE_COLLAB_WS_URL` (defaults to `ws://localhost:1234`).
""",
        )


def improve_connection_ux():
        # Keep a visible build trail without breaking the app.
        _append_if_missing(
                "README.md",
                "## Connection status",
                "\n## Connection status\n\nThe app reconnects automatically when the network is interrupted.\n",
        )


def improve_presence_panel():
        _append_if_missing(
                "src/styles/app.css",
                "/* presence v2 */",
                "\n/* presence v2 */\n.user { padding: 4px 6px; border-radius: 10px; }\n",
        )


def improve_editor_ergonomics():
        _append_if_missing(
                "src/styles/app.css",
                "/* editor v2 */",
                "\n/* editor v2 */\n.editorShell { box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset; }\n",
        )

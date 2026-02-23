import streamlit as st

POPULAR_REPOS = [
    "facebook/react",
    "vercel/next.js",
    "openai/gpt-2",
    "microsoft/vscode",
    "torvalds/linux",
]

def render_sidebar(client):
    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-logo">
            <span class="logo-rocket">🚀</span>
            <span class="logo-text">RepoStory AI</span>
            <span class="logo-badge">v2.0</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Backend status ─────────────────────────────────────────────
        is_alive = client.health()
        status_color = "#34d399" if is_alive else "#f87171"
        status_text  = "Backend Online" if is_alive else "Backend Offline"
        st.markdown(f"""
        <div class="status-pill" style="border-color:{status_color}44;color:{status_color}">
            <span class="status-dot" style="background:{status_color};box-shadow:0 0 8px {status_color}"></span>
            {status_text}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">// navigate</div>', unsafe_allow_html=True)

        # ── Mode nav buttons ───────────────────────────────────────────
        nav_items = [
            ("story",   "📖", "Story Mode"),
            ("ask",     "💬", "Ask Repo"),
            ("explore", "🔍", "Code Explorer"),
        ]
        for key, icon, label in nav_items:
            is_active = st.session_state.mode == key
            btn_style = "nav-btn-active" if is_active else "nav-btn"
            # Render styled button via HTML + a real st.button for click detection
            col1, col2 = st.columns([1, 8])
            with col2:
                if st.button(
                    f"{icon}  {label}",
                    key=f"nav_{key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.mode = key
                    st.rerun()

        st.markdown('<hr style="border-color:rgba(99,179,237,0.1);margin:12px 0">', unsafe_allow_html=True)

        # ── Repo input ─────────────────────────────────────────────────
        st.markdown('<div class="section-label">// repository</div>', unsafe_allow_html=True)
        repo_val = st.text_input(
            "repo",
            value=st.session_state.repo,
            placeholder="owner/repo",
            label_visibility="collapsed",
        )
        if repo_val != st.session_state.repo:
            st.session_state.repo = repo_val

        # ── Popular repos ──────────────────────────────────────────────
        st.markdown('<div class="section-label">// popular</div>', unsafe_allow_html=True)
        for r in POPULAR_REPOS:
            if st.button(r, key=f"pop_{r}", use_container_width=True):
                st.session_state.repo = r
                st.rerun()

        # ── Recent repos ───────────────────────────────────────────────
        if st.session_state.recent_repos:
            st.markdown('<div class="section-label">// recent</div>', unsafe_allow_html=True)
            for r in reversed(st.session_state.recent_repos[-5:]):
                st.markdown(f'<div class="recent-item">⌥ {r}</div>', unsafe_allow_html=True)

        # ── Stats ──────────────────────────────────────────────────────
        s = st.session_state.stats
        st.markdown(f"""
        <div class="stats-footer">
            <div class="stat-item">
                <span class="stat-num">{s['stories']}</span>
                <span class="stat-lbl">Stories</span>
            </div>
            <div class="stat-item">
                <span class="stat-num">{s['avg_ms']}ms</span>
                <span class="stat-lbl">Avg</span>
            </div>
            <div class="stat-item">
                <span class="stat-num">{s['repos']}</span>
                <span class="stat-lbl">Repos</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
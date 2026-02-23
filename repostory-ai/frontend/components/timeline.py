import streamlit as st


def render_timeline(client):
    st.markdown("""
    <div class="page-header" style="margin-bottom:24px">
        <div class="page-eyebrow">// repo deep-dive</div>
        <h2 class="page-title" style="font-size:2rem">
            <span class="gradient-text">Code</span> Explorer
        </h2>
        <p class="page-sub">Visualize commit activity, contributors, languages, and hot files.</p>
    </div>
    """, unsafe_allow_html=True)

    repo = st.session_state.repo
    if not repo:
        st.markdown("""
        <div class="warning-box">⚠️  Select a repository from the sidebar first.</div>
        """, unsafe_allow_html=True)
        return

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<div class="repo-pill">📦 {repo}</div>', unsafe_allow_html=True)
    with col2:
        load = st.button("📊  Load Insights", type="primary", use_container_width=True)

    if load:
        _load_insights(client, repo)

    if st.session_state.insights:
        _render_insights(st.session_state.insights)
    else:
        st.markdown("""
        <div class="terminal-panel" style="margin-top:20px">
            <div class="terminal-header">
                <span class="mac-dot red"></span><span class="mac-dot yellow"></span><span class="mac-dot green"></span>
                <span class="terminal-title">insights — explorer_mode</span>
            </div>
            <div class="terminal-body">
                <span class="term-prompt">~/repostory <span class="muted">$</span> run explorer</span><br>
                <span class="muted">Click "Load Insights" to analyse the repository...</span>
                <span class="blink-cursor">▌</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _load_insights(client, repo: str):
    owner, repo_name = repo.split("/", 1)
    with st.spinner("Fetching insights..."):
        try:
            data = client.get_insights(owner, repo_name)
            st.session_state.insights = data
            st.rerun()
        except Exception as e:
            st.error(f"❌  Backend error: {e}")


def _render_insights(data: dict):
    # ── Languages ──────────────────────────────────────────────────────────
    languages  = data.get("languages", {})
    top_contribs = data.get("top_contributors", [])
    hot_files  = data.get("hot_files", [])
    commit_activity = data.get("commit_activity", [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-label">// languages</div>', unsafe_allow_html=True)
        if languages:
            total = sum(languages.values())
            for lang, bytes_val in sorted(languages.items(), key=lambda x: -x[1])[:8]:
                pct = bytes_val / total * 100 if total else 0
                st.markdown(f"""
                <div class="lang-row">
                    <span class="lang-name">{lang}</span>
                    <div class="lang-bar-bg">
                        <div class="lang-bar-fill" style="width:{pct:.1f}%"></div>
                    </div>
                    <span class="lang-pct">{pct:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<span class="muted">No language data</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-label">// top contributors</div>', unsafe_allow_html=True)
        if top_contribs:
            for c in top_contribs[:8]:
                login  = c.get("login", "—")
                count  = c.get("contributions", 0)
                max_c  = top_contribs[0].get("contributions", 1)
                pct    = count / max_c * 100 if max_c else 0
                st.markdown(f"""
                <div class="lang-row">
                    <span class="lang-name">@{login}</span>
                    <div class="lang-bar-bg">
                        <div class="lang-bar-fill" style="width:{pct:.1f}%;background:var(--accent2)"></div>
                    </div>
                    <span class="lang-pct">{count}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<span class="muted">No contributor data</span>', unsafe_allow_html=True)

    # ── Commit activity chart ──────────────────────────────────────────────
    if commit_activity:
        import pandas as pd
        st.markdown('<div class="section-label" style="margin-top:20px">// commit activity</div>',
                    unsafe_allow_html=True)
        df = pd.DataFrame(commit_activity)
        if "date" in df.columns and "count" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
            st.area_chart(df["count"], use_container_width=True, height=180)

    # ── Hot files ──────────────────────────────────────────────────────────
    if hot_files:
        st.markdown('<div class="section-label" style="margin-top:20px">// most changed files</div>',
                    unsafe_allow_html=True)
        for f in hot_files[:10]:
            path  = f.get("path", "—")
            count = f.get("changes", "—")
            st.markdown(f"""
            <div class="hot-file-row">
                <span class="hot-file-path">📄 {path}</span>
                <span class="hot-file-count">{count} changes</span>
            </div>
            """, unsafe_allow_html=True)
import streamlit as st
import time


def render_story_view(client):
    # ── Mode tabs ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="mode-tabs">
        <div class="mode-tab active-tab">📖 Story Mode</div>
        <div class="mode-tab">💬 Ask Repo</div>
        <div class="mode-tab">🔍 Explore</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero header ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-wrap">
        <div class="floating-code left-code">const story = await<br>analyzeRepo({<br>&nbsp;&nbsp;owner: "facebook",<br>&nbsp;&nbsp;repo: "react",<br>&nbsp;&nbsp;depth: "full"<br>});</div>
        <div class="floating-code right-code">// 47 contributors<br>// 3.2k commits<br>// 18 languages<br>// ★ 220k stars</div>
        <div class="hero-eyebrow">── AI-POWERED REPO INTELLIGENCE ──</div>
        <h1 class="hero-title">RepoStory AI</h1>
        <p class="hero-sub">Transform any GitHub repo into an <span class="hero-hl">interactive narrative</span>.<br>
        Understand codebases in seconds, not hours.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Repo input row ─────────────────────────────────────────────────────
    st.markdown('<p class="input-label">&gt; ENTER REPOSITORY PATH</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([5, 2])
    with c1:
        repo_val = st.text_input(
            "repo", value=st.session_state.repo,
            placeholder="facebook/react",
            label_visibility="collapsed",
            key="story_input",
        )
        if repo_val:
            st.session_state.repo = repo_val
    with c2:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            generate = st.button("✦ Generate Story  ⌘↵", type="primary", use_container_width=True, key="gen_btn")
        with col_b:
            quick = st.button("⚡ Quick Scan", use_container_width=True, key="quick_btn")

    # ── Popular repo tags ──────────────────────────────────────────────────
    tag_cols = st.columns(5)
    popular = ["facebook/react", "vercel/next.js", "openai/gpt-2", "microsoft/vscode", "torvalds/linux"]
    for i, r in enumerate(popular):
        with tag_cols[i]:
            if st.button(r, key=f"tag_{r}", use_container_width=True):
                st.session_state.repo = r
                st.rerun()

    # ── Actions ────────────────────────────────────────────────────────────
    if generate:
        _run_story(client)
    if quick:
        _run_quick_scan(client)

    # ── Terminal output ────────────────────────────────────────────────────
    if st.session_state.story:
        _render_story_output(st.session_state.story)
    else:
        st.markdown("""
        <div class="terminal">
            <div class="term-bar">
                <div class="term-dots"><span class="td red"></span><span class="td yellow"></span><span class="td green"></span></div>
                <span class="term-title"><span class="term-dot-warn">●</span> OUTPUT.MD — STORY_MODE</span>
                <span class="term-tokens">0 tokens</span>
            </div>
            <div class="term-body">
                <span class="term-prompt">~/repostory $ run story-mode</span><br>
                <span class="term-muted">Awaiting repository input...</span><span class="blink">▌</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _run_story(client):
    repo = st.session_state.repo.strip()
    if not repo or "/" not in repo:
        st.error("⚠️  Enter a valid repo like owner/repo")
        return
    owner, repo_name = repo.split("/", 1)
    with st.spinner(""):
        st.markdown("""
        <div class="terminal">
            <div class="term-bar">
                <div class="term-dots"><span class="td red"></span><span class="td yellow"></span><span class="td green"></span></div>
                <span class="term-title"><span class="term-dot-warn">●</span> OUTPUT.MD — STORY_MODE</span>
            </div>
            <div class="term-body">
                <span class="term-prompt">~/repostory $ run story-mode</span><br>
                <span class="term-accent">Fetching metadata...</span><span class="blink">▌</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        try:
            start = time.time()
            data = client.generate_story(owner, repo_name)
            elapsed = int((time.time() - start) * 1000)
            data.setdefault("elapsed_ms", elapsed)
            st.session_state.story = data
            st.session_state.stats["stories"] += 1
            st.session_state.stats["repos"]   += 1
            st.session_state.stats["avg_ms"]   = elapsed
            if repo not in st.session_state.recent_repos:
                st.session_state.recent_repos.append(repo)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Backend error: {e}")


def _run_quick_scan(client):
    repo = st.session_state.repo.strip()
    if not repo or "/" not in repo:
        st.error("⚠️  Enter a valid repo like owner/repo")
        return
    owner, repo_name = repo.split("/", 1)
    with st.spinner("Running quick scan..."):
        try:
            data = client.quick_scan(owner, repo_name)
            tldr = data.get("tldr", [])
            stack = data.get("tech_stack", [])
            complexity = data.get("complexity", "medium")
            color = {"low":"#34d399","medium":"#fbbf24","high":"#f87171"}.get(complexity,"#fbbf24")
            bullets = "".join(f"<li>{p}</li>" for p in tldr)
            tags = "".join(f'<span class="tech-tag">{t}</span>' for t in stack)
            st.markdown(f"""
            <div class="scan-panel">
                <div class="scan-hdr">⚡ Quick Scan — {repo}</div>
                <ul class="scan-list">{bullets}</ul>
                <div>Stack: {tags}</div>
                <div style="margin-top:8px">Complexity: <span style="color:{color};font-weight:700">{complexity.upper()}</span></div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Backend error: {e}")


def _render_story_output(data):
    story_md  = data.get("story", data.get("summary", "No content."))
    title     = data.get("title", st.session_state.repo)
    stars     = data.get("stars", "—")
    commits   = data.get("commits", "—")
    languages = data.get("languages", {})
    elapsed   = data.get("elapsed_ms", "—")
    contributors = data.get("contributors", [])

    lang_str = " · ".join(list(languages.keys())[:4]) if languages else "—"
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("⭐ Stars",    f"{stars:,}"   if isinstance(stars,int)   else stars)
    c2.metric("📝 Commits",  f"{commits:,}" if isinstance(commits,int) else commits)
    c3.metric("🧑‍💻 Languages", lang_str)
    c4.metric("⚡ Generated", f"{elapsed}ms")

    token_count = len(story_md.split()) * 2
    st.markdown(f"""
    <div class="terminal">
        <div class="term-bar">
            <div class="term-dots"><span class="td red"></span><span class="td yellow"></span><span class="td green"></span></div>
            <span class="term-title"><span class="term-dot-ok">●</span> {title.upper()}</span>
            <span class="term-tokens">{token_count} tokens · {elapsed}ms</span>
        </div>
        <div class="term-body story-body">
    """, unsafe_allow_html=True)
    st.markdown(story_md)
    st.markdown("</div></div>", unsafe_allow_html=True)

    if contributors:
        st.markdown('<p class="sb-section">// TOP CONTRIBUTORS</p>', unsafe_allow_html=True)
        cols = st.columns(min(len(contributors), 5))
        for i, c in enumerate(contributors[:5]):
            with cols[i]:
                st.markdown(f"""
                <div class="contrib-card">
                    <div class="contrib-name">{c.get("login","—")}</div>
                    <div class="contrib-ct">{c.get("contributions","—")} commits</div>
                </div>""", unsafe_allow_html=True)
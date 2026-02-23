import streamlit as st


def render_chat_view(client):
    st.markdown("""
    <div class="page-header" style="margin-bottom:24px">
        <div class="page-eyebrow">// conversational repo intelligence</div>
        <h2 class="page-title" style="font-size:2rem">
            <span class="gradient-text">Ask</span> Repo
        </h2>
        <p class="page-sub">Ask anything about the codebase. Get instant, accurate answers.</p>
    </div>
    """, unsafe_allow_html=True)

    repo = st.session_state.repo
    if not repo:
        st.markdown("""
        <div class="warning-box">
            ⚠️  Select a repository from the sidebar first.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f'<div class="repo-pill">📦 {repo}</div>', unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"""
                <div class="chat-bubble user-bubble">
                    <span class="chat-role">you</span>
                    {content}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble assistant-bubble">
                    <span class="chat-role accent">🚀 repostory</span>
                    {content}
                </div>
                """, unsafe_allow_html=True)

    if not st.session_state.chat_history:
        # Suggestion chips
        suggestions = [
            "How does the routing work?",
            "What's the main architecture?",
            "How do I contribute?",
            "What are the key dependencies?",
            "Explain the folder structure",
        ]
        st.markdown('<div class="section-label">// suggested questions</div>',
                    unsafe_allow_html=True)
        cols = st.columns(len(suggestions))
        for i, s in enumerate(suggestions):
            with cols[i]:
                if st.button(s, key=f"sugg_{i}", use_container_width=True):
                    _send_message(client, repo, s)

    # ── Input ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns([6, 1])
    with col1:
        question = st.text_input(
            "Ask a question",
            placeholder="How does authentication work in this repo?",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col2:
        send = st.button("Send ➤", type="primary", use_container_width=True)

    if send and question:
        _send_message(client, repo, question)

    # Clear button
    if st.session_state.chat_history:
        if st.button("🗑️  Clear chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


def _send_message(client, repo: str, question: str):
    owner, repo_name = repo.split("/", 1)

    st.session_state.chat_history.append({"role": "user", "content": question})

    with st.spinner("Thinking..."):
        try:
            resp = client.ask_repo(
                owner, repo_name,
                question,
                st.session_state.chat_history[:-1],  # history without current msg
            )
            answer = resp.get("answer", "No answer returned.")
            sources = resp.get("sources", [])

            if sources:
                src_md = "\n\n📁 **Sources:** " + " · ".join(f"`{s}`" for s in sources[:5])
                answer += src_md

            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ Backend error: {e}"
            })
            st.rerun()
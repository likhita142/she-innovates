import streamlit as st

from api_client import generate_story

st.set_page_config(

page_title="RepoStory AI",

layout="wide"

)

st.title("📘 RepoStory AI")

repo = st.text_input(

"Enter repo owner/repo",

placeholder="facebook/react"

)


if st.button("Generate Story"):

    if repo:

        with st.spinner("Talking to AI..."):

            result = generate_story(repo)

        col1,col2 = st.columns(2)

        with col1:

            st.subheader("Story Mode")

            st.write(result["story"])

        with col2:

            st.subheader("TLDR")

            st.write(result["tldr"])
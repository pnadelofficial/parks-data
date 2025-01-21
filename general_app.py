import streamlit as st
import pandas as pd
import general_utils as gu
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from whoosh import query
import os

st.title("Search Engine Creator")

# query tips
                                                  

upload_expander = st.expander("Upload your data", expanded=True)
collection = None

with upload_expander:
    uploaded_file = st.file_uploader("Choose a CSV file")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        collection = st.text_input("Collection name")
        text = st.selectbox("Select text column", data.columns)

        if collection and text:
            if st.button("Create index"):
                with st.spinner("Creating index..."):
                    si = gu.SearchIndexer(data, text, *[c for c in data.columns if c not in [text]], name=collection)
                st.write("Index created!")

if collection and os.path.exists(collection):    
    with st.expander("Search your data"):
        if 'page_count' not in st.session_state:
            st.session_state['page_count'] = 0

        if 'to_see' not in st.session_state:
            st.session_state['to_see'] = 10

        if 'pages' not in st.session_state:
            st.session_state['pages'] = []

        ix = open_dir(collection)
        query_str = st.text_input("Search")
        stemmer = st.toggle('Use stemming', help='If selected, the search will use stemming to find words with the same root. For example, "running" will match "run" and "ran".', on_change=gu.clear_session_state)

        if stemmer:
            parser = QueryParser("text", ix.schema, termclass=query.Variations)
        else:
            parser = QueryParser("text", ix.schema)

        if query_str:
            upload_expander.expanded = False
            st.session_state['pages'] = []
            with ix.searcher() as searcher:
                with st.spinner("Searching..."):
                    res = searcher.search(parser.parse(query_str), limit=None)
                    res.fragmenter.maxchars = 1000
                    res.fragmenter.surround = 250
                    pages = (len(res) // st.session_state['to_see']) + 1
                    for i in range(1, pages):
                        page = res[i*st.session_state['to_see']-st.session_state['to_see']:i*st.session_state['to_see']]
                        p = gu.Page(page, i, st.session_state['to_see'])
                        st.session_state['pages'].append(p)
                
                with st.sidebar:
                    st.markdown("# Page Navigation")
                    if st.button('See next page', key='next'):
                        st.session_state['page_count'] += 1
                    if st.button('See previous page', key='prev'):
                        st.session_state['page_count'] -= 1
                    page_swap = st.number_input('What page do you want to visit?', min_value=1, max_value=len(st.session_state['pages']), value=1)
                    if st.button('Go to page'):
                        st.session_state['page_count'] = page_swap-1
                
                st.write(f"Page {st.session_state['page_count']+1} of {pages}")
                if st.session_state['page_count'] < len(st.session_state['pages']):
                    selected_page = st.session_state['pages'][st.session_state['page_count']]
                    selected_page()
                elif st.session_state['page_count'] < 1:
                    st.session_state['page_count'] = 0
                else:
                    st.write("No more pages!")
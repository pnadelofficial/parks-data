import streamlit as st
import utils
from whoosh import query
from whoosh.qparser import QueryParser

st.title("Rosa Parks Papers Search Engine")

ix = utils.get_index()

if 'page_count' not in st.session_state:
    st.session_state['page_count'] = 0

if 'to_see' not in st.session_state:
    st.session_state['to_see'] = 10

if 'pages' not in st.session_state:
    st.session_state['pages'] = []

query_str = st.text_input("Search", key="search", on_change=utils.clear_session_state)
stemmer = st.toggle('Use stemming', help='If selected, the search will use stemming to find words with the same root. For example, "running" will match "run" and "ran".', on_change=utils.clear_session_state)

if stemmer:
    parser = QueryParser("transcription", ix.schema, termclass=query.Variations)
else:
    parser = QueryParser("transcription", ix.schema)
q = parser.parse(query_str)

if query_str:
    st.session_state['pages'] = []
    with ix.searcher() as searcher:
        with st.spinner("Searching..."):
            res = searcher.search(q, limit=None)
            res.fragmenter.maxchars = 1000
            res.fragmenter.surround = 250
            pages = (len(res) // st.session_state['to_see']) + 1
            print(res)
            for i in range(1, pages):
                page = res[i*st.session_state['to_see']-st.session_state['to_see']:i*st.session_state['to_see']]
                p = utils.Page(page, i, st.session_state['to_see'])
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
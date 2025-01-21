import streamlit as st
from whoosh.index import open_dir
import re

@st.cache_data
def get_index():
    return open_dir("parks_index")

def clear_session_state():
    st.session_state['page_count'] = 0
    st.session_state['to_see'] = 10
    st.session_state['pages'] = []

class Page:
    def __init__(self, results, pageno, items_per_page):
        self.results = results
        self.pageno = pageno
        self.items_per_page = items_per_page

    def __len__(self):
        return len(self.results)

    def __call__(self):
        for i, hit in enumerate(self.results):
            st.write(f"<small>Document {i+1} of {len(self.results)}</small>", unsafe_allow_html=True)
            st.write(f"<h4>{hit['item']}</h4>", unsafe_allow_html=True)
            r = re.split('\w\.\.\.\w', hit.highlights("transcription").replace("\n\n", ""))
            for h in r:
                st.write(h, unsafe_allow_html=True)
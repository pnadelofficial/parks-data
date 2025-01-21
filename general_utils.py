import streamlit as st
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import index
from whoosh.index import open_dir
import os
import pandas as pd
from typing import List
import re

def clear_session_state():
    st.session_state['page_count'] = 0
    st.session_state['to_see'] = 10
    st.session_state['pages'] = []

class SearchIndexer:
    def __init__(self, df:pd.DataFrame, text_col:str, *args:List[str], name='indexdir'):
        self.df = df
        self.args = args
        self.text_col = text_col 
        self.name = name  

        self.schema = Schema(
            id=ID(stored=True),
            **{arg: STORED() for arg in args},
            text=TEXT(analyzer=StemmingAnalyzer(), stored=True)
        )

        if os.path.exists(self.name):
            self.ix = open_dir(self.name)
        else:
            os.makedirs(self.name)
            self.ix = index.create_in(self.name, self.schema)
        self.writer = self.ix.writer()

        self.create_index()
    
    def create_index(self):
        for i, row in self.df.iterrows():
            row = row.fillna("")
            self.writer.add_document(
                id=str(i), 
                **{arg: row[arg] for arg in self.args},
                text=row[self.text_col]
            )
        self.writer.commit()

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
            stored_fields = [k for k in hit.keys() if k != 'text']
            for f in stored_fields:
                st.write(f"<b>{f}</b>: {hit[f]}", unsafe_allow_html=True)
            r = re.split('\w\.\.\.\w', hit.highlights("text").replace("\n\n", ""))
            st.write("<b><u>Relevant Text:</u></b>", unsafe_allow_html=True)
            for h in r:
                st.write(f'<pre style="white-space: pre-wrap;">{h}</pre>', unsafe_allow_html=True)
            st.write("<hr>", unsafe_allow_html=True)
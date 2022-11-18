import streamlit as st

def markdown_not_bold_and_bold_text_to_html(not_bold_text, bold_text, color='Blue'):
    st.markdown(
        f"<p style='color:{color}; text-align: input {{unicode-bidi:bidi-override; direction: LTR;}} "
        f" direction: LTR; '>{not_bold_text} <span style=  font-weight:bold;>{bold_text} </span></p>",
        unsafe_allow_html=True)


def markdown_bold_text_to_html(bold_text, color='Blue'):
    st.markdown(
        f"<p style='color:{color}; text-align: input {{unicode-bidi:bidi-override; direction: LTR;}} "
        f" direction: LTR; '>{bold_text} </p>",
        unsafe_allow_html=True)


def markdown_not_bold_text_to_html(bold_text, color='Blue'):
    st.markdown(
        f"<p style='color:{color};  text-align: input {{unicode-bidi:bidi-override; direction: LTR;}} "
        f" direction: LTR; '>{bold_text} </p>",
        unsafe_allow_html=True)

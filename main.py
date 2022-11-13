import docx
import pandas as pd
import streamlit as st
import os
from manage_txt import TxtManager, TxtDirManager



def run(txt_dir, labels):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = TxtDirManager(txt_dir)

    if "files" not in st.session_state:
        st.session_state["df"] = idm.get_df()
        st.session_state["files"] = st.session_state["df"]['title'].tolist()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["file_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])
        idm.set_annotation_files(st.session_state["annotation_files"])

    def refresh():
        st.session_state["df"] = idm.get_df()
        st.session_state["files"] = st.session_state["df"]['title'].tolist()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["file_index"] = 0




    def next_image():
        file_index = st.session_state["file_index"]
        if file_index < len(st.session_state["files"]) - 1:
            st.session_state["file_index"] += 1
        else:
            st.warning('This is the last image.')

    def previous_image():
        file_index = st.session_state["file_index"]
        if file_index > 0:
            st.session_state["file_index"] -= 1
        else:
            st.warning('This is the first image.')

    def next_annotate_file():
        file_index = st.session_state["file_index"]
        next_file_index = idm.get_next_annotation_txt(file_index)
        if next_file_index:
            st.session_state["file_index"] = idm.get_next_annotation_txt(file_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    # def annotate():
    #     # im.save_annotation()
    #     image_annotate_file_name = txt_file_name.split(".")[0] + ".xml"
    #     if image_annotate_file_name not in st.session_state["annotation_files"]:
    #         st.session_state["annotation_files"].append(image_annotate_file_name)
    #     next_annotate_file()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["file_index"] = file_index

    def find_sentence_in_file(file_path, sentence):
        doc = docx.Document(file_path)
        # create a list of all the text in  paragraphs
        paragraphs = [p.text for p in doc.paragraphs]
        # check if any of the paragraphs contain the sentence
        if any(sentence in p for p in paragraphs):
            st.session_state["sentence"] = sentence
            return paragraphs
        return None

    def read_file():
        # loop over the df
        df = st.session_state["df"]
        row = df.iloc[st.session_state["file_index"]]
        sentence = row['origin_sentence']
        file_name = row['title'] + ".docx"
        # read the file
        file_path = os.path.join(r'sentencing_decisions', file_name)
        if os.path.exists(file_path):
            return find_sentence_in_file(file_path, sentence)
        return None

    def get_sentence_from_file(paragraphs):
        sentence = st.session_state["sentence"]
        #split the paragraph into sentences
        sentences = [s for p in paragraphs for s in p.split('.')]
        # remove sentences without any letters
        sentences = [s for s in sentences if any(c.isalpha() for c in s)]
        # find the index of sentence in the list of sentences
        sentence_index = sentences.index(sentence)
        st.session_state["sentence_index"] = sentence_index
        if "start_sentence_index" not in st.session_state:
            st.session_state["start_sentence_index"] = sentence_index
        if "end_sentence_index" not in st.session_state:
            st.session_state["end_sentence_index"] = sentence_index + 1
        st.session_state["sentences"] = sentences

    def display_text():
        st.text('text')
        for i in range(st.session_state["start_sentence_index"], st.session_state["end_sentence_index"]):
            sentence = st.session_state["sentences"][i]

            if i == st.session_state["sentence_index"]:
                st.markdown(
                    f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}} direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> {sentence} </span></p>",
                    unsafe_allow_html=True)
            else:
                    st.markdown(
                        f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}} direction: RTL; color: grey; '>{sentence}</p>",
                        unsafe_allow_html=True)

    # Sidebar: show status
    n_files = len(st.session_state["files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    st.sidebar.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["file_index"],
        on_change=go_to_image,
        key="file",
    )


    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image)
    with col2:
        st.button(label="Next image", on_click=next_image)
    st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
    st.sidebar.button(label="Refresh", on_click=refresh)

    # Main content: annotate images
    paragraphs = read_file()
    if paragraphs:
        get_sentence_from_file(paragraphs)
        col1, col2 = st.columns(2)

        def next_sentence():
            end_sentence_index = st.session_state["end_sentence_index"]
            if end_sentence_index < len(st.session_state["sentences"]) - 1:
                st.session_state["end_sentence_index"] += 1
            else:
                st.warning('This is the last sentence.')

        def previous_sentence():
            start_sentence_index = st.session_state["start_sentence_index"]
            if start_sentence_index > 0:
                st.session_state["start_sentence_index"] -= 1
            else:
                st.warning('This is the first sentence.')

        def remove_first_sentence():
            start_sentence_index = st.session_state["start_sentence_index"]
            if start_sentence_index < st.session_state["sentence_index"]:
                st.session_state["start_sentence_index"] += 1
            else:
                st.warning('This is the first sentence.')

        def remove_last_sentence():
            end_sentence_index = st.session_state["end_sentence_index"]
            if end_sentence_index > st.session_state["sentence_index"]+1:
                st.session_state["end_sentence_index"] -= 1
            else:
                st.warning('This is the last sentence.')

        with col1:
            st.button(label="Add the previous sentence", on_click=previous_sentence)
            st.button(label="Remove the first sentence", on_click=remove_first_sentence)
        with col2:
            st.button(label="Add the next sentence", on_click=next_sentence)
            st.button(label="Remove the last sentence", on_click=remove_last_sentence)


        col1, col2 = st.columns(2)
        with col1:
            display_text()

        with col2:
            default_index = 0
            select_label = col2.selectbox(
                "Label", labels, key=f"label", index=default_index
            )

        # st.button(label="Save", on_click=annotate)


if __name__ == "__main__":
    #list of labels
    labels = ["category{}".format(i) for i in range(1, 11)]

    run("txt_dir", labels)
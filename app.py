import docx
import numpy as np
import pandas as pd
import streamlit as st
import os
from manage_txt import TxtDirManager


def init_session_state(idm):
    chosen_tagger = st.session_state["chosen_tagger"]
    if "files_number" not in st.session_state:

        # read df of the chosen tagger
        tagger_df = pd.read_csv(os.path.join("taggers", f"{chosen_tagger}.csv"))
        # get sentences from the chosen tagger
        st.session_state["df"] = tagger_df
        st.session_state["files_number"] = tagger_df.shape[0]
        st.session_state["annotation_files"] = tagger_df[tagger_df["status"] == "annotated"]["title"].tolist()
        st.session_state["file_index"] = 0
        st.session_state["start_sentence_index"]=-1
        st.session_state["end_sentence_index"]=-1
    else:
        tagger_df = pd.read_csv(os.path.join("taggers", f"{chosen_tagger}.csv"))
        st.session_state["df"] = tagger_df

        # read df of the chosen tagger
        tagger_df = pd.read_csv(os.path.join("taggers", f"{chosen_tagger}.csv"))
        # get sentences from the chosen tagger

        st.session_state["files_number"] = tagger_df.shape[0]
        st.session_state["annotation_files"] = tagger_df[tagger_df["status"] == "annotated"]["title"].tolist()
        # st.session_state["file_index"] = 0
    #     st.session_state["files_number"] = np.arange(len(st.session_state["df"]['title'].tolist()))
    #     # idm.set_all_files(st.session_state["files_number"])
    #     idm.set_annotation_files(st.session_state["annotation_files"])

def run(txt_dir, labels):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = TxtDirManager(txt_dir)

    # Sidebar: show status
    # get names of all the taggers from "taggers" folder
    taggers = [f for f in os.listdir('taggers') if os.path.isfile(os.path.join('taggers', f))]
    # remove the suffix of the files from the list
    taggers = [t.split(".")[0] for t in taggers]
    # get the name of the current tagger. Ask the uset to choose his name from the list
    chosen_tagger = st.sidebar.selectbox(
        "Choose your name",
        taggers,
        key="tagger",
    )
    st.session_state["chosen_tagger"] = chosen_tagger

    init_session_state(idm)

    n_files = st.session_state["files_number"]
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Total sentences:", n_files)
    st.sidebar.write("Total annotate sentences:", n_annotate_files)
    st.sidebar.write("Remaining sentences:", n_files - n_annotate_files)






    def refresh():
        st.session_state["df"] = idm.get_df()
        st.session_state["files_number"] = np.arange(len(st.session_state["df"]['title'].tolist()))
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["file_index"] = 0




    def next_sentence():
        file_index = st.session_state["file_index"]

        if file_index < st.session_state["files_number"] - 1:
            st.session_state["file_index"] += 1
            st.session_state["start_sentence_index"]=-1
            st.session_state["end_sentence_index"]=-1

        else:
            st.warning('This is the last sentence.')
        # print(st.session_state["file_index"])

    def previous_sentence():
        file_index = st.session_state["file_index"]
        if file_index > 0:
            st.session_state["file_index"] -= 1
            st.session_state["start_sentence_index"]=-1
            st.session_state["end_sentence_index"]=-1
        else:
            st.warning('This is the first sentence.')

    def next_annotate_file():
        file_index = st.session_state["file_index"]
        if file_index < st.session_state["files_number"] - 1:
            st.session_state["file_index"] += 1
            st.session_state["start_sentence_index"]=-1
            st.session_state["end_sentence_index"]=-1
        else:
            st.warning("All sentences are annotated.")
            next_sentence()

    def go_to_sentence():
        # split the number of the sentence from the string of st.session_state["sentence_for_tagging"]
        # and then convert it to int
        sentence_number = int(st.session_state["sentence_for_tagging"].split(" ")[1])-1
        st.session_state["file_index"] = sentence_number
        st.session_state["start_sentence_index"] =-1
        st.session_state["end_sentence_index"] =-1

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
        annotate = row['status']
        if annotate == "annotated":
            label= row['label']
            st.session_state["label"] = label
        else:
            st.session_state["label"] = None
        st.session_state['sentence_id'] = row['sentence_id']
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
        if st.session_state["start_sentence_index"] < 0  or st.session_state["end_sentence_index"] <0:
            st.session_state["start_sentence_index"] = sentence_index
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

    st.sidebar.selectbox(
        "Sentences",
        [f"sentence {i}" for i in range(1, n_files + 1)],
        index=st.session_state["file_index"],
        on_change=go_to_sentence,
        key="sentence_for_tagging",
    )
    def annotate():
        idm.save_annotation(st.session_state["selected_label"], st.session_state["tagger"], st.session_state["sentence_id"])
        # if image_annotate_file_name not in st.session_state["annotation_files"]:
        #     st.session_state["annotation_files"].append(image_annotate_file_name)
        next_annotate_file()


    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(label="Previous sentence for tagging", on_click=previous_sentence)
    with col2:
        st.button(label="Next sentence for tagging", on_click=next_sentence)
    # st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
    st.sidebar.button(label="Refresh", on_click=refresh)
    # print("192", st.session_state["file_index"])

    # Main content: annotate sentences
    paragraphs = read_file()
    # print(f"len(paragraphs) = {len(paragraphs)}")
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
            if st.session_state["label"]:
                # there is a saved label for this sentence
                st.session_state["selected_label"] = st.session_state["label"]
                # print a message that the sentence is already annotated
                # st.markdown(
                #     f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}}"
                #     f" direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> This sentence is already annotated </span></p>",
                #     unsafe_allow_html=True)
                title1 = f"This sentence is already annotated. The saved label:"
                title2 = f"{st.session_state['selected_label']}"
                title3 = f"If you want to change the label, select a new label and click on the 'Save' button."
                new_title1 = f'<p style="font-family:sans-serif; color:Green; font-size: 22px;">{title1}</p>'
                new_title2 = f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}} direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> {title2} </span></p>"
                new_title2 = f'<p style="font-family:sans-serif; color:black; ' \
                             f'font-weight:bold;><span style=font-weight:bold;>font-size: 22px;">{title2}</p>'
                new_title3 = f'<p style="font-family:sans-serif; color:Green; font-size: 22px;">{title3}</p>'
                # st.markdown(
                #     f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}}"
                #     f" direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> This sentence is already annotated </span></p>",
                #     unsafe_allow_html=True)
                # st.markdown(
                #     f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}}"
                #     f" direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> This sentence is already annotated </span></p>",
                #     unsafe_allow_html=True)
                 # st.markdown title2 in the middle of the screen
                # print the saved label in the middle of the screen
                # st.markdown(
                #     f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}}"
                #     f" direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> {st.session_state['selected_label']} </span></p>",
                #     unsafe_allow_html=True)


                st.markdown(new_title1, unsafe_allow_html=True)
                st.markdown(new_title2, unsafe_allow_html=True)
                st.markdown(new_title3, unsafe_allow_html=True)
            default_index = 0

            selected_label = col2.selectbox(
                "Label", labels, key=f"selectedLabel",
                index=default_index
            )
            st.session_state["selected_label"] = selected_label
            # print to the screen the selected label
            st.markdown(
                f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}}"
                f" direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> {selected_label} </span></p>",
                unsafe_allow_html=True)

        # st.button(label="Save", on_click=annotate)
        # put save button in the middle of the page
        col1, col2, col3 = st.columns(3)
        with col2:

            st.button(label="Save", on_click=annotate)


if __name__ == "__main__":
    #list of labels
    labels = ["category{}".format(i) for i in range(1, 11)]

    run("txt_dir", labels)
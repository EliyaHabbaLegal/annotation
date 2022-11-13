import streamlit as st
import os
# from streamlit_txt_label import st_txt_label
from manage_txt import TxtManager,TxtDirManager



def run(txt_dir, labels):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = TxtDirManager(txt_dir)

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])
        idm.set_annotation_files(st.session_state["annotation_files"])

    def refresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0


    def next_sentence():
        end_sentence_index = st.session_state["end_sentence_index"]
        if end_sentence_index < len(st.session_state["num_sentences"]) - 1:
            st.session_state["end_sentence_index"] += 1
        else:
            st.warning('This is the last sentence.')

    def previous_sentence():
        start_sentence_index = st.session_state["start_sentence_index"]
        if start_sentence_index > 0:
            st.session_state["start_sentence_index"] -= 1
        else:
            st.warning('This is the first sentence.')

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning('This is the last image.')

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning('This is the first image.')

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_txt(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_txt(image_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    def annotate():
        # im.save_annotation()
        image_annotate_file_name = txt_file_name.split(".")[0] + ".xml"
        if image_annotate_file_name not in st.session_state["annotation_files"]:
            st.session_state["annotation_files"].append(image_annotate_file_name)
        next_annotate_file()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index

    # Sidebar: show status
    n_files = len(st.session_state["files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    st.sidebar.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
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
    txt_file_name = idm.get_image(st.session_state["image_index"])
    txt_path = os.path.join(txt_dir, txt_file_name)
    txt_manager = TxtManager(txt_path)
    txt = txt_manager.get_docx_file()



    col1, col2 = st.columns(2)
    with col1:
        st.button(label="Add the previous sentence", on_click=previous_sentence)
    with col2:
        st.button(label="Add the next sentence", on_click=next_sentence)


    col1, col2 = st.columns(2)
    with col1:
        for t in txt:
            st.markdown(
                f"<p style='text-align: input {{unicode-bidi:bidi-override; direction: RTL;}} direction: RTL; color: grey; 'font-weight:bold;><span style=font-weight:bold;> {t} </span></p>",
                unsafe_allow_html=True)

    with col2:
        default_index = 0
        select_label = col2.selectbox(
            "Label", labels, key=f"label", index=default_index
        )

    st.button(label="Save", on_click=annotate)


if __name__ == "__main__":
    custom_labels = ["", "dog", "cat"]
    run("txt_dir", custom_labels)
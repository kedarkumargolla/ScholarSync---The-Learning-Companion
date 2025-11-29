# app.py

import streamlit as st
import os
import tempfile
import zipfile
from rag_core import (
    load_and_split_documents,
    index_documents,
    ingest_files,
    query_rag,
    clear_database,
)

st.set_page_config(page_title="ScholarSync - The Learning Companion", layout="wide")
st.title("ScholarSync - The Learning Companion")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Knowledge Base")
    # Ensure knowledge base directory exists
    KB_DIR = "knowledge_base"
    if not os.path.exists(KB_DIR):
        os.makedirs(KB_DIR)
    # Ensure Others folder exists
    OTHERS_DIR = os.path.join(KB_DIR, "Others")
    if not os.path.exists(OTHERS_DIR):
        os.makedirs(OTHERS_DIR)

    # Folder actions (create / delete)
    with st.expander("Folder Actions"):
        action = st.radio("Action", ["Create Subfolder", "Delete Folder"])
        # Gather existing folders
        all_folders = ["/"]
        for root, dirs, _ in os.walk(KB_DIR):
            for d in dirs:
                rel_path = os.path.relpath(os.path.join(root, d), KB_DIR)
                all_folders.append(rel_path)
        if action == "Create Subfolder":
            parent_folder = st.selectbox("Select Parent Folder", all_folders, key="create_parent")
            new_folder_name = st.text_input("New Folder Name")
            if st.button("Create Folder"):
                if new_folder_name:
                    target_base = KB_DIR if parent_folder == "/" else os.path.join(KB_DIR, parent_folder)
                    folder_path = os.path.join(target_base, new_folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        st.success(f"Created: {new_folder_name}")
                        st.rerun()
                    else:
                        st.warning("Folder already exists.")
        else:  # Delete Folder
            folder_to_delete = st.selectbox("Select Folder to Delete", [f for f in all_folders if f != "/"], key="delete_target")
            if st.button("Delete Folder", type="primary"):
                if folder_to_delete:
                    folder_path = os.path.join(KB_DIR, folder_to_delete)
                    try:
                        import shutil
                        shutil.rmtree(folder_path)
                        st.success(f"Deleted: {folder_to_delete}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting folder: {e}")

    st.subheader("Explorer")
    def display_tree(startpath):
        try:
            items = sorted(os.listdir(startpath))
            dirs = [d for d in items if os.path.isdir(os.path.join(startpath, d))]
            files = [f for f in items if os.path.isfile(os.path.join(startpath, f))]
            for d in dirs:
                dir_path = os.path.join(startpath, d)
                with st.expander(f"📁 {d}", expanded=False):
                    display_tree(dir_path)
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                icon = (
                    "🖼️" if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                    else "📕" if ext == ".pdf"
                    else "📊" if ext in [".xlsx", ".csv"]
                    else "📝" if ext == ".docx"
                    else "📊" if ext in [".pptx", ".ppt"]
                    else "📄"
                )
                st.markdown(f"{icon} {f}")
            if not dirs and not files:
                st.caption("Empty folder")
        except Exception as e:
            st.error(f"Error reading directory: {e}")
    display_tree(KB_DIR)
    st.divider()

    # ---------- Folder selector ----------
    folder_options = []
    def add_folders_recursive(parent_path, level=0):
        try:
            items = sorted(os.listdir(parent_path))
            dirs = [d for d in items if os.path.isdir(os.path.join(parent_path, d))]
            for d in dirs:
                full_path = os.path.join(parent_path, d)
                rel_path = os.path.relpath(full_path, KB_DIR)
                prefix = "— " * level
                label = f"{prefix}📁 {d}"
                folder_options.append((label, rel_path))
                add_folders_recursive(full_path, level + 1)
        except Exception:
            pass
    add_folders_recursive(KB_DIR)
    if not folder_options:
        folder_options = [("📁 Others", "Others")]
    default_index = 0
    for i, (lbl, val) in enumerate(folder_options):
        if val == "Others":
            default_index = i
            break
    selected_opt = st.selectbox(
        "Select Target Folder for Upload",
        folder_options,
        format_func=lambda x: x[0],
        index=default_index,
    )
    selected_folder = selected_opt[1]
    st.divider()

    # ---------- Reset Everything button ----------
    st.header("⚙️ System Settings")
    st.warning(
        """
        ### ⚠️ Danger Zone
        The button below will **permanently delete**:
        - All uploaded files in `knowledge_base/`
        - All vector embeddings in `chroma_db/`
        - All folder structures you created
        **This action cannot be undone!**
        """
    )
    confirm_reset = st.checkbox("I understand this will delete ALL data permanently")
    if st.button("🗑️ Reset Everything (Delete All Files & Database)", type="secondary", disabled=not confirm_reset):
        try:
            import shutil
            # Delete vector store
            if os.path.exists("chroma_db"):
                shutil.rmtree("chroma_db")
                st.success("✅ Vector database deleted")
            # Delete knowledge base
            if os.path.exists(KB_DIR):
                shutil.rmtree(KB_DIR)
                st.success("✅ Knowledge base files deleted")
            # Recreate empty structure
            os.makedirs(KB_DIR, exist_ok=True)
            os.makedirs(OTHERS_DIR, exist_ok=True)
            st.success("✅ Fresh folders created")
            st.info("🔄 Please refresh the page to see the changes.")
        except Exception as e:
            st.error(f"❌ Error during reset: {e}")

# ---------- Main Tabs ----------
tab1, tab2 = st.tabs(["Manage Knowledge Base", "Chat with Knowledge Base"])

# Helper to save uploaded files
def save_uploaded_file(uploaded_file, target_folder=None):
    try:
        if target_folder:
            folder_path = os.path.join(KB_DIR, target_folder)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, uploaded_file.name)
        else:
            # Temporary file for quick upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                return tmp_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file {uploaded_file.name}: {e}")
        return None

# ---------- Tab 1: Upload ----------
with tab1:
    st.header("Upload to Knowledge Base")
    st.info(f"Target Folder: **{selected_folder}** (Change in Sidebar)")
    upload_mode = st.radio("Upload Mode", ["Single File Upload", "Batch File Upload"])
    if upload_mode == "Single File Upload":
        uploaded_files = st.file_uploader(
            "Choose a file",
            accept_multiple_files=False,
            type=["pdf", "docx", "pptx", "ppt", "xlsx", "csv", "jpg", "jpeg", "png", "gif", "webp"],
        )
        if uploaded_files:
            uploaded_files = [uploaded_files]
    else:
        st.info("To upload a folder structure, compress it into a ZIP file and upload it here. To upload multiple individual files, select them all.")
        uploaded_files = st.file_uploader(
            "Choose files (Batch/ZIP Upload)",
            accept_multiple_files=True,
            type=["pdf", "docx", "pptx", "ppt", "xlsx", "csv", "jpg", "jpeg", "png", "gif", "webp", "zip"],
        )
    st.divider()
    st.warning(f"⚠️ Verify Target Folder: Files will be saved to `{selected_folder}`. Change it in the sidebar if needed before processing.")
    if st.button("Process Files", type="primary"):
        if uploaded_files:
            progress_bar = st.progress(0)
            status_text = st.empty()
            file_paths = []
            # Save / extract files
            with st.spinner("Saving and extracting files..."):
                for uploaded_file in uploaded_files:
                    if uploaded_file.name.lower().endswith(".zip"):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
                                tmp_zip.write(uploaded_file.getvalue())
                                tmp_zip_path = tmp_zip.name
                            target_extract_path = os.path.join(KB_DIR, selected_folder)
                            with zipfile.ZipFile(tmp_zip_path, "r") as zip_ref:
                                zip_ref.extractall(target_extract_path)
                            os.remove(tmp_zip_path)
                            for root, _, files in os.walk(target_extract_path):
                                for f in files:
                                    file_paths.append(os.path.join(root, f))
                        except Exception as e:
                            st.error(f"Error extracting {uploaded_file.name}: {e}")
                    else:
                        path = save_uploaded_file(uploaded_file, selected_folder)
                        if path:
                            file_paths.append(path)
            if file_paths:
                file_paths = list(set(file_paths))
                def update_progress(current, total, filename):
                    progress = int((current / total) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing file {current+1}/{total}: {filename}")
                result = load_and_split_documents(file_paths, progress_callback=update_progress)
                if result["status"] == "success":
                    status_text.text("Indexing documents into vector store...")
                    with st.spinner("Indexing..."):
                        index_documents(result["splits"])
                    progress_bar.progress(100)
                    status_text.text("Done!")
                    success_msg = f"Successfully processed {len(file_paths) - len(result['failed']) - len(result['ignored'])} files."
                    if result["ignored"]:
                        success_msg += f" Ignored: {', '.join(result['ignored'])}."
                    st.success(success_msg)
                    if result["failed"]:
                        st.error("Failed Files:")
                        for fail in result["failed"]:
                            st.write(f"- {fail}")
                    st.rerun()
                else:
                    st.error(result["message"])
        else:
            st.warning("Please upload files first.")

# ---------- Tab 2: Chat ----------
with tab2:
    st.header("Chat")
    st.subheader("Quick Upload (Single File)")
    quick_file = st.file_uploader(
        "Upload a file to add to context",
        type=["pdf", "docx", "pptx", "xlsx", "csv", "jpg", "jpeg", "png", "gif", "webp"],
        key="quick_upload",
    )
    if quick_file:
        if st.button("Add to Context"):
            with st.spinner("Adding file..."):
                path = save_uploaded_file(quick_file)
                if path:
                    result = ingest_files([path])
                    st.success(result)
                    os.remove(path)
    st.divider()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer, source_docs = query_rag(prompt)
                    st.markdown(answer)
                    with st.expander("📚 Source Documents"):
                        for i, doc in enumerate(source_docs):
                            doc_type = doc.metadata.get('type', 'document')
                            source_file = doc.metadata.get('source', 'Unknown')
                            st.markdown(f"**Source {i+1}:** {os.path.basename(source_file)}")
                            if doc_type == 'image' and os.path.exists(source_file):
                                try:
                                    st.image(source_file, caption=os.path.basename(source_file), width=300)
                                except:
                                    pass
                            st.markdown(f"**Type:** {doc_type}")
                            st.markdown(f"**Content:** {doc.page_content[:300]}...")
                            st.divider()
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"An error occurred: {e}")

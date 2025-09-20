import streamlit as st
import pandas as pd
from fishki import data_store
from fishki.ui import set_toast, toast_notifications

st.set_page_config(page_title="Saved Words", page_icon="💾", layout="wide")

# Initialize data from CSV files into session state
if 'decks_df' not in st.session_state or 'cards_df' not in st.session_state or 'saved_words_df' not in st.session_state:
    st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df = data_store.load_data()

st.header("💾 Saved Words")

# Load data from session state
saved_words_df = st.session_state.saved_words_df
toast_notifications()

# Add new word form
with st.expander("➕ Add New Word", expanded=False):
    with st.form("add_word_form"):
        col1, col2 = st.columns(2)
        with col1:
            german = st.text_input("German Word/Phrase", placeholder="e.g., das Haus")
        with col2:
            english = st.text_input("English Translation", placeholder="e.g., the house")
        
        context = st.text_area("Context/Example", placeholder="e.g., Ich wohne in einem großen Haus.")
        notes = st.text_area("Personal Notes", placeholder="Any additional notes...")
        source = st.selectbox("Source", ["Manual", "Learn", "Review", "Quiz", "Other"])
        
        if st.form_submit_button("Save Word", type="primary"):
            if german and english:
                word_data = {
                    "german": german,
                    "english": english,
                    "context": context,
                    "notes": notes,
                    "source": source
                }
                st.session_state.saved_words_df = data_store.add_saved_word(saved_words_df, word_data)
                data_store.save_data(st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df)
                set_toast(f"Word '{german}' saved successfully!")
                st.rerun()
            else:
                st.error("German and English fields are required.")

# Filter options
col1, col2, col3 = st.columns(3)
with col1:
    show_reviewed = st.selectbox("Show", ["All", "Not Reviewed", "Reviewed Only"])
with col2:
    source_filter = st.selectbox("Source", ["All"] + list(saved_words_df["source"].unique()) if not saved_words_df.empty else ["All"])
with col3:
    sort_by = st.selectbox("Sort by", ["Date Added (Newest)", "Date Added (Oldest)", "German A-Z", "German Z-A"])

# Filter the data
filtered_df = saved_words_df.copy()

if show_reviewed == "Not Reviewed":
    filtered_df = filtered_df[filtered_df["reviewed"] == False]
elif show_reviewed == "Reviewed Only":
    filtered_df = filtered_df[filtered_df["reviewed"] == True]

if source_filter != "All":
    filtered_df = filtered_df[filtered_df["source"] == source_filter]

# Sort the data
if sort_by == "Date Added (Newest)":
    filtered_df = filtered_df.sort_values("created_at", ascending=False)
elif sort_by == "Date Added (Oldest)":
    filtered_df = filtered_df.sort_values("created_at", ascending=True)
elif sort_by == "German A-Z":
    filtered_df = filtered_df.sort_values("german", ascending=True)
elif sort_by == "German Z-A":
    filtered_df = filtered_df.sort_values("german", ascending=False)

# Display saved words
if not filtered_df.empty:
    st.subheader(f"📚 {len(filtered_df)} Saved Words")
    
    # Bulk actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Mark All as Reviewed", help="Mark all displayed words as reviewed"):
            for word_id in filtered_df["id"]:
                st.session_state.saved_words_df = data_store.mark_word_reviewed(st.session_state.saved_words_df, word_id)
            data_store.save_data(st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df)
            set_toast("All words marked as reviewed!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Delete All Displayed", type="secondary", help="Delete all currently displayed words"):
            for word_id in filtered_df["id"]:
                st.session_state.saved_words_df = data_store.delete_saved_word(st.session_state.saved_words_df, word_id)
            data_store.save_data(st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df)
            set_toast("All displayed words deleted!")
            st.rerun()
    
    with col3:
        if st.button("📤 Export to CSV", help="Download current view as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"saved_words_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Display words in a nice format
    for idx, word in filtered_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                # Main content
                st.markdown(f"**{word['german']}** → {word['english']}")
                if word['context']:
                    st.caption(f"Context: {word['context']}")
                if word['notes']:
                    st.caption(f"Notes: {word['notes']}")
                
                # Metadata
                metadata = f"Source: {word['source']} | Added: {pd.to_datetime(word['created_at']).strftime('%Y-%m-%d %H:%M')}"
                if word['reviewed']:
                    metadata += " | ✅ Reviewed"
                st.caption(metadata)
            
            with col2:
                if not word['reviewed']:
                    if st.button("✅", key=f"review_{word['id']}", help="Mark as reviewed"):
                        st.session_state.saved_words_df = data_store.mark_word_reviewed(st.session_state.saved_words_df, word['id'])
                        data_store.save_data(st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df)
                        set_toast(f"'{word['german']}' marked as reviewed!")
                        st.rerun()
                else:
                    if st.button("↩️", key=f"unreview_{word['id']}", help="Mark as not reviewed"):
                        st.session_state.saved_words_df = data_store.update_saved_word(st.session_state.saved_words_df, word['id'], {"reviewed": False})
                        data_store.save_data(st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df)
                        set_toast(f"'{word['german']}' marked as not reviewed!")
                        st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{word['id']}", help="Delete word"):
                    st.session_state.saved_words_df = data_store.delete_saved_word(st.session_state.saved_words_df, word['id'])
                    data_store.save_data(st.session_state.decks_df, st.session_state.cards_df, st.session_state.saved_words_df)
                    set_toast(f"'{word['german']}' deleted!")
                    st.rerun()
            
            st.divider()

else:
    st.info("No saved words found. Add some words using the form above or save words from other pages!")

# Statistics
if not saved_words_df.empty:
    st.subheader("📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_words = len(saved_words_df)
    reviewed_words = len(saved_words_df[saved_words_df["reviewed"] == True])
    not_reviewed_words = total_words - reviewed_words
    
    with col1:
        st.metric("Total Words", total_words)
    with col2:
        st.metric("Reviewed", reviewed_words)
    with col3:
        st.metric("Not Reviewed", not_reviewed_words)
    with col4:
        if total_words > 0:
            review_percentage = (reviewed_words / total_words) * 100
            st.metric("Review Progress", f"{review_percentage:.1f}%")
        else:
            st.metric("Review Progress", "0%")

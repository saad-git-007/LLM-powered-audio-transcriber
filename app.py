import streamlit as st
from openai import OpenAI
import pydub
import io
import math
import time
import os
from streamlit.errors import StreamlitAPIException, StreamlitSecretNotFoundError

# --- Configuration ---
st.set_page_config(
    page_title="🎙️ Audio Transcriber",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---

def get_openai_client():
    """Initializes OpenAI client using Streamlit secrets."""
    try:
        # Attempt to get the key from secrets (e.g., secrets.toml or HF secrets)
        api_key = st.secrets["OPENAI_API_KEY"]
        # If successful, return the client and indicate key was found via secrets
        return OpenAI(api_key=api_key), True

    # --- MODIFIED EXCEPTION HANDLING ---
    # Explicitly catch the StreamlitSecretNotFoundError first
    except StreamlitSecretNotFoundError:
        st.sidebar.warning("🔑 OpenAI API Key not found in secrets.")
        # Display the text input box in the sidebar
        api_key_input = st.sidebar.text_input(
            "Enter OpenAI API Key (local testing only):",
            type="password",
            help="Add your key to Streamlit secrets (secrets.toml or HF Space secrets) for deployed apps."
        )
        # Check if the user actually entered something into the box
        if api_key_input:
             st.sidebar.success("✅ API Key entered locally.")
             # If they entered a key, create client with it and indicate key provided
             return OpenAI(api_key=api_key_input), True
        else:
             # If secrets failed AND they didn't enter anything, indicate no key
             return None, False
    # --- END OF MODIFIED BLOCK ---

    # Keep the general exception handler for other unexpected issues during init
    except Exception as e:
        st.sidebar.error(f"Unexpected error initializing OpenAI client: {e}")
        return None, False


def convert_and_chunk_audio(audio_file, chunk_length_min=10):
    """
    Loads audio, converts to WAV in memory, and splits into chunks.
    Returns a list of BytesIO objects, each containing a WAV chunk.
    """
    chunks = []
    try:
        st.info(f"Loading and processing uploaded file: {audio_file.name}...")
        # Load audio using pydub - attempts to handle various formats
        audio = pydub.AudioSegment.from_file(audio_file)

        chunk_length_ms = chunk_length_min * 60 * 1000
        num_chunks = math.ceil(len(audio) / chunk_length_ms)
        st.info(f"Audio duration: {len(audio) / 1000:.2f}s. Splitting into {num_chunks} chunk(s) of max {chunk_length_min} mins.")

        for i in range(num_chunks):
            start_ms = i * chunk_length_ms
            end_ms = start_ms + chunk_length_ms
            chunk = audio[start_ms:end_ms]

            # Export chunk to WAV format in memory
            buffer = io.BytesIO()
            chunk.export(buffer, format="wav") # WAV is generally well-supported
            buffer.seek(0) # Reset buffer position to the beginning
            chunks.append(buffer)
            st.info(f"   - Created chunk {i+1}/{num_chunks}")
            time.sleep(0.1) # Small delay for visual feedback

        return chunks, None
    except pydub.exceptions.CouldntDecodeError:
        error_msg = "Error: Could not decode audio file. Please ensure it's a valid audio format (MP3, WAV, M4A, OGG, etc.)."
        st.error(error_msg)
        return [], error_msg
    except Exception as e:
        error_msg = f"Error during audio processing: {e}"
        st.error(error_msg)
        return [], error_msg

def transcribe_chunk(client, audio_chunk_buffer, chunk_index):
    """Transcribes a single audio chunk using OpenAI API."""
    try:
        # Pass the buffer directly. Provide a filename tuple.
        # Use .name attribute if available, otherwise provide a generic name.
        filename = f"chunk_{chunk_index}.wav"
        audio_chunk_buffer.name = filename # Ensure the buffer has a name attribute for the API

        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_chunk_buffer, # Pass the BytesIO object directly
            language="en" # Specify English
            # response_format="text" # Optional: get plain text directly
        )
        return transcript.text, None
    except Exception as e:
        error_msg = f"Error transcribing chunk {chunk_index}: {e}"
        st.warning(error_msg) # Use warning for chunk errors, allow proceeding
        return None, error_msg

# --- Streamlit UI ---

st.title("🎙️ LLM Powered Audio to Text Convertor")
st.markdown("Upload an **English** audio file, and this app will transcribe it using OpenAI's `gpt-4o-mini-transcribe` model")
st.markdown("Large files will be automatically split into chunks for processing.")
st.divider()

# Initialize OpenAI client (handles API key via secrets or sidebar fallback)
client, key_provided = get_openai_client() # This function now handles the logic and sidebar warnings

# File Uploader
allowed_types = ['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'amr', 'mpga', 'mpeg', 'webm']
uploaded_file = st.file_uploader(
    "Choose an audio file...",
    type=allowed_types,
    help="Supports various formats like MP3, WAV, M4A, etc."
)

# --- Logic Handling File Upload and Transcription Button ---

if uploaded_file is not None:
    st.subheader("🔊 Uploaded Audio")
    st.write(f"Filename: `{uploaded_file.name}` | Type: `{uploaded_file.type}` | Size: `{uploaded_file.size / (1024*1024):.2f} MB`")
    try:
        # Display audio player
        st.audio(uploaded_file)
    except Exception as e:
        st.warning(f"Could not display audio player. Error: {e}")

    st.divider()

    # --- Only show/enable the button if the API key was provided ---
    if key_provided:
        if st.button("✨ Transcribe Audio", type="primary"):
            start_process_time = time.time()

            # 1. Process Audio (Convert & Chunk)
            # Use a placeholder to show status messages related to chunking
            processing_placeholder = st.empty()
            with processing_placeholder.container():
                audio_chunks, error = convert_and_chunk_audio(uploaded_file, chunk_length_min=10) # 10 min chunks

            if error:
                st.error(f"Failed to process audio: {error}")
                processing_placeholder.empty() # Clear processing messages on error
            elif not audio_chunks:
                 st.warning("No audio chunks were generated. Cannot proceed.")
                 processing_placeholder.empty() # Clear processing messages
            else:
                processing_placeholder.empty() # Clear processing messages before transcription
                num_chunks = len(audio_chunks)
                st.info(f"Starting transcription for {num_chunks} chunk(s)...")

                # Progress Bar & Placeholder for results
                progress_bar = st.progress(0, text="Initializing transcription...")
                results_placeholder = st.empty()
                full_transcript = []
                errors_encountered = []

                # 2. Transcribe Chunks
                for i, chunk_buffer in enumerate(audio_chunks):
                    chunk_num = i + 1
                    progress_text = f"Transcribing chunk {chunk_num}/{num_chunks}..."
                    # Update progress bar *before* starting the transcription for responsiveness
                    progress_bar.progress(i / num_chunks, text=progress_text)

                    # Use spinner for the actual API call duration
                    with st.spinner(progress_text):
                         transcript_text, chunk_error = transcribe_chunk(client, chunk_buffer, chunk_num)

                    if chunk_error:
                        errors_encountered.append(chunk_error)
                        full_transcript.append(f"[ERROR in chunk {chunk_num}]") # Placeholder in transcript
                    elif transcript_text is not None: # Check if text is not None
                        full_transcript.append(transcript_text)
                    else:
                         full_transcript.append(f"[EMPTY RESULT in chunk {chunk_num}]") # Handle None case

                    # Update progress bar after completion of the chunk
                    progress_bar.progress((i + 1) / num_chunks, text=f"Chunk {chunk_num}/{num_chunks} completed.")
                    # Remove the small sleep, spinner provides better feedback

                # Clear progress bar at the end
                time.sleep(0.5) # Brief pause before removing progress bar
                progress_bar.empty()
                end_process_time = time.time()
                total_time = end_process_time - start_process_time

                # 3. Display Results
                st.subheader("📄 Transcription Result")
                final_text = "\n\n".join(full_transcript).strip() # Join chunks with double newline

                if final_text and not all(s.startswith("[ERROR") or s.startswith("[EMPTY") for s in full_transcript):
                     with st.expander("Show Full Transcription", expanded=True):
                        st.text_area("Transcription", final_text, height=400)
                     st.success(f"✅ Transcription completed in {total_time:.2f} seconds!")
                else:
                     st.warning("Transcription result is empty or only contains errors.")

                if errors_encountered:
                    st.error("Some errors occurred during transcription:")
                    for err in errors_encountered:
                        st.code(err) # Show specific errors
    else:
        # If no API key is available, show an error message instead of the button
        st.error("🔴 OpenAI API Key is missing. Please configure secrets or enter it in the sidebar.")

elif uploaded_file is None:
    st.info("Please upload an audio file to begin.")

# --- End of Corrected Section ---


# Sidebar Info
st.sidebar.header("About")
st.sidebar.info(
    "This app uses **OpenAI's gpt-4o-mini-transcribe API** via `pydub` for audio processing. "
    "Large files are chunked automatically. Ensure your OpenAI API key is set up correctly "
    "in Hugging Face Space secrets for deployment."
)
st.sidebar.warning(
    "**Cost:** Running transcriptions incurs costs based on the duration of audio processed by OpenAI."
)
st.sidebar.markdown("---")
st.sidebar.markdown(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}") # Display current time
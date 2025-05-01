import streamlit as st
from google.cloud import storage
from google import genai
from google.genai import types
import base64

def getfilelist(bucket_name, prefix=""):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

    print(f"Files in bucket '{bucket_name}':")
    file_list = []
    for blob in blobs:
        print(blob)
        file_list.append(blob.name)
    return file_list

def generate(file_uri):
  client = genai.Client(
      vertexai=True,
      project="genaillentsearch",
      location="us-central1",
  )

  document1 = types.Part.from_uri(
      file_uri=file_uri,
      mime_type="application/pdf",
  )

  model = "gemini-2.0-flash-001"
  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part.from_text(text="""Can you summarise this file"""),
        document1
      ]
    )
  ]
  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
  )
  output = ""
  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    print(chunk.text, end="")
    output = output + chunk.text
  return output




st.set_page_config(layout="wide")
col1, col2 = st.columns([1,3])
with col1:
    st.image("image/logo.png", width=150)
    if "filelist" not in st.session_state:
        st.session_state.filelist = getfilelist("contract-analysis-sg")
    selected_file = st.selectbox("Select File", st.session_state.filelist, key="selected_file")
    summary_clicked = st.button("Generate Summary")
with col2:
    st.title("BUD Claims")
    if summary_clicked:
       st.write(selected_file)
       with st.container(border=True):
        st.markdown(generate(f"gs://contract-analysis-sg/{selected_file}"))
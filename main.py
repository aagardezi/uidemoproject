import streamlit as st
from google.cloud import storage
from google import genai
from google.genai import types
import os
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
import io
import base64

import helpercode

BUCKET_NAME = os.environ.get("BUCKET_NAME")
PROJECT_ID = helpercode.get_project_id()


def getfilelist(bucket_name, prefix=""):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

    print(f"Files in bucket '{bucket_name}':")
    file_list = []
    for blob in blobs:
        print(blob)
        file_list.append(blob.name)
    return file_list

def download_pdf_from_gcs(bucket_name, blob_name):
    """Downloads a PDF from GCS into a BytesIO object."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        pdf_bytes = blob.download_as_bytes()
        return io.BytesIO(pdf_bytes)
    except Exception as e:
        st.error(f"Error downloading PDF '{blob_name}' from bucket '{bucket_name}': {e}")
        return None


def generate(file_uri):
  client = genai.Client(
      vertexai=True,
      project=PROJECT_ID,
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

def generategroundtruth(summarydata):
  client = genai.Client(
      vertexai=True,
      project=PROJECT_ID,
      location="us-central1",
  )

  

  model = "gemini-2.0-flash-001"
  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part.from_text(text=f"""Can you create some sample groundtruth data based on 
                             the Gemini generated summary given here: {summarydata}""")
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


def generatedataframe():
  client = genai.Client(
      vertexai=True,
      project=PROJECT_ID,
      location="us-central1",
  )

  msg1_text1 = types.Part.from_text(text="""Can you generate some random claims data the follows the json schema specified. make sure there are 11 different entries""")

  model = "gemini-2.0-flash-001"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_text1
      ]
    ),
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
    response_mime_type = "application/json",
    response_schema = {"type":"ARRAY","items":{"type":"OBJECT","properties":{"loss_location":{"type":"OBJECT","properties":{"Location Name":{"type":"STRING"},"Street Number1":{"type":"STRING"},"Street Number2":{"type":"STRING"},"Street Name":{"type":"STRING"},"City":{"type":"STRING"},"State/Region":{"type":"STRING"},"Country":{"type":"STRING"}},"required":["Location Name","Street Number1","Street Number2","Street Name","City","State/Region","Country"]},"rag":{"type":"OBJECT","properties":{"RAG Rating":{"type":"STRING","enum":["RED","AMBER","GREEN"]},"Reasoning":{"type":"STRING"}},"required":["RAG Rating"]},"denial":{"type":"OBJECT","properties":{"Claim Denied":{"type":"STRING","enum":["YES","NO","Not Known"]},"Reasoning":{"type":"STRING"}},"required":["Claim Denied"]},"bad_faith":{"type":"OBJECT","properties":{"Any Bad Faith Allegations":{"type":"STRING","enum":["YES","NO"]},"Allegations":{"type":"ARRAY","items":{"type":"STRING"},"min_items":0}},"required":["Any Bad Faith Allegations"]},"peril":{"type":"OBJECT","properties":{"Claim Peril":{"type":"STRING"},"Reasoning":{"type":"STRING"}},"required":["Claim Peril"]},"date_occurence":{"type":"OBJECT","properties":{"Date Specified":{"type":"STRING","enum":["YES","NO"]},"Day":{"type":"INTEGER","minimum":1,"maximum":31},"Month":{"type":"INTEGER","minimum":1,"maximum":12},"Year":{"type":"INTEGER","minimum":1000,"maximum":2030}},"required":["Date Specified"]},"claim_event":{"type":"OBJECT","properties":{"CAT Classification":{"type":"STRING"},"Event Classification":{"type":"STRING"},"PCS Classification":{"type":"STRING"}},"required":["PCS Classification"]},"litigation":{"type":"OBJECT","properties":{"Any Litigation":{"type":"STRING","enum":["YES","NO"]},"Coverage/Insured Litigation":{"type":"ARRAY","items":{"type":"STRING"},"min_items":0}},"required":["Any Litigation"]}}}},
  )
  output = ""

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    print(chunk.text, end="")
    output = output + chunk.text
  return pd.read_json(output)


st.set_page_config(layout="wide")
col1, col2 = st.columns([1,3])
with col1:
    st.image("image/logo.png", width=150)
    if "filelist" not in st.session_state:
        st.session_state.filelist = getfilelist(BUCKET_NAME)
    selected_file = st.selectbox("Select File", st.session_state.filelist, key="selected_file")
    summary_clicked = st.button("Generate Summary")
    json_clicked = st.button("Generate Claims Data")

with col2:
    st.title("BUD Claims")
    if summary_clicked:
      st.write(selected_file)
      with st.container(border=True):
        summarydata = generate(f"gs://{BUCKET_NAME}/{selected_file}")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
           st.title("Ground Truth")
           st.markdown(generategroundtruth(summarydata))
        with subcol2:
           st.title("Summary")
           st.markdown(summarydata)
      st.title("Source PDF File")
      pdf_viewer(input=download_pdf_from_gcs(BUCKET_NAME, selected_file).getvalue())
    if json_clicked:
      with st.container(border=True):
        st.dataframe(generatedataframe())
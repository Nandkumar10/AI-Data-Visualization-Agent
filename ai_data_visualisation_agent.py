# AI Data Visualization Agent
# Built with Streamlit + Together AI + E2B Sandbox
# The idea is simple — upload a CSV, ask a question, get a chart back.
# The LLM writes the Python code and E2B runs it safely in the cloud.

import os
import json
import re
import sys
import io
import contextlib
import warnings
from typing import Optional, List, Any, Tuple
from PIL import Image
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from together import Together
from e2b_code_interpreter import Sandbox

# Suppress noisy pydantic warnings that don't affect functionality
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# This regex pulls out the Python code block from the LLM's markdown response
pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)


def code_interpret(e2b_code_interpreter: Sandbox, code: str) -> Optional[List[Any]]:
    """
    Sends the AI-generated Python code to the E2B sandbox and runs it.
    I redirect stdout/stderr during execution to keep the Streamlit UI clean.
    Returns the execution results (charts, dataframes, etc.) or None if something fails.
    """
    with st.spinner('Running your code in the sandbox...'):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec = e2b_code_interpreter.run_code(code)

        # Log any warnings or errors to stderr for debugging purposes
        if stderr_capture.getvalue():
            print("[Sandbox Warnings/Errors]", file=sys.stderr)
            print(stderr_capture.getvalue(), file=sys.stderr)

        if stdout_capture.getvalue():
            print("[Sandbox Output]", file=sys.stdout)
            print(stdout_capture.getvalue(), file=sys.stdout)

        if exec.error:
            print(f"[Sandbox ERROR] {exec.error}", file=sys.stderr)
            return None

        return exec.results


def match_code_blocks(llm_response: str) -> str:
    """
    Extracts the Python code block from the LLM's response.
    The model wraps its code in triple backticks — this pulls it out cleanly.
    Returns an empty string if no code block is found.
    """
    match = pattern.search(llm_response)
    if match:
        code = match.group(1)
        return code
    return ""


def chat_with_llm(e2b_code_interpreter: Sandbox, user_message: str, dataset_path: str) -> Tuple[Optional[List[Any]], str]:
    """
    Sends the user's question to the LLM along with the dataset path as context.
    The model is prompted to act as a data scientist and return executable Python code.
    Once we get the code back, we pass it straight to the E2B sandbox to run.
    """
    # I tell the model exactly where the dataset lives so it reads the right file
    system_prompt = f"""You are an expert Python data scientist and visualization specialist.
You have been given a dataset located at '{dataset_path}' and a question from the user.
Analyze the dataset and answer the question by writing and running Python code.
IMPORTANT: Always load the dataset using the path '{dataset_path}' in your code."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    with st.spinner('Thinking and generating code...'):
        client = Together(api_key=st.session_state.together_api_key)
        response = client.chat.completions.create(
            model=st.session_state.model_name,
            messages=messages,
        )

        response_message = response.choices[0].message
        python_code = match_code_blocks(response_message.content)

        if python_code:
            # Run the extracted code in the sandbox and return results
            code_interpreter_results = code_interpret(e2b_code_interpreter, python_code)
            return code_interpreter_results, response_message.content
        else:
            # Sometimes the model responds with text only — handle that gracefully
            st.warning("The model didn't return any executable code. Try rephrasing your question.")
            return None, response_message.content


def upload_dataset(code_interpreter: Sandbox, uploaded_file) -> str:
    """
    Uploads the user's CSV file into the E2B sandbox environment.
    The sandbox is isolated, so the file needs to be pushed in before the code can read it.
    Returns the file path inside the sandbox.
    """
    dataset_path = f"./{uploaded_file.name}"

    try:
        code_interpreter.files.write(dataset_path, uploaded_file)
        return dataset_path
    except Exception as error:
        st.error(f"Couldn't upload the file to the sandbox: {error}")
        raise error


def main():
    """
    Main app entry point.
    Handles the full user flow: API key setup → file upload → question → result display.
    """
    st.title("📊 AI Data Visualization Agent")
    st.write("Upload your CSV dataset and ask anything about it in plain English!")

    # Set up session state to persist API keys and model choice across reruns
    if 'together_api_key' not in st.session_state:
        st.session_state.together_api_key = ''
    if 'e2b_api_key' not in st.session_state:
        st.session_state.e2b_api_key = ''
    if 'model_name' not in st.session_state:
        st.session_state.model_name = ''

    with st.sidebar:
        st.header("Configuration")

        # Together AI key — used to call the LLM
        st.session_state.together_api_key = st.sidebar.text_input("Together AI API Key", type="password")
        st.sidebar.info("💡 New users get a free $1 credit on Together AI — enough to get started!")
        st.sidebar.markdown("[Get your Together AI key](https://api.together.ai/signin)")

        # E2B key — used to spin up the code execution sandbox
        st.session_state.e2b_api_key = st.sidebar.text_input("E2B API Key", type="password")
        st.sidebar.markdown("[Get your E2B key](https://e2b.dev/docs/legacy/getting-started/api-key)")

        # Model selector — I added a few options so you can experiment
        model_options = {
            "Meta-Llama 3.1 405B": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "DeepSeek V3": "deepseek-ai/DeepSeek-V3",
            "Qwen 2.5 7B": "Qwen/Qwen2.5-7B-Instruct-Turbo",
            "Meta-Llama 3.3 70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        }
        selected_model = st.selectbox(
            "Choose a Model",
            options=list(model_options.keys()),
            index=0  # Defaults to Llama 405B — strongest option
        )
        st.session_state.model_name = model_options[selected_model]

    # File uploader — only accepts CSV for now
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.write("Your Dataset:")
        show_full = st.checkbox("Show full dataset")
        if show_full:
            st.dataframe(df)
        else:
            st.write("Preview (first 5 rows):")
            st.dataframe(df.head())

        # The user types their question here
        query = st.text_area(
            "What would you like to know about your data?",
            "Can you compare the average cost for two people between different categories?"
        )

        if st.button("Analyze"):
            if not st.session_state.together_api_key or not st.session_state.e2b_api_key:
                st.error("Please add both API keys in the sidebar before running.")
            else:
                # Spin up the E2B sandbox, upload the file, run the analysis
                with Sandbox(api_key=st.session_state.e2b_api_key) as code_interpreter:
                    dataset_path = upload_dataset(code_interpreter, uploaded_file)
                    code_results, llm_response = chat_with_llm(code_interpreter, query, dataset_path)

                    # Show the model's full text response
                    st.write("AI Response:")
                    st.write(llm_response)

                    # Render whatever the sandbox returned — chart, table, or plain output
                    if code_results:
                        for result in code_results:
                            if hasattr(result, 'png') and result.png:
                                # Decode base64 PNG and render it as an image
                                png_data = base64.b64decode(result.png)
                                image = Image.open(BytesIO(png_data))
                                st.image(image, caption="Generated Chart", use_container_width=False)

                            elif hasattr(result, 'figure'):
                                # Matplotlib figure
                                st.pyplot(result.figure)

                            elif hasattr(result, 'show'):
                                # Plotly figure
                                st.plotly_chart(result)

                            elif isinstance(result, (pd.DataFrame, pd.Series)):
                                # Tabular result
                                st.dataframe(result)

                            else:
                                # Fallback for any other output type
                                st.write(result)


if __name__ == "__main__":
    main()

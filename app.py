import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Matrix", page_icon=":robot_face:", layout="wide")
st.title("AI Matrix")
st.subheader("A simple app to run multiple OpenAI models at once")


def api_key_loaded():
    return st.session_state.get("api_key", "") != ""


def load_model_options():
    if "model_options" not in st.session_state or st.session_state["model_options"] == [
        "Load API key first..."
    ]:
        st.session_state["model_options"] = [model.id for model in openai.models.list()]


def add_column():
    st.session_state.num_columns += 1


def run_column(column_index):
    openai_message = [
        {
            "role": "system",
            "content": common_system_prompt
            if use_common_system
            else st.session_state[f"system_{column_index}"],
        },
        {
            "role": "user",
            "content": common_user_prompt
            if use_common_user
            else st.session_state[f"user_{column_index}"],
        },
    ]
    response = openai.chat.completions.create(
        model=st.session_state[f"model_{column_index}"],
        messages=openai_message,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    st.session_state[f"model_response_{column_index}"] = response.choices[
        0
    ].message.content


def run_all():
    for idx, col in enumerate(cols):
        run_column(idx)


def createColumn(column, idx):
    with column:
        default_index = (
            st.session_state["model_options"].index("gpt-4-1106-preview")
            if "gpt-4-1106-preview" in st.session_state["model_options"]
            else 0
        )
        model = st.selectbox(
            "Choose a model",
            st.session_state["model_options"],
            index=default_index,
            key=f"model_{idx}",
            disabled=not api_key_loaded(),
        )
        if not use_common_system:
            system_prompt = st.text_area(
                "System Prompt",
                value="You are a helpful assistant.",
                key=f"system_{idx}",
            )
        if not use_common_user:
            user_prompt = st.text_area(
                "User Prompt", placeholder="Enter prompt...", key=f"user_{idx}"
            )
        if f"model_response_{idx}" in st.session_state:
            generated_text = st.markdown(st.session_state[f"model_response_{idx}"])
        st.button(
            "Run",
            key=f"run{idx}",
            on_click=run_column,
            args=(idx,),
            disabled=not api_key_loaded(),
            use_container_width=True,
        )


if api_key_loaded():
    openai = OpenAI(api_key=st.session_state["api_key"])
    load_model_options()
else:
    st.session_state["model_options"] = ["Load API key first..."]

st.sidebar.markdown("## Settings")
sidebar_text = st.sidebar.text_input(
    "OpenAI API Key", placeholder="sk-...", key="api_key"
)
use_common_system = st.sidebar.checkbox(
    "Use common system prompt", value=True, key="use_common_system_prompt"
)
if use_common_system:
    common_system_prompt = st.sidebar.text_area(
        "Common System Prompt",
        value="You are a helpful assistant.",
        key="common_system_prompt",
    )
use_common_user = st.sidebar.checkbox(
    "Use common user prompt", value=True, key="use_common_user_prompt"
)
if use_common_user:
    common_user_prompt = st.sidebar.text_area(
        "Common user Prompt", placeholder="Enter prompt...", key="common_user_prompt"
    )
temperature = st.sidebar.slider(
    "Temperature", min_value=0.0, max_value=2.0, value=0.5, step=0.1, key="temperature"
)
max_tokens = st.sidebar.slider(
    "Max Tokens", min_value=1, max_value=4096, value=1000, step=1, key="max_tokens"
)

if "num_columns" not in st.session_state:
    st.session_state.num_columns = 1
cols = st.columns(st.session_state.num_columns)

for idx, col in enumerate(cols):
    createColumn(col, str(idx))

add_model_col, run_all_col = st.columns([1, 5])
with add_model_col:
    add_model_button = st.button(
        "Add Model", on_click=add_column, use_container_width=True
    )
with run_all_col:
    run_all_button = st.button(
        "Run All",
        on_click=run_all,
        type="primary",
        disabled=not api_key_loaded(),
        use_container_width=True,
    )

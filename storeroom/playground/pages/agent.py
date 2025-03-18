import asyncio
from dataclasses import dataclass

import streamlit as st


@dataclass
class Tool:
    name: str
    description: str


Manifest = list[Tool]


@dataclass
class Agent:
    name: str
    instruction: str
    manifest: Manifest

    def invoke(self, messages: list) -> str: ...


def format_manifest(manifest: Manifest) -> str:
    string = ""

    for tool in manifest:
        string += f"- **{tool.name}**: {tool.description}\n\n"

    return string


async def main():
    agent = Agent(name="...", instruction="...", manifest=[])
    manifest = format_manifest(agent.manifest)

    st.title("💬 Basic Agent Chatbot")
    st.caption("🚀 A Streamlit chatbot")

    with st.expander("View Manifest"):
        st.markdown(manifest)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})

        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            response = ""
            with st.spinner("Thinking..."):
                response = await agent.invoke(messages=st.session_state["messages"])

            st.markdown(response)

        st.session_state["messages"].append({"role": "assistant", "content": response})


if __name__ == "__main__":
    asyncio.run(main())

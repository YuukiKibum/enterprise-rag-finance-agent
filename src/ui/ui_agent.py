import streamlit as st
import uuid
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage

from langgraph.checkpoint.memory import InMemorySaver

from common import config
from chroma_db_functionalities.fetch_result_from_vectorDb import retrieve_context
from chroma_db_functionalities.vector_db_inspection import format_vector_db_summary

load_dotenv()

# ---------------------------------------------------------
# TOOL: VECTOR DB RETRIEVAL
# ---------------------------------------------------------
@tool
def fetchDataFromSercoKnowBase(query: str):
    """
    Fetch context from Serco vector DB
    """
    docs, metas = retrieve_context(query)

    context = ""
    for i, (d, m) in enumerate(zip(docs, metas)):
        context += f"\n[Chunk {i} from {m['file_name']}]\n{d}\n"

    return context

@tool
def getSercoKnowledgeBaseFileInventory(query: str = ""):
    """
    Gets the current ChromaDB knowledge base inventory.
    Use this tool when the user asks:
    - how many files are uploaded
    - what files are stored
    - file names in ChromaDB
    - number of chunks
    - knowledge base contents
    """
    return format_vector_db_summary()

# ---------------------------------------------------------
# LLM + AGENT
# ---------------------------------------------------------
llm = ChatOpenAI(
    model=config.OPENAI_LLM_MODEL,
    temperature=0.7
)

system_prompt = """
You are an AI-powered FP&A, Bids, and M&A Manager for Serco, specializing in financial analysis, bid support, mergers & acquisitions analysis, invoice review, financial consolidation, reporting, and strategic business support.

Your responsibilities include:

* Reviewing and analyzing finance invoices accurately and efficiently
* Extracting and consolidating financial data from multiple business documents
* Supporting FP&A activities including budgeting, forecasting, variance analysis, and financial reporting
* Assisting with bid analysis, pricing support, cost evaluations, commercial reviews, and profitability assessments
* Supporting M&A activities including financial due diligence, business evaluations, synergy analysis, and investment assessments
* Identifying financial inconsistencies, risks, duplicate entries, missing information, and operational concerns
* Creating professional financial summaries, executive-ready reports, and business insights
* Generating structured Excel-ready tables and financial outputs whenever required
* Providing concise, analytical, and business-focused recommendations

You must behave like a senior Serco finance professional:

* Highly analytical and detail-oriented
* Professional and concise in communication
* Strong commercial and strategic mindset
* Focused on accuracy, compliance, and business impact
* Capable of handling sensitive financial and operational information professionally

IMPORTANT STRICT KNOWLEDGE SOURCE RULES:

* For document-content questions, you MUST use `fetchDataFromSercoKnowBase` before answering.
* For knowledge base inventory questions, you MUST use `getSercoKnowledgeBaseFileInventory` before answering.
* Do not answer file count, file name, or ChromaDB inventory questions from memory.
* The tool returns contextual information retrieved from Serco’s internal Vector Database (RAG context)
* ALL responses must be based STRICTLY on the information returned by the `fetchDataFromSercoKnowBase` tool
* Do NOT generate assumptions, hallucinations, or unsupported financial conclusions
* Do NOT rely on general knowledge when answering Serco-related questions
* If the retrieved context does not contain enough information, respond with:
  "The requested information is not available in the provided Serco knowledge base context."
* Always prioritize retrieved Serco data over general knowledge
* Maintain confidentiality and professionalism at all times

TOOLS AVAILABLE:

1. fetchDataFromSercoKnowBase

Purpose:
Fetches relevant document chunks from the Serco Vector Database knowledge base using semantic search.

Use this tool when the user asks business, finance, FP&A, bid, M&A, invoice, reporting, or document-content questions.

2. getSercoKnowledgeBaseFileInventory

Purpose:
Reads the current ChromaDB inventory and returns:
- number of files stored
- file names
- number of chunks stored
- chunk count per file

Use this tool when the user asks:
- how many files are uploaded
- what files are in ChromaDB
- what documents are in the knowledge base
- list the file names
- how many chunks are stored
- whether the knowledge base has files

Tool Input:

* query (str): User question or search query

Tool Output:

* Relevant Serco document chunks and contextual information

OUTPUT GUIDELINES:

* First retrieve relevant context using the `fetchDataFromSercoKnowBase` tool
* Analyze the retrieved context carefully before answering
* Present financial and business data in structured, executive-friendly formats
* Use clear summaries, bullet points, tables, and categorized insights where appropriate
* Generate Excel-friendly outputs with properly structured rows and columns when requested
* Highlight key risks, opportunities, discrepancies, assumptions, and actionable insights
* Ensure financial calculations and consolidations are logically accurate and internally consistent
* Keep responses concise, professional, and decision-oriented
* Clearly mention when information is unavailable in the retrieved knowledge base

Your objective is to function as a trusted AI finance and strategy assistant for Serco, supporting FP&A operations, bids, M&A activities, invoice processing, and financial analysis using only the trusted Serco knowledge base context retrieved through the provided tool.
"""
agent = create_agent(
    llm,
    tools=[fetchDataFromSercoKnowBase, getSercoKnowledgeBaseFileInventory],
    system_prompt=system_prompt,
    checkpointer=InMemorySaver()
)


# ---------------------------------------------------------
# STREAMLIT UI CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Serco AI Agent", layout="centered")

st.title("🤖 Serco AI Finance & M&A Agent")

st.caption("Powered by LangChain + ChromaDB + OpenAI")

# ---------------------------------------------------------
# SESSION ID
# ---------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# ---------------------------------------------------------
# SESSION STATE (chat memory)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------
user_input = st.chat_input("Ask your Serco AI Agent...")

if user_input:

    # show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # call agent
    response = agent.invoke(
    {"messages": [HumanMessage(user_input)]},
    config=
        {
            "configurable": 
            {
                "thread_id": st.session_state.thread_id
            }
        }
    )

    response_text = response["messages"][-1].content

    # store assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # show assistant response
    with st.chat_message("assistant"):
        st.markdown(response_text)
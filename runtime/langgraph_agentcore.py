from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from typing import Optional
import boto3
import datetime
import json
import random
import os
import tempfile

# Exclusive deploy to AgentCore Runtime
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

region = "us-west-2"
s3 = boto3.client('s3', region_name=region)

# Retrieve Gemini API Key from AWS Secret Manager
secretmanager = boto3.client('secretsmanager', region_name=region)
response = secretmanager.get_secret_value(SecretId='geminiapikey')
secret_json = json.loads(response["SecretString"])
api_key = secret_json["GEMINI_API_KEY"]
llm = init_chat_model("google_genai:gemini-2.5-flash", google_api_key=api_key)

# Structure of this AI Agent
# User --> Extract CV --> Compare and Match between Job Requirements and CV --> Result to the next step of the recruitment process -->
# Create Interview Email --> Create Interview Question --> End OR Create Rejection Email -> End

# NODE 1: Compare and Match between Job Requirements and CV
class compareMatchClass(BaseModel):
    """Compare and match between job requirements and curriculum vitae."""
    minimal_requirements_analysis: str = Field(description="Analysis of minimal requirements")
    preferred_requirements_analysis: str = Field(description="Analysis of preferred requirements")
    strengths: str = Field(description="Strengths of candidate")
    potential_gaps: str = Field(description="Potential gaps of candidate")
    candidate_name: str = Field(description="Candidate name in the CV")

compareMatch = create_agent(
    model=llm,
    response_format=compareMatchClass,
    system_prompt="""
    You are a virtual human resources expert. You help me compare and match between curriculum vitae of candidate and AI engineer position job requirements like this :
    1. Work across the AI lifecycle: from data preparation and model development to evaluation and deployment.
    2. Fine-tune and integrate LLMs (like OpenAI and Gemini) into ERP workflows.
    3. Build smart features such as recommendation engines, forecasting modules, NLP tools, and more.
    Preferred requirements :
    Develop and maintain scalable cloud-based AI solutions across multi-cloud platforms (AWS, GCP, Azure).
    Write output structure like this:
    Minimal Requirements Analysis :

    Requirement 1:

    Requirement n (n is the number of requirement):

    Preferred Requirement Analysis :

    Strengths:

    Potential Gaps:

    Candidate Name:
    """
)

def compareMatchNode(state: MessagesState):
    result = compareMatch.invoke(state)
    return Command(update={"messages": result["messages"]})

# NODE 2: Score to the Next Step of the Recruitment Process
class scoreNextStepClass(BaseModel):
    """Score value to proceed to the next step in the recruitment process."""
    score: int = Field(description="Score of candidate matched")

scoreNextStep = create_agent(
    model=llm,
    response_format=scoreNextStepClass,
    system_prompt="""
    You are a virtual human resources expert. You help me add value from 0 until 10 to the next step of recruitment process.
    Answer with a number between 0 and 10 ONLY without any additions. Write output structure like this:
    1
    """
)

def scoreNextStepNode(state: MessagesState):
    result = scoreNextStep.invoke(state)
    return Command(update={"messages": result["messages"]})

# NODE 3: Create Rejection/Interview Email
class createEmailClass(BaseModel):
    """Create rejection email or interview invitation email for candidate."""
    email: str = Field(description="Body of email for candidate. Use `[CANDIDATE_NAME]`, `[INTERVIEW_DATE]` and `[INTERVIEW_TIME]` as placeholders for interview emails.")

createEmail = create_agent(
    model=llm,
    response_format=createEmailClass,
    system_prompt="""
    You are a virtual human resources expert. You are help me create email in the recruitment process.

    If the score is LESS THAN 7 out of 10, create a very simple rejection about failed to AI engineer position email for unsuccessful candidate.
    Write output structure like this:
    Hello, [CANDIDATE_NAME]\n
    ........\n
    Thanks,\n
    HRD of AgentCore.

    But if the score is MORE THAN 7 out of 10, create an interview email for a candidate accepted to the next step to AI engineer position. Write output structure like this:
    Hello, [CANDIDATE_NAME]\n
    ........\n
    Date : [INTERVIEW_DATE]\n
    Time : [INTERVIEW_TIME]\n
    Google Meet interview link : https://bit.ly/agentcore-interview\n
    ........\n
    Thanks,\n
    HRD of AgentCore.
    """
)

def createEmailNode(state: MessagesState):
    # Extract candidate name from the compareMatch output
    compare_match_output_str = state["messages"][1].content
    compare_match_output = json.loads(compare_match_output_str)
    candidate_name = compare_match_output['candidate_name']

    result = createEmail.invoke(state)
    llm_output_message = result["messages"][-1]

    email_data = json.loads(llm_output_message.content)
    email_body = email_data['email']

    # Replace candidate name placeholder
    email_body = email_body.replace("[CANDIDATE_NAME]", candidate_name)

    if "[INTERVIEW_DATE]" in email_body and "[INTERVIEW_TIME]" in email_body:
        # Formatted interview date (today + 3 days)
        today = datetime.date.today()
        interview_date = today + datetime.timedelta(days=3)
        formatted_date = interview_date.strftime("%d-%m-%Y")

        # Formatted interview time between 1 PM (13:00) and 4 PM (16:00)
        hour = random.randint(13, 16)
        minute = random.choice([0, 30])
        if hour == 16 and minute == 30:
            minute = 0 # if 4:30 PM was chosen, adjust to 4:00 PM
        interview_time = datetime.time(hour, minute, 0)
        formatted_time = interview_time.strftime("%I:%M %p")

        # Replace placeholders in the email body
        email_body = email_body.replace("[INTERVIEW_DATE]", formatted_date)
        email_body = email_body.replace("[INTERVIEW_TIME]", formatted_time)

    updated_email_data = {"email": email_body}
    updated_email_message = AIMessage(
        content=json.dumps(updated_email_data)
    )

    new_messages = state["messages"][:-1] + [updated_email_message]
    return Command(update={"messages": new_messages})

# NODE 4: Create Interview Questions
class createInterviewQuestionClass(BaseModel):
    """Create interview questions for candidates who are accepted to the next step."""
    questions: str = Field(description="Interview questions for candidate")

createInterviewQuestion = create_agent(
    model=llm,
    response_format=createInterviewQuestionClass,
    system_prompt="""
    You are a virtual human resources expert. You are help me create 3 interview questions about CV PDF file that already extracted.

    If the score is LESS THAN 7 out of 10, DO NOT create interview questions. Write output structure like this:
    {\"questions\": \"-\"}

    But if the score is MORE THAN 7 out of 10, create 3 interview questions about CV PDF file that already extracted. Write output structure like this:
    QUESTION 1 : ........ \n
    QUESTION 2 : ........ \n
    QUESTION 3 : ........ \n
    """
)

def createInterviewQuestionNode(state: MessagesState):
    result = createInterviewQuestion.invoke(state)
    return Command(update={"messages": result["messages"]})

# Create AI agent graph
workflow = StateGraph(MessagesState)
workflow.add_node("compareMatch", compareMatchNode)
workflow.add_node("scoreNextStep", scoreNextStepNode)
workflow.add_node("createEmail", createEmailNode)
workflow.add_node("createInterviewQuestion", createInterviewQuestionNode)

workflow.add_edge(START, "compareMatch")
workflow.add_edge("compareMatch", "scoreNextStep")
workflow.add_edge("scoreNextStep", "createEmail")
workflow.add_edge("createEmail", "createInterviewQuestion")
workflow.add_edge("createInterviewQuestion", END)
graph = workflow.compile()

# Extract CV PDF file
def extract_cv(inputpdf):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        local_file_path = temp_pdf_file.name
        s3.download_file("screening-candidate", inputpdf, local_file_path)
    from pypdf import PdfReader
    reader = PdfReader(local_file_path)
    page = reader.pages[0]
    text = page.extract_text()
    return text
    os.remove(local_file_path)

@app.entrypoint
def langgraph_agentcore(payload):
    # This input is the filename of the PDF
    pdf_filename = payload.get("inputpdf")

    # Extract text from the PDF file
    user_input = extract_cv(pdf_filename)
    events = graph.invoke({"messages": [("user", user_input)]})
    messages = events["messages"]
    # If write events["messages"][-1].content, return questions only without email, score, etc.
    # Create all classes to produce output like below.

    # Output from Node 1
    content_dict = json.loads(messages[1].content)
    mra = content_dict['minimal_requirements_analysis']
    pra = content_dict['preferred_requirements_analysis']
    strengths = content_dict['strengths']
    potential_gaps = content_dict['potential_gaps']

    # Output from Node 2
    content_dict_2 = json.loads(messages[2].content)
    score = content_dict_2['score']

    # Output from Node 3
    content_dict_3 = json.loads(messages[3].content)
    email = content_dict_3['email']

    # Output from Node 4
    content_dict_4 = json.loads(messages[4].content)
    questions = content_dict_4['questions']

    # Delete CV PDF file in S3 after processing
    s3.delete_object(Bucket="screening-candidate", Key=pdf_filename)
    return mra, pra, strengths, potential_gaps, score, email, questions

app.run()
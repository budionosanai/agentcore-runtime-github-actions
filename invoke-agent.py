import boto3
import json
import os

region = "us-west-2"
s3 = boto3.client('s3', region)
invoke = boto3.client('bedrock-agentcore', region)
control = boto3.client('bedrock-agentcore-control', region)

def upload_to_s3(file_path):
    # Upload PDF file to S3
    s3.upload_file(file_path, "screening-candidate", file_path)
    return file_path

def analyze_cv(file_path):
    # Get Agent Runtime ID
    agent_id = os.getenv('AGENT_ID')
    get_agent_arn = control.get_agent_runtime(
        agentRuntimeId=agent_id
    )

    # Invoke AI Agent
    cvpdf = upload_to_s3(file_path)
    invoke_response = invoke.invoke_agent_runtime(
        agentRuntimeArn=get_agent_arn['agentRuntimeArn'],
        payload=json.dumps({"inputpdf": cvpdf})
    )
    response_body = invoke_response['response'].read()
    response_data = json.loads(response_body)
    
    # Result
    mra = response_data[0]
    pra = response_data[1]
    strengths = response_data[2]
    potential_gaps = response_data[3]
    score = response_data[4]
    email = response_data[5]
    questions = response_data[6]
    
    print("Minimal Requirements Analysis:")
    print(mra)
    print("\nPreferred Requirements Analysis:")
    print(pra)
    print("\nStrengths:")
    print(strengths)
    print("\nPotential Gaps:")
    print(potential_gaps)
    print("\nScore:")
    print(score)
    print("\nEmail:")
    print(email)
    print("\nQuestions:")
    print(questions)

if __name__ == "__main__":
    for pdf in ["Always Winner CV.pdf", "Sonny Wawwak CV.pdf"]:
        print(f"\nAnalyzing {pdf}...\n")
        analyze_cv(pdf)
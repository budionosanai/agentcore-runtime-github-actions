## 📘 Overview

This repository explains CI/CD implementation for AI agent candidate screening using **Github Actions**, deploy AI agent to **AgentCore Runtime** and invoke AI agent.

## 📁 Repository Structure

| File | Description |
| :--- | :--- |
| `.github/workflows/workflow.yaml` | End-to-end workflow from deployment to testing invocation. |
| `runtime/langgraph_agentcore.py` | Code of AI agent implementation using **Google Gemini** and **Langgraph**. |
| `runtime/requirements.txt` | Dependencies of libraries such as Langgraph, Google Gemini, Bedrock AgentCore, etc. |
| `deploy-runtime.py` | Code of configure using previous IAM role from `amazon-bedrock-agentcore-one-to-one/runtime/langgraph` and deploy to **AgentCore Runtime**. |
| `invoke-agent.py` | Code of invoke AI agent on **AgentCore Runtime**. |
| `Always Winner CV.pdf` and `Sonny Wawwak CV.pdf` | Sample PDF file used in `invoke-agent.py` code. |

## ✅ Prerequisites

1. **Amazon Web Services (AWS)**: Access to AWS services, you can sign up/sign in [here.](https://console.aws.amazon.com)
- **Amazon S3** : upload file from local to S3 and download file from S3 to AI agent processes.
- **AWS Secret Manager** : store Gemini API Key and LLM inference in AI agent.
- **AgentCore Runtime**, **AgentCore Observability** and **CloudWatch Logs**.
- **AgentCore Starter Toolkit** : quickly configure and deploy AI agent with several AWS services such as **Amazon ECR**, **AWS CodeBuild**, and **AWS IAM**.

2. **Langgraph**: Access to create AI agent application.

3. **Google Gemini**: Access to Gemini API key, you can sign up/sign in [here.](https://aistudio.google.com)

4. **Github**: Access to Github services, you can sign up/sign in [here.](https://github.com)
- **Github Actions**: CI/CD service that automate workflow.
- **Github Codespaces**: IDE service that write, commit and push code to a repository. 

5. To get an IAM role for **AgentCore Runtime**, you can see [this notebook](https://github.com/budionosanai/amazon-bedrock-agentcore-one-to-one/blob/main/runtime/langgraph/LanggraphWithAgentcore.ipynb) then open and run the notebook.

## 🚀 Getting Started

**Step 1 - AWS**

1. Sign in/login AWS account, click AWS username top right corner, click Security credentials.
2. In My security credentials page, see Access keys then click Create access key.
3. Checklist understand then click Create access key.
4. Copy AWS access key and AWS secret key to notepad.

**Step 2 - Github**

1. Create new repository, click Settings, click Secrets and variables in Security section, click Actions.
2. Click Repository secrets then click "New repository secret".
3. Input secret name and secret key : AWSACCESSKEY and your AWS access key & AWSSECRETKEY and your AWS secret key.
4. Click "Add secret". Now go to Github Codespaces to create IDE online.
5. Choose repository, click "Create codespace".
6. Create all file in Repository Structure then write following code. In `deploy-runtime.py` file, change to your IAM role.
7. After all code is done, add all code, commit and push all code to repository.
8. Go to repository, click Actions, see Action is available and running until done.
9. Check AWS services such as AgentCore Runtime, Amazon ECR and AgentCore Observability on Amazon CloudWatch for monitoring/observability.

**Step 3 - Delete AWS services (Optional)**

## ⚠️ Warning

**Ensure securely API keys such as AWS credentials and Gemini API key — DO NOT HARDCORE them in notebooks.**

## 📚 Resources

* [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
* [Langgraph documentation](https://docs.langchain.com/oss/python/langgraph/)
* [Google Gemini documentation](https://ai.google.dev/gemini-api/docs/)
* [Github Actions documentation](https://docs.github.com/en/actions/)

## Tutorial Blog

* https://dev.to/budionosan/amazon-bedrock-agentcore-runtime-with-langgraph-crewai-and-google-gemini-57l5
* https://dev.to/budionosan/deploy-and-invoke-ai-agent-to-agentcore-runtime-with-github-actions-j6f

## 🙏 Acknowledgments

**Amazon Web Services, Google Gemini, Langgraph and Github**

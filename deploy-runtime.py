from bedrock_agentcore_starter_toolkit import Runtime
import boto3

def deploy():
    # Retrieve AWS Account ID
    sts_client = boto3.client('sts')
    response = sts_client.get_caller_identity()
    aws_account_id = response['Account']
    
    agentcore_runtime = Runtime()
    region = "us-west-2"
    agent_name = "langgraph_githubActions"
    
    # Configure AgentCore Runtime
    response = agentcore_runtime.configure(
    	entrypoint="runtime/langgraph_agentcore.py",
    	auto_create_execution_role=False,
        execution_role=f"arn:aws:iam::{aws_account_id}:role/AmazonBedrockAgentCoreSDKRuntime-us-west-2-abffe6b486",
    	auto_create_ecr=True,
    	requirements_file="runtime/requirements.txt",
    	region=region,
    	agent_name=agent_name
    )
    
    # Launch/update AgentCore Runtime
    launch_result = agentcore_runtime.launch(auto_update_on_conflict=True)
    print("✅ Deployment completed successfully :)")
    agent_id = launch_result.agent_id
    print("✅ Your Agent Runtime ID : " + agent_id)

    # Write Agent ID
    with open('agent_id.txt', 'w') as f:
        f.write(agent_id)
    
if __name__ == "__main__":
    deploy()
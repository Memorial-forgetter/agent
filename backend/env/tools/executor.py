from langchain_community.chat_models import ChatOpenAI
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from tools.tool import empty_tools, collider, confound, edge_direction, condition_independent_test_tools, generate_causalgraph_tool, ate_tool, summarize_dag_tool, analyze_dag_tool

memory = None
api_key = 'sk-rdffprsjjtdjnfhivtftvpiobqdrahnxgmmnwhrjxxrpxfcj'

prompt = hub.pull("hwchase17/react")

ICL_lizi = """
##DEMO：
The doctor wants to explore the relationship between smoking, lung cancer, and yellow fingers, so he collects a batch of data, stores it in 'data.csv', and gives the following proposition: if all of the statements are false, output no; if one of the statements is true, output uncertain; if all of the statements are true, output yes. The proposition is as follows:

1. Yellow fingers are a cause of lung cancer
2. There is a collider between yellow finger and lung cancer
3. There is a confounder between yellow fingers and lung cancer
4. Yellow fingers and lung cancer are independent of each other given smoking

The output is just formatted as a json string, such as {{"answer":"yes"}}.

Thought: I need to generate a causal diagram, and then analyze the causal and independent relationships between variables to judge the correctness of each proposition
Action:Generate Causal
Action Input:{{"filename": "data.csv", "analyse_relationship": "True"}}
Observation:causal graph named 'data' is generate succeed!  and have written to the memory.

Thought: I need to use the Determine_edge_directions tool to determine if the yellow finger is the cause of smoking
Action:Determine_edge_directions
Action Input:{{"cg_name": "data", "interesting_var": ["yellow fingers", "lung cancer"]}}
Observation:There is no direct edge linking  yellow finger and cancer


Thought: There is no direct causal link between yellow finger and lung cancer. The proposition "yellow finger is the cause of lung cancer" is wrong. I need to continue to determine whether there is a collider between yellow finger and lung cancer
Action:Determine_collider
Action Input:{{"cg_name": "data", "interesting_var": ["yellow fingers", "lung cancer"]}}
Observation:There don't exists collider Smoking of yellow fingers and lung cancer

Thought: There is no collider between yellow finger and lung cancer, I need to continue to determine whether there is a confounder between yellow finger and lung cancer
Action:Determine_confounder
Action Input:{{"cg_name": "data", "interesting_var": ["yellow fingers", "lung cancer"]}}
Observation:yes, There is an unblocked backdoor path between yellow finger and lung cancer so confounder exists. Backdoor path: yellow fingers, smoking, lung cancer

Thought: There is an unblocked backdoor path between yellow finger and lung cancer, so there is a confounder, and it is smoking, I need to continue to determine whether yellow finger and lung cancer are independent of each other given smoking
Action:condition independent test
Action Input:{{"filename":"data.csv","interesting_var":["yellow fingers","lung cancer"],"condition":["somking"]}}
Observation:yellow fingers and lung cancer is independent under conditions: smoking

Thought:i now get the final answer. I have analyzed the four propositions, among which the confounder between yellow fingers and lung cancer is correct, and the others are all wrong, so the answer is uncertian

Final Answer:{{"answer":"uncertain"}}

##Requirement: 
Answer the following questions with examples:

"""

prompt.template = 'Answer the following questions as best you can. You have access to the following tools:\n\n{tools}\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [{tool_names}]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nCheck you output and make sure it conforms! Do not output an action and a final answer at the same time.\n\nBegin!\n\n'+ICL_lizi +'Question: {input}\nThought:{agent_scratchpad}'

def get_agent():
    llm = ChatOpenAI(temperature=0.5, 
                    openai_api_key=api_key,
                    model_name="Pro/deepseek-ai/DeepSeek-R1",
                    openai_api_base='https://api.siliconflow.cn/v1',
                    streaming=True)
    tools = [condition_independent_test_tools, generate_causalgraph_tool, empty_tools, ate_tool,collider,confound,edge_direction,summarize_dag_tool,analyze_dag_tool]
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, 
                                tools=tools, 
                                verbose=True,
                                handle_parsing_errors="Check you output and make sure it conforms! Do not output an action and a final answer at the same time.",
                                return_intermediate_steps=True)
    return agent_executor
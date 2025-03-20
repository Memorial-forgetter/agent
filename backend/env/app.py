from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from causallearn.search.ConstraintBased.PC import pc
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
import json
from flask import Response
import os
import io
import warnings
import matplotlib
from tools.DGP import generate_description
from tools.util import Dataloader, CGMemory
from tools.executor import get_agent
import tools.executor as executor
from langchain.schema import AgentAction, AgentFinish
import time
warnings.filterwarnings("ignore")
matplotlib.use('TkAgg')


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# sanity check route
@app.route('/datagraph', methods=['GET'])
def get_data_graph():
    # 加载数据
    name = "auto-mpg.csv"  
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    file_path = os.path.join(current_dir, name)  # 拼接成绝对路径
    data = pd.read_csv(file_path, na_values=['?'])  # 将 `?` 视为缺失值

    # 数据预处理
    data = data.dropna()  # 去掉包含缺失值的行
    data = data.drop(['car name'], axis=1)  # 删除非数值列

    # 使用 PC 算法进行因果推断
    data_np = data.to_numpy()
    cg = pc(data_np)
    # print(cg.G)
    # cg.draw_pydot_graph()

    # 将图转换为邻接矩阵
    adj_matrix = np.zeros((cg.G.num_vars, cg.G.num_vars), dtype=int)
    for i in range(cg.G.num_vars):
        for j in range(cg.G.num_vars):
            if cg.G.graph[i][j] == -1 and cg.G.graph[j][i] == 1:
                adj_matrix[i][j] = 1
            if cg.G.graph[i][j] == 1 and cg.G.graph[j][i] == 1:
                adj_matrix[i][j] = 1
                adj_matrix[j][i] = 1

    # 将邻接矩阵转换为列表
    adj_matrix_list = adj_matrix.tolist()

    # 返回 JSON 响应
    return jsonify(adj_matrix_list)


@app.route('/datatable', methods=['GET'])
def get_data():
    # 加载数据
    name = "auto-mpg.csv"  
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    file_path = os.path.join(current_dir, name)  # 拼接成绝对路径
    data = pd.read_csv(file_path, na_values=['?'])  # 将 `?` 视为缺失值
    data = data.dropna()  # 去掉包含缺失值的行
    # print(data)
    
    # 将数据转换为字典
    data_dict = data.to_dict(orient='records')  
    # print(data_dict)

    # 返回 JSON 响应
    return jsonify(data_dict)  

@app.route('/dgp', methods=['POST'])
def dgp():
    # Parse incoming JSON data
    accept = request.get_json()

    # Get the data from the request
    type = accept.get("type", "")
    interesting = accept.get("interesting", [])  # List of interesting items
    T0 = accept.get("T0", None)  # Some floating-point number
    T1 = accept.get("T1", None)  # Another floating-point number

    # Initialize or modify description based on received data
    generate_description(type, interesting, T0, T1)

    # Return a confirmation response or a status message
    return jsonify({"message": "Data received and description generated."})

@app.route('/agent', methods=['GET'])
def agent():
    def stream():
        json_data = json.dumps({"message": "Processing started..."})
        yield f"data: {json_data}\n\n"

        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
        file_path = os.path.join(current_dir, 'dataset.jsonl')  # 拼接成绝对路径
        data_loader = Dataloader()
        num = data_loader.read_data(file_path)

        skip_num = 0
        out_file_path = os.path.join(current_dir, "result.jsonl")  # 拼接成绝对路径
        with open(out_file_path, 'r', encoding='utf-8') as f:
            skip_num = len(f.readlines())

        for index in range(num):
            line = data_loader.read_one(1)
            if index < skip_num:
                continue
            q, name, col, q_type = data_loader.Get_question_answer_pair(line)

            executor.memory = CGMemory()
            agent_executor = get_agent()
            resp = agent_executor.invoke({"input": q})
            intermediate_steps = resp["intermediate_steps"]
            print(resp)
            # print(intermediate_steps)
            reasoning_steps = []
            final_answer = ""
            for step in intermediate_steps:
                if isinstance(step, tuple) and len(step) == 2:
                    agent_action, observation = step
                    if isinstance(agent_action, AgentAction):
                        step_data = {
                            "thought": agent_action.log,  # Record thought process
                            "action": agent_action.tool,  # Record called tool
                            "action_input": agent_action.tool_input,  # Record tool input
                            "observation": observation  # Record tool result
                        }
                        reasoning_steps.append(step_data)
                        json_data = json.dumps({"message": step_data['thought']})
                        yield f"data: {json_data}\n\n"
                        string = "Observation: " + step_data['observation']
                        json_data = json.dumps({"message": string})
                        yield f"data: {json_data}\n\n"
                elif isinstance(step, AgentFinish):
                    final_answer = step.return_values["output"]
                    string = "Final Answer: " + final_answer
                    json_data = json.dumps({"message": string})
                    yield f"data: {json_data}\n\n"


            # Print reasoning process (for debugging)
            for i, step in enumerate(reasoning_steps):
                print(f"Step {i+1}:")
                print(f"Thought: {step['thought']}")
                print(f"Action: {step['action']}")
                print(f"Input: {step['action_input']}")
                print(f"Observation: {step['observation']}")

            executor.memory.clear()
            line['output'] = resp['output']
            with open(out_file_path, 'a+', encoding='utf-8') as f:
                json.dump(line, f, ensure_ascii=False)
                f.write('\n')

        json_data = json.dumps({"message": "done"})
        yield f"data: {json_data}\n\n"

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
    }
    return Response(stream(), headers=headers)

@app.route('/llmgraph', methods=['GET'])
def get_llm_graph():
    adj_matrix = np.array([[0, 0, 0, 0, 0, 0, 0, 0], 
                           [1, 0, 1, 1, 1, 1, 0, 0],
                           [1, 0, 0, 1, 1, 1, 0, 0],
                           [1, 0, 0, 0, 0, 1, 0, 0],
                           [1, 0, 0, 0, 0, 1, 0, 0],
                           [1, 0, 0, 0, 0, 0, 0, 0],
                           [1, 1, 1, 1, 1, 1, 0, 0],
                           [1, 1, 1, 0, 0, 0, 0, 0]])
    # print(adj_matrix)
    # 将邻接矩阵转换为列表
    adj_matrix_list = adj_matrix.tolist()

    # 返回 JSON 响应
    return jsonify(adj_matrix_list)
    
if __name__ == '__main__':
    app.run()


import pandas as pd
import numpy as np
from causallearn.search.ConstraintBased.PC import pc
from causallearn.utils.cit import CIT
from causallearn.utils.cit import fisherz
import json
import os
import io
import warnings
import matplotlib
from econml.dml import LinearDML
from tools.util import has_confounder, has_collider, Relationship
from tools.gpt_api import ChatGPT
warnings.filterwarnings("ignore")
matplotlib.use('TkAgg')


car_elements = [
    "mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model year", "origin"
]

def condition_independent_test(input_str):
    '''
    Args:
        input_str: json string
        {
            "filename":..., # filename for the data
            "interesting_var":[...], # the variables that user whats to test on
            "condition":[...] # condition variables
        }
    '''
    try:
        print(input_str)
        input_str = json.loads(input_str)
        index = input_str['interesting_var']
        filename = input_str['filename']
        condition = None if input_str['condition'] == "None" or [] else input_str['condition']
        postfix = ''
        if condition is not None:
            postfix = 'under conditions : ' + ','.join(condition)

        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
        parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
        file_path = os.path.join(parent_dir, filename)  # 拼接成绝对路径
        data_sum = pd.read_csv(file_path, na_values=['?'], header=None)
        data_sum.columns = car_elements
        data_sum = data_sum.dropna()
        data = data_sum.loc[:, data_sum.columns.isin(index)]
        data.columns = index
        cit = CIT(data=np.array(data), method='fisherz')
        pValue = cit(data.columns.get_loc(index[0]), data.columns.get_loc(index[1]),
                     [data.columns.get_loc(col) for col in condition] if condition is not None else None)

        if pValue < 0.05:
            return '''{} and {} is independent'''.format(index[0], index[1])+postfix
        else:
            return '''{} and {} is  not independent'''.format(index[0], index[1])+postfix
    except Exception as e:
        return f"tool raise a error :{e}. please check your input format and input variables."

# def draw_pydot(pyd):
#     tmp_png = pyd.create_png(f="png")
#     fp = io.BytesIO(tmp_png)
#     img = mpimg.imread(fp, format='png')
#     plt.rcParams["figure.figsize"] = [20, 12]
#     plt.rcParams["figure.autolayout"] = True
#     plt.axis('off')
#     plt.imshow(img)
#     plt.show()


def generate_causalgraph(input_str, memory):
    '''
    Args:
        input_str: json string
        {
            "filename":..., # filename for the data
            "analyse_relationship":..., # True for complete causal graph, False for partial causal graph
            "interesting_var":[...], # when generate partial causal graph, it's values are list of variables appear in causal graph.
        }
        memory: store the generated causal graph
    '''
    try:
        print("\n" + input_str)
        input_str = json.loads(input_str)
        filename = input_str['filename']
        method = input_str['method'] if 'method' in input_str.keys() else 'pc'
        interested_var = input_str['interesting_var'] if 'interesting_var' in input_str.keys() else None
        analyse_relationship = input_str['analyse_relationship'] if 'analyse_relationship' in input_str.keys() else None
        config = input_str['config'] if 'config' in input_str.keys() else None
        print(config)
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
        parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
        file_path = os.path.join(parent_dir, filename)  # 拼接成绝对路径
        data_sum = pd.read_csv(file_path, na_values=['?'], header=None)
        data_sum.columns = car_elements
        data_sum = data_sum.dropna()
        # data = np.array(data_sum)
        if interested_var is not None and interested_var != [] and analyse_relationship == "False":
            data = data_sum.loc[:, data_sum.columns.isin(interested_var)]
            data.columns = interested_var
            data = np.array(data)
            cg = pc(data, 0.05, fisherz, node_names=interested_var)
        else:
            data = np.array(data_sum)
            cg = pc(data, 0.05, fisherz, node_names=car_elements)
            # cg.draw_pydot_graph()
        name = memory.Get_name(filename)
        memory.add(name, cg)
        file_name = "tempCG.txt"
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
        parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
        file_path = os.path.join(parent_dir, file_name)  # 拼接成绝对路径
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(str(cg.G))
        return f"causal graph named '{name}' is generate succeed! and have written to the memory, you can use {name} as parameter 'cg_name' "
    except Exception as e:
        return str(e)


def prase_data(config, filename):
    Y_name = config['Y'] if 'Y' in config.keys() and config['Y'] != [] else None
    Z_name = config['Z'] if 'Z' in config.keys() and config['Z'] != [] else None
    T_name = config['T'] if 'T' in config.keys() and config['T'] != [] else None
    W_name = config['W'] if 'W' in config.keys() and config['W'] != [] else None
    X_name = config['X'] if 'X' in config.keys() and config['X'] != [] else None
    assert Y_name is not None and T_name is not None
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
    file_path = os.path.join(parent_dir, filename)  # 拼接成绝对路径
    data = pd.read_csv(file_path, na_values=['?'], header=None)
    data.columns = car_elements
    data = data.dropna()
    T_mat = data[T_name] if T_name is not None else None
    Y_mat = data[Y_name] if Y_name is not None else None
    Z_mat = data[Z_name] if Z_name is not None else None
    W_mat = data[W_name] if W_name is not None else None
    X_mat = data[X_name] if X_name is not None else None
    return T_mat, Y_mat, Z_mat, W_mat, X_mat,config['T0'],config['T1']


def ATE_sim(input_str):
    '''
    Args:
        input_str: json string
        {
            "filename":..., # filename for the data
            "config":
            {
                Y:[...],  # outcome variable
                T:[...],  # treatment variable
                X:[...],  # covariate variable
                T0:...,   # treatment value T0
                T1:...    # treatment value T1
            } # config for the data
        }
    '''
    try:
        print("\n" + input_str)
        input_str = json.loads(input_str)
        filename = input_str['filename']
        config = input_str['config']

        # T0 = input_str['T0']
        # T1 = input_str['T1']
        # print(T0,T1)
        T_mat, Y_mat, Z_mat, W_mat, X_mat,T0,T1 = prase_data(config, filename)
        est = LinearDML(random_state=123)
        est.fit(Y_mat,T_mat,X=X_mat,W=W_mat)
        ate = est.ate(T0=T0,T1=T1,X=X_mat)
        return f'ate : E(Y|T1) - E(Y|T0) is {ate}'
    except Exception as e:
        return f"tools error : {str(e)}"


def empty(input_str):
    print(input_str)
    return "this question doesn't need other tools, so you can only answer the question directly."


def Determine_collider(input_str, memory):
    '''
    Args:
        input_str: json string
        {
            "cg_name":..., # generated causal graph name
            "interesting_var":[...] # the variables that user whats to test on
        }
        memory: store the generated causal graph
    '''
    try:
        print("\n" + input_str)
        input_str = json.loads(input_str)
        method = input_str["method"] if 'method' in input_str.keys() else None
        activate_var = input_str['interesting_var']
        filename = None
        cg = None
        if 'cg_name' in input_str.keys():
            filename = input_str["cg_name"]
            cg, rela = memory.get(filename)
            if rela == Relationship.NO:
                return cg
        else:
            return f"missing cg_name parameter.please input cg_name."
        node_names = [str(i) for i in cg.G.nodes]
        index_a = node_names.index(activate_var[0])
        index_b = node_names.index(activate_var[1])
        rela, varlist = has_collider(index_a, index_b, cg.G.graph)

        if rela == Relationship.YES:
            return "There exists at least one collider {} of {} and {} ".format(node_names[varlist[0]],
                                                                                activate_var[0],
                                                                                activate_var[1])
        if rela == Relationship.UNCERTAIN:
            return "Whether there exist collider of {} and {} is uncertain because some edge direction is uncertain.following variables may be collider : ".format(
                activate_var[0], activate_var[1]) + ','.join([node_names[i] for i in varlist])

        return "There don't exists collider between {} and {} ".format(activate_var[0], activate_var[1])
    except Exception as e:
        return f"tool raise error : {e}"


def Determine_confounder(input_str, memory):
    '''
    Args:
        input_str: json string
        {
            "cg_name":..., # generated causal graph name
            "interesting_var":[...] # the variables that user whats to test on
        }
        memory: store the generated causal graph
    '''
    try:
        print("\n" + input_str)
        input_str = json.loads(input_str)
        method = input_str["method"] if 'method' in input_str.keys() else None
        activate_var = input_str['interesting_var']
        filename = None
        cg = None
        if 'cg_name' in input_str.keys():
            filename = input_str["cg_name"]
            cg, rela = memory.get(filename)
            if rela == Relationship.NO:
                return cg
        else:
            return f"missing cg_name parameter.please input cg_name."
        node_names = [str(i) for i in cg.G.nodes]
        index_a = node_names.index(activate_var[0])
        index_b = node_names.index(activate_var[1])
        rela, varlist = has_confounder(index_a, index_b, cg.G.graph)

        if rela == Relationship.YES:
            return "yes，There is an unblocked backdoor path between {} and {} so confounder exists. Backdoor path : ".format(
                varlist[0],
                activate_var[0]) + ','.join([node_names[i] for i in varlist])
        if rela == Relationship.UNCERTAIN:
            paths = ''
            for p in varlist:
                paths += "\n" + ','.join([node_names[i] for i in p])
            return "Whether there exist confounder between {} and {} is uncertain because some edge direction is uncertain.following paths may be backdoor path : ".format(
                activate_var[0], activate_var[1]) + paths
        return "no，No unblocked backdoor paths exist between {} and {}. So don't exist confounder".format(
            activate_var[0], activate_var[1])
    except Exception as e:
        return f"tool raise error : {e}"


def Determine_edge_direction(input_str, memory):
    '''
    Args:
        input_str: json string
        {
            "cg_name":..., # generated causal graph name
            "interesting_var":[...] # the variables that user whats to test on
        }
        memory: store the generated causal graph
    '''
    try:
        print("\n" + input_str)
        input_str = json.loads(input_str)
        filename = None
        cg = None

        if 'cg_name' in input_str.keys():
            filename = input_str["cg_name"]
            cg, rela = memory.get(filename)
            if rela == Relationship.NO:
                return cg
        else:
            return f"missing cg_name parameter.please input cg_name."
        method = input_str["method"] if 'method' in input_str.keys() else None
        activate_var = input_str['interesting_var']
        node_names = [str(i) for i in cg.G.nodes]
        index_a = node_names.index(activate_var[0])
        index_b = node_names.index(activate_var[1])
        a_to_b = cg.G.graph[index_a][index_b]
        b_to_a = cg.G.graph[index_b][index_a]
        prefix = ''
        if a_to_b == -1 and b_to_a == 1:
            return prefix + activate_var[0] + " is a directly cause of " + activate_var[
                1] + ".The opposite is not true"
        elif a_to_b == 1 and b_to_a == -1:
            return prefix + activate_var[1] + " is a cause of " + activate_var[
                0] + ".The opposite is not true"
        elif a_to_b == -1 and b_to_a == -1:
            return prefix + f"An undirected edge exists between  {activate_var[0]} and {activate_var[1]}, which means they are not independent. However, the direction of causality between the two variables is uncertain."
        else:
            return prefix + f"There is no direct edge linking  {activate_var[0]} and {activate_var[1]}.{activate_var[0]} doesn't directly cause {activate_var[1]}."
    except Exception as e:
        return str(e)
    

def parse_dag_from_file(filename):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
        parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
        file_path = os.path.join(parent_dir, filename)  # 拼接成绝对路径
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        nodes = []
        edges = []
        reading_nodes = False
        reading_edges = False

        for line in lines:
            # print("befroe strip",line)
            line = line.strip()
            # print("after strip",line)
            if not line:
                continue
            if line.startswith("Graph Nodes:"):
                reading_nodes = True
            elif reading_nodes:
                nodes = line.split(";")
                reading_nodes = False
            elif line.startswith("Graph Edges:"):
                reading_edges = True
            elif reading_edges:
                if "-->" in line:
                    edge = line.split(".")[1]
                    edge = tuple(map(str.strip, edge.split("-->")))
                    edges.append(edge)
        
        return {"nodes": nodes, "edges": edges}
    
    except Exception as e:
        return {"error": f"Failed to parse file: {str(e)}"}
    

def summarize_dag(input_str):
    '''
    Args:
        input_str: json string
        {
            "filename":..., # filename for the causal graph to summarize
        }
    '''
    try:
        params = json.loads(input_str)
        filename = params.get("filename")
        dag_data = parse_dag_from_file(filename)
        
        if "error" in dag_data:
            return dag_data["error"]
        
        nodes_str = ", ".join(dag_data["nodes"])
        edges_str = "\n".join([f"{src} → {dst}" for src, dst in dag_data["edges"]])
        prompt = f"""
        Given the following DAG structure:

        **Nodes:**
        {nodes_str}

        **Edges:**
        {edges_str}

        Please provide a concise summary of this DAG. 
        Identify key causal relationships, confounders, colliders, and any other important structural insights.
        """
        
        llm = ChatGPT()
        reason, response = llm.call(prompt)
        print(reason)
        
        return response
        
    except Exception as e:
        return str(e)
    
def analyze_dag(input_str):
    """
    Args:
        input_str: json string
        {
            "filename":..., # filename for the causal graph to summarize
        }
    """
    try:
        params = json.loads(input_str)
        filename = params.get("filename")
        dag_data = parse_dag_from_file(filename)
        if "error" in dag_data:
            return dag_data["error"]
        
        nodes_str = ", ".join(dag_data["nodes"])
        edge_analyses = []
        
        for src, dst in dag_data["edges"]:
            prompt = f"""
            We have a directed acyclic graph (DAG) with the following nodes:
            {nodes_str}
            
            Now, let's analyze the causal relationship between "{src}" and "{dst}".
            
            - Is the edge "{src} → {dst}" a reasonable causal connection?
            - If yes, explain why.
            - If no, explain why it may be incorrect or misleading.
            - If uncertain, explain possible conditions under which it could hold.
            """
            
            llm = ChatGPT()  
            reason, response = llm.call(prompt)
            # print(f"Analysis for {src} → {dst}:\n{reason}\n")

            edge_analyses.append({
                "edge": f"{src} → {dst}",
                "analysis": response
            })
        
        return edge_analyses

    except Exception as e:
        return str(e)


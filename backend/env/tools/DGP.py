import json
import os
from tools.gpt_api import ChatGPT

question_CG = {
    "IT":
        "A study on vehicle fuel efficiency aims to analyze how engine characteristics (**cylinders**, **displacement**, **horsepower**), vehicle **weight**, **acceleration**, **model year**, and **origin** influence miles per gallon (**mpg**). The dataset includes these variables, and preliminary analysis suggests potential confounding relationships. To refine the causal model, it is critical to assess dependencies among variables. **Q: Is {} independent of {}?**",
    "CIT":
        "A automotive researcher is analyzing historical vehicle data to model fuel efficiency determinants, examining variables like engine specifications (**cylinders**, **displacement**, **horsepower**), vehicle characteristics (**weight**, **acceleration**), production details (**model year**, **origin**), and performance metrics (**mpg**). The dataset includes these variables. In the process of causal reasoning, they noticed that some variables may confuse the relationships between other variables. So they want to test the conditional independence between variables. **Q: Is {} independent of {} given condition {}?**",
    "MULTCIT":
        "A automotive researcher is analyzing historical vehicle data to model fuel efficiency determinants, examining variables like engine specifications (**cylinders**, **displacement**, **horsepower**), vehicle characteristics (**weight**, **acceleration**), production details (**model year**, **origin**), and performance metrics (**mpg**). The dataset includes these variables. In the process of causal reasoning, they noticed that some variables may confuse the relationships between other variables. So they want to test the conditional independence between variables. **Q: whether {} and {} is independent under conditions: ",
    "CAUSE":
        "When analyzing vehicle performance data containing variables like **mpg**, **cylinders**, **displacement**, **horsepower**, **weight**, **acceleration**, **model year**, and **origin**, a key step involves mapping causal relationships to determine the impact relationship between variables. For example, **displacement** may be the direct cause of **cylinders**, and **weight** may be the direct cause of **horsepower**. I want to explore the causal direction between some interesting variables. **Q: Assess if {} has a direct causal impact on {}.**",
    "Has-Collider":
        "When analyzing vehicle performance data containing variables like **mpg**, **cylinders**, **displacement**, **horsepower**, **weight**, **acceleration**, **model year**, and **origin**, a key step involves mapping causal relationships to avoid biased inferences. During causal graph construction, I notice potential interdependencies between variables. To properly adjust for collider bias, I must identify if any variable acts as a common effect of another two variables. **Q: Whether there exists at least one collider (i.e., common effect) of {} and {}?**",
    "Has-Confounder":
        "When analyzing vehicle performance data containing variables like **mpg**, **cylinders**, **displacement**, **horsepower**, **weight**, **acceleration**, **model year**, and **origin**, a key step involves mapping causal relationships to avoid biased inferences. During causal graph construction, I notice potential interdependencies between variables. To properly adjust for confounding bias, I must identify if any variable acts as a common cause of another two variables. **Q: Whether there exists at least one confounder (i.e., common cause) of {} and {}?**",
    "CAUSALKG":
        "Analyzing vehicle performance data, we examine relationships between engine characteristics (**cylinders**, **displacement**, **horsepower**), vehicle properties (**weight**, **acceleration**), environmental factors (**mpg**), and contextual variables (**model year**, **origin**). Engine parameters like **displacement** and **horsepower** are likely influenced by **cylinder** count, while **weight** and **acceleration** may mediate effects on fuel efficiency. **Model year** and **origin** could act as external confounders, reflecting technological advancements or regional design preferences. We want to disentangle these interactions. **Q: Please generate causal graph of the input tabular data.**",
    "PARTIAL_CG":
        "When analyzing vehicle performance data containing variables like **mpg**, **cylinders**, **displacement**, **horsepower**, **weight**, **acceleration**, **model year**, and **origin**, a key step involves causal graph construction. Sometimes, generating a causal diagram that includes all variables may not be conducive to observing certain local features. **Q: Please generate a partial causal diagram for some of the following variables that interest me: ",
    "ATE":
        "A automotive researcher is analyzing historical vehicle data to model fuel efficiency determinants, examining variables like engine specifications (**cylinders**, **displacement**, **horsepower**), vehicle characteristics (**weight**, **acceleration**), production details (**model year**, **origin**), and performance metrics (**mpg**). The dataset includes these variables. They want to evaluate the causal effects between variables. **Q: Calculate the Average Treatment Effect (ATE) of a continuous treatment variable {T} on an outcome variable {Y}, given that the treatment {T} change from {T0} to {T1}.**"
}

question_content = {
    "IT": "Is {} independent of {}?",
    "CIT": "Is {} independent of {} given condition {}?",
    "MULTCIT": "Whether {} and {} is independent under conditions: ",
    "CAUSE": "Assess if {} has a direct causal impact on {}.",
    "Has-Collider": "Whether there exists at least one collider (i.e., common effect) of {} and {}?",
    "Has-Confounder": "Whether there exists at least one confounder (i.e., common cause) of {} and {}?",
    "CAUSALKG": "Please generate causal graph of the input tabular data.",
    "PARTIAL_CG": "Please generate a partial causal diagram for some of the following variables that interest me: ",
    "ATE": "Calculate the Average Treatment Effect (ATE) of a continuous treatment variable {T} on an outcome variable {Y}, given that the treatment {T} change from {T0} to {T1}."
}

# prompt_template = '''
# ##Requirements: Suppose you are a statistician and need to perform causal analysis on data. You need to use your imagination to compile a reasonable scene description based on the following elements, and finally ask a question Q: " {} ". The scenario description needs to be related to the problem and form a paragraph together with the problem. This output must directly end up with the question Q. Below are all the elements you need to use to describe the scenario (including those involved in the  question Q). Elements don't exist in variables listed below are not allowed.

# ##element:[{}]

# ##Output:
# '''

car_elements = [
    "mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model year", "origin"
]

def generate_description(type, interesting, T0, T1):
    file_name = "dataset.jsonl"
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
    file_path = os.path.join(parent_dir, file_name)  # 拼接成绝对路径
    node_num = len(car_elements)

    description = question_CG[type]
    question = question_content[type]
    if type in ["IT","CAUSE","Has-Collider","Has-Confounder"]:
        text = description.format(interesting[0],interesting[1])
        Q = question.format(interesting[0],interesting[1])
        one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': text,'file':"new.csv",'Q':Q}
        print(text)
        print(Q)
        with open(file_path,'a+', encoding='utf-8') as f:
            json.dump(one_item, f, ensure_ascii=False)
            f.write('\n')
    if type in ["CIT"]:
        text = description.format(interesting[0],interesting[1],interesting[2])
        Q = question.format(interesting[0],interesting[1],interesting[2])
        one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': text,'file':"new.csv",'Q':Q}
        print(text)
        print(Q)
        with open(file_path,'a+', encoding='utf-8') as f:
            json.dump(one_item, f, ensure_ascii=False)
            f.write('\n')
    if type in ["MULTCIT"]:
        text = description.format(interesting[0],interesting[1]) + ','.join(interesting[2:]) + "?**"
        Q = question.format(interesting[0],interesting[1]) + ','.join(interesting[2:])
        one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': text,'file':"new.csv",'Q':Q}
        print(text)
        print(Q)
        with open(file_path,'a+', encoding='utf-8') as f:
            json.dump(one_item, f, ensure_ascii=False)
            f.write('\n')
    if type in ["CAUSALKG"]:
        text = description
        Q = question
        one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': text,'file':"new.csv",'Q':Q}
        print(text)
        print(Q)
        with open(file_path,'a+', encoding='utf-8') as f:
            json.dump(one_item, f, ensure_ascii=False)
            f.write('\n')
    if type in ["PARTIAL_CG"]:
        text = description + ','.join(interesting) + "?**"
        Q = question + ','.join(interesting)
        one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': text,'file':"new.csv",'Q':Q}
        print(text)
        print(Q)
        with open(file_path,'a+', encoding='utf-8') as f:
            json.dump(one_item, f, ensure_ascii=False)
            f.write('\n')
    if type in ["ATE"]:
        text = description.format(T=interesting[0], Y=interesting[1],T0=T0,T1=T1)
        Q = question.format(T=interesting[0], Y=interesting[1],T0=T0,T1=T1)
        one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': text,'file':"new.csv",'Q':Q}
        print(text)
        print(Q)
        with open(file_path,'a+', encoding='utf-8') as f:
            json.dump(one_item, f, ensure_ascii=False)
            f.write('\n')


# def generate_description(type, interesting, T0, T1):
#     gpt = ChatGPT()
#     file_name = "dataset.jsonl"
#     current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
#     parent_dir = os.path.dirname(current_dir)  # 获取当前脚本所在目录的上级目录
#     file_path = os.path.join(parent_dir, file_name)  # 拼接成绝对路径
#     node_num = len(car_elements)
#     for item in question_CG[type]:
#         if type in ["IT","CAUSE","Has-Collider","Has-Confounder"]:
#             question = item.format(interesting[0],interesting[1])
#             prompt = prompt_template.format(question,','.join(car_elements))
#             resp = gpt.call(prompt)
#             print(resp)
#             one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': resp,'file':"new.csv",'Q':question}
#             with open(file_path,'a+', encoding='utf-8') as f:
#                 json.dump(one_item, f, ensure_ascii=False)
#                 f.write('\n')
#         if type in ["CIT"]:
#             question = item.format(interesting[0],interesting[1],interesting[2])
#             prompt = prompt_template.format(question,','.join(car_elements))
#             resp = gpt.call(prompt)
#             print(resp)
#             one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': resp,'file':"new.csv",'Q':question}
#             with open(file_path,'a+', encoding='utf-8') as f:
#                 json.dump(one_item, f, ensure_ascii=False)
#                 f.write('\n')
#         if type in ["MULTCIT"]:
#             question = item.format(interesting[0],interesting[1]) + ','.join(interesting[2:])
#             prompt = prompt_template.format(question,','.join(car_elements))
#             resp = gpt.call(prompt)
#             print(resp)
#             one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': resp,'file':"new.csv",'Q':question}
#             with open(file_path,'a+', encoding='utf-8') as f:
#                 json.dump(one_item, f, ensure_ascii=False)
#                 f.write('\n')
#         if type in ["CAUSALKG"]:
#             question = item
#             prompt = prompt_template.format(question,','.join(car_elements))
#             resp = gpt.call(prompt)
#             print(resp)
#             one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': resp,'file':"new.csv",'Q':question}
#             with open(file_path,'a+', encoding='utf-8') as f:
#                 json.dump(one_item, f, ensure_ascii=False)
#                 f.write('\n')
#         if type in ["PARTIAL_CG"]:
#             question = item + ','.join(interesting)
#             prompt = prompt_template.format(question,','.join(car_elements))
#             resp = gpt.call(prompt)
#             print(resp)
#             one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': resp,'file':"new.csv",'Q':question}
#             with open(file_path,'a+', encoding='utf-8') as f:
#                 json.dump(one_item, f, ensure_ascii=False)
#                 f.write('\n')
#         if type in ["ATE"]:
#             question = item.format(T=interesting[0], Y=interesting[1],T0=T0,T1=T1)
#             prompt = prompt_template.format(question, ','.join(car_elements))
#             resp = gpt.call(prompt)
#             print(resp)
#             one_item = {'node num':node_num,'question_type':type,'interest':interesting,'variables':car_elements,'text': resp,'file':"new.csv",'Q':question}
#             with open(file_path,'a+', encoding='utf-8') as f:
#                 json.dump(one_item, f, ensure_ascii=False)
#                 f.write('\n')
<template>
  <div class="chat-container">
    <div class="chat-box">
      <!-- 聊天记录显示区域 -->
      <div class="chat-messages">
        <div v-for="(message, index) in messages" :key="index" :class="message.from === 'user' ? 'user-message' : 'model-message'">
          <p><strong>{{ message.from === 'user' ? 'You' : 'Model' }}:</strong></p>
          <pre>{{ message.text }}</pre>
        </div>
      </div>
      
      <!-- 用户输入区域 -->
      <div class="chat-input">
        <input v-model="inputType" placeholder="Type" />
        <input v-model="inputInteresting" placeholder="Interesting" />
        <input v-model="inputT0" placeholder="T0" />
        <input v-model="inputT1" placeholder="T1" />
        <button @click="sendMessage">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      messages: [],        
      inputType: '',       
      inputInteresting: '', 
      inputT0: '',         
      inputT1: '',         
      eventSource: null,   
      currentModelIndex: null, 
    };
  },
  methods: {
    formatToArray(input) {
      return input.trim() ? input.split(',').map(item => item.trim()) : [];
    },

    parseToFloat(input) {
      const num = parseFloat(input);
      return isNaN(num) ? null : num;
    },

    connectToSSE() {
      this.eventSource = new EventSource('http://localhost:5001/agent');

      this.eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);  
        console.log('Received from SSE:', data);  
        
        if (data.message !== 'done') {  
          if (this.currentModelIndex === null) {
            this.messages.push({ from: 'model', text: data.message });
            this.currentModelIndex = this.messages.length - 1;
          } else {
            this.messages[this.currentModelIndex].text += "\n" + data.message;
          }
        } else {
          this.currentModelIndex = null;
          this.eventSource.close();
        }
      };
      
      this.eventSource.onerror = (error) => {
        if (this.eventSource.readyState === EventSource.CLOSED) {
          console.log('Connection to server closed');
        } else {
          console.error('Error occurred:', error);
        }
      };
    },
    
    sendMessage() {
      let queryData = {};
      if (
        this.inputType.trim() || 
        this.inputInteresting.trim() || 
        this.inputT0.trim() || 
        this.inputT1.trim()
      ) {
        queryData = {
          type: this.inputType.trim(),  // 保持字符串
          interesting: this.formatToArray(this.inputInteresting), // 转换为数组
          T0: this.parseToFloat(this.inputT0), // 转换为浮点数
          T1: this.parseToFloat(this.inputT1)  // 转换为浮点数
        };

        console.log(queryData); // 调试，检查数据格式是否正确

        let question = null;
        if (queryData.type === "IT") {
          question = `Is ${queryData.interesting[0]} independent of ${queryData.interesting[1]}?`;
        }
        if (queryData.type === "CIT") {
          question = `Is ${queryData.interesting[0]} independent of ${queryData.interesting[1]} given condition ${queryData.interesting[2]}?`;
        }
        if (queryData.type === "MULTCIT") {
          let conditionsContent = queryData.interesting.slice(2).join(", ");  // 获取从索引2及之后的内容，并用逗号连接
          question = `whether ${queryData.interesting[0]} and ${queryData.interesting[1]} is independent under conditions: ${conditionsContent}?`;
        }
        if (queryData.type === "CAUSE") {
          question = `Assess if ${queryData.interesting[0]} has a direct causal impact on ${queryData.interesting[1]}.`;
        }
        if (queryData.type === "Has-Collider") {
          question = `Whether there exists at least one collider (i.e., common effect) of ${queryData.interesting[0]} and ${queryData.interesting[1]}?`;
        }
        if (queryData.type === "Has-Confounder") {
          question = `Assess if ${queryData.interesting[0]} and ${queryData.interesting[1]} share at least one confounding factor (common cause).`;
        }
        if (queryData.type === "CAUSALKG") {
          question = `please generate a causal graph of the variables.`;
        }
        if (queryData.type === "PARTIAL_CG") {
          question = `Please generate a partial causal diagram for some of the following variables that interest me: ${queryData.interesting}`;
        }
        if (queryData.type === "ATE") {
          question = `calculate the Average Treatment Effect (ATE) of a continuous treatment variable ${queryData.interesting[0]} on an outcome variable ${queryData.interesting[1]}, given that the treatment ${queryData.interesting[0]} change from ${queryData.T0} to ${queryData.T1}.`;
        }
        this.messages.push({ from: 'user', text: question });
        this.messages.push({ from: 'model', text: '' });
        this.currentModelIndex = this.messages.length - 1;

        this.inputType = '';
        this.inputInteresting = '';
        this.inputT0 = '';
        this.inputT1 = '';

        fetch('http://localhost:5001/dgp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(queryData)
        })
        .then(response => response.json())  // 解析 JSON 响应
        .then(data => {
          console.log("Response:", data);
          this.connectToSSE();  
        })
        .catch(error => {
          console.error('Error sending message:', error);
        });
      }
    },
  },
  beforeDestroy() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  justify-content: center;
  height: 100vh;
}

.chat-box {
  width: 350px;
  height: 730px;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  border-bottom: 1px solid #ddd;
}

.chat-messages pre {
  white-space: pre-wrap;   /* 保留换行符，并且文本会自动换行 */
  word-wrap: break-word;   /* 防止单词超出容器宽度 */
  overflow-wrap: break-word; /* 兼容性处理 */
  word-break: break-word;  /* 确保超出宽度时单词能换行 */
  max-width: 100%; /* 防止超出父容器的宽度 */
  margin: 0; /* 移除默认的预设边距 */
}

.user-message {
  background-color: #d4f5c3;
  padding: 5px;
  margin: 5px 0;
  border-radius: 5px;
}

.model-message {
  background-color: #f0f0f0;
  padding: 5px;
  margin: 5px 0;
  border-radius: 5px;
}

.chat-input {
  display: flex;
  flex-direction: column;
  padding: 10px;
  background-color: #f9f9f9;
}

.chat-input input {
  padding: 10px;
  margin: 5px 0;
  border: 1px solid #ccc;
  border-radius: 10px;
}

.chat-input button {
  padding: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 10px;
}

.chat-input button:hover {
  background-color: #45a049;
}
</style>

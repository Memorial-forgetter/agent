<template>
  <div>
    <div class="container">
      <!-- Chat 部分 -->
      <div class="box chat">
        <div class="box-title">Chat</div>
        <Chat />
      </div>

      <!-- LLM Graph 部分 -->
      <div class="box llm-graph">
        <div class="box-title">LLM Graph</div>
        <LLMGraph />
      </div>

      <!-- Data Graph 部分 -->
      <div class="box data-graph">
        <div class="box-title">Data Graph</div>
        <DataGraph />
      </div>

      <!-- Data Table 部分 -->
      <div class="box data-table">
        <div class="box-title">Data Table</div>
        <DataTable />
      </div>
    </div>
  </div>
</template>

<script>
// 导入 DataGraph 组件
import DataGraph from './components/DataGraph.vue';
import Chat from './components/Chat.vue';
import LLMGraph from './components/LLMGraph.vue';
import DataTable from './components/DataTable.vue';

export default {
  name: 'App',
  components: {
    DataGraph,  // 注册 DataGraph 组件
    Chat,
    LLMGraph,
    DataTable
  }
};
</script>

<style scoped>
/* 页面整体样式 */
body, html {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: #fff;
  height: 100%; 
  width: 100%;  
}

.container {
  display: grid;
  grid-template-columns: 310px 410px 410px;
  grid-template-rows: 500px 280px;      
  gap: 10px;
  padding: 10px 0;
  height: 100vh; 
  width: 100%;   
}

.box {
  border: 1px solid #6A0DAD;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.box-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.box.chat {
  grid-column: 1;
  grid-row: 1 / span 2;
}

.box.llm-graph {
  grid-column: 2;
  grid-row: 1;
}

.box.data-graph {
  grid-column: 3;
  grid-row: 1;
}

.box.data-table {
  grid-column: 2 / span 2;
  grid-row: 2;
}
</style>

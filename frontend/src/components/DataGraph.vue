<template>
  <div>
    <!-- <h3>Data Graph</h3> -->
    <div ref="graphContainer" style="height: 400px; width: 100%;"></div>
  </div>
</template>

<script>
import axios from 'axios';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// 注册 dagre 插件
cytoscape.use(dagre);

export default {
  name: 'DataGraph',
  data() {
    return {
      adjMatrix: [],  // 邻接矩阵
    };
  },
  mounted() {
    // 从后端获取因果图邻接矩阵
    const path = 'http://localhost:5001/datagraph';
    axios.get(path)
      .then(response => {
        this.adjMatrix = response.data;
        this.createGraph();  // 创建因果图
      })
      .catch(error => {
        console.error('Error loading causal graph:', error);
      });
  },
  methods: {
    createGraph() {
      const nodeNames = ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration', 'model year', 'origin'];  // 结点名称

      // 创建结点和边
      const nodes = this.adjMatrix.map((_, index) => ({
        data: { 
          id: `X${index + 1}`, 
          name: nodeNames[index]  // 为每个结点添加名称
        }
      }));

      const edges = [];
      for (let i = 0; i < this.adjMatrix.length; i++) {
        for (let j = 0; j < this.adjMatrix[i].length; j++) {
          if (this.adjMatrix[i][j] === 1) {
            edges.push({
              data: { source: `X${i + 1}`, target: `X${j + 1}` }
            });
          }
        }
      }

      // 使用 Cytoscape.js 绘制图形
      cytoscape({
        container: this.$refs.graphContainer,
        elements: [
          ...nodes,
          ...edges
        ],
        style: [
          {
            selector: 'node',
            style: {
              'background-color': '#0074D9',
              'label': 'data(name)',  
              'color': 'black',
              'text-valign': 'center',
              'text-halign': 'center',
              'width': 40,
              'height': 30,
              'text-margin-x': 20,  // 标签和节点的水平距离
              'text-margin-y': -30,  // 标签和节点的垂直距离
              'font-size': 20  // 字体大小
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': 'red',
              'target-arrow-color': 'red',
              'target-arrow-shape': 'triangle',  // 箭头形状
              'curve-style': 'bezier'  // 弯曲样式
            }
          }
        ],
        layout: {
          name: 'dagre', // 使用 dagre 布局
          rankDir: 'TB', // 方向: 'TB'（自上而下），'LR'（从左到右）
          nodeSep: 50,   // 节点间距
          edgeSep: 30,   // 边间距
          rankSep: 100   // 层级间距
        }
      });
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>

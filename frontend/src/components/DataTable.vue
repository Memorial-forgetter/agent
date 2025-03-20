<template>
  <div class="data-graph-container">
    <div v-for="field in fields" :key="field" :ref="`graphContainer-${field}`" class="bar-chart" style="height: 200px; flex: 1; margin-right: 10px; margin-top: 10px;">
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import * as d3 from 'd3';

export default {
  name: 'DataTable',
  data() {
    return {
      data: [], // 原始数据
      fields: ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration', 'model year', 'origin'], // 原始数据的字段
    };
  },
  mounted() {
    // 从后端获取原始数据
    const path = 'http://localhost:5001/datatable';
    axios.get(path)
      .then(response => {
        this.data = response.data;
        this.fields.forEach(field => {
          this.createBarChart(field); // 为每个字段绘制柱形图
        });
      })
      .catch(error => {
        console.error('Error loading data:', error);
      });
  },
  methods: {
    createBarChart(field) {
      const max = d3.max(this.data, d => d[field]);
      const min = d3.min(this.data, d => d[field]);

      const bins = d3.histogram()
        .domain([min, max])
        .thresholds(5)
        .value(d => d[field])(this.data);

      const width = this.$refs[`graphContainer-${field}`][0].clientWidth;
      const height = 180;
      const margin = { top: 20, right: 0, bottom: 0, left: 0 }; // 预留空间用于标题

      d3.select(this.$refs[`graphContainer-${field}`]).html('');

      const svg = d3.select(this.$refs[`graphContainer-${field}`][0])
        .append('svg')
        .attr('width', width)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const x = d3.scaleBand()
        .domain(bins.map((d, i) => `${d.x0} - ${d.x1}`))
        .range([0, width - margin.left - margin.right])
        .padding(0.1);

      const y = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)])
        .nice()
        .range([height, 0]);

      const tooltip = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .style('position', 'absolute')
        .style('background', 'rgba(0,0,0,0.6)')
        .style('color', 'white')
        .style('padding', '5px')
        .style('border-radius', '5px')
        .style('visibility', 'hidden');

      svg.selectAll('.bar')
        .data(bins)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(`${d.x0} - ${d.x1}`))
        .attr('y', d => y(d.length))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.length))
        .attr('fill', '#69b3a2')
        .on('mouseover', (event, d) => {
          tooltip.style('visibility', 'visible')
            .text(`区间: ${d.x0.toFixed(1)} - ${d.x1.toFixed(1)} | 样本数量: ${d.length}`);
        })
        .on('mousemove', (event) => {
          tooltip.style('top', `${event.pageY + 10}px`)
            .style('left', `${event.pageX + 10}px`);
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
        });

      // 添加图表名称（标题）
      svg.append('text')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', -5) // 放在顶部
        .attr('text-anchor', 'middle')
        .style('font-size', '11px')
        .style('font-weight', 'bold')
        .text(field.toUpperCase());

      // 添加 X 轴（隐藏刻度）
      svg.append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(x).tickSize(0).tickFormat('')) // 设 tickSize(0) 隐藏刻度，tickFormat('') 隐藏标签
        .selectAll('path')
        .style('stroke', 'black'); // 仅显示坐标轴线

      // 添加 Y 轴（隐藏刻度）
      svg.append('g')
        .call(d3.axisLeft(y).tickSize(0).tickFormat(''))
        .selectAll('path')
        .style('stroke', 'black'); // 仅显示坐标轴线
    }
  }
};
</script>

<style scoped>
.data-graph-container {
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.bar-chart {
  flex: 1; /* 每个柱形图占据相等的宽度 */
  min-width: 50px; /* 设置最小宽度 */
  padding: 10px;
}

/* 样式：Tooltip */
.tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 5px;
  border-radius: 5px;
  visibility: hidden; 
}
</style>

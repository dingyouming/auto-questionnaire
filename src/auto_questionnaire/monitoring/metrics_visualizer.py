import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pandas as pd
from typing import List, Dict
import numpy as np

class MetricsVisualizer:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置基础的图表样式
        plt.rcParams.update({
            'figure.figsize': (12, 6),
            'axes.grid': True,
            'grid.alpha': 0.3,
            'lines.linewidth': 2,
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12
        })
        
    def generate_report(self, metrics_data: dict) -> str:
        if not metrics_data or not any(metrics_data.values()):
            return self._generate_empty_report()
            
        report_dir = os.path.join(self.output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(report_dir, exist_ok=True)
        
        try:
            print(f"\nGenerating report in: {report_dir}")
            print(f"Metrics data keys: {metrics_data.keys()}")
            
            if 'api_calls' in metrics_data:
                print(f"API calls data sample: {metrics_data['api_calls'][0]}")
                
            # 生成所有图表
            self._generate_all_plots(metrics_data, report_dir)
            
            # 生成HTML报告
            report_path = os.path.join(report_dir, 'report.html')
            self._generate_html_report(metrics_data, report_path)
            
            # 验证生成的文件
            print(f"Generated files: {os.listdir(report_dir)}")
            
            return report_dir
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            raise
            
    def _generate_all_plots(self, metrics_data: Dict, report_dir: str):
        # API延迟图表
        if api_calls := metrics_data.get('api_calls'):
            self._create_api_latency_plot(api_calls, report_dir)
            
        # 答案质量图表
        if quality_data := metrics_data.get('answer_quality'):
            self._create_quality_plot(quality_data, report_dir)
            
        # 缓存命中率图表
        if cache_data := metrics_data.get('cache_hits'):
            self._create_cache_plot(cache_data, report_dir)
            
    def _create_api_latency_plot(self, api_calls: List[Dict], report_dir: str):
        try:
            df = pd.DataFrame(api_calls)
            if 'elapsed' not in df.columns or 'timestamp' not in df.columns:
                print(f"Warning: Missing required columns. Available columns: {df.columns}")
                return
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig, ax = plt.subplots()
            ax.plot(df['timestamp'], df['elapsed'], '-o', alpha=0.7)
            ax.set_title('API Response Latency Over Time')
            ax.set_xlabel('Time')
            ax.set_ylabel('Latency (seconds)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            output_path = os.path.join(report_dir, 'api_latency.png')
            print(f"Saving API latency plot to: {output_path}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 验证文件是否成功保存
            if not os.path.exists(output_path):
                print(f"Warning: Failed to save plot to {output_path}")
                
        except Exception as e:
            print(f"Error creating API latency plot: {str(e)}")
            raise
        
    def _create_quality_plot(self, quality_data: List[Dict], report_dir: str):
        df = pd.DataFrame(quality_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig, ax = plt.subplots()
        ax.plot(df['timestamp'], df['score'], '-o', alpha=0.7)
        ax.set_title('Answer Quality Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Quality Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(report_dir, 'answer_quality.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def _create_cache_plot(self, cache_data: List[Dict], report_dir: str):
        df = pd.DataFrame(cache_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.strftime('%H:%M')
        
        fig, ax = plt.subplots()
        ax.bar(df['hour'], df['hit'].astype(int), alpha=0.7)
        ax.set_title('Cache Hit Rate')
        ax.set_xlabel('Time')
        ax.set_ylabel('Hit (1) / Miss (0)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(report_dir, 'cache_hits.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def _generate_html_report(self, metrics_data: Dict, report_path: str):
        summary_stats = self._calculate_summary_stats(metrics_data)
        
        html_content = f"""
        <html>
            <head>
                <title>Performance Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .summary {{ margin: 20px 0; }}
                    .plots {{ display: flex; flex-direction: column; gap: 20px; }}
                    img {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <h1>Performance Report</h1>
                <div class="summary">
                    <h2>Summary Statistics</h2>
                    <ul>
                        <li>Average API Latency: {summary_stats['avg_latency']:.2f}s</li>
                        <li>Cache Hit Rate: {summary_stats['cache_hit_rate']:.2%}</li>
                        <li>Average Answer Quality: {summary_stats['avg_quality']:.2f}</li>
                    </ul>
                </div>
                <div class="plots">
                    <img src="api_latency.png" alt="API Latency">
                    <img src="answer_quality.png" alt="Answer Quality">
                    <img src="cache_hits.png" alt="Cache Hits">
                </div>
            </body>
        </html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content)
            
    def _calculate_summary_stats(self, metrics_data: Dict) -> Dict:
        api_calls = metrics_data.get('api_calls', [])
        cache_hits = metrics_data.get('cache_hits', [])
        quality_data = metrics_data.get('answer_quality', [])
        
        return {
            'avg_latency': np.mean([call['elapsed'] for call in api_calls]) if api_calls else 0,
            'cache_hit_rate': sum(1 for hit in cache_hits if hit['hit']) / len(cache_hits) if cache_hits else 0,
            'avg_quality': np.mean([q['score'] for q in quality_data]) if quality_data else 0
        }
        
    def _generate_empty_report(self) -> str:
        report_dir = os.path.join(self.output_dir, "empty_report")
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, 'report.html')
        with open(report_path, 'w') as f:
            f.write("<h1>No metrics data available</h1>")
            
        return report_dir
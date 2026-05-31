"""
Data Export Module - export analysis results for research.

Exports fractal analysis data in various formats for:
- Scientific papers
- Statistical analysis
- Further processing in other tools
"""

import numpy as np
import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class AnalysisExporter:
    """
    Export fractal analysis data to various formats.
    """

    def __init__(self):
        self._data = {}
        self._metadata = {
            'software': 'Fractal Explorer',
            'version': '3.0',
            'export_time': None,
        }

    def set_fractal_info(self, fractal_name: str,
                         center_re: float, center_im: float,
                         scale: float, max_iterations: int):
        """Set basic fractal parameters."""
        self._data['fractal'] = {
            'name': fractal_name,
            'center_re': center_re,
            'center_im': center_im,
            'scale': scale,
            'max_iterations': max_iterations,
            'zoom_level': 3.5 / scale,
        }

    def set_dimension_data(self, dimension: float, r_squared: float,
                           box_sizes: List[int], box_counts: List[int],
                           theoretical: float = None):
        """Set fractal dimension analysis data."""
        self._data['dimension_analysis'] = {
            'computed_dimension': dimension,
            'r_squared': r_squared,
            'theoretical_dimension': theoretical,
            'box_sizes': box_sizes,
            'box_counts': box_counts,
            'log_inverse_sizes': [-np.log(s) for s in box_sizes] if box_sizes else [],
            'log_counts': [np.log(c) for c in box_counts] if box_counts else [],
        }

    def set_benchmark_data(self, resolutions: List[str],
                           cpu_times: List[float],
                           gpu_times: List[Optional[float]],
                           iterations_test: Dict = None):
        """Set benchmark data."""
        speedups = []
        for cpu, gpu in zip(cpu_times, gpu_times):
            if gpu is not None and gpu > 0:
                speedups.append(cpu / gpu)
            else:
                speedups.append(None)

        self._data['benchmark'] = {
            'resolutions': resolutions,
            'cpu_times_ms': cpu_times,
            'gpu_times_ms': gpu_times,
            'speedups': speedups,
            'iterations_test': iterations_test,
        }

    def set_orbit_data(self, start_re: float, start_im: float,
                       orbit_points: List[tuple], escaped: bool,
                       fractal_type: str):
        """Set orbit trace data."""
        self._data['orbit_analysis'] = {
            'start_point': {'re': start_re, 'im': start_im},
            'fractal_type': fractal_type,
            'escaped': escaped,
            'num_iterations': len(orbit_points),
            'orbit_points': [{'re': p[0], 'im': p[1]} for p in orbit_points],
        }

    def set_render_stats(self, width: int, height: int,
                         render_time_ms: float, backend: str):
        """Set rendering statistics."""
        self._data['render_stats'] = {
            'width': width,
            'height': height,
            'total_pixels': width * height,
            'render_time_ms': render_time_ms,
            'pixels_per_second': (width * height) / (render_time_ms / 1000) if render_time_ms > 0 else 0,
            'backend': backend,
        }

    def export_json(self, filepath: str) -> bool:
        """Export all data to JSON format."""
        try:
            self._metadata['export_time'] = datetime.now().isoformat()

            output = {
                'metadata': self._metadata,
                'data': self._data,
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"JSON export error: {e}")
            return False

    def export_csv_dimension(self, filepath: str) -> bool:
        """Export dimension analysis to CSV."""
        if 'dimension_analysis' not in self._data:
            return False

        try:
            dim_data = self._data['dimension_analysis']

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header with metadata
                writer.writerow(['# Fractal Dimension Analysis'])
                writer.writerow([f"# Fractal: {self._data.get('fractal', {}).get('name', 'Unknown')}"])
                writer.writerow([f"# Computed D: {dim_data['computed_dimension']:.6f}"])
                writer.writerow([f"# R-squared: {dim_data['r_squared']:.6f}"])
                if dim_data['theoretical_dimension']:
                    writer.writerow([f"# Theoretical D: {dim_data['theoretical_dimension']:.6f}"])
                writer.writerow([])

                # Data header
                writer.writerow(['box_size', 'box_count', 'log(1/s)', 'log(N)'])

                # Data rows
                for i in range(len(dim_data['box_sizes'])):
                    writer.writerow([
                        dim_data['box_sizes'][i],
                        dim_data['box_counts'][i],
                        f"{dim_data['log_inverse_sizes'][i]:.6f}",
                        f"{dim_data['log_counts'][i]:.6f}",
                    ])

            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False

    def export_csv_benchmark(self, filepath: str) -> bool:
        """Export benchmark data to CSV."""
        if 'benchmark' not in self._data:
            return False

        try:
            bench = self._data['benchmark']

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Resolution test
                writer.writerow(['# GPU vs CPU Benchmark - Resolution Test'])
                writer.writerow(['resolution', 'cpu_ms', 'gpu_ms', 'speedup'])

                for i, res in enumerate(bench['resolutions']):
                    gpu = bench['gpu_times_ms'][i]
                    speedup = bench['speedups'][i]
                    writer.writerow([
                        res,
                        f"{bench['cpu_times_ms'][i]:.2f}",
                        f"{gpu:.2f}" if gpu else "N/A",
                        f"{speedup:.2f}x" if speedup else "N/A",
                    ])

                # Iterations test
                if bench.get('iterations_test'):
                    writer.writerow([])
                    writer.writerow(['# Iterations Test'])
                    writer.writerow(['iterations', 'cpu_ms', 'gpu_ms'])

                    itest = bench['iterations_test']
                    for i, iters in enumerate(itest['iterations']):
                        gpu = itest['gpu'][i]
                        writer.writerow([
                            iters,
                            f"{itest['cpu'][i]:.2f}",
                            f"{gpu:.2f}" if gpu else "N/A",
                        ])

            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False

    def export_csv_orbit(self, filepath: str) -> bool:
        """Export orbit data to CSV."""
        if 'orbit_analysis' not in self._data:
            return False

        try:
            orbit = self._data['orbit_analysis']

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                writer.writerow(['# Orbit Trace Analysis'])
                writer.writerow([f"# Fractal: {orbit['fractal_type']}"])
                writer.writerow([f"# Start: ({orbit['start_point']['re']}, {orbit['start_point']['im']})"])
                writer.writerow([f"# Escaped: {orbit['escaped']}"])
                writer.writerow([f"# Iterations: {orbit['num_iterations']}"])
                writer.writerow([])

                writer.writerow(['iteration', 're', 'im', 'magnitude'])

                for i, pt in enumerate(orbit['orbit_points']):
                    mag = np.sqrt(pt['re']**2 + pt['im']**2)
                    writer.writerow([i, f"{pt['re']:.10f}", f"{pt['im']:.10f}", f"{mag:.10f}"])

            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False

    def export_latex_table(self, filepath: str, table_type: str = 'dimension') -> bool:
        """Export data as LaTeX table for academic papers."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                if table_type == 'dimension' and 'dimension_analysis' in self._data:
                    self._write_latex_dimension_table(f)
                elif table_type == 'benchmark' and 'benchmark' in self._data:
                    self._write_latex_benchmark_table(f)
                else:
                    return False
            return True
        except Exception as e:
            print(f"LaTeX export error: {e}")
            return False

    def _write_latex_dimension_table(self, f):
        """Write LaTeX dimension table."""
        dim = self._data['dimension_analysis']
        fractal = self._data.get('fractal', {}).get('name', 'Unknown')

        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write(f"\\caption{{Box-counting dimension analysis for {fractal}}}\n")
        f.write("\\begin{tabular}{|c|c|c|c|}\n")
        f.write("\\hline\n")
        f.write("Box size $s$ & Count $N(s)$ & $\\log(1/s)$ & $\\log N$ \\\\\n")
        f.write("\\hline\n")

        for i in range(len(dim['box_sizes'])):
            f.write(f"{dim['box_sizes'][i]} & {dim['box_counts'][i]} & ")
            f.write(f"{dim['log_inverse_sizes'][i]:.4f} & {dim['log_counts'][i]:.4f} \\\\\n")

        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write(f"\\par Computed dimension: $D = {dim['computed_dimension']:.4f}$, ")
        f.write(f"$R^2 = {dim['r_squared']:.4f}$\n")
        if dim['theoretical_dimension']:
            f.write(f"\\par Theoretical: $D = {dim['theoretical_dimension']:.4f}$\n")
        f.write("\\end{table}\n")

    def _write_latex_benchmark_table(self, f):
        """Write LaTeX benchmark table."""
        bench = self._data['benchmark']

        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\caption{GPU vs CPU rendering performance comparison}\n")
        f.write("\\begin{tabular}{|c|c|c|c|}\n")
        f.write("\\hline\n")
        f.write("Resolution & CPU (ms) & GPU (ms) & Speedup \\\\\n")
        f.write("\\hline\n")

        for i, res in enumerate(bench['resolutions']):
            gpu = bench['gpu_times_ms'][i]
            speedup = bench['speedups'][i]
            f.write(f"{res} & {bench['cpu_times_ms'][i]:.2f} & ")
            f.write(f"{gpu:.2f if gpu else 'N/A'} & ")
            f.write(f"{speedup:.1f}$\\times$" if speedup else "N/A")
            f.write(" \\\\\n")

        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")

    def clear(self):
        """Clear all stored data."""
        self._data = {}


# Global exporter instance
_exporter = AnalysisExporter()


def get_exporter() -> AnalysisExporter:
    """Get the global exporter instance."""
    return _exporter

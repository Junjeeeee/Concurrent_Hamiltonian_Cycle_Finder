import re
import matplotlib.pyplot as plt
import csv
from collections import defaultdict

# Função para processar o arquivo
def process_file(file_path):
    results = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    current_graph = None
    nexte = "None"
    threads = -1
    for line in lines:
        if "Processando" in line:
            match = re.search(r'Processando .* do arquivo (\S+)', line)
            if match:
                current_graph = match.group(1)
                if current_graph not in results:
                    results[current_graph] = {"sequencial": [], "concorrente": defaultdict(list)}
        elif "Codigo sequencial" in line and current_graph:
            nexte = "Sequencial"
        elif "Codigo concorrente" in line and current_graph:
            match_threads = re.search(r"com\s+(\d+)\s+threads", line)
            threads = int(match_threads.group(1))
            nexte = "Concorrente"
        elif "Tempo" in line:
            match = re.search(r"Tempo total: ([0-9.]+)", line)
            if match:
                if nexte == "Sequencial":
                    results[current_graph]["sequencial"].append(float(match.group(1)))
                elif nexte == "Concorrente":
                    time = float(match.group(1))
                    results[current_graph]["concorrente"][threads].append(time)
    return results

# Função para calcular médias dos tempos
def calculate_averages(results_list):
    averaged_results = {}
    for graph in results_list[0]:  # Assumimos que todos os arquivos têm os mesmos grafos
        averaged_results[graph] = {"sequencial": 0, "concorrente": {}}
        # Média do tempo sequencial
        seq_times = [time for result in results_list for time in result[graph]["sequencial"]]
        averaged_results[graph]["sequencial"] = sum(seq_times) / len(seq_times)
        # Média do tempo concorrente para cada thread
        threads_to_include = {1, 2, 4, 8, 16}
        for thread in threads_to_include:
            thread_times = [time for result in results_list if thread in result[graph]["concorrente"] for time in result[graph]["concorrente"][thread]]
            if thread_times:
                averaged_results[graph]["concorrente"][thread] = sum(thread_times) / len(thread_times)
    return averaged_results

# Função para formatar os nomes dos grafos
def format_graph_name(graph):
    graph_cleaned = re.sub(r'.*/', '', graph)  # Remove o caminho
    if "22_no_limit" in graph_cleaned:
        return "100 grafos com 22 vértices sem limite de arestas"
    elif "random_sizes" in graph_cleaned:
        return "100 grafos com tamanhos aleatórios"
    else:
        return graph_cleaned.replace("_", " grafos com ").replace(".txt", " vértices")

# Função para salvar resultados em CSV
def save_to_csv(results, output_file):
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Cabeçalhos para a tabela de tempos
        header_time = ["Grafo", "Tempo Sequencial (s)", "Tempo Concorrente (1 thread) (s)", "Tempo Concorrente (2 threads) (s)",
                  "Tempo Concorrente (4 threads) (s)", "Tempo Concorrente (8 threads) (s)", "Tempo Concorrente (16 threads) (s)"]
        writer.writerow(header_time)

        # Dados da tabela de tempos
        for graph, data in results.items():
            graph_name = format_graph_name(graph)
            # Linha de tempos
            row_time = [graph_name, f"{data['sequencial']:.4f} s"]
            for t in [1, 2, 4, 8, 16]:
                row_time.append(f"{data['concorrente'].get(t, 'N/A'):.4f} s" if t in data['concorrente'] else "N/A")
            writer.writerow(row_time)

        # Adiciona uma linha em branco para separar as tabelas
        writer.writerow([])

        # Cabeçalhos para a tabela de speedups
        header_speedup = ["Grafo", "Speedup Sequencial", "Speedup (1 thread)", "Speedup (2 threads)", "Speedup (4 threads)", "Speedup (8 threads)", "Speedup (16 threads)"]
        writer.writerow(header_speedup)

        # Dados da tabela de speedups
        for graph, data in results.items():
            graph_name = format_graph_name(graph)
            # Linha de speedup
            row_speedup = [graph_name, "N/A"]  # Speedup do sequencial é N/A
            for t in [1, 2, 4, 8, 16]:
                if t in data["concorrente"]:
                    speedup = data["sequencial"] / data["concorrente"][t]
                    row_speedup.append(f"{speedup:.2f}x")
                else:
                    row_speedup.append("N/A")
            writer.writerow(row_speedup)

# Função para análise e comparação
def analyze_results(results):
    for graph, data in results.items():
        graph_name = format_graph_name(graph)
        print(f"Arquivo: {graph_name}")
        seq_time = data["sequencial"]
        print(f"  Sequencial: {seq_time:.4f} segundos")
        print("  Concorrente:")
        for threads, time in sorted(data["concorrente"].items()):
            speedup = seq_time / time
            print(f"    {threads} threads: {time:.4f} segundos (Speedup: {speedup:.2f}x)")
        print()

# Função para gerar gráficos
def plot_results(results):
    for graph, data in results.items():
        seq_time = data["sequencial"]
        threads = sorted(data["concorrente"].keys())
        times = [data["concorrente"][t] for t in threads]

        plt.figure(figsize=(10, 5))
        graph_name = format_graph_name(graph)
        plt.suptitle(f"Desempenho: {graph_name}")

        # Tempo absoluto
        plt.subplot(1, 2, 1)
        plt.plot([0] + threads, [seq_time] + times, marker='o', label="Tempo")
        plt.xlabel("Número de Threads")
        plt.ylabel("Tempo Total (segundos)")
        plt.title("Tempo Absoluto")
        plt.legend()

        # Speedup
        speedups = [seq_time / t for t in times]
        plt.subplot(1, 2, 2)
        plt.plot(threads, speedups, marker='o', label="Speedup")
        plt.xlabel("Número de Threads")
        plt.ylabel("Speedup")
        plt.title("Aceleração")
        plt.axhline(1, color='r', linestyle='--', label="Baseline")
        plt.legend()

        plt.tight_layout()
        plt.show()

# Lista de arquivos a processar
file_paths = [
    "resultados/resultados1.txt",
    "resultados/resultados2.txt",
    "resultados/resultados3.txt"
]

# Processando todos os arquivos
results_list = [process_file(file_path) for file_path in file_paths]

# Calculando as médias
averaged_results = calculate_averages(results_list)

# Salvando os resultados no arquivo CSV
output_csv = "resultados/benchmark_results.csv"
save_to_csv(averaged_results, output_csv)

# Analisando e gerando gráficos
analyze_results(averaged_results)
plot_results(averaged_results)

print(f"Resultados salvos em {output_csv}")

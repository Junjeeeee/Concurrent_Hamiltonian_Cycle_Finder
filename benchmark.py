#Esse código mede o tempo do programa sequencial e concorrente no processo de encontrar um ciclo
# hamiltoniano (ou indicar que não existe), testamos com diversos arquivos de grafos diferentes
# e o output desse código foi usado para gerar os relatórios.
# como o pc que tive acesso só tem 4 cores, testamos com 1,2 e 4 threads

#Esse código foi feito pro tabalho final de programação concorrente.
#grupo: João David, Eduarda Leal


import subprocess
import re
import time

def get_graph_data_from_file(filename):
    #pega os grafos do arquivo
    with open(filename, 'r') as file:
        lines = file.readlines()

    q = int(lines[0].strip())  # Número de grafos
    graphs = []
    index = 1

    for _ in range(q):
        num_vertices, num_edges = map(int, lines[index].strip().split())
        edges = [tuple(map(int, lines[index + 1 + i].strip().split())) for i in range(num_edges)]
        is_directed = int(lines[index + 1 + num_edges].strip())
        graphs.append((num_vertices, edges, is_directed))
        index += 2 + num_edges  # Atualiza o índice para o próximo grafo

    return q, graphs

def get_hamiltonian_path(num_vertices, edges, is_directed,qthreads,program_name):
    #Roda o código e recebe o output do caminho hamiltoniano
    is_directed = 1
    input_data = f"{num_vertices}\n{len(edges)}\n"
    input_data += "\n".join(f"{v1} {v2}" for v1, v2 in edges)
    input_data += f"\n{is_directed}\n"
    if qthreads > 0:
        input_data += f"\n{qthreads}\n"

    try:
        result = subprocess.run(
            [program_name], input=input_data, capture_output=True, text=True
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            lines = output.splitlines()
            if lines:
                last_line = lines[-1]
                numbers = re.findall(r'\d+', last_line)
                hamiltonian_path = [int(num) for num in numbers]
                return hamiltonian_path
            else:
                return None
        else:
            return None

    except Exception as e:
        print("Erro ao executar o programa C++:", e)
        return None

def process_multiple_graphs(filename,f):
    #Roda os testes de performance, medindo o tempo
    q, graphs = get_graph_data_from_file(filename)

    print(f"Processando {q} grafos do arquivo " + filename)
    print(f"Processando {q} grafos do arquivo " + filename,file = f)

    threads = [-1,1,2,4,8,16]

    program_name = "./concurrent_hamilton"
    for thread in threads:
        if thread == -1:
            print("Codigo sequencial")
            print("Codigo sequencial",file=f)
            program_name = "./hamilton"
        else:
            program_name = "./concurrent_hamilton"
            print("Codigo concorrente com ", thread, "threads")
            print("Codigo concorrente com ", thread, "threads",file=f)

        start_time = time.time()

        for i, (num_vertices, edges, is_directed) in enumerate(graphs):
            path = get_hamiltonian_path(num_vertices, edges, is_directed,thread,program_name)

        end_time = time.time()

        total_time = end_time - start_time
        average_time = total_time / q

        print(f"Tempo total: {total_time:.4f} segundos\n")
        print(f"Tempo total: {total_time:.4f} segundos\n",file=f)


filename = ["random_graphs/100_10.txt","random_graphs/100_15.txt","random_graphs/100_16.txt","random_graphs/100_17.txt","random_graphs/100_18.txt","random_graphs/100_19.txt","random_graphs/100_20.txt","random_graphs/100_21.txt","random_graphs/100_22.txt","random_graphs/22_no_limit.txt","random_graphs/random_sizes.txt"]  # Substitua pelo nome do arquivo de entrada
with open("resultados/bench_results.txt", 'w') as f:
    for s in filename:
        process_multiple_graphs(s,f)

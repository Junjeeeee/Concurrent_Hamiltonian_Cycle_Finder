#Esse código mede o tempo do programa sequencial e concorrente no processo de encontrar um ciclo
# hamiltoniano (ou indicar que não existe), testamos com diversos arquivos de grafos diferentes
# e o output desse código foi usado para gerar os relatórios.
# como o pc que tive acesso só tem 4 cores, testamos com 1,2 e 4 threads

#Esse código foi feito pro tabalho final de programação concorrente.
#grupo: João David, Eduarda Leal


import subprocess
import re

def get_graph_data_from_file(filename):
    #Pega os grafos do arquivo
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

def process_multiple_graphs(filename):
    #Roda os testes de corretude

    q, graphs = get_graph_data_from_file(filename)

    print(f"Processando {q} grafos do arquivo " + filename)

    threads = [1,2,4,8,16,-1]

    program_name = "./concurrent_hamilton"
    for thread in threads:
        if thread == -1:
            print("Codigo sequencial")
            program_name = "./hamilton"
        else:
            print("Codigo concorrente com ", thread, "threads")
            
        for i, (num_vertices, edges, is_directed) in enumerate(graphs):
            path = get_hamiltonian_path(num_vertices, edges, is_directed,thread,program_name)
            acertou = check_path(path,edges,is_directed,num_vertices)
            if len(path) == 0:
                
                print("Não encontrou caminho hamiltoniano")
                if filename == "random_graphs/corretude_cicle.txt":
                    #Se o arquivo com certeza tiver ciclo, esse é um caso de erro
                    print("código incorreto\n")
                    return -1
            elif acertou:
                print("Caminho Hamiltoniano encontrado com sucesso")
                if filename == "random_graphs/corretude_trees.txt":
                    #Se o arquivo com certeza não tiver ciclo, esse é um caso de erro
                    print("código incorreto\n")
                    return -1
            else:
                #Em qualquer ocasião esse é um caso de erro, o caminho hamiltoniano não está correto
                print("Caminho Hamiltoniano errado")
                print("código incorreto\n")
                return -1
            
def check_path(path, edges, is_directed, num_vertices):
    #Checa se o caminho hamiltoniano dado é correto

    adjacency_list = [set() for _ in range(num_vertices)]
    for v1, v2 in edges:
        v1-=1
        v2-=1
        adjacency_list[v1].add(v2)
        if not is_directed:
            adjacency_list[v2].add(v1)

    atual = 0
    visited = set()
    for node in path:
        node-=1
        if node == atual: continue
        if node in visited: return False
        if node not in adjacency_list[atual]:
            return False
        atual = node
        visited.add(node)
    
    if len(visited) != num_vertices: return False
    return True


filename = ["random_graphs/corretude_cicle.txt","random_graphs/corretude_trees.txt","random_graphs/random_sizes.txt"]  # Substitua pelo nome do arquivo de entrada
for s in filename:
    process_multiple_graphs(s)

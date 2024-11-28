#Esse código foi usado para gerar grafos aleatórios para realizar os testes entre
#o código sequencial e o concorrente de encontrar um ciclo hamiltoniano.
#
# Nesse código, criamos grafos de tamanhos diversos para os testes, incluindo grafos onde com certeza temos
# ciclos hamiltonianos, que são usados para testes de corretude dos códigos
#
#Esse código foi feito pro tabalho final de programação concorrente.
#grupo: João David, Eduarda Leal



import random

def create_random_graphs(low_num_vertices,high_num_vertices,filename,confirmed_hamiltonian_path=False,limit = 3,amount = 100):
    #Essa função cria diversos grafos aleatórios com características específicas, além de coloca-los em um arquivo
    iterations = 100000
    random_graphs = amount
    with open(filename, 'w') as f:
        print(random_graphs, file=f)
        for _ in range(random_graphs):
            num_vertices = random.randint(low_num_vertices,high_num_vertices)
            directed = random.randint(0,1)
            adjacency_list = [set() for _ in range(num_vertices)]
            hamiltonian_path = [set() for _ in range(num_vertices)]
            if confirmed_hamiltonian_path:
                create_hamiltonian_cycle(num_vertices,adjacency_list,hamiltonian_path,directed)
            else:
                create_spanning_tree(num_vertices,directed,adjacency_list)
            mcmc(iterations,num_vertices,directed,limit,adjacency_list,hamiltonian_path)
            edge_list = transform_graph_in_edge_list(num_vertices,adjacency_list)
            put_graph_in_file(num_vertices, edge_list, f, directed)

def create_random_graph(num_vertices,directed = 0,confirmed_hamiltonian_path=True,limit = 3):
    #Essa função cria 1 grafo aleatório e retorna uma lista de arestas
    iterations = 100000
    adjacency_list = [set() for _ in range(num_vertices)]
    hamiltonian_path = [set() for _ in range(num_vertices)]
    if confirmed_hamiltonian_path:
        create_hamiltonian_cycle(num_vertices,adjacency_list,hamiltonian_path,directed)
    else:
        create_spanning_tree(num_vertices,directed,adjacency_list)
    mcmc(iterations,num_vertices,directed,limit,adjacency_list,hamiltonian_path)
    edge_list = transform_graph_in_edge_list(num_vertices,adjacency_list)
    return edge_list


def create_hamiltonian_cycle(num_vertices,adjacency_list,hamiltonian_path,directed):
    #Cria um ciclo hamiltoniano inicial
    vector = []
    for i in range(num_vertices):
        vector.append(i)
    random.shuffle(vector)
    for i in range(num_vertices):
        add_edge(vector[i], vector[(i+1)%num_vertices], directed, adjacency_list)
        hamiltonian_path[vector[i]].add(vector[(i+1)%num_vertices])
        if not directed:
            hamiltonian_path[vector[(i+1)%num_vertices]].add(vector[i])

def create_spanning_tree(num_vertices,directed,adjacency_list):
    #Cria uma árvore geradora aleatória de um grafo, isso garante que o grafo será conexo
    next = []
    for i in range(num_vertices-1):
        next.append(i+1)
    random.shuffle(next)
    current = [0]
    for i in range (num_vertices-1):
        current_choosed = random.choice(current)
        next_choosed = next.pop()
        add_edge(current_choosed, next_choosed,directed,adjacency_list)
        current.append(next_choosed)


def dfs(current_vertex,num_vertices,adjacency_list,visited):
    #Busca em profundidade no grafo usado na função de checar conectividade
    visited[current_vertex] = True
    for neighbor in adjacency_list[current_vertex]:
        if not visited[neighbor]:
            dfs(neighbor,num_vertices,adjacency_list,visited)


def check_conectivity(num_vertices,adjacency_list):
    #Checa a conectividade do grafo, usado no MCMC para não desconectar um grafo quando deletar uma aresta
    visited = [False for _ in range(num_vertices)]
    first_time = True
    for i in range(num_vertices):
        if not visited[i]:
            if first_time:
                first_time = False
                dfs(0,num_vertices,adjacency_list,visited)
            else:
                return False
    return True

def add_edge(a,b,directed,adjacency_list):
    #Adiciona uma aresta
    if directed == 0:
        adjacency_list[a].add(b)
        adjacency_list[b].add(a)
    else:
        adjacency_list[a].add(b)

def remove_edge(a,b,directed,adjacency_list):
    #Remove uma aresta
    if directed == 0:
        adjacency_list[a].remove(b)
        adjacency_list[b].remove(a)
    else:
        adjacency_list[a].remove(b)

def mcmc(iterations,num_vertices,directed,max_edges_multiplier,adjacency_list,hamiltonian_path):
    #Algoritmo MCMC (Monte Carlo Markov Chain) para gerar grafos conexos aleatórios
    # Obs: é necessário iniciar o grafo com uma árvore geradora aleatória antes de rodar o mcmc
    edges = 0
    if len(hamiltonian_path) != 0:
        edges = num_vertices-1
    for _ in range(iterations):
        current_vertex = random.randint(0, num_vertices-1)
        neighbor = random.randint(0, num_vertices-1)
        if neighbor == current_vertex:
            continue

        if neighbor in adjacency_list[current_vertex]:
            if neighbor in hamiltonian_path[current_vertex]:
                continue
            edges-=1
            remove_edge(current_vertex, neighbor,directed,adjacency_list)
            if not check_conectivity(num_vertices,adjacency_list):
                edges+=1
                add_edge(current_vertex,neighbor,directed,adjacency_list)
        else:
            if edges >= max_edges_multiplier*num_vertices:
                continue
            edges+=1
            add_edge(current_vertex,neighbor,directed,adjacency_list)

    return adjacency_list
        

def transform_graph_in_edge_list(num_vertices,adjacency_list):
    #transforma a lista de adjascências em uma lista de arestas
    edge_list = []
    for i in range(num_vertices):
        for j in adjacency_list[i]:
            edge_list.append((i+1,j+1))
    return edge_list


def put_graph_in_file(num_vertices, edge_list, f, directed):
    #coloca o grafo em um arquivo
    print(num_vertices, len(edge_list), file=f)
    for pair in edge_list:
        print(pair[0], pair[1], file=f)
    print(1, file=f)


#Vamos gerar grafos aleatorios para os testes de corretude e de performance

def create_files():
    
    #Testar a performance
    create_random_graphs(10,10,"random_graphs/100_10.txt")
    create_random_graphs(15,15,"random_graphs/100_15.txt")
    create_random_graphs(16,16,"random_graphs/100_16.txt")
    create_random_graphs(17,17,"random_graphs/100_17.txt")
    create_random_graphs(18,18,"random_graphs/100_18.txt")
    create_random_graphs(19,19,"random_graphs/100_19.txt")
    create_random_graphs(20,20,"random_graphs/100_20.txt")
    create_random_graphs(21,21,"random_graphs/100_21.txt")
    create_random_graphs(22,22,"random_graphs/100_22.txt")
    create_random_graphs(22,22,"random_graphs/22_no_limit.txt",False,22)

    #Esse também está sendo usado para corretude
    create_random_graphs(5,22,"random_graphs/random_sizes.txt")

def create_corretude_files():
    #200 grafos com ciclos hamiltonianos
    create_random_graphs(5,22,"random_graphs/corretude_cicle.txt",True,3,200)
    #200 grafos sem ciclos hamiltonianos (árvores)
    create_random_graphs(5,22,"random_graphs/corretude_trees.txt",False,0,200)



create_corretude_files()
create_files()

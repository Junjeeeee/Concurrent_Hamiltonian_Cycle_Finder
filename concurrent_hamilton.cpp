/*
Código concorrente do procedimento de Rubin para encontrar ciclos hamiltonianos.
O código está todo comentado, eu recomendo você ler do início da função main(),
e então seguir conforme as funções são chamadas.
Obs: como a versão sequencial é bem parecida, foram omitidos alguns comentários repetitivos
Esse código faz parte do trabalho final da matéria "Programação Concorrente".

A estratégia para a paralelização foi gerar caminhos iniciais para que as threads pudessem
ter um ponto de partida diferente, e percorrer por todos os caminhos possíveis de forma
eficiente

Grupo: João David, Eduarda Leal
*/


#include<unordered_set>
#include<unordered_map>
#include<stack>
#include<queue>
#include<array>
#include<vector>
#include<iostream>
#include<pthread.h>

using namespace std;



bool deductions(int current_node,int first_node,int parent, stack<int> &modifications, stack<int> &incident_modifications, vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //sem alterações
    stack<int> erase_stack;
    bool all_except_one = false;
    for(int neighbour : graph[current_node])
    {
        if(incidentgraph[neighbour].size() == 1)
        {
            if(all_except_one) return false; // Rule F4
            for(int neighbour2 : graph[current_node])
            {
                if(neighbour2 == neighbour) continue;
                erase_stack.push(neighbour2);
            }
            all_except_one = true;
            continue;
        }
    }

    while(!erase_stack.empty())
    {
        int neighbour = erase_stack.top();
        erase_stack.pop();
        graph[current_node].erase(neighbour);
        incidentgraph[neighbour].erase(current_node);
        modifications.push(neighbour);
    }

    for(int neighbour : incidentgraph[current_node])
    {
        if(current_node == first_node) break;
        if(neighbour == parent) continue;
        erase_stack.push(neighbour);
    }

    while(!erase_stack.empty())
    {
        int neighbour = erase_stack.top();
        erase_stack.pop();
        graph[neighbour].erase(current_node);
        incidentgraph[current_node].erase(neighbour);
        incident_modifications.push(neighbour);
        if(graph[neighbour].size() == 0) return false;
    }


    return true;
}

void unstack(int current_node, stack<int> &modifications, stack<int> &incident_modifications,vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //sem alterações
    while(!modifications.empty())
    {
        int neighbour = modifications.top();
        modifications.pop();
        graph[current_node].insert(neighbour);
        incidentgraph[neighbour].insert(current_node);
    }

    while(!incident_modifications.empty())
    {
        int neighbour = incident_modifications.top();
        incident_modifications.pop();
        graph[neighbour].insert(current_node);
        incidentgraph[current_node].insert(neighbour);
    }
}

void localunstack(int current_node, stack<int> &local_modifications,vector<unordered_set<int>> &incidentgraph)
{
    //sem alterações
    while(!local_modifications.empty())
    {
        int neighbour = local_modifications.top();
        local_modifications.pop();
        incidentgraph[neighbour].insert(current_node);
    }
}

bool dfs_rubin(int current_node,int first_node,int parent, int n, vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph,unordered_set<int> &nodes_in_path,stack<int> &path, bool &found_path)
{
    //Se uma das threads achar um caminho hamiltoniano, podemos parar de procurar.
    //Perceba que não estamos usando locks, pois essa veriável será lida diversas vezes
    //e só será escrita uma vez, e uma condição de corrida não afeta em nada no código, somente
    // afetará em uma busca rápida que gastará um tempo extra pequeno, tempo pequeno comparado
    // ao que um lock causaria aqui
    if(found_path) return false;

    stack<int> modifications;
    stack<int> incident_modifications;
    if(current_node != first_node)
    {
        nodes_in_path.insert(current_node);
        path.push(current_node);
    }
    bool aproved = deductions(current_node,first_node,parent, modifications,incident_modifications,graph,incidentgraph);
    if(!aproved)
    {
        unstack(current_node,modifications,incident_modifications,graph,incidentgraph);
        return false;
    }

    stack<int> local_modifications;

    vector<int> current_neighbors;
    for(int neighbour:graph[current_node])
    {
        current_neighbors.push_back(neighbour);
    }

    for(int neighbour:current_neighbors)
    {
        if(nodes_in_path.find(neighbour) != nodes_in_path.end()) continue;
        if(neighbour == first_node)
        {
            if(nodes_in_path.size() == n-1)
            {
                path.push(first_node);
                return found_path = true; // sinalizamos para as outras threads que encontramos um ciclo hamiltoniano
            }
            continue;
        }

        for(int neighbourd:graph[current_node])
        {
            if(neighbourd == neighbour) continue;
            incidentgraph[neighbourd].erase(current_node);
            local_modifications.push(neighbourd);
        }

        bool found = dfs_rubin(neighbour,first_node,current_node,n,graph,incidentgraph,nodes_in_path,path,found_path);
        if(found) return true;
        if(found_path) return false;
        nodes_in_path.erase(neighbour);
        path.pop();
        localunstack(current_node,local_modifications,incidentgraph);
    }

    unstack(current_node,modifications,incident_modifications,graph,incidentgraph);
    return false;
}

vector<int> hamiltonian_path(int n, vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph,unordered_set<int> &nodes_in_path,stack<int> &path, bool &found)
{
    int cur_v = 0;
    int parent = 0;
    unordered_map<int,stack<int>> modifications; //Esses hashmaps são utilizados para que os rolls-backs sejam feitos com os vértices certos, sendo uma stack de roll-back para cada vértice do caminho inicial
    unordered_map<int,stack<int>> incident_modifications;
    unordered_map<int,stack<int>> local_modifications;

    //Aqui pegamos o vértice atual e seu pai do caminho inicial dado
    if(path.size()>0)
    {
        cur_v = path.top();
        path.pop();
        nodes_in_path.erase(cur_v);
        if(path.size()>0)
        {
            parent = path.top();


            // Essa parte do código toda se trata do uso das deduções de rubin, por isso não estar sendo
            // Feito dentro da função dfs_rubin, além de estar sendo feito para vários vértices ao mesmo tempo
            // (os vértices do caminho inicial), foi necessário um tratamento mais complexo.

            stack<int> path2 = path;
            stack<int> sequence;
            int cur_vr = 0;
            int cur_p = 0;
            while(!path2.empty())
            {
                int at = path2.top();
                path2.pop();
                sequence.push(at);
            }
            sequence.push(0);


            while(!sequence.empty())
            {
                cur_p = cur_vr;
                cur_vr = sequence.top();
                sequence.pop();
                local_modifications[cur_p] = stack<int>();
                if(cur_p != cur_vr)
                {
                    for(int neighbour:graph[cur_p])
                    {
                        if(neighbour == cur_vr) continue;
                        incidentgraph[neighbour].erase(cur_p);
                        local_modifications[cur_p].push(neighbour);
                    }
                }
                modifications[cur_vr] = stack<int>();
                incident_modifications[cur_vr] = stack<int>();
                bool aproved = deductions(cur_vr,0,cur_p, modifications[cur_vr],incident_modifications[cur_vr],graph,incidentgraph);
                if(!aproved)
                {
                    for(auto v:local_modifications)
                    {
                        localunstack(v.first,v.second,incidentgraph);
                    }
                    for(auto v:modifications)
                    {
                        unstack(v.first,v.second,incident_modifications[v.first],graph,incidentgraph);
                    }
                    return vector<int>();
                }
                if((cur_vr != cur_p) && (graph[cur_p].find(cur_vr) == graph[cur_p].end() || incidentgraph[cur_vr].find(cur_p) == incidentgraph[cur_vr].end()))
                {
                    for(auto v:local_modifications)
                    {
                        localunstack(v.first,v.second,incidentgraph);
                    }
                    for(auto v:modifications)
                    {
                        unstack(v.first,v.second,incident_modifications[v.first],graph,incidentgraph);
                    }
                    return vector<int>();
                }

            }

        }

    }

    if((cur_v != parent) && graph[parent].find(cur_v) == graph[parent].end())
    {
        for(auto v:local_modifications)
        {
            localunstack(v.first,v.second,incidentgraph);
        }
        for(auto v:modifications)
        {
            unstack(v.first,v.second,incident_modifications[v.first],graph,incidentgraph);
        }
        return vector<int>();
    }

    //fim das deduções no caminho inicial dado


    bool foi = dfs_rubin(cur_v,0,parent,n,graph,incidentgraph,nodes_in_path,path,found);
    vector<int> path_return;
    if(!foi)
    {
        for(auto v:local_modifications)
        {
            localunstack(v.first,v.second,incidentgraph);
        }
        for(auto v:modifications)
        {
            unstack(v.first,v.second,incident_modifications[v.first],graph,incidentgraph);
        }
        return path_return;
    }
    while(!path.empty())
    {
        path_return.push_back(path.top());
        path.pop();
    }
    path_return.push_back(0);

    return path_return;
}

void graph_creator(int n,vector<pair<int,int>> edge_list,bool undirected,vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //sem alterações
    unordered_set<int> tmp;
    graph.assign(n,tmp);
    incidentgraph.assign(n,tmp);

    for(pair<int,int> edge : edge_list)
    {
        int u = edge.first;
        int v = edge.second;
        graph[u].insert(v);
        incidentgraph[v].insert(u);
        if(undirected)
        {
            graph[v].insert(u);
            incidentgraph[u].insert(v);
        }
    }
    return;
}

struct argument_thread //struct para os argumentos das threads
{
    bool *caminho_encontrado; //compartilhado
    stack<pair<stack<int>,unordered_set<int>>> *path_pool; //compartilhado
    pthread_mutex_t *mutex; //compartilhado
    pthread_mutex_t *mutex2; //compartilhado
    vector<int> *caminho_hamiltoniano; //compartilhado
    int n; //um pra cada thread
    vector<unordered_set<int>> graph; //um pra cada thread
    vector<unordered_set<int>> incidentgraph; //um pra cada thread
};


void *thread(void *arg)
{
    //typecasting para nossa struct
    argument_thread *args = static_cast<argument_thread*>(arg);
    pair<stack<int>,unordered_set<int>> current_job;

    while(true)
    {
        pthread_mutex_lock(args->mutex); //vamos procurar um trabalho
        if((*args->path_pool).empty() || (*args->caminho_encontrado))
        {
            // se a pilha estiver vazia ou já tiverem encontrado caminho, finalizamos
            pthread_mutex_unlock(args->mutex);
            pthread_exit(NULL);
        }
        current_job = (*args->path_pool).top(); //pegamos um trabalho do topo da pilha
        (*args->path_pool).pop(); //removemos ele do topo
        pthread_mutex_unlock(args->mutex);
        //procuramos um ciclo hamiltoniano a partir do caminho inicial do nosso job
        vector<int> resp = hamiltonian_path(args->n,args->graph,args->incidentgraph,current_job.second,current_job.first,(*args->caminho_encontrado));
        if(resp.size() != 0) //achamos!!
        {
            pthread_mutex_lock(args->mutex2);  //2 threads podem achar um caminho ao mesmo tempo
            (*args->caminho_hamiltoniano) = resp;
            pthread_mutex_unlock(args->mutex2);
        }
    }
}

void generate_paths(stack<pair<stack<int>,unordered_set<int>>> &path_pool,vector<unordered_set<int>> &graph, int q_paths)
{
    vector<stack<int>> path; //caminho
    vector<unordered_set<int>> path_nodes; //hashset com os nós do caminho
    path.push_back(stack<int>());
    path_nodes.push_back(unordered_set<int>());
    q_paths--; //quantidade de caminhos necessários

    ///"bfs"
    int d_max = 0; //distância máxima
    bool acabou = false; //Sinaliza que não iremos ir mais longe que a distância atual

    queue<array<int,4>> fila_bfs; //fila com as informações: vertice, pai, distancia, indice_fila_pai

    fila_bfs.push({0,0,0,0}); //colocamos o vértice inicial na fila

    if(q_paths==0) // se só temos 1 thread só precisamos de 1 caminho
    {
    	path_pool.push(make_pair(path[0],path_nodes[0]));
    	return;
    }

    //Aqui faremos uma busca parecida com um BFS, contudo, o vetor de "visitado" clássico
    //será substituido por uma checagem se o vizinho é o pai do vértice atual, ou se
    //o vértice já está no caminho atual. Isso efetivamente testaria todos os caminhos possíveis
    // caso não colocássemos uma condição de parada

    while(!fila_bfs.empty()) // preencheremos os caminhos
    {
        array<int,4> v_atual = fila_bfs.front();
        fila_bfs.pop();

        if(v_atual[2] > d_max)
        {
            if(acabou) break; //se acabou, não iremos uma distância mais longe
            d_max = v_atual[2]; //se não acabou ainda, iremos explorar essa distância inteira
        }

        int i=0;
        stack<int> mods; // modificações
        for(int v : graph[v_atual[0]])
        {
            i++;
            if(v == v_atual[1]) continue;
            if(path_nodes[v_atual[3]].find(v) != path_nodes[v_atual[3]].end()) continue;
            if(v == 0) continue;
            mods.push(v);  //esse vértice pode ser adicionado ao caminho atual
        }

        while(!mods.empty()) //aqui criamos os novos caminhos
            {
                int v = mods.top();
                mods.pop();
                if(mods.size() == 0) //colocamos o nó no caminho do índice atual
                {
                    path[v_atual[3]].push(v);
                    path_nodes[v_atual[3]].insert(v);
                    fila_bfs.push({v,v_atual[0],v_atual[2]+1,v_atual[3]});
                }
                else //criamos um novo valor no vetor para esse vértice
                {
                    path.push_back(path[v_atual[3]]);
                    path_nodes.push_back(path_nodes[v_atual[3]]);
                    path[path.size()-1].push(v);
                    path_nodes[path.size()-1].insert(v);
                    fila_bfs.push({v,v_atual[0],v_atual[2]+1,(int)path.size()-1});
                    //estamos aumentando a quantidade de caminhos
                    q_paths--;
                    if(q_paths <= 0) acabou = true;
                }
            }
    }

    for(int i=0;i<path.size();i++) //colocamos os caminhos no pool de caminhos para as threads
    {
        path_pool.push(make_pair(path[i],path_nodes[i]));
    }

}

vector<int> concurrent_hamilton(vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph,int qthreads,int n)
{
    vector<int> path; // ciclo hamiltoniano
    stack<pair<stack<int>,unordered_set<int>>> path_pool; //pool de jobs

    generate_paths(path_pool,graph,2*qthreads); //A quantidade de caminhos é igual a 2x quantidade de threads no mínimo

    pthread_mutex_t mutex;
    pthread_mutex_t mutex2;
    pthread_mutex_init(&mutex,NULL);
    pthread_mutex_init(&mutex2,NULL);
    bool found = false; //booleano que diz se o ciclo foi encontrado
    vector<argument_thread> argthreads(qthreads);
    pthread_t tid[qthreads];

    for(int i=0;i<qthreads;i++) //Inicializamos os argumentos para as threads
    {
        argthreads[i].caminho_encontrado = &found; //referência para bool que diz que foi encontrado
        argthreads[i].path_pool = &path_pool; // referência para pool de tarefas (caminhos iniciais)
        argthreads[i].mutex = &mutex;
        argthreads[i].mutex2 = &mutex2;
        argthreads[i].caminho_hamiltoniano = &path; //referência para vetor com ciclo hamiltoniano
        argthreads[i].n = n; //tamanho do grafo
        argthreads[i].graph = graph; //grafo (uma cópia)
        argthreads[i].incidentgraph = incidentgraph; //grafo incidente (uma cópia)
    }

    for(int t=0; t<qthreads; t++)
    {
        if (pthread_create(&tid[t], NULL, thread, (void *) &argthreads[t]))
        {
            cout << "--ERRO: pthread_create()\n";
            exit(-1);
        }
    }

    for (int t = 0; t < qthreads; t++)
    {
        pthread_join(tid[t], NULL);
    }

    pthread_mutex_destroy(&mutex);
    pthread_mutex_destroy(&mutex2);

    return path;
}


int main(void)
{
    cout << "insira a quantidade de vértices\n";
    int n; cin >> n;
    cout << "insira a quantidade de arestas\n";
    int m; cin >> m;
    vector<pair<int, int>> edge_list;

    cout << "insira as arestas duas a duas, separadas por espaço ou enter\n";

    for(int i=0;i<m;i++)
    {
        int a,b; cin >> a >> b; a--; b--;
        edge_list.push_back(make_pair(a,b));
    }

    cout << "digite 1 se o grafo for direcionado, 0 se não for\n";

    bool undirected; cin >> undirected;
    undirected = !undirected;

    vector<unordered_set<int>> graph, incidentgraph;

    graph_creator(n, edge_list, undirected, graph, incidentgraph);

    unordered_set<int> nodes_in_path;
    stack<int> path;

    int qthreads;
    cout << "insira a quantidade de Threads\n";
    cin >> qthreads;

    vector<int> hamiltonian = concurrent_hamilton(graph,incidentgraph,qthreads,n);
    for(int i=0;i<hamiltonian.size()/2;i++)
    {
        swap(hamiltonian[i],hamiltonian[hamiltonian.size()-i-1]);
    }

    if (hamiltonian.size() > 1)
    {
        cout << "Caminho Hamiltoniano encontrado: ";
        for (int node : hamiltonian)
        {
            cout << node + 1 << " "; // Voltando para indexação 1
        }
        cout << '\n';
    }
    else
    {
        cout << "Nenhum caminho Hamiltoniano foi encontrado." << endl;
    }

    return 0;
}

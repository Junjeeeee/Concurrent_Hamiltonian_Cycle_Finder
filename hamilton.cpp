/*
Código sequencial do procedimento de Rubin para encontrar ciclos hamiltonianos.
O código está todo comentado, eu recomendo você ler do início da função main(),
e então seguir conforme as funções são chamadas.
Esse código faz parte do trabalho final da matéria "Programação Concorrente".
Grupo: João David, Eduarda Leal
*/


#include<unordered_set>
#include<stack>
#include<vector>
#include<iostream>

using namespace std;


bool deductions(int current_node,int first_node,int parent, stack<int> &modifications, stack<int> &incident_modifications, vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //Aqui aplicaremos algumas deduções feitas no procedimento de Rubin.
    //Essas deduções são importantes para diminuir a quantidade de caminhos que precisamos
    // investigar.

    stack<int> erase_stack; // quais arestas deletaremos
    bool all_except_one = false; // Se existe somente um caminho possível

    for(int neighbour : graph[current_node])
    {
        //Regra R1, se um vértice vizinho só tem uma aresta incidente,
        // Deletaremos todos as outras arestas.
        if(incidentgraph[neighbour].size() == 1)
        {
            if(all_except_one) return false;
            // Se existem 2 vértices nessa situação, entramos na regra de falha F4,
            // Não há caminho possível

            //sinalizamos as arestas para deletar
            for(int neighbour2 : graph[current_node])
            {
                if(neighbour2 == neighbour) continue;
                erase_stack.push(neighbour2);
            }
            all_except_one = true;
            continue;
        }
    }

    //deletamos as arestas
    while(!erase_stack.empty())
    {
        int neighbour = erase_stack.top();
        erase_stack.pop();
        graph[current_node].erase(neighbour);
        incidentgraph[neighbour].erase(current_node);
        modifications.push(neighbour);
    }

    //sinalizamos todos as arestas que visitam o vértice atual, pois
    // ele já foi visitado
    for(int neighbour : incidentgraph[current_node])
    {
        if(current_node == first_node) break;
        if(neighbour == parent) continue;
        erase_stack.push(neighbour);
    }

    //deletamos as arestas
    while(!erase_stack.empty())
    {
        int neighbour = erase_stack.top();
        erase_stack.pop();
        graph[neighbour].erase(current_node);
        incidentgraph[current_node].erase(neighbour);
        incident_modifications.push(neighbour);
        //Falha F3, checamos se o vértice que acabamos de deletar está sem arestas de saída
        if(graph[neighbour].size() == 0) return false;
    }

    // não encontramos nenhuma condição de falha
    return true;
}

void unstack(int current_node, stack<int> &modifications, stack<int> &incident_modifications,vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //reverte alterações de deleção no grafo
    while(!modifications.empty())
    {
        int neighbour = modifications.top();
        modifications.pop();
        graph[current_node].insert(neighbour);
        incidentgraph[neighbour].insert(current_node);
    }

    //reverte alterações de deleção no grafo incidente
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
    while(!local_modifications.empty())
    {
        int neighbour = local_modifications.top();
        local_modifications.pop();
        incidentgraph[neighbour].insert(current_node);
    }
}

bool dfs_rubin(int current_node,int first_node,int parent, int n, vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph,unordered_set<int> &nodes_in_path,stack<int> &path)
{
    stack<int> modifications; // Essa pilha é usada para reverter mudanças no grafo no backtracking
    stack<int> incident_modifications; // Essa pilha é usada para reverter mudanças no grafo incidente no backtracking

    if(current_node != first_node) //colocamos o nó no caminho
    {
        nodes_in_path.insert(current_node);
        path.push(current_node);
    }

    bool aproved = deductions(current_node,first_node,parent, modifications,incident_modifications,graph,incidentgraph);
    if(!aproved) // Atingiu uma condição de falha na dedução, teremos que voltar e tentar outro caminho
    {
        //rollback
        unstack(current_node,modifications,incident_modifications,graph,incidentgraph);
        return false;
    }

    stack<int> local_modifications; //quando visitamos um vértice, deletamos os seus irmãos,
    // essa pilha reverterá essa operação

    vector<int> current_neighbors;
    for(int neighbour:graph[current_node])
    {
        current_neighbors.push_back(neighbour);
    }

    for(int neighbour:current_neighbors)
    {
        if(nodes_in_path.find(neighbour) != nodes_in_path.end()) continue; //Regra D2. O nó já está no caminho
        if(neighbour == first_node)
        {
            if(nodes_in_path.size() == n-1)
            {
                path.push(first_node); //Achamos um ciclo hamiltoniano!
                return true;
            }
            continue;
        }

        for(int neighbourd:graph[current_node]) //deletamos todas as arestas para os irmãos antes de prosseguir pelo caminho
        {
            if(neighbourd == neighbour) continue;
            incidentgraph[neighbourd].erase(current_node);
            local_modifications.push(neighbourd);
        }

        //seguimos no caminho novo
        bool found = dfs_rubin(neighbour,first_node,current_node,n,graph,incidentgraph,nodes_in_path,path);
        if(found) return true; // Se encontrou o caminho hamiltoniano

        //As três próximas linhas revertem as alterações anteriores
        nodes_in_path.erase(neighbour);
        path.pop();
        localunstack(current_node,local_modifications,incidentgraph);

        //Partimos para o próximo vizinho
    }

    //Se o código seguiu até aqui, nenhum dos nossos vizinhos gera um ciclo hamiltoniano,
    //portanto, o caminho até o vértice atual não encontra um ciclo hamiltoniano, logo,
    //Voltaremos para o vértice anterior e tentaremos outros caminhos.
    unstack(current_node,modifications,incident_modifications,graph,incidentgraph); //reverte mudanças
    return false;
}

vector<int> hamiltonian_path(int n, vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //hashset que diz quais nós estão no caminho atual
    unordered_set<int> nodes_in_path;
    stack<int> path; //pilha com os nós do caminho atual
    bool foi = dfs_rubin(0,0,0,n,graph,incidentgraph,nodes_in_path,path); //procedimento de Rubin

    vector<int> path_return; // caminho de retorno
    if(!foi) return path_return; // Se não encontramos caminho hamiltoniano

    while(!path.empty()) //Aqui colocamos o caminho de retorno no vetor
    {
        path_return.push_back(path.top());
        path.pop();
    }
    path_return.push_back(0); //colocamos o vértice inicial no vetor
    return path_return;
}

void graph_creator(int n,vector<pair<int,int>> edge_list,bool undirected,vector<unordered_set<int>> &graph,vector<unordered_set<int>> &incidentgraph)
{
    //Inicializamos os grafos com valores vazios
    unordered_set<int> tmp;
    graph.assign(n,tmp);
    incidentgraph.assign(n,tmp);

    // Passamos da lista de arestas para lista de adjascências
    for(pair<int,int> edge : edge_list)
    {
        int u = edge.first;
        int v = edge.second;
        graph[u].insert(v);
        incidentgraph[v].insert(u);
        if(undirected) // se não for direcionado, temos que adicionar a aresta de volta
        {
            graph[v].insert(u);
            incidentgraph[u].insert(v);
        }
    }
    return;
}


int main(void)
{
    cout << "insira a quantidade de vértices\n";
    int n; cin >> n;
    cout << "insira a quantidade de arestas\n";
    int m; cin >> m;

    // Arestas do grafo
    vector<pair<int, int>> edge_list;

    cout << "insira as arestas duas a duas, separadas por espaço ou enter\n";

    for(int i=0;i<m;i++)
    {
        int a,b; cin >> a >> b; a--; b--; // recebo indexado em 1 e indexo em 0
        edge_list.push_back(make_pair(a,b));
    }

    cout << "digite 1 se o grafo for direcionado, 0 se não for\n";

    bool undirected; cin >> undirected; //No benchmark, todos são direcionados
    undirected = !undirected;

    // Vetores para armazenar o grafo e o grafo incidente
    vector<unordered_set<int>> graph, incidentgraph;

    // Criar o grafo
    graph_creator(n, edge_list, undirected, graph, incidentgraph);

    // Obter o caminho hamiltoniano
    vector<int> hamiltonian = hamiltonian_path(n, graph, incidentgraph);
    for(int i=0;i<hamiltonian.size()/2;i++)
    {
        swap(hamiltonian[i],hamiltonian[hamiltonian.size()-i-1]);    
    }

    // Exibir o caminho hamiltoniano
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

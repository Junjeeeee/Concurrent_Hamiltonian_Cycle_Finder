import pygame
import math
import re
import subprocess
import networkx as nx
import pyperclip
from create_random_graphs import create_random_graph

# Função para calcular a posição dos vértices usando o layout spring do NetworkX
def calculate_positions_spring(num_vertices, edges):
    G = nx.Graph()
    G.add_nodes_from(range(1, num_vertices + 1))
    G.add_edges_from(edges)
    positions = nx.spring_layout(G, seed=42)
    return positions

# Função para converter as posições calculadas para as coordenadas do Pygame
def convert_positions_to_pygame(positions, center, scale):
    pygame_positions = {}
    for node, (x, y) in positions.items():
        pygame_x = int(center[0] + x * scale)
        pygame_y = int(center[1] + y * scale)
        pygame_positions[node] = (pygame_x, pygame_y)
    return pygame_positions

def animate_path(screen, positions, edges, path, color_path, color_default, clock, speed=0.01):
    edge_colors = {edge: color_default for edge in edges}
    visited_nodes = set()  # Conjunto para armazenar os vértices já visitados

    for i in range(len(path) - 1):
        start_node = path[i]
        end_node = path[i + 1]
        start_pos = positions[start_node]
        end_pos = positions[end_node]

        # Animação da bolinha ao longo da aresta
        for t in range(0, 101):
            interp_x = start_pos[0] + (end_pos[0] - start_pos[0]) * (t / 100)
            interp_y = start_pos[1] + (end_pos[1] - start_pos[1]) * (t / 100)

            screen.fill((30, 30, 30))  # Limpa a tela com a cor preta
            draw_graph(screen, positions, edges, path[:i], color_path, edge_colors, visited_nodes)
            pygame.draw.line(screen, color_path, start_pos, (interp_x, interp_y), 4)
            pygame.draw.circle(screen, color_path, (int(interp_x), int(interp_y)), 10)
            pygame.display.flip()
            clock.tick(60)

        # Após a bolinha chegar ao vértice de destino
        edge_colors[(start_node, end_node)] = color_path
        edge_colors[(end_node, start_node)] = color_path  # Caso o grafo não seja direcionado
        visited_nodes.add(end_node)  # Marca o vértice de destino como visitado

        # Atualiza a tela para exibir o vértice de destino na cor vermelha
        screen.fill((30, 30, 30))
        draw_graph(screen, positions, edges, path[:i + 1], color_path, edge_colors, visited_nodes)
        pygame.display.flip()

    # Marca o último vértice como visitado
    final_node = path[-1]
    visited_nodes.add(final_node)

    final_pos = positions[final_node]
    screen.fill((30, 30, 30))
    draw_graph(screen, positions, edges, path, color_path, edge_colors, visited_nodes)
    pygame.draw.circle(screen, color_path, final_pos, 10)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        clock.tick(60)


# Função draw_graph atualizada
def draw_graph(screen, positions, edges, path, color_path, edge_colors, visited_nodes):
    for v1, v2 in edges:
        start_pos = positions[v1]
        end_pos = positions[v2]
        edge_color = edge_colors.get((v1, v2), (169, 169, 169))
        pygame.draw.line(screen, edge_color, start_pos, end_pos, 2)

    for node, pos in positions.items():
        # Define a cor do vértice: vermelho para visitados, azul para não visitados
        node_color = (255, 0, 0) if node in visited_nodes else (0, 128, 255)
        pygame.draw.circle(screen, node_color, pos, 20)
        font = pygame.font.Font(None, 24)
        text = font.render(str(node), True, (255, 255, 255))
        screen.blit(text, (pos[0] - 10, pos[1] - 10))

# Função para exibir a tela inicial
def display_start_screen(screen, clock):
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    button_rect = pygame.Rect(300, 250, 250, 60)
    button_run_cpp = pygame.Rect(300, 350, 250, 60)

    while True:
        screen.fill((30, 30, 30))
        title_text = font.render("Caminho Hamiltoniano", True, (255, 255, 255))
        button_text = small_font.render("Criar Grafo", True, (255, 255, 255))
        text_run_cpp = small_font.render("Executar Caminho", True, (255, 255, 255))

        screen.blit(title_text, (250, 150))
        pygame.draw.rect(screen, (0, 128, 255), button_rect, border_radius=8)
        screen.blit(button_text, (button_rect.x + 65, button_rect.y + 20))

        pygame.draw.rect(screen, (0, 128, 255), button_run_cpp, border_radius=8)
        screen.blit(text_run_cpp, (button_run_cpp.x + 30, button_run_cpp.y + 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return "create_graph"
                if button_run_cpp.collidepoint(event.pos):
                    return "execute_path"


        clock.tick(30)

def get_random_graph_data_interface(screen, clock):
    pygame.font.init()
    font = pygame.font.Font(None, 32)
    input_box = {'value': '', 'rect': pygame.Rect(300, 250, 250, 40), 'active': False}
    thread_input_box = {'value': '', 'rect': pygame.Rect(300, 330, 250, 40), 'active': False}

    button_rect = pygame.Rect(300, 400, 250, 50)

    while True:
        screen.fill((30, 30, 30))

        # Renderiza o prompt e a caixa para "Número de vértices"
        prompt_surface = font.render("Número de vértices:", True, (255, 255, 255))
        screen.blit(prompt_surface, (input_box['rect'].x, input_box['rect'].y - 30))
        color = (0, 128, 255) if input_box['active'] else (200, 200, 200)
        pygame.draw.rect(screen, color, input_box['rect'], 2)
        text_surface = font.render(input_box['value'], True, (255, 255, 255))
        screen.blit(text_surface, (input_box['rect'].x + 5, input_box['rect'].y + 5))

        # Renderiza o prompt e a caixa para "Quantidade de threads"
        thread_prompt_surface = font.render("Quantidade de threads:", True, (255, 255, 255))
        screen.blit(thread_prompt_surface, (thread_input_box['rect'].x, thread_input_box['rect'].y - 30))
        thread_color = (0, 128, 255) if thread_input_box['active'] else (200, 200, 200)
        pygame.draw.rect(screen, thread_color, thread_input_box['rect'], 2)
        thread_text_surface = font.render(thread_input_box['value'], True, (255, 255, 255))
        screen.blit(thread_text_surface, (thread_input_box['rect'].x + 5, thread_input_box['rect'].y + 5))

        # Renderiza o botão "Procurar"
        pygame.draw.rect(screen, (0, 128, 255), button_rect, border_radius=8)
        button_text = font.render("Procurar", True, (255, 255, 255))
        screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2,
                                  button_rect.y + (button_rect.height - button_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                input_box['active'] = input_box['rect'].collidepoint(event.pos)
                thread_input_box['active'] = thread_input_box['rect'].collidepoint(event.pos)

                # Verifica clique no botão "Procurar"
                if button_rect.collidepoint(event.pos):
                    if input_box['value'].isdigit() and thread_input_box['value'].isdigit():
                        num_vertices = int(input_box['value'])
                        num_threads = int(thread_input_box['value'])
                        edges = create_random_graph(num_vertices)
                        directed = 0
                        return num_vertices, edges, directed, num_threads

            if event.type == pygame.KEYDOWN:
                if input_box['active']:
                    if event.key == pygame.K_RETURN:
                        input_box['active'] = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_box['value'] = input_box['value'][:-1]
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        input_box['value'] += pyperclip.paste()
                    else:
                        input_box['value'] += event.unicode
                elif thread_input_box['active']:
                    if event.key == pygame.K_RETURN:
                        thread_input_box['active'] = False
                    elif event.key == pygame.K_BACKSPACE:
                        thread_input_box['value'] = thread_input_box['value'][:-1]
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        thread_input_box['value'] += pyperclip.paste()
                    else:
                        thread_input_box['value'] += event.unicode

        clock.tick(30)

def get_graph_data_interface(screen, clock):
    pygame.font.init()
    font = pygame.font.Font(None, 25)
    margin_left = 50
    input_boxes = [
        {'prompt': 'Quantidade de vértices:', 'value': '', 'rect': pygame.Rect(margin_left, 80, 400, 32), 'active': False},
        {'prompt': 'Quantidade de arestas:', 'value': '', 'rect': pygame.Rect(margin_left, 160, 400, 32), 'active': False},
        {'prompt': 'Quantidade de threads:', 'value': '', 'rect': pygame.Rect(margin_left, 240, 400, 32), 'active': False},  # Novo input
    ]
    adjacency_list_box = {
        'prompt': 'Lista de adjacências (um par por linha):',
        'value': '',
        'rect': pygame.Rect(margin_left, 320, 700, 200),
        'active': False,
        'scroll_offset': 0
    }

    # Botões de escolha "Sim" e "Não"
    directed_prompt = 'É direcionado?'
    button_sim_rect = pygame.Rect(300, 580, 70, 40)
    button_nao_rect = pygame.Rect(380, 580, 70, 40)
    directed_choice = None  # Nenhuma escolha inicial

    # Botão "Procurar"
    button_rect = pygame.Rect(300, 640, 200, 50)

    while True:
        screen.fill((30, 30, 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for box in input_boxes:
                    box['active'] = box['rect'].collidepoint(event.pos)

                adjacency_list_box['active'] = adjacency_list_box['rect'].collidepoint(event.pos)

                # Verifica seleção dos botões "Sim" e "Não"
                if button_sim_rect.collidepoint(event.pos):
                    directed_choice = 1
                elif button_nao_rect.collidepoint(event.pos):
                    directed_choice = 0

                # Verifica clique no botão "Procurar"
                if button_rect.collidepoint(event.pos):
                    if all(box['value'] for box in input_boxes) and adjacency_list_box['value'] and directed_choice != None:
                        adjacency_list = []
                        for line in adjacency_list_box['value'].strip().split('\n'):
                            v1, v2 = map(int, line.split())
                            adjacency_list.append((v1, v2))

                        num_vertices = int(input_boxes[0]['value'])
                        num_edges = int(input_boxes[1]['value'])
                        num_threads = int(input_boxes[2]['value'])  # Lê a quantidade de threads
                        return num_vertices, adjacency_list, directed_choice, num_threads

            if event.type == pygame.KEYDOWN:
                for box in input_boxes:
                    if box['active']:
                        if event.key == pygame.K_RETURN:
                            box['active'] = False
                        elif event.key == pygame.K_BACKSPACE:
                            box['value'] = box['value'][:-1]
                        elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            box['value'] += pyperclip.paste()
                        else:
                            box['value'] += event.unicode

                if adjacency_list_box['active']:
                    if event.key == pygame.K_RETURN:
                        adjacency_list_box['value'] += '\n'
                    elif event.key == pygame.K_BACKSPACE:
                        adjacency_list_box['value'] = adjacency_list_box['value'][:-1]
                    elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        adjacency_list_box['value'] += pyperclip.paste()
                    else:
                        adjacency_list_box['value'] += event.unicode

            # Controle de rolagem para a lista de adjacências
            if adjacency_list_box['active']:
                if event.type == pygame.MOUSEWHEEL:
                    adjacency_list_box['scroll_offset'] -= event.y * 20
                    max_scroll = max(0, len(adjacency_list_box['value'].split('\n')) * 28 - adjacency_list_box['rect'].height + 10)
                    adjacency_list_box['scroll_offset'] = max(0, min(adjacency_list_box['scroll_offset'], max_scroll))

        # Renderiza os prompts e as caixas de input
        for box in input_boxes:
            prompt_surface = font.render(box['prompt'], True, (255, 255, 255))
            screen.blit(prompt_surface, (box['rect'].x, box['rect'].y - 30))
            color = (0, 128, 255) if box['active'] else (200, 200, 200)
            pygame.draw.rect(screen, color, box['rect'], 2)
            text_surface = font.render(box['value'], True, (255, 255, 255))
            screen.blit(text_surface, (box['rect'].x + 5, box['rect'].y + 5))

        # Renderiza o prompt e a caixa de lista de adjacências com rolagem
        adj_color = (0, 128, 255) if adjacency_list_box['active'] else (200, 200, 200)
        adj_prompt_surface = font.render(adjacency_list_box['prompt'], True, (255, 255, 255))
        screen.blit(adj_prompt_surface, (adjacency_list_box['rect'].x, adjacency_list_box['rect'].y - 30))
        pygame.draw.rect(screen, adj_color, adjacency_list_box['rect'], 2)

        # Define uma área de recorte para renderizar o texto dentro da caixa
        clip_rect = pygame.Rect(
            adjacency_list_box['rect'].x + 5,
            adjacency_list_box['rect'].y + 5,
            adjacency_list_box['rect'].width - 10,
            adjacency_list_box['rect'].height - 10
        )
        screen.set_clip(clip_rect)

        # Renderiza as linhas de texto visíveis dentro da área da caixa
        adj_lines = adjacency_list_box['value'].split('\n')
        line_height = 28
        for i, line in enumerate(adj_lines):
            y_position = i * line_height - adjacency_list_box['scroll_offset']
            # Renderiza apenas as linhas visíveis
            if clip_rect.top <= adjacency_list_box['rect'].y + 5 + y_position < clip_rect.bottom:
                line_surface = font.render(line, True, (255, 255, 255))
                screen.blit(line_surface, (adjacency_list_box['rect'].x + 5, adjacency_list_box['rect'].y + 5 + y_position))

        # Remove a área de recorte
        screen.set_clip(None)

        # Renderiza os botões "Sim" e "Não"
        directed_prompt_surface = font.render(directed_prompt, True, (255, 255, 255))
        screen.blit(directed_prompt_surface, (margin_left, 540))  # Novo posicionamento do texto

        # Ajusta as posições dos botões "Sim" e "Não" ao lado do texto
        button_sim_rect.topleft = (margin_left + 200, 530)  # Botão "Sim" à direita do texto
        button_nao_rect.topleft = (margin_left + 280, 530)  # Botão "Não" ao lado do "Sim"

        # Renderiza os botões "Sim" e "Não"
        sim_color = (0, 128, 255) if directed_choice == 1 else (200, 200, 200)
        nao_color = (0, 128, 255) if directed_choice == 0 else (200, 200, 200)
        pygame.draw.rect(screen, sim_color, button_sim_rect, border_radius=8)
        pygame.draw.rect(screen, nao_color, button_nao_rect, border_radius=8)

        sim_text = font.render("Sim", True, (255, 255, 255))
        nao_text = font.render("Não", True, (255, 255, 255))

        screen.blit(sim_text, (button_sim_rect.x + (button_sim_rect.width - sim_text.get_width()) // 2,
                            button_sim_rect.y + (button_sim_rect.height - sim_text.get_height()) // 2))
        screen.blit(nao_text, (button_nao_rect.x + (button_nao_rect.width - nao_text.get_width()) // 2,
                            button_nao_rect.y + (button_nao_rect.height - nao_text.get_height()) // 2))

        # Renderiza o botão "Procurar"
        if all(box['value'] for box in input_boxes) and adjacency_list_box['value'] and directed_choice != None:
            pygame.draw.rect(screen, (0, 128, 255), button_rect, border_radius=8)
        else:
            pygame.draw.rect(screen, (128, 128, 128), button_rect, border_radius=8)

        button_text = font.render("Procurar", True, (255, 255, 255))
        button_rect.topleft = (margin_left + 200, 580)

        screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2,
                                  button_rect.y + (button_rect.height - button_text.get_height()) // 2))
        pygame.display.flip()
        clock.tick(30)


# Função para obter o caminho Hamiltoniano usando o programa C++
def get_hamiltonian_path(num_vertices, edges, is_directed, num_threads):
    input_data = f"{num_vertices}\n{len(edges)}\n"
    input_data += "\n".join(f"{v1} {v2}" for v1, v2 in edges)
    input_data += f"\n{is_directed}\n"
    input_data += f"\n{num_threads}\n"
    try:
        result = subprocess.run(
            ["./concurrent_hamilton"], input=input_data, capture_output=True, text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            lines = output.splitlines()
            if lines:
                last_line = lines[-1]
                numbers = re.findall(r'\d+', last_line)
                hamiltonian_path = [int(num) for num in numbers]
                print("Caminho Hamiltoniano encontrado:", hamiltonian_path)
                return hamiltonian_path
            else:
                print("Saída vazia do programa C++.")
                return None
        else:
            print("Erro ao executar o programa C++:", result.stderr)
            return None

    except Exception as e:
        print("Erro ao tentar executar o programa C++:", e)
        return None

# Função principal para rodar a interface
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Visualizador de Caminho Hamiltoniano")
    clock = pygame.time.Clock()

    # Exibe a tela inicial
    choice = display_start_screen(screen, clock)

    # Navega conforme a escolha
    if choice == "create_graph":
        try:
            num_vertices, edges, is_directed, num_threads = get_graph_data_interface(screen, clock)
        except Exception as e:
            print("Erro ao coletar dados do grafo:", e)
            pygame.quit()
            return
    elif choice == "execute_path":
        try:
            num_vertices, edges, is_directed, num_threads = get_random_graph_data_interface(screen, clock)
        except Exception as e:
            print("Erro ao coletar dados do grafo:", e)
            pygame.quit()
            return

    center = (400, 300)
    scale = 250

    positions = calculate_positions_spring(num_vertices, edges)
    pygame_positions = convert_positions_to_pygame(positions, center, scale)

    hamiltonian_path = get_hamiltonian_path(num_vertices, edges, is_directed, num_threads)

    if not hamiltonian_path:
        print("Nenhum caminho Hamiltoniano encontrado.")
        pygame.quit()
        return

    background_color = (30, 30, 30)
    color_path = (255, 0, 0)
    color_default = (169, 169, 169)

    animate_path(screen, pygame_positions, edges, hamiltonian_path, color_path, color_default, clock)
    pygame.quit()

if __name__ == "__main__":
    main()
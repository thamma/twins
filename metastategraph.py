import random
import json

import resourcemanager


class Node:
    def __init__(self, node_id, texts=None, images=None):
        self.id = node_id
        self.texts = texts
        self.images = images
        self.text_gen = None
        self.image_gen = None
        self.action = None
        self.exit_action = None
        self.edges = []

    def get_text(self, state):
        if self.text_gen is not None:
            texts = self.text_gen(state)
            if isinstance(texts, str):
                texts = [texts]
        else:
            texts = self.texts

        return random.choice(texts)

    def get_image(self, state):
        if self.image_gen is not None:
            imgs = self.image_gen(state)

            if imgs is None or len(imgs) < 1:
                return None

            if isinstance(imgs, str):
                imgs = [imgs]

            return random.choice(imgs)
        else:
            return self.images

    def add_text_gen(self, f):
        self.text_gen = f

    def on_enter(self, state):
        if self.action is not None:
            self.action(state)

    def on_exit(self, state):
        if self.exit_action is not None:
            self.exit_action(state)

    def add_action(self, f):
        self.action = f

    def add_exit_action(self, f):
        self.exit_action = f

    def add_image_gen(self, f):
        self.image_gen = f

    def add_edge(self, edge_id):
        self.edges.append(edge_id)


class Edge:
    def __init__(self, edge_id, target, label=None, guard=None):
        self.id = edge_id
        self.target = target
        self.label = label
        self.guard = guard
        self.action = None

    def is_valid(self, state):
        return self.guard is None or self.guard(state)

    def on_taken(self, state):
        if self.action is not None:
            self.action(state)

    def add_guard(self, f):
        self.guard = f

    def add_action(self, f):
        self.action = f

    def add_label(self, label):
        self.label = label


class MetaGameState:
    def __init__(self):
        self.pos = {0: 'init', 1: 'init'}
        self.current_player = 0
        self.env = {f.__name__: f for f in [
            self.teleport
        ]}
        self.quicksave = {}

    def update_env(self):
        self.env['player'] = self.current_player
        self.env['other_player'] = self.other_player

    @property
    def other_player(self):
        return 1 - self.current_player

    def teleport(self, player_id, node_id):
        self.pos[player_id] = node_id

    def save(self):
        for k in self.env:
            self.quicksave[k] = self.env[k]

    def reset(self):
        self.pos = {0: 'init', 1: 'init'}
        self.env = {}
        for k in self.quicksave:
            self.env[k] = self.quicksave[k]


class MetaStateGraph:
    def __init__(self):
        self.nodes = {}  # node_id : Node
        self.edges = {}  # edge_id : Edge
        self.gamestate = MetaGameState()

        self.resourcemanager = resourcemanager.ResourceManager("res")

    def get_transitions(self, player_id):
        self.gamestate.current_player = player_id
        self.gamestate.update_env()

        current_node = self.nodes[self.gamestate.pos[player_id]]
        result = {"text": current_node.get_text(self.gamestate), "transitions": {}}

        img = current_node.get_image(self.gamestate)
        if img is not None:
            result['image'] = self.resourcemanager.get_image(img)

        for edge_id in current_node.edges:
            edge = self.edges[edge_id]
            if edge.is_valid(self.gamestate):
                result["transitions"][edge_id] = eval('f{}'.format(repr(edge.label)), None, self.gamestate.env)

        return result

    def step(self, player_id, edge_id):
        self.gamestate.current_player = player_id
        self.gamestate.update_env()

        old_node = self.nodes[self.gamestate.pos[player_id]]
        old_node.on_exit(self.gamestate)
        edge = self.edges[edge_id]
        edge.on_taken(self.gamestate)
        node = self.nodes[edge.target]
        self.gamestate.pos[player_id] = node.id
        node.on_enter(self.gamestate)

        # print(f'step: {player_id}, {old_node.id} --[{edge.id}]-> {node.id}')

    def node(self, node_id, text=None, image=None):
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        if isinstance(text, str):
            text = [text]
        new_node = Node(node_id, texts=text, images=image)
        self.nodes[node_id] = new_node

        def wrapper(f):
            new_node.add_text_gen(f)
            return wrapper

        def enter(f):
            new_node.add_action(f)

        def exit(f):
            new_node.add_exit_action(f)

        def image(f):
            new_node.add_image_gen(f)

        wrapper.enter = enter
        wrapper.exit = exit
        wrapper.image = image
        return wrapper

    def edge(self, start, target, label=None, guard=None):
        edge_id = start + target
        while edge_id in self.edges:
            edge_id += '\''

        new_edge = Edge(edge_id, target, label=label, guard=guard)
        self.edges[edge_id] = new_edge
        self.nodes[start].add_edge(edge_id)

        def wrapper(f):
            if f.__doc__:
                new_edge.add_label(f.__doc__)
            new_edge.add_action(f)
            return wrapper

        def guard(f):
            new_edge.add_guard(f)

        wrapper.guard = guard
        return wrapper

    def add_json_node(self, id, texts, images=None, on_enter=None, on_exit=None, on_empty=None, on_occupied=None, **kwargs):
        @self.node(id)
        def node_obj(state):
            # print(f'text_gen {id}')
            results = []
            for opt in texts:
                if eval(opt.get('guard', 'True'), None, state.env):
                    if isinstance(opt['text'], list):
                        text = ''.join(opt['text'])
                    else:
                        text = opt['text']
                    res = eval('f{}'.format(repr(text)), None, state.env)
                    results.append(res)
            return results

        @node_obj.image
        def _(state):
            if images is None:
                return []
            results = []
            for opt in images:
                if eval(opt.get('guard', 'True'), None, state.env):
                    results.append(opt['path'])
            return results

        @node_obj.enter
        def _(state):
            if on_enter is not None:
                exec(on_enter, None, state.env)

            if on_occupied is not None:
                if state.pos[state.other_player] != id:
                    exec(on_occupied, None, state.env)

        @node_obj.exit
        def _(state):
            if on_exit is not None:
                exec(on_exit, None, state.env)

            if on_empty is not None:
                if state.pos[state.other_player] != id:
                    exec(on_empty, None, state.env)

    def add_json_edge(self, start, target, label, guard=None, action=None, sync=None, **kwargs):
        @self.edge(start, target, label)
        def edge_obj(state):
            if action is not None:
                exec(action, None, state.env)
            if sync is not None:
                state.pos[state.other_player] = target

        if guard is not None:

            @edge_obj.guard
            def _(state):
                try:
                    return eval(guard, None, state.env)
                except NameError:
                    print(f'NameError in {repr(guard)}')
                    return False

    def read_json_file(self, fname):
        with open(fname, "r") as f:
            json_obj = json.load(f)

        edges_queue = []

        for node in json_obj["nodes"]:

            self.add_json_node(**node)

            for e in node['edges']:
                edges_queue.append({'start': node['id'], **e})

        for edge in edges_queue:
            self.add_json_edge(**edge)

        env = json_obj['env']
        for name in env:
            self.gamestate.env[name] = eval(env[name], None, None)

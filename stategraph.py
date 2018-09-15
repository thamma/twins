import metastategraph

Graph = metastategraph.MetaStateGraph()

Graph.read_json_file("intro.json")
Graph.read_json_file("twobuttons.json")
Graph.read_json_file("ktane.json")
Graph.read_json_file("jojo.json")

Graph.edge("2btn_r1", "jojo_1", label="Untersuche die Maske")
Graph.edge("jojo_2", "2btn_r1", label="NANI?!?")

Graph.edge("intro_exit", "2btn_init", label="Ruine betreten")

# -------------------- Tetraeder-Maze --------------------

maze_nodes = []

maze_colors = [
    "Rot",
    "Gelb",
    "Grün",
    "Magenta",
    "Blau",
    "Violett",
    "Blau",
    "Cyan",
    "Blau",
    "Grün",
    "Rot",
    "Grün",
    "Grün",
    "Gelb",
    "Blau",
    "Orange"
]
enter_texts = ["Du betrittst einen ovalen Raum.", "Du findest dich in einem hohen, dreieckigen Raum wieder.", "Vor dir befindet sich ein großer, fast kreisrunder Raum.", "Du passierst die Tür und betrittst einen großen Raum.", "Du findest dich in einem länglichen Raum - fast ein Korridor - wieder."]
doors_texts = ["Dir gegenüber siehst du zwei hölzerne Türen.", "Du siehst zwei Türen vor dir.", "Es befinden sich drei Türen in dem Raum.", "Du siehst zwei offene Türen."]
color_fluff = [
        "Gusseiserne Kettenglieder stehen aufrecht und bilden einen Kerzenständer. Eine rote, sehr verlaufene Kerze spendet wenig, flackerndes Licht.",
        "Viele Meter in der Höhe siehst du Metallgitter. Wasser tropft von oben herab und du siehst Tageslicht. Ein wohliges Gefühl erfüllt dich.",
        "Ehe du dich versiehst, rutschst du in einer Pfütze fast auf dem nassen Moos aus. Ein eisiger Wind weht aus der rechten Tür.",
        "An zwei Wänden befinden sich zwei weiße Kerzen in Wandhalterungen. Eine ist entzündet und strahlt violettes Licht aus. Dieser Ort wirkt magisch.",
        "Der Weg aus dem du kamst bricht aprupt ab. Wenige Centimeter unter dem Rand der Steinplatform befindet sich trübes Wasser. Ohne dieses zu durchqueren wirst du es nicht zu den gegenüberliegenden Vorsprüngen schaffen.",
        "Ein dichter Nebel hüllt alles unterhalb deiner Hüfte ein. Sehn wohin du trittst kannst du kaum. Vereinzelt trittst du gegen ein Häufchen menschlicher Knochen.",
        "Eine Kule in der Mitte des Raumes birgt Feuerholz und einige Stücke Holzkohle. Die Feuerstelle ist noch warm. Jemand war hier kürzlich.",
        "Die kalten Steinwände tragen weiße Zeichnungen mit roten Aktzenten. Dir schaudert es. Es ist Zeit weiterzugehen.",
        "Ratten zehren an unidentifizierbaren Resten eines Lebewesens auf dem Boden. Ein maximal scheußlicher Gestank schießt dir in die Nase. Du rennst an dem Kadaver vorbei zur nächsten Tür.",
        "Die Raumdecke ist defekt, Licht schimmert von oben herab. Efeu und weitere Rankenpflanzen versperren die Sicht. Die hohe Luftfeuchte erschwert es dir zu atmen.",
        "Rote unleserliche Glyphen sind in einem Kreis auf dem Boden geschrieben. In der Mitte des Kreises steht ein Kessel mit einer brodelnden blutroten Flüssigkeit.",
        "In der Mitte des Raumes liegt ein großer Haufen Gestein. Scheibar ist ein Felsbrocken aus der Decke gebrochen und zerschlagen.",
        "Holzdielen zieren den Boden. Die Seiten eines zerfledderten Buches liegen verstreut umher.",
        "Zahlreiche Kiesel liegen im Raum verstreut.",
        "Zahlreiche Glühwürmchen erhellen den Raum.",
        "Du hörst ein leises, tiefes Summen. Ein mystisches Gefühl durchströmt dich."

]
random_fluff_pre = ["", "Die Tür aus der du gekommen bist, fällt ins Schloss.",
        "", "",
        "Aus der rechten Tür hörst du das Echo von Schritten.", "Ein Schwarm fliegen schwirrt um dich herum.",
        "Du reißt ein großes Spinnennetz mit.", "",
        "","Eine Ratte rennt erschrocken durch die Tür zu deiner Rechten."]
random_fluff_post = ["Du meinst etwas gehört zu haben.", "",
        "Ein eiskalter Wassertropfen fällt dir von der Decke in den Nacken.", "",
        "", "",
        "", "",
        "Du hörst, wie Wassertropfen von der Decke auf dem Boden aufschlagen.", ""]
from random import shuffle
shuffle(random_fluff_pre)
shuffle(random_fluff_post)
tetra_texts = {
    i: f"{enter_texts[i%len(enter_texts)]} {doors_texts[i%len(doors_texts)]} {random_fluff_pre[i%len(random_fluff_pre)]} <br><br> {color_fluff[i%len(color_fluff)]} {random_fluff_post[i%len(random_fluff_post)]}" for i in range(16)
}


def maze_add_node(room_num, view):
    node_id = f"maze_{room_num}_{view}"

    @Graph.node(node_id)
    def _(state):
        return tetra_texts[room_num]

    maze_nodes.append(node_id)


for room_num in range(16):
    if room_num in [0, 2, 4, 6, 7, 9, 11, 12, 14, 15]:
        views = [1, 3, 5]
    else:
        views = [0, 2, 4]

    for view in views:
        maze_add_node(room_num, view)


def maze_connect(room, u=None, ur=None, dr=None, d=None, dl=None, ul=None):
    room_a = f"maze_{room}"

    for (i, room2) in enumerate([u, ul, dl, d, dr, ur]):
        if room2 is None:
            continue

        room_b = f"maze_{room2}"

        Graph.edge(f"{room_a}_{(i+3)%6}", f"{room_b}_{i}", label="Gehe nach hinten")
        Graph.edge(f"{room_a}_{(i+5)%6}", f"{room_b}_{i}", label="Gehe nach links")
        Graph.edge(f"{room_a}_{(i+1)%6}", f"{room_b}_{i}", label="Gehe nach rechts")


def maze_nonplanar_edge(room1, view1, room2, view2):
    room_b = f"maze_{room2}_{view2}"

    Graph.edge(f"maze_{room1}_{(view1+3)%6}", room_b, label="Gehe nach hinten")
    Graph.edge(f"maze_{room1}_{(view1+5)%6}", room_b, label="Gehe nach links")
    Graph.edge(f"maze_{room1}_{(view1+1)%6}", room_b, label="Gehe nach rechts")


maze_connect(0, dr=1)
maze_connect(1, ul=0, ur=2, d=7)
maze_connect(2, dl=1, dr=3)
maze_connect(3, ul=2, ur=4, d=9)
maze_connect(4, dl=3, dr=5)
maze_connect(5, ul=4, ur=6, d=11)
maze_connect(6, dl=5)
maze_connect(7, u=1, dr=8)
maze_connect(8, ul=7, ur=9, d=12)
maze_connect(9, u=3, dl=8, dr=10)
maze_connect(10, ul=9, ur=11, d=14)
maze_connect(11, u=5, dl=10)
maze_connect(12, u=8, dr=13)
maze_connect(13, ul=12, ur=14, d=15)
maze_connect(14, u=10, dl=13)
maze_connect(15, u=13)

maze_nonplanar_edge(0, 0, 6, 3)
maze_nonplanar_edge(0, 2, 15, 5)
maze_nonplanar_edge(2, 0, 4, 3)
maze_nonplanar_edge(4, 0, 2, 3)
maze_nonplanar_edge(6, 0, 0, 3)
maze_nonplanar_edge(6, 4, 15, 1)
maze_nonplanar_edge(7, 2, 12, 5)
maze_nonplanar_edge(11, 4, 14, 1)
maze_nonplanar_edge(12, 2, 7, 5)
maze_nonplanar_edge(14, 4, 11, 1)
maze_nonplanar_edge(15, 2, 0, 5)
maze_nonplanar_edge(15, 4, 6, 1)

Graph.node("maze_exit", text="You got out of the maze :D")

for node_id in maze_nodes:
    Graph.nodes[node_id].edges.sort(key=lambda e: Graph.edges[e].label)


    @Graph.edge(node_id, "maze_exit", label="Leave maze")
    def edge(s):
        s.pos[s.other_player] = "maze_exit"


    @edge.guard
    def _(s):
        if not s.pos[s.other_player].startswith("maze_"):
            return False
        a = s.pos[s.current_player].split("_")[1]
        b = s.pos[s.other_player].split("_")[1]
        return a == b

Graph.edge("2btn_exit_A", "ktane_spawn_A", label="Ahhh!", guard=lambda s: s.env["_2btn_barrier"] == 2)
Graph.edge("2btn_exit_B", "ktane_spawn_B", label="Ahhh!", guard=lambda s: s.env["_2btn_barrier"] == 2)

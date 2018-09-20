# Twins birthday present
A text adventure encoded as non-regular state graph in JSON. The `metastategraph.py` file takes care of the encoding format. The `stategraph.py` file stitches together the individual `.json` stategraphs and takes care of some automation that would otherwise be too tedious to implement in the stategraph format.

## The stategraph format
At top level, there are two objects: a list of `nodes` and `env`. `env`, the environment initializes variables used later

A `node` object must have an internal, unique `id` string. It can provide a list of text objects, called `texts`. `texts` contains all possible texts a state can display (see guards). A text object consists of its `text` (a list of strings to display; the strings will be concatenated, but it aids with readability to split the lines). It must also contain a (possiby empty) list of `edges`.

`edges` must contain a `label` that refers to another states `id` and a `label` string to display.

## The stategraph magic
Any `edge`, or text object inside of a nodes `texts` may have a `guard`. A `guard` is a valid python expression that is evaluated (using `eval`) at play time. The edge or state text is shown iff the `guard` expression evaluates to true.

To make `guard`s infinitely useful, edges can have `action`s. An action is valid python code to be executed upon taking the transition. Similarly to `action`s, states may have an `on_enter` field that contains code to be executed upon visiting that state.


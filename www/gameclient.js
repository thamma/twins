const ws = new WebSocket("ws://" + location.hostname + ":51862/"),
    options = [];

const get_param = name => {
    if (name = (new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)')).exec(location.search))
        return decodeURIComponent(name[1]);
};

ws.onopen = () => ws.send(get_param('hello') || "hello");

let selection = 0,
    waiting = true;

const emojify = emojione.toImage;

$("#topdots").click(() => {
    if (options.length < 1) {
        return;
    }
    selection = (selection + options.length - 1) % options.length;
    updateCursor();
});

$("#bottomdots").click(() => {
    if (options.length < 1) {
        return;
    }
    selection = (selection + options.length + 1) % options.length;
    updateCursor();
});

const updateState = state => {

    const imgbox = $("#imagebox");

    let option;
    while (option = options.pop()) {
        let [elem] = option;
        elem.remove();
    }

    $("#textbox").html(emojify(state.text));

    if (state.image) {
        imgbox.attr("src", state.image);
        imgbox.show();
    } else {
        imgbox.hide();
    }

    for (let key in state.transitions) {
        const text = state.transitions[key];
        const elem = $("<div class='option'></divclass>"),
            leftcursor = $("<span class='cursor'>&gt;</span>"),
            inner = $("<span></span>"),
            rightcursor = $("<span class='cursor'>&lt;</span>");

        inner.html(emojify(text));

        elem.append(leftcursor);
        elem.append(inner);
        elem.append(rightcursor);

        $("#bottomdots").before(elem);
        options.push([elem, key]);

        const i = options.length - 1;

        inner.click(() => {
            if (selection !== i) {
                selection = i;
                updateCursor();
            } else {
                submit();
            }
        });

        inner.css("cursor", "pointer");
    }

    selection = Math.max(0, Math.min(selection, options.length - 1));
    updateCursor();
};

const updateCursor = () => {

    const k = 3, topdots = $("#topdots"), bottomdots = $("#bottomdots");

    // show/hide dots
    if (selection - k - 1 < 0) {
        topdots.hide();
    } else {
        topdots.show();
    }

    if (selection + k + 1 > options.length - 1) {
        bottomdots.hide();
    } else {
        bottomdots.show();
    }

    for (let j in options) {
        let [elem] = options[j];
        const i = parseInt(j);

        if (selection - k <= i && i <= selection + k) {
            elem.show();
        } else {
            elem.hide();
        }

        if (i === selection) {
            elem.children(".cursor").show();
        } else {
            elem.children(".cursor").hide();
        }
    }
};

ws.onmessage = msg => {
    const event = JSON.parse(msg.data),
        waitbox = $("#waiting"),
        textbox = $("#textbox"),
        container = $("#container");

    switch (event.type) {
        case 'nope':
            waitbox.hide();
            textbox.html('Game full :(');
            document.title = ":(";
            break;

        case 'gogo':
            waiting = false;
            waitbox.hide();
            container.css("color", "white");
            break;

        case 'wait':
            waiting = true;
            waitbox.show();
            container.css("color", "gray");
            break;

        case 'state':
            updateState(event.state);
            break;

        default:
            break;
    }
};

const submit = () => {
    let [_, key] = options[selection];
    ws.send(key);
    selection = 0;
};

$("body").keydown(e => {
    if (waiting || options.length < 1) {
        return;
    }

    switch (e.keyCode) {

        case 38: // up arrow
            selection = (selection + options.length - 1) % options.length;
            break;

        case 40: // down arrow
            selection = (selection + options.length + 1) % options.length;
            break;

        case 13: // enter
            if (!(selection in options)) {
                return;
            }
            submit();
            break;

        default:
            break;
    }
    updateCursor();
});

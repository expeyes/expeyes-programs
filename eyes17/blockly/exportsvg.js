var DOMURL = self.URL || self.webkitURL || self;

function getsvg(){
    canvas = Blockly.mainWorkspace.svgBlockCanvas_.cloneNode(true);
    if (canvas.children[0] === undefined) throw "Couldn't find Blockly canvas."

    canvas.removeAttribute("transform");

    var css = '<defs><style type="text/css" xmlns="http://www.w3.org/1999/xhtml"><![CDATA[' + Blockly.Css.content + ']]></style></defs>';
    var bbox = document.getElementsByClassName("blocklyBlockCanvas")[0].getBBox();
    var content = new XMLSerializer().serializeToString(canvas);

    xml = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'
        + bbox.width + '" height="' + bbox.height + '" viewBox=" ' + bbox.x + ' ' + bbox.y + ' ' + bbox.width + ' ' + bbox.height + '">' +
        css + '">' + content + '</svg>';    

    return new Blob([xml], { type: 'image/svg+xml;base64' });
}


function getrawsvg(){
    canvas = Blockly.mainWorkspace.svgBlockCanvas_.cloneNode(true);
    if (canvas.children[0] === undefined) throw "Couldn't find Blockly canvas."

    canvas.removeAttribute("transform");

    var css = '<defs><style type="text/css" xmlns="http://www.w3.org/1999/xhtml"><![CDATA[' + Blockly.Css.content + ']]></style></defs>';
    var bbox = document.getElementsByClassName("blocklyBlockCanvas")[0].getBBox();
    var content = new XMLSerializer().serializeToString(canvas);

    xml = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'
        + bbox.width + '" height="' + bbox.height + '" viewBox=" ' + bbox.x + ' ' + bbox.y + ' ' + bbox.width + ' ' + bbox.height + '">' +
        css + '">' + content + '</svg>';
    return xml;
}


function download(url, filename){
        let element = document.createElement('a')
        element.href = url
        element.download = filename;
        element.click();
        DOMURL.revokeObjectURL(element.href)
}

function exportSVG() {
    download(DOMURL.createObjectURL(getsvg()),'blocks.svg');
}

function exportPNG(){
    var img = new Image();
    img.onload = function() {
        var canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 600;
        canvas.getContext("2d").drawImage(img, 0, 0);
        download(canvas.toDataURL("image/png"),'blocks.png');
    };
    img.src = DOMURL.createObjectURL(getsvg());
}

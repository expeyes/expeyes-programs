// https://github.com/albertaleksieiev
// https://github.com/quilljs/quill/issues/3240#issuecomment-849679016
/*
function applyGoogleKeyboardWorkaround(editor) {
    try {
        if (editor.applyGoogleKeyboardWorkaround) {
            return
        }

        editor.applyGoogleKeyboardWorkaround = true
        editor.quill.on('editor-change', function (eventName, ...args) {
            if (eventName === 'text-change') {
              // args[0] will be delta
              var ops = args[0]['ops']
              var oldSelection = editor.getSelection()
              var oldPos = oldSelection.index
              var oldSelectionLength = oldSelection.length

              if (ops[0]["retain"] === undefined || !ops[1] || !ops[1]["insert"] || !ops[1]["insert"] || ops[1]["insert"] != "\n"  || oldSelectionLength > 0) {
                return
              }

              setTimeout(function () {
                var newPos = editor.getSelection().index
                if (newPos === oldPos) {
                  console.log("Change selection bad pos")
                  editor.setSelection(editor.getSelection().index + 1, 0)
                }
              }, 30);
            }
          });
    } catch {
    }
}
*/
const toolbarOptions = [
  [{'header': [1, 2, 3, , false] }],
  ['bold', 'underline'],        // toggled buttons
  ['image','video', 'code-block', 'formula'],
  [{ 'list': 'ordered' }, { 'list': 'bullet' }],
  [{ 'script': 'sub' }, { 'script': 'super' }],      // superscript/subscript
  [{ 'indent': '-1' }, { 'indent': '+1' }],          // outdent/indent


  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  ['omega','clean']                                        // remove formatting button
];
function loadquill(){
    var helpeditor = new Quill('#quilleditor', {
    modules: {
        history: {
          delay: 2000,
          maxStack: 50,
          userOnly: true
        },
      toolbar: toolbarOptions },
    theme: 'snow',
  });
  helpeditor.disable();




    var toolbar = helpeditor.getModule("toolbar");
    toolbar.addHandler("omega", function () {
      console.log("omega");
    });
    var customButton = document.querySelector(".ql-omega");
    customButton.addEventListener("click", function () {
      var range = helpeditor.getSelection();
      if (range) {
        helpeditor.insertText(range.index, "Ω");
      }
    });




  //applyGoogleKeyboardWorkaround(helpeditor);
    return helpeditor;
}
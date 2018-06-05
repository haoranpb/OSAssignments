let sequence = new Array();
let colorList = new Array();

function add_sequence(task, size, type){
    this.task = task;
    this.size = size;
    this.type = type;
}
function add_color(color, occupy){
    this.color = color;
    this.occupy = occupy;
}

// add tasks sequence
sequence[0] = add_sequence(1, 130, 0);
sequence[1] = add_sequence(2, 60, 0);
sequence[2] = add_sequence(3, 100, 0);
sequence[3] = add_sequence(2, 60, 1);
sequence[4] = add_sequence(4, 200, 0);
sequence[5] = add_sequence(3, 100, 1);
sequence[6] = add_sequence(1, 130, 1);
sequence[7] = add_sequence(5, 140, 0);
sequence[8] = add_sequence(6, 60, 0);
sequence[9] = add_sequence(7, 50, 0);
sequence[10] = add_sequence(6, 60, 1);

colorList[0] = add_color('#0099ff', false);
colorList[1] = add_color('#3300ff', false);
colorList[2] = add_color('#f200ff', false);
colorList[3] = add_color('#00e1ff', false);
colorList[4] = add_color('#b30740', false);
colorList[5] = add_color('#00ff66', false);
colorList[6] = add_color('#525252', false);

let step = 0; // the step of task sequence

$("button#ff").click(function(){ // func for first fit
    let blockColor = '';
    for(let i = 0; i < colorList.length; i++){ // find the first available color
        if(colorList[i][occupy]==false){
            blockColor = colorList[i][color];
            break;
        }
    }
    
})

$("button#bf").click(function(){ // func for best fit
    let blockColor = '';
    for(let i = 0; i < colorList.length; i++){ // find the first available color
        if(colorList[i][occupy]==false){
            blockColor = colorList[i][color];
            break;
        }
    }
})

function clear(){

}
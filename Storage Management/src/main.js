let sequence = new Array();
let colorList = new Array();

// add task sequence
sequence[0] = new Task(1, 130, 0);
sequence[1] = new Task(2, 60, 0);
sequence[2] = new Task(3, 100, 0);
sequence[3] = new Task(2, 60, 1);
sequence[4] = new Task(4, 200, 0);
sequence[5] = new Task(3, 100, 1);
sequence[6] = new Task(1, 130, 1);
sequence[7] = new Task(5, 140, 0);
sequence[8] = new Task(6, 60, 0);
sequence[9] = new Task(7, 50, 0);
sequence[10] = new Task(6, 60, 1);

// add color list
colorList[0] = new Color('#7d3f98', false);
colorList[1] = new Color('#279b37', false);
colorList[2] = new Color('#0066CC', false);
colorList[3] = new Color('#d5641c', false);
colorList[4] = new Color('#be0027', false);
colorList[5] = new Color('#005696', false);
colorList[6] = new Color('#543729', false);

let step = 0; // the step of task sequence

$("button#ff").click(function(){ // func for first fit
    if(step>10){
        alert("The sequnence is empty. Please click Clear button to restart!");
        return;
    }
    // find the next task
    let task = sequence[step].task;
    let size = sequence[step].size;
    let type = sequence[step].type;
    step++;

    if(type == 0){ // add task
        let blockColor = ''; // find the available color
        for(let i = 0; i < colorList.length; i++){
            if(colorList[i].avail == false){
                blockColor = colorList[i].color;
                console.log(blockColor);
                colorList[i].avail = true;
                break;
            }
        }
        $("div.block").each(function(){
            if($(this).css("background-color") == "rgba(0, 0, 0, 0)"){ // if this block is empty
                if(parseInt($(this).css("height")) >= size){ // if this block is enough for the task
                    newBlock(task, $(this).css("top"), size, blockColor, this);
                    adjustEmptyBlock(size, $(this).css("top"), $(this).css("height"), this);
                    return false; // break from the loop
                }
            }
        })
    }
    else{ // delete task
        let selecter = "." + task.toString();
        deleteBlock($(selecter));
    }
})

$("button#bf").click(function(){ // func for best fit
    let blockColor = '';
    for(let i = 0; i < colorList.length; i++){
        if(colorList[i].avail == false){
            blockColor = colorList[i].color;
            colorList[i].avail = true;
            break;
        }
    }

})

$("button#clear").click(function(){

})


function newBlock(task, top, size, color, obj){
    let block = $("<div class=\"block\"></div>");
    block.css({"top": top,"height": size + "px", "background-color": color, "display": "none"});
    block.addClass(task.toString());
    $(obj).before(block);
    block.slideDown("slow");
}

function adjustEmptyBlock(size, top, height, obj){
    const newHeight = parseInt(height) - size;
    const newTop = parseInt(top) + size;
    $(obj).css({"height": newHeight + "px", "top": newTop + "px"});
}

function deleteBlock(obj){
    let prevObj = obj.prev();
    let nextObj = obj.next();
    if(prevObj.length != 0){ // previous obj exist
        if(nextObj.length != 0){ // next obj exist
            if(prevObj.css("background-color") == "rgba(0, 0, 0, 0)"){
                if(nextObj.css("background-color") == "rgba(0, 0, 0, 0)"){
                    const newHeight = parseInt(prevObj.css("height")) + parseInt(obj.css("height")) + parseInt(nextObj.css("height"));
                    prevObj.css("height", newHeight + "px");
                    nextObj.remove();
                    obj.slideUp("fast", function(){
                        obj.remove();
                    });
                }
                else{
                    const newHeight = parseInt(prevObj.css("height")) + parseInt(obj.css("height"));
                    prevObj.css("height", newHeight + "px");
                    obj.slideUp("fast", function(){
                        obj.remove();
                    });
                }
            }
            else{
                if(nextObj.css("background-color") == "rgba(0, 0, 0, 0)"){
                    const newHeight = parseInt(obj.css("height")) + parseInt(nextObj.css("height"));
                    nextObj.css({"top": obj.css("top"),"height": newHeight + "px"});
                    obj.slideUp("fast", function(){
                        obj.remove();
                    });
                }
                else{
                    let block = $("<div class=\"block\"></div>");
                    block.css({"top": obj.css("top"), "height": obj.css("height")});
                    obj.before(block);
                    obj.slideUp("fast", function(){
                        obj.remove();
                    });
                }
            }
        }
        else{
            if(prevObj.css("background-color") == "rgba(0, 0, 0, 0)"){ // if prev is empty
                const newHeight = parseInt(obj.css("height")) + parseInt(prevObj.css("height"));
                prevObj.css("height", newHeight + "px");
                obj.slideUp("fast", function(){
                    obj.remove();
                });
            }
        }
    }
    else{
        if(nextObj.length != 0){
            if(nextObj.css("background-color") == "rgba(0, 0, 0, 0)"){ // if next obj is empty
                const newHeight = parseInt(obj.css("height")) + parseInt(nextObj.css("height"));
                nextObj.css({"top": obj.css("top"), "height": newHeight + "px"});
                obj.slideUp("fast", function(){
                    obj.remove();
                });
            }
        }
        else{
            alert("Error!");
        }
    }   
}
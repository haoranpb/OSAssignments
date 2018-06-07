let missCount = 0;
let orderList = createOrderSequence(); // create order sequence
let blocks = new Array();

$(document).ready(function(){
    print("指令序列生成成功！", "blue");
})

$("#start").click(function(){
    for(let i = 0; i < orderList.length; i++){
        let page = parseInt(orderList[i]/10);
        let exist = false; // wether exist in blocks
        let blockNum = 0;
        for(let i = 0; i < blocks.length; i++){
            if(blocks[i] == page){
                exist = true;
                blockNum = i + 1;
                break;
            }
        }
        if(exist){
            print("指令" + orderList[i] + "命中！ 页" + page + "存在于物理块" + blockNum + "中", "black");
        }
        else{
            missCount++;
            if(blocks.length < 4){ // there are empty blocks 
                blocks.push(page);
                print("指令" + orderList[i] + "未命中！ 页" + page + "加入物理块", "#FF9900");
            }
            else{
                let out = blocks.shift();
                blocks.push(page);
                print("指令" + orderList[i] + "未命中！ 页" + out + "移出物理块；页" + page + "放入物理块", "#FF9900");
            }
        }
    }
    $("#result").find("p.info").text("缺页次数：" + missCount);
})

function print(message, color){
    let txt = $("<div class='txt'></div>").text(message);
    txt.css("color", color);
    $("#dashboard").append(txt);
}

function createOrderSequence(){
    let list = new Array();

    let newOrder = getRandomInt(0, 320);
    list.push(newOrder);
    list.push(newOrder + 1);

    let orderCount = 2;
    while(orderCount < 320){
        newOrder = getRandomInt(0, newOrder);
        list.push(newOrder);
        list.push(newOrder + 1);
        orderCount = orderCount + 2;
        if(orderCount >= 320){
            break;
        }

        newOrder = getRandomInt(newOrder + 1, 320);
        list.push(newOrder);
        list.push(newOrder + 1);
        orderCount = orderCount + 2;
    }
    return list;
}

function getRandomInt(min, max) { // random num in [min, max)
    return Math.floor(Math.random() * Math.floor(max - min) + min);
  }
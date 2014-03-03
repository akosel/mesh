addItems = function(){
for(i = 0; i < 5; i++){
$('#toDoList').append(
"    <div class='container'>"+
"        <div class='media'>"+
"                <i class='fa-media-object fa fa-square-o fa-4x' id='toDoItem"+ i + "' ></i>"+
"            <div class='media-body'>"+
"                 <h5 class='toDoDate'>February 1, 2014</h5>"+
"                <h4 class='media-heading media-heading-bold'>Run "+ Math.ceil(Math.random()*10)  +"</h4>"+
"                Part of my training program"+
"            </div>"+
"        </div>"+
"    </div>"
)
}
}

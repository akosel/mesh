$(document).on('click','i.fa-square-o',function(){
    taskId = $(this).attr('id'); 
    goalId = $(this).attr('label'); 
    $(this).removeClass('fa-square-o');
    $(this).addClass('fa-check-square-o');
    $(this).parent().append(
        "<div id='shareForm"+$(this).attr('id') + "'>"+
        "<textarea label='" + goalId + "' id='" + taskId + "' class='form-control' placeholder='Say something about this!' rows='3'></textarea>"+
        "<button type='button'  class='menu-btn btn-brown share-btn' id='shareButton'>Share</button>"+
        "<button type='button' id='notNow"+ $(this).attr('id') + "' class='menu-btn notnow-btn'>Not Now</button>"+
        "</div>"
    )
});

$(document).on('click','i.fa-check-square-o',function(){
    $(this).removeClass('fa-check-square-o');
    $(this).addClass('fa-square-o');    
    $('#shareForm'+$(this).attr('id')).remove(); 
});



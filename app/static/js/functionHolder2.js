$(document).on('click','i.fa-square',function(){
    $(this).removeClass('fa-square');
    $(this).addClass('fa-check-square');
   
});

$(document).on('click','i.fa-check-square',function(){
    $(this).removeClass('fa-check-square');
    $(this).addClass('fa-square');    
    $('#shareForm'+$(this).attr('id')).remove(); 
});


$(document).ready(function(){
});
// JavaScript Document

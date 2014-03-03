$(document).ready(function() {
  //toggle the componenet with class msg_body
  $(".unread").click(function()
  {
    if ($(this).next().css('display') == 'none') 
        $(this).next().css('display','block'); 
    else
        $(this).next().css('display','none'); 
		
	
  });
 
});

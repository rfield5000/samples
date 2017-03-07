allow_item_clicks = true;

function ping_task_update(id_number, selection) {
    // issue an AJAX call with the specified update.
    // Don't wait for response (will change soon).
    //alert("PING");
    disable_item_clicks();
    $('#popup_announce').text('PLEASE WAIT')
    $('#popup_announce').show();
    parm = $.param([{name:'id', value:id_number},
		    {name:'choice', value:selection}]);
    $.ajax({url:'/kanban/task_update?'.concat(parm),
	    type: "GET",
	    success: ping_is_done,
	    error: ping_has_failed,
	   });
}

function receive_item_clicks() {
    allow_item_clicks = true;
    $("p.item_text").click (
	function () {
	    load_popup_box($(this));
	}
    );
}

function disable_item_clicks() {
    allow_item_clicks = false;
}

function update_table_after(data, status, jqXHR) {
    resp_text = eval('(' + data + ')');
    $("#notes_table").html(resp_text['table']);
    // add the click watch again, since we have
    // replaced the HTML the original function
    // attachment seems to be lost
    receive_item_clicks();
}

function ping_has_failed(data, status, jqXHR) {
    receive_item_clicks();
}

function ping_is_done (data, status, jqXHR) {
    $('#popup_announce').text('DONE')
    update_table_after(data, status, jqXHR);

//    resp_text = eval('(' + data + ')');
//    $("#notes_table").html(resp_text['table']);
//    // add the click watch again, since we have
//    // replaced the HTML the original function
//    // attachment seems to be lost
//    receive_item_clicks();
    hide_popup_box();
}

function initial_error() {
    $("#please_wait_main").css('display', 'none');
    $("#problem_loading_main").css('display', 'inherit');
}

function refresh_task_list(final_fixup, error_fixup) {
    $.ajax({url:'/kanban/get_task_list',
	    success: function() {final_fixup();},
	    error: function() {error_fixup();}
	   });
}

function text_matches_attr(the_text, the_attr) {
    if (the_text == 'IN PROGRESS') {
	return (the_attr == 'WORK');
    }
    else {
	return (the_text == the_attr);
    }
}

function load_popup_box(selection) {    // To Load the Popupbox
    if (! allow_item_clicks) {
	return;
    }
    disable_item_clicks();
    original_id = '';
    // the database key for the selection
    $(selection).find('.text_holder').each(
	function () {
	    $('#item_text').text($(this).text());
	    id_number=$(this).parent().attr('db_id');
	    original_id = id_number;
	}
    );
    $('#popup_announce').hide();
    $('#item_popup').fadeIn("fast");
    // make the dropdown have the current value as the default
    $("#item_popup #popup_select option").filter (
	function () {
	    return text_matches_attr($(this).text(), selection.attr('db_state'));
	}
    ).prop('selected', true);
    $("#main_text").css({ // this is just for style
        "opacity": "0.5" 
    });
    $('#item_popup').attr('db_id', original_id);
}        

function hide_popup_box () {
    // ok_to_save - true if use requested update back to data store
    $('#item_popup').fadeOut("slow");
    $("#main_text").css({ // this is just for style       
        "opacity": "1" 
    });
    receive_item_clicks();
}

function complete_popup_box(ok_to_save) {    // TO Unload the Popupbox
    if (ok_to_save) {
	db_id = $('#item_popup').attr('db_id');
	// get the value of the selected option, that's what ":selected" is for
	selection = $("#item_popup #popup_select option:selected").val();
	ping_task_update(db_id, selection);
    }
    else {
	hide_popup_box();
    }
}

function create_is_done(jqXHR, textStatus) {
    if (textStatus != 'success') {
	alert("PROBLEM " . textStatus);
    }
    //alert("DONE TEXT:" + textStatus + ":");
    $("#add_popup").fadeOut("slow");
}

function create_is_success(data, jqXHR, textStatus) {
    update_table_after(data, jqXHR, textStatus);
    receive_item_clicks();
//    resp_text = eval('(' + data + ')');
//    $("#notes_table").html(resp_text['table']);
//    $("#add_popup").fadeOut("slow");
}

function create_failed() {
    alert("failed");
    $("#add_popup").fadeOut("slow");
    receive_item_clicks();
}

ajax_active = 0;

function save_new_task(new_text) {
    if (ajax_active == 0) {
	parm = $.param([{name:'new_text', value:new_text},]);
	$.ajax({url:'/kanban/task_create?'.concat(parm),
		type: "GET",
		complete: create_is_done,
		success: create_is_success,
	       });
	ajax_active = 1;
    }
}

function add_new_task() {
    if (!allow_item_clicks) {
	return;
    }
    disable_item_clicks();
    ajax_active = 0;
    $("[name='new_item_text']").val('');
    $('#add_popup').fadeIn("fast");
    $("#add_popup #done").click(
	function () {
	    new_text = $("[name='new_item_text']").val();
	    save_new_task(new_text);
	}
    );
    $("#add_popup #cancel").click(
	function () {
	    receive_item_clicks();
	    $("#add_popup").fadeOut("slow");
	}
    );
}

function fix_visibility() {
    $("#please_wait_main").css('display', 'none');
    $("#main_part").css('display', 'inherit');
}
    
$(document).ready(
    function () {
	refresh_task_list(fix_visibility, initial_error);

	$("#main_text").css('display', 'inherit');
	$("#loading_text").css('display', 'none');
	$("#popup_save").click (
	    function () {
		complete_popup_box(true);
	    }
	);

	$("#popup_cancel").click (
	    function () {
		complete_popup_box(false);
	    }
	);

	$("#add_new_task").click (
	    function () {
		add_new_task();
	    }
	);

	receive_item_clicks();

    }
);


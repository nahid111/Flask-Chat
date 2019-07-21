// ----------------------------------------------------------------------
//                          Get user AJAX
// ----------------------------------------------------------------------
// input: user_id   // Output: User as JSON
function get_user(uid) {
    var user_object = {};
    $.ajax({
        url: '/chat/get_user',
        type: 'GET',
        data: {'user_id': uid},
        async: false
    })
        .done(function (response) {
            user_object = response;
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            console.log("get_user() AJAX failed..!!!");
        });
    return user_object;
}


// ================================================================================
//                                  Variables
// ================================================================================
var $chat_box = $('#the_chat_box');
var $empty_chat_box = $('#empty_chat_box');
var $conversation_list = $('#conversation_list');

var $msg_container = $('.msg_card_body');
var $send_btn = $('.send_btn');
var $user_input_field = $('#user_input');
var current_user_id = Number($('#current_user_id').val());
var current_user_avatar = $('#current_user_avatar').text();

var $receiver_id = $('#receiver_id');
var $receiver_name = $('#receiver_name');
var $receiver_img = $('#receiver_img');


// -----------------------------------------------------------
//                  set receiver details
// -----------------------------------------------------------
function set_receiver_details(usr) {
    $receiver_id.html(usr.id);
    $receiver_name.html(usr.username);
    $receiver_img.attr("src", "/static/uploads/avatars/" + usr.avatar);
}


// -----------------------------------------------------------
//              Display The Chatting Box
// -----------------------------------------------------------
function show_msg_box() {
    if ($chat_box.is(":hidden") && $empty_chat_box.is(":visible")) {
        $chat_box.show();
        $empty_chat_box.hide();
    }
}


// ================================================================================
//                      Updating the Conversation list
// ================================================================================

// ----------------------------------------------------------------------
//        Append a Conversation to the Left-side Conversation list
// ----------------------------------------------------------------------
// input: json_obj
function append_conversation_to_list(json_obj) {
    var temp_conv = `
                <li class="single_conversation">
                    <div class="d-flex bd-highlight">
                        <div class="img_cont">
                            <img src="/static/uploads/avatars/`+json_obj.rcvr_avatar+`" class="rounded-circle user_img">
                            <span class="user_id" style="display: none">`+json_obj.rcvr_id+`</span>
                            <span class="online_icon"></span>
                        </div>
                        <div class="user_info">
                            <span>`+json_obj.rcvr_name+`</span>
                            <!-- <p> User is online </p> -->
                        </div>
                    </div>
                </li>
                `;
    $conversation_list.append(temp_conv);
}


// ----------------------------------------------------------------------
//                Update the Left-side Conversation list
// ----------------------------------------------------------------------
function update_conversations_list() {
    $.ajax({
        url: '/chat/update_conversations_list',
        type: 'GET',
        // data: { 'user_id': uid },
        async: false
    })
        .done(function (response) {
            $conversation_list.empty();
            // append each conversation to the list of conversations
            for (i = 0; i < response.length; i++) {
                append_conversation_to_list(response[i]);
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            console.log("update_conversations_list failed..!!!");
        });
}



// ----------------------------------------------------------------------
//                    check if a Conversation exists
// ----------------------------------------------------------------------
// Output: conversation_id, or False
function has_conversation(current_user_id, other_id) {
    var res;
    $.ajax({
        url: '/chat/load_conversation',
        type: 'GET',
        data: {
            'current_user_id': current_user_id,
            'other_user_id': Number(other_id)
        },
        async: false
    })
        .done(function (response) {
            if (response.conv_found) {
                res = response.conv_id;
            } else {
                res = false;
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            console.log("AJAX failed..!!!");
        });
    return res;
}


// ----------------------------------------------------------------------
//                  Append a Message to the Chat box
// ----------------------------------------------------------------------
function append_msg_to_box(msg_JSON) {

    if (Number(msg_JSON.sent_from) === current_user_id) {
        var m = `
                <div class="d-flex justify-content-end mb-4">
                    <div class="msg_cotainer_send">
                        `+msg_JSON.message+`
                        <span class="msg_time_send">`+msg_JSON.created_at+`</span>
                    </div>
                    <div class="img_cont_msg">
                        <img src="/static/uploads/avatars/`+current_user_avatar+`" class="rounded-circle user_img_msg">
                    </div>
                </div>
                `;
    } else {
        var sent_from = get_user(msg_JSON.sent_from);
        var m = `
                <div class="d-flex justify-content-start mb-4">
                    <div class="img_cont_msg">
                        <img src="/static/uploads/avatars/`+sent_from.avatar+`" class="rounded-circle user_img_msg">
                    </div>
                    <div class="msg_cotainer">
                        `+msg_JSON.message+`
                        <span class="msg_time">`+msg_JSON.created_at+`</span>
                    </div>
                </div>
                `;
    }

    $msg_container.append(m);
}


// ----------------------------------------------------------------------
//                  Load messages of a conversation
// ----------------------------------------------------------------------
function load_messages(conv_id) {
    var messages = {};
    $.ajax({
        url: '/chat/load_messages',
        type: 'GET',
        data: {
            'conversation_id': Number(conv_id)
        },
        async: false
    })
        .done(function (response) {
            messages = response;
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            console.log("AJAX failed..!!!");
        });
    for (i = 0; i < messages.length; i++) {
        append_msg_to_box(messages[i]);
    }
}


// ----------------------------------------------------------------------
//                      On selecting an user
// ----------------------------------------------------------------------
function select_user(usr) {
    var conv_id = has_conversation(current_user_id, usr.id);
    $msg_container.empty();
    if (conv_id !== false) {
        load_messages(conv_id);
    }
    set_receiver_details(usr);
    show_msg_box();
    update_conversations_list();
}


// ----------------------------------------------------------------------
//                      On selecting a Conversion
// ----------------------------------------------------------------------
$(document).on('click', 'li.single_conversation', function () {
    // get receiver details
    var r_id = $(this).find('span.user_id').text();
    var usr = get_user(r_id);
    select_user(usr);
});





// ================================================================================
//                               Chatting Functions
// ================================================================================

// ----------------------------------------------------------------------
//                    save a message to DB | AJAX
// ----------------------------------------------------------------------
// input: the_msg, sender_id, receiver_id   // output: msg_JSON
function save_message(the_msg, sender_id, receiver_id) {
    var msg = {};
    $.ajax({
        url: '/chat/save_message',
        type: 'GET',
        data: {
            'the_msg': the_msg,
            'sender_id': Number(sender_id),
            'receiver_id': Number(receiver_id)
        },
        async: false
    })
        .done(function (response) {
            msg = response;
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            console.log("Saving message failed..!!!");
        });
    return msg;
}


// ----------------------------------------------------------------------
//                          SEND a message
// ----------------------------------------------------------------------
function send_message(msg_JSON) {
    // socket.emit('event_name', JSON );
    socket.emit('send request', msg_JSON, function () {
        console.log('message sent, by - ', msg_JSON.sent_from, ', To - ', msg_JSON.sent_to);
    });
}


// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//                  Send messages on Form submission
// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
$send_btn.on('click', function (e) {
    e.preventDefault();
    var the_msg = $user_input_field.val();
    var receiver_id = Number($receiver_id.text());

    // save the msg to db
    var msg_JSON = save_message(the_msg, current_user_id, receiver_id);

    // send the msg
    send_message(msg_JSON);

    // append the msg to chat box
    append_msg_to_box(msg_JSON);

    $user_input_field.val('').focus();

    update_conversations_list();
});


// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//                          Receive messages
// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
// socket.on('event_name', function (JSON) {}
socket.on('receive response', function (msg_JSON) {
    if (Number($receiver_id.text()) === Number(msg_JSON.sent_from)) {
        append_msg_to_box(msg_JSON);
    }
    update_conversations_list();
});





// ================================================================================
//                                  On Page Load
// ================================================================================
$(document).ready(function () {

    // toggle action button
    $('#action_menu_btn').click(function () {
        $('.action_menu').toggle();
    });


    // -----------------------------------------------------------------
    //                  initiate Search Autocomplete
    // -----------------------------------------------------------------
    var $search_user = $("#search_user");
    $search_user.autocomplete({
        source: function (request, response) {
            $.ajax({
                url: '/chat/search_user',
                method: 'GET',
                data: {search: request.term},
                dataType: 'json'
            })
                .done(function (res) {
                    response($.map(res.users, function (item) {
                        if (Number(item.id) !== current_user_id) {
                            return {
                                id: item.id,
                                username: item.username,
                                avatar: item.avatar
                            }
                        }
                    }));
                })
                .fail(function (jqXHR, textStatus, errorThrown) {
                    console.log("User Search Failed");
                });
        },
        minLength: 1,
        select: function (event, ui) {
            var usrr = get_user(ui.item.id);
            select_user(usrr);
        },
        html: true,
        open: function (event, ui) {
            $(".ui-autocomplete").css("z-index", 1000);
        }
    })
        .autocomplete("instance")._renderItem = function (ul, new_item) {
        var lis_itm = `
                    <li class="chat_search_result">
                        <div>
                            <img src='/static/uploads/avatars/` + new_item.avatar + `' style='height: 50px; width: auto;'>
                            <span style="font-size: 20px;">` + new_item.username + `</span>
                        </div>
                    </li>
                    `;
        return $(lis_itm).appendTo(ul);
    };


    // -----------------------------------------------------------------
    //                  load existing conversations
    // -----------------------------------------------------------------
    update_conversations_list();


});



